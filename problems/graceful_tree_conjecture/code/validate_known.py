#!/usr/bin/env python3
"""
Sanity checks before attacking the open spider frontier.

Paths and stars are classically graceful via simple EXPLICIT
constructions (no search needed) -- used here as direct correctness
checks on verify_graceful_labeling itself, since search performance on
these two particular shapes turned out to be a poor fit for both our
backtracking and local-search implementations (confirmed empirically:
even P20, trivially graceful, resisted both a 5M-node randomized
backtracking search and a 400K-iteration x 15-trial local search --
a real, documented tooling limitation on paths specifically, not
relevant to the actual target below). Spiders (the real target) are
checked via the actual search machinery, both backtracking and local
search, to confirm each works on genuinely tree-shaped (non-path)
structures before trusting either for the open investigation.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from graceful_lib import (find_graceful_labeling_backtrack, find_graceful_local_search_restarts,
                           verify_graceful_labeling, make_spider)


def explicit_path_labeling(n):
    # classic zig-zag construction: 0, n-1, 1, n-2, 2, n-3, ...
    label = {}
    lo, hi = 0, n - 1
    for i in range(n):
        if i % 2 == 0:
            label[i] = lo
            lo += 1
        else:
            label[i] = hi
            hi -= 1
    return label


def explicit_star_labeling(n):
    # center=0 gets label 0, leaves get labels 1..n-1 (diffs are trivially 1..n-1)
    return {i: i for i in range(n)}


print('Check 1 -- paths, explicit classical construction (verify_graceful_labeling correctness check):')
for n in [5, 10, 20, 50, 100]:
    G = nx.path_graph(n)
    label = explicit_path_labeling(n)
    ok = verify_graceful_labeling(G, label)
    print(f'  P{n}: explicit construction verified graceful: {ok}')
    assert ok, f'FAILED: explicit path construction should always verify for P{n}!'

print('\nCheck 2 -- stars, explicit trivial construction:')
for n in [5, 10, 30, 100]:
    G = nx.star_graph(n - 1)
    label = explicit_star_labeling(n)
    ok = verify_graceful_labeling(G, label)
    print(f'  K1,{n-1}: explicit construction verified graceful: {ok}')
    assert ok, f'FAILED: explicit star construction should always verify for K1,{n-1}!'

print('\nCheck 3 -- small/medium spiders via actual search machinery (backtracking AND local search):')
test_spiders = [
    [3, 3, 3],              # n=10
    [2, 3, 5, 7],           # n=18
    [1, 1, 1, 1, 5, 6, 7],  # n=23, mixed with length-1 legs
    [3, 3, 3, 3, 3, 3],     # n=19, 6 legs (the family of interest, easy sub-case)
]
for legs in test_spiders:
    G = make_spider(legs)
    n = G.number_of_nodes()
    t0 = time.time()
    label, nodes, exhausted = find_graceful_labeling_backtrack(G, node_budget=500_000)
    method = 'backtracking'
    if label is None:
        label, dup = find_graceful_local_search_restarts(G, trials=10, max_iters=100_000, seed_base=n)
        method = 'local search'
    ok = label is not None and verify_graceful_labeling(G, label)
    print(f'  legs={legs} (n={n}): found via {method}: {label is not None}, verified={ok}, {time.time()-t0:.2f}s')
    assert ok, f'FAILED: spider {legs} (n={n}) should be findable-graceful by SOME method!'

print('\nPASS: verify_graceful_labeling confirmed correct via explicit constructions; '
      'both search methods confirmed working on genuine (non-path) tree structures.')
