#!/usr/bin/env python3
"""
Phase 2 for the R(3,11) attack: exact ILP verification of independence
number for triangle-free circulant candidates from phase 1, prioritized
densest-first, time-boxed and parallelized (same pattern as R(4,7)'s
partial verification). Looking for independence number <= 10 (no K11 in
the complement) -- a candidate satisfying this proves R(3,11) > N.

Usage: python3 verify_candidates.py <N> [time_budget_seconds]
"""
import json
import os
import sys
import time
import multiprocessing as mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import circulant_edges, has_independent_set_of_size

TARGET_INDEP = 11  # looking for independence number <= 10


def check_one(args):
    S_list, N = args
    S = set(S_list)
    edges = circulant_edges(S, N)
    feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=8)
    return S_list, feasible, witness


def main():
    N = int(sys.argv[1])
    time_budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600

    in_path = os.path.join(os.path.dirname(__file__), 'results', f'triangle_free_candidates_n{N}.json')
    with open(in_path) as f:
        data = json.load(f)
    candidates = data['candidates']
    candidates.sort(key=lambda s: -len(s))

    print(f'Loaded {len(candidates)} triangle-free candidates for n={N}. '
          f'Verifying independence number via ILP (priority: densest first), '
          f'parallelized across {mp.cpu_count()} cores, time budget={time_budget}s...', flush=True)

    start = time.time()
    deadline = start + time_budget
    found = []
    inconclusive = []
    checked = 0

    tasks = [(c, N) for c in candidates]

    with mp.Pool(mp.cpu_count()) as pool:
        for S_list, feasible, witness in pool.imap(check_one, tasks, chunksize=2):
            checked += 1
            if feasible is False:
                print(f'*** FOUND WITNESS: S={S_list} triangle-free on n={N}, '
                      f'independence number <= {TARGET_INDEP - 1}! ***', flush=True)
                print(f'*** THIS PROVES R(3,11) >= {N + 1} ***', flush=True)
                found.append(S_list)
                out_path = os.path.join(os.path.dirname(__file__), 'results', f'FOUND_witness_n{N}.json')
                with open(out_path, 'w') as f:
                    json.dump({'S': S_list, 'n': N, 'edges': circulant_edges(set(S_list), N)}, f, indent=2)
            elif feasible is None:
                inconclusive.append(S_list)

            if checked % 500 == 0:
                elapsed = time.time() - start
                print(f'  verified {checked}/{len(candidates)} candidates (priority order), '
                      f'{len(found)} found, {len(inconclusive)} inconclusive, '
                      f'{elapsed:.1f}s elapsed', flush=True)

            if time.time() > deadline:
                print(f'  time budget ({time_budget}s) reached at {checked}/{len(candidates)} candidates.',
                      flush=True)
                break

    elapsed = time.time() - start
    result = {
        'n': N, 'target_indep': TARGET_INDEP,
        'total_candidates': len(candidates),
        'checked': checked,
        'coverage_fraction': checked / len(candidates) if candidates else 0,
        'found': found,
        'inconclusive_count': len(inconclusive),
        'elapsed_seconds': elapsed,
        'partial': checked < len(candidates),
    }
    out_path = os.path.join(os.path.dirname(__file__), 'results', f'verify_n{N}.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'DONE. N={N}: {checked}/{len(candidates)} candidates verified '
          f'({100*checked/len(candidates) if candidates else 0:.1f}% coverage, priority-ordered by density), '
          f'{len(found)} witnesses found, {len(inconclusive)} inconclusive, '
          f'{elapsed:.1f}s elapsed. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
