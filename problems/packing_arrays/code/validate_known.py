#!/usr/bin/env python3
"""
Sanity checks before attacking open instances:
  1. k=2 trivial case: PA(N;2,2,g) exists iff N <= g^2 (there are only
     g^2 possible ordered pairs for 2 columns) -- confirm SAT finds a
     solution at N=g^2 and correctly reports UNSAT at N=g^2+1.
  2. MOLS-equivalence sanity check (small case, deliberately NOT
     touching order 10): a Packing Array with k columns hitting the
     N=g^2 upper bound is equivalent to k-2 MOLS of order g existing.
     For g=4 (where 3 MOLS exist, since 4 is a prime power), confirm
     PA(16; 5, 4) [5 = 2 base columns + 3 MOLS columns] is achievable
     -- reproduces a known design via a totally different (SAT, not
     Latin-square) encoding, a real cross-check.
  3. Every found array is independently re-verified from scratch.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from pa_lib import solve_pa, verify_packing_array

print('Check 1 -- k=2 trivial bound N=g^2:')
for g in [3, 4, 5]:
    N = g * g
    t0 = time.time()
    sat, array = solve_pa(N, 2, g)
    ok = sat and verify_packing_array(array, 2, g)
    print(f'  g={g}: PA({N};2,2,{g}) SAT={sat}, verified={ok}, {time.time()-t0:.2f}s')
    assert ok, f'FAILED: PA({N};2,2,{g}) should exist (trivial all-pairs construction)!'

# UNSAT-side re-confirmation only for the smallest g -- proving UNSAT is
# much harder for the solver than finding SAT (the same pattern seen
# repeatedly elsewhere in this project), and the underlying reasoning
# (only g^2 distinct ordered pairs exist for 2 columns) is basic
# combinatorics we don't need heavy exact search to reconfirm per g.
t0 = time.time()
sat2, array2 = solve_pa(10, 2, 3)
print(f'  g=3: PA(10;2,2,3) SAT={sat2} (expect False -- only g^2=9 distinct pairs possible), '
      f'{time.time()-t0:.2f}s')
assert sat2 is False, 'FAILED: PA(10;2,2,3) should be UNSAT (exceeds the g^2 bound)!'

print('\nCheck 2 -- MOLS-equivalence sanity check (g=4, small, NOT touching order 10):')
t0 = time.time()
sat, array = solve_pa(16, 5, 4)
ok = sat and verify_packing_array(array, 5, 4)
print(f'  PA(16;2,5,4) [=2 base cols + 3 MOLS of order 4, known to exist]: '
      f'SAT={sat}, verified={ok}, {time.time()-t0:.2f}s')
assert ok, 'FAILED: PA(16;2,5,4) should exist (3 MOLS of order 4 are known to exist)!'

print('\nPASS: tooling validated against trivial bounds and a known MOLS-equivalent construction.')
