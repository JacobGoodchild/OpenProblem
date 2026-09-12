#!/usr/bin/env python3
"""
Sanity checks before attacking n=6:
  1. Q_n for small n (2,3,4) -- every matching tested (several random
     matchings of varying size, including maximal and perfect ones)
     must extend to a Hamiltonian cycle, since the conjecture is known
     true at these tiny sizes (well within MathCheck's n=5 verification,
     and n<=4 is utterly trivial by hand).
  2. Every found extension is independently re-verified from scratch.
  3. A basic Hamiltonicity sanity check: Q_n itself (empty matching) is
     known Hamiltonian for all n>=2 (the standard Gray-code Hamiltonian
     cycle) -- confirm our SAT encoding finds one with zero required
     edges too.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from rs_lib import hypercube, random_matching, random_maximal_matching, extends_to_hamiltonian_cycle, verify_extension

print('Check 1 -- empty matching (must find SOME Hamiltonian cycle, e.g. Gray code):')
for n in [2, 3, 4]:
    G = hypercube(n)
    t0 = time.time()
    result, cycle, iters, status = extends_to_hamiltonian_cycle(G, [])
    ok = result is True and verify_extension(G, [], cycle)
    print(f'  Q{n}: result={result}, verified={ok}, {iters} iterations, {time.time()-t0:.2f}s')
    assert ok, f'FAILED: Q{n} must be Hamiltonian (classical Gray-code result)!'

print('\nCheck 2 -- random matchings of various sizes on Q2,Q3,Q4 (all must extend, '
      'known true at these tiny sizes):')
random.seed(0)
for n in [2, 3, 4]:
    G = hypercube(n)
    for trial in range(5):
        rng = random.Random(trial + n * 100)
        size = rng.randint(1, (2 ** n) // 2)
        M = random_matching(G, rng, target_size=size)
        t0 = time.time()
        result, cycle, iters, status = extends_to_hamiltonian_cycle(G, M)
        ok = result is True and verify_extension(G, M, cycle)
        print(f'  Q{n}, |M|={len(M)}: result={result}, verified={ok}, {iters} iters, {time.time()-t0:.2f}s')
        assert ok, f'FAILED: matching {M} on Q{n} should extend -- known true at this size!'

print('\nCheck 3 -- maximal matchings on Q3, Q4 (the literature-flagged tricky case, '
      'still must extend at these small, already-safe sizes):')
for n in [3, 4]:
    G = hypercube(n)
    for trial in range(5):
        rng = random.Random(trial + n * 1000)
        M = random_maximal_matching(G, rng)
        t0 = time.time()
        result, cycle, iters, status = extends_to_hamiltonian_cycle(G, M)
        ok = result is True and verify_extension(G, M, cycle)
        print(f'  Q{n}, maximal |M|={len(M)}: result={result}, verified={ok}, '
              f'{iters} iters, {time.time()-t0:.2f}s')
        assert ok, f'FAILED: maximal matching {M} on Q{n} should extend!'

print('\nPASS: tooling validated on Q2-Q4 (empty, random, and maximal matchings). Trusted for Q5/Q6.')
