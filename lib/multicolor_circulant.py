"""
Multicolor circulant Ramsey constructions: generalizes lib/circulant_ramsey.py
(built for the 2-color case, R(3,10) and R(4,6)/R(4,7)) to r colors.

A witness for R(s_1, s_2, ..., s_r) > n is an edge-coloring of K_n with r
colors such that color i contains no clique of size s_i. Restricting to
CIRCULANT colorings: partition the "full difference set" {1,...,floor(n/2)}
into r disjoint parts S_1,...,S_r (color i connects vertices whose
difference's absolute residue is in S_i); this is vertex-transitive in
each color and is the standard, long-established technique for finding
multicolor Ramsey lower-bound witnesses (same idea as the 2-color case,
just partitioned further).

Since a full 3-way (or higher) partition of the difference set is a much
larger search space (r^half instead of 2^half) than the 2-color case,
exhaustive enumeration is only feasible for small half; for larger cases
we use local/random search over colorings -- BUT, unlike the van der
Waerden / Schur attempts elsewhere in this project (which failed to
scale), each candidate coloring here is checked with FAST ARITHMETIC
(clique-free checks directly on the difference sets, not an expensive
ILP or SAT call), so many random restarts / hill-climbing moves can be
tried per second. This is closer in spirit to the R(3,10)/R(4,6)
adversarial-search pattern that worked well, not the local-search pattern
that didn't.
"""
import random
from lib.circulant_ramsey import difference_set, is_clique_free


def is_valid_coloring(color_sets, n, clique_sizes):
    """color_sets: list of r sets, partitioning {1,...,n//2}. clique_sizes:
    list of r forbidden clique sizes (color i must have no K_{clique_sizes[i]}).
    Returns True iff every color is clique-free at its target size."""
    for S, s in zip(color_sets, clique_sizes):
        if not is_clique_free(S, n, s):
            return False
    return True


def random_coloring(n, r, rng):
    half = n // 2
    color_sets = [set() for _ in range(r)]
    for d in range(1, half + 1):
        color_sets[rng.randrange(r)].add(d)
    return color_sets


def local_search_multicolor(n, clique_sizes, rng, max_flips=100000, restart_after_stuck=5000):
    """Hill-climb over colorings of {1,...,n//2} into len(clique_sizes)
    colors, minimizing total "excess clique" violations (counted as: for
    each color, 1 point per clique found via a quick greedy scan -- exact
    zero means a valid witness). Uses is_clique_free as a hard check (fast
    arithmetic) rather than a soft violation count, since re-deriving a
    smooth violation-count objective for arbitrary clique sizes is complex;
    instead we do randomized local moves (move one element to a different
    color) and only keep moves, tracked via full is_valid_coloring
    re-checks -- fast because is_clique_free itself is fast for the
    modest set sizes involved (each color usually has O(n) elements at
    most, and the backtracking clique search is only over the "D" set
    which has size O(popcount), not O(n))."""
    r = len(clique_sizes)
    half = n // 2
    color_sets = random_coloring(n, r, rng)

    def count_violations(sets):
        return sum(0 if is_clique_free(S, n, s) else 1 for S, s in zip(sets, clique_sizes))

    cur_viol = count_violations(color_sets)
    best_viol = cur_viol
    best_coloring = [set(s) for s in color_sets]

    stuck = 0
    for _ in range(max_flips):
        if cur_viol == 0:
            break
        d = rng.randrange(1, half + 1)
        old_color = next(i for i, S in enumerate(color_sets) if d in S)
        new_color = rng.randrange(r)
        if new_color == old_color:
            continue
        color_sets[old_color].discard(d)
        color_sets[new_color].add(d)
        new_viol = count_violations(color_sets)
        if new_viol <= cur_viol:
            cur_viol = new_viol
            if new_viol < best_viol:
                best_viol = new_viol
                best_coloring = [set(s) for s in color_sets]
            stuck = 0
        else:
            # revert
            color_sets[new_color].discard(d)
            color_sets[old_color].add(d)
            stuck += 1

        if stuck >= restart_after_stuck:
            stuck = 0
            color_sets = random_coloring(n, r, rng)
            cur_viol = count_violations(color_sets)

    return best_coloring, best_viol
