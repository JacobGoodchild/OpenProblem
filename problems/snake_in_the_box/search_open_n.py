#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on the open snake-in-the-box records. For n>=9 only
lower bounds are known (current published records, per recent literature
as of 2025-2026: a(9)>=191, a(10)>=379, a(11)>=746). Finding an even
LONGER snake for any of these n would be a genuine improvement to a real,
currently open record -- though we should be honest going in: a July 2026
paper ("A Census of New Snake-in-the-Box Records") suggests active,
well-resourced research on exactly this question, so a generic heuristic
search in a single session is a long shot against specialists' dedicated
tooling. This is still worth doing rigorously and honestly reporting,
same spirit as the R(3,10) circulant search earlier in this project.

Runs randomized backtracking DFS (most-constrained-first ordering,
lib/snake_in_box.py) for a fixed wall-clock time budget, keeping the best
snake found. Every result is independently re-verified from scratch
(verify_snake) before being reported -- no trusting the search's internal
bookkeeping.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.snake_in_box import randomized_snake_search, verify_snake

KNOWN_RECORDS = {9: 191, 10: 379, 11: 746, 12: 1493, 13: 2795}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n', type=int)
    ap.add_argument('--time-budget', type=float, default=180, help='seconds')
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    n = args.n
    rng = random.Random(args.seed)
    deadline = time.time() + args.time_budget

    best_path = []
    restarts = 0
    start = time.time()

    while time.time() < deadline:
        restarts += 1
        p = randomized_snake_search(n, rng, max_restarts=1, max_steps_per_restart=2_000_000,
                                     time_budget=deadline, start_time_fn=time.time)
        if len(p) > len(best_path):
            best_path = p
            valid, msg = verify_snake(best_path, n)
            elapsed = time.time() - start
            print(f'  [restart {restarts}] new best length={len(best_path)-1} '
                  f'(valid={valid}, {msg}), {elapsed:.1f}s elapsed', flush=True)

    elapsed = time.time() - start
    valid, msg = verify_snake(best_path, n)
    length = len(best_path) - 1
    known = KNOWN_RECORDS.get(n)

    result = {
        'n': n, 'best_length': length, 'valid': valid, 'verify_msg': msg,
        'path': best_path, 'restarts': restarts, 'elapsed_seconds': elapsed,
        'known_published_record': known,
        'improved_on_record': (known is not None and length > known),
    }
    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'search_n{n}_seed{args.seed}.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'DONE. n={n}: best length found = {length} (valid={valid}), '
          f'known published record = {known}, '
          f'{"*** IMPROVED ON RECORD ***" if result["improved_on_record"] else "did not beat the published record"}, '
          f'{restarts} restarts, {elapsed:.1f}s elapsed. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
