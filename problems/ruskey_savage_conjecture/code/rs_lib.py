"""
Tools for attacking the Ruskey-Savage conjecture (1993): every matching
of the n-dimensional hypercube graph Q_n can be extended to a
Hamiltonian cycle. Proven for perfect matchings (Fink, 2007) and for
matchings spanning at most 5 "directions" (2024-2025). General case
open. Last exhaustive computational check: MathCheck, 2015, confirmed
for n=5 (32 vertices) via SAT enumeration + CAS verification. Nobody
appears to have pushed to n=6 (64 vertices) since.

Core computational primitive: given a matching M of Q_n (a required
edge set), does a Hamiltonian cycle exist that CONTAINS all of M?
Encoded as SAT: binary variable per edge (1 = in the cycle), degree-2
constraint at every vertex, required matching edges forced to 1, and
LAZY subtour elimination (solve -> check if the selected edges form a
single cycle -> if not, block that exact subtour decomposition and
resolve -- iterate to convergence). This mirrors the SAT+CAS approach
MathCheck used (SAT proposes an edge set, a connectivity check plays
the role of the CAS).
"""
import itertools

import networkx as nx
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def hypercube(n):
    """Q_n: vertices 0..2^n-1, edges between vertices differing in
    exactly one bit."""
    G = nx.Graph()
    N = 1 << n
    G.add_nodes_from(range(N))
    for v in range(N):
        for b in range(n):
            u = v ^ (1 << b)
            if u > v:
                G.add_edge(v, u)
    return G


def edge_direction(n, u, v):
    """Which bit position (0..n-1) u and v differ in -- the 'direction'
    of a hypercube edge."""
    d = u ^ v
    return d.bit_length() - 1


def random_matching(G, rng, target_size=None, max_size=None):
    """A random (not necessarily maximal or maximum) matching of G."""
    edges = list(G.edges())
    rng.shuffle(edges)
    matched = set()
    M = []
    for u, v in edges:
        if u in matched or v in matched:
            continue
        M.append((u, v))
        matched.add(u)
        matched.add(v)
        if target_size is not None and len(M) >= target_size:
            break
        if max_size is not None and len(M) >= max_size:
            break
    return M


def random_maximal_matching(G, rng):
    """A maximal matching (can't add any more edges) -- greedy random
    order. This is the family flagged in the literature as the
    genuinely tricky, under-studied case (perfect matchings are already
    proven safe; maximal-but-not-perfect ones are not)."""
    edges = list(G.edges())
    rng.shuffle(edges)
    matched = set()
    M = []
    for u, v in edges:
        if u in matched or v in matched:
            continue
        M.append((u, v))
        matched.add(u)
        matched.add(v)
    return M


def extends_to_hamiltonian_cycle(G, matching, max_iters=200, time_limit_per_solve=None):
    """SAT-based check (lazy subtour elimination): does a Hamiltonian
    cycle of G exist that contains every edge in `matching`? Returns
    (result, cycle_edges_or_None, iterations, status) where result is
    True/False/None (None = gave up after max_iters without resolving --
    inconclusive, NOT a proof of non-existence)."""
    nodes = list(G.nodes())
    n = len(nodes)
    edges = list(G.edges())
    matching_set = set(frozenset(e) for e in matching)

    vpool = IDPool()
    evar = {}
    for u, v in edges:
        evar[frozenset((u, v))] = vpool.id(('e', u, v))

    base_clauses = []
    # degree-2 constraint at every vertex among selected edges
    for v in nodes:
        incident = [evar[frozenset((v, u))] for u in G.neighbors(v)]
        enc = CardEnc.equals(lits=incident, bound=2, vpool=vpool, encoding=EncType.seqcounter)
        base_clauses.extend(enc.clauses)
    # force matching edges to be selected
    for e in matching:
        base_clauses.append([evar[frozenset(e)]])

    extra_clauses = []
    with Glucose4(bootstrap_with=base_clauses) as solver:
        for it in range(max_iters):
            for c in extra_clauses[-1:] if extra_clauses else []:
                solver.add_clause(c)
            sat = solver.solve()
            if not sat:
                return False, None, it + 1, 'UNSAT'
            model = set(solver.get_model())
            selected = [e for e in edges if evar[frozenset(e)] in model]
            H = nx.Graph()
            H.add_nodes_from(nodes)
            H.add_edges_from(selected)
            # every vertex should have degree exactly 2 by construction;
            # check if H is a SINGLE cycle covering all vertices
            components = list(nx.connected_components(H))
            if len(components) == 1 and all(H.degree(v) == 2 for v in nodes):
                return True, selected, it + 1, 'SAT_HAMILTONIAN'
            # subtour(s) found -- block each component's exact edge set
            # (at least one of its internal edges must be excluded)
            for comp in components:
                if len(comp) == n:
                    continue  # shouldn't happen given the check above, but be safe
                comp_edges = [e for e in selected if e[0] in comp and e[1] in comp]
                if not comp_edges:
                    continue
                block_clause = [-evar[frozenset(e)] for e in comp_edges]
                solver.add_clause(block_clause)
        return None, None, max_iters, 'GAVE_UP'


def verify_extension(G, matching, cycle_edges):
    """Independent from-scratch check: cycle_edges must contain every
    matching edge, form a single cycle, and cover every vertex of G."""
    n = G.number_of_nodes()
    matching_set = set(frozenset(e) for e in matching)
    cycle_set = set(frozenset(e) for e in cycle_edges)
    if not matching_set.issubset(cycle_set):
        return False
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(cycle_edges)
    if H.number_of_edges() != n:
        return False
    if any(H.degree(v) != 2 for v in G.nodes()):
        return False
    if not nx.is_connected(H):
        return False
    # also must be a SUBGRAPH of G (all edges real hypercube edges)
    for e in cycle_edges:
        if not G.has_edge(*e):
            return False
    return True
