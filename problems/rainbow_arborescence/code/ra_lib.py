"""
Tools for attacking the Rainbow Arborescence Conjecture (Berczi, Kiraly,
Yamaguchi, Yokoi, Dec 2024, arXiv:2412.15457): take a digraph on n
vertices formed as the union of n-1 spanning arborescences, each given
a distinct color. Conjecture: there is always a spanning arborescence
using exactly one arc of each color. Proven only for the case where the
underlying undirected graph is a cycle (Nov 2025, arXiv:2511.04953).
General case open, no known counterexample.

IMPORTANT complexity fact (confirmed via multiple search sources, since
arxiv.org itself is network-blocked in this environment): testing
whether a rainbow arborescence exists rooted at a SPECIFIC given vertex
is NP-complete in general, even restricted to these union-of-n-1-
arborescences instances. This rules out a simple polynomial check for
the fixed-root question. We instead use SAT (tractable in practice for
the small n this session can reach) to check each candidate root, one
at a time: the conjecture (free-root version) holds for an instance iff
AT LEAST ONE of the n candidate roots admits a rainbow arborescence.

Root-checking SAT encoding (mirrors the Hamiltonian-cycle-with-required-
edges lazy-elimination pattern used for the Ruskey-Savage problem in
this same project): binary variable per arc; in-degree exactly 1 for
every non-root vertex, 0 for the root; AT MOST one arc selected per
color (combined with n-1 arcs total across n-1 colors, this forces
EXACTLY one arc per color). A satisfying assignment might still contain
a cycle not through the root (a "rho-shaped" functional graph, not a
tree) -- checked directly (fast) and, if found, blocked with a clause
before resolving (lazy elimination), exactly as for Hamiltonian cycles.
"""
import itertools
import random

import networkx as nx
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def random_arborescence(vertices, rng):
    """A uniformly random LABELED tree on `vertices` (via a random
    Prufer-like process using networkx), oriented as an arborescence
    away from a randomly chosen root. Returns (root, list_of_arcs)."""
    n = len(vertices)
    if n == 1:
        return vertices[0], []
    # random tree via networkx's random_tree helper on a 0..n-1 index
    # set, then relabel to the actual vertex ids
    idx_tree = nx.random_labeled_tree(n, seed=rng.randint(0, 2**31))
    relabel = {i: vertices[i] for i in range(n)}
    T = nx.relabel_nodes(idx_tree, relabel)
    root = rng.choice(vertices)
    arcs = []
    # orient away from root via BFS
    for u, v in nx.bfs_edges(T, root):
        arcs.append((u, v))
    return root, arcs


def random_instance(n, rng):
    """Generate a valid Rainbow Arborescence instance: n-1 independently
    random spanning arborescences (each its own random root, possibly
    different from each other), unioned together with a distinct color
    per arborescence. Returns (vertices, colored_arcs) where
    colored_arcs is a list of (u, v, color) with color in 0..n-2.
    Parallel arcs of different colors between the same ordered pair are
    allowed (and do occur) -- checked and kept, matching the problem's
    own definition (a digraph, arcs distinguished by color)."""
    vertices = list(range(n))
    colored_arcs = []
    roots = []
    for color in range(n - 1):
        root, arcs = random_arborescence(vertices, rng)
        roots.append(root)
        for u, v in arcs:
            colored_arcs.append((u, v, color))
    return vertices, colored_arcs, roots


def verify_is_arborescence(vertices, arcs, root):
    """Independent from-scratch check that `arcs` forms a valid
    spanning arborescence of `vertices` rooted at `root`."""
    n = len(vertices)
    if len(arcs) != n - 1:
        return False
    indeg = {v: 0 for v in vertices}
    for u, v in arcs:
        indeg[v] += 1
    if indeg[root] != 0:
        return False
    if any(indeg[v] != 1 for v in vertices if v != root):
        return False
    # every vertex must reach the root by following predecessor arcs
    parent = {v: u for u, v in arcs}
    for v in vertices:
        seen = set()
        cur = v
        while cur != root:
            if cur in seen:
                return False  # cycle
            seen.add(cur)
            if cur not in parent:
                return False
            cur = parent[cur]
    return True


