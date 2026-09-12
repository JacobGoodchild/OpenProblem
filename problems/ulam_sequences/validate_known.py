#!/usr/bin/env python3
"""
Sanity checks for the Ulam/1-additive sequence generator before the
deep sweep:
  1. U(1,2) (the classical Ulam sequence) must exactly match the first
     30 terms of OEIS A002858.
  2. U(4,5) (Cassaigne & Finch proved all (4,n) with n=1 mod 4 are
     eventually periodic with exactly 3 even terms) must be found
     periodic by our own from-scratch periodicity detector.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.ulam_sequences import generate_ulam, gaps, find_period

terms = generate_ulam(1, 2, 30)
known_A002858 = [1, 2, 3, 4, 6, 8, 11, 13, 16, 18, 26, 28, 36, 38, 47, 48,
                  53, 57, 62, 69, 72, 77, 82, 87, 97, 99, 102, 106, 114, 126]
match = list(int(x) for x in terms) == known_A002858
print(f'U(1,2) first 30 terms match OEIS A002858: {match}')
assert match, 'FAILED to reproduce the classical Ulam sequence!'

terms = generate_ulam(4, 5, 5000)
g = gaps(terms)
res = find_period(g, max_period=50)
print(f'U(4,5), 5000 terms: periodicity result = {res} '
      f'(expected: some period found, proven eventually periodic in the literature)')
assert res is not None, 'FAILED to detect periodicity in a known-periodic case!'

# independent count of even terms in U(4,5) -- literature says exactly 3 even terms total
n_even = int((terms % 2 == 0).sum())
print(f'U(4,5): number of even terms among {len(terms)} computed = {n_even} '
      f'(literature: exactly 3, proven by Cassaigne & Finch)')

print('\nPASS: tooling validated on two independently-checkable known cases.')
