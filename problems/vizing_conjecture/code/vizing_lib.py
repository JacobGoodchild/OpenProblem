"""
Tools for attacking Vizing's conjecture (1968): for graphs G, H,
gamma(G [] H) >= gamma(G) * gamma(H), where gamma is the domination
number and [] is the Cartesian product. Proven for gamma(G) in
{1,2,3}, cycles, trees, and several other special families. OPEN in
general. Best known general lower bound (Clark & Suen, 2000):
gamma(G [] H) >= (1/2) gamma(G) gamma(H).

A MINIMAL counterexample (from the survey literature, Bresar, Henning,
Klavzar, Rall) must be:
  - connected
  - have domination number >= 4
  - edge-critical: adding ANY missing edge strictly decreases gamma(G)
  - every vertex belongs to SOME minimum dominating set
  - identifying (contracting) any two vertices u,v strictly decreases
    the domination number of the resulting graph

These give powerful, cheap pre-filters: a candidate graph failing any
one of them CANNOT be part of a minimal counterexample, so can be
pruned immediately without ever needing to test it against any H.
"""
import itertools

import networkx as nx
import pulp


def domination_number(G, time_limit=15):
    """Exact minimum dominating set size via ILP set-cover: binary
    variable per vertex, minimize count, each vertex's closed
    neighborhood must include >=1 selected vertex."""
    nodes = list(G.nodes())
    x = {v: pulp.LpVariable(f'x_{v}', cat='Binary') for v in nodes}
    prob = pulp.LpProblem('domination', pulp.LpMinimize)
    prob += pulp.lpSum(x.values())
    for u in nodes:
        closed_nbhd = [u] + list(G.neighbors(u))
        prob += pulp.lpSum(x[v] for v in closed_nbhd) >= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)
    val = pulp.value(prob.objective)
    if val is None:
        return None, None
    dom_set = [v for v in nodes if pulp.value(x[v]) > 0.5]
    return int(round(val)), dom_set


def is_dominating_set(G, D):
    D = set(D)
    for v in G.nodes():
        if v in D:
            continue
        if not (set(G.neighbors(v)) & D):
            return False
    return True


def has_min_dominating_set_of_size_containing(G, v, gamma, time_limit=15):
    """Feasibility check: does a dominating set of size gamma (the
    already-known domination number) exist that includes vertex v?"""
    nodes = list(G.nodes())
    x = {u: pulp.LpVariable(f'x_{u}', cat='Binary') for u in nodes}
    prob = pulp.LpProblem('feas', pulp.LpMinimize)
    prob += 0  # feasibility only
    prob += x[v] == 1
    prob += pulp.lpSum(x.values()) <= gamma
    for u in nodes:
        closed_nbhd = [u] + list(G.neighbors(u))
        prob += pulp.lpSum(x[w] for w in closed_nbhd) >= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    status = prob.solve(solver)
    return pulp.LpStatus[status] == 'Optimal'


def every_vertex_in_some_min_dominating_set(G, gamma=None, time_limit=15):
    if gamma is None:
        gamma, _ = domination_number(G, time_limit)
    for v in G.nodes():
        if not has_min_dominating_set_of_size_containing(G, v, gamma, time_limit):
            return False
    return True


def is_edge_critical(G, gamma=None, time_limit=15):
    """Adding ANY missing edge must strictly decrease gamma(G)."""
    if gamma is None:
        gamma, _ = domination_number(G, time_limit)
    nodes = list(G.nodes())
    for u, v in itertools.combinations(nodes, 2):
        if G.has_edge(u, v):
            continue
        G2 = G.copy()
        G2.add_edge(u, v)
        g2, _ = domination_number(G2, time_limit)
        if g2 is None or g2 >= gamma:
            return False
    return True


def identifying_decreases_domination(G, gamma=None, time_limit=15):
    """Identifying (contracting) ANY two vertices u,v must strictly
    decrease the domination number of the resulting (simplified, no
    self-loops/multi-edges) graph."""
    if gamma is None:
        gamma, _ = domination_number(G, time_limit)
    nodes = list(G.nodes())
    for u, v in itertools.combinations(nodes, 2):
        G2 = nx.contracted_nodes(G, u, v, self_loops=False)
        g2, _ = domination_number(G2, time_limit)
        if g2 is None or g2 >= gamma:
            return False
    return True


def is_minimal_counterexample_candidate(G, time_limit=15, min_gamma=4):
    """Runs all the cheap-to-expensive necessary-condition filters in
    order (cheapest / most-likely-to-fail first), short-circuiting as
    soon as one fails. Returns (passes: bool, gamma_or_None, reason)."""
    if not nx.is_connected(G):
        return False, None, 'not connected'
    gamma, _ = domination_number(G, time_limit)
    if gamma is None:
        return False, None, 'domination ILP failed to solve'
    if gamma < min_gamma:
        return False, gamma, f'gamma={gamma} < {min_gamma}'
    if not is_edge_critical(G, gamma, time_limit):
        return False, gamma, 'not edge-critical'
    if not every_vertex_in_some_min_dominating_set(G, gamma, time_limit):
        return False, gamma, 'not every vertex in a min dominating set'
    if not identifying_decreases_domination(G, gamma, time_limit):
        return False, gamma, 'identifying two vertices does not always decrease gamma'
    return True, gamma, 'passes all necessary-condition filters'


def check_vizing(G, H, time_limit_each=15):
    """Compute gamma(G), gamma(H), gamma(G [] H) exactly and check the
    conjectured inequality. Returns a dict with all values plus
    'holds' (True/False/None if any ILP failed to solve)."""
    gG, _ = domination_number(G, time_limit_each)
    gH, _ = domination_number(H, time_limit_each)
    if gG is None or gH is None:
        return {'holds': None, 'reason': 'gamma(G) or gamma(H) ILP failed'}
    P = nx.cartesian_product(G, H)
    gP, domP = domination_number(P, time_limit_each * 4)
    if gP is None:
        return {'gamma_G': gG, 'gamma_H': gH, 'holds': None,
                'reason': 'gamma(G[]H) ILP failed (likely too large / timed out)'}
    return {'gamma_G': gG, 'gamma_H': gH, 'gamma_product': gP,
            'bound': gG * gH, 'holds': gP >= gG * gH, 'dom_set_product': domP}
