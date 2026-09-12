# The Ramsey Number R(3,11)

**Source:** classical Ramsey theory. **Status: genuinely open, and
recently active**: `47 <= R(3,11) <= 50`. The lower bound of 47 is
notable in its own right — it only recently broke a **46-year-old**
record of 46 (Exoo). The upper bound of 50 comes from computational
methods (Goedgebeur et al.). This is a live, tight (gap of only 3), and
recently-advanced target, not a settled or stale one.

## The problem, in plain English

`R(3,11)` is the smallest `N` such that every 2-coloring of `K_N`
contains a monochromatic triangle in one color or a monochromatic `K11`
in the other. To push the lower bound, exhibit a triangle-free graph on
`n` vertices with independence number `<= 10` (no independent set of
size 11, which corresponds to no `K11` in the complementary color).

## What we did

Reused the exact tooling already built and validated in this project for
`R(3,10)` and `R(4,7)` — no new library code:

1. **Phase 1** (`enumerate_candidates.py`): exhaustive enumeration of all
   circulant connection sets on `Z_n`, keeping the triangle-free ones via
   the fast arithmetic check (`is_triangle_free`), for `n=46` (the known
   record) and `n=47` (the actual open target — a witness here would
   improve the published lower bound).
2. **Phase 2** (`verify_candidates.py`): exact ILP feasibility check
   (does an independent set of size 11 exist?) on each triangle-free
   candidate, densest-first, parallelized, time-boxed at 300s per `n` —
   same pattern used for R(4,7)'s partial verification.

## Results

| n | triangle-free candidates (phase 1, exhaustive) | phase 2 coverage | witnesses found |
|---|---|---|---|
| 46 | 13,258 (out of 8,388,607 checked) | 3,143 / 13,258 = **23.7%** (densest-first) | 0 |
| 47 | 8,947 (out of 8,388,607 checked) | 1,069 / 8,947 = **11.9%** (densest-first) | 0 |

Phase 1 (the fast arithmetic filter) was exhaustive and complete for
both `n` — we have the *complete* list of triangle-free circulant
connection sets in both cases. Phase 2 (the expensive ILP independence
check) was only partial: the per-candidate ILP feasibility check turned
out considerably slower here than in the R(4,7) run (candidates near the
`k=11` independence threshold appear to be harder for CBC to resolve
quickly), so only the densest ~12-24% of candidates were checked within
the time budget.

## Honest conclusion

**This is a partial, inconclusive result, not a complete search** — same
honesty caveat as R(4,7). Two things are worth being precise about:

- At **n=47** (the actual open gap): no witness found among the densest
  11.9% of triangle-free circulant candidates. This neither supports nor
  rules out a circulant witness existing — 88% of the candidate space is
  simply unchecked. We are **not** claiming any progress on the open
  question of whether `R(3,11) >= 48`.
- At **n=46** (the *known* record, R(3,11)>=47): we also did not find a
  witness in our 23.7% coverage. This is a useful, if modest, negative
  data point: either the known n=46 witness is a *pure circulant*
  construction that happens to sit outside the densest quarter of the
  candidate space we checked, or (plausibly, going by how the
  literature describes it — "cyclic structure... a cluster of distances
  in the mid-range are of a single common colour") it is a **modified**
  cyclic construction rather than a pure circulant one, the same pattern
  we saw with Exoo's actual R(5,5) record earlier this session. We did
  not chase this down further given the time budget for this problem.

**What would move this forward:** (a) finish the exhaustive phase 2 pass
on both n=46 and n=47 (all triangle-free candidates are already
enumerated and saved — this is "just" more ILP wall-clock time, no new
method needed); (b) if a complete pass on n=46 still finds nothing, that
would be a concrete, interesting finding in itself (pure circulant
constructions cannot reach the known record here, mirroring what we
found for R(5,5)); (c) try near-circulant constructions (circulant plus
a small number of vertex/edge repairs) to actually target n=47+, rather
than pure circulant.

## Reproducing

```
cd problems/ramsey_3_11
python3 enumerate_candidates.py 46
python3 enumerate_candidates.py 47
python3 verify_candidates.py 46 300
python3 verify_candidates.py 47 300
```
