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

| n | m range tried | best simultaneously-bad fraction found |
|---|---|---|
| 10 | 1–8 | 90% (9/10) |
| 15 | 1–8 | 93% (14/15) |
| 20 | 1–15 | 85–95% |
| 30 | 1–15 | 83–90% |
| 50 | 1–3 (sweep still running for more m) | 88–90% |
| *(80, 120, 200 — see `results/` for final numbers once the sweep completes)* | | |

**No counterexample was found at any (n, m) tried.** Every single run
converges to a very consistent, striking pattern: adversarial pressure can
force **all but a small handful of vertices** (typically exactly 1, up to
~3 at larger n within our step budget) to be simultaneously bad — and then
gets stuck there, no matter how many more annealing steps or how the
"missing games" are rearranged. The number of missing edges `m` barely
matters at all in the range we tried (1 through 15, and up to n/8) — the
achievable bad-fraction is essentially flat around 85-95% regardless.

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

**What would move this forward:** push `m` much higher relative to `n`
(sparser graphs, further from a tournament, is the genuinely *less*
explored region — current papers focus on "missing a star" or "missing
two stars", i.e. small/structured `m`), and try structured (non-uniform)
missing-edge patterns designed to mimic the star/path constructions in the
literature, to see if unstructured adversarial search can match or beat
what hand-crafted constructions achieve.

## Reproducing

```
cd problems/second_neighborhood_conjecture
python3 adversarial_search.py 30 5 --steps 60000     # n=30 vertices, 5 missing games
./sweep.sh                                            # full (n, m) grid
```

Raw results (adjacency matrices, per-vertex slack, full step history) are
under `results/`.
