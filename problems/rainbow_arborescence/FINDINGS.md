# The Rainbow Arborescence Conjecture (Bérczi, Király, Yamaguchi, Yokoi, Dec 2024)

**Status: stopped early, diminishing returns from random sampling
recognized honestly.** A digraph formed as the union of `n-1` distinctly
colored spanning arborescences conjecturally contains a spanning
arborescence using exactly one arc of each color. Proven only for
cycles (Nov 2025). No known counterexample.

## What we did

1. Built a SAT-based checker for the free-root question (fixed-root is
   NP-complete even on these constrained instances, confirmed via
   multiple search sources since arxiv.org itself is network-blocked
   here) — loop over candidate roots, lazy cycle elimination per root.
2. **Caught and fixed a real, consequential bug** during initial scaling
   tests: independent verification failed at `n=20+` despite SAT
   reporting success. Root cause: the checker discarded which specific
   colored arc (of possibly several parallel arcs with different
   colors between the same pair) was actually selected, and the
   verifier tried to re-derive some valid color assignment via greedy
   search — which can fail even when a real assignment exists. Fixed by
   tracking exact `(u,v,color)` triples end to end; also incidentally
   much faster afterward (n=30: 8.3s → 0.15s).
3. Validated on random instances at `n=4-8` (must always have a rainbow
   arborescence at these tiny sizes) — all confirmed and independently
   re-verified.
4. Ran a large tiered random sweep, `n=10` through `31` (of a planned
   `10`-`70` range), 150-500 trials per `n`.

## Results and why this was stopped

**Every single tested instance — several thousand across `n=10-31` —
had a rainbow arborescence, essentially always found on the very first
candidate root tried.** Zero flags, zero near-misses, zero escalations
needed at any point.

This is a real result (no counterexample in a genuine, bug-fixed sweep)
but a **low-information one**, and continuing it further was recognized
as a poor use of time before running the whole planned range: random
sampling is fundamentally unlikely to stumble onto a genuine
counterexample to an existence conjecture like this one — if one
exists, it would need to be *adversarially constructed* (the original
attack plan's stage 4), not found by chance. That adversarial search
was never built. Stopped here rather than let a low-yield random sweep
run to completion for its own sake.

## Honest conclusion

No counterexample found in ~4,000+ bug-fixed, independently-verified
random instances at `n=10-31` — real, if modest, evidence consistent
with the conjecture, but not a serious computational attack on it.
**The adversarial search (mutating arborescences, hill-climbing toward
configurations that resist a rainbow solution) is the part of the
original plan that would have actually mattered, and it wasn't
attempted.**

**What would move this forward:** build the adversarial search rather
than more random sampling — in particular, specifically constructing
instances designed to make many colors "compete" for the same few
edges near non-root vertices (intuitively the actual difficulty in a
system-of-distinct-representatives problem like this one), rather than
independently-random arborescences, which tend to spread color options
out and make the free-root question trivially easy, exactly as
observed here.

## Reproducing

```
cd problems/rainbow_arborescence/code
python3 validate_known.py
python3 large_sweep.py --tiers "10,25,500,300;26,31,150,300"
```
