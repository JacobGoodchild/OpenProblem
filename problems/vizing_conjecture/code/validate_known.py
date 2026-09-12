#!/usr/bin/env python3
"""
Sanity checks before attacking the open cases:
  1. Domination numbers of cycles: gamma(C_n) = ceil(n/3), a classical
     exact formula -- reproduce it for several n.
  2. Vizing's conjecture itself, checked directly on several small
     graph pairs (including cases with gamma up to 3, which is PROVEN
     true) -- our own ILP-based check must never find a violation on
     these, since the theorem guarantees it can't happen. If it ever
     does, that's a bug in our tooling, not a mathematical discovery.
  3. The Clark & Suen general lower bound (gamma(G[]H) >= 0.5*gamma(G)*
     gamma(H), proven for ALL G,H) as an extra live sanity check on
     every computed product.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import networkx as nx
from vizing_lib import domination_number, check_vizing

# Check 1: cycle domination numbers
print('Check 1 -- domination number of cycles (known exact formula ceil(n/3)):')
for n in [3, 4, 5, 6, 7, 8, 9, 10]:
    G = nx.cycle_graph(n)
    g, _ = domination_number(G)
    expected = math.ceil(n / 3)
    status = 'OK' if g == expected else '*** MISMATCH ***'
    print(f'  C{n}: computed gamma={g}, expected={expected}  {status}')
    assert g == expected, f'FAILED: domination number formula mismatch for C{n}!'

# Check 2: Vizing's conjecture on small known-true cases
print('\nCheck 2 -- Vizing\'s conjecture on small cases (gamma<=3, PROVEN true; '
      'our ILP must never contradict this):')
test_pairs = [
    (nx.cycle_graph(4), nx.cycle_graph(4)),
    (nx.cycle_graph(5), nx.cycle_graph(3)),
    (nx.path_graph(5), nx.path_graph(5)),
    (nx.petersen_graph(), nx.cycle_graph(4)),
    (nx.complete_graph(4), nx.cycle_graph(5)),
]
for G, H in test_pairs:
    r = check_vizing(G, H, time_limit_each=20)
    ok = r['holds'] is True
    print(f'  |V(G)|={G.number_of_nodes()}, |V(H)|={H.number_of_nodes()}: '
          f"gamma(G)={r.get('gamma_G')}, gamma(H)={r.get('gamma_H')}, "
          f"gamma(G[]H)={r.get('gamma_product')}, bound={r.get('bound')}, holds={r['holds']}")
    assert ok, f'UNEXPECTED: Vizing\'s conjecture appears to FAIL on a small known-true case! {r}'
    # also check Clark & Suen's proven general bound as an extra check
    if r.get('gamma_product') is not None:
        cs_bound = 0.5 * r['bound']
        assert r['gamma_product'] >= cs_bound - 1e-9, 'Clark & Suen bound violated -- definitely a bug!'

print('\nPASS: tooling validated against known formulas and the (already-proven) small cases '
      'of Vizing\'s conjecture. Trusted for the open gamma>=4 investigation.')
