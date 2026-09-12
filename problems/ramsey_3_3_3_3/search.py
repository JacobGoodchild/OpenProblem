#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on R(3,3,3,3): the classical 4-color diagonal Ramsey
number, all four colors forbidding a triangle. Published bounds:
51 <= R(3,3,3,3) <= 62. The lower bound (Chung, 1973) is over 50 years
old; the upper bound comes from a 100+-page proof (Kramer, 2006), who
also conjectured the true value IS 62 -- i.e. many believe the lower
bound is the one far from the truth, which makes finding ANY witness
above n=50 an interesting (if very unlikely to succeed) thing to check
computationally, not a hopeless "everyone already looked here" search.

Same tooling as R(3,3,5)/R(5,5)/R(6,6): lib/multicolor_circulant.py,
this time with r=4 colors, all forbidding K3. No new library code.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.multicolor_circulant import local_search_multicolor, is_valid_coloring

CLIQUE_SIZES = [3, 3, 3, 3]


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
    ap.add_argument('--start', type=int, default=20)
    ap.add_argument('--stop', type=int, default=55)
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
            print(f'n={n}: FOUND valid pure-circulant (K3,K3,K3,K3)-avoiding 4-coloring '
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
