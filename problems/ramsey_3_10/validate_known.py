#!/usr/bin/env python3
"""Sanity check: search for a triangle-free circulant graph on n=35 vertices
with independence number <= 8 (which would reproduce, via an independently
found construction, the known fact that R(3,9)=36 -- i.e. R(3,9)>35). This
validates the search method against ground truth before using it on the
genuinely open n=40 case for R(3,10)."""
import itertools
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_triangle_free, circulant_edges, has_independent_set_of_size, independence_number

N = 35
TARGET_INDEP = 9  # looking for independence number <= 8, i.e. no indep set of size 9
half = N // 2  # 17

found = []
checked = 0
tri_free_count = 0
start = time.time()

for popcount in range(half, 0, -1):
    for combo in itertools.combinations(range(1, half + 1), popcount):
        S = set(combo)
        checked += 1
        if not is_triangle_free(S, N):
            continue
        tri_free_count += 1
        edges = circulant_edges(S, N)
        feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=5)
        if feasible is False:
            print(f'FOUND: S={sorted(S)} is triangle-free on n={N} with independence number <= {TARGET_INDEP-1}!',
                  flush=True)
            found.append(sorted(S))
            break
    if found:
        break
    if checked % 2000 == 0:
        print(f'  checked {checked} connection sets ({tri_free_count} triangle-free), '
              f'{time.time()-start:.1f}s elapsed', flush=True)

print(f'Done. checked={checked}, triangle_free={tri_free_count}, found={len(found)}, '
      f'elapsed={time.time()-start:.1f}s')
if found:
    print('Example:', found[0])
