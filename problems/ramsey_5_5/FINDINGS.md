# The Ramsey Number R(5,5)

**Source:** classical Ramsey theory — one of the most famous open problems
in the field (sometimes called Erdős's "$100 problem" for the closely
related gap-closing question). **Status: genuinely open.** Published
bounds, confirmed via multiple 2024-2025 sources: `43 <= R(5,5) <= 46`
(lower bound: Exoo, 1989; upper bound: Angeltveit & McKay, 2024, improving
an earlier bound of 48). By multiple accounts, "a lot of computer
resources have been expended in an unsuccessful attempt" to push the
lower bound past 43 since 1989 — this is a problem that has resisted
dedicated, specialist computational effort for over three decades.

## The problem, in plain English

`R(5,5)` is the smallest `N` such that every 2-coloring of the edges of
`K_N` contains a monochromatic `K5` (5 vertices all connected to each
other in the same color). To push the lower bound up, exhibit a
2-coloring of `K_n` where neither color contains a `K5`. The current
record witness is on 42 vertices, giving `R(5,5) >= 43`; nobody has found
one on 43+ vertices despite heavy effort, and nobody has proved one can't
exist below 46.

## Honest scoping, stated up front

Exoo's actual record construction is **not a pure circulant graph** — it's
built from `Cyclic(43)` with one vertex deleted and some edges
recolored, which breaks the full rotational symmetry. This project's
tooling (`lib/circulant_ramsey.py`, `lib/multicolor_circulant.py`) only
searches **pure circulant** 2-colorings. So this search does not attempt
to reproduce or extend Exoo's exact construction — it answers a
narrower, well-defined question instead: **how far can a purely
circulant construction push a (K5,K5)-avoiding witness, using the same
local-search method already validated on R(3,3,5)?**

## What we did

1. **Validated the clique-free checker** against the classical circulant
   witness for `R(4,4)=18`: the Paley graph on 17 vertices (quadratic
   residues mod 17), which is self-complementary and `K4`-free — a
   real, citable circulant Ramsey construction, not an invented sanity
   check. Reproduced exactly (`validate_known.py`).
2. **Reused `lib/multicolor_circulant.py` with `r=2`, both colors
   forbidding `K5`** — no new library code needed, since a 2-coloring of
   `K_n` is just a graph and its complement, and the complement of a
   circulant graph is itself circulant.
3. **Swept `n=20` through `45`**, 20-25 seconds per `n`, local search
   (greedy recoloring + noise + periodic restarts) looking for the
   largest achievable pure-circulant `(K5,K5)`-avoiding witness.

## Results

| n | result |
|---|--------|
| 20-38 | found valid witnesses (fast, mostly instant to a few seconds) |
| 39 | not found in 21.3s |
| 40-41 | found — color sizes `[10,10]` at both |
| **42-45** | **not found** (4 consecutive misses, 20-22s each) |

The witness at **n=41** (`{4,6,7,9,10,11,12,14,18,20}` /
`{1,2,3,5,8,13,15,16,17,19}` as the two difference-set halves) was
independently re-verified from scratch using `networkx.find_cliques`
(not our own `is_clique_free` function) — confirmed both color classes
have max clique size exactly 4.

## Honest conclusion

**This does not improve, match, or meaningfully challenge the published
record.** The known lower bound (`R(5,5) >= 43`, from a 42-vertex
witness) is one better than what pure circulant search here reached
(`n=41`), and the actual open question — whether a 43+-vertex witness
exists at all, pure circulant or otherwise — is untouched: our search
found *nothing* at n=42 through 45, which is not evidence either way,
just this particular search's limit. Given that decades of dedicated
computational effort by specialists in the field have already failed to
find such a witness by any construction, it would have been a
near-miracle for a basic local search built in under an hour to succeed
where they didn't — and it didn't.

What this run *does* establish, honestly: a clean, independently-verified
`R(5,5) >= 41+1 = 42`-style data point via pure circulant construction
(weaker than the known bound, since 41 < 42), confirming the tooling
generalizes correctly to this problem, and a believable "ceiling" signal
(4 consecutive misses right after the last success) suggesting pure
circulant constructions specifically are unlikely to reach 42 vertices
at all, let alone surpass the known record — consistent with why the
real record construction had to break full circulant symmetry in the
first place.

**What would move this forward:** near-circulant constructions (a
circulant graph plus a small number of vertex deletions/edge repairs,
matching Exoo's actual technique) rather than pure circulant ones; or a
proper simulated-annealing schedule instead of greedy + noise, which is
a fairly basic local search as implemented here.

## Reproducing

```
cd problems/ramsey_5_5
python3 validate_known.py
python3 search.py --start 20 --stop 45 --time-per-n 20
```
