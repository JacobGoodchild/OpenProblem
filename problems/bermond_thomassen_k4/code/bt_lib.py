"""
Tools for attacking the Bermond-Thomassen conjecture at k=4: every
digraph with minimum out-degree >= 2k-1 = 7 contains k=4 vertex-disjoint
directed cycles. Proven for k=1,2,3 (Thomassen 1983 for k=2;
Lichiardopol, Por, Sereni for k=3); OPEN for all k>=4.

Core computational primitive: given a digraph, what is the maximum
number of pairwise VERTEX-DISJOINT directed cycles it contains? If we
can ever exhibit a digraph with min out-degree >= 7 and max disjoint
cycle count <= 3, that's a counterexample.

Approach: enumerate all elementary (simple) directed cycles via
networkx's Johnson's-algorithm-based `simple_cycles` (exact, complete --
not a heuristic), then solve exact "maximum set packing" via ILP
(pulp/CBC): one binary variable per cycle, maximize the count of
selected cycles subject to each vertex being used by at most one
selected cycle. This is the same ILP-packing pattern used elsewhere in
this project (e.g. independent set / clique packing), just with
directed-cycle vertex-sets as the "items" instead of edges/cliques.
"""
import random

import networkx as nx
import pulp


def random_min_outdegree_digraph(n, d, rng):
    """A digraph on n vertices where every vertex has out-degree EXACTLY
    d (d distinct out-neighbors chosen uniformly at random from the
    other n-1 vertices, no self-loops). Requires n >= d+1."""
    assert n >= d + 1
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for v in range(n):
        others = [u for u in range(n) if u != v]
        targets = rng.sample(others, d)
        for t in targets:
            G.add_edge(v, t)
    return G


def verify_min_outdegree(G, d):
    """Independent from-scratch check that every vertex has out-degree
    >= d (the conjecture's hypothesis)."""
    return all(G.out_degree(v) >= d for v in G.nodes())


def enumerate_cycles(G, max_cycles=200_000, max_length=None):
    """Enumerate all elementary directed cycles (vertex-sets) via
    networkx's exact simple_cycles. Returns (cycles_as_frozensets,
    truncated) -- truncated=True if we hit max_cycles (a safety valve
    for dense graphs where the true cycle count could be astronomical;
    callers MUST check this before trusting a "no k disjoint cycles"
    conclusion, since a truncated cycle list can only UNDERCOUNT, never
    overcount, the true max disjoint-cycle packing)."""
    cycles = []
    truncated = False
    for i, c in enumerate(nx.simple_cycles(G, length_bound=max_length)):
        if i >= max_cycles:
            truncated = True
            break
        cycles.append(frozenset(c))
    return cycles, truncated


def max_disjoint_cycle_packing(n, cycles, time_limit=30):
    """Exact ILP: maximum number of pairwise vertex-disjoint cycles
    (from the given list of candidate cycles, as vertex-sets) that can
    be simultaneously selected. Returns (max_count, selected_cycles)."""
    if not cycles:
        return 0, []
    prob = pulp.LpProblem('max_disjoint_cycles', pulp.LpMaximize)
    x = [pulp.LpVariable(f'c_{i}', cat='Binary') for i in range(len(cycles))]
    prob += pulp.lpSum(x)
    for v in range(n):
        covering = [x[i] for i, c in enumerate(cycles) if v in c]
        if covering:
            prob += pulp.lpSum(covering) <= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)
    val = pulp.value(prob.objective)
    if val is None:
        return None, None  # solver gave up
    selected = [cycles[i] for i in range(len(cycles)) if pulp.value(x[i]) > 0.5]
    return int(round(val)), selected


def has_k_disjoint_cycles_feasibility(n, cycles, k, time_limit=15):
    """Cheaper feasibility-only ILP: does a selection of >= k disjoint
    cycles exist? (Faster than full optimization when we only care
    about crossing the k=4 threshold, not the true maximum.)"""
    if not cycles:
        return (k == 0), []
    prob = pulp.LpProblem('feasibility_k_disjoint', pulp.LpMaximize)
    x = [pulp.LpVariable(f'c_{i}', cat='Binary') for i in range(len(cycles))]
    prob += pulp.lpSum(x)
    for v in range(n):
        covering = [x[i] for i, c in enumerate(cycles) if v in c]
        if covering:
            prob += pulp.lpSum(covering) <= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)
    val = pulp.value(prob.objective)
    if val is None:
        return None, None
    if val >= k - 1e-6:
        selected = [cycles[i] for i in range(len(cycles)) if pulp.value(x[i]) > 0.5]
        return True, selected
    return False, None


def verify_disjoint_cycles(G, selected_cycles):
    """Independent from-scratch check: each 'cycle' (given as a vertex
    set) must actually admit a directed cyclic tour using real edges of
    G, and all selected cycles must be pairwise vertex-disjoint."""
    all_vertices = set()
    for c in selected_cycles:
        if all_vertices & c:
            return False  # not disjoint
        all_vertices |= c
        # check c admits SOME cyclic ordering using real edges (brute
        # force over rotations/permutations is too slow in general, but
        # cycles here came from nx.simple_cycles which already returns
        # an actual cyclic order -- so this check instead reconstructs
        # via a Hamiltonian-cycle-on-subgraph search, which is correct
        # and still fast for the small cycle sizes involved)
        sub = G.subgraph(c)
        found = False
        c_list = list(c)
        start = c_list[0]
        # DFS Hamiltonian cycle search restricted to sub, starting at `start`
        def dfs(path, visited):
            if len(path) == len(c_list):
                return sub.has_edge(path[-1], start)
            for nxt in sub.successors(path[-1]):
                if nxt not in visited:
                    visited.add(nxt)
                    path.append(nxt)
                    if dfs(path, visited):
                        return True
                    path.pop()
                    visited.remove(nxt)
            return False
        if dfs([start], {start}):
            found = True
        if not found:
            return False
    return True
