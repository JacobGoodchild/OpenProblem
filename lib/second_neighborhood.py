"""
Core routines for Seymour's Second Neighborhood Conjecture (SNC).

Definition
----------
An *oriented graph* is a digraph with no 2-cycles (at most one arc between
any pair of vertices -- no "digons"). For a vertex v:
    N+(v)  = out-neighbourhood  (vertices w with an arc v->w)
    N++(v) = second out-neighbourhood (vertices at directed distance
             exactly 2 from v that are NOT in N+(v) and are not v itself)

Seymour's Second Neighborhood Conjecture (1990/1996, open since):

    Every oriented graph has at least one vertex v with |N++(v)| >= |N+(v)|.

Status: PROVEN for tournaments (complete oriented graphs) -- Fisher 1996
(algebraic proof), Havet & Thomasse 2000 (combinatorial proof). OPEN for
general oriented graphs. The active research frontier studies tournaments
with a few arcs removed ("tournaments missing a star", "missing two
stars or disjoint paths", etc.) -- i.e. graphs *close to* complete, since
sparse oriented graphs are comparatively easy (small out-degree implies a
weak requirement on the 2nd neighbourhood) and random sparse graphs
trivially tend to satisfy the conjecture.

We represent an oriented graph on n labeled vertices as an n x n int8
matrix `A` with A[i,j] = 1 meaning arc i->j exists (and then A[j,i] must
be 0). Missing pairs have A[i,j] = A[j,i] = 0.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class SNCState:
    n: int
    A: np.ndarray  # n x n, A[i,j]=1 iff arc i->j

    def copy(self):
        return SNCState(self.n, self.A.copy())


def slack_per_vertex(A: np.ndarray) -> np.ndarray:
    """
    Return an array S of length n: S[v] = |N++(v)| - |N+(v)|.
    The conjecture claims max(S) >= 0 always. A counterexample would be a
    graph with S[v] < 0 for EVERY v (i.e. max(S) < 0).
    """
    n = A.shape[0]
    out1 = A.astype(bool)                       # out1[v,w] = arc v->w
    # second-neighbourhood reachability: w reachable in exactly 2 steps
    # from v via some u with v->u->w
    two_step = out1 @ out1                       # counts paths, but we just need boolean reach
    reach2 = two_step > 0
    not_self_or_n1 = ~out1 & ~np.eye(n, dtype=bool)
    N2 = reach2 & not_self_or_n1
    n1_size = out1.sum(axis=1)
    n2_size = N2.sum(axis=1)
    return n2_size.astype(np.int64) - n1_size.astype(np.int64)


def count_bad(A: np.ndarray) -> int:
    """Number of vertices v with S(v) < 0 (i.e. would-be counterexample
    vertices). A TRUE counterexample to SNC has count_bad == n."""
    return int((slack_per_vertex(A) < 0).sum())


def random_tournament_minus_m(n: int, m: int, rng: random.Random) -> np.ndarray:
    """A random tournament on n vertices with m of the C(n,2) pairs having
    their arc removed entirely (chosen uniformly at random)."""
    A = np.zeros((n, n), dtype=np.int8)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    missing = set(pairs[:m])
    for (i, j) in pairs:
        if (i, j) in missing:
            continue
        if rng.random() < 0.5:
            A[i, j] = 1
        else:
            A[j, i] = 1
    return A


def all_pairs(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def flip_arc_move(A: np.ndarray, rng: random.Random) -> np.ndarray:
    """Pick a random pair that currently HAS an arc and reverse it."""
    n = A.shape[0]
    present = [(i, j) for (i, j) in all_pairs(n) if A[i, j] or A[j, i]]
    if not present:
        return A
    i, j = rng.choice(present)
    B = A.copy()
    if B[i, j]:
        B[i, j], B[j, i] = 0, 1
    else:
        B[j, i], B[i, j] = 0, 1
    return B


def move_gap_move(A: np.ndarray, rng: random.Random) -> np.ndarray:
    """Pick a random pair with NO arc (a 'gap') and a random pair WITH an
    arc; remove the arc-pair's arc (making it the new gap) and add a
    random-direction arc to the old gap. Keeps the number of missing pairs
    (m) constant while letting SA relocate where the gaps are."""
    n = A.shape[0]
    pairs = all_pairs(n)
    gaps = [(i, j) for (i, j) in pairs if not A[i, j] and not A[j, i]]
    present = [(i, j) for (i, j) in pairs if A[i, j] or A[j, i]]
    if not gaps or not present:
        return A
    gi, gj = rng.choice(gaps)
    pi, pj = rng.choice(present)
    B = A.copy()
    B[pi, pj] = 0
    B[pj, pi] = 0
    if rng.random() < 0.5:
        B[gi, gj] = 1
    else:
        B[gj, gi] = 1
    return B
