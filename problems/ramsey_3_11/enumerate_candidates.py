#!/usr/bin/env python3
"""
Phase 1 for the R(3,11) attack: exhaustively enumerate circulant
connection sets on Z_N and keep the triangle-free ones, prioritized by
DESCENDING popcount (density) since denser triangle-free circulant
graphs are more likely to have small independence number -- the property
we actually need (independence number <= 10, i.e. no K11 in the
complement) to witness R(3,11) > N.

Background: R(3,11) is currently OPEN with bounds 47 <= R(3,11) <= 50.
The lower bound of 47 (a known 46-vertex witness) was only established
recently, breaking a 46-year-old record of 46 -- so this is a genuinely
live, recently-active research target, not a settled classical value.
Usage: python3 enumerate_candidates.py <N>
"""
import itertools
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_triangle_free


def main():
    N = int(sys.argv[1])
    half = N // 2

    survivors = []
    checked = 0
    start = time.time()

    for popcount in range(half, 0, -1):
        for combo in itertools.combinations(range(1, half + 1), popcount):
            checked += 1
            S = set(combo)
            if is_triangle_free(S, N):
                survivors.append(sorted(S))
        elapsed = time.time() - start
        print(f'  N={N} popcount={popcount}: {checked} checked total, '
              f'{len(survivors)} triangle-free so far, {elapsed:.1f}s', flush=True)
        if popcount % 2 == 0:
            out_path = os.path.join(os.path.dirname(__file__), 'results', f'triangle_free_candidates_n{N}.json')
            with open(out_path, 'w') as f:
                json.dump({'n': N, 'candidates': survivors, 'completed_popcount_down_to': popcount,
                           'checked_so_far': checked}, f)

    out_path = os.path.join(os.path.dirname(__file__), 'results', f'triangle_free_candidates_n{N}.json')
    with open(out_path, 'w') as f:
        json.dump({'n': N, 'candidates': survivors, 'completed_popcount_down_to': 0,
                   'checked_so_far': checked}, f)

    print(f'DONE. N={N}: {checked} total connection sets checked, {len(survivors)} triangle-free '
          f'candidates saved to {out_path}. {time.time()-start:.1f}s elapsed.', flush=True)


if __name__ == '__main__':
    main()
