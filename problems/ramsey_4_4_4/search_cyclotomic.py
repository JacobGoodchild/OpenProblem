#!/usr/bin/env python3
"""
THE ACTUAL ATTACK on R(4,4,4), now targeting the RIGHT structured space:
having confirmed (validate_known.py) that the real 127-vertex record is
a cyclotomic cubic-residue construction, search primes p > 127 with
p = 1 (mod 3) (so Z_p^* has a subgroup of index 3, giving 3 cubic-residue
cosets) for one where all 3 cosets are simultaneously K4-free. Unlike
generic local search over arbitrary partitions (which this project's
R(3,3,3,3) attempt showed has no bias toward finding this kind of
algebraic structure), this searches EXACTLY the family the real record
comes from -- a much better-motivated (though still narrow) search.

Note: this only searches PRIME p with -1 a cubic residue (needed for
the cosets to be valid "distance classes" for a circulant coloring).
Not all such p will have -1 as a cube; we check and skip those that don't.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.circulant_ramsey import is_clique_free


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def find_generator_not_in(subgroup, p):
    for g in range(2, p):
        if g not in subgroup:
            return g
    return None


def try_prime(p):
    """Returns (success, distance_sets) if p yields a valid (K4,K4,K4)-free
    cyclotomic coloring, else (False, None). None if p isn't eligible."""
    if (p - 1) % 3 != 0:
        return None
    cubes = set(pow(x, 3, p) for x in range(1, p))
    if len(cubes) != (p - 1) // 3:
        return None  # shouldn't happen for prime p with 3 | p-1, but be safe
    if (p - 1) not in cubes:
        return None  # -1 not a cubic residue -- cosets aren't negation-closed

    g = find_generator_not_in(cubes, p)
    coset0 = cubes
    coset1 = set((g * x) % p for x in cubes)
    coset2 = set((g * g * x) % p for x in cubes)
    if not (coset0 | coset1 | coset2 == set(range(1, p)) and
            len(coset0) == len(coset1) == len(coset2)):
        return None  # g wasn't a valid non-cubic-residue rep; skip (rare)

    def to_distance_set(coset):
        return set(min(d, p - d) for d in coset)

    D0, D1, D2 = to_distance_set(coset0), to_distance_set(coset1), to_distance_set(coset2)

    ok = (is_clique_free(D0, p, 4) and is_clique_free(D1, p, 4) and is_clique_free(D2, p, 4))
    return ok, [sorted(D0), sorted(D1), sorted(D2)] if ok else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=128)
    ap.add_argument('--stop', type=int, default=600)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)

    checked_primes = []
    found = []
    start_t = time.time()

    for p in range(args.start, args.stop + 1):
        if not is_prime(p):
            continue
        result = try_prime(p)
        if result is None:
            continue  # not eligible (p != 1 mod 3, or -1 not a cube, etc.)
        checked_primes.append(p)
        ok, D = result
        if ok:
            found.append(p)
            print(f'p={p}: *** FOUND (K4,K4,K4)-free cyclotomic coloring! '
                  f'This gives R(4,4,4) >= {p+1} ***', flush=True)
            with open(os.path.join(out_dir, f'FOUND_p{p}.json'), 'w') as f:
                json.dump({'p': p, 'distance_sets': D}, f, indent=2)
        else:
            print(f'p={p}: eligible cyclotomic prime, but coloring is NOT (K4,K4,K4)-free', flush=True)

    elapsed = time.time() - start_t
    print(f'\nDONE. Checked {len(checked_primes)} eligible primes in [{args.start},{args.stop}] '
          f'({elapsed:.1f}s). Found {len(found)} valid witnesses: {found}', flush=True)

    with open(os.path.join(out_dir, 'cyclotomic_search_summary.json'), 'w') as f:
        json.dump({'range': [args.start, args.stop], 'eligible_primes_checked': checked_primes,
                   'found': found, 'elapsed': elapsed}, f, indent=2)


if __name__ == '__main__':
    main()
