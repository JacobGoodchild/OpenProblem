# The Ramsey Number R(4,7)

**Source:** classical Ramsey theory. **Status: genuinely open.**
`49 <= R(4,7) <= 61`. The published lower bound comes from a `(4,7)`-
coloring of `K48` — i.e. a `K4`-free graph on 48 vertices with
independence number `<=6`. Finding such a graph on 48 vertices ourselves,
or a valid one on 49, would be relevant to this bound (finding one on 48
would just reproduce the known result; on 49 would improve it).

**This is explicitly a PARTIAL result, unlike the complete searches for
R(3,10) and R(4,6) in this repo.** We say so clearly and don't dress it
up as more than it is.

## The problem, in plain English

Same setup as `R(4,6)` in this repo, one number further out: `R(4,7)` is
the smallest `N` such that every graph on `N` vertices contains a 4-clique
or a 7-vertex independent set.

## What we did, and where the scale forced a compromise

1. **Same circulant-graph, `K4`-free technique** as R(4,6), applied at
   `n=48` (connection sets are subsets of `{1,...,24}`: `2^24 = 16,777,215`
   total — 64x the search space of the R(4,6) attempt at n=36).
2. **Phase 1 (fast arithmetic `K4`-free filter) completed in full:** all
   16,777,215 connection sets checked in 130 seconds, yielding **334,411**
   `K4`-free candidates — again, ~19x more survivors than the n=36 case,
   because looser structural constraints at a larger n admit far more
   valid sparse graphs.
3. **Phase 2 (exact ILP independence-number check) could not run to
   completion.** Extrapolating from the R(4,6) verification rate
   (17,858 candidates in 972 seconds), checking all 334,411 candidates
   here would take on the order of **5 hours** — not something we chose
   to commit an entire session to for one candidate value, especially
   given the discovered instances got *harder* per-candidate here too
   (each ILP check took noticeably longer on average than at n=36,
   consistent with larger graphs).
4. **Fell back to a prioritized, time-boxed partial search:** sorted all
   334,411 candidates by descending density (popcount) — denser circulant
   graphs are more likely to have small independence number, so this
   concentrates effort on the candidates most likely to actually matter —
   and ran the ILP verification with a fixed 15-minute wall-clock budget,
   stopping wherever it got to.

## Results

- **11,743 of 334,411 candidates verified (3.5% coverage)**, the
  *densest* 3.5% specifically (highest popcount first), in 900 seconds.
- **Zero witnesses found in this subset.** No K4-free graph on 48
  vertices with independence number `<=6` among the candidates checked.
- **Zero solver timeouts/inconclusive results** — every individual check
  that was performed gave a definite answer; the limitation here is
  coverage, not per-instance ambiguity.
- **How close did the checked candidates get?** A follow-up sample of 150
  from the already-verified top-11,743 region found a minimum exact
  independence number of **9** (mean 15.3) — notably *not* as close a
  near-miss as the R(3,10) (best=10 vs target 9) or R(4,6) (best=6 vs
  target 5) results. This might mean the interesting structure (if any
  circulant witness exists at all) lies outside the very-densest region
  we prioritized, or it might mean circulant graphs are simply a worse
  fit for this particular `(4,7)` pair than they were for `(3,10)` and
  `(4,6)` — we can't distinguish those possibilities from this data
  alone.

## Honest conclusion

**This is a genuinely weaker result than R(3,10) or R(4,6) in this repo,
and we're not going to claim otherwise.** We checked 3.5% of one
restricted construction family (circulant graphs) at one specific size,
prioritized by a reasonable but unproven heuristic (density), and found
nothing — which tells us very little with confidence, unlike the
*complete* R(3,10)/R(4,6) searches where "nothing found" meant "provably
nothing in this entire family." Here, 96.5% of even just the circulant
family at n=48 remains unchecked.

**What would be needed to make this a real result:** (a) far more compute
time — even finishing the full circulant enumeration at n=48 seriously
would need hours, and that's still only the *cyclic*-symmetry slice of
all graphs on 48 vertices; (b) a faster per-candidate independence-number
check — the ILP approach that worked fine at n=36 is showing real
scaling strain at n=48, so a bespoke faster exact method (e.g. exploiting
circulant structure directly in the independence-number computation,
rather than treating each graph as generic input to a black-box ILP)
would be needed before this approach is worth pushing further; (c) given
the disappointing "how close" result compared to R(3,10)/R(4,6), it may
be more productive to abandon the density-first heuristic and try
covering a broader, more diverse subset of the 334,411 candidates instead
of just the top slice.

## Reproducing

```
cd problems/ramsey_4_7
python3 search_n48.py                          # phase 1: full enumeration (fast, ~2 min)
python3 verify_candidates_partial.py 900       # phase 2: partial, time-boxed (pass a larger budget for more coverage)
```
