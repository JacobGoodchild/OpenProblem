#!/usr/bin/env python3
"""
Exhaustive verification of Tuza's conjecture (tau(G) <= 2*nu(G)) over EVERY
graph (not just regular ones -- the conjecture is about all graphs) on n
vertices, up to isomorphism, using nauty-geng to enumerate and an exact ILP
oracle (lib/tuza.py) to compute tau and nu for each one.

Usage: python3 exhaustive_search.py N [--connected-only]
"""
import argparse
import json
import subprocess
import sys
import time
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import networkx as nx
from lib.tuza import tuza_ratio, enumerate_triangles


def parse_graph6_stream(proc_stdout):
    for line in proc_stdout:
        line = line.strip()
        if not line:
            continue
        yield nx.from_graph6_bytes(line.encode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n', type=int)
    ap.add_argument('--connected-only', action='store_true',
                     help='only enumerate connected graphs (geng -c)')
    ap.add_argument('--min-edges', type=int, default=3,
                     help='skip graphs with fewer than this many edges (need >=3 for a triangle)')
    args = ap.parse_args()

    n = args.n
    cmd = ['nauty-geng']
    if args.connected_only:
        cmd.append('-c')
    cmd.append(str(n))

    print(f'Enumerating {"connected " if args.connected_only else ""}graphs on {n} vertices via: {" ".join(cmd)}',
          flush=True)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)

    checked = 0
    skipped_no_triangle = 0
    max_ratio = 0.0
    max_ratio_graph = None
    violations = []
    start = time.time()

    for G in parse_graph6_stream(proc.stdout):
        if G.number_of_edges() < args.min_edges:
            skipped_no_triangle += 1
            continue
        triangles = enumerate_triangles(G)
        if not triangles:
            skipped_no_triangle += 1
            continue

        tau, nu, ratio = tuza_ratio(G)
        checked += 1

        if ratio is not None and ratio > max_ratio:
            max_ratio = ratio
            max_ratio_graph = nx.to_graph6_bytes(G, header=False).decode().strip()

        if ratio is not None and ratio > 2.0 + 1e-9:
            g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
            violations.append({'graph6': g6, 'tau': tau, 'nu': nu, 'ratio': ratio})
            print(f'  *** POTENTIAL COUNTEREXAMPLE: tau={tau} nu={nu} ratio={ratio} graph6={g6}',
                  flush=True)

        if checked % 200 == 0:
            elapsed = time.time() - start
            print(f'  checked {checked} graphs with triangles, max_ratio so far={max_ratio:.4f}, '
                  f'{elapsed:.1f}s elapsed', flush=True)

    proc.wait()
    elapsed = time.time() - start

    result = {
        'n': n,
        'connected_only': args.connected_only,
        'checked_with_triangles': checked,
        'skipped_no_triangle': skipped_no_triangle,
        'max_ratio': max_ratio,
        'max_ratio_graph6': max_ratio_graph,
        'violations': violations,
        'elapsed_seconds': elapsed,
    }

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    suffix = '_conn' if args.connected_only else ''
    out_path = os.path.join(out_dir, f'exhaustive_n{n}{suffix}.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'n={n}: {checked} graphs with triangles checked, {skipped_no_triangle} skipped '
          f'(triangle-free / too sparse), max ratio observed = {max_ratio:.4f}, '
          f'{len(violations)} violations found. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
