# The Union-Closed Sets Conjecture (Frankl, 1979)

**Source:** classical set theory / combinatorics. **Status: genuinely
open**, but not obscure — it made real news in 2022 when Gilmer proved
a first constant-fraction bound (breaking decades of only-`o(1)`
progress), and a 2024 paper (Alweiss, Huang, Sellke) pushed the proven
bound to **~0.381966** (the "golden ratio bound", `(3-sqrt(5))/2`). The
conjectured true bound is **0.5**. Exhaustively verified true for all
ground-set sizes `m <= 12` (Vučković & Živković).

**Why this problem instead of another famous Ramsey number:** after a
long run of Ramsey-number attempts in this project mostly falling short
of already-famous, heavily-fought-over records, this is a deliberate
pivot to a problem that is real and actively studied but where a
computational search has a more sensible role to play — the current
frontier is a specific numeric gap (0.382 vs 0.5), not a "everyone's
already tried this exact construction for 60 years" wall.

## The problem, in plain English

Take a collection of sets `F` where, whenever two sets `A` and `B` are
in the collection, their union `A ∪ B` is also in the collection (this
is "union-closed"). The conjecture: as long as `F` isn't trivial (not
just the empty set on its own), some element must show up in **at
least half** of the sets in `F`. Nobody has found a counterexample in
over 45 years, and nobody has proven it either.

## What we did

1. **Built fast union-closure computation** (`lib/union_closed.py`):
   sets as bitmasks, closure via repeated bitwise-OR to a fixed point,
   starting from a small chosen set of "generator" sets (guarantees a
   valid union-closed family every time, no repair needed).
2. **Validated**: reproduced the classical *exact* `0.5` tight example
   (the full power set of an `m`-element ground set — every element is
   in exactly half of all `2^m` subsets), and ran the local search on
   `m=8` through `12` (where the conjecture is **proven true** by
   exhaustive computer verification) to confirm it never reports a
   ratio below 0.5 there — a live check against our own search code
   fabricating a false "counterexample."
3. **Attacked `m=13` through `24`** (past the exhaustively-verified
   boundary) with adversarial local search over generator sets, hill-
   climbing to *minimize* the max-element-frequency ratio — actively
   hunting for a counterexample, or at least a family closer to the
   `0.5` boundary than trivial examples.

## Results

| m | best ratio found | trials |
|---|---|---|
| 13-20 | exactly 0.5000 | 246-1679 |
| 21 | 0.5079 | 108 |
| 22 | 0.5000 | 99 |
| 23 | 0.5556 | 94 |
| 24 | 0.6462 | 41 |

**No ratio below 0.5 was found anywhere.** The `m=13` result (ratio
exactly 0.5) was independently re-verified from scratch — but it's a
tiny, structurally trivial 4-set family, not a sophisticated
construction; the search converges to easy local optima rather than
exploring deeply.

## Honest conclusion

**No counterexample, and no meaningful progress on the actual gap
(0.382 vs 0.5).** This was never a likely outcome — finding a
counterexample would instantly resolve a famous 45-year-old conjecture,
so its absence here isn't informative on its own. Two things are worth
being explicit about:

- The **rising ratios at `m=21`-`24`** (0.508, 0.556, 0.646) are **not**
  evidence that larger `m` gets harder to violate — they're a search-
  budget artifact. Larger `m` makes each union-closure computation more
  expensive, so the fixed 20-second-per-`m` budget buys far fewer local-
  search trials (1679 trials at `m=13` vs. 41 at `m=24`), and the search
  simply doesn't have time to find as good a family. This should not be
  read as a trend.
- The search itself is fairly basic (generator-based hill-climbing with
  a handful of move types), and it's not clear it's actually exploring
  the *interesting* part of the space — the theoretical near-tight
  examples in the literature (getting close to but not below 0.5) tend
  to have specific lattice/matroid structure that a generic search has
  no bias toward finding, the same lesson learned repeatedly with the
  Ramsey cyclotomic constructions earlier in this project.

**What would move this forward:** seed the search with known near-tight
theoretical constructions from the literature (rather than random
generators) and perturb from there; give larger `m` a proportionally
larger time budget so the comparison across `m` is fair; or target a
narrower, more tractable sub-question (e.g., verify the conjecture
holds for a specific structured family class, like families generated
by a fixed small number of "large" sets, which is more exhaustively
checkable than the fully general case).

## Reproducing

```
cd problems/union_closed_sets
python3 validate_known.py
python3 search.py --m-start 13 --m-stop 24 --time-per-m 20
```
