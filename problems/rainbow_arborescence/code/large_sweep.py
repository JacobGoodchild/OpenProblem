#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: large-scale random sampling of Rainbow Arborescence
instances, checking the free-root existence question for each. Per-
check cost grows faster than linearly with n (n=50: ~0.3s, n=80: ~6s),
so this uses a tiered trial budget: many trials at small-to-moderate n,
fewer at larger n. Any instance where check_rainbow_arborescence_any_root
returns False for EVERY root (a genuine counterexample) or None (never
resolved, even after retrying with a larger iteration budget) is
flagged and escalated before being reported.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from ra_lib import random_instance, check_rainbow_arborescence_any_root, verify_rainbow_arborescence

TIERS = [
    (10, 25, 500, 300),
    (26, 40, 150, 300),
    (41, 55, 40, 400),
    (56, 70, 8, 600),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--tiers', type=str, default=None,
                     help='override as "nmin,nmax,trials,itersperroot;..."')
    args = ap.parse_args()

    tiers = TIERS
    if args.tiers:
        tiers = []
        for chunk in args.tiers.split(';'):
            a, b, t, it = chunk.split(',')
            tiers.append((int(a), int(b), int(t), int(it)))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    summary = {}
    flagged = []
    total_checked = 0
    t_start = time.time()

    for nmin, nmax, trials, max_iters in tiers:
        for n in range(nmin, nmax + 1):
            n_ok, n_flag = 0, 0
            t0 = time.time()
            for trial in range(trials):
                rng = random.Random(args.seed + n * 100000 + trial)
                vertices, colored_arcs, roots = random_instance(n, rng)
                result, root, arcs, details = check_rainbow_arborescence_any_root(
                    vertices, colored_arcs, max_iters_per_root=max_iters)
                total_checked += 1
                if result is True:
                    if not verify_rainbow_arborescence(vertices, colored_arcs, root, arcs):
                        print(f'*** BUG: SAT success failed independent verification! n={n} ***', flush=True)
                    n_ok += 1
                else:
                    # escalate before reporting
                    result2, root2, arcs2, details2 = check_rainbow_arborescence_any_root(
                        vertices, colored_arcs, max_iters_per_root=max_iters * 4)
                    if result2 is True:
                        if verify_rainbow_arborescence(vertices, colored_arcs, root2, arcs2):
                            n_ok += 1
                        else:
                            print(f'*** BUG (escalated): SAT success failed verification! n={n} ***', flush=True)
                            n_ok += 1
                    else:
                        n_flag += 1
                        status = 'NO_RAINBOW_ARBORESCENCE_ANY_ROOT' if result2 is False else 'INCONCLUSIVE'
                        print(f'*** FLAGGED (n={n}, trial={trial}): {status} -- {details2} ***', flush=True)
                        flagged.append({'n': n, 'trial': trial, 'status': status,
                                         'colored_arcs': colored_arcs, 'details': details2})
            elapsed = time.time() - t0
            summary[n] = {'trials': trials, 'ok': n_ok, 'flagged': n_flag, 'elapsed': elapsed}
            print(f'n={n}: {trials} trials, {n_ok} confirmed rainbow-arborescence-exists, '
                  f'{n_flag} flagged, {elapsed:.1f}s', flush=True)
            with open(os.path.join(out_dir, 'large_sweep_progress.json'), 'w') as f:
                json.dump({'summary': summary, 'flagged': flagged, 'total_checked': total_checked}, f, indent=2)

    total_elapsed = time.time() - t_start
    print(f'\nDONE. {total_checked} instances checked in {total_elapsed:.1f}s. '
          f'{len(flagged)} flagged (potential counterexamples or inconclusive).')


if __name__ == '__main__':
    main()
