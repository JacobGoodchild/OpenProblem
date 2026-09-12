#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: exhaustively search all circulant connection sets on
Z_36 for a K4-free graph with independence number <= 5.

If found: this proves R(4,6) >= 37, improving on the published lower
bound of 36 (Exoo) -- a genuine, real improvement to a currently open
small Ramsey number (R(4,6) and R(3,10) are, per the literature, the two
smallest currently-unknown classical Ramsey numbers).

n=36 means connection sets are subsets of {1,...,18}: 2^18 = 262,144
total, enumerated by decreasing popcount.
"""
import itertools
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free

N = 36
CLIQUE_S = 4
half = N // 2  # 18

survivors = []
checked = 0
start = time.time()

for popcount in range(half, 0, -1):
    for combo in itertools.combinations(range(1, half + 1), popcount):
        checked += 1
        S = set(combo)
        if is_clique_free(S, N, CLIQUE_S):
            survivors.append(sorted(S))
    print(f'  popcount={popcount}: {checked} checked total, {len(survivors)} K4-free so far, '
          f'{time.time()-start:.1f}s', flush=True)

out_path = os.path.join(os.path.dirname(__file__), 'results', 'k4_free_candidates_n36.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump({'n': N, 'candidates': survivors}, f)

print(f'DONE. {checked} total connection sets checked, {len(survivors)} K4-free candidates '
      f'saved to {out_path}. {time.time()-start:.1f}s elapsed.', flush=True)
