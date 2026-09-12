# The Multicolor Ramsey Number R(3,3,5)

**Source:** classical multicolor Ramsey theory. **Status: genuinely
open**, per multiple 2025-2026 sources: `R(3,3,5) <= 57` (published upper
bound), and among 3-color classical Ramsey numbers only `R(3,3,3)` and
`R(3,3,4)=30` are known exactly. **We could not confirm the current
published lower bound for R(3,3,5) from available sources** despite
several searches — this is an honest limitation of the research phase for
this problem, and we say so rather than guess or imply a comparison we
can't actually support.

## The problem, in plain English

`R(3,3,5)` is the smallest `N` such that every 3-coloring of the edges of
`K_N` contains a monochromatic triangle in color 1 or 2, or a
monochromatic `K5` in color 3. To push the lower bound up, exhibit a
3-coloring of `K_n` where color 1 and color 2 are each triangle-free and
color 3 is `K5`-free.

## What we did

1. **Generalized the circulant-graph technique to `r` colors**
   (`lib/multicolor_circulant.py`): partition the difference set
   `{1,...,n/2}` into `r` parts, one per color. Since a full `r`-way
   partition is a much bigger space than the 2-color case (`r^(n/2)`
   instead of `2^(n/2)`), exhaustive search stops being feasible much
   sooner — but each *candidate* coloring is still checked with fast
   arithmetic (`is_clique_free`, the same backtracking check validated
   earlier for R(4,6)/R(4,7)), not an expensive ILP or SAT call. This
   matters: it's the same lesson learned from the `W(2,7)`/`S(6)`
   failures earlier in this project — local search only works well here
   *because* the per-candidate check is cheap, unlike those two attempts.
2. **Validated by reproducing `R(3,3,4)=30`**: found a valid
   `(K3,K3,K4)`-avoiding circulant 3-coloring at `n=29` (the correct
   witness size) within a handful of random restarts.
3. **Swept `n=35` through `46`** with a local search (greedy recoloring
   + noise + periodic restarts), 25 seconds per `n`, looking for the
   largest achievable `(K3,K3,K5)`-avoiding circulant witness.

## Results

| n | result |
|---|--------|
| 35-39 | found valid witnesses (fast, under 13s each) |
| 40 | not found in 25s |
| **41** | **found** — color sizes `[5,6,9]`, independently re-verified valid |
| 42-46 | not found in 25s each (5 consecutive misses) |

The clean run of 5 consecutive misses right after the `n=41` success is a
reasonably strong (though not conclusive) signal that **41 is close to
this search method's practical ceiling** — not proof that no larger
circulant witness exists, just that this particular local search, with
this time budget, consistently fails to find one past that point.

**The witness at n=41** (`{3,5,7,15,16}`, `{8,11,14,17,18,20}`,
`{1,2,4,6,9,10,12,13,19}` as the three difference-set partitions) gives
`R(3,3,5) >= 42`, independently re-derived and re-verified from scratch.

## Honest conclusion

**We cannot say whether this improves on, matches, or falls short of the
actual current record** for R(3,3,5), because we were unable to find a
citable, specific published lower-bound figure for this exact value
during this session's research — a real gap in our own process, not a
claim of novelty we're not entitled to make. What we *can* say
confidently: `R(3,3,5) >= 42` is independently, computationally verified
by us, via a from-scratch implementation, cross-validated against the
known `R(3,3,4)=30` case first.

This result sits between the complete, airtight negative results
(R(3,10), R(4,6)) and the honestly-limited ones (R(4,7)'s 3.5% partial
coverage, W(2,7)/S(6)'s complete non-starts) in this project: it's a
**positive construction** (we found something, not just failed to find
something), independently verified, but with an important caveat about
not knowing how it compares to the literature.

**What would move this forward:** (a) actually locate Radziszowski's
current multicolor Ramsey survey (blocked from direct access during this
session) to get the real current lower bound and know whether 42 is new
information or already superseded; (b) push the search further past
n=46 with a longer time budget or a better local search (e.g. simulated
annealing with a proper temperature schedule instead of pure greedy +
noise, which is a fairly basic heuristic); (c) try non-circulant
3-colorings, or circulant colorings on other symmetry groups, the same
general lesson as the two-color Ramsey write-ups in this repo.

## Reproducing

```
cd problems/ramsey_3_3_5
python3 search.py --start 30 --stop 45 --time-per-n 20
```
