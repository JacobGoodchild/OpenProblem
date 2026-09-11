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
| 14 | *(in progress — see results/exhaustive_n14.json for the live/final count)* | | |

`K6` itself is an exception — consistent with the pattern from other
degrees (`K4`/`K3,3` for r=3, `K5` for r=4): the complete graph `K_{r+1}`
is always too small and too symmetric to split fairly.

**The exception *fraction* drops sharply and monotonically** as n grows
(100% → 33% → 22% → 9% → ...). That's the encouraging sign the conjecture
predicts. But a shrinking *fraction* is not the same as a shrinking
*count* — the open question is whether the absolute number of exceptions
eventually hits zero and stays there (finite exception list) or merely
gets rarer forever without ever vanishing (which would make the
DeVos conjecture **false** for r=5).

### Random sampling, larger n

| n   | samples | exceptions found | rate |
|-----|---------|-------------------|------|
| 14  | 300     | 3                 | ~1%  |
| 16  | 20,000  | 9                 | 0.045% |
| 18  | 20,000 (+100k running) | 0 (so far) | — |
| 20  | 20,000 (+100k running) | 0 (so far) | — |
| 24  | 20,000  | 0                 | 0% |
| 100 | 100     | 0                 | 0% |
| 300 | 30      | 0                 | 0% |

The n=16 exceptions are genuine, SAT-verified (not heuristic artifacts).
Structurally, the small exceptions we inspected (at n=12 and n=16) are
**not** built from cliques — none of a sample of 200 n=12 exceptions
contains a `K6` subgraph, they are almost all maximally (5-)connected, and
the n=16 examples found have **trivial automorphism group** (no special
symmetry at all) — so these are not "obvious" symmetric constructions, they
are structurally generic-looking 5-regular graphs that simply happen to
have no friendly partition.

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

- The exception rate falls off sharply and (so far) monotonically as `n`
  grows, consistent with the conjectured finiteness.
- We confirmed the frontier of *known* exceptions empirically out to at
  least **n=16** (new finds via random sampling beyond n=14, which is
  about where prior published exhaustive work seems to have stopped for
  general — non-Cayley — 5-regular graphs, though the abelian-Cayley
  sub-case is already fully resolved in the literature).
- We have **not** found any exception at n ≥ 18 despite tens of thousands
  of random samples and (separately) tens of thousands of adversarial
  search steps per size — but this is far from a proof of absence; the
  n=16 rate (0.045%) is already low enough that n=18/20 could easily have
  an even-rarer population we simply haven't hit yet.
- If exceptions do stop entirely at some point, our data does not yet
  pin down where — n=14 still had a ~1% raw rate; by n=16 it was down
  to 0.045%.

**What would move this forward:** (a) exhaustive enumeration at n=14 and
n=16 (n=14 was running at the time of writing; n=16 is likely computationally
out of reach for full nauty enumeration, but a much larger random/SA sample
would sharpen the n=18+ picture), and (b) a genuinely different heuristic
that isn't blind to whatever structural feature makes an exception (since
our double-edge-swap SA seems to have no gradient toward them at all,
worth trying vertex-based rewiring, or a "grow a known small exception
by 2 vertices" constructive move instead of pure edge-swaps).

## Reproducing

```
cd problems/friendly_partitions_5regular
python3 exhaustive_search.py 12                       # exact, all graphs of a given n
python3 random_search.py 20 --samples 5000             # random sampling + SAT escalation
python3 adversarial_search.py 20 --steps 20000          # SA over graph space
```

All raw results (including every discovered exception, in `graph6` format)
are under `results/`.
