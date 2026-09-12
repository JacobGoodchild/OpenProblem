# The Schur Number S(6)

**Source:** classical Ramsey-type additive combinatorics (Issai Schur,
1916). **Status: genuinely open.** `S(6) >= 536` is the published lower
bound (only known via computer search); the exact value is unknown. Only
`S(1)` through `S(5)` are known exactly (`1, 4, 13, 44, 160` — the last
established by a massive, famous 2017 SAT proof, "Schur Number Five").

**We made no progress on the actual open question, same as the earlier
`W(2,7)` attempt in this repo, and for essentially the same reason.**

## The problem, in plain English

Partition `{1,...,N}` into `k` groups (colors) so that no group contains
`a, b, c` (repeats allowed) with `a+b=c`. `S(k)` is the largest `N` for
which this is possible with `k` groups. `S(6)` asks: what's the largest
`N` for which 6 such sum-free groups exist? Known to be at least 536;
unknown beyond that.

## What we did

1. **Exact SAT encoding**, one-hot color variables per integer, clauses
   forbidding any monochromatic `a+b=c` triple. **Validated exactly**
   against `S(1)=1`, `S(2)=4`, `S(3)=13`, `S(4)=44` — SAT one below each
   threshold, UNSAT at it, every time.
2. **Local search (WalkSAT-style multi-color)** for the larger cases where
   a complete solver isn't practical: minimize monochromatic-triple
   violations via greedy recoloring with noise. Tested against the
   *already known* `S(5)=160` boundary (not yet the open target — just
   the next case up from what we could validate exactly) as a scaling
   check before attempting `S(6)`.
3. **The scaling check failed.** After 500,000 flip attempts (~75 seconds),
   the local search still had 100 unresolved violations at `N=160, k=5` —
   a case that is **already known to have a valid solution**. It did not
   converge even there.

## Honest conclusion

**We did not attempt `S(6)` at all**, because there was no reason to
expect success: the same local search technique failed to converge on a
*smaller, easier, already-solved* case (`k=5, N=160`) well before we ever
got to the actual open target (`k=6, N=536`, both a larger `N` and one
more color).

This is the same outcome, for the same underlying reason, as the
`problems/vdw_2_7/` write-up earlier in this project: a from-scratch
Python WalkSAT-style local search, without careful low-level engineering
(incremental data structures tuned for speed, adaptive noise schedules,
restart strategies validated on the actual target scale), does not
reliably scale to instances of this size. Two independent attempts at
"multi-color / multi-position combinatorial coloring with local sum/AP
constraints" (van der Waerden colorings, Schur colorings) have now hit
essentially the same wall.

**The actionable lesson for this project going forward:** local-search
implementations built from scratch in Python are not (at least as
implemented here) a reliable tool for problems at this scale. The
approaches that *have* worked reliably in this project are the ones built
on professional, compiled solvers doing the heavy lifting exactly
(`pulp`+CBC for the Tuza's conjecture and Ramsey-number ILP checks;
`pysat`+Glucose for small, tractable SAT instances) rather than a
hand-rolled heuristic search loop. Future problems in this rotation
should prefer that pattern — exact search over a restricted, tractable
space (like the circulant-graph technique used for R(3,10)/R(4,6)/R(4,7))
— over reimplementing a general-purpose local search solver, which is a
much harder engineering problem than it looks and one this project has
now failed at twice.

## Reproducing

```
cd problems/schur_6
python3 -c "
import sys; sys.path.insert(0, '../..')
from lib.schur import check_schur_sat
print(check_schur_sat(44, 4))   # SAT (validated against S(4)=44)
print(check_schur_sat(45, 4))   # UNSAT
"
```
