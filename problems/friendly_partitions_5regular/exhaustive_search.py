"""
Exhaustively check EVERY connected 5-regular graph on n vertices (for small
n, using nauty-geng to generate all of them up to isomorphism) for the
existence of a friendly (internal) partition.

Usage: python3 exhaustive_search.py N [--timeout-per-graph SECONDS]

Writes results/exhaustive_n{N}.json with a summary and a list of any
"exceptions" (graphs proven, via exact SAT, to have NO friendly partition).
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import networkx as nx
from friendly_partitions_sat import sat_friendly_partition


def gen_graphs(n):
    """Yield networkx Graphs: all connected 5-regular graphs on n vertices."""
    proc = subprocess.Popen(
        ["nauty-geng", "-c", "-d5", "-D5", str(n)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    for line in proc.stdout:
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        yield nx.from_graph6_bytes(line.encode())
    proc.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--limit", type=int, default=None, help="stop after checking this many graphs")
    args = ap.parse_args()

    n = args.n
    outdir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"exhaustive_n{n}.json")

    checked = 0
    exceptions = []
    t0 = time.time()
    for G in gen_graphs(n):
        if args.limit and checked >= args.limit:
            break
        r = sat_friendly_partition(G)
        checked += 1
        if not r.sat:
            g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
            exceptions.append({"n": n, "graph6": g6, "edges": sorted(map(sorted, G.edges()))})
            print(f"  [n={n}] EXCEPTION found! graph6={g6}", flush=True)
        if checked % 500 == 0:
            print(f"  [n={n}] checked {checked} graphs, {len(exceptions)} exceptions so far, "
                  f"{time.time()-t0:.1f}s elapsed", flush=True)

    elapsed = time.time() - t0
    result = {
        "n": n,
        "graphs_checked": checked,
        "num_exceptions": len(exceptions),
        "exceptions": exceptions,
        "elapsed_seconds": elapsed,
    }
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"n={n}: checked {checked} connected 5-regular graphs in {elapsed:.1f}s, "
          f"found {len(exceptions)} without a friendly partition. Saved to {outpath}")


if __name__ == "__main__":
    main()
