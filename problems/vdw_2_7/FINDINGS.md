# The Van der Waerden Number W(2,7)

**Source:** classical Ramsey-type theorem on arithmetic progressions
(van der Waerden, 1927); current bounds from the literature (e.g. Rabung
& Lotts). **Status: genuinely open, with an enormous bound gap.** Only
seven exact two-color van der Waerden numbers are known at all
(`W(2,1..6) = 1, 3, 9, 35, 178, 1132`). `W(2,7)` is only known to satisfy
`W(2,7) >= 3703` (an explicit witness coloring), with the best *proven*
upper bound so weak it's really just "somewhere below `2^48`" — one of
the largest known gaps between lower and upper bound for any small
combinatorial number of this kind.

**This is the weakest result of the four problems in this repo so far,
and we're saying that plainly rather than dressing it up.**

## The problem, in plain English

Color every integer from 1 to N using 2 colors (say red and blue). Is
there always a monochromatic arithmetic progression of length 7 (7
equally-spaced numbers, all the same color)? `W(2,7)` is the smallest N
for which the answer is guaranteed yes. Currently: nobody knows whether
`N=3703` is close to that threshold or wildly far from it — proven bounds
allow the true answer to be anywhere in a range spanning many orders of
magnitude.

## What we did (and where it fell short)

1. **SAT encoding.** One boolean variable per integer 1..N; for every
   length-7 AP within {1,...,N}, two clauses forbid it from being
   monochromatic. This is the standard, well-established technique in
   this literature (Herwig, Heule, van Lambalgen & van Maaren 2007, and
   others). **Validated exactly** against all three smaller known values:
   `W(2,3)=9`, `W(2,4)=35`, `W(2,5)=178` — the solver (Glucose4 via
   `pysat`) correctly reports SAT one below each threshold and UNSAT
   exactly at it, in every case.
2. **The SAT approach did not scale to the actual target.** Attempting to
   even *reproduce* the already-published `N=3703` witness (not find a
   new one — just confirm SAT on an instance with a known-to-exist
   solution) via a raw call to Glucose4 on the full ~2.3-million-clause
   CNF instance **did not finish within 300 seconds.** This is itself an
   honest, informative negative data point: a generic complete SAT solver
   call is not the right tool at this scale without much more careful
   engineering (a better encoding, symmetry breaking, or supplying the
   solver with a partial assignment as a hint).
3. **Pivoted to local search** (WalkSAT-style greedy-with-noise flipping,
   minimizing the number of monochromatic APs), which is closer to how
   such witnesses are typically found in practice for large instances (a
   complete SAT proof is really only needed for the *upper*-bound/UNSAT
   direction, not for finding a valid coloring). After fixing a bug in
   the first version (choosing which position to flip uniformly at random
   within a violated AP, rather than greedily — this failed to converge
   even at `k=5`), the corrected version validated cleanly: **instant**
   at `k=3`, `0.8s` at `k=4`, `21s` at `k=5` (`N=177`, matching `W(2,5)-1`
   exactly).
4. **Still did not scale far enough.** Testing the same local search on
   `k=6` (`N=1131`, matching the known `W(2,6)-1`) **did not converge
   within ~2.5 minutes** (we cut it off there rather than let it run
   indefinitely). Since `k=6` at `N=1131` is already smaller and easier
   than the actual open target (`k=7` at `N=3703`, a ~3.3x larger
   instance with a longer, rarer-but-more-numerous constraint structure),
   we did not attempt the real `k=7` case at all — there was no reason to
   expect it would do better than the `k=6` run that already failed to
   converge in reasonable time.

## Honest conclusion

**We made no progress whatsoever on the actual open question.** We did
not reproduce the published `N=3703` lower-bound witness, we did not
attempt to extend it, and our local search implementation's difficulty
scaling (instant -> 0.8s -> 21s -> did-not-converge-in-150s going from
`k=3` to `k=6`) makes clear that a substantially better implementation —
not just more patience — would be needed before `k=7` at the relevant
scale is worth attempting at all.

This is a different, more limited kind of negative result than the other
three problems in this repo:
- **Tuza's conjecture / R(3,10):** complete, airtight negative results —
  every candidate in a well-defined search space was checked, and none
  worked.
- **Snake-in-the-box:** an honest shortfall against published records,
  but the method itself worked correctly and got meaningfully close
  (81-90% of the target).
- **This problem:** the method didn't even reach the *starting line* —
  we couldn't efficiently reproduce a smaller, already-easier known
  value, so no claim can be made about the actual open target at all.

**What would be needed to make real progress:** (a) a much better local
search — real WalkSAT implementations use efficient incremental
data structures (watched literals / occurrence lists tuned in C, not
Python dictionaries) and adaptive noise schedules; a Python
implementation is likely 100-1000x slower than what's needed here; (b)
alternatively, a smarter SAT encoding exploiting known structural
results about van der Waerden colorings (e.g. many good colorings have
partial periodic/self-similar structure, which could be encoded as extra
constraints or used to seed the search rather than starting purely
random); (c) simply using a purpose-built, optimized solver (e.g. a
C/C++ WalkSAT variant, or state-of-the-art local-search SAT solvers like
YalSAT) instead of implementing one from scratch in Python.

## Reproducing

```
cd problems/vdw_2_7
python3 -c "
import sys; sys.path.insert(0, '../..')
from lib.van_der_waerden import check_vdw, verify_coloring
# validated exactly for k=3,4,5:
print(check_vdw(8, 3))    # SAT
print(check_vdw(9, 3))    # UNSAT
"
```

`lib/van_der_waerden.py` has both the SAT encoding (`check_vdw`, exact but
does not scale past small k) and the local search (`local_search_coloring`,
scales further but still not far enough for k=7 in this session).
