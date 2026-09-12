#!/usr/bin/env python3
"""
Sanity checks for the union-closed sets tooling before attacking the
open range (m > 12):
  1. The full power set of an m-element ground set is a classical tight
     example achieving EXACTLY ratio 0.5 -- reproduce it exactly.
  2. Run the local search itself on small m <= 12 (where the conjecture
     is proven true by exhaustive computer verification) and confirm it
     never finds ratio < 0.5, as a live check that our search code
     doesn't have a bug that would fabricate a false "counterexample".
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.union_closed import union_closure, max_frequency_ratio, verify_union_closed, local_search_min_ratio

m = 4
gens = [0] + [1 << i for i in range(m)]
fam = union_closure(gens, m)
ratio, _ = max_frequency_ratio(fam, m)
print(f'Power set of {{0,1,2,3}}: family size={len(fam)} (expect 16), ratio={ratio} (expect exactly 0.5)')
print(f'  independently verified union-closed: {verify_union_closed(fam)}')
assert len(fam) == 16 and abs(ratio - 0.5) < 1e-9, 'FAILED to reproduce the classical tight example!'

print('\nRunning local search on m=8..12 (conjecture PROVEN true here) -- '
      'should never find ratio < 0.5:')
for m in range(8, 13):
    rng = random.Random(42 + m)
    best_ratio, best_gens, best_size = local_search_min_ratio(m, max(3, m // 3), rng, iters=500)
    ok = best_ratio >= 0.5 - 1e-9
    print(f'  m={m}: best ratio found = {best_ratio:.4f}  ({"OK" if ok else "*** BUG: below 0.5! ***"})')
    assert ok, f'Local search found ratio < 0.5 at m={m}, where the conjecture is PROVEN true -- tooling bug!'

print('\nPASS: tooling validated. Trusted for the m > 12 open-range search.')
