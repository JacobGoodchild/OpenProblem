#!/usr/bin/env python3
"""
Stage 1 (exhaustive small-case check): use nauty-geng to enumerate all
non-isomorphic CONNECTED graphs on n vertices, compute gamma(G) for
each via exact ILP, and keep only those with gamma(G) >= min_gamma
(4 or 5 -- the smallest values not already proven safe for Vizing's
conjecture). Survivors are then run through the full necessary-
condition filter (edge-critical, every vertex in a min dominating set,
identification-decreases-domination) from vizing_lib.py -- these are
individually expensive (many ILP calls each), so we only run them on
the much smaller set of gamma-qualifying survivors, not on every graph.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from vizing_lib import domination_number, is_minimal_counterexample_candidate


def graphs_from_geng(n):
    """Stream non-isomorphic connected graphs on n vertices from
    nauty-geng, yielding networkx Graph objects (parsed from graph6)."""
    proc = subprocess.Popen(['nauty-geng', '-c', str(n)], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        yield nx.from_graph6_bytes(line.encode())
    proc.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--min-gamma', type=int, default=4)
    ap.add_argument('--ilp-time', type=float, default=5)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    checked = 0
    gamma_hist = {}
    survivors = []  # graphs with gamma >= min_gamma
    candidates = []  # survivors that also pass ALL necessary-condition filters

    t0 = time.time()
    for G in graphs_from_geng(args.n):
        checked += 1
        g, _ = domination_number(G, time_limit=args.ilp_time)
        if g is None:
            continue
        gamma_hist[g] = gamma_hist.get(g, 0) + 1
        if g >= args.min_gamma:
            survivors.append((nx.to_graph6_bytes(G, header=False).decode().strip(), g))
        if checked % 20000 == 0:
            print(f'  ...{checked} graphs checked, {time.time()-t0:.1f}s elapsed, '
                  f'gamma histogram so far: {gamma_hist}', flush=True)

    elapsed_phase1 = time.time() - t0
    print(f'Phase 1 done: {checked} connected graphs on n={args.n} checked in {elapsed_phase1:.1f}s.')
    print(f'gamma histogram: {gamma_hist}')
    print(f'{len(survivors)} graphs with gamma >= {args.min_gamma}.', flush=True)

    t1 = time.time()
    for g6, g in survivors:
        G = nx.from_graph6_bytes(g6.encode())
        passes, gamma, reason = is_minimal_counterexample_candidate(
            G, time_limit=args.ilp_time * 2, min_gamma=args.min_gamma)
        if passes:
            candidates.append({'graph6': g6, 'gamma': gamma})
            print(f'  *** CANDIDATE (passes ALL necessary-counterexample conditions): '
                  f'{g6}, gamma={gamma} ***', flush=True)
        # (silently skip non-passers -- there are usually many and printing
        # each reason would be noise; summary counts reported at the end)

    elapsed_phase2 = time.time() - t1
    print(f'\nPhase 2 done: {len(survivors)} gamma>={args.min_gamma} survivors filtered in '
          f'{elapsed_phase2:.1f}s. {len(candidates)} pass ALL necessary conditions.', flush=True)

    with open(os.path.join(out_dir, f'exhaustive_n{args.n}.json'), 'w') as f:
        json.dump({'n': args.n, 'min_gamma': args.min_gamma, 'checked': checked,
                    'gamma_histogram': gamma_hist, 'survivors_count': len(survivors),
                    'candidates': candidates}, f, indent=2)

    print(f'\nDONE n={args.n}. {len(candidates)} true minimal-counterexample CANDIDATES found '
          f'(still need to be tested against actual H graphs for a real Vizing violation).')


if __name__ == '__main__':
    main()
