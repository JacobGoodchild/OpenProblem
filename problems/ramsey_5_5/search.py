#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on R(5,5): one of the most famous open problems in
Ramsey theory. Current published bounds: 43 <= R(5,5) <= 46 (lower bound
Exoo 1989, a near-circulant construction on 42 vertices derived from
Cyclic(43) with a vertex deleted and some edges recolored; upper bound
Angeltveit & McKay 2024). The gap has stood at "somewhere in {43,...,46}"
for decades despite heavy computational effort from specialists in the
field -- so this is exactly the kind of long-standing, precisely-stated,
computationally-flavored open problem the project is looking for.

Scope, honestly stated up front: Exoo's actual record construction is
NOT a pure circulant graph (it's Cyclic(43) minus a vertex plus repairs),
so this search -- which only looks at PURE circulant 2-colorings of K_n
-- is not even attempting to reproduce the exact record construction.
What it CAN do is answer a well-defined, narrower question: how far can
the *purely circulant* restriction push a (K5,K5)-avoiding coloring
lower bound, using the same local-search technique already validated
for the multicolor case (R(3,3,5) in this repo)? Since a 2-coloring of
K_n is just a graph + its complement, and the complement of a circulant
graph is also circulant (complement distance set = the set-complement
of the distance set), this reduces to exactly lib/multicolor_circulant's
r=2 case with clique_sizes=[5,5] -- no new library code needed.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.multicolor_circulant import local_search_multicolor, is_valid_coloring

CLIQUE_SIZES = [5, 5]


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
    ap.add_argument('--stop', type=int, default=45)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--time-per-n', type=float, default=25)
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
            results[n] = {'found': True, 'sizes': [len(s) for s in coloring], 'elapsed': elapsed,
                          'coloring': largest_coloring}
            print(f'n={n}: FOUND valid pure-circulant (K5,K5)-avoiding 2-coloring '
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
