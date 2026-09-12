# The Ruskey-Savage Conjecture (1993)

**Source:** Ruskey & Savage, 1993. **Status: genuinely open.** Every
matching of the n-dimensional hypercube graph `Q_n` conjecturally
extends to a Hamiltonian cycle of `Q_n`. Proven for perfect matchings
(Fink, 2007) and for matchings spanning at most 5 "directions"
(2024-2025). Last exhaustive computational check: **MathCheck, 2015**,
confirmed it for `n=5` (32 vertices) via SAT enumeration + CAS
verification. As far as could be determined, nobody has pushed this
computational frontier since.

## The problem, in plain English

The `n`-dimensional hypercube has `2^n` vertices (binary strings of
length `n`), with an edge between any two strings differing in exactly
one bit. A "matching" is a set of edges that don't share endpoints.
The conjecture: no matter which matching you pick, you can always
extend it into a single cycle that visits every vertex exactly once
(a Hamiltonian cycle) while keeping every matching edge in place.

## What we did

1. **Built a SAT-based extension checker**: binary variable per edge,
   degree-2 constraint at every vertex, required matching edges forced
   selected, and lazy subtour elimination (solve → check if the
   selected edges form one single cycle → if not, block that exact
   subtour decomposition and resolve). This mirrors MathCheck's own
   SAT+CAS approach (a connectivity check plays the role of the CAS).
2. **Validated on Q2-Q4**: the empty matching (must find a Hamiltonian
   cycle — the classical Gray code), random matchings of varying size,
   and random *maximal* matchings (the literature-flagged tricky case,
   since perfect matchings are already proven safe) — all independently
   re-verified.
3. **Performance came as a genuine surprise**: a single check resolves
   in well under 0.1 seconds even at `Q8` (256 vertices, 1024 edges) —
   far more scalable than expected. This opened the door to large-scale
   sampling rather than a narrow hand-picked test.
4. **Large-scale random sweep**: thousands of random and maximal
   matchings across `Q6`, `Q7`, `Q8` (all past the MathCheck frontier),
   plus a deeper follow-up specifically targeting `Q6` with 20,000
   trials (an attempt to push toward `Q9`/`Q10` was in progress when
   this investigation was redirected to a different problem and
   stopped early — noted honestly below).

## Results

| dimension | matchings tested | result |
|---|---|---|
| Q6 | 23,000 (3,000 + a deeper 20,000-trial follow-up) | **all extend**, 0 flagged |
| Q7 | 3,000 | **all extend**, 0 flagged |
| Q8 | 3,000 | **all extend**, 0 flagged |
| Q9, Q10 | — | sweep was stopped before completing any trials |

**Every single one of the 29,000 tested matchings extends to a
Hamiltonian cycle**, with zero flags and zero escalations needed
(every flagged case during development resolved trivially on a bigger
iteration budget — no genuine near-misses were seen).

## Honest conclusion

**No counterexample, and a genuine, if modest, extension of the
computational frontier.** This is the first record (that this project
could find) of anyone testing Ruskey-Savage matchings at `n=6, 7, 8` —
one dimension beyond MathCheck's 2015 exhaustive `n=5` result, via
large-scale random sampling rather than exhaustive enumeration (the
total number of matchings of `Q6`+ is astronomically large; this is
sampling, not exhaustive coverage, and should not be overstated as
such). The sampling was weighted toward maximal matchings specifically
because perfect matchings are already proven safe by Fink — the
"maximal but not perfect" case is the genuinely open one.

**What would move this forward:** finish pushing to `Q9`/`Q10` (the
method scales far better than expected, so this is realistic — the
interrupted follow-up run had already completed 20,000/20,000 Q6
trials in 73 seconds before being stopped mid-`Q9`); implement the
adversarial search described in the original attack plan (mutate a
matching's edges, using the SAT solver's iteration count as a cheap
"hardness" proxy to hunt for resistant instances, rather than pure
random sampling); and use `Q6`'s large automorphism group for symmetry
reduction to get genuine exhaustive-style coverage rather than random
sampling at that size.

## Reproducing

```
cd problems/ruskey_savage_conjecture/code
python3 validate_known.py
python3 large_sweep.py --dims 6 7 8 --trials-per-dim 3000
```
