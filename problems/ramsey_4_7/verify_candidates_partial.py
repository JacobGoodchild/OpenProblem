#!/usr/bin/env python3
"""Phase 2, PARTIAL (n=48 has 334,411 K4-free candidates -- extrapolating
from the R(4,6) n=36 verification rate, checking all of them would take
on the order of 5 hours, not tractable in one session). Instead: sort
candidates by DESCENDING popcount (density) -- denser circulant graphs
are more likely to have small independence number, so this prioritizes
the candidates most likely to be a real witness -- and verify as many as
possible within a fixed wall-clock time budget, honestly reporting
partial (not exhaustive) coverage.

This is explicitly different from the R(3,10) and R(4,6) results, which
were COMPLETE exhaustive searches. Here we can only report "no witness
found among the N candidates we had time to check" -- a much weaker
claim, and the write-up says so.
"""
import json
import os
import sys
import time
import multiprocessing as mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import circulant_edges, has_independent_set_of_size

N = 48
TARGET_INDEP = 7  # looking for independence number <= 6


def check_one(S_list):
    S = set(S_list)
    edges = circulant_edges(S, N)
    feasible, witness = has_independent_set_of_size(edges, N, TARGET_INDEP, time_limit=8)
    return S_list, feasible, witness


def main():
    time_budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1200

    in_path = os.path.join(os.path.dirname(__file__), 'results', 'k4_free_candidates_n48.json')
    with open(in_path) as f:
        data = json.load(f)
    candidates = data['candidates']
    # prioritize densest (highest popcount) first
    candidates.sort(key=lambda s: -len(s))

    print(f'Loaded {len(candidates)} K4-free candidates for n={N}. '
          f'Verifying independence number via ILP (priority: densest first), '
          f'parallelized across {mp.cpu_count()} cores, time budget={time_budget}s...', flush=True)

    start = time.time()
    deadline = start + time_budget
    found = []
    inconclusive = []
    checked = 0
    min_alpha_seen_gt6 = None  # track how close we get

    with mp.Pool(mp.cpu_count()) as pool:
        for S_list, feasible, witness in pool.imap(check_one, candidates, chunksize=2):
            checked += 1
            if feasible is False:
                print(f'*** FOUND WITNESS: S={S_list} K4-free on n={N}, '
                      f'independence number <= {TARGET_INDEP - 1}! ***', flush=True)
                print(f'*** THIS PROVES R(4,7) >= {N + 1} ***', flush=True)
                found.append(S_list)
                out_path = os.path.join(os.path.dirname(__file__), 'results', 'FOUND_witness.json')
                with open(out_path, 'w') as f:
                    json.dump({'S': S_list, 'n': N, 'edges': circulant_edges(set(S_list), N)}, f, indent=2)
                break
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
        'coverage_fraction': checked / len(candidates),
        'found': found,
        'inconclusive_count': len(inconclusive),
        'elapsed_seconds': elapsed,
        'partial': True,
    }
    out_path = os.path.join(os.path.dirname(__file__), 'results', 'verify_n48_partial.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'DONE (PARTIAL). {checked}/{len(candidates)} candidates verified '
          f'({100*checked/len(candidates):.1f}% coverage, priority-ordered by density), '
          f'{len(found)} witnesses found, {len(inconclusive)} inconclusive, '
          f'{elapsed:.1f}s elapsed. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
