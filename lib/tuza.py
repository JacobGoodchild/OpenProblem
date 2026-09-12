"""
Exact computation of the two quantities in Tuza's conjecture (1981):

    For every graph G, tau(G) <= 2 * nu(G)

where:
  nu(G)  = triangle packing number = max number of pairwise edge-disjoint
           triangles in G ("packing").
  tau(G) = triangle (edge) cover number = min number of edges whose removal
           destroys every triangle in G ("covering" / "transversal").

Both are computed *exactly* via integer linear programming (ILP), not
heuristically -- this is the rigorous oracle equivalent to the SAT solver
used for the friendly-partitions problem. Both problems are NP-hard in
general, so this is only tractable for small-to-medium graphs (roughly up
to a few hundred triangles), which is exactly the regime where an honest
verification of the conjecture (or a counterexample) is meaningful.

Known facts used to sanity-check this module:
  - tau(K4) = 2, nu(K4) = 1  -> ratio 2 (tight)
  - tau(K5) = 4, nu(K5) = 2  -> ratio 2 (tight)
  - Tuza's conjecture is proven for planar graphs (ratio <= 1.5 actually,
    per Tuza's own paper for planar), and best known general bound is
    tau(G) <= (66/23) * nu(G) (Haxell). Conjecture claims tau <= 2*nu.
"""
import itertools
import pulp


def enumerate_triangles(G):
    """Return list of triangles as frozensets of 3 vertices, using adjacency
    sets for speed. G is a networkx Graph."""
    triangles = []
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    nodes = list(G.nodes())
    for i, u in enumerate(nodes):
        nbrs_u = [w for w in adj[u] if w > u]
        for v in nbrs_u:
            common = adj[u] & adj[v]
            for w in common:
                if w > v:
                    triangles.append(frozenset((u, v, w)))
    return triangles


def triangle_edges(tri):
    """Given a triangle (frozenset of 3 vertices), return its 3 edges as
    frozensets of 2 vertices."""
    a, b, c = tuple(tri)
    return [frozenset((a, b)), frozenset((a, c)), frozenset((b, c))]


def _solver():
    return pulp.PULP_CBC_CMD(msg=0)


def triangle_packing_number(G, triangles=None, time_limit=None, relax=False):
    """Exact nu(G): max set of edge-disjoint triangles, via ILP.
    Returns (value, chosen_triangles) where chosen_triangles is a list of
    frozensets (empty list if relax=True, since LP relaxation gives no
    integral solution)."""
    if triangles is None:
        triangles = enumerate_triangles(G)
    if not triangles:
        return 0, []

    cat = 'Continuous' if relax else 'Binary'
    prob = pulp.LpProblem('triangle_packing', pulp.LpMaximize)
    x = {t: pulp.LpVariable(f'x_{i}', lowBound=0, upBound=1, cat=cat)
         for i, t in enumerate(triangles)}
    prob += pulp.lpSum(x.values())

    # edge -> triangles containing it
    edge_tris = {}
    for t in triangles:
        for e in triangle_edges(t):
            edge_tris.setdefault(e, []).append(t)
    for e, tris in edge_tris.items():
        prob += pulp.lpSum(x[t] for t in tris) <= 1

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit) if time_limit else _solver()
    prob.solve(solver)
    val = pulp.value(prob.objective)
    chosen = [] if relax else [t for t in triangles if pulp.value(x[t]) > 0.5]
    return val, chosen


def triangle_cover_number(G, triangles=None, time_limit=None, relax=False):
    """Exact tau(G): min edges hitting every triangle, via ILP.
    Returns (value, chosen_edges)."""
    if triangles is None:
        triangles = enumerate_triangles(G)
    if not triangles:
        return 0, []

    edges = set()
    for t in triangles:
        edges.update(triangle_edges(t))
    edges = list(edges)

    cat = 'Continuous' if relax else 'Binary'
    prob = pulp.LpProblem('triangle_cover', pulp.LpMinimize)
    y = {e: pulp.LpVariable(f'y_{i}', lowBound=0, upBound=1, cat=cat)
         for i, e in enumerate(edges)}
    prob += pulp.lpSum(y.values())

    for t in triangles:
        te = triangle_edges(t)
        prob += pulp.lpSum(y[e] for e in te) >= 1

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit) if time_limit else _solver()
    prob.solve(solver)
    val = pulp.value(prob.objective)
    chosen = [] if relax else [e for e in edges if pulp.value(y[e]) > 0.5]
    return val, chosen


def tuza_ratio(G, time_limit=None):
    """Compute (tau, nu, ratio) exactly for graph G. ratio = tau/nu (None if
    nu == 0, i.e. triangle-free graph -- conjecture is trivially true)."""
    triangles = enumerate_triangles(G)
    if not triangles:
        return 0, 0, None
    nu, _ = triangle_packing_number(G, triangles, time_limit=time_limit)
    tau, _ = triangle_cover_number(G, triangles, time_limit=time_limit)
    ratio = tau / nu if nu > 0 else None
    return tau, nu, ratio


def greedy_cover_upper_bound(G, triangles=None):
    """Fast greedy heuristic upper bound on tau(G): repeatedly pick the edge
    hitting the most currently-uncovered triangles, until all are covered.
    Not exact, but O(triangles * edges) fast and useful for a quick
    pre-filter / search heuristic before calling the ILP."""
    if triangles is None:
        triangles = enumerate_triangles(G)
    remaining = set(triangles)
    chosen_edges = []
    # edge -> set of triangles containing it (recomputed lazily as triangles
    # get covered)
    while remaining:
        edge_count = {}
        for t in remaining:
            for e in triangle_edges(t):
                edge_count[e] = edge_count.get(e, 0) + 1
        best_edge = max(edge_count, key=edge_count.get)
        chosen_edges.append(best_edge)
        remaining = {t for t in remaining if best_edge not in triangle_edges(t)}
    return len(chosen_edges), chosen_edges


def _greedy_packing_once(triangles, order):
    used_edges = set()
    count = 0
    for t in order:
        te = triangle_edges(t)
        if not any(e in used_edges for e in te):
            used_edges.update(te)
            count += 1
    return count


def greedy_packing_lower_bound(G, triangles=None, trials=12, rng=None):
    """Fast greedy heuristic lower bound on nu(G): repeatedly pick a
    triangle whose edges are all still free, remove its edges from
    availability. A single greedy pass in a fixed order can be far from
    optimal (order-dependent), so this tries several random orderings and
    keeps the best -- still O(trials * triangles), and much tighter than a
    single deterministic pass. Not exact, but fast and useful as a search
    heuristic / pre-filter before calling the ILP."""
    if triangles is None:
        triangles = enumerate_triangles(G)
    if not triangles:
        return 0
    if rng is None:
        import random as _random
        rng = _random
    tri_list = list(triangles)
    best = _greedy_packing_once(triangles, tri_list)
    for _ in range(trials - 1):
        order = tri_list[:]
        rng.shuffle(order)
        val = _greedy_packing_once(triangles, order)
        if val > best:
            best = val
    return best
