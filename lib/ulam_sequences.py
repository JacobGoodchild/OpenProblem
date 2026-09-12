"""
Generalized Ulam ("1-additive") sequences: starting from a(1)=a < a(2)=b,
each subsequent term is the SMALLEST integer greater than the current
max that can be written as a sum of two DISTINCT earlier terms in
EXACTLY ONE way. The classical Ulam sequence is (a,b)=(1,2).

Finch (1992, "Patterns in 1-Additive Sequences") computed these for many
small (a,b) and classified each as "eventually periodic" (the sequence
of gaps between consecutive terms settles into a strict repeating
cycle) or not, based on the number of terms computers of that era could
reach (typically thousands). This is genuinely open territory to push
further: modern hardware can compute vastly more terms per sequence,
which can (a) confirm a claimed period holds much further than
originally checked, (b) catch a period that was reported based on too
short a run and actually breaks later, or (c) find periodicity in
sequences previously reported as having none.

Efficient generation: naive "check all pairs" per new term is O(n) per
term (O(n^2) total) -- for the term counts we want (10^5-10^6), this is
still the dominant cost, but done with numpy vectorized array updates
(not nested Python loops) it's fast enough in practice.
"""
import numpy as np


def generate_ulam(a, b, n_terms, max_bound=None):
    """Generate the first n_terms of the (a,b) 1-additive sequence.
    max_bound: search ceiling for term values (auto-sized if None,
    based on the empirical ~0.3-0.5 density of these sequences).
    Returns a numpy int64 array of terms (may be shorter than n_terms
    if max_bound is reached first -- caller should check)."""
    if max_bound is None:
        max_bound = int(n_terms * 8) + 1000  # generous safety margin

    count = np.zeros(max_bound + 1, dtype=np.int16)
    terms = np.empty(n_terms, dtype=np.int64)
    terms[0] = a
    terms[1] = b
    count_len = 2

    # initialize: the sum a+b has one representation
    if a + b <= max_bound:
        count[a + b] += 1

    cur = b
    for idx in range(2, n_terms):
        # find smallest value > cur with count == 1
        search_start = cur + 1
        window = count[search_start:max_bound + 1]
        hits = np.nonzero(window == 1)[0]
        if hits.size == 0:
            return terms[:idx]  # ran out of room in max_bound
        next_val = search_start + hits[0]

        terms[idx] = next_val
        cur = next_val
        count_len += 1

        # update counts: next_val + each existing term (vectorized)
        existing = terms[:idx]  # all terms before this one (idx of them)
        sums = existing + next_val
        valid = sums <= max_bound
        sums = sums[valid]
        np.add.at(count, sums, 1)

    return terms


def gaps(terms):
    return np.diff(terms)


def find_period(gap_seq, min_period=1, max_period=200, min_repeats=5, tail_frac=0.3):
    """Look for a repeating cycle in the TAIL of the gap sequence (the
    last tail_frac of it), trying period lengths from min_period to
    max_period. Returns (period, num_repeats_confirmed) for the first
    (smallest) period that repeats at least min_repeats times
    consecutively in the tail, or None if none found."""
    n = len(gap_seq)
    tail_start = int(n * (1 - tail_frac))
    tail = gap_seq[tail_start:]
    for p in range(min_period, max_period + 1):
        if len(tail) < p * min_repeats:
            continue
        # check the last p*min_repeats elements for period p
        chunk = tail[-(p * min_repeats):]
        block0 = chunk[:p]
        ok = True
        for r in range(1, min_repeats):
            if not np.array_equal(chunk[r * p:(r + 1) * p], block0):
                ok = False
                break
        if ok:
            # extend backward to see how far the period actually holds
            repeats = min_repeats
            while True:
                start = len(tail) - (repeats + 1) * p
                if start < 0:
                    break
                if np.array_equal(tail[start:start + p], block0):
                    repeats += 1
                else:
                    break
            return p, repeats
    return None
