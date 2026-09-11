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
| 18  | 420,000 (+400,000 more running) | 0 | 0% |
| 20  | **420,000** | **0** | **0%** |
| 22  | **410,000** | **0** | **0%** |
| 24  | **320,000** | **0** | **0%** |
| 26  | 60,000 (+150,000 more running) | 0 | 0% |
| 28  | 60,000 (+150,000 more running) | 0 | 0% |
| 30  | 50,000  | 0 | 0% |
| 40  | 40,000  | 0 | 0% |
| 46, 50, 60, 80 | 15,000-30,000 each | 0 | 0% |
| 100, 120, 150, 200, 300, 500 | 30-10,000 each | 0 | 0% |

Every single size we tried from **n=18 up through n=500** — nearly **3
million** combined random samples — came back completely clean. Not one
exception. Meanwhile n=16, sampled just as hard (420,000 draws), keeps
producing them at a stable, well-measured rate of about 1 in 3,600. That's
a striking, sudden cliff: if the true n=18 rate were even remotely close to
the n=16 rate, 420,000 samples would have turned up roughly 116 more —
instead there are zero.

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
- **From n=18 all the way up to n=500, across over a million combined
  random samples, we found zero exceptions.** That's a sharp, sudden drop
  from a measurable ~0.03-1% rate at n≤16 to nothing detectable at n≥18 —
  much sharper than the smooth decay from n=6 to n=16 would suggest. That
  asymmetry is itself the most interesting thing we found: it's consistent
  with a genuinely finite exception set that simply stops somewhere in
  [16, 18], but it's equally consistent with an ever-rarer population that
  a million samples still isn't enough to detect at these sizes (the space
  of 5-regular graphs on 500 vertices is astronomically larger than a
  couple thousand samples can meaningfully cover).
- Adversarial graph-space SA (see below) never found a hard instance at
  any size we tried — it has no discoverable "gradient" toward whatever
  makes a graph an exception, reinforcing that these are structurally
  isolated, not part of a smoothly-connected hard region.

**Bottom line:** we did not prove or disprove DeVos's conjecture for r=5,
but we pushed the *exhaustive* frontier from n=12 to n=14, and the
*empirical* frontier (confirmed real exceptions) to n=16 — plus a strong
negative result (zero exceptions in a million+ samples) from n=18 to 500.
If a professional graph theorist wanted to pick this up, the natural next
questions are exactly the ones this data poses: is there truly a sharp
cutoff around n=16-18, and if so, why — what structural argument would
prove no 5-regular graph beyond some fixed size can lack a friendly
partition?

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
