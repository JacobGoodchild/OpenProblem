"""
Simulated-annealing search for a counterexample to Seymour's Second
Neighborhood Conjecture (SNC), restricted to "tournaments missing m
edges" (the frontier where the conjecture is still open -- it is PROVEN
for full tournaments, m=0).

We search directly for graphs where EVERY vertex is "bad"
(|N++(v)| < |N+(v)|), which is exactly a counterexample. Since none is
believed to exist, the realistic goal is to (a) confirm no counterexample
turns up even under adversarial pressure, for a range of (n, m), and
(b) report how close we can force the graph to get (max fraction of
simultaneously-bad vertices), which is itself an interesting empirical
quantity: the conjecture is "tight" in the sense that adversarial search
easily forces ALL BUT ONE vertex to be bad, but that stubborn last vertex
never disappears.

Usage: python3 adversarial_search.py N M --steps 20000
"""
import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import numpy as np
from second_neighborhood import (
    random_tournament_minus_m, slack_per_vertex, count_bad,
    flip_arc_move, move_gap_move,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("m", type=int, help="number of missing edges (0 = full tournament)")
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--t0", type=float, default=3.0)
    ap.add_argument("--tmin", type=float, default=0.05)
    args = ap.parse_args()

    n, m = args.n, args.m
    rng = random.Random(args.seed)
    A = random_tournament_minus_m(n, m, rng)
    cur = count_bad(A)
    best, best_A = cur, A.copy()
    t0 = time.time()
    history = []
    for step in range(args.steps):
        T = args.t0 * (args.tmin / args.t0) ** (step / args.steps)
        if m > 0 and rng.random() < 0.3:
            B = move_gap_move(A, rng)
        else:
            B = flip_arc_move(A, rng)
        b = count_bad(B)
        delta = b - cur
        if delta >= 0 or rng.random() < math.exp(delta / max(T, 1e-6)):
            A, cur = B, b
        if cur > best:
            best, best_A = cur, A.copy()
            if best == n:
                break  # would be a genuine counterexample!
        if step % 2000 == 0:
            print(f"  [n={n} m={m}] step {step}/{args.steps} T={T:.3f} cur_bad={cur}/{n} "
                  f"best_bad={best}/{n} elapsed={time.time()-t0:.1f}s", flush=True)
            history.append({"step": step, "cur_bad": cur, "best_bad": best})

    S = slack_per_vertex(best_A)
    is_counterexample = bool((S < 0).all())
    outdir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(outdir, exist_ok=True)
    out = {
        "n": n, "m": m, "steps": args.steps, "seed": args.seed,
        "best_bad": best, "best_bad_fraction": best / n,
        "is_true_counterexample": is_counterexample,
        "slack_of_best": S.tolist(),
        "adjacency": best_A.tolist(),
        "history": history,
        "elapsed_seconds": time.time() - t0,
    }
    outpath = os.path.join(outdir, f"adv_n{n}_m{m}_seed{args.seed}.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)

    verdict = "*** GENUINE COUNTEREXAMPLE FOUND ***" if is_counterexample else \
              f"no counterexample (best: {best}/{n} vertices simultaneously bad, " \
              f"{n-best} vertex(es) always satisfy the conjecture)"
    print(f"n={n} m={m}: {verdict}")
    print(f"Saved to {outpath}")


if __name__ == "__main__":
    main()
