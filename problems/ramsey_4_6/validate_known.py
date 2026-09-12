#!/usr/bin/env python3
"""Sanity check: search for a K4-free circulant graph on n=24 vertices
with independence number <= 4 (which would reproduce, via an
independently found construction, the known fact that R(4,5)=25 -- i.e.
R(4,5)>24). Validates the generalized clique-free circulant search before
using it on the genuinely open R(4,6) case."""
import itertools
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free, circulant_edges, has_independent_set_of_size

N = 24
CLIQUE_S = 4       # K4-free
TARGET_INDEP = 5   # looking for independence number <= 4
half = N // 2

found = []
checked = 0
clique_free_count = 0
start = time.time()

for popcount in range(half, 0, -1):
    for combo in itertools.combinations(range(1, half + 1), popcount):
        S = set(combo)
        checked += 1
        if not is_clique_free(S, N, CLIQUE_S):
            continue
        clique_free_count += 1
        edges = circulant_edges(S, N)
        feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=5)
        if feasible is False:
            print(f'FOUND: S={sorted(S)} is K4-free on n={N} with independence number <= {TARGET_INDEP-1}!',
                  flush=True)
            found.append(sorted(S))
            break
    if found:
        break
    if checked % 2000 == 0:
        print(f'  checked {checked} connection sets ({clique_free_count} K4-free), '
              f'{time.time()-start:.1f}s elapsed', flush=True)

print(f'Done. checked={checked}, K4_free={clique_free_count}, found={len(found)}, '
      f'elapsed={time.time()-start:.1f}s')
if found:
    print('Example:', found[0])
