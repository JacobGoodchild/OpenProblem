#!/usr/bin/env python3
"""
Sanity check before attacking R(5,5): reproduce the classical circulant
witness for R(4,4)=18, i.e. the Paley graph on 17 vertices (quadratic
residues mod 17 as the connection set). This is a circulant / Cayley
graph on Z_17, self-complementary, K4-free with independence number 3 --
the textbook example that R(4,4) >= 18. If our generalized clique-free
checker (lib/circulant_ramsey.is_clique_free, already validated for
R(4,6)/R(4,7) against networkx) reproduces this correctly, we trust it
for the K5-vs-K5 search on R(5,5).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free

n = 17
qr = set((x * x) % n for x in range(1, n))
# reduce to "distance" representation: distance d in {1..8} is in the
# connection set iff d or n-d is a quadratic residue
half = n // 2
S = set(d for d in range(1, half + 1) if d in qr or (n - d) % n in qr)
print(f'Paley(17) distance set: {sorted(S)}')

comp = set(range(1, half + 1)) - S
print(f'complement distance set: {sorted(comp)}')

ok1 = is_clique_free(S, n, 4)
ok2 = is_clique_free(comp, n, 4)
print(f'Paley(17) graph K4-free: {ok1}')
print(f'Paley(17) complement K4-free: {ok2}')

if ok1 and ok2:
    print('PASS: reproduces the known R(4,4)>=18 witness. Tooling trusted for R(5,5) search.')
else:
    print('FAIL: something is wrong with is_clique_free or the QR construction.')
    sys.exit(1)
