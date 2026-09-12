# Generalized Ulam ("1-Additive") Sequences: Periodicity Classification

**Source:** Finch, "Patterns in 1-Additive Sequences" (Experimental
Mathematics, 1992), and follow-up work (Schmerl & Spiegel, Cassaigne &
Finch, Steinerberger). **Status:** a real, ongoing area of research —
not a single famous named conjecture, but a genuine open classification
problem: for a starting pair `(a,b)`, is the resulting 1-additive
sequence's gap pattern eventually periodic, and if so what's the
period? Only some cases have been proven either way; many are only
"probably" classified based on how far someone historically computed.

**Why this instead of another famous problem:** per direction from this
session's user, this is a deliberate pivot toward something obscure
(not Ramsey-numbers-famous) but still a real, checkable question, where
modern hardware can push meaningfully past what 1990s-era computers
checked for a *broad* sweep of starting pairs.

## The problem, in plain English

Starting from two numbers `a < b`, keep adding the smallest number that
can be written as a sum of two *different* earlier terms in *exactly
one* way. Look at the gaps between consecutive terms. For some starting
pairs, those gaps eventually settle into a strict repeating pattern
forever; for others (famously the original Ulam sequence `(1,2)`), they
never seem to.

## What we did (including a bug we caught and fixed — worth being
transparent about)

1. **Built a numpy-vectorized generator** and validated it exactly
   reproduces OEIS A002858 (the classical `(1,2)` sequence) for its
   first 30 terms, and confirms the proven periodicity (period 32) and
   exact even-term-count (3) of `(4,5)`, a case proven periodic by
   Cassaigne & Finch.
2. **First periodicity-detector version had a real bug**: it only
   checked a short window at the very end of the gap sequence for a
   repeating block, which is fooled by ordinary short runs of a common
   gap value (e.g. `(1,9)` was wrongly flagged "period 1, confirmed 7
   times" — inspecting the actual data showed the gaps are mostly `1`
   with occasional large spikes, not constant at all). Caught this via
   manual inspection before trusting any sweep results, and rewrote the
   detector to require ≥99.9% match over a span of at least 20 periods
   (or 500 elements), re-validated against both known cases, confirmed
   it now correctly rejects the `(1,9)` false positive.
3. **Swept 65 coprime pairs** (`a<=6`, `b<=20`, excluding pairs sharing
   a common factor — those are just scaled copies of a smaller pair,
   not independently interesting), 15,000 terms each.
4. **Followed up with a deeper check** on one "no period found" case
   (`(3,4)`) at 60,000 terms and a period search up to 500 (vs. 80 in
   the broad sweep), to see whether the shallow pass was just missing a
   longer period.

## Results

| | count |
|---|---|
| Periodic (confirmed, 100% match over long span) | 4 — `(2,5)` period 32, `(2,7)` period 26, `(2,15)` period 80, `(4,5)` period 32 |
| No period ≤80 found (15,000 terms) | 61 |
| `(3,4)` deeper check: no period ≤500 found even at 60,000 terms | — |

## Honest conclusion

**No counterexample to anything, and no dramatic discovery** — but this
wasn't really a "find one witness" search like most of this project's
earlier attempts; it's closer to an honest resurvey. The real findings:

- The **catch-and-fix of our own detector bug** is the most concrete
  outcome of this run. It's a reminder that "periodic-looking" data is
  easy to fabricate by accident (a common repeated value plus a short
  check window), and it's exactly the kind of thing an unverified
  automated sweep could have reported as a false discovery if we hadn't
  manually inspected a sample before trusting it.
- The "61 no-period-found" result from the broad sweep is **not**
  evidence those sequences are aperiodic — it only means no period
  ≤80 was detected within 15,000 terms, a real but narrow search limit.
- The `(3,4)` deep-dive genuinely extends what's been checked (60,000
  terms, period search to 500) and still finds nothing — a small,
  honest, incrementally-new data point, not proof of anything, since an
  even longer period or transient can't be ruled out by finite search.

**What would move this forward:** run the deep-dive (60k+ terms,
period search to 500+) on all 61 unclassified pairs, not just one — the
broad sweep already tells us which pairs are worth the extra compute;
compare our full classification table against Finch's original 1992
table and any follow-up papers to see exactly which cells are genuinely
new territory versus already documented; and for any pair that stays
unclassified even after a deep pass, that's a legitimate candidate for
"nobody has actually resolved this specific small case," worth writing
up on its own.

## Reproducing

```
cd problems/ulam_sequences
python3 validate_known.py
python3 sweep.py --a-max 6 --b-max 20 --n-terms 15000
```
