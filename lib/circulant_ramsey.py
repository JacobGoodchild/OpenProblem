"""
Search for lower-bound Ramsey graphs of the classical diagonal-ish form
R(3, k) using CIRCULANT (Cayley) graphs on Z_n.

Background: R(3,k) is the smallest N such that every graph on N vertices
contains either a triangle or an independent set of size k. A "Ramsey
graph" witnessing R(3,k) > n is a triangle-free graph on n vertices with
independence number < k. Finding one directly PROVES R(3,k) >= n+1.

Circulant graphs (vertices = Z_n, edges defined by a difference/connection
set S closed under negation mod n) are the standard, long-established
technique for finding such witnesses -- essentially all of the best known
lower-bound constructions for small R(3,k) in the literature are circulant
or close to it (this is not a novel idea; it's the right tool, reused
faithfully). The appeal is purely computational: instead of searching over
all 2^C(n,2) graphs on n vertices, you search over the vastly smaller space
of 2^floor(n/2) connection sets, and the resulting graph is automatically
vertex-transitive (regular), which tends to be favourable for minimizing
independence number for a given edge density.

Triangle-free check, done via pure arithmetic (fast): a circulant graph
C_n(S) (S subset of {1,...,floor(n/2)}, D = S union {n-s : s in S} the
full symmetric difference set) contains a triangle iff there exist
a, b in D, a != b, with (b - a) mod n also in D. This is O(|D|^2), not
O(n^3) -- checking a candidate connection set is essentially instant.

Independence number check: done via exact ILP (max independent set),
formulated as a FEASIBILITY query "does an independent set of size >= k
exist?" rather than full optimization, since a definite yes/no is all we
need and is typically much faster for the solver to establish than the
exact optimum.
"""
import itertools
import pulp


def difference_set(S, n):
    """Given S (set of positive differences <= n//2), return the full
    symmetric difference set D = S union {n-s : s in S} (mod n), used to
    build the circulant graph's edge relation."""
    D = set()
    for s in S:
        D.add(s % n)
        D.add((n - s) % n)
    D.discard(0)
    return D


def is_triangle_free(S, n):
    D = difference_set(S, n)
    D_list = list(D)
    for i in range(len(D_list)):
        a = D_list[i]
        for j in range(i + 1, len(D_list)):
            b = D_list[j]
            if (b - a) % n in D:
                return False
            if (a - b) % n in D:
                return False
    return True


def is_clique_free(S, n, s):
    """Check whether the circulant graph C_n(S) has no clique of size s
    (generalizes is_triangle_free, which is the s=3 case). By vertex-
    transitivity it suffices to check whether there exist s-1 elements of
    D = difference_set(S,n) (the "neighbors of vertex 0") that are
    pairwise also related by an element of D -- i.e. a clique of size s-1
    within D's own "graph structure" (D as a vertex set, with the same
    connection rule) union vertex 0 gives a clique of size s.

    Implemented via straightforward backtracking over D (size is at most
    n-1, but for the graphs of interest here |D| is small, so this is
    fast) -- looking for s-1 mutually D-connected elements."""
    D = difference_set(S, n)
    D_list = sorted(D)

    def extends(clique, cand):
        for c in clique:
            diff = (cand - c) % n
            if diff not in D and (n - diff) % n not in D:
                return False
        return True

    def backtrack(start_idx, clique):
        if len(clique) == s - 1:
            return True
        for i in range(start_idx, len(D_list)):
            cand = D_list[i]
            if extends(clique, cand):
                if backtrack(i + 1, clique + [cand]):
                    return True
        return False

    return not backtrack(0, [])


def circulant_edges(S, n):
    D = difference_set(S, n)
    edges = []
    for i in range(n):
        for d in D:
            j = (i + d) % n
            if j > i:
                edges.append((i, j))
    return edges


def has_independent_set_of_size(edges, n, k, time_limit=15):
    """Exact ILP feasibility check: does the graph (n vertices, given
    edges) have an independent set of size >= k? Returns (bool, solution)
    where solution is the list of chosen vertices if found (else None)."""
    prob = pulp.LpProblem('indep_set_feasibility', pulp.LpMaximize)
    x = [pulp.LpVariable(f'x_{i}', cat='Binary') for i in range(n)]
    prob += pulp.lpSum(x)  # maximize (helps CBC find a size->=k witness fast)
    for (u, v) in edges:
        prob += x[u] + x[v] <= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)
    val = pulp.value(prob.objective)
    if val is None:
        return None, None  # solver gave up / no info
    if val >= k - 1e-6:
        chosen = [i for i in range(n) if pulp.value(x[i]) > 0.5]
        return True, chosen
    return False, None


def independence_number(edges, n, time_limit=30):
    """Exact max independent set size via ILP (full optimization, not just
    feasibility) -- used only for final, rigorous confirmation of a
    candidate that already passed the fast feasibility filter."""
    prob = pulp.LpProblem('indep_set_exact', pulp.LpMaximize)
    x = [pulp.LpVariable(f'x_{i}', cat='Binary') for i in range(n)]
    prob += pulp.lpSum(x)
    for (u, v) in edges:
        prob += x[u] + x[v] <= 1
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)
    return pulp.value(prob.objective)
