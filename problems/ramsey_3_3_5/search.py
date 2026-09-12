#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on R(3,3,5): search for circulant 3-colorings of K_n
(colors avoiding K3, K3, K5 respectively) at increasing n, to empirically
map out how far this construction family can push the lower bound on the
currently-open R(3,3,5) (published upper bound <= 57; exact value and
best circulant-specific lower bound not confirmed from available
sources during this session's research, so this search also serves to
establish our own independently-verified data point).
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.multicolor_circulant import local_search_multicolor, is_valid_coloring

CLIQUE_SIZES = [3, 3, 5]


def try_n(n, time_budget, seed_base):
    deadline = time.time() + time_budget
    seed = seed_base
    while time.time() < deadline:
        rng = random.Random(seed)
        coloring, viol = local_search_multicolor(n, CLIQUE_SIZES, rng,
                                                   max_flips=30000, restart_after_stuck=3000)
        if viol == 0:
            valid = is_valid_coloring(coloring, n, CLIQUE_SIZES)
            if valid:
                return coloring
        seed += 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=35)
    ap.add_argument('--stop', type=int, default=56)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--time-per-n', type=float, default=20)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    largest_found = None
    largest_coloring = None
    results = {}

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    for n in range(args.start, args.stop + 1, args.step):
        t0 = time.time()
        coloring = try_n(n, args.time_per_n, args.seed + n * 1000)
        elapsed = time.time() - t0
        if coloring is not None:
            largest_found = n
            largest_coloring = [sorted(s) for s in coloring]
            results[n] = {'found': True, 'sizes': [len(s) for s in coloring], 'elapsed': elapsed}
            print(f'n={n}: FOUND valid (K3,K3,K5)-avoiding circulant 3-coloring '
                  f'(color sizes {[len(s) for s in coloring]}), {elapsed:.1f}s', flush=True)
        else:
            results[n] = {'found': False, 'elapsed': elapsed}
            print(f'n={n}: no valid coloring found in {elapsed:.1f}s (this does NOT prove '
                  f'none exists -- just that this search did not find one)', flush=True)

        with open(os.path.join(out_dir, 'search_progress.json'), 'w') as f:
            json.dump({'results': results, 'largest_found': largest_found,
                       'largest_coloring': largest_coloring}, f, indent=2)

    print(f'DONE. Largest n with a found circulant witness: {largest_found}', flush=True)
    if largest_found:
        print(f'This gives R(3,3,5) >= {largest_found + 1} (if this witness is correct and '
              f'is a genuine improvement over -- or at least confirmation of -- the published bound).',
              flush=True)


if __name__ == '__main__':
    main()
