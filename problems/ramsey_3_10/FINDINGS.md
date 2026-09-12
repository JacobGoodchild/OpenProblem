# The Ramsey Number R(3,10)

**Source:** classical Ramsey theory; current bounds tracked in Stanisław
Radziszowski's dynamic survey "Small Ramsey Numbers" (Electronic Journal of
Combinatorics, DS1). **Status as of this writing (Sept 2026): genuinely
open.** `40 <= R(3,10) <= 41` — the lower bound comes from an explicit
39-vertex witness graph, the upper bound of 41 from a large 2024
computer-assisted proof (down from a long-standing 42). The exact value is
unknown; it's one of the smallest Ramsey numbers still unresolved.

**This write-up is different from the previous two in this repo.** For
friendly partitions and Tuza's conjecture, most of the value came from
throwing search at a problem more or less blind. Here, we did the research
first: R(3,k) is a 40-year, heavily-mined problem with recent papers
(2024-2026) reporting multi-CPU-year efforts on this exact question. We
are not going to out-compute a dedicated research group's custom C tooling
in a few hours. So the actual computational contribution here is narrow
and honest: **exhaustively rule out one entire, well-defined construction
family** (circulant graphs) for the specific open case n=40, rather than
attempt the unrestricted (and effectively hopeless at this scale) general
search.

## The problem, in plain English

`R(3,k)` is the smallest number of people `N` such that at any party of
`N` people, either three of them all know each other (a triangle), or `k`
of them are all total strangers to each other (an independent set of size
`k`). Equivalently: the smallest `N` such that *every* triangle-free graph
on `N` vertices is forced to contain an independent set of size `k`.

To prove `R(3,k) > n` (i.e. push the *lower* bound up), you just need to
*exhibit one* triangle-free graph on `n` vertices whose largest
independent set has fewer than `k` vertices — a single concrete
counterexample settles it. For `R(3,10)`, finding a triangle-free graph on
**40** vertices with independence number `<= 9` would prove `R(3,10) >= 41`,
which combined with the already-published upper bound `R(3,10) <= 41`
would pin the value down **exactly** to 41.

## What we did

1. **Circulant graph construction.** Rather than search the astronomically
   large space of all graphs on 40 vertices, we restricted to *circulant*
   (Cayley) graphs on `Z_40`: pick a "connection set" `S ⊆ {1,...,20}`,
   and connect vertices `i,j` whenever `(i-j) mod 40` or its negative is in
   `S`. This is not a novel idea — essentially all of the best-known small
   `R(3,k)` lower-bound constructions in the literature are circulant or
   close to it — but it turns an intractable search into a genuinely
   exhaustive one: `2^20 = 1,048,576` possible connection sets, versus
   `2^780` possible graphs on 40 vertices.
2. **Fast triangle-free filter.** A circulant graph is triangle-free iff no
   three elements of the (signed, symmetric) connection set sum to zero
   mod 40 — a simple `O(|S|^2)` arithmetic check, not a graph traversal.
   This let us check *all 1,048,575* connection sets in **2.6 seconds**.
3. **Exact ILP independence-number oracle.** For each triangle-free
   survivor, we ask (via integer programming, `pulp`+CBC): does an
   independent set of size `>= 10` exist? This is a feasibility query, not
   full optimization, which resolves faster since the solver only needs a
   witness or a proof of infeasibility, not the exact optimum.
4. **Method validated against known ground truth first.** Before touching
   the open n=40 case, we ran the identical method on n=35 (where
   `R(3,9)=36` is already known, so a valid witness graph is known to
   exist) and it found one in under a minute (`S = {1,7,11,16}`), confirming
   the pipeline is correct before trusting a negative result on the open
   case.

## Results

- **All 1,048,575 non-empty connection sets on `Z_40` were checked.**
  4,522 are triangle-free.
- **All 4,522 triangle-free circulant graphs were verified via exact ILP**
  to have independence number `>= 10` — **none achieves the target `<= 9`.**
  Every single check resolved decisively (zero solver timeouts / zero
  inconclusive cases), so this is a complete, airtight result for this
  construction family, not a partial or heuristic one.
- A follow-up random sample of 1,000 of the 4,522 candidates, computing
  the *exact* independence number (not just "is it >= 10"), found a
  minimum of **10** (mean across the sample: 15.2, max: 20 — the densest
  "all-odd-difference" candidates are literally complete bipartite graphs
  `K_{20,20}`, triangle-free but with independence number exactly 20, the
  worst possible). At least two distinct connection sets in the sample
  (e.g. `S={3,4,9,15,17}`) achieve independence number **exactly 10** —
  one vertex short of the target 9. This is a genuine near-miss, not a
  family that's structurally hopeless: circulant graphs on 40 vertices get
  right up to the boundary of proving `R(3,10)=41`, just not across it.

## Honest conclusion

**We did not resolve `R(3,10)`.** What we established, rigorously and
completely: **no circulant graph on 40 vertices proves `R(3,10) >= 41`.**
This is a real (if narrow) negative result — it rules out an entire,
well-established construction technique for this specific open question,
with a complete search (not a sample) and zero ambiguity in the outcome.

This does *not* mean `R(3,10) = 40` is settled — a non-circulant
construction on 40 vertices might still exist (most graphs are not
circulant; symmetry helps minimize independence number for a given edge
count, but isn't guaranteed to be optimal), and determining which
possibility is true is exactly the open research question that has
resisted a dedicated multi-CPU-year computational effort already. What we
can say is that if a 40-vertex witness exists, it is *not* vertex-transitive
under the cyclic group — future computational attacks on this specific
question should look at other symmetry groups (e.g. Cayley graphs on
`Z_2 x Z_20`, `Z_4 x Z_10`, `Z_5 x Z_8`, dihedral groups) or abandon
symmetry assumptions entirely (which reopens the intractability problem
this whole approach was designed to avoid).

**What would move this forward:** (a) repeat this exact method for other
abelian groups of order 40 (there are several, and each has its own
tractable-sized connection-set space); (b) try "twisted"/non-abelian
Cayley graphs (dihedral `D_20`); (c) since we now know the *exact* minimum
independence number achieved by the circulant family is close to (not far
from) the target, a local search that starts from the best circulant
graph and makes small *non-circulant* perturbations (breaking symmetry
slightly) might close the remaining gap — this is a natural next
experiment we did not have time to run in this session, per the "keep
rotating problems" discipline for this project.

## Reproducing

```
cd problems/ramsey_3_10
python3 validate_known.py           # sanity check against known R(3,9)=36 (finds a witness on n=35)
python3 enumerate_candidates.py     # phase 1: fast triangle-free filter, all 2^20 connection sets on Z_40
python3 verify_candidates.py        # phase 2: parallel ILP verification of all triangle-free survivors
python3 exact_alpha_sample.py       # characterizes how close the family gets (exact independence numbers)
```
