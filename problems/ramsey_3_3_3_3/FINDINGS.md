# The Classical Multicolor Ramsey Number R(3,3,3,3)

**Source:** classical Ramsey theory. **Status: genuinely open.**
Published bounds, consistent across multiple sources: `51 <= R(3,3,3,3)
<= 62`. The lower bound (Chung, 1973) is over **50 years old**. The
upper bound comes from a 100+-page proof (Kramer, 2006), who also
**conjectured the true value is 62** — meaning the consensus in the
field leans toward the *lower* bound being the one far from the truth,
which makes searching for a witness above n=50 a genuinely interesting
(if very unlikely to succeed) thing to try, not a settled dead end.

## The problem, in plain English

`R(3,3,3,3)` is the smallest `N` such that every 4-coloring of the edges
of `K_N` contains a monochromatic triangle in *some* color. To push the
lower bound, exhibit a 4-coloring of `K_n` where all four colors are
triangle-free. The known record is on 50 vertices.

## What we did

Reused `lib/multicolor_circulant.py` exactly as built for R(3,3,5),
just with `r=4` colors, all forbidding `K3` — no new code. Swept
`n=20` through `55` with the same local search (greedy recoloring +
noise + periodic restarts) used successfully in that earlier attempt.

## Results

| n | result |
|---|--------|
| 20-41 (with scattered misses at 21,24,27,30,33,36,39) | found valid witnesses when found |
| **41** | **last success** — color sizes `[5,4,6,5]` |
| **42-55** | **not found** (14 consecutive misses) |

The witness at **n=41** (difference sets `{4,9,14,15,20}`, `{6,7,10,11}`,
`{2,3,8,13,17,18}`, `{1,5,12,16,19}`) was independently re-verified from
scratch via `networkx.find_cliques` — all four color classes confirmed
triangle-free (max clique size 2).

## Honest conclusion

**This does not improve on, or match, the published record.** Pure
circulant search here reaches `n=41`, well short of the known 50-vertex
witness. The 14-consecutive-miss run from n=42 onward is a fairly clean
signal that this is close to this search method's practical ceiling —
consistent with the pattern seen throughout this project's Ramsey
attempts (R(5,5): reached 41 vs record 42; R(6,6): reached 62 vs record
101; here: reached 41 vs record 50).

One thing worth being honest about, though it's speculative: since
Chung's actual R(3,3,3,3)>=51 construction is a well-known circulant
construction on `Z_50` (partitioning nonzero residues via a
multiplicative-subgroup / cyclotomic-class structure specific to the
number 50's factorization), it is plausible that our generic local
search simply isn't finding *that specific* algebraic construction —
cyclotomic partitions are a much more structured, narrower search than
"any" partition of the difference set, and a naive local search has no
special bias toward number-theoretic structure like that. We didn't
build a cyclotomic-class-aware search in the time available for this
problem; that would be the natural next step rather than continuing to
throw more time at generic local search.

**What would move this forward:** (a) implement a cyclotomic-class-aware
search (partition `{1,...,25}` by the multiplicative structure of
`Z_50^*` or similar, rather than by arbitrary element) to actually have
a chance of reproducing or extending Chung's construction; (b) a proper
simulated-annealing schedule instead of greedy + noise.

## Reproducing

```
cd problems/ramsey_3_3_3_3
python3 search.py --start 20 --stop 55 --time-per-n 20
```
