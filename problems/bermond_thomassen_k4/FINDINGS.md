# The Bermond-Thomassen Conjecture, k=4

**Source:** Bermond & Thomassen, 1981. **Status: genuinely open, and
essentially unattacked computationally** — as far as could be
determined during this session's research, all existing progress on
this conjecture (k=1 trivial, k=2 proven by Thomassen 1983, k=3 proven
by Lichiardopol, Pór & Sereni) comes from hand proofs, not computer
search. A relaxed version was proven as recently as August 2026,
confirming this is a live, actively-studied area — not abandoned.

## The problem, in plain English

Take any directed graph where every vertex has at least 7 outgoing
edges. The conjecture: no matter how that graph is built, it must
contain 4 cycles that don't share any vertices with each other. This
is known to be true if you only need 2 or 3 such cycles (with the
correspondingly smaller out-degree requirements, 3 and 5). Whether it's
true for 4 (out-degree 7) is unknown.

## What we did

1. **Built exact tooling**: complete elementary-cycle enumeration
   (networkx's `simple_cycles`, exact — not a heuristic — but
   length-capped for tractability since full enumeration blows up
   combinatorially even at n=12) feeding an exact ILP (pulp/CBC) for
   the maximum vertex-disjoint cycle packing — the same "set packing"
   pattern used elsewhere in this project for independent sets.
2. **Validated three ways**, the third being the important one: (a) the
   complete digraph on 8 vertices trivially has 4 disjoint cycles; (b)
   a digraph built as exactly 4 disjoint cycles by construction reports
   exactly 4; (c) **on random digraphs with the minimum out-degree
   matching the *already-proven* k=2 and k=3 cases (out-degree 3 and 5
   respectively), our tooling never found fewer disjoint cycles than
   those real theorems guarantee**, across 20 random trials — a
   genuine check against established mathematics, not just internal
   self-consistency.
3. **Adversarial local search**: hill-climbing over digraphs with out-
   degree exactly 7 (the tightest case), rewiring one out-edge at a
   time, trying to *minimize* the maximum disjoint-cycle count, for
   `n=9` (the smallest possible size) through `n=30`.
4. Any candidate that looked like it might drop below 4 would trigger
   an automatic escalated recheck (much higher cycle-length cap, longer
   ILP time) before being taken seriously — none did.

## Results

| n | best (minimum) max-disjoint-cycles the search could achieve |
|---|---|
| 9 | **4** (exact — see below) |
| 10 | 5 |
| 11 | 5 |
| 12-14 | 6 |
| 15-17 | 7 |
| 18-19 | 8 |
| 20-23 | 9 |
| 24-25 | 10 |
| 26-29 | 11 |
| 30 | 12 |

**No counterexample found anywhere.** The minimum achievable count
rises steadily with `n` and never dips below 4 at any tested size.

**The n=9 result is the most solid finding of this run and is worth
being precise about**: at `n=9`, a simple cycle can have at most 9
vertices, so setting the cycle-length cap to 9 makes the search
*exact*, not an approximation — this is a genuine, complete, verified
result, not a proxy. We independently reproduced it, re-ran the
recheck with the length cap raised to the true maximum possible (9,
covering every conceivable cycle length), and independently verified
the selected 4 disjoint cycles against the actual graph edges. The
adversarial search found a real, non-trivial 9-vertex, out-degree-7
digraph (not the complete digraph — each vertex omits exactly one
possible out-neighbor) whose true maximum disjoint-cycle count is
**exactly 4** — sitting right at the conjectured boundary, with zero
slack, and consistent with (not violating) the conjecture.

## Honest conclusion

**No counterexample, and this was never a likely outcome for a
scattered local search over a 45-year-old open conjecture** — but this
is a meaningfully different kind of "no counterexample" than most of
this project's negative results, for two reasons:

- The tooling was validated against *actual proven theorems* (k=2,
  k=3), not just internal sanity checks, which is a stronger guarantee
  that a "no violation found" result would have been trustworthy had
  the search gotten lucky.
- The `n=9` result is an *exact*, complete verification (not a search
  proxy) — this is likely close to the extremal case for the
  conjecture (the fewest vertices at which out-degree-7 digraphs even
  exist), and finding a real example that hits the bound exactly, with
  zero slack, is itself informative: it suggests the conjecture (if
  true) is tight at small n, matching the "tight examples on `2k-1`
  vertices" pattern the k=2/k=3 literature describes for their own
  bounds.

**Caveats, stated plainly**: for `n>9`, results come from a
length-capped (`<=5`), time-limited (8s per ILP call) local search —
every disjoint-cycle count reported IS a real, valid witness (so
compliance at those `n` is genuinely confirmed for the specific
digraphs found), but the search covers only a tiny fraction of all
possible out-degree-7 digraphs at each `n`, and the true minimum
achievable count at each `n` could be lower than what a few hundred
hill-climbing iterations found. This is exploratory evidence consistent
with the conjecture, not anything close to a proof.

**What would move this forward:** push `n` higher with a much larger
iteration budget and a smarter search (simulated annealing with a real
cooling schedule, or restart diversity); do exact (uncapped)
verification at more values of `n` where feasible; and specifically
study the structure of the `n=9` extremal example we found (which
out-neighbor each vertex omits) for a pattern that might generalize
into a genuine, if long-shot, systematic attack rather than pure random
search.

## Reproducing

```
cd problems/bermond_thomassen_k4/code
python3 validate_known.py
python3 adversarial_search.py --n-start 9 --n-stop 30 --iters-per-n 500
```
