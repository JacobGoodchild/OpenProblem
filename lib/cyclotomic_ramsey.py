"""
Generalizes the R(4,4,4) cyclotomic (prime power residue) construction
technique into a reusable search tool, so it can be applied as a cheap,
EXHAUSTIVE complement to the generic local search used elsewhere in this
project (lib/multicolor_circulant.py) for multiple open Ramsey numbers.

Background: for a prime p with r | (p-1), the multiplicative group
Z_p^* has a subgroup of index r (the r-th power residues), giving r
cosets that partition Z_p^*. If -1 is itself an r-th power residue mod
p, each coset is closed under negation, so the cosets can be used
directly as "distance classes" for an r-coloring of the circulant graph
on Z_p -- this is the standard cyclotomic-coloring technique, and it's
exactly how the real R(4,4,4) record (Hill & Irving's G_127, cubic
residues mod 127) is built. Checking a candidate prime this way is pure
fast arithmetic (build cosets, then the existing is_clique_free check
per color) -- MUCH cheaper than local search, so we can afford to check
every eligible prime in a wide range exhaustively, not just sample.
"""
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


def find_non_residue(subgroup, p):
    for g in range(2, p):
        if g not in subgroup:
            return g
    return None


def cyclotomic_cosets(p, r):
    """Returns the r cosets of the index-r subgroup of Z_p^*, or None if
    r does not divide p-1, or if -1 is not in the subgroup (cosets
    wouldn't be negation-closed), or some other degeneracy occurs."""
    if (p - 1) % r != 0:
        return None
    subgroup = set(pow(x, r, p) for x in range(1, p))
    if len(subgroup) != (p - 1) // r:
        return None
    if (p - 1) not in subgroup:
        return None  # -1 not in the subgroup

    cosets = [subgroup]
    covered = set(subgroup)
    g = 2
    while len(cosets) < r:
        if g not in covered:
            new_coset = set((g * x) % p for x in subgroup)
            if new_coset & covered:
                return None  # degenerate overlap, shouldn't happen for valid g
            cosets.append(new_coset)
            covered |= new_coset
        g += 1
        if g >= p:
            return None
    if covered != set(range(1, p)):
        return None
    return cosets


def try_cyclotomic(p, r, clique_sizes):
    """Check whether the r cyclotomic cosets of Z_p^* give a valid
    (clique_sizes[0], ..., clique_sizes[r-1])-avoiding r-coloring of the
    circulant graph on Z_p. Returns (True, distance_sets) or (False, None)
    or (None, None) if p/r aren't eligible."""
    cosets = cyclotomic_cosets(p, r)
    if cosets is None:
        return None, None

    def to_distance_set(coset):
        return set(min(d, p - d) for d in coset)

    D = [to_distance_set(c) for c in cosets]
    ok = all(is_clique_free(D[i], p, clique_sizes[i]) for i in range(r))
    return ok, ([sorted(d) for d in D] if ok else None)


def search_cyclotomic_range(clique_sizes, p_min, p_max):
    """Exhaustively check every eligible prime p in [p_min, p_max] for a
    valid cyclotomic |clique_sizes|-coloring avoiding the given clique
    sizes. Returns (checked_primes, found_primes_with_witnesses)."""
    r = len(clique_sizes)
    checked = []
    found = []
    for p in range(p_min, p_max + 1):
        if not is_prime(p):
            continue
        ok, D = try_cyclotomic(p, r, clique_sizes)
        if ok is None:
            continue
        checked.append(p)
        if ok:
            found.append((p, D))
    return checked, found
