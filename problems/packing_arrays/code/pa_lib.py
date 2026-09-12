"""
Tools for attacking PACKING ARRAYS: PA(N; 2, k, g) is an N x k array
over a g-ary alphabet {0,...,g-1} such that for every pair of columns
(i,j) and every ordered symbol pair (a,b), AT MOST ONE row has that
exact (a,b) pair in columns (i,j) -- i.e. every pair of columns,
restricted to their N row-values, forms a set of N pairwise-DISTINCT
ordered pairs. The central open question (Chateauneuf, Colbourn, Kreher
and many follow-ups; a Jan 2025 paper "Using Code Generation to Solve
Open Instances of Combinatorial Design Problems" specifically improved
several small open Packing Array instances, e.g. PA(9,6): N=14,
PA(11,7): N=15, as NEW lower-bound constructions) is: for given k,g,
what is the MAXIMUM possible N?

Universal upper bound: for ANY fixed pair of columns, there are only
g^2 possible ordered symbol pairs, so N <= g^2 always. When k <= g+1,
this bound is achievable (equivalent to a set of k-2 mutually
orthogonal Latin squares of order g existing -- e.g. k=5,g=10 achieving
N=100 is EXACTLY the "do 3 MOLS of order 10 exist" question, a
different famous 60+-year-old open problem this project already
assessed as intractable to brute-force -- deliberately avoided here).
The genuinely interesting, more tractable regime is k notably LARGER
than g+1, where the trivial g^2 bound is impossible to reach and the
true maximum sits well below it -- exactly the regime of the cited
literature examples.

SAT encoding: one-hot variable x[r][c][s] per (row, column, symbol).
Each cell gets exactly one symbol (standard exactly-one). For every
pair of columns (c1,c2) and every symbol pair (a,b), at most one row
can have (x[r][c1][a] AND x[r][c2][b]) -- via auxiliary AND variables
and an at-most-one cardinality constraint, same "auxiliary + exactly/
at-most-one" pattern used for MOLS orthogonality earlier in this
project.
"""
import itertools

from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def build_pa_cnf(N, k, g):
    vpool = IDPool()

    def xvar(r, c, s):
        return vpool.id(('x', r, c, s))

    clauses = []
    # each cell exactly one symbol
    for r in range(N):
        for c in range(k):
            lits = [xvar(r, c, s) for s in range(g)]
            clauses.append(lits)  # at least one
            enc = CardEnc.atmost(lits=lits, bound=1, vpool=vpool, encoding=EncType.seqcounter)
            clauses.extend(enc.clauses)

    # packing constraint: for every column pair, every symbol pair,
    # at most one row matches both
    for c1, c2 in itertools.combinations(range(k), 2):
        for a in range(g):
            for b in range(g):
                row_aux = []
                for r in range(N):
                    av = vpool.id(('aux', r, c1, c2, a, b))
                    x1 = xvar(r, c1, a)
                    x2 = xvar(r, c2, b)
                    clauses.append([-av, x1])
                    clauses.append([-av, x2])
                    clauses.append([av, -x1, -x2])
                    row_aux.append(av)
                enc = CardEnc.atmost(lits=row_aux, bound=1, vpool=vpool, encoding=EncType.seqcounter)
                clauses.extend(enc.clauses)

    return clauses, vpool, xvar


def solve_pa(N, k, g, time_limit=None):
    """Returns (sat, array) -- array is an N x k list of symbols if SAT."""
    clauses, vpool, xvar = build_pa_cnf(N, k, g)
    with Glucose4(bootstrap_with=clauses) as solver:
        if time_limit:
            # pysat's Glucose4 has no native timeout; caller should wrap
            # this call with a process-level timeout if needed
            pass
        sat = solver.solve()
        if not sat:
            return False, None
        model = set(solver.get_model())
        array = [[None] * k for _ in range(N)]
        for r in range(N):
            for c in range(k):
                for s in range(g):
                    if xvar(r, c, s) in model:
                        array[r][c] = s
                        break
        return True, array


def verify_packing_array(array, k, g):
    """Independent from-scratch check."""
    N = len(array)
    for row in array:
        if len(row) != k:
            return False
        if any(not (0 <= s < g) for s in row):
            return False
    for c1, c2 in itertools.combinations(range(k), 2):
        seen = set()
        for row in array:
            pair = (row[c1], row[c2])
            if pair in seen:
                return False
            seen.add(pair)
    return True
