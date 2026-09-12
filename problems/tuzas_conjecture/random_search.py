#!/usr/bin/env python3
"""
Random sampling for Tuza's conjecture: draw G(n,p) Erdos-Renyi graphs across
a range of edge densities p, compute the exact tau/nu ratio for each via
ILP, and record the distribution -- in particular the maximum ratio
observed and whether anything exceeds 2.

Unlike the friendly-partitions problem, Tuza's conjecture concerns ALL
graphs (not a fixed-degree family), so density p is swept explicitly since
the interesting regime (near known tight examples like K4/K5, and the
general upper-bound proofs for dense graphs) depends heavily on it.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import networkx as nx
from lib.tuza import enumerate_triangles, tuza_ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n', type=int)
    ap.add_argument('--samples-per-p', type=int, default=200)
    ap.add_argument('--ps', type=str, default='0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9',
                     help='comma-separated list of edge probabilities to sweep')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--time-limit', type=float, default=10.0,
                     help='per-graph ILP time limit (seconds) to keep large/dense graphs tractable')
    args = ap.parse_args()

    n = args.n
    rng = random.Random(args.seed)
    ps = [float(x) for x in args.ps.split(',')]

    by_p = {}
    max_ratio = 0.0
    max_ratio_info = None
    violations = []

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    start = time.time()
    total_checked = 0

    for p in ps:
        ratios = []
        skipped = 0
        for i in range(args.samples_per_p):
            G = nx.gnp_random_graph(n, p, seed=rng.randrange(2**31))
            triangles = enumerate_triangles(G)
            if not triangles:
                skipped += 1
                continue
            if len(triangles) > 4000:
                # too many triangles for the ILP to solve quickly; skip to
                # keep the sweep moving (dense-graph regime is also the
                # regime with the best proven bounds already, per Tuza 1990
                # and Haxell 1999, so this is a reasonable place to cut off)
                skipped += 1
                continue
            tau, nu, ratio = tuza_ratio(G, time_limit=args.time_limit)
            total_checked += 1
            if ratio is not None:
                ratios.append(ratio)
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_ratio_info = {
                        'n': n, 'p': p, 'tau': tau, 'nu': nu, 'ratio': ratio,
                        'graph6': nx.to_graph6_bytes(G, header=False).decode().strip(),
                    }
                if ratio > 2.0 + 1e-9:
                    violations.append(max_ratio_info)
                    print(f'  *** VIOLATION at p={p}: ratio={ratio} ***', flush=True)

        by_p[p] = {
            'samples_with_triangles': len(ratios),
            'skipped': skipped,
            'mean_ratio': sum(ratios) / len(ratios) if ratios else None,
            'max_ratio': max(ratios) if ratios else None,
        }
        elapsed = time.time() - start
        print(f'  [n={n}, p={p}] {len(ratios)} graphs checked, skipped={skipped}, '
              f'mean_ratio={by_p[p]["mean_ratio"]}, max_ratio={by_p[p]["max_ratio"]}, '
              f'{elapsed:.1f}s elapsed', flush=True)

    result = {
        'n': n, 'ps': ps, 'samples_per_p': args.samples_per_p,
        'total_checked': total_checked,
        'by_p': by_p,
        'overall_max_ratio': max_ratio,
        'overall_max_ratio_info': max_ratio_info,
        'violations': violations,
        'elapsed_seconds': time.time() - start,
    }
    out_path = os.path.join(out_dir, f'random_n{n}_seed{args.seed}.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'n={n}: {total_checked} total graphs checked across {len(ps)} densities, '
          f'overall max ratio = {max_ratio:.4f}, {len(violations)} violations. '
          f'Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
