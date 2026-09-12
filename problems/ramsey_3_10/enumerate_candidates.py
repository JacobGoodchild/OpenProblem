#!/usr/bin/env python3
"""Phase 1 (fast, single-threaded): enumerate ALL 2^20 circulant connection
sets on Z_40 and keep only the triangle-free ones (pure arithmetic check,
no ILP). Saves the survivors to a JSON file for phase 2 (parallel ILP
verification) to consume."""
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_triangle_free

N = 40
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
    print(f'  popcount={popcount}: {checked} checked total, {len(survivors)} triangle-free so far, '
          f'{time.time()-start:.1f}s', flush=True)

out_path = os.path.join(os.path.dirname(__file__), 'results', 'triangle_free_candidates_n40.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump({'n': N, 'candidates': survivors}, f)

print(f'DONE. {checked} total connection sets checked, {len(survivors)} triangle-free candidates '
      f'saved to {out_path}. {time.time()-start:.1f}s elapsed.', flush=True)
