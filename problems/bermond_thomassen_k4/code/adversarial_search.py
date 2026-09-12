#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on Bermond-Thomassen k=4: adversarial local search
over the space of digraphs with min out-degree EXACTLY 7, hill-climbing
to MINIMIZE the maximum number of vertex-disjoint directed cycles.
If this ever finds a digraph with min out-degree >= 7 and provably
fewer than 4 disjoint directed cycles, that is a counterexample to a
45-year-old open conjecture -- any such finding gets escalated to a
much more thorough (higher cycle-length-cap, longer ILP time limit)
re-verification before being believed at all.

Move: rewire one out-edge of a random vertex to a different random
target (preserves out-degree=7 exactly, the tightest/most adversarial
case). Objective for hill-climbing: the max disjoint cycle count using
a LENGTH-CAPPED cycle enumeration (fast, but only an upper-bound-safe /
lower-bound-risky proxy -- see honest caveat in FINDINGS.md). Any
candidate whose length-capped max drops below 4 gets a full escalated
recheck with a much higher length cap before being taken seriously.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from bt_lib import (random_min_outdegree_digraph, enumerate_cycles, max_disjoint_cycle_packing,
                     verify_disjoint_cycles, verify_min_outdegree)


def rewire_move(G, n, d, rng):
    v = rng.randrange(n)
    out_neighbors = list(G.successors(v))
    old_target = rng.choice(out_neighbors)
    candidates = [u for u in range(n) if u != v and u not in out_neighbors]
    if not candidates:
        return None
    new_target = rng.choice(candidates)
    G.remove_edge(v, old_target)
    G.add_edge(v, new_target)
    return (v, old_target, new_target)


def undo_move(G, move):
    v, old_target, new_target = move
    G.remove_edge(v, new_target)
    G.add_edge(v, old_target)


def evaluate(G, n, search_length_cap, ilp_time=8):
    cycles, truncated = enumerate_cycles(G, max_cycles=150_000, max_length=search_length_cap)
    maxc, sel = max_disjoint_cycle_packing(n, cycles, time_limit=ilp_time)
    return maxc, sel, truncated


def escalated_recheck(G, n, escalated_length_cap=12, ilp_time=60):
    """A candidate that looked suspiciously low needs a much more
    thorough check before being believed -- higher cycle-length cap,
    more ILP time. Returns (maxc, selected, truncated)."""
    cycles, truncated = enumerate_cycles(G, max_cycles=1_000_000, max_length=escalated_length_cap)
    maxc, sel = max_disjoint_cycle_packing(n, cycles, time_limit=ilp_time)
    return maxc, sel, truncated


def local_search(n, d, rng, iters, search_length_cap=5):
    G = random_min_outdegree_digraph(n, d, rng)
    cur_max, cur_sel, cur_trunc = evaluate(G, n, search_length_cap)
    best_max = cur_max
    best_G = G.copy()

    for it in range(iters):
        move = rewire_move(G, n, d, rng)
        if move is None:
            continue
        new_max, new_sel, new_trunc = evaluate(G, n, search_length_cap)
        if new_max is None:
            undo_move(G, move)
            continue
        if new_max <= cur_max:
            cur_max = new_max
            if new_max < best_max:
                best_max = new_max
                best_G = G.copy()
        elif rng.random() < 0.1:  # noise to escape local optima
            cur_max = new_max
        else:
            undo_move(G, move)

    return best_G, best_max


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-start', type=int, default=9)
    ap.add_argument('--n-stop', type=int, default=30)
    ap.add_argument('--d', type=int, default=7)
    ap.add_argument('--iters-per-n', type=int, default=300)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)

    results = {}
    global_min = None
    global_min_info = None

    for n in range(max(args.n_start, args.d + 1), args.n_stop + 1):
        rng = random.Random(args.seed + n)
        t0 = time.time()
        best_G, best_max = local_search(n, args.d, rng, args.iters_per_n)
        elapsed = time.time() - t0

        assert verify_min_outdegree(best_G, args.d), 'BUG: degree constraint violated!'

        escalated_note = ''
        if best_max < 4:
            # a candidate that looks like it might violate the conjecture --
            # escalate to a much more thorough check before believing it
            esc_max, esc_sel, esc_trunc = escalated_recheck(best_G, n)
            escalated_note = (f' [ESCALATED RECHECK: max={esc_max}, cycle-enum truncated={esc_trunc}]')
            if esc_max is not None and esc_max < 4 and not esc_trunc:
                print(f'\n*** POTENTIAL COUNTEREXAMPLE at n={n}: escalated recheck confirms '
                      f'max disjoint cycles = {esc_max} < 4, with min out-degree {args.d} '
                      f'(cycle enumeration NOT truncated -- this needs extremely careful '
                      f'independent re-verification) ***\n', flush=True)
                verified = verify_disjoint_cycles(best_G, esc_sel)
                print(f'    independent verify_disjoint_cycles on the {esc_max} selected '
                      f'cycles: {verified}', flush=True)
                edges = list(best_G.edges())
                with open(os.path.join(out_dir, f'POTENTIAL_COUNTEREXAMPLE_n{n}.json'), 'w') as f:
                    json.dump({'n': n, 'd': args.d, 'edges': edges, 'escalated_max': esc_max}, f, indent=2)
            best_max_report = esc_max if esc_max is not None else best_max
        else:
            best_max_report = best_max

        results[n] = {'best_max_disjoint_found': best_max, 'elapsed': elapsed,
                       'escalated_note': escalated_note}
        print(f'n={n}: best (min achieved) max-disjoint-cycles = {best_max} '
              f'(length<=5 search){escalated_note}, {elapsed:.1f}s', flush=True)

        if global_min is None or best_max < global_min:
            global_min = best_max
            global_min_info = n

        with open(os.path.join(out_dir, 'search_progress.json'), 'w') as f:
            json.dump({'results': results, 'global_min': global_min, 'global_min_n': global_min_info}, f, indent=2)

    print(f'\nDONE. Global minimum max-disjoint-cycles found across all n: {global_min} '
          f'(at n={global_min_info}). Conjecture requires this to always be >= 4.', flush=True)


if __name__ == '__main__':
    main()
