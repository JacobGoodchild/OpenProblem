#!/usr/bin/env python3
"""Phase 1: exhaustively enumerate all circulant connection sets on Z_48
and keep the K4-free ones, for the R(4,7) attack (open, bounds [49,61],
known witness on 48 vertices). n=48 -> half=24 -> 2^24 = 16,777,215 total
connection sets -- much larger than the n=36 R(4,6) search, so this phase
alone (though fast per-check) will take longer; sized so we can decide on
a verification strategy (full vs. sampled) based on the actual survivor
count once phase 1 completes."""
import itertools
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free

N = 48
CLIQUE_S = 4
half = N // 2  # 24

survivors = []
checked = 0
start = time.time()

for popcount in range(half, 0, -1):
    for combo in itertools.combinations(range(1, half + 1), popcount):
        checked += 1
        S = set(combo)
        if is_clique_free(S, N, CLIQUE_S):
            survivors.append(sorted(S))
    elapsed = time.time() - start
    print(f'  popcount={popcount}: {checked} checked total, {len(survivors)} K4-free so far, '
          f'{elapsed:.1f}s', flush=True)
    # periodic checkpoint in case this needs to be interrupted
    if popcount % 2 == 0:
        out_path = os.path.join(os.path.dirname(__file__), 'results', 'k4_free_candidates_n48.json')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump({'n': N, 'candidates': survivors, 'completed_popcount_down_to': popcount,
                       'checked_so_far': checked}, f)

out_path = os.path.join(os.path.dirname(__file__), 'results', 'k4_free_candidates_n48.json')
with open(out_path, 'w') as f:
    json.dump({'n': N, 'candidates': survivors, 'completed_popcount_down_to': 0,
               'checked_so_far': checked}, f)

print(f'DONE. {checked} total connection sets checked, {len(survivors)} K4-free candidates '
      f'saved to {out_path}. {time.time()-start:.1f}s elapsed.', flush=True)
