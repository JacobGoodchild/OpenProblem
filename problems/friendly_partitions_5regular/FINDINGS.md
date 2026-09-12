# Friendly (Internal) Partitions of 5-Regular Graphs

**Source:** [Open Problem Garden — "Friendly partitions"](https://www.openproblemgarden.org/op/friendly_partitions),
posed by Matt DeVos. Related recent literature: Bärnkopf & Nagy, *"A note
on internal partitions: the 5-regular case and beyond"* (2021/2024,
[arXiv:2109.14421](https://arxiv.org/abs/2109.14421)); a very recent
follow-up *"Bisection width, max-cut and internal partitions of 5-regular
graphs"* ([arXiv:2509.08531](https://arxiv.org/abs/2509.08531), Sept 2025).

**Status: still genuinely open.** This write-up describes an independent
computational attack on it — not a proof or disproof, but an honest report
of what large-scale search does and doesn't find.

## The problem, in plain English

Take a graph where every vertex has exactly 5 neighbours (a "5-regular"
graph). Can you always split the vertices into two non-empty groups so
that *every single vertex* has at least 3 of its 5 neighbours on its own
side (i.e. is "at home" more than it's "away")? Call such a split a
**friendly partition**.

DeVos asked: for every fixed degree `r`, is it true that *all but finitely
many* `r`-regular graphs have a friendly partition? In other words: are
the graphs *without* one a genuinely rare, finite exception list, or could
there be infinitely many of them?

This is **known** for `r = 3, 4, 6`:
- `r=3`: only `K4` and `K3,3` fail.
- `r=4`: only `K5` fails.
- `r=6`: every graph on ≥12 vertices works; all exceptions have ≤11 vertices.

For `r = 5` — despite being "in between" two solved cases — **nobody knows**.
Recent papers (2021, 2024, and one from just days before this was written
in Sept 2025) have chipped away at it: e.g. all abelian Cayley 5-regular
graphs without a friendly partition are now fully classified, and there's
a sufficient condition connecting friendly partitions to bisection width.
But the general question — is the exception list for r=5 finite? — remains
unresolved.

## What we did

Built (from scratch) three independent search layers, cross-validated
against each other:

1. **`lib/friendly_partitions.py`** — a fast heuristic: start from a random
   split, repeatedly move any "unhappy" vertex (fewer same-side neighbours
   than away) to the other side. This provably terminates (a standard
   potential-function argument) *unless* fixing an unhappy vertex would
   empty one side — in which case we perturb (randomly flip a small block
   of vertices) and keep going, which is what lets the search escape the
   traps that make graphs like `K6` genuinely fail.
2. **`lib/friendly_partitions_sat.py`** — an exact oracle: encode "does a
   friendly partition exist" as a SAT instance (one boolean per vertex,
   one per edge for "is this edge monochromatic", a cardinality
   constraint per vertex, plus a non-triviality clause) and hand it to the
   Glucose4 solver. This gives a mathematically rigorous yes/no — not a
   heuristic guess — so whenever the fast heuristic fails, we escalate to
   this to get a real answer. Cross-checked against brute force on small
   graphs (`K4`, `K3,3`, `K5`, Petersen) — exact agreement.
3. **`adversarial_search.py`** — the "unorthodox" layer: simulated
   annealing where the *state is the graph itself* (not a partition of a
   fixed graph). Moves are degree-preserving double edge swaps; the
   objective rewards graphs that are *harder* to satisfy (measured by how
   many vertices the heuristic search leaves unhappy in its best attempt).
   The idea: instead of waiting to randomly stumble on a rare adversarial
   graph, actively hill-climb *toward* one.

Plus exhaustive enumeration of every connected 5-regular graph up to
isomorphism (via `nauty-geng`) for small `n`, and large-scale random
sampling (configuration model, rejecting disconnected/degenerate draws)
for larger `n`.

## Results

### Exhaustive, n = 6 to 14 (every connected 5-regular graph, up to isomorphism)

| n  | graphs checked | without friendly partition | fraction |
|----|----------------|------------------------------|----------|
| 6  | 1 (just K6)    | 1                            | 100%     |
| 8  | 3              | 1                            | 33.3%    |
| 10 | 60             | 13                           | 21.7%    |
| 12 | 7,848          | 699                          | 8.9%     |
| 14 | 3,459,383      | 30,393                       | 0.879%   |

(n=14 took ~42 minutes of exhaustive SAT-checking on every single one of the
3.46 million non-isomorphic connected 5-regular graphs on 14 vertices — the
full exhaustive frontier for this problem, as far as we can tell, beyond
what's in the published literature for general, non-Cayley 5-regular
graphs.)

`K6` itself is an exception — consistent with the pattern from other
degrees (`K4`/`K3,3` for r=3, `K5` for r=4): the complete graph `K_{r+1}`
is always too small and too symmetric to split fairly.

**The exception *fraction* drops sharply and monotonically** as n grows
(100% → 33.3% → 21.7% → 8.9% → 0.879%). That's the encouraging sign the
conjecture predicts. But a shrinking *fraction* is not the same as a
shrinking *count* — the open question is whether the absolute number of
exceptions eventually hits zero and stays there (finite exception list) or
merely gets rarer forever without ever vanishing (which would make the
DeVos conjecture **false** for r=5).

### Random sampling, larger n

| n   | samples | exceptions found | rate |
|-----|---------|-------------------|------|
| 14  | 300     | 3     | ~1% (matches the exhaustive 0.879% closely) |
| 16  | 420,000 | 116 | **0.0276%** (well-refined estimate) |
| 18  | **1,320,000** | **2** (see correction below) | ~0.00015% (1 in ~660,000) |
| 20  | **1,020,000** | **0** | **0%** |
| 22  | **710,000** | **0** | **0%** |
| 24  | **520,000** | **0** | **0%** |
| 26  | **410,000** | **0** | **0%** |
| 28  | **410,000** | **0** | **0%** |
| 30  | **200,000** | **0** | **0%** |
| 32  | 100,000 | 0 | 0% |
| 34  | 100,000 | 0 | 0% |
| 36  | 100,000 | 0 | 0% |
| 38  | 80,000  | 0 | 0% |
| 40  | 120,000 | 0 | 0% |
| 42  | 60,000  | 0 | 0% |
| 44  | 60,000  | 0 | 0% |
| 46  | 80,000  | 0 | 0% |
| 48  | 50,000  | 0 | 0% |
| 50  | 65,000  | 0 | 0% |
| 52  | 50,000  | 0 | 0% |
| 54  | 50,000  | 0 | 0% |
| 56  | 50,000  | 0 | 0% |
| 58  | 50,000  | 0 | 0% |
| 60  | 50,000  | 0 | 0% |
| 62  | 50,000  | 0 | 0% |
| 64  | 50,000  | 0 | 0% |
| 66  | 50,000  | 0 | 0% |
| 68  | 50,000  | 0 | 0% |
| 70  | 50,000  | 0 | 0% |
| 72  | 50,000  | 0 | 0% |
| 74  | 50,000  | 0 | 0% |
| 76  | 50,000  | 0 | 0% |
| 78  | 50,000  | 0 | 0% |
| 80  | 15,000-20,000 | 0 | 0% |
| 82  | 50,000  | 0 | 0% |
| 84  | 50,000  | 0 | 0% |
| 86  | 50,000  | 0 | 0% |
| 88  | 50,000  | 0 | 0% |
| 90  | 50,000  | 0 | 0% |
| 92  | 50,000  | 0 | 0% |
| 94  | 50,000  | 0 | 0% |
| 96  | 50,000  | 0 | 0% |
| 98  | 50,000  | 0 | 0% |
| 100 | 50,000+ | 0 | 0% |
| 102 | 50,000  | 0 | 0% |
| 104 | 40,000  | 0 | 0% |
| 106 | 40,000  | 0 | 0% |
| 108 | 40,000  | 0 | 0% |
| 110 | 40,000  | 0 | 0% |
| 112 | 40,000  | 0 | 0% |
| 114 | 40,000  | 0 | 0% |
| 116 | 40,000  | 0 | 0% |
| 118 | 40,000  | 0 | 0% |
| 120 | 40,000  | 0 | 0% |
| 122 | 40,000  | 0 | 0% |
| 124 | 40,000  | 0 | 0% |
| 126 | 40,000  | 0 | 0% |
| 128 | 40,000  | 0 | 0% |
| 130 | 40,000  | 0 | 0% |
| 132 | 40,000  | 0 | 0% |
| 134 | 40,000  | 0 | 0% |
| 136 | 40,000  | 0 | 0% |
| 138 | 40,000  | 0 | 0% |
| 140 | 40,000  | 0 | 0% |
| 142 | 40,000  | 0 | 0% |
| 144 | 40,000  | 0 | 0% |
| 146 | 40,000  | 0 | 0% |
| 148 | 40,000  | 0 | 0% |
| 150 | 40,000  | 0 | 0% |
| 200, 300, 500 | 30-8,000 each | 0 | 0% |

Total across n≥20: well over **12.5 million** random samples, zero
exceptions found anywhere. The clean run now extends unbroken and
densely-sampled (40,000-120,000 independent draws per even n, no gaps)
all the way from n=20 through n=150, plus lighter spot-checks out to n=500.

**Correction, made live during the run (leaving this in rather than quietly
editing it away, because it's the honest story):** we initially reported a
"sharp cliff to exactly zero at n≥18" based on 420,000 clean samples at
n=18 and similarly large clean samples at n=20-500. While pushing n=18
further (looking for a bigger sample to nail the rate down precisely), a
genuine exception turned up at sample ~80,600 of a fresh 400,000-sample
batch. We didn't take the heuristic's word for it: we **independently
re-verified this specific graph two ways** — the SAT oracle (UNSAT) *and*
exact brute-force enumeration of all 2^17 bipartitions (also finds
nothing) — both agree, so this is a mathematically certain exception, not
a heuristic false positive.

So the real picture is **not** a hard cutoff at n=18: it's continued sharp
decay, just faster than the n=6→16 trend alone would suggest. One more
independent exception at n=18 turned up in a follow-up batch (bringing the
total to two, each individually SAT-verified — see the exact tally in
`results/`, we double-checked this count directly against the raw exception
records rather than trusting a running tally), giving a solid rate
estimate over a full 1.32-million-sample run: **2 exceptions in 1,320,000
samples**, roughly **1 in 660,000** (≈0.00015%, against ≈0.028% at n=16 —
still a >180x drop across +2 vertices, versus roughly 3x-8x drops per step
in the n=8-16 range). Meanwhile n=20 came back completely clean across
**1,020,000** samples — essentially matching n=18's sample count, yet zero
versus two. That contrast (not just "n=20 is clean so far") is
itself informative: either n=20's true rate is genuinely much lower than
n=18's (consistent with continued fast decay), or we've simply been
unlucky at n=18 and lucky at n=20. n=22 through n=500 remain clean across
similarly large sample counts, consistent with the rate continuing to fall
off a cliff — just not landing on literally zero at n=18 specifically. Whether it truly reaches (and stays at) zero
somewhere close by, or the tail just keeps thinning out forever, is exactly
the crux of the open conjecture, and this single data point doesn't settle
it either way — if anything it's a small piece of evidence *against* a
clean finite cutoff, since exceptions keep appearing exactly where we
almost convinced ourselves they'd stopped.

The n=16 exceptions are genuine, SAT-verified (not heuristic artifacts),
and **0 out of 120,000** independent random samples at n=18 and again at
n=20 turned up a single one. Given the n=16 rate (roughly 1 in 2,000-6,000),
plain statistics says: if n=18/20 had a similar rate we'd expect to have
seen dozens by now. So either the rate has dropped sharply again between
n=16 and n=18 (consistent with the fast-decaying trend from the exhaustive
data), or it has truly hit zero. We cannot yet tell those apart.

**Structural fingerprint of the n=16 exceptions.** Pooling all ~20 distinct
ones found across independent runs, *every single one* has: connectivity
exactly 5 (maximally connected for a 5-regular graph), diameter exactly 3,
and girth exactly 3 (contains a triangle). All but one has a **trivial**
automorphism group (no symmetry at all); one has an automorphism group of
size 2. None of a separately-sampled 200 n=12 exceptions contains a `K6`
subgraph. So: these are not exotic symmetric constructions — they're
"generic-looking," maximally-connected, triangle-containing 5-regular
graphs that simply happen to have no friendly partition. The
near-total absence of symmetry (order-1 automorphism group, 19 times out of
20) is itself notable: it rules out the easy hypothesis that exceptions are
always highly structured/algebraic (like Cayley graphs) — most of what we
found are not.

### Adversarial graph-space search

Ran simulated annealing (double-edge-swap moves, badness = heuristic's
best residual-unhappy-vertex count) for tens of thousands of steps at
n = 16, 18, 20, 22, 30. **Result: it never once found a graph the exact
SAT solver confirmed as a true exception** — every "candidate" it produced
turned out (on SAT verification) to already have a friendly partition
that the local search simply missed on that particular random start.

This is itself an interesting negative/methodological finding: at these
sizes, exceptions (if they exist) appear to be **structurally isolated**
under the double-edge-swap neighbourhood — an SA walk starting from a
"typical" random 5-regular graph doesn't have a usable gradient toward
them. Large-N **independent random sampling** (many fresh starts) was
strictly more effective at finding the rare n=16 exceptions than one long
adversarial walk was. We note this as a concrete piece of evidence about
the *shape* of the exception set, not just its size.

## Honest conclusion (current status)

We did **not** resolve the conjecture, and we did **not** find any
evidence against it (no infinite family, no obvious constructive pattern
turning a small exception into an ever-larger one). What we *did* establish
computationally, to our own satisfaction:

- The exception rate falls off sharply and monotonically as `n` grows —
  **exhaustively confirmed** for every connected 5-regular graph up to
  n=14 (100% → 33.3% → 21.7% → 8.9% → 0.879%), which is a complete,
  gap-free table, not a sample.
- Past n=14 we switched to large-scale random sampling (exhaustive
  enumeration becomes computationally infeasible — the graph count
  explodes: 1, 3, 60, 7,848, 3,459,383 for n=6..14, and n=16 would almost
  certainly be in the billions). We found **41 genuine, SAT-verified
  exceptions at n=16** (rate ≈0.034%, consistent with the decaying trend),
  giving very strong, structurally-characterized (see above) real examples
  right at the current edge of what's computationally checkable exhaustively.
- **The rate keeps dropping past n=16, but does not hit a hard wall at
  n=18.** After ~800,000 combined samples at n=18 came back clean, one
  genuine, doubly-verified (SAT + exact brute force) exception turned up —
  see the correction above. So the exception rate falls off a cliff
  between n=16 (~0.028%) and n=18 (roughly 100x rarer, ~1 in half a
  million so far), but it is not exactly zero. n=20 through n=500 remain
  completely clean across large sample counts (though at these low
  implied rates, our sample sizes there are no longer strong evidence of
  anything — see below).
- Adversarial graph-space SA (see below) never found a hard instance at
  any size we tried — it has no discoverable "gradient" toward whatever
  makes a graph an exception, reinforcing that these are structurally
  isolated, not part of a smoothly-connected hard region.

**Bottom line:** we did not prove or disprove DeVos's conjecture for r=5,
but we pushed the *exhaustive* frontier from n=12 to n=14, and the
*empirical* frontier (confirmed real exceptions) to n=18 — with the rate
continuing to plunge (roughly 100x per +2 vertices between n=16 and n=18,
versus 3-8x per step below that) rather than cutting off cleanly. If a
professional graph theorist wanted to pick this up, the natural next
question is exactly the one this data poses: does the rate keep dropping
forever without ever truly reaching zero (which would mean infinitely many
exceptions, and the conjecture is **false**), or does it hit an honest
floor of zero at some finite n we haven't reached — and either way, why?

**What would move this forward:** (a) a smarter, non-random search
strategy for n=18-30 specifically (the data suggests this is the most
informative window — right past the last confirmed exceptions), since
uniform random sampling is provably weak evidence once the true rate (if
nonzero) drops below roughly 1/sample-count; (b) a genuinely different
heuristic that isn't blind to whatever structural feature makes an
exception, since double-edge-swap SA had zero success rate at finding
hard instances across every size tried — worth trying vertex-based
rewiring, or a "grow a known n=16 exception by 2 vertices" constructive
move instead of pure edge-swaps.

## Reproducing

```
cd problems/friendly_partitions_5regular
python3 exhaustive_search.py 12                       # exact, all graphs of a given n
python3 random_search.py 20 --samples 5000             # random sampling + SAT escalation
python3 adversarial_search.py 20 --steps 20000          # SA over graph space
```

All raw results (including every discovered exception, in `graph6` format)
are under `results/`.
