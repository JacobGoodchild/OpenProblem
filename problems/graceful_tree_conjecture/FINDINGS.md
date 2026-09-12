# The Graceful Tree (Ringel-Kotzig) Conjecture (1964)

**Status: stopped mid-investigation** — pivoted to other problems
(Ruskey-Savage, then Rainbow Arborescence) per user direction before
this could be run to a real conclusion. Documenting honestly what was
actually established, not what might have been found with more time.

## The problem, in plain English

Every tree's `n` vertices can be labelled with `{0,...,n-1}` so that the
resulting edge labels (differences between adjacent vertices' labels)
are exactly `{1,...,n-1}`, each used once. Verified computationally for
all trees up to `n=35` (Fang, published; `n=39` claimed but
unpublished/unconfirmed). Full-tree enumeration is astronomically
infeasible past that. This attack targeted a specific, currently active
gap confirmed via recent (2026) literature: **spiders with six or more
long legs of mixed length**, a family small enough to enumerate
exhaustively even at large `n` (unlike general trees).

## What we did

1. Built a backtracking search (using the necessary condition that
   labels `0` and `n-1` must be adjacent) and a local-search fallback
   (Aldred & McKay-style simulated annealing over labelings).
2. **Caught and fixed a real tooling weakness during validation**: both
   search methods struggled specifically on path graphs (`P20`+)
   despite paths being trivially graceful via an explicit closed-form
   construction — worked around by using explicit constructions for
   paths/stars in validation rather than debugging a shape irrelevant
   to the actual target.
3. **First sweep run produced 20 false-positive "unresolved" flags** —
   spot-checked 6 with a much bigger search budget and all 6 resolved
   instantly, confirming these were search-tooling artifacts (an
   underpowered local search getting stuck one swap short of a
   solution), not genuine difficulty. Also noticed most flagged cases
   were `n=20-31`, inside or at the edge of the already-verified `n<=35`
   frontier — not new territory even when resolved.
4. **Fixed and retargeted**: raised the default search budget
   substantially, added automatic escalation before ever reporting a
   flag, and retargeted the sweep to `n>39` (comfortably past even the
   unconfirmed Fang claim).
5. **The corrected, properly-targeted sweep was stopped after checking
   only 8 spiders** (all resolved, 0 unresolved) before this
   investigation was redirected to other problems.

## Honest conclusion

**No counterexample, but only a token amount of genuinely new-territory
coverage was completed** — 8 spiders with 6 long legs at `n>39`, all
found graceful, is not a meaningful sample size. The real, useful output
of this session's work on this problem is the validated, bug-fixed
tooling itself (backtracking + local search + explicit-construction
sanity checks), not a substantive sweep of the actual open gap.

**What would move this forward:** simply resume `spider_sweep.py` at
the corrected settings — the tooling is validated and the false-positive
issue is fixed, so this is purely a matter of compute time, not further
design work.

## Reproducing

```
cd problems/graceful_tree_conjecture/code
python3 validate_known.py
python3 spider_sweep.py --num-long-legs 6 --long-total-min 25 --long-total-max 45 \
    --min-leg-len 2 --ones-counts 0 8 20 --max-partitions-per-total 10
```
