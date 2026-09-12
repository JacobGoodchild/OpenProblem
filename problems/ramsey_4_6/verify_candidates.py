#!/usr/bin/env python3
"""Phase 2 (parallel): for each K4-free circulant connection set found in
phase 1 (n=36), check via ILP whether the resulting graph has an
independent set of size >= 6. If ANY candidate comes back infeasible (no
such independent set), we have found a K4-free graph on 36 vertices with
independence number <= 5 -- a witness proving R(4,6) >= 37, improving on
the published lower bound of 36."""
import json
import os
import sys
import time
import multiprocessing as mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import circulant_edges, has_independent_set_of_size

N = 36
TARGET_INDEP = 6


def check_one(S_list):
    S = set(S_list)
    edges = circulant_edges(S, N)
    feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=10)
    return S_list, feasible, witness


def main():
    in_path = os.path.join(os.path.dirname(__file__), 'results', 'k4_free_candidates_n36.json')
    with open(in_path) as f:
        data = json.load(f)
    candidates = data['candidates']
    print(f'Loaded {len(candidates)} K4-free candidates for n={N}. '
          f'Verifying independence number via ILP, parallelized across '
          f'{mp.cpu_count()} cores...', flush=True)

    start = time.time()
    found = []
    inconclusive = []
    checked = 0

    with mp.Pool(mp.cpu_count()) as pool:
        for S_list, feasible, witness in pool.imap_unordered(check_one, candidates, chunksize=4):
            checked += 1
            if feasible is False:
                print(f'*** FOUND WITNESS: S={S_list} K4-free on n={N}, '
                      f'independence number <= {TARGET_INDEP - 1}! ***', flush=True)
                print(f'*** THIS PROVES R(4,6) >= {N + 1} ***', flush=True)
                found.append(S_list)
                out_path = os.path.join(os.path.dirname(__file__), 'results', 'FOUND_witness.json')
                with open(out_path, 'w') as f:
                    json.dump({'S': S_list, 'n': N, 'edges': circulant_edges(set(S_list), N)}, f, indent=2)
            elif feasible is None:
                inconclusive.append(S_list)

            if checked % 500 == 0:
                elapsed = time.time() - start
                print(f'  verified {checked}/{len(candidates)} candidates, '
                      f'{len(found)} found, {len(inconclusive)} inconclusive (timeout), '
                      f'{elapsed:.1f}s elapsed', flush=True)

    elapsed = time.time() - start
    result = {
        'n': N, 'target_indep': TARGET_INDEP,
        'total_candidates': len(candidates),
        'checked': checked,
        'found': found,
        'inconclusive_count': len(inconclusive),
        'inconclusive': inconclusive,
        'elapsed_seconds': elapsed,
    }
    out_path = os.path.join(os.path.dirname(__file__), 'results', 'verify_n36_final.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'DONE. {checked}/{len(candidates)} candidates verified, {len(found)} witnesses found, '
          f'{len(inconclusive)} inconclusive (solver timeout), {elapsed:.1f}s elapsed. '
          f'Saved to {out_path}', flush=True)
    if not found:
        print('No K4-free circulant graph on 36 vertices with independence number <= 5 '
              'exists among ALL 2^18 possible connection sets (modulo any inconclusive/timeout '
              'cases).', flush=True)


if __name__ == '__main__':
    main()
