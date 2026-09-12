#!/usr/bin/env python3
"""
Stage 2/4 (heuristic + adversarial search): for n beyond what exhaustive
nauty-geng enumeration can cover (n=10 alone has 11.7M connected
graphs), generate random connected graphs targeting gamma in
{min_gamma, min_gamma+1}, and separately run a local search that
hill-climbs toward SATISFYING MORE of the necessary-counterexample
conditions (treating "number of filters currently passed" as the
objective) -- a graph doesn't need to already be a full candidate to
be a useful search state; the search rewards getting closer.

Any graph that ends up passing ALL necessary conditions gets
immediately tested against a battery of H graphs for an actual Vizing
violation (the real target).
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from vizing_lib import (domination_number, is_edge_critical, every_vertex_in_some_min_dominating_set,
                         identifying_decreases_domination, is_minimal_counterexample_candidate,
                         check_vizing)


def random_connected_graph(n, edge_prob, rng):
    while True:
        G = nx.gnp_random_graph(n, edge_prob, seed=rng.randint(0, 2**31))
        if nx.is_connected(G):
            return G


def filter_score(G, time_limit=3, min_gamma=4):
    """Returns (score in 0..4, gamma) -- how many of the 4 necessary
    conditions this graph currently satisfies (connected is assumed /
    enforced by construction, so not separately scored here)."""
    if not nx.is_connected(G):
        return -1, None
    gamma, _ = domination_number(G, time_limit)
    if gamma is None:
        return -1, None
    score = 0
    if gamma >= min_gamma:
        score += 1
    else:
        return score, gamma  # no point checking expensive filters if gamma too low
    if is_edge_critical(G, gamma, time_limit):
        score += 1
    if every_vertex_in_some_min_dominating_set(G, gamma, time_limit):
        score += 1
    if identifying_decreases_domination(G, gamma, time_limit):
        score += 1
    return score, gamma


TEST_H_GRAPHS = {
    'K1': lambda: nx.empty_graph(1), 'K2': lambda: nx.complete_graph(2),
    'P3': lambda: nx.path_graph(3), 'P4': lambda: nx.path_graph(4),
    'P5': lambda: nx.path_graph(5), 'C3': lambda: nx.cycle_graph(3),
    'C4': lambda: nx.cycle_graph(4), 'C5': lambda: nx.cycle_graph(5),
    'star4': lambda: nx.star_graph(4),
}


def test_candidate_against_batch(G, extra_H=None):
    results = {}
    Hs = dict(TEST_H_GRAPHS)
    if extra_H is not None:
        Hs['G_itself'] = G
    for name, mkH in Hs.items():
        H = mkH() if callable(mkH) else mkH
        r = check_vizing(G, H, time_limit_each=15)
        results[name] = r
        if r.get('holds') is False:
            return results, True  # VIOLATION
    return results, False


def local_search_toward_candidate(n, min_gamma, rng, iters, edge_prob_init=0.3):
    G = random_connected_graph(n, edge_prob_init, rng)
    cur_score, cur_gamma = filter_score(G, min_gamma=min_gamma)
    best_score, best_G, best_gamma = cur_score, G.copy(), cur_gamma

    nodes = list(range(n))
    for it in range(iters):
        G2 = G.copy()
        u, v = rng.sample(nodes, 2)
        if G2.has_edge(u, v):
            G2.remove_edge(u, v)
        else:
            G2.add_edge(u, v)
        if not nx.is_connected(G2):
            continue
        new_score, new_gamma = filter_score(G2, min_gamma=min_gamma)
        if new_score >= cur_score or rng.random() < 0.15:
            G, cur_score, cur_gamma = G2, new_score, new_gamma
            if new_score > best_score:
                best_score, best_G, best_gamma = new_score, G.copy(), new_gamma
        if best_score == 4:
            break
    return best_G, best_score, best_gamma


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-start', type=int, default=9)
    ap.add_argument('--n-stop', type=int, default=16)
    ap.add_argument('--trials-per-n', type=int, default=15)
    ap.add_argument('--iters-per-trial', type=int, default=150)
    ap.add_argument('--min-gamma', type=int, default=4)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    full_candidates = []
    summary = {}

    for n in range(args.n_start, args.n_stop + 1):
        best_overall = -1
        t0 = time.time()
        for trial in range(args.trials_per_n):
            rng = random.Random(args.seed + n * 1000 + trial)
            G, score, gamma = local_search_toward_candidate(n, args.min_gamma, rng, args.iters_per_trial)
            if score > best_overall:
                best_overall = score
            if score == 4:
                # full candidate! verify rigorously and test against H battery
                passes, gamma2, reason = is_minimal_counterexample_candidate(
                    G, time_limit=10, min_gamma=args.min_gamma)
                if passes:
                    print(f'n={n} trial={trial}: *** FULL CANDIDATE (gamma={gamma2}) *** '
                          f'testing against H battery...', flush=True)
                    results, violation = test_candidate_against_batch(G, extra_H=True)
                    g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
                    full_candidates.append({'n': n, 'graph6': g6, 'gamma': gamma2,
                                             'vizing_results': {k: v.get('holds') for k, v in results.items()},
                                             'violation_found': violation})
                    if violation:
                        print(f'\n*** VIZING VIOLATION FOUND at n={n}! graph6={g6} ***\n', flush=True)
                    else:
                        print(f'  no violation in H battery for this candidate (n={n}, graph6={g6})',
                              flush=True)
        elapsed = time.time() - t0
        summary[n] = {'best_filter_score_achieved': best_overall, 'trials': args.trials_per_n,
                       'elapsed': elapsed}
        print(f'n={n}: best filter-score achieved across {args.trials_per_n} trials = '
              f'{best_overall}/4, {elapsed:.1f}s', flush=True)

        with open(os.path.join(out_dir, 'random_adversarial_progress.json'), 'w') as f:
            json.dump({'summary': summary, 'full_candidates': full_candidates}, f, indent=2)

    print(f'\nDONE. {len(full_candidates)} full candidates found across n={args.n_start}-{args.n_stop}.',
          flush=True)


if __name__ == '__main__':
    main()
