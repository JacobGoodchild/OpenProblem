"""
Tools for attacking the Ringel-Kotzig graceful tree conjecture (1964):
every tree on n vertices admits a bijective labeling of its vertices
with {0,...,n-1} such that the induced edge labels (|label(u)-label(v)|
for each edge) are EXACTLY {1,...,n-1} (each value once).

Verified by exhaustive computer search up to n=35 (Fang, published;
an unpublished/unconfirmed claim exists for n=39). Since the total
number of non-isomorphic trees explodes combinatorially past that
(hundreds of billions+ by n=40), further FULL-TREE exhaustive
verification is not computationally realistic here. Instead this
targets a specific, actively-studied structural family where
exhaustive coverage IS realistic well past n=35: SPIDERS (trees with
at most one vertex of degree > 2) with many legs of mixed length --
per recent (2026) literature, "six or more long legs together with
arbitrarily many length-one legs" is a real, currently open gap that
existing theorems don't cover.

Key necessary condition used to speed up search: the edge-label n-1
(the maximum possible, since vertex labels lie in [0,n-1]) can ONLY be
achieved by the vertex pair (0, n-1) -- so in any graceful labeling,
the vertices labeled 0 and n-1 MUST be adjacent in the tree. This lets
backtracking search fix that structural fact up front instead of
discovering it by trial and error.
"""
import itertools

import networkx as nx


def make_spider(leg_lengths):
    """Build a spider (tree) with one center vertex and legs of the
    given lengths (list of positive ints, each length = number of
    edges in that leg / path from center to leaf). Returns a networkx
    Graph. Vertex 0 is always the center."""
    G = nx.Graph()
    G.add_node(0)
    next_id = 1
    for length in leg_lengths:
        prev = 0
        for _ in range(length):
            G.add_node(next_id)
            G.add_edge(prev, next_id)
            prev = next_id
            next_id += 1
    return G


def spider_partitions(total_edges, num_legs, min_leg=1, max_leg=None):
    """All ways to write total_edges as an ORDERED-doesn't-matter
    (we dedupe) sum of num_legs positive integers each >= min_leg,
    <= max_leg (default total_edges). Returns a list of sorted tuples
    (leg-length multisets), i.e. all partitions of total_edges into
    exactly num_legs parts within the given bounds."""
    if max_leg is None:
        max_leg = total_edges
    results = []

    def helper(remaining, parts_left, min_part, current):
        if parts_left == 0:
            if remaining == 0:
                results.append(tuple(current))
            return
        # each remaining part must be >= min_part (keeps partitions
        # sorted/canonical, avoids duplicate enumeration) and <= max_leg,
        # and remaining must be achievable
        lo = min_part
        hi = min(max_leg, remaining - (parts_left - 1) * min_part)
        for v in range(lo, hi + 1):
            if v * parts_left > remaining or v > remaining:
                continue
            current.append(v)
            helper(remaining - v, parts_left - 1, v, current)
            current.pop()

    helper(total_edges, num_legs, min_leg, [])
    return results


def find_graceful_labeling_backtrack(G, node_budget=5_000_000, rng=None):
    """Backtracking search for a graceful labeling. Uses the 0/(n-1)
    adjacency necessary condition to fix the top-level choice, then
    assigns remaining vertex labels via DFS with constraint propagation
    (track which edge-difference values are already used). Returns
    (labeling_dict_or_None, nodes_explored, exhausted_bool) -- exhausted
    means the WHOLE search space was explored (a None result here is
    then a real proof of non-existence, not just a search giving up).

    If `rng` is given, both the order of (zero_v, max_v) starting pairs
    AND the order candidate labels are tried in at each step are
    shuffled -- a fixed deterministic order can get catastrophically
    unlucky (confirmed empirically: P20, provably graceful, failed to
    resolve in 5M nodes with a fixed order; trivial with randomization)."""
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    edges = list(G.edges())
    adj = {v: list(G.neighbors(v)) for v in nodes}

    nodes_explored = [0]

    def try_with_zero_at(zero_v, max_v):
        # zero_v gets label 0, max_v (a neighbor of zero_v) gets label n-1
        label = {zero_v: 0, max_v: n - 1}
        used_labels = {0, n - 1}
        used_diffs = {n - 1}  # the edge (zero_v, max_v) uses diff n-1
        remaining_vertices = [v for v in nodes if v not in label]
        # order remaining vertices by BFS distance from the labeled pair,
        # so each new vertex likely has an already-labeled neighbor
        # (lets us prune via the edge-diff constraint immediately)
        order = sorted(remaining_vertices, key=lambda v: min(
            nx.shortest_path_length(G, v, zero_v), nx.shortest_path_length(G, v, max_v)))

        def backtrack(idx):
            nodes_explored[0] += 1
            if nodes_explored[0] > node_budget:
                return 'exhausted'
            if idx == len(order):
                return True
            v = order[idx]
            labeled_neighbors = [u for u in adj[v] if u in label]
            candidate_order = range(1, n - 1) if rng is None else rng.sample(range(1, n - 1), n - 2)
            for candidate in candidate_order:
                if candidate in used_labels:
                    continue
                # check all edges to already-labeled neighbors give NEW diffs
                new_diffs = []
                ok = True
                for u in labeled_neighbors:
                    d = abs(candidate - label[u])
                    if d == 0 or d in used_diffs or d in new_diffs:
                        ok = False
                        break
                    new_diffs.append(d)
                if not ok:
                    continue
                label[v] = candidate
                used_labels.add(candidate)
                for d in new_diffs:
                    used_diffs.add(d)
                result = backtrack(idx + 1)
                if result is True:
                    return True
                if result == 'exhausted':
                    return 'exhausted'
                del label[v]
                used_labels.discard(candidate)
                for d in new_diffs:
                    used_diffs.discard(d)
            return False

        r = backtrack(0)
        if r is True:
            return dict(label)
        return None if r is False else 'exhausted'

    pairs = [(zero_v, max_v) for zero_v in nodes for max_v in adj[zero_v]]
    if rng is not None:
        rng.shuffle(pairs)
    any_exhausted_hit = False
    for zero_v, max_v in pairs:
        r = try_with_zero_at(zero_v, max_v)
        if isinstance(r, dict):
            return r, nodes_explored[0], False
        if r == 'exhausted':
            any_exhausted_hit = True

    return None, nodes_explored[0], any_exhausted_hit


