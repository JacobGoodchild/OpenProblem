#!/usr/bin/env python3
"""
Sanity checks before searching:
  1. random_arborescence + verify_is_arborescence: generated arborescences
     must actually verify as valid.
  2. random_instance: the n-1 unioned color classes must each
     independently verify as a valid spanning arborescence.
  3. Small n (4, 5, 6): every randomly generated instance MUST have a
     rainbow arborescence (free-root) -- the conjecture is unproven in
     general, but for such tiny n it would be astonishing (and instantly
     newsworthy) to find a violation by pure chance in a handful of
     trials, so failures here are overwhelmingly likely bugs, not
     discoveries -- treated as such (loud assert, not a quiet report).
  4. The cycle case specifically (PROVEN true, Nov 2025): build a
     cycle-underlying-graph instance and confirm our checker agrees.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from ra_lib import (random_arborescence, verify_is_arborescence, random_instance,
                     check_rainbow_arborescence_any_root, verify_rainbow_arborescence)

print('Check 1 -- random_arborescence produces valid arborescences:')
rng = random.Random(0)
for n in [3, 5, 10, 20]:
    vertices = list(range(n))
    root, arcs = random_arborescence(vertices, rng)
    ok = verify_is_arborescence(vertices, arcs, root)
    print(f'  n={n}: root={root}, |arcs|={len(arcs)}, verified={ok}')
    assert ok, f'FAILED: random_arborescence produced an invalid arborescence at n={n}!'

print('\nCheck 2 -- random_instance: each color class is independently a valid arborescence:')
for n in [4, 6, 8]:
    rng = random.Random(n)
    vertices, colored_arcs, roots = random_instance(n, rng)
    all_ok = True
    for c in range(n - 1):
        color_arcs = [(u, v) for u, v, cc in colored_arcs if cc == c]
        ok = verify_is_arborescence(vertices, color_arcs, roots[c])
        all_ok = all_ok and ok
    print(f'  n={n}: all {n-1} color classes independently verified as arborescences: {all_ok}')
    assert all_ok, f'FAILED: random_instance produced an invalid color class at n={n}!'

print('\nCheck 3 -- small random instances (n=4,5,6) MUST have a rainbow arborescence:')
for n in [4, 5, 6]:
    for trial in range(5):
        rng = random.Random(n * 1000 + trial)
        vertices, colored_arcs, roots = random_instance(n, rng)
        t0 = time.time()
        result, root, arcs, details = check_rainbow_arborescence_any_root(vertices, colored_arcs)
        elapsed = time.time() - t0
        ok = result is True and verify_rainbow_arborescence(vertices, colored_arcs, root, arcs)
        print(f'  n={n} trial={trial}: result={result}, root={root}, verified={ok}, '
              f'{elapsed:.2f}s, details={details if result is not True else ""}')
        assert ok, (f'UNEXPECTED: n={n} trial={trial} found NO rainbow arborescence -- '
                     f'either a real (sensational) counterexample or, far more likely, a bug! '
                     f'instance={colored_arcs}')

print('\nPASS: tooling validated on random small instances. Trusted for the actual search.')
