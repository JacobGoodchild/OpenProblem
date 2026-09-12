#!/usr/bin/env python3
"""Compute the EXACT independence number for a large random sample of the
triangle-free circulant candidates on n=40, to characterize how close the
best of this construction family gets to the target of <=9 (we already
know via the exhaustive feasibility check that none achieves <=9, but
knowing the minimum achieved -- e.g. 10 vs 15 -- indicates how close a
"near miss" this negative result really is)."""
import json
import os
import random
import sys
import time
import multiprocessing as mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import circulant_edges, independence_number

N = 40


def compute_one(S):
    edges = circulant_edges(set(S), N)
    alpha = independence_number(edges, N, time_limit=15)
    return S, alpha


def main():
    with open(os.path.join(os.path.dirname(__file__), 'results',
                            'triangle_free_candidates_n40.json')) as f:
        data = json.load(f)
    candidates = data['candidates']
    random.seed(1)
    sample_size = min(1000, len(candidates))
    sample = random.sample(candidates, sample_size)

    start = time.time()
    results = []
    with mp.Pool(mp.cpu_count()) as pool:
        for i, (S, alpha) in enumerate(pool.imap_unordered(compute_one, sample, chunksize=4)):
            results.append({'S': S, 'alpha': alpha})
            if (i + 1) % 200 == 0:
                print(f'  computed {i+1}/{sample_size}, {time.time()-start:.1f}s elapsed', flush=True)

    alphas = [r['alpha'] for r in results if r['alpha'] is not None]
    best = min(alphas)
    best_entry = min(results, key=lambda r: r['alpha'] if r['alpha'] is not None else 999)

    out = {
        'n': N, 'sample_size': sample_size,
        'min_alpha_found': best,
        'min_alpha_example': best_entry,
        'alpha_distribution_summary': {
            'min': min(alphas), 'max': max(alphas),
            'mean': sum(alphas) / len(alphas),
        },
        'elapsed_seconds': time.time() - start,
    }
    out_path = os.path.join(os.path.dirname(__file__), 'results', 'alpha_sample_n40.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'DONE. sample={sample_size}, min alpha found={best} (target was <=9), '
          f'mean={out["alpha_distribution_summary"]["mean"]:.2f}, '
          f'{time.time()-start:.1f}s elapsed. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
