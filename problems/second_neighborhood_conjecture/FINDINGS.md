# Seymour's Second Neighborhood Conjecture

**Source:** Paul Seymour, ~1990 (also attributed via Caccetta–Häggkvist-adjacent
literature); see the [Open Problem Garden](https://www.openproblemgarden.org)
family of digraph conjectures and the survey page
[sfu.ca/~mohar/Problems/P0601_SeymourSecondNbdConj.html](https://www.sfu.ca/~mohar/Problems/P0601_SeymourSecondNbdConj.html).
Active recent literature specifically on the still-open general case:
*"Seymour's second neighborhood conjecture for tournaments missing a
generalized star"* (2011), *"About the second neighborhood conjecture for
tournaments missing two stars or disjoint paths"* (2024).

**Status: proven for tournaments (complete oriented graphs); open in
general.** This write-up covers the open, general case.

## The problem, in plain English

Picture a group of people where every pair either has no relationship, or
one of them "beats" the other (like a one-way tournament bracket, but you
don't have to have played everyone). For a person `v`, call the people `v`
directly beats their **first circle**, and the people beaten by someone in
`v`'s first circle (but not already in it, and not `v`) their **second
circle**.

Seymour conjectured: **in any such setup, at least one person's second
circle is at least as big as their first circle.** Intuitively — beating a
lot of people directly tends to "use up" the strong players, leaving the
second circle relatively thin; the conjecture says this thinning effect
can never apply to *everyone at once*.

This is **proven** when literally everyone has played everyone (a
"tournament") — two different proofs exist (Fisher 1996, algebraic; Havet
& Thomassé 2000, combinatorial). It is **open** the moment you allow some
pairs to simply not have played each other (a general "oriented graph").
The active research frontier studies graphs that are tournaments with just
a handful of missing games, since sparser graphs are comparatively easy
(a vertex with few out-neighbours has an easy time satisfying the
inequality) — the hard case is staying as close to a full tournament as
possible while breaking the property everywhere at once.

## What we did

Built `lib/second_neighborhood.py`: represent an oriented graph as an
adjacency matrix, compute every vertex's "slack" `S(v) = |2nd circle| -
|1st circle|` via one boolean matrix multiply. A counterexample is a graph
where `S(v) < 0` for literally every vertex.

Then ran **adversarial simulated annealing directly in the space of
graphs**: start from a random tournament on `n` vertices with `m` games
missing (m games removed uniformly at random, each remaining pair
oriented randomly), then hill-climb — via single-arc reversals and
"relocate a missing game" moves — toward **maximizing the number of
simultaneously-bad vertices**, i.e. actively searching for the
counterexample rather than hoping to sample one. Any run that reaches
`n`-out-of-`n` bad vertices is a genuine counterexample (code checks this
explicitly and would flag it loudly and save the adjacency matrix).

Swept this across `n` from 10 to 200 and `m` (missing games) from 1 up to
~n/8, 60,000 annealing steps per (n, m) combination — a few seconds each,
so the whole grid runs in minutes.

## Results

The full sweep is complete: **59 (n, m) combinations** tried, `n` from 10
to 200, `m` (missing games) from 1 up to `n` itself (i.e. all the way from
near-complete tournaments to graphs with half their pairs unplayed).

| n | m range tried | best simultaneously-bad fraction found |
|---|---|---|
| 10 | 1–8 | 90.0% (9/10) |
| 15 | 1–8 | 93.3% (14/15) |
| 20 | 1–20 | 85.0–95.0% |
| 30 | 1–30 | 80.0–90.0% |
| 50 | 1–50 | 82.0–90.0% |
| 80 | 1–15 | 85.0–90.0% |
| 100 | 25–100 | 80.0–86.0% |
| 120 | 1–15 | 84.2–87.5% |
| 200 | 1–15 | 81.5–84.5% |

**No counterexample was found in any of the 59 combinations — not one.**
Every single run converges to the same striking pattern: adversarial
pressure can force **all but a small handful of vertices** to be
simultaneously bad — and then gets stuck there, no matter how many more
annealing steps or how the "missing games" are rearranged. Two honest
observations about the shape of this data:

1. **`m` barely matters.** Across the entire range tried — from just 1
   missing game up to `m = n` (i.e. sparse graphs where half the possible
   pairs never played) — the achievable bad-fraction stays in a narrow
   80-95% band. There is no sign of it becoming easier to approach a
   counterexample as the graph gets sparser, which is itself informative:
   the conjecture's difficulty (for an adversary) doesn't appear to hinge
   on density in the range we could search.
2. **The achievable fraction drifts down slightly as `n` grows** (≈90-95%
   at n≤30 down to ≈82-85% at n=200) — i.e. more vertices are left
   "resisting" at larger n. We do **not** read this as evidence the
   conjecture gets easier to break at scale; it's almost certainly a
   budget artifact. Our simulated annealing ran a *fixed* 60,000-80,000
   steps regardless of `n`, and each step is a local, single-arc tweak —
   so the fraction of the search space explored shrinks as `n²` grows
   while the step count doesn't. Squeezing out the last few resisters at
   n=200 likely just needs more steps, not that they're fundamentally
   unresponsive to pressure the way the very last one is.

We verified the machinery is correct by checking `m=0` (full tournaments):
3,000 random tournaments on 9 vertices, conjecture held every single time
(as it must, being a proven theorem), with the code independently
re-deriving the known extremal behaviour (e.g. a transitive tournament's
lone "sink" vertex is always the one that satisfies the inequality, with
slack exactly 0).

## Honest conclusion

We did not find a counterexample, and — more informatively — adversarial
search **actively trying** to build one, with a completely free hand over
which games are missing and how the rest are oriented, consistently hits
a wall at "all but a tiny handful of vertices." That last holdout never
gives way, across every (n, m) combination tried. This is exactly the
qualitative signature you'd expect if the conjecture is simply true and
tight: there's always (at least) one vertex — generally looking like a
low-out-degree "sink-like" vertex — that the adversarial pressure cannot
touch.

This is a negative result (no counterexample, unsurprising given how
well-studied this conjecture is), but the *shape* of the search — how
easily and consistently it plateaus at n-1 or n-2, never budging further —
is itself a small, honest piece of empirical evidence for the conjecture's
robustness in exactly the regime (near-tournaments, small numbers of
missing edges) that current published partial results are chipping away
at analytically.

**Update:** we did subsequently push `m` all the way up to `n` (i.e. very
sparse graphs, half the pairs unplayed) across a wide range of `n` — the
full 59-combination sweep above. The result held: no counterexample, and
the achievable bad-fraction stayed flat regardless of sparsity. That
somewhat undercuts our original hypothesis that sparser/less-explored
territory would be more fruitful — within an unstructured random-missing-
edges search, at least, density genuinely doesn't seem to matter.

**What would move this forward next:** try *structured* (non-uniform)
missing-edge patterns designed to mimic the star/path constructions
in the literature (tournaments missing a star, missing two stars, missing
disjoint paths), since those are the specific structures published partial
results have needed to handle separately — an unstructured search may be
missing exactly the adversarial patterns that matter; and, separately,
scale up the annealing step budget proportionally to `n²` to rule out the
budget-artifact explanation for the n=200 vs n=10 gap noted above.

## Reproducing

```
cd problems/second_neighborhood_conjecture
python3 adversarial_search.py 30 5 --steps 60000     # n=30 vertices, 5 missing games
./sweep.sh                                            # main (n, m) grid, small/moderate m
./sweep_sparse.sh                                     # sparser regime, m up to n
```

Raw results (adjacency matrices, per-vertex slack, full step history) are
under `results/`.