def find_graceful_with_restarts(G, trials=15, trial_node_budget=300_000, seed_base=0):
    """Try several randomized-order restarts (fast at finding a
    labeling when one exists -- a fixed order can get unluckily stuck),
    falling back to one deterministic exhaustive attempt (the only
    thing that can actually PROVE non-existence) if all restarts fail.
    Returns (labeling_or_None, total_nodes, exhausted_bool)."""
    import random
    total_nodes = 0
    for t in range(trials):
        rng = random.Random(seed_base + t)
        label, nodes, exhausted = find_graceful_labeling_backtrack(
            G, node_budget=trial_node_budget, rng=rng)
        total_nodes += nodes
        if label is not None:
            return label, total_nodes, False
    return None, total_nodes, False  # inconclusive unless caller does an exhaustive follow-up


def local_search_graceful(G, rng, max_iters=200_000, restart_after_stuck=8000):
    """Simulated-annealing-style local search directly over labelings
    (not a backtracking construction): state = a random bijection
    V(G) -> {0,...,n-1}; objective = number of DUPLICATE edge-
    difference values (0 means a valid graceful labeling). Move: swap
    two vertices' labels. This is the same style of search Aldred &
    McKay's original stochastic approach used to reach n=27, and tends
    to scale much better than exhaustive backtracking for larger trees
    (at the cost of being unable to PROVE non-existence -- a search
    that fails here just means "didn't find one", not "none exists").
    Returns (labeling_dict_or_None, best_duplicate_count)."""
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    edges = list(G.edges())

    def duplicate_count(label):
        diffs = [abs(label[u] - label[v]) for u, v in edges]
        seen = {}
        dup = 0
        for d in diffs:
            seen[d] = seen.get(d, 0) + 1
        for d, c in seen.items():
            if c > 1:
                dup += c - 1
        return dup

    perm = list(range(n))
    rng.shuffle(perm)
    label = {nodes[i]: perm[i] for i in range(n)}
    cur_dup = duplicate_count(label)
    best_dup = cur_dup
    best_label = dict(label)

    stuck = 0
    for _ in range(max_iters):
        if cur_dup == 0:
            break
        i, j = rng.sample(range(n), 2)
        vi, vj = nodes[i], nodes[j]
        label[vi], label[vj] = label[vj], label[vi]
        new_dup = duplicate_count(label)
        if new_dup <= cur_dup:
            cur_dup = new_dup
            if new_dup < best_dup:
                best_dup = new_dup
                best_label = dict(label)
            stuck = 0
        else:
            label[vi], label[vj] = label[vj], label[vi]  # revert
            stuck += 1
        if stuck >= restart_after_stuck:
            stuck = 0
            rng.shuffle(perm)
            label = {nodes[i]: perm[i] for i in range(n)}
            cur_dup = duplicate_count(label)

    if best_dup == 0:
        return best_label, 0
    return None, best_dup


def find_graceful_local_search_restarts(G, trials=10, max_iters=200_000, seed_base=0):
    """Multiple independent local-search runs; returns the first valid
    labeling found, or (None, best_duplicate_count_seen) if none."""
    import random
    best_overall = None
    for t in range(trials):
        rng = random.Random(seed_base + t)
        label, dup = local_search_graceful(G, rng, max_iters=max_iters)
        if label is not None:
            return label, 0
        if best_overall is None or dup < best_overall:
            best_overall = dup
    return None, best_overall


def verify_graceful_labeling(G, labeling):
    """Independent from-scratch check: labeling must be a bijection
    V(G) -> {0,...,n-1}, and the induced edge differences must be
    exactly {1,...,n-1} (each exactly once)."""
    n = G.number_of_nodes()
    if set(labeling.keys()) != set(G.nodes()):
        return False
    if sorted(labeling.values()) != list(range(n)):
        return False
    diffs = []
    for u, v in G.edges():
        diffs.append(abs(labeling[u] - labeling[v]))
    return sorted(diffs) == list(range(1, n))
