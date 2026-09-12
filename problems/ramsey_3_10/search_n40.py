#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: exhaustively search all circulant connection sets on
Z_40 for a triangle-free graph with independence number <= 9.

If found: this proves R(3,10) >= 41, which combined with the published
upper bound R(3,10) <= 41 (Angeltveit & Exoo / Codish et al.) would
determine R(3,10) = 41 EXACTLY -- resolving a real, currently open small
Ramsey number. This is the actual goal, not guaranteed to succeed (if
specialists with better tools haven't found one among circulant graphs
specifically, it may not exist in this restricted family, or may require
a non-circulant construction) -- but it is a genuine, currently-unresolved
question this search can give a real (if partial, since it only rules out
circulant constructions specifically) answer to.

n=40 means connection sets are subsets of {1,...,20}: 2^20 = 1,048,576
total, enumerated by decreasing popcount (higher-degree/denser graphs
first, since degree needs to be reasonably high to keep independence
number small, per the crude bound n/(d+1) <= independence number).
"""
import itertools
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_triangle_free, circulant_edges, has_independent_set_of_size

N = 40
TARGET_INDEP = 10  # looking for independence number <= 9, i.e. no indep set of size 10
half = N // 2  # 20

found = []
checked = 0
tri_free_count = 0
ilp_calls = 0
start = time.time()

out_dir = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(out_dir, exist_ok=True)

for popcount in range(half, 0, -1):
    for combo in itertools.combinations(range(1, half + 1), popcount):
        S = set(combo)
        checked += 1
        if not is_triangle_free(S, N):
            continue
        tri_free_count += 1
        edges = circulant_edges(S, N)
        ilp_calls += 1
        feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=8)
        if feasible is False:
            print(f'*** FOUND: S={sorted(S)} is triangle-free on n={N} '
                  f'with independence number <= {TARGET_INDEP-1}! ***', flush=True)
            print(f'*** This proves R(3,10) >= {N+1} ***', flush=True)
            found.append({'S': sorted(S), 'n': N, 'edges': edges})
            with open(os.path.join(out_dir, 'FOUND_witness.json'), 'w') as f:
                json.dump(found[-1], f, indent=2)

        if checked % 5000 == 0:
            elapsed = time.time() - start
            print(f'  checked {checked}/{2**half} connection sets ({tri_free_count} triangle-free, '
                  f'{ilp_calls} ILP calls), popcount={popcount}, {elapsed:.1f}s elapsed', flush=True)

    # checkpoint after each popcount layer
    result = {
        'n': N, 'target_indep': TARGET_INDEP,
        'checked': checked, 'triangle_free_count': tri_free_count,
        'ilp_calls': ilp_calls, 'found': found,
        'completed_popcount_down_to': popcount,
        'elapsed_seconds': time.time() - start,
    }
    with open(os.path.join(out_dir, 'search_n40_progress.json'), 'w') as f:
        json.dump(result, f, indent=2)
    print(f'--- finished popcount={popcount} layer, {checked} total checked, '
          f'{tri_free_count} triangle-free so far, {time.time()-start:.1f}s elapsed ---', flush=True)

    if found:
        break

elapsed = time.time() - start
print(f'DONE. n={N}: checked={checked}, triangle_free={tri_free_count}, ilp_calls={ilp_calls}, '
      f'found={len(found)}, elapsed={elapsed:.1f}s', flush=True)
if not found:
    print('No triangle-free circulant graph on 40 vertices with independence number <= 9 '
          'was found among ALL 2^20 possible connection sets. This rules out the entire '
          'circulant construction family for proving R(3,10) >= 41 (a non-circulant '
          'construction, if one exists, would need a different search method).', flush=True)
