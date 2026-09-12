# The Ramsey Number R(5,6)

**Source:** classical Ramsey theory. **Status: genuinely open, and
actively moving** — unlike R(5,5)/R(6,6) (records standing since
1989/1966), this one's lower bound was improved **within the last two
years**: `59 <= R(5,6) <= 85` (lower bound raised from 58 to 59 in
October 2023; upper bound 85 from earlier work, cross-checked across
multiple sources).

## The problem, in plain English

`R(5,6)` is the smallest `N` such that every 2-coloring of `K_N`
contains a monochromatic `K5` in one color or a monochromatic `K6` in
the other. To push the lower bound, exhibit a 2-coloring of `K_n` where
color 1 is `K5`-free and color 2 is `K6`-free. The current record is on
58 vertices.

## Honest scoping (same caveat as R(5,5)/R(6,6))

We don't know whether the actual 58-vertex record construction is a
pure circulant graph. This search only covers the pure circulant
restriction.

## What we did

Reused `lib/multicolor_circulant.py` exactly as built for R(5,5)/R(6,6),
this time with **asymmetric** clique sizes `[5,6]` (one color forbids
`K5`, the other forbids `K6`) — the library already supported this
generically, no changes needed. Swept `n=30` through `60`.

## Results

| n | result |
|---|--------|
| 30-47 | found valid witnesses (fast, mostly under a second) |
| 48 | not found in 22.7s |
| 49-50 | found |
| 51 | not found in 20.8s |
| **52** | **found** — color sizes `[13,13]` |
| **53-60** | **not found** (8 consecutive misses) |

The witness at **n=52** (`{1,3,8,13,15,16,17,19,22,23,24,25,26}` for
the `K5`-avoiding color, `{2,4,5,6,7,9,10,11,12,14,18,20,21}` for the
`K6`-avoiding color) was independently re-verified from scratch via
`networkx.find_cliques` — confirmed max clique size 4 and 5
respectively.

## Honest conclusion

**This does not improve on, or match, the published record.** Pure
circulant search reaches `n=52`, six short of the known 58-vertex
record. This is actually the closest pure-circulant search has gotten
to a known record in this project's Ramsey attempts so far, relative to
gap size (compare: R(5,5) reached 41 vs record 42 — 1 short; R(6,6)
reached 62 vs record 101 — 39 short; here, 52 vs 58 — 6 short), so this
family may be somewhat more amenable to pure circulant constructions
than the K6-heavy cases, though this is a loose pattern from a handful
of data points, not a proven trend.

The 8-consecutive-miss run from n=53 onward is a reasonably clean
ceiling signal for this particular search. We are **not** claiming any
progress on the actual open question (is `R(5,6) >= 60`, matching or
beating the recent 2023 improvement) — no witness was found anywhere
near the actual frontier.

**What would move this forward:** since this is the *most recently
active* Ramsey target attempted in this project (lower bound moved as
recently as 2023), it's worth reading the actual 2023 paper's
construction technique (not accessible during this session due to
network restrictions on arxiv.org) to see whether it's circulant-based
and, if so, what made the search that found it succeed where a generic
local search here fell 6 short.

## Reproducing

```
cd problems/ramsey_5_6
python3 search.py --start 30 --stop 60 --time-per-n 20
```
