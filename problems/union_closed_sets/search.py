#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on the union-closed sets conjecture (Frankl, 1979):
for any nonempty union-closed family F (not just {emptyset}), does some
element appear in at least half of F's sets? Proven true exhaustively
for all ground-set sizes m <= 12 (Vuckovic & Zivkovic); best PROVEN
general bound as of 2024 is ~0.381966 (the golden-ratio bound); the
conjectured true bound is 0.5. A family with ratio < 0.5 anywhere would
disprove the conjecture; nobody has found one despite decades of search.

This runs an adversarial local search (lib/union_closed.py) over
GENERATOR sets for m > 12 (past the exhaustively-verified boundary),
trying to MINIMIZE the max-element-frequency ratio -- i.e. actively
hunting for either a counterexample (essentially certain not to exist,
but worth an honest try) or families that get unusually close to the
0.5 boundary, which is itself an interesting empirical data point.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.union_closed import local_search_min_ratio, union_closure, max_frequency_ratio, verify_union_closed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m-start', type=int, default=13)
    ap.add_argument('--m-stop', type=int, default=24)
    ap.add_argument('--time-per-m', type=float, default=25)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    results = {}
    global_best_ratio = 2.0
    global_best = None

    for m in range(args.m_start, args.m_stop + 1):
        deadline = time.time() + args.time_per_m
        best_for_m = 2.0
        best_gens_for_m = None
        trial = 0
        k_generators = max(3, m // 3)
        while time.time() < deadline:
            rng = random.Random(args.seed + m * 1000 + trial)
            ratio, gens, fam_size = local_search_min_ratio(m, k_generators, rng, iters=800)
            if ratio < best_for_m:
                best_for_m = ratio
                best_gens_for_m = gens
            trial += 1

        results[m] = {'best_ratio': best_for_m, 'trials': trial, 'generators': best_gens_for_m,
                       'k_generators': k_generators}
        print(f'm={m}: best ratio found = {best_for_m:.4f} over {trial} local-search trials '
              f'(conjectured floor: 0.5, proven floor: ~0.382)', flush=True)

        if best_for_m < global_best_ratio:
            global_best_ratio = best_for_m
            global_best = (m, best_gens_for_m)

        if best_for_m < 0.5 - 1e-9:
            print(f'*** POSSIBLE COUNTEREXAMPLE at m={m}: ratio={best_for_m} < 0.5 ***', flush=True)
            fam = union_closure(best_gens_for_m, m)
            print(f'    independent re-verification: union-closed={verify_union_closed(fam)}, '
                  f'ratio={max_frequency_ratio(fam, m)}', flush=True)

        with open(os.path.join(out_dir, 'search_progress.json'), 'w') as f:
            json.dump(results, f, indent=2)

    print(f'\nDONE. Global best ratio found: {global_best_ratio:.4f} at m={global_best[0] if global_best else None}',
          flush=True)


if __name__ == '__main__':
    main()
