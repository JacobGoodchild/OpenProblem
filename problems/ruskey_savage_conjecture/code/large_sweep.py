#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: since a single Hamiltonian-cycle-extension check
turned out to be extremely fast even at Q8 (256 vertices, well under
0.1s per matching), this runs a LARGE-SCALE random sweep across
Q6/Q7/Q8 -- thousands of random matchings, weighted toward the
literature-flagged "maximal but not perfect" case (perfect matchings
are already proven safe by Fink) -- rather than a narrow hand-picked
sample. This is a genuine, if not exhaustive, extension of the
computational frontier past MathCheck's 2015 n=5 result: not a full
enumeration of all matchings (astronomically many), but real coverage
at sizes nobody appears to have tested before.

Any matching returning UNSAT, or GAVE_UP after a large iteration
budget, gets flagged and escalated to a much larger iteration budget
before being taken seriously -- a genuine UNSAT here would disprove a
30+-year-old conjecture and demands extreme scrutiny.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from rs_lib import hypercube, random_matching, random_maximal_matching, extends_to_hamiltonian_cycle, verify_extension


def run_trial(G, matching, max_iters=1500):
    t0 = time.time()
    result, cycle, iters, status = extends_to_hamiltonian_cycle(G, matching, max_iters=max_iters)
    elapsed = time.time() - t0
    verified = None
    if result is True:
        verified = verify_extension(G, matching, cycle)
    return result, cycle, iters, status, elapsed, verified


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dims', type=int, nargs='+', default=[6, 7, 8])
    ap.add_argument('--trials-per-dim', type=int, default=500)
    ap.add_argument('--frac-maximal', type=float, default=0.6)
    ap.add_argument('--max-iters', type=int, default=1500)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    summary = {}
    flagged = []

    for n in args.dims:
        G = hypercube(n)
        t0 = time.time()
        n_sat = 0
        n_flagged = 0
        min_iters, max_iters_seen = None, 0
        for trial in range(args.trials_per_dim):
            rng = random.Random(args.seed + n * 100000 + trial)
            if rng.random() < args.frac_maximal:
                M = random_maximal_matching(G, rng)
                kind = 'maximal'
            else:
                size = rng.randint(1, G.number_of_nodes() // 2)
                M = random_matching(G, rng, target_size=size)
                kind = 'random'

            result, cycle, iters, status, elapsed, verified = run_trial(G, M, args.max_iters)
            max_iters_seen = max(max_iters_seen, iters)
            if min_iters is None or iters < min_iters:
                min_iters = iters

            if result is True:
                n_sat += 1
                if not verified:
                    print(f'*** BUG: SAT result failed independent verification! n={n}, M={M} ***',
                          flush=True)
            else:
                # escalate before ever reporting -- much bigger budget
                n_flagged += 1
                print(f'  flagged: n={n}, kind={kind}, |M|={len(M)}, status={status}, '
                      f'{iters} iters -- escalating...', flush=True)
                result2, cycle2, iters2, status2, elapsed2, verified2 = run_trial(
                    G, M, max_iters=args.max_iters * 5)
                if result2 is True:
                    print(f'    -> resolved on escalation (verified={verified2}), {iters2} iters', flush=True)
                    n_sat += 1
                    n_flagged -= 1
                elif status2 == 'UNSAT':
                    print(f'\n*** GENUINE UNSAT (escalated, {iters2} iters): n={n}, matching={M} ***', flush=True)
                    print('*** THIS WOULD DISPROVE THE RUSKEY-SAVAGE CONJECTURE -- EXTREME SCRUTINY NEEDED ***',
                          flush=True)
                    flagged.append({'n': n, 'matching': M, 'status': 'UNSAT_ESCALATED', 'iters': iters2})
                else:
                    print(f'    -> STILL inconclusive after escalation ({iters2} iters, status={status2})',
                          flush=True)
                    flagged.append({'n': n, 'matching': M, 'status': 'GAVE_UP_ESCALATED', 'iters': iters2})

            if (trial + 1) % 100 == 0:
                print(f'  n={n}: {trial+1}/{args.trials_per_dim} trials, {n_sat} SAT, '
                      f'{n_flagged} still flagged, max_iters_seen={max_iters_seen}, '
                      f'{time.time()-t0:.1f}s elapsed', flush=True)

        elapsed = time.time() - t0
        summary[n] = {'trials': args.trials_per_dim, 'sat_confirmed': n_sat,
                       'still_flagged': n_flagged, 'min_iters': min_iters,
                       'max_iters_seen': max_iters_seen, 'elapsed': elapsed}
        print(f'DONE n={n}: {args.trials_per_dim} trials in {elapsed:.1f}s, {n_sat} confirmed SAT, '
              f'{n_flagged} still flagged after escalation.', flush=True)

        with open(os.path.join(out_dir, 'large_sweep_progress.json'), 'w') as f:
            json.dump({'summary': summary, 'flagged': flagged}, f, indent=2)

    print(f'\nALL DONE. Total flagged (genuinely unresolved or UNSAT) across all dims: {len(flagged)}')


if __name__ == '__main__':
    main()
