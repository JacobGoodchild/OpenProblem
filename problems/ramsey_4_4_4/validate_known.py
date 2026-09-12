#!/usr/bin/env python3
"""
Attempt to directly reproduce Hill & Irving's classical G_127 construction
for R(4,4,4) >= 128: a cyclotomic (cubic-residue) 3-coloring of K_127.

Since 127 is prime and 127-1 = 126 = 3*42, the multiplicative group
Z_127^* has a subgroup of index 3 (the cubic residues, size 42), giving
3 cosets that partition Z_127^*. We checked computationally that -1 IS
a cubic residue mod 127, so these cosets are each closed under negation
-- meaning they can be used directly as "distance classes" for a
3-coloring of the circulant graph on Z_127 (color of edge {v, v+d} =
which coset d's residue-class falls into). This is the standard
cyclotomic-coloring technique, and it's exactly the kind of algebraic
structure a generic local search has no special bias toward finding
(as flagged as a limitation in this project's R(3,3,3,3) write-up).

If this reproduces a genuine (K4,K4,K4)-free coloring, it: (a) validates
our tooling on the actual real-world record construction (not just an
invented sanity check), and (b) confirms the record is indeed circulant,
meaning a smarter cyclotomic-aware search (rather than generic local
search) is the right next step to try to extend it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free

p = 127
cubes = set(pow(x, 3, p) for x in range(1, p))
print(f'Number of distinct nonzero cubic residues mod {p}: {len(cubes)}')
print(f'-1 ({p-1}) is a cubic residue: {(p - 1) in cubes}')

# the three cosets of the cubic-residue subgroup
g = 3  # a generator check isn't needed; we just need SOME element not in `cubes`
coset0 = cubes
coset1 = set((g * x) % p for x in cubes)
coset2 = set((g * g * x) % p for x in cubes)
assert coset0 | coset1 | coset2 == set(range(1, p)), 'cosets do not partition Z_127^*'
assert len(coset0) == len(coset1) == len(coset2) == 42, 'cosets not equal size — g not a valid coset rep'

half = p // 2  # 63
# reduce each full coset (closed under negation) to its "distance" representation
def to_distance_set(coset):
    return set(min(d, p - d) for d in coset)

D0, D1, D2 = to_distance_set(coset0), to_distance_set(coset1), to_distance_set(coset2)
print(f'distance-set sizes: {len(D0)}, {len(D1)}, {len(D2)} (should each be 21, i.e. 42/2)')
assert D0 | D1 | D2 == set(range(1, half + 1)) and len(D0) + len(D1) + len(D2) == half

ok0 = is_clique_free(D0, p, 4)
ok1 = is_clique_free(D1, p, 4)
ok2 = is_clique_free(D2, p, 4)
print(f'coset 0 K4-free: {ok0}')
print(f'coset 1 K4-free: {ok1}')
print(f'coset 2 K4-free: {ok2}')

if ok0 and ok1 and ok2:
    print('PASS: reproduced the real Hill-Irving G_127 witness for R(4,4,4) >= 128 '
          '(cyclotomic cubic-residue construction). Tooling trusted; record confirmed circulant.')
else:
    print('Cosets as constructed did NOT reproduce a valid witness -- either the coset '
          'assignment (which of the 3 cosets is "coset0" vs 1 vs 2) or generator choice '
          'differs from the literature construction, or our cyclotomic hypothesis is wrong.')
