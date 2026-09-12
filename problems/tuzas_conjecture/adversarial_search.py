#!/usr/bin/env python3
"""
Adversarial simulated-annealing search over GRAPH SPACE for graphs with a
high tau(G)/nu(G) ratio, in an attempt to either:
  (a) find a genuine counterexample to Tuza's conjecture (ratio > 2), or
  (b) find a new extremal family approaching ratio 2 other than the known
      K4/K5-based constructions, which would itself be an interesting
      structural finding.

Moves: toggle a single edge (add if absent, remove if present) -- unlike
the friendly-partitions problem, Tuza's conjecture is NOT restricted to
regular graphs, so we search over all of graph space directly.

Scoring during the SA walk uses FAST GREEDY heuristics (O(triangles) per
step, not the expensive exact ILP) so that many thousands of moves can be
tried per second:
  - greedy_packing_lower_bound(G)  <= true nu(G)
  - greedy_cover_upper_bound(G)    >= true tau(G)
  heuristic_ratio = greedy_cover_upper_bound / greedy_packing_lower_bound
This heuristic_ratio is a genuine >= true_ratio upper bound (since it uses
a lower bound on nu's denominator and upper bound on tau's numerator), so
it can only ever OVERESTIMATE how close to / past 2 a graph is. Any
candidate whose heuristic ratio exceeds ~1.9 is re-verified with the exact
ILP oracle (lib/tuza.py) before being taken seriously.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import networkx as nx
from lib.tuza import (enumerate_triangles, greedy_packing_lower_bound,
                       greedy_cover_upper_bound, tuza_ratio)


def heuristic_ratio(G):
    triangles = enumerate_triangles(G)
    if not triangles:
        return 0.0, 0, 0
    nu_lb = greedy_packing_lower_bound(G, triangles)
    tau_ub, _ = greedy_cover_upper_bound(G, triangles)
    if nu_lb == 0:
        return 0.0, 0, tau_ub
    return tau_ub / nu_lb, nu_lb, tau_ub


def random_graph(n, p, rng):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                G.add_edge(i, j)
    return G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n', type=int, help='number of vertices')
    ap.add_argument('--steps', type=int, default=50000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--init-p', type=float, default=0.5)
    ap.add_argument('--restarts', type=int, default=1)
    ap.add_argument('--verify-threshold', type=float, default=1.85,
                     help='re-verify with exact ILP when heuristic ratio exceeds this')
    args = ap.parse_args()

    n = args.n
    rng = random.Random(args.seed)

    best_overall_heur = 0.0
    best_overall_G = None
    exact_verified = []  # list of {heur_ratio, tau, nu, ratio, graph6}
    counterexamples = []

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    start = time.time()
    total_steps = 0

    for restart in range(args.restarts):
        G = random_graph(n, args.init_p, rng)
        cur_score, _, _ = heuristic_ratio(G)
        best_score = cur_score
        best_G = G.copy()

        temp = 1.0
        cooling = 0.99995

        edges_all = [(i, j) for i in range(n) for j in range(i + 1, n)]

        for step in range(args.steps):
            total_steps += 1
            i, j = rng.choice(edges_all)
            had_edge = G.has_edge(i, j)
            if had_edge:
                G.remove_edge(i, j)
            else:
                G.add_edge(i, j)

            new_score, nu_lb, tau_ub = heuristic_ratio(G)

            delta = new_score - cur_score
            accept = delta >= 0 or rng.random() < pow(2.71828, delta / max(temp, 1e-6))

            if accept:
                cur_score = new_score
                if new_score > best_score:
                    best_score = new_score
                    best_G = G.copy()
                    if new_score >= args.verify_threshold:
                        tau, nu, ratio = tuza_ratio(G, time_limit=30)
                        rec = {
                            'restart': restart, 'step': step,
                            'heuristic_ratio': new_score,
                            'tau': tau, 'nu': nu, 'exact_ratio': ratio,
                            'graph6': nx.to_graph6_bytes(G, header=False).decode().strip(),
                        }
                        exact_verified.append(rec)
                        print(f'  [restart {restart} step {step}] heuristic={new_score:.4f} '
                              f'-> EXACT tau={tau} nu={nu} ratio={ratio}', flush=True)
                        if ratio is not None and ratio > 2.0 + 1e-9:
                            counterexamples.append(rec)
                            print(f'  *** COUNTEREXAMPLE CANDIDATE FOUND: ratio={ratio} ***',
                                  flush=True)
            else:
                # revert
                if had_edge:
                    G.add_edge(i, j)
                else:
                    G.remove_edge(i, j)

            temp *= cooling

            if step % 5000 == 0:
                elapsed = time.time() - start
                print(f'  [restart {restart}] step {step}/{args.steps}, '
                      f'cur_heur={cur_score:.4f}, best_heur={best_score:.4f}, '
                      f'temp={temp:.4f}, {elapsed:.1f}s elapsed', flush=True)

        if best_score > best_overall_heur:
            best_overall_heur = best_score
            best_overall_G = best_G.copy()

    elapsed = time.time() - start
    result = {
        'n': n,
        'total_steps': total_steps,
        'restarts': args.restarts,
        'best_heuristic_ratio': best_overall_heur,
        'best_graph6': nx.to_graph6_bytes(best_overall_G, header=False).decode().strip()
                       if best_overall_G is not None else None,
        'exact_verified_candidates': exact_verified,
        'counterexamples': counterexamples,
        'elapsed_seconds': elapsed,
    }
    out_path = os.path.join(out_dir, f'adversarial_n{n}_seed{args.seed}.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'n={n}: {total_steps} SA steps across {args.restarts} restart(s), '
          f'best heuristic ratio={best_overall_heur:.4f}, '
          f'{len(exact_verified)} exact-verified candidates, '
          f'{len(counterexamples)} counterexamples found. Saved to {out_path}', flush=True)


if __name__ == '__main__':
    main()
