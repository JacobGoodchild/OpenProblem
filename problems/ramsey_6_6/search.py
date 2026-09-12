#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on R(6,6): published bounds 102 <= R(6,6) <= 160. The
lower bound (Kalbfleisch, 1966) is *older* than R(5,5)'s (Exoo, 1989) --
nearly 60 years without improvement, and it's listed by Epoch AI's
FrontierMath "open problems" collection as a genuinely notable unsolved
target. Same honest scoping caveat as R(5,5): we don't know whether
Kalbfleisch's actual 101-vertex construction is pure circulant, so this
searches the PURE circulant restriction only, using the exact same
r=2-color local search already built and validated for R(5,5)
(lib/multicolor_circulant.py, clique_sizes=[6,6] instead of [5,5]).
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.multicolor_circulant import local_search_multicolor, is_valid_coloring

CLIQUE_SIZES = [6, 6]


def try_n(n, time_budget, seed_base):
    deadline = time.time() + time_budget
    seed = seed_base
    while time.time() < deadline:
        rng = random.Random(seed)
        coloring, viol = local_search_multicolor(n, CLIQUE_SIZES, rng,
                                                   max_flips=60000, restart_after_stuck=4000)
        if viol == 0:
            if is_valid_coloring(coloring, n, CLIQUE_SIZES):
                return coloring
        seed += 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=50)
    ap.add_argument('--stop', type=int, default=101)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--time-per-n', type=float, default=25)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    largest_found = None
    results = {}

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    for n in range(args.start, args.stop + 1, args.step):
        t0 = time.time()
        coloring = try_n(n, args.time_per_n, args.seed + n * 1000)
        elapsed = time.time() - t0
        if coloring is not None:
            largest_found = n
            results[n] = {'found': True, 'sizes': [len(s) for s in coloring], 'elapsed': elapsed,
                          'coloring': [sorted(s) for s in coloring]}
            print(f'n={n}: FOUND valid pure-circulant (K6,K6)-avoiding 2-coloring '
                  f'(color sizes {[len(s) for s in coloring]}), {elapsed:.1f}s', flush=True)
        else:
            results[n] = {'found': False, 'elapsed': elapsed}
            print(f'n={n}: no valid circulant coloring found in {elapsed:.1f}s (does NOT prove '
                  f'none exists -- just that this search did not find one)', flush=True)

        with open(os.path.join(out_dir, 'search_progress.json'), 'w') as f:
            json.dump({'results': results, 'largest_found': largest_found}, f, indent=2)

    print(f'DONE. Largest n with a found pure-circulant witness: {largest_found}', flush=True)


if __name__ == '__main__':
    main()
