"""
Sample many random connected 5-regular graphs at a given n (configuration
model + rejection of multi-edges/self-loops/disconnected graphs), and for
each check (heuristically first, then exactly via SAT if the heuristic
fails) whether a friendly partition exists. This extends our empirical
picture of the exception rate to n well beyond what exhaustive nauty-geng
enumeration can reach.

Usage: python3 random_search.py N --samples 2000
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import networkx as nx
from friendly_partitions import local_search_friendly_partition
from friendly_partitions_sat import sat_friendly_partition


def random_5regular_connected(n, rng, tries=200):
    for _ in range(tries):
        try:
            G = nx.random_regular_graph(5, n, seed=rng.randrange(2**31))
        except nx.NetworkXError:
            continue
        if nx.is_connected(G):
            return G
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    n = args.n
    rng = random.Random(args.seed)
    outdir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"random_n{n}_seed{args.seed}.json")

    checked = 0
    exceptions = []
    heuristic_hits = 0
    t0 = time.time()
    for i in range(args.samples):
        G = random_5regular_connected(n, rng)
        if G is None:
            continue
        r_ls = local_search_friendly_partition(G, rng, max_flips=4000, restarts=8)
        checked += 1
        if r_ls.found:
            heuristic_hits += 1
            continue
        # heuristic failed -- escalate to exact SAT
        r_sat = sat_friendly_partition(G)
        if not r_sat.sat:
            g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
            exceptions.append({"n": n, "graph6": g6})
            print(f"  [n={n}] EXCEPTION (SAT-proven) graph6={g6}", flush=True)
        if checked % 100 == 0:
            print(f"  [n={n}] checked {checked}/{args.samples} random samples, "
                  f"{len(exceptions)} exceptions, {time.time()-t0:.1f}s elapsed", flush=True)

    elapsed = time.time() - t0
    result = {
        "n": n, "samples_checked": checked, "heuristic_hits": heuristic_hits,
        "num_exceptions": len(exceptions), "exceptions": exceptions,
        "elapsed_seconds": elapsed,
    }
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"n={n}: {checked} random 5-regular graphs checked, {len(exceptions)} exceptions found. "
          f"Saved to {outpath}")


if __name__ == "__main__":
    main()
