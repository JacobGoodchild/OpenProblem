#!/usr/bin/env python3
"""
A systematic sweep applying the cyclotomic (prime-power-residue)
construction technique -- which reproduced the REAL R(4,4,4) record
from first principles (problems/ramsey_4_4_4) -- across every other
open Ramsey number this project has already attempted with generic
LOCAL SEARCH over circulant colorings. Local search is fast but
incomplete (it can miss a witness that exists); the cyclotomic search
is exhaustive over its (narrower) family of candidates: every eligible
prime up to a bound, checked with cheap arithmetic. So this isn't
re-doing prior work -- it's trying a categorically different, exact
construction method on the same open targets, motivated directly by the
R(4,4,4) result and the "what would move this forward" notes left in
several of this project's earlier Ramsey write-ups.

Targets (clique_sizes, r) and their published bounds:
  R(5,5)      [5,5]        43 <= R(5,5) <= 46
  R(6,6)      [6,6]        102 <= R(6,6) <= 160
  R(3,11)     [3,11]       47 <= R(3,11) <= 50
  R(5,6)      [5,6]        59 <= R(5,6) <= 85
  R(3,3,3,3)  [3,3,3,3]    51 <= R(3,3,3,3) <= 62
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.cyclotomic_ramsey import search_cyclotomic_range

TARGETS = {
    'R(5,5)':     {'clique_sizes': [5, 5],       'p_min': 20,  'p_max': 5000, 'known_record': 42},
    'R(6,6)':     {'clique_sizes': [6, 6],       'p_min': 20,  'p_max': 5000, 'known_record': 101},
    'R(3,11)':    {'clique_sizes': [3, 11],      'p_min': 10,  'p_max': 5000, 'known_record': 46},
    'R(5,6)':     {'clique_sizes': [5, 6],       'p_min': 20,  'p_max': 5000, 'known_record': 58},
    'R(3,3,3,3)': {'clique_sizes': [3, 3, 3, 3], 'p_min': 10,  'p_max': 5000, 'known_record': 50},
}


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    summary = {}

    for name, cfg in TARGETS.items():
        t0 = time.time()
        checked, found = search_cyclotomic_range(cfg['clique_sizes'], cfg['p_min'], cfg['p_max'])
        elapsed = time.time() - t0
        best_found = max((p for p, _ in found), default=None)
        improves_on_record = best_found is not None and best_found > cfg['known_record']
        print(f"{name}: checked {len(checked)} eligible primes in [{cfg['p_min']},{cfg['p_max']}] "
              f"({elapsed:.2f}s). Found {len(found)} cyclotomic witnesses: "
              f"{[p for p, _ in found]}. Known record: {cfg['known_record']}. "
              f"{'*** IMPROVES ON RECORD ***' if improves_on_record else 'no improvement.'}",
              flush=True)
        summary[name] = {
            'clique_sizes': cfg['clique_sizes'],
            'p_range': [cfg['p_min'], cfg['p_max']],
            'eligible_primes_checked': len(checked),
            'found_primes': [p for p, _ in found],
            'known_record': cfg['known_record'],
            'improves_on_record': improves_on_record,
            'elapsed_seconds': elapsed,
        }
        if found:
            for p, D in found:
                with open(os.path.join(out_dir, f'{name.replace(",", "_").replace("(", "").replace(")", "")}_p{p}.json'), 'w') as f:
                    json.dump({'target': name, 'p': p, 'distance_sets': D}, f, indent=2)

    with open(os.path.join(out_dir, 'sweep_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print('\nDONE. Summary saved.', flush=True)


if __name__ == '__main__':
    main()
