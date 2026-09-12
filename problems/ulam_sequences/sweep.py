#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: broadly classify many generalized Ulam ("1-additive")
sequences (a,b) as eventually-periodic (gap sequence settles into a
strict repeating cycle) or not, computing far more terms per sequence
than the original 1990s-era literature typically did for a broad sweep
(Finch's 1992 classification table was necessarily limited by the
computers of that era). This is a fresh, deep pass over a real
combinatorial family -- most (a,b) pairs here have likely never been
pushed this far by anyone, so a genuine surprise (a claimed-periodic
pattern that breaks, or new periodicity in a case usually left
unclassified) is a real, if unlikely, possibility -- not a rediscovery
of settled 60-year-old territory.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.ulam_sequences import generate_ulam, gaps, find_period


def classify(a, b, n_terms, max_period=80):
    t0 = time.time()
    terms = generate_ulam(a, b, n_terms)
    elapsed = time.time() - t0
    if len(terms) < n_terms:
        return {'a': a, 'b': b, 'terms_reached': int(len(terms)), 'requested': n_terms,
                'status': 'ran_out_of_bound', 'elapsed': elapsed}
    g = gaps(terms)
    res = find_period(g, max_period=max_period)
    if res is None:
        return {'a': a, 'b': b, 'terms_reached': int(len(terms)), 'requested': n_terms,
                'status': 'no_period_found', 'elapsed': elapsed}
    period, span, frac = res
    return {'a': a, 'b': b, 'terms_reached': int(len(terms)), 'requested': n_terms,
            'status': 'periodic', 'period': int(period), 'span_checked': int(span),
            'match_fraction': float(frac), 'elapsed': elapsed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a-max', type=int, default=6)
    ap.add_argument('--b-max', type=int, default=20)
    ap.add_argument('--n-terms', type=int, default=15000)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    results = []
    t_start = time.time()
    for a in range(1, args.a_max + 1):
        for b in range(a + 1, args.b_max + 1):
            if math.gcd(a, b) != 1:
                continue  # gcd(a,b)=d>1 is just a d-scaled copy of the (a/d,b/d) sequence
            r = classify(a, b, args.n_terms)
            results.append(r)
            print(f"({a},{b}): {r['status']}"
                  + (f" period={r.get('period')} match={r.get('match_fraction'):.4f} "
                     f"over span={r.get('span_checked')}"
                     if r['status'] == 'periodic' else '')
                  + f"  [{r['elapsed']:.1f}s]", flush=True)

    total_elapsed = time.time() - t_start
    n_periodic = sum(1 for r in results if r['status'] == 'periodic')
    n_no_period = sum(1 for r in results if r['status'] == 'no_period_found')
    print(f'\nDONE. {len(results)} pairs checked in {total_elapsed:.1f}s. '
          f'{n_periodic} periodic, {n_no_period} no-period-found (candidates of interest).', flush=True)

    with open(os.path.join(out_dir, 'sweep_results.json'), 'w') as f:
        json.dump({'a_max': args.a_max, 'b_max': args.b_max, 'n_terms': args.n_terms,
                    'results': results, 'total_elapsed': total_elapsed}, f, indent=2)


if __name__ == '__main__':
    main()
