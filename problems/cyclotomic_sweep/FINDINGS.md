# Cyclotomic (Prime-Power-Residue) Construction Sweep Across Open Ramsey Numbers

**This isn't a single new open problem — it's a new *method* applied to
five open problems already attempted elsewhere in this project**
(R(5,5), R(6,6), R(3,11), R(5,6), R(3,3,3,3)), directly motivated by the
success of the R(4,4,4) attack: instead of generic local search over
arbitrary circulant partitions (fast per trial, but incomplete — it can
simply fail to find a witness that exists), search the much narrower,
literature-grounded family of **cyclotomic constructions**: for a prime
`p` with `r | (p-1)`, partition `Z_p^*` into `r` cosets of the index-`r`
subgroup (checking `-1` lands in the subgroup, so cosets are valid
"distance classes"). Checking one candidate is pure cheap arithmetic, so
this search can be **exhaustive** over a wide range of primes, not just
a sample — a fundamentally different, more rigorous kind of search than
the local search used elsewhere in this repo.

## What we did

1. Generalized the R(4,4,4)-specific code into `lib/cyclotomic_ramsey.py`
   (`search_cyclotomic_range(clique_sizes, p_min, p_max)`), validated
   against the known R(4,4,4) p=127 result.
2. Ran it exhaustively for **every eligible prime from the smallest
   sensible starting point up to 50,000** against 5 open targets whose
   generic local-search attempts (elsewhere in this repo) fell short of
   their known records.

## Results

| Target | published bounds | known record (n) | cyclotomic hits found (up to 50,000) | matches/beats record? |
|---|---|---|---|---|
| R(5,5) | [43,46] | 42 | 29, 37 | no |
| **R(6,6)** | **[102,160]** | **101** | 29, 37, 41, 53, 61, 73, 89, **101** | **YES — exact match** |
| R(3,11) | [47,50] | 46 | (none) | no |
| R(5,6) | [59,85] | 58 | 29, 37 | no |
| R(3,3,3,3) | [51,62] | 50 | 17, 41 | no |

**The R(6,6) hit at p=101 is a real finding, independently verified**
(via `networkx.find_cliques`, not just our own checker): the cosets are
exactly the **quadratic residues mod 101** (the classical Paley graph
construction, since `r=2` cyclotomic cosets are just QR/QNR). Both color
classes have max clique size 5 — confirmed `K6`-free — exactly
reproducing the known `R(6,6) >= 102` record. This is a genuine success
for this project: our earlier generic local search for R(6,6) only
reached `n=62` and completely failed to find anything close to the
actual record; this exhaustive, structured search found it directly,
confirming the hypothesis explicitly flagged in that write-up (that the
real record likely has algebraic structure a generic search has no bias
toward finding).

No witness beyond a target's known record was found for any of the 5
targets, up to prime 50,000 in every case.

## Honest conclusion

**No new lower bound was found for any of the 5 targets.** The one
genuine success here is methodological, not a new result: we
demonstrated that a cheap, exhaustive, literature-grounded search
(cyclotomic constructions) can succeed exactly where an expensive,
incomplete heuristic search (generic local search) fails — the R(6,6)
case is direct proof of this within this project's own prior work. That
said, this doesn't mean cyclotomic constructions are guaranteed to find
every known record: they found nothing matching or close to the actual
records for R(5,5) (42), R(3,11) (46), R(5,6) (58), or R(3,3,3,3) (50)
— consistent with our earlier documented suspicion that several of
those real constructions use *modified* circulant graphs (a base
circulant/cyclotomic graph plus small repairs — the Exoo pattern), not
pure cyclotomic ones.

**What would move this forward:** extend `cyclotomic_ramsey.py` to
search "cyclotomic-plus-repair" constructions (start from a cyclotomic
base and try small local modifications) for the 4 targets that didn't
match; or search prime *powers* (not just primes) as the modulus, which
covers a wider algebraic family (this is how some literature
constructions, e.g. those built over `GF(p^k)`, actually work).

## Reproducing

```
cd problems/cyclotomic_sweep
python3 sweep.py
```
