# Sequenceable Groups (Keedwell's Conjecture): Order 33+

**Status: abandoned mid-investigation** — pivoted to a different problem
(Bermond-Thomassen conjecture, k=4) per user direction before this could
be run to a real conclusion. Documenting honestly what was actually
found, not what might have been found with more time.

## What we did

Built and validated (against Q8's known non-sequenceability and a known
order-21 sequenceable case) a backtracking search for whether a
non-abelian group can have its elements ordered with all distinct
partial products. Targeted odd-order semidirect product groups
`Z_q ⋊ Z_p` (odd primes `p<q`, `p | q-1`) — genuinely outside every
family Keedwell's conjecture is currently proven for (not dihedral, no
element of order 2, not A5/S5), at orders beyond the proven 10-32 range.

**Mid-course correction worth recording:** the first attempt used a
fixed deterministic element order and came back "inconclusive" on all
8 candidates, even 30M+ nodes into the smallest one (order 39).
Rewriting to try randomized restarts first resolved order 39 in ~11,000
nodes — the fixed order was simply unlucky, not evidence of anything.

## Results (partial — search was stopped mid-run)

| order | result |
|---|---|
| 39, 55, 57, 93 | sequenceable (each independently verified) |
| 111, 129, 155 | inconclusive — neither randomized restarts (20 trials, 2M nodes each) nor one exhaustive 30M-node deterministic run resolved it |
| 183+ | not reached — search killed before completing |

## Honest conclusion

**No counterexample, no progress, and no real conclusion either way** —
this was stopped before the search strategy was pushed far enough to
say anything meaningful about orders 111+. The "inconclusive" results
are a genuine open question about whether more compute or a smarter
search (better randomization, symmetry-breaking on the group's known
automorphisms, or a SAT encoding instead of raw backtracking) would
resolve them, not evidence of anything about Keedwell's conjecture
itself.

## Reproducing

```
cd problems/sequenceable_groups
python3 validate_known.py
python3 search.py --min-order 33 --max-order 200 --randomized-trials 20 --trial-node-budget 2000000
```
