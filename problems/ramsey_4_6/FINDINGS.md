# The Ramsey Number R(4,6)

**Source:** classical Ramsey theory; current bounds from Geoffrey Exoo's
literature. **Status: genuinely open.** `36 <= R(4,6) <= 41`. Per multiple
independent sources, R(4,6) and R(3,10) are described as the two smallest
currently-unknown classical two-color Ramsey numbers.

This uses the exact same methodology as `problems/ramsey_3_10/` in this
repo, generalized from "triangle-free" (`K3`-free) to `K4`-free, and
applied to a different specific open value — a natural extension once the
circulant-graph technique was built and validated, rather than a
from-scratch reinvention.

## The problem, in plain English

`R(4,6)` is the smallest `N` such that every graph on `N` vertices
contains either a clique of 4 mutually-connected vertices, or an
independent set of 6 mutually-*disconnected* vertices. To push the lower
bound up, exhibit one graph on `N` vertices that is `K4`-free (no 4-clique)
*and* has independence number `<=5` (no 6 mutually-disconnected
vertices). Finding such a graph on **36** vertices would prove
`R(4,6) >= 37`, improving on the published record of 36 (Exoo).

## What we did

1. **Generalized the circulant-graph technique** from `lib/circulant_ramsey.py`
   (built for R(3,10)'s triangle-free check) to an arbitrary `K_s`-free
   check via backtracking over the connection-set's "difference graph"
   (looking for `s-1` mutually-related elements, which by vertex-
   transitivity means a `K_s` exists in the full graph). **Validated
   against `networkx`'s exact clique-number computation** with zero
   mismatches across hundreds of random test cases, for both `s=3`
   (matching the original triangle check exactly) and `s=4`.
2. **Validated the full pipeline** by reproducing the *already known*
   `R(4,5)=25`: found a `K4`-free circulant witness on 24 vertices with
   independence number `<=4` in 2 seconds (`S={1,2,4,8,9}`).
3. **The actual attack:** exhaustively enumerated all `2^18 = 262,144`
   circulant connection sets on `Z_36`, found 17,858 that are `K4`-free,
   then verified each one's independence number via exact ILP
   (feasibility check: does an independent set of size `>=6` exist?).

## Results

- **All 262,144 connection sets checked** (2.2 seconds — the `K4`-free
  arithmetic filter is fast).
- **All 17,858 `K4`-free candidates verified via exact ILP** (972 seconds,
  parallelized across 4 cores) — **every single check resolved
  decisively, zero solver timeouts.**
- **None achieves independence number `<=5`.** This is a complete,
  airtight negative result for the circulant construction family at
  `n=36` — not a sample, not a heuristic search that gave up, an
  exhaustive check of the entire restricted search space with a
  guaranteed-conclusive answer on every single candidate.
- **How close did it get?** A follow-up random sample of 300 of the
  17,858 candidates, computing the *exact* independence number, found a
  minimum of **6** (one off the target of 5), e.g.
  `S={1,4,6,11,14,15}` — mean across the sample was 10.2, max 18. Just
  like the R(3,10) circulant search, this is a genuine near-miss: the
  construction family gets right up to the boundary, not nowhere close.

## Honest conclusion

**We did not resolve R(4,6).** What we established, rigorously and
completely: **no circulant graph on 36 vertices proves `R(4,6) >= 37`.**
This rules out an entire well-established construction technique for this
specific open value, with a complete search (not a sample) and zero
ambiguity in every individual outcome.

This does not mean `R(4,6)=36` is settled — a non-circulant construction
on 36 vertices might still exist. What we can say is that if a 36-vertex
witness exists, it is not vertex-transitive under the cyclic group. Same
as the R(3,10) write-up: future attempts on this specific question should
look at other symmetry groups of order 36 (there are several: `Z_2 x
Z_18`, `Z_3 x Z_12`, `Z_4 x Z_9`, `Z_6 x Z_6`, dihedral `D_18`, etc.) or
try small non-circulant perturbations starting from the best
near-miss graphs found here (independence number 6, one off target).

**What would move this forward:** (a) repeat this exact method for other
groups of order 36; (b) a local search seeded at the alpha=6 near-misses,
perturbing edges slightly (breaking the circulant symmetry a little) to
see if the independence number can be pushed down to 5 without
introducing a `K4`; (c) the same experiment one level up — for `n=37,
38,...` — although the circulant connection-set space doubles with every
2 added to `n`, so this gets more expensive quickly (n=38's `2^19` space
is still tractable, `n=44`'s `2^22` starts to become a multi-hour
undertaking for the ILP-verification phase at this problem's rate).

## Reproducing

```
cd problems/ramsey_4_6
python3 validate_known.py    # sanity check: reproduces R(4,5)=25 on n=24
python3 search_n36.py        # phase 1: fast K4-free filter, all 2^18 connection sets on Z_36
python3 verify_candidates.py # phase 2: parallel ILP verification of all K4-free survivors
```
