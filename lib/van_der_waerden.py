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


def local_search_coloring(N, k, rng, max_flips=200000, restart_after_stuck=20000, noise=0.3):
    """Stochastic local search for a 2-coloring of {1,...,N} with NO
    monochromatic length-k AP: start random, repeatedly flip the color of
    a vertex involved in the most currently-violated (monochromatic) APs
    (a standard "min-conflicts"-style heuristic), with occasional random
    restarts of a portion of the coloring when stuck. This is much faster
    than a plain CDCL SAT solve at this problem's scale (a raw Glucose4
    call on a single ~2.3M-clause N=3703 instance did not finish in 300s
    in practice) and is closer to how many actual van der Waerden
    lower-bound records in the literature were originally found (a
    complete SAT/CDCL proof is really only needed for the UPPER bound
    direction -- proving UNSAT -- not for finding a satisfying witness).

    Returns (coloring_dict, num_violations) -- if num_violations==0, a
    valid coloring was found (verify independently with verify_coloring
    before trusting it)."""
    coloring = [rng.random() < 0.5 for _ in range(N + 1)]  # 1-indexed, [0] unused

    aps = list(all_length_k_aps(N, k))
    # position -> list of AP indices it participates in
    pos_to_aps = [[] for _ in range(N + 1)]
    for idx, ap in enumerate(aps):
        for p in ap:
            pos_to_aps[p].append(idx)

    def ap_is_mono(idx):
        ap = aps[idx]
        c0 = coloring[ap[0]]
        return all(coloring[p] == c0 for p in ap[1:])

    violated_set = set(idx for idx in range(len(aps)) if ap_is_mono(idx))

    def simulate_delta(pos):
        """Read-only: net change in violation count if pos were flipped,
        without mutating any tracking state."""
        affected = pos_to_aps[pos]
        before = {a: ap_is_mono(a) for a in affected}
        coloring[pos] = not coloring[pos]
        delta = 0
        for a in affected:
            now = ap_is_mono(a)
            if now and not before[a]:
                delta += 1
            elif not now and before[a]:
                delta -= 1
        coloring[pos] = not coloring[pos]  # undo
        return delta

    def apply_flip(pos):
        """Actually flip pos and update violated_set correctly."""
        affected = pos_to_aps[pos]
        before = {a: ap_is_mono(a) for a in affected}
        coloring[pos] = not coloring[pos]
        for a in affected:
            now = ap_is_mono(a)
            if now and not before[a]:
                violated_set.add(a)
            elif not now and before[a]:
                violated_set.discard(a)

    stuck_counter = 0
    for flip_num in range(max_flips):
        if not violated_set:
            break
        idx = rng.choice(tuple(violated_set)) if len(violated_set) <= 200 \
            else rng.sample(list(violated_set), 1)[0]
        ap = aps[idx]

        if rng.random() < noise:
            pos = rng.choice(ap)  # WalkSAT-style random diversification move
        else:
            order = list(ap)
            rng.shuffle(order)
            best_pos, best_delta = order[0], simulate_delta(order[0])
            for p in order[1:]:
                d = simulate_delta(p)
                if d < best_delta:
                    best_delta, best_pos = d, p
            pos = best_pos

        apply_flip(pos)

        stuck_counter += 1
        if stuck_counter >= restart_after_stuck:
            stuck_counter = 0
            chunk = rng.sample(range(1, N + 1), min(N, max(20, N // 20)))
            for p in chunk:
                coloring[p] = rng.random() < 0.5
            violated_set = set(idx for idx in range(len(aps)) if ap_is_mono(idx))

    return {i: coloring[i] for i in range(1, N + 1)}, len(violated_set)


def verify_coloring(coloring, N, k):
    """Independent, from-scratch check: does this coloring (dict i->bool)
    really avoid every monochromatic length-k AP in {1,...,N}?"""
    for ap in all_length_k_aps(N, k):
        colors = {coloring[i] for i in ap}
        if len(colors) == 1:
            return False, ap
    return True, None
