"""
UNORTHODOX METHOD: adversarial / evolutionary search over the SPACE OF
GRAPHS ITSELF (not just over partitions of a fixed graph), directly
hunting for 5-regular graphs that are hard -- or impossible -- to give a
friendly partition.

Idea
----
Random 5-regular graphs almost always have a friendly partition (easy to
find). The known exceptions (K6 and its small cousins) are highly
atypical. So instead of sampling randomly and hoping to stumble on a rare
exception, we run simulated annealing *on the graph itself*:

  state      = a connected simple 5-regular graph G on n vertices
  move       = a random degree-preserving double edge swap
               (a,b),(c,d) -> (a,d),(c,b)   [rejected if it creates a
               multi-edge/self-loop, or disconnects the graph]
  "badness"  = how hard G is to satisfy: we run the fast local-search
               heuristic from many random restarts and record the
               fewest-still-unhappy-vertices achieved. 0 badness means a
               friendly partition was found; positive badness means every
               attempt got stuck with that many vertices still unhappy.
  acceptance = standard Metropolis: always accept if badness doesn't
               decrease; accept a decrease with probability exp(delta/T).

We anneal upward in n as well: whenever the search converges (many moves
without improving badness) on a graph with badness==0 everywhere nearby,
we are wasting time -- so this script also supports simply hammering a
fixed n hard for a long time. Any G ending with badness > 0 after the
full annealing budget is escalated to the exact SAT oracle: a positive
answer there (UNSAT = no friendly partition) is a genuine, rigorously
verified new exception.

Usage: python3 adversarial_search.py N --steps 20000 --restarts-per-eval 6
"""
import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import networkx as nx
from friendly_partitions import local_search_friendly_partition
from friendly_partitions_sat import sat_friendly_partition


def badness(G, rng, restarts=6, max_flips=1500):
    """0 if a friendly partition was found (by the robust, perturbation-
    capable local search); else the fewest still-unhappy vertices it ever
    got down to across all restarts -- how close it came."""
    r = local_search_friendly_partition(G, rng, max_flips=max_flips, restarts=restarts)
    if r.found:
        return 0
    return max(r.closest_unhappy, 0)
    return best


def double_edge_swap(G, rng, tries=50):
    edges = list(G.edges())
    for _ in range(tries):
        (a, b), (c, d) = rng.sample(edges, 2)
        if len({a, b, c, d}) < 4:
            continue
        if G.has_edge(a, d) or G.has_edge(c, b):
            continue
        H = G.copy()
        H.remove_edge(a, b)
        H.remove_edge(c, d)
        H.add_edge(a, d)
        H.add_edge(c, b)
        if nx.is_connected(H):
            return H
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--restarts-per-eval", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--t0", type=float, default=2.0)
    ap.add_argument("--tmin", type=float, default=0.05)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    n = args.n
    outdir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(outdir, exist_ok=True)

    G = nx.random_regular_graph(5, n, seed=rng.randrange(2**31))
    while not nx.is_connected(G):
        G = nx.random_regular_graph(5, n, seed=rng.randrange(2**31))

    cur_bad = badness(G, rng, restarts=args.restarts_per_eval)
    best_bad = cur_bad
    best_G = G.copy()
    t0 = time.time()
    history = []
    for step in range(args.steps):
        T = args.t0 * (args.tmin / args.t0) ** (step / args.steps)
        H = double_edge_swap(G, rng)
        if H is None:
            continue
        h_bad = badness(H, rng, restarts=args.restarts_per_eval)
        delta = h_bad - cur_bad
        if delta >= 0 or rng.random() < math.exp(delta / max(T, 1e-6)):
            G, cur_bad = H, h_bad
        if cur_bad > best_bad:
            best_bad, best_G = cur_bad, G.copy()
        if step % 1000 == 0:
            elapsed = time.time() - t0
            print(f"  [n={n}] step {step}/{args.steps} T={T:.3f} cur_bad={cur_bad} "
                  f"best_bad={best_bad} elapsed={elapsed:.1f}s", flush=True)
            history.append({"step": step, "cur_bad": cur_bad, "best_bad": best_bad})

    # escalate the best (hardest) graph found to the exact SAT oracle
    sat_result = sat_friendly_partition(best_G)
    g6 = nx.to_graph6_bytes(best_G, header=False).decode().strip()
    out = {
        "n": n, "steps": args.steps, "seed": args.seed,
        "best_heuristic_badness": best_bad,
        "sat_has_friendly_partition": sat_result.sat,
        "graph6": g6,
        "history": history,
    }
    outpath = os.path.join(outdir, f"adversarial_n{n}_seed{args.seed}.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)
    verdict = "NO FRIENDLY PARTITION -- genuine exception!" if not sat_result.sat else \
              "has a friendly partition (heuristic just missed it)"
    print(f"n={n} seed={args.seed}: best heuristic badness={best_bad}. "
          f"SAT oracle says graph {verdict}. graph6={g6}")
    print(f"Saved to {outpath}")


if __name__ == "__main__":
    main()
