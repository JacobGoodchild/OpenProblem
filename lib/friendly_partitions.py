"""
Core routines for the "friendly partition" (a.k.a. internal / satisfactory
partition) problem.

Definition
----------
Given a graph G = (V, E), a *friendly partition* is a partition of V into
two NON-EMPTY parts A, B such that every vertex v has

        |N(v) ∩ (v's own part)|  >=  |N(v) ∩ (the other part)|

i.e. every vertex has at least as many neighbours "at home" as "away".

Open problem (posed by M. DeVos, hosted on Open Problem Garden, see
https://www.openproblemgarden.org/op/friendly_partitions):

    For every regularity degree r, do all but finitely many r-regular
    graphs have a friendly partition?

This is settled for r = 3, 4, 6 (finite, fully-known exception lists).
It is OPEN for r = 5 (and for every r >= 7 except a couple of special
cases), which is the case we attack computationally here.

All functions below are written for general (loopless, simple) graphs but
are used exclusively on 5-regular graphs in this project.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Optional

import networkx as nx
import numpy as np


@dataclass
class SearchResult:
    found: bool
    partition: Optional[dict] = None          # vertex -> 0/1
    method: str = ""
    iterations: int = 0
    note: str = ""
    closest_unhappy: int = -1                 # fewest unhappy vertices ever seen (any attempt)


def _neighbor_arrays(G: nx.Graph):
    """Return (nodes list, index map, adjacency-as-int-array) for fast search."""
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    deg = G.degree()
    maxdeg = max(d for _, d in deg) if n else 0
    adj = -np.ones((n, maxdeg), dtype=np.int32)
    for v in nodes:
        i = idx[v]
        for j, w in enumerate(G.neighbors(v)):
            adj[i, j] = idx[w]
    degs = np.array([deg[v] for v in nodes], dtype=np.int32)
    return nodes, idx, adj, degs


def local_search_friendly_partition(
    G: nx.Graph,
    rng: random.Random,
    max_flips: int = 20000,
    perturb_after_stuck: int = 25,
    restarts: int = 1,
) -> SearchResult:
    """
    Flip-based local search a la "local max-uncut" / Hopfield dynamics.

    Potential function: number of monochromatic edges (edges whose two
    endpoints are on the same side). Flipping a vertex whose "home" count
    is strictly less than its "away" count strictly increases this
    potential, is bounded above by |E|, so plain flipping always
    terminates UNLESS the flip would empty one of the two parts (which we
    forbid to keep the partition non-trivial). When we get stuck with only
    "part-emptying" unhappy vertices remaining, we perturb (random block
    flip) and continue -- this is the "unorthodox" simulated-annealing-ish
    part that lets us escape the traps that make K4/K3,3/K5-like small
    dense graphs fail.
    """
    nodes, idx, adj, degs = _neighbor_arrays(G)
    n = len(nodes)
    if n < 2:
        return SearchResult(False, method="local_search", note="graph too small")

    best_note = ""
    total_iters = 0
    best_unhappy = n
    for attempt in range(restarts):
        side = np.array([rng.randint(0, 1) for _ in range(n)], dtype=np.int8)
        # avoid degenerate all-one-side start
        if side.sum() == 0:
            side[rng.randrange(n)] = 1
        if side.sum() == n:
            side[rng.randrange(n)] = 0

        stuck_counter = 0
        for it in range(max_flips):
            total_iters += 1
            # same-side neighbour counts, vectorised
            valid = adj >= 0
            nbr_side = np.where(valid, side[np.clip(adj, 0, n - 1)], -1)
            same_count = ((nbr_side == side[:, None]) & valid).sum(axis=1)
            away_count = degs - same_count

            unhappy = np.where(same_count < away_count)[0]
            if len(unhappy) < best_unhappy:
                best_unhappy = int(len(unhappy))
            if len(unhappy) == 0:
                partition = {nodes[i]: int(side[i]) for i in range(n)}
                if len(set(partition.values())) == 2:
                    return SearchResult(True, partition, "local_search", total_iters)
                else:
                    break  # degenerate, retry

            # only allow flips that keep both sides non-empty
            side_size = [int((side == 0).sum()), int((side == 1).sum())]
            flippable = [v for v in unhappy if side_size[side[v]] > 1]

            if not flippable:
                stuck_counter += 1
                if stuck_counter >= perturb_after_stuck:
                    # perturb: flip a random small block of vertices to escape
                    block = rng.sample(range(n), k=min(3, n))
                    for b in block:
                        side[b] = 1 - side[b]
                    stuck_counter = 0
                    continue
                else:
                    # try flipping a random truly-unhappy-but-blocked vertex's
                    # neighbour instead, to shuffle state
                    v = rng.choice(list(unhappy))
                    side[v] = 1 - side[v]
                    continue

            # flip the most unhappy vertex (largest deficit), random tie-break
            deficits = away_count[flippable] - same_count[flippable]
            m = deficits.max()
            best = [v for v, d in zip(flippable, deficits) if d == m]
            v = rng.choice(best)
            side[v] = 1 - side[v]
        best_note = f"exhausted max_flips on attempt {attempt}"

    return SearchResult(False, method="local_search", iterations=total_iters, note=best_note,
                         closest_unhappy=best_unhappy)


def brute_force_friendly_partition(G: nx.Graph, cap_vertices: int = 24) -> SearchResult:
    """
    Exact search by trying every non-trivial bipartition (fixing node 0 to
    side 0 by symmetry, so 2^(n-1) - 1 partitions). Only safe for small n.
    Returns found=True with a witness partition, or found=False meaning a
    PROVEN absence of any friendly partition (a genuine counterexample to
    the "no infinite family" hope, if it recurs at unboundedly large n!).
    """
    nodes = list(G.nodes())
    n = len(nodes)
    if n > cap_vertices:
        raise ValueError(f"n={n} too large for brute force (cap={cap_vertices})")
    idx = {v: i for i, v in enumerate(nodes)}
    adj_bits = [0] * n
    for u, v in G.edges():
        adj_bits[idx[u]] |= (1 << idx[v])
        adj_bits[idx[v]] |= (1 << idx[u])
    degs = [G.degree(v) for v in nodes]

    full = (1 << n) - 1
    # iterate subsets containing vertex 0 as side A representative,
    # 1 <= |A| <= n-1
    for mask in range(1, 1 << (n - 1)):
        A = mask << 0  # vertex 0's bit is bit0; ensure vertex0 in A
        A |= 1  # vertex 0 always in A
        B = full & ~A
        if A == 0 or B == 0:
            continue
        ok = True
        for i in range(n):
            same = bin(adj_bits[i] & (A if (A >> i) & 1 else B)).count("1")
            away = degs[i] - same
            if same < away:
                ok = False
                break
        if ok:
            partition = {nodes[i]: (0 if (A >> i) & 1 else 1) for i in range(n)}
            return SearchResult(True, partition, "brute_force")
    return SearchResult(False, method="brute_force", note="exhaustively checked all bipartitions")


def verify_partition(G: nx.Graph, partition: dict) -> bool:
    """Sanity-check that `partition` really is a friendly partition of G."""
    values = set(partition.values())
    if len(values) != 2:
        return False
    for v in G.nodes():
        same = sum(1 for w in G.neighbors(v) if partition[w] == partition[v])
        away = G.degree(v) - same
        if same < away:
            return False
    return True
