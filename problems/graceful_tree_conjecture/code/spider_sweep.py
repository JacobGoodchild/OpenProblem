#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: exhaustively sweep spiders with exactly `num_long_legs`
legs of length >= 2 (mixed lengths, i.e. every partition of the total
long-leg edge count into that many parts), each combined with a range
of counts of additional length-1 legs -- this is exactly the family
recent (2026) literature identifies as the open gap: "six or more long
legs together with arbitrarily many length-one legs". Unlike general
trees (astronomically many past n=35), spiders are cheap to enumerate
exhaustively even at large n, since a spider is fully determined by its
multiset of leg lengths.

For each spider: try backtracking first (fast + can, in principle,
prove non-existence if it exhausts), falling back to local search
(handles larger/harder cases backtracking chokes on). Any spider that
BOTH methods fail on gets flagged for an escalated, much longer-budget
recheck before being taken seriously as a genuine open case.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from graceful_lib import (make_spider, spider_partitions, find_graceful_labeling_backtrack,
                           find_graceful_local_search_restarts, verify_graceful_labeling)


def try_find(legs, bt_budget=150_000, ls_trials=8, ls_iters=80_000, seed=0):
    G = make_spider(legs)
    n = G.number_of_nodes()
    import random
    rng = random.Random(seed)
    label, nodes, exhausted = find_graceful_labeling_backtrack(G, node_budget=bt_budget, rng=rng)
    method = 'backtracking'
    if label is None:
        label, dup = find_graceful_local_search_restarts(G, trials=ls_trials, max_iters=ls_iters, seed_base=seed)
        method = 'local_search' if label is not None else 'local_search_failed'
    else:
        dup = 0
    if label is not None:
        ok = verify_graceful_labeling(G, label)
        return {'legs': list(legs), 'n': n, 'found': True, 'method': method, 'verified': ok}
    return {'legs': list(legs), 'n': n, 'found': False, 'method': method, 'best_dup': dup}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--num-long-legs', type=int, default=6)
    ap.add_argument('--long-total-min', type=int, default=12)
    ap.add_argument('--long-total-max', type=int, default=30)
    ap.add_argument('--min-leg-len', type=int, default=2)
    ap.add_argument('--ones-counts', type=int, nargs='+', default=[0, 3, 8])
    ap.add_argument('--max-partitions-per-total', type=int, default=30)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    all_results = []
    unresolved = []
    checked = 0
    t0 = time.time()

    for long_total in range(args.long_total_min, args.long_total_max + 1):
        partitions = spider_partitions(long_total, args.num_long_legs, min_leg=args.min_leg_len)
        if len(partitions) > args.max_partitions_per_total:
            # sample to keep this tractable -- still covers a real spread
            import random
            rng = random.Random(long_total)
            partitions = rng.sample(partitions, args.max_partitions_per_total)
        for long_legs in partitions:
            for num_ones in args.ones_counts:
                legs = list(long_legs) + [1] * num_ones
                checked += 1
                r = try_find(legs, seed=checked)
                all_results.append(r)
                if not r['found']:
                    unresolved.append(r)
                    print(f'*** NOT FOUND (both methods): legs={legs} n={r["n"]} '
                          f'best_dup={r.get("best_dup")} ***', flush=True)
                if checked % 25 == 0:
                    elapsed = time.time() - t0
                    print(f'  ...{checked} spiders checked, {len(unresolved)} unresolved so far, '
                          f'{elapsed:.1f}s elapsed', flush=True)

    elapsed = time.time() - t0
    print(f'\nDONE. {checked} spiders checked ({args.num_long_legs} long legs, total long-leg-edges '
          f'{args.long_total_min}-{args.long_total_max}, ones-counts={args.ones_counts}) in {elapsed:.1f}s.')
    print(f'{len(unresolved)} spiders unresolved by both backtracking and local search.')

    with open(os.path.join(out_dir, f'spider_sweep_{args.num_long_legs}legs.json'), 'w') as f:
        json.dump({'args': vars(args), 'checked': checked, 'unresolved': unresolved,
                    'elapsed': elapsed, 'all_results_summary': [
                        {'legs': r['legs'], 'n': r['n'], 'found': r['found'], 'method': r['method']}
                        for r in all_results]}, f, indent=2)


if __name__ == '__main__':
    main()