def check_rainbow_arborescence_at_root(vertices, colored_arcs, root, max_iters=300):
    """SAT check (lazy cycle elimination): does a rainbow arborescence
    (exactly one arc per color) rooted at `root` exist? Returns
    (result, arcs_or_None, iters, status). result is True/False/None
    (None = gave up after max_iters, inconclusive)."""
    n = len(vertices)
    colors = sorted(set(c for _, _, c in colored_arcs))
    vpool = IDPool()
    avar = {}
    for i, (u, v, c) in enumerate(colored_arcs):
        avar[i] = vpool.id(('a', i))

    base_clauses = []
    # in-degree exactly 1 for non-root, 0 for root
    for v in vertices:
        incident_in = [avar[i] for i, (a, b, c) in enumerate(colored_arcs) if b == v]
        if v == root:
            for lit in incident_in:
                base_clauses.append([-lit])
        else:
            if not incident_in:
                return False, None, 0, 'NO_INCOMING_ARCS'  # trivially impossible
            enc = CardEnc.equals(lits=incident_in, bound=1, vpool=vpool, encoding=EncType.seqcounter)
            base_clauses.extend(enc.clauses)
    # at most one arc per color
    for c in colors:
        color_lits = [avar[i] for i, (u, v, cc) in enumerate(colored_arcs) if cc == c]
        enc = CardEnc.atmost(lits=color_lits, bound=1, vpool=vpool, encoding=EncType.seqcounter)
        base_clauses.extend(enc.clauses)

    with Glucose4(bootstrap_with=base_clauses) as solver:
        for it in range(max_iters):
            sat = solver.solve()
            if not sat:
                return False, None, it + 1, 'UNSAT'
            model = set(solver.get_model())
            selected_idx = [i for i in range(len(colored_arcs)) if avar[i] in model]
            selected = [(colored_arcs[i][0], colored_arcs[i][1], colored_arcs[i][2]) for i in selected_idx]
            selected_edges = [(u, v) for u, v, c in selected]
            if verify_is_arborescence(vertices, selected_edges, root):
                return True, selected, it + 1, 'SAT_ARBORESCENCE'
            # find the cycle(s) not reaching root and block them
            parent = {}
            parent_idx = {}
            for i in selected_idx:
                u, v, c = colored_arcs[i]
                parent[v] = u
                parent_idx[v] = i
            visited_global = set()
            blocked_any = False
            for v in vertices:
                if v == root or v in visited_global:
                    continue
                path = []
                cur = v
                local_seen = set()
                while cur != root and cur not in local_seen and cur in parent:
                    local_seen.add(cur)
                    path.append(cur)
                    cur = parent[cur]
                if cur != root:
                    # cycle found among `path` (the part from where the
                    # repeat starts) -- block: at least one of these
                    # vertices' selected in-arcs must differ
                    cyc_start = cur if cur in local_seen else path[0]
                    if cyc_start in local_seen:
                        cyc_vertices = path[path.index(cyc_start):] if cyc_start in path else path
                    else:
                        cyc_vertices = path
                    cyc_arc_idxs = [parent_idx[w] for w in cyc_vertices if w in parent_idx]
                    if cyc_arc_idxs:
                        solver.add_clause([-avar[i] for i in cyc_arc_idxs])
                        blocked_any = True
                visited_global.update(local_seen)
            if not blocked_any:
                # shouldn't happen if verify_is_arborescence returned False,
                # but guard against infinite loop
                return None, None, it + 1, 'STUCK'
        return None, None, max_iters, 'GAVE_UP'


def check_rainbow_arborescence_any_root(vertices, colored_arcs, max_iters_per_root=300):
    """The actual conjecture check: try every candidate root; the
    instance satisfies the (free-root) conjecture iff SOME root works.
    Returns (result, root_or_None, arcs_or_None, details)."""
    inconclusive_roots = []
    for root in vertices:
        result, arcs, iters, status = check_rainbow_arborescence_at_root(
            vertices, colored_arcs, root, max_iters_per_root)
        if result is True:
            return True, root, arcs, {'status': status, 'iters': iters}
        if result is None:
            inconclusive_roots.append((root, status, iters))
    if inconclusive_roots:
        return None, None, None, {'inconclusive_roots': inconclusive_roots}
    return False, None, None, {'all_roots_unsat': True}


def verify_rainbow_arborescence(vertices, colored_arcs, root, selected_arcs):
    """Independent from-scratch check. `selected_arcs` must be a list of
    EXACT (u, v, c) triples (the specific colored arc chosen -- not just
    endpoints, since parallel arcs of different colors between the same
    pair are allowed and a check that only looks at (u,v) can be fooled:
    it might find SOME valid color assignment via greedy search even
    when the SPECIFIC triples returned by the solver weren't actually a
    valid choice, or vice versa miss that a real assignment exists.
    Caught this exact bug empirically -- the original endpoint-only
    version reported false negatives at n=20+). Checks: (a) the (u,v)
    projection is a valid arborescence rooted at `root`, (b) every
    (u,v,c) triple is one of the colored arcs actually present in the
    instance, and (c) all c values across the triples are distinct."""
    edges = [(u, v) for u, v, c in selected_arcs]
    if not verify_is_arborescence(vertices, edges, root):
        return False
    colored_arcs_set = set(colored_arcs)
    colors_used = [c for u, v, c in selected_arcs]
    if len(set(colors_used)) != len(colors_used):
        return False  # a color repeated
    for triple in selected_arcs:
        if triple not in colored_arcs_set:
            return False  # not a real arc of the instance
    return True
