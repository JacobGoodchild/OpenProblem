# The Classical Multicolor Ramsey Number R(4,4,4)

**Source:** classical Ramsey theory. **Status: genuinely open, and
actively being worked on** — a 2026 preprint ("New Upper Bounds for the
Classical Ramsey Numbers R(4,4,4), R(3,4,5) and R(3,3,6)") improved the
upper bound to `R(4,4,4) <= 229`. Published bounds: `128 <= R(4,4,4) <=
229`. The lower bound comes from a classical construction by Hill and
Irving (the "`G_127`" graph); nothing has beaten it since.

## The problem, in plain English

`R(4,4,4)` is the smallest `N` such that every 3-coloring of the edges
of `K_N` contains a monochromatic `K4`. To push the lower bound,
exhibit a 3-coloring of `K_n` where all three colors are `K4`-free. The
known record is on 127 vertices.

## What we did — and this is the interesting part

1. **Reproduced the real record from first principles**, not a generic
   sanity check. `127` is prime and `126 = 3 x 42`, so `Z_127^*` has a
   subgroup of index 3 (the cubic residues, 42 elements). We checked
   computationally that `-1` **is** a cubic residue mod 127, which
   means the 3 cosets of this subgroup are each closed under negation
   — exactly the condition needed to use them directly as "distance
   classes" for a 3-coloring of the circulant graph on `Z_127` (this is
   the standard cyclotomic-coloring technique). We built this coloring
   from scratch (`validate_known.py`) and confirmed: **all three cosets
   give `K4`-free circulant graphs** — i.e., we independently
   reconstructed Hill & Irving's actual published witness via number
   theory, not by searching for it. This is a stronger validation than
   the generic sanity checks used elsewhere in this project (e.g. the
   Paley(17) check for R(5,5)) because it *is* the literature's real
   construction, confirming the record is indeed cyclotomic/circulant.
2. **Searched the right space for a larger witness**
   (`search_cyclotomic.py`): rather than generic local search over
   arbitrary partitions (which this project's R(3,3,3,3) attempt showed
   has no bias toward finding algebraic structure like this), we
   searched *exactly* the family the real record comes from — every
   prime `p > 127` with `p = 1 (mod 3)` and `-1` a cubic residue mod
   `p`, checking whether its 3 cyclotomic cosets are simultaneously
   `K4`-free.

## Results

**Checked all 1,110 eligible primes from 128 to 20,000** (a range over
**150x** larger than the actual record) in 5.4 seconds — this is a fast
arithmetic check, not a heuristic search, so this coverage is complete
and exhaustive, not partial. **Zero** gave a `(K4,K4,K4)`-free
cyclotomic coloring.

## Honest conclusion

**This does not improve on the published record**, but it is a
genuinely different kind of result than most of this project's other
Ramsey write-ups: it's a **complete, exhaustive negative result within
a well-motivated, literature-grounded search space** (not a partial or
heuristic one). We can say with confidence: *no other prime up to
20,000 admits an analogous cubic-residue cyclotomic (K4,K4,K4)-free
coloring* — `p=127` looks like an isolated, special case for this exact
construction recipe, not one member of a larger family we just haven't
searched far enough into.

This is useful negative information (it rules out the simplest possible
way to extend the record), but it does **not** touch the actual open
question, since there are other algebraic recipes not tried here:
higher-index cyclotomic classes (e.g. index-6 partitions combined
pairwise into 3 colors), composite or prime-power moduli, or entirely
non-circulant constructions.

**What would move this forward:** try index-6 (or other) cyclotomic
partitions grouped into 3 colors in different ways; try prime powers
`p^k` (not just primes) as the modulus; or abandon the cyclotomic
restriction and try a smarter structured local search that's still
narrower than fully generic (e.g. restricting to affine-invariant
partitions).

## Reproducing

```
cd problems/ramsey_4_4_4
python3 validate_known.py
python3 search_cyclotomic.py --start 128 --stop 20000
```
