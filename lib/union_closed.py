"""
Tools for exploring Frankl's union-closed sets conjecture: for any
nonempty union-closed family F of finite sets (not just {empty set}),
some element belongs to at least half the sets in F. Best proven bound
as of 2024 is ~0.381966 (the "golden ratio bound", (3-sqrt(5))/2);
conjectured true bound is 0.5. A single family achieving max-element
frequency < 0.5 would disprove the conjecture outright.

Sets are represented as bitmasks (Python ints) over a ground set
{0,...,m-1}, so union = bitwise OR (fast) and closure computation is
just repeated OR-ing to a fixed point.
"""
import random


def union_closure(generators, m, size_cap=200000):
    """Given a list of generator bitmasks over an m-element ground set,
    compute the union-closure (repeatedly OR-ing pairs until no new
    sets appear). Returns None if the closure exceeds size_cap (to
    avoid blowing up memory/time on generator choices that are too
    "rich"). Always includes the empty set implicitly IF it's already
    reachable (e.g. if 0 is a generator) -- we do NOT auto-add it."""
    family = set(generators)
    frontier = list(family)
    while frontier:
        new_frontier = []
        flist = list(family)
        for a in frontier:
            for b in flist:
                u = a | b
                if u not in family:
                    family.add(u)
                    new_frontier.append(u)
                    if len(family) > size_cap:
                        return None
        frontier = new_frontier
    return family


def max_frequency_ratio(family, m):
    """Returns (ratio, best_element) -- ratio = (max count of any
    element across the family's sets) / |family|. Family must be
    nonempty and not equal to {0} (the all-empty-set family), else
    returns (None, None) (the conjecture is stated for genuine
    nonempty families with at least one nonempty set, conventionally)."""
    if not family or family == {0}:
        return None, None
    counts = [0] * m
    for s in family:
        for i in range(m):
            if s & (1 << i):
                counts[i] += 1
    best = max(counts)
    best_elem = counts.index(best)
    return best / len(family), best_elem


def random_generators(m, k, rng, density=0.3):
    gens = []
    for _ in range(k):
        mask = 0
        for i in range(m):
            if rng.random() < density:
                mask |= (1 << i)
        gens.append(mask)
    return gens


def local_search_min_ratio(m, k_generators, rng, iters=2000, size_cap=200000):
    """Hill-climb over the choice of k_generators generator masks (each
    a subset of the m-element ground set), minimizing the union-closure's
    max-element-frequency ratio. Move: replace one generator with a
    fresh random mask, or flip a random bit in one generator. Returns
    (best_ratio, best_generators, best_family_size)."""
    gens = random_generators(m, k_generators, rng)
    fam = union_closure(gens, m, size_cap)
    while fam is None:
        gens = random_generators(m, k_generators, rng, density=rng.uniform(0.1, 0.4))
        fam = union_closure(gens, m, size_cap)
    ratio, _ = max_frequency_ratio(fam, m)
    if ratio is None:
        ratio = 1.0

    best_ratio = ratio
    best_gens = list(gens)
    best_size = len(fam)

    cur_gens = list(gens)
    cur_ratio = ratio

    for _ in range(iters):
        new_gens = list(cur_gens)
        idx = rng.randrange(k_generators)
        move = rng.random()
        if move < 0.5:
            # flip a random bit
            bit = rng.randrange(m)
            new_gens[idx] = new_gens[idx] ^ (1 << bit)
        else:
            # replace with fresh random mask
            new_gens[idx] = random_generators(m, 1, rng, density=rng.uniform(0.1, 0.5))[0]

        new_fam = union_closure(new_gens, m, size_cap)
        if new_fam is None:
            continue
        new_ratio, _ = max_frequency_ratio(new_fam, m)
        if new_ratio is None:
            continue

        if new_ratio <= cur_ratio:
            cur_gens = new_gens
            cur_ratio = new_ratio
            if new_ratio < best_ratio:
                best_ratio = new_ratio
                best_gens = list(new_gens)
                best_size = len(new_fam)
        elif rng.random() < 0.05:  # small noise to escape local optima
            cur_gens = new_gens
            cur_ratio = new_ratio

    return best_ratio, best_gens, best_size


def verify_union_closed(family):
    """Independent from-scratch check: for every pair A,B in family,
    A|B must also be in family."""
    flist = list(family)
    for i in range(len(flist)):
        for j in range(len(flist)):
            if (flist[i] | flist[j]) not in family:
                return False
    return True
