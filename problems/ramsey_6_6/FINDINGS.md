# The Ramsey Number R(6,6)

**Source:** classical Ramsey theory. **Status: genuinely open**, and
listed by Epoch AI's FrontierMath "open problems" collection as a
notable unsolved target. Published bounds, cross-checked across
multiple sources: `102 <= R(6,6) <= 160`. The lower bound (Kalbfleisch,
1966) is even older than R(5,5)'s (Exoo, 1989) — nearly **60 years**
without improvement.

## The problem, in plain English

`R(6,6)` is the smallest `N` such that every 2-coloring of `K_N`
contains a monochromatic `K6`. To push the lower bound, exhibit a
2-coloring of `K_n` where neither color contains a `K6`. The current
record witness is on 101 vertices, giving `R(6,6) >= 102`.

## Honest scoping, stated up front (same caveat as R(5,5))

We don't know whether Kalbfleisch's actual 101-vertex construction is a
pure circulant graph — like Exoo's R(5,5) construction, many of these
older records use modified/near-circulant constructions. This search
only covers **pure circulant** 2-colorings, so it doesn't attempt to
reproduce the exact record.

## What we did

Reused `lib/multicolor_circulant.py` exactly as built for R(5,5), just
changing `clique_sizes` from `[5,5]` to `[6,6]`. Swept representative
values of `n` with a local search (greedy recoloring + noise + periodic
restarts), then narrowed in on the actual ceiling once a rough range was
established.

## Results

| n | result |
|---|--------|
| 30-59 | found valid witnesses (fast — under a second for most) |
| 60 | not found in 27.2s |
| 61-62 | found — color sizes `[14,16]`/`[15,16]` |
| **63-101** (checked at 63,64,65,70,80,85,90,95,99,100,101) | **not found** at any of these points |

The witness at **n=62** (difference sets `{1,3,4,5,6,7,12,15,16,17,18,
20,21,27,28}` / `{2,8,9,10,11,13,14,19,22,23,24,25,26,29,30,31}`) was
independently re-verified from scratch using `networkx.find_cliques` —
confirmed both color classes have max clique size exactly 5.

## Honest conclusion

**This does not improve on, or come close to, the published record.**
Pure circulant search here caps out at `n=62` — well under half of the
known 101-vertex record. This is a noticeably lower ceiling (relative to
the gap to the actual record) than we saw with R(5,5), where the search
reached `n=41` against a record of `42` — nearly matching it. Here the
gap between what pure circulant local search can reach (62) and the
actual record (101) is large, suggesting either:
- the K6-vs-K6 local search itself scales worse than K5-vs-K5 (each
  candidate check requires finding a 5-clique within the difference set
  rather than a 4-clique, which is a real jump in per-check cost, and we
  observed this directly — trials at n=90 took 20+ seconds without even
  converging), and/or
- the real 101-vertex record construction is *structurally* further
  from pure circulant than R(5,5)'s was.

We can't distinguish between these from this run alone. Either way, the
actual open question (does a 102+-vertex witness exist at all) is
completely untouched — no evidence for or against was produced here.

**What would move this forward:** a proper simulated-annealing schedule
or a smarter incremental clique-check (rather than full backtracking
from scratch on every candidate flip) to push the pure-circulant ceiling
further before concluding it's genuinely far from the record; or,
better, investigating what Kalbfleisch's actual construction looks like
structurally (near-circulant with repairs, product/blow-up
construction, etc.) rather than assuming pure circulant.

## Reproducing

```
cd problems/ramsey_6_6
python3 search.py --start 30 --stop 65 --time-per-n 20
```
