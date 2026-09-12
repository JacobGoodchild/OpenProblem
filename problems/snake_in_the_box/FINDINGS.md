# Snake-in-the-Box

**Source:** classical combinatorics on the hypercube; current records
tracked in the OEIS (A099155 and related sequences) and recent literature,
notably a July 2026 paper "A Census of New Snake-in-the-Box Records"
reporting active, dedicated computational work on exactly this question.

**Status: genuinely open for n>=9**, and — unlike the other two problems in
this repo so far — **we did not improve on any published record.** This
write-up says so plainly and reports what we actually found, rather than
reframing a negative result as something bigger than it is.

## The problem, in plain English

Take the n-dimensional hypercube: `2^n` vertices (bit strings of length
`n`), edges between any two that differ in exactly one bit. A "snake" is
the longest possible path through this cube that never takes a "shortcut"
— formally, an *induced* path: no two non-consecutive vertices on the path
are allowed to be hypercube-adjacent (that would be a "chord", and defeats
the point of the exercise, which comes from an actual engineering
application: error-detecting coding schemes for rotating shaft encoders).

The maximum snake length is known exactly only for `n <= 8`
(`1,2,4,7,13,26,50,98`). For `n >= 9`, nobody has ever proven the maximum
— only the best *lower bound* snake anyone has found so far is published
(currently `a(9)>=191`, `a(10)>=379`, `a(11)>=746`). Finding an even longer
one for any of these `n` would be a genuine, real improvement to an open
record.

## What we did

1. **Randomized backtracking DFS with incremental bookkeeping.** Build the
   snake vertex-by-vertex; when stuck (no legal extension), backtrack.
   Naive backtracking recomputes which vertices are "blocked" (adjacent to
   an interior path vertex) from scratch after every backtrack step — this
   is the version we started with, and it was too slow to even reproduce
   `n=6` (target 26) within a reasonable time. We fixed this by
   maintaining blocked-status incrementally with an O(n) push/pop
   operation (a reference count per vertex) instead of an O(n · path
   length) full recompute — this is what made the search viable at all.
2. **Most-constrained-first ordering.** When there's a choice of which
   neighbor to extend to, we try the candidate with the *fewest* remaining
   future options first (a standard heuristic: using up tightly-constrained
   vertices early leaves more freedom later). This is what took us from
   barely reaching `n=4` correctly to getting within 1-4 of the exact
   optimum at `n=6,7`.
3. **An actual, embarrassing bug caught during development, worth
   recording honestly:** our first working version of the backtracking
   search only checked "is this the longest path found?" *after* the
   entire search for that restart had already finished and un-wound back
   to a short or empty path — so it reported length 0 for every `n` from
   1 to 4, even though valid length-1, length-2, etc. snakes were being
   built and briefly held during the search. The fix was to check for a
   new best length immediately after each successful extension, not only
   at the end. We flag this because it's exactly the kind of silent
   correctness bug that would have produced a false "we found nothing"
   result if we hadn't independently verified every reported snake from
   scratch (`verify_snake`, checking edges and the no-chord condition
   directly against the reported vertex list) rather than trusting the
   search's internal state.
4. **Independent, from-scratch verification of every result.** Every
   reported snake length is re-checked by an independent function that
   re-derives, from the raw vertex sequence alone, that consecutive
   vertices are hypercube-adjacent, all vertices are distinct, and no
   non-consecutive pair is adjacent. This caught nothing wrong in the end
   (all reported results were valid), but it's what makes the negative
   result below trustworthy rather than "we assume our code is right."

## Results

**Validation against known exact values** (small `n`, cheap to check
thoroughly):

| n | found | known exact | match? |
|---|-------|-------------|--------|
| 1 | 1 | 1 | exact |
| 2 | 2 | 2 | exact |
| 3 | 4 | 4 | exact |
| 4 | 7 | 7 | exact |
| 5 | 13 | 13 | exact |
| 6 | 25 | 26 | 1 short |
| 7 | 46 | 50 | 4 short |

**The actual attempt on open/harder cases**, 5-minute wall-clock budget
each, one process per `n`:

| n | found | published record | result |
|---|-------|-------------------|--------|
| 8 (control, known optimal=98) | 88 | 98 (exact, known) | 90% of optimal |
| 9 (open) | 155 | >=191 | **short of the record by 36** |
| 10 (open) | 290 | >=379 | **short of the record by 89** |

## Honest conclusion

**We did not improve on any published snake-in-the-box record, and did
not even match the known-exact value at n=8** in the time we gave it. The
gap widens as `n` grows (10% short at n=8, ~19% short at n=9, ~23% short
at n=10) — exactly the pattern you'd expect from a generic, from-scratch
heuristic competing against a research area with a dedicated, recent
(July 2026) publication specifically about finding new records for this
exact problem. Our method is real and correctly implemented (the
validation table above is honest evidence of that), but it is simply not
as good as the specialized techniques — better heuristics, longer
compute budgets, quite possibly parallel/distributed search or
problem-specific symmetry reduction — that produced the current records.

This is a different flavor of result than the other two problems in this
repo: Tuza's conjecture and R(3,10) each produced a complete, airtight
statement about a well-defined restricted search space (every circulant
graph checked, every structured family checked). Here, by contrast, we
simply ran a decent-but-not-best heuristic for a fixed wall-clock budget
and it came up short — which is a much weaker kind of result (it doesn't
rule anything out; a better implementation of the *same* general approach
might well find more) and we're not going to inflate it into more than
that.

**What would move this forward:** (a) more compute time — the search was
still finding new bests at the very end of the 5-minute budget for n=10,
so it had clearly not converged; (b) a proper simulated-annealing / genetic
algorithm layer on top of the backtracking (perturb a near-miss snake
rather than restarting from scratch each time — restarting throws away all
the structural progress made by a long unsuccessful attempt); (c)
symmetry reduction (fixing the starting vertex's automorphism class rather
than sampling uniformly, which wastes effort on equivalent starts); (d)
honestly, at this point, reading the actual construction method in the
July 2026 census paper rather than reinventing a weaker version of the
same idea from scratch.

## Reproducing

```
cd problems/snake_in_the_box
python3 search_open_n.py 9 --time-budget 300   # attempt an open record
```

`lib/snake_in_box.py` has the core search and the independent verifier.
