"""
Van der Waerden numbers: W(r,k) is the smallest N such that every
r-coloring of {1,...,N} contains a monochromatic arithmetic progression
of length k. Only a handful of exact values are known at all (this is a
genuinely hard problem -- upper bounds are believed extremely weak, e.g.
W(2,7) is only known to lie somewhere between 3703 and a number as large
as 2^48).

This module builds and solves the standard 2-color instance as a SAT
problem: one boolean variable per integer 1..N (True = color A, False =
color B), and for every length-k arithmetic progression within {1,...,N},
two clauses forbidding it from being monochromatic (all-True or
all-False). If the SAT solver finds W(2,k) is SATISFIABLE for N, that
means a valid 2-coloring exists with NO monochromatic k-term AP -- i.e.
W(2,k) > N (a lower-bound witness, extractable as an explicit coloring).
If UNSATISFIABLE, W(2,k) <= N.

This is exactly the standard technique in the literature for computing/
bounding van der Waerden numbers (see e.g. Herwig, Heule, van Lambalgen &
van Maaren 2007; Ahmed, Kullmann & Snevily). Nothing novel about the
method -- the value here is in applying it directly to the specific
currently-open question of whether the published W(2,7) lower bound of
3703 can be extended.
"""
from pysat.solvers import Glucose4
from pysat.formula import CNF


def all_length_k_aps(N, k):
    """Yield every length-k arithmetic progression within {1,...,N} as a
    tuple of positions."""
    for d in range(1, (N - 1) // (k - 1) + 1):
        max_start = N - (k - 1) * d
        for a in range(1, max_start + 1):
            yield tuple(a + i * d for i in range(k))


def build_cnf(N, k):
    cnf = CNF()
    for ap in all_length_k_aps(N, k):
        cnf.append(list(ap))          # forbid all-False
        cnf.append([-x for x in ap])  # forbid all-True
    return cnf


def check_vdw(N, k, time_limit=None):
    """Returns ('SAT', coloring) or ('UNSAT', None) or (None, None) if the
    solver didn't finish (only relevant if a time limit / interrupt is
    used -- Glucose4 here runs to completion, no built-in time limit, so
    callers should wrap this in their own timeout if needed)."""
    cnf = build_cnf(N, k)
    solver = Glucose4(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    if sat:
        model = solver.get_model()
        coloring = {abs(v): (v > 0) for v in model}
        solver.delete()
        return 'SAT', coloring
    solver.delete()
    return 'UNSAT', None


def verify_coloring(coloring, N, k):
    """Independent, from-scratch check: does this coloring (dict i->bool)
    really avoid every monochromatic length-k AP in {1,...,N}?"""
    for ap in all_length_k_aps(N, k):
        colors = {coloring[i] for i in ap}
        if len(colors) == 1:
            return False, ap
    return True, None
