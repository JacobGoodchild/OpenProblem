"""
SAT encoding for the existence of k pairwise-orthogonal Latin squares of
order n (MOLS(n,k)), targeting the famous open question: do 3 mutually
orthogonal Latin squares of order 10 exist? (N(10) is known to be
between 2 and 6; whether it's >= 3 has been open for over 60 years,
since Bose-Shrikhande-Parker's 1959 disproof of Euler's conjecture
established N(10) >= 2.)

Variables: x[s][i][j][k] = True iff square s has value k in cell (i,j),
for s in 0..k_squares-1, i,j,k in 0..n-1.

Latin square constraints (per square s):
  - each cell (i,j) has exactly one value k
  - each row i has each value k exactly once (i.e. for fixed i,k,
    exactly one j with x[s][i][j][k])
  - each column j has each value k exactly once

Orthogonality constraint (per pair of squares s1<s2): the map
(i,j) -> (value in s1, value in s2) must be a bijection onto pairs
(a,b) in {0..n-1}^2 -- i.e. for every (a,b), exactly one cell (i,j) has
s1's value = a AND s2's value = b. We introduce auxiliary variables
z[s1][s2][i][j] = x[s1][i][j][a] AND x[s2][i][j][b] is handled by
instead directly working with "pair-value" variables: for a FIXED
(s1,s2,a,b), the "witness cells" are those where x[s1][i][j][a] AND
x[s2][i][j][b] both hold; we introduce one aux variable per (i,j) for
this AND, then an exactly-one constraint over the n^2 cells.
"""
import itertools
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def build_mols_cnf(n, k_squares, fixed_squares=None):
    """Build the CNF for k_squares pairwise-orthogonal Latin squares of
    order n. fixed_squares: optional list of length < k_squares giving
    already-fixed Latin square assignments (as n x n arrays of values)
    for the first len(fixed_squares) squares -- used to search for an
    extension of a KNOWN base pair, which is the practically tractable
    version of the MOLS(10) question (rather than searching for all
    k_squares simultaneously from scratch, which is far too large).
    Returns (cnf, vpool, x) where x[s][i][j][k] gives the variable id.
    """
    vpool = IDPool()
    fixed_squares = fixed_squares or []

    def xvar(s, i, j, k):
        return vpool.id(('x', s, i, j, k))

    cnf_clauses = []

    def add_exactly_one(vars_list):
        # exactly one true: at-least-one (one big clause) + pairwise/seq at-most-one
        cnf_clauses.append(list(vars_list))
        enc = CardEnc.atmost(lits=list(vars_list), bound=1, vpool=vpool, encoding=EncType.seqcounter)
        cnf_clauses.extend(enc.clauses)

    for s in range(k_squares):
        if s < len(fixed_squares):
            # fix all cell values for this square directly as unit clauses
            for i in range(n):
                for j in range(n):
                    val = fixed_squares[s][i][j]
                    cnf_clauses.append([xvar(s, i, j, val)])
            continue
        # each cell exactly one value
        for i in range(n):
            for j in range(n):
                add_exactly_one([xvar(s, i, j, k) for k in range(n)])
        # each row: each value exactly once
        for i in range(n):
            for k in range(n):
                add_exactly_one([xvar(s, i, j, k) for j in range(n)])
        # each column: each value exactly once
        for j in range(n):
            for k in range(n):
                add_exactly_one([xvar(s, i, j, k) for i in range(n)])

    # orthogonality between every pair of squares
    for s1, s2 in itertools.combinations(range(k_squares), 2):
        for a in range(n):
            for b in range(n):
                # aux var per cell = AND(x[s1][i][j][a], x[s2][i][j][b])
                cell_aux = []
                for i in range(n):
                    for j in range(n):
                        av = vpool.id(('aux', s1, s2, a, b, i, j))
                        x1 = xvar(s1, i, j, a)
                        x2 = xvar(s2, i, j, b)
                        # av <-> (x1 AND x2)
                        cnf_clauses.append([-av, x1])
                        cnf_clauses.append([-av, x2])
                        cnf_clauses.append([av, -x1, -x2])
                        cell_aux.append(av)
                add_exactly_one(cell_aux)

    return cnf_clauses, vpool, xvar


def solve_mols(n, k_squares, fixed_squares=None, time_limit=None):
    """Returns (sat, squares) where squares is a list of n x n arrays
    (one per square) if SAT, else None. time_limit currently unused by
    Glucose4's basic interface (pysat doesn't expose a timeout directly
    for this solver -- callers should use a process-level timeout)."""
    cnf_clauses, vpool, xvar = build_mols_cnf(n, k_squares, fixed_squares)
    with Glucose4(bootstrap_with=cnf_clauses) as solver:
        sat = solver.solve()
        if not sat:
            return False, None
        model = set(solver.get_model())
        squares = []
        for s in range(k_squares):
            sq = [[None] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        if xvar(s, i, j, k) in model:
                            sq[i][j] = k
                            break
            squares.append(sq)
        return True, squares


def verify_latin_square(sq, n):
    for row in sq:
        if sorted(row) != list(range(n)):
            return False
    for j in range(n):
        col = [sq[i][j] for i in range(n)]
        if sorted(col) != list(range(n)):
            return False
    return True


def verify_orthogonal(sq1, sq2, n):
    pairs = set()
    for i in range(n):
        for j in range(n):
            pairs.add((sq1[i][j], sq2[i][j]))
    return len(pairs) == n * n
