#!/usr/bin/env python3
"""
Sanity checks before attacking k=4:
  1. The complete bidirected digraph on 8 vertices (the unique
     min-out-degree-7 digraph at the smallest possible n) trivially
     has >=4 disjoint cycles (via digons alone) -- confirms the
     ILP packing + cycle enumeration machinery works correctly.
  2. A digraph built as exactly 4 disjoint directed cycles (plus no
     other edges) must report max disjoint = exactly 4, not more or
     less -- confirms the ILP isn't over/under-counting.
  3. Try the k=2 and k=3 cases (already PROVEN true) on random digraphs
     with the corresponding minimum out-degree (2*2-1=3, 2*3-1=5) to
     make sure our machinery agrees with established theory before
     trusting it on the open k=4 case.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from bt_lib import (random_min_outdegree_digraph, enumerate_cycles,
                     max_disjoint_cycle_packing, verify_disjoint_cycles, verify_min_outdegree)

# check 1: K8* trivially has >=4 disjoint cycles
G = nx.complete_graph(8, create_using=nx.DiGraph())
cycles, trunc = enumerate_cycles(G, max_length=2)
maxc, sel = max_disjoint_cycle_packing(8, cycles, time_limit=10)
print(f'Check 1 -- K8* (complete digraph, min out-degree 7): max disjoint cycles = {maxc} (expect 4)')
assert maxc == 4 and verify_disjoint_cycles(G, sel)

# check 2: exactly 4 disjoint cycles by construction, nothing else
G2 = nx.DiGraph()
# 4 disjoint cycles of varying length: [0,1,2], [3,4], [5,6,7,8], [9,10]
cycle_defs = [[0, 1, 2], [3, 4], [5, 6, 7, 8], [9, 10]]
for cyc in cycle_defs:
    for i in range(len(cyc)):
        G2.add_edge(cyc[i], cyc[(i + 1) % len(cyc)])
cycles2, trunc2 = enumerate_cycles(G2, max_length=10)
maxc2, sel2 = max_disjoint_cycle_packing(11, cycles2, time_limit=10)
print(f'Check 2 -- exactly-4-disjoint-cycles-by-construction graph: max disjoint = {maxc2} (expect 4)')
assert maxc2 == 4 and verify_disjoint_cycles(G2, sel2)

# check 3: k=2 (proven, min out-degree 3) and k=3 (proven, min out-degree 5)
# on random digraphs -- should ALWAYS find enough disjoint cycles
random.seed(0)
for k, d, trials in [(2, 3, 10), (3, 5, 10)]:
    all_ok = True
    for t in range(trials):
        rng = random.Random(t)
        n = d + 1 + t  # grow n a bit across trials
        G3 = random_min_outdegree_digraph(n, d, rng)
        assert verify_min_outdegree(G3, d)
        cycles3, trunc3 = enumerate_cycles(G3, max_length=6)
        maxc3, sel3 = max_disjoint_cycle_packing(n, cycles3, time_limit=10)
        if maxc3 is None or maxc3 < k:
            all_ok = False
            print(f'  UNEXPECTED: k={k}, trial={t}, n={n}: only found {maxc3} disjoint cycles '
                  f'(within length<=6) -- proven theorem says >= {k} must exist!')
    print(f'Check 3 -- k={k} (proven, min out-degree {d}), {trials} random trials: '
          f'{"all found >= " + str(k) + " disjoint cycles (as proven theory requires)" if all_ok else "SOME TRIALS FAILED -- investigate!"}')

print('\nPASS (assuming no failures printed above): tooling validated against known theory. Trusted for k=4.')
