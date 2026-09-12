"""
Schur numbers: S(k) is the largest N such that {1,...,N} can be
partitioned into k "sum-free" classes -- sets containing no a,b,c (a,b not
necessarily distinct) with a+b=c. S(k)+1 is then the smallest N such that
EVERY k-coloring of {1,...,N} has a monochromatic solution to a+b=c.

Known exactly: S(1)=1, S(2)=4, S(3)=13, S(4)=44, S(5)=160 (the last
established by a massive 2017 SAT proof, "Schur Number Five"). S(6) is
open: only a lower bound is published (S(6) >= 536).

This module provides:
  - an exact SAT check (via pysat) for small k, validated against all 5
    known values
  - a local search (multi-color WalkSAT-style) for larger N/k, since (as
    established on the van der Waerden problem earlier in this project) a
    raw complete SAT solve does not scale to these sizes in this
    environment.
"""
import itertools
from pysat.solvers import Glucose4
from pysat.formula import CNF, IDPool


def check_schur_sat(N, k):
    """Exact SAT check: can {1,...,N} be partitioned into k sum-free sets?
    One-hot encoding: k boolean variables per integer (exactly one true).
    Returns ('SAT', coloring) or ('UNSAT', None)."""
    vpool = IDPool()
    cnf = CNF()

    def var(i, c):
        return vpool.id(('x', i, c))

    for i in range(1, N + 1):
        lits = [var(i, c) for c in range(k)]
        cnf.append(lits)  # at least one color
        for c1, c2 in itertools.combinations(range(k), 2):
            cnf.append([-var(i, c1), -var(i, c2)])  # at most one color

    for a in range(1, N + 1):
        for b in range(a, N + 1):
            c_val = a + b
            if c_val > N:
                break
            for color in range(k):
                cnf.append([-var(a, color), -var(b, color), -var(c_val, color)])

    solver = Glucose4(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    if sat:
        model = set(solver.get_model())
        coloring = {}
        for i in range(1, N + 1):
            for c in range(k):
                if var(i, c) in model:
                    coloring[i] = c
                    break
        solver.delete()
        return 'SAT', coloring
    solver.delete()
    return 'UNSAT', None


def verify_schur_coloring(coloring, N, k):
    """Independent from-scratch check that coloring (dict i->color in
    0..k-1) has no monochromatic a+b=c with a,b,c in {1,...,N}."""
    for a in range(1, N + 1):
        for b in range(a, N + 1):
            c_val = a + b
            if c_val > N:
                break
            if coloring[a] == coloring[b] == coloring[c_val]:
                return False, (a, b, c_val)
    return True, None


def local_search_schur(N, k, rng, max_flips=200000, restart_after_stuck=20000, noise=0.3):
    """WalkSAT-style local search for a sum-free k-coloring of {1,...,N}:
    minimize the count of monochromatic a+b=c violations via greedy
    recoloring (try all k colors for a position involved in a violation,
    keep whichever reduces total violations most), with noise for
    diversification and periodic restarts when stuck."""
    coloring = [rng.randrange(k) for _ in range(N + 1)]  # 1-indexed, [0] unused

    # precompute triples (a,b,c) with a+b=c, a<=b, all in [1,N]
    triples = []
    for a in range(1, N + 1):
        for b in range(a, N + 1):
            c_val = a + b
            if c_val > N:
                break
            triples.append((a, b, c_val))

    pos_to_triples = [[] for _ in range(N + 1)]
    for idx, (a, b, c_val) in enumerate(triples):
        pos_to_triples[a].append(idx)
        pos_to_triples[b].append(idx)
        pos_to_triples[c_val].append(idx)

    def triple_is_mono(idx):
        a, b, c_val = triples[idx]
        return coloring[a] == coloring[b] == coloring[c_val]

    violated_set = set(idx for idx in range(len(triples)) if triple_is_mono(idx))

    def simulate_recolor(pos, new_color):
        old = coloring[pos]
        if old == new_color:
            return 0
        affected = pos_to_triples[pos]
        before = {idx: triple_is_mono(idx) for idx in affected}
        coloring[pos] = new_color
        delta = 0
        for idx in affected:
            now = triple_is_mono(idx)
            if now and not before[idx]:
                delta += 1
            elif not now and before[idx]:
                delta -= 1
        coloring[pos] = old
        return delta

    def apply_recolor(pos, new_color):
        affected = pos_to_triples[pos]
        before = {idx: triple_is_mono(idx) for idx in affected}
        coloring[pos] = new_color
        for idx in affected:
            now = triple_is_mono(idx)
            if now and not before[idx]:
                violated_set.add(idx)
            elif not now and before[idx]:
                violated_set.discard(idx)

    stuck_counter = 0
    for _ in range(max_flips):
        if not violated_set:
            break
        idx = rng.choice(tuple(violated_set)) if len(violated_set) <= 200 \
            else rng.sample(list(violated_set), 1)[0]
        a, b, c_val = triples[idx]
        pos = rng.choice((a, b, c_val))

        if rng.random() < noise:
            new_color = rng.randrange(k)
        else:
            best_color, best_delta = coloring[pos], 0
            for col in range(k):
                if col == coloring[pos]:
                    continue
                d = simulate_recolor(pos, col)
                if d < best_delta:
                    best_delta, best_color = d, col
            new_color = best_color

        apply_recolor(pos, new_color)

        stuck_counter += 1
        if stuck_counter >= restart_after_stuck:
            stuck_counter = 0
            chunk = rng.sample(range(1, N + 1), min(N, max(20, N // 20)))
            for p in chunk:
                coloring[p] = rng.randrange(k)
            violated_set = set(idx for idx in range(len(triples)) if triple_is_mono(idx))

    return {i: coloring[i] for i in range(1, N + 1)}, len(violated_set)
