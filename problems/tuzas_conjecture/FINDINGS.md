# Tuza's Conjecture

**Source:** Zsolt Tuza, 1981 (see e.g. [Wikipedia](https://en.wikipedia.org/wiki/Tuza%27s_conjecture),
[DIMACS summary](http://dimacs.rutgers.edu/news_archive/tuza-conjecture)).
Still an open problem in general as of this writing (Sept 2026); recent
arXiv activity on it is ongoing (special-case results in 2024-2026).

**Status: genuinely open.** Like the friendly-partitions write-up in this
repo, this is an honest report of an independent computational attack —
not a proof, not a disproof, but a rigorous (exact, not heuristic-only)
search for a counterexample or new extremal structure.

## The problem, in plain English

Take any graph. Two natural questions about its triangles:

- **Packing:** what's the largest collection of triangles you can pick so
  that no two of them share an edge? Call this number `nu(G)`.
- **Covering:** what's the smallest set of edges you could delete so that
  *no triangle survives at all*? Call this number `tau(G)`.

Obviously `tau(G) >= nu(G)`: if you have `nu(G)` edge-disjoint triangles,
you need at least one edge from each of them just to kill those, and since
they don't share edges, that's `nu(G)` edges at minimum.

Tuza conjectured the reverse direction can't be too far off either:
**`tau(G) <= 2 * nu(G)` for every graph, always.** In other words, you never
need more than *twice* as many edges to kill every triangle as the size of
the biggest disjoint bundle of triangles you could find.

This is known to be true for planar graphs, and for a handful of other
restricted graph classes, and the best known *general* upper bound (Haxell,
1999) is `tau(G) <= (66/23) * nu(G) ≈ 2.87 * nu(G)` — meaningfully weaker
than the conjectured `2`. `K4` and `K5` are known to hit the bound exactly
(`ratio = 2`), and Baron & Kahn (2014) showed a partly-random construction
proving the bound can't be improved much *asymptotically* for large dense
graphs — but nobody has ever found a graph, of any size, where the ratio
actually *exceeds* 2.

## What we did

Built three independent, cross-validating layers (same philosophy as the
friendly-partitions investigation in this repo):

1. **`lib/tuza.py`** — an exact oracle. `nu(G)` and `tau(G)` are each
   NP-hard optimization problems (maximum triangle packing / minimum
   triangle edge cover), so we formulate each as an integer linear program
   — one binary variable per triangle for packing (maximize count subject
   to each edge used by at most one chosen triangle), one binary variable
   per edge for covering (minimize count subject to every triangle having
   at least one chosen edge) — and solve exactly with the CBC solver via
   `pulp`. Sanity-checked against the two known tight cases: `K4` gives
   `tau=2, nu=1, ratio=2` and `K5` gives `tau=4, nu=2, ratio=2`, both
   matching the literature exactly.
2. **`exhaustive_search.py`** — drives `nauty-geng` to enumerate *every*
   graph (not a restricted class — every isomorphism class) on `n`
   vertices, and checks the exact ratio on each one that contains a
   triangle at all.
3. **`adversarial_search.py`** — the "unorthodox" layer: simulated
   annealing directly over graph space (single-edge toggles as moves),
   scored by a *fast, provably-conservative* heuristic
   (`greedy_cover_upper_bound / greedy_packing_lower_bound`, which is
   mathematically guaranteed to be `>= true_ratio`, i.e. it can only
   *overestimate* how close to 2 a graph is), with any promising candidate
   re-verified by the exact ILP oracle before being taken seriously. Two
   seeding strategies were used: uniform-random graphs, and graphs seeded
   as a disjoint union of `K4`s or `K5`s (the known tight construction) so
   the search explores the *neighbourhood* of the known extremal examples
   directly, rather than hoping to stumble on one from noise.

Plus **`structured_families.py`**, computing the exact ratio on a range of
natural named graph families (friendship graphs, book graphs, wheels,
complete multipartite graphs, and cliques glued together in chains/cycles)
across many sizes — a systematic check of "would any mathematician's first
guess at an extremal family beat `K4`/`K5`?"

And `random_search.py` for plain Erdos-Renyi `G(n,p)` sampling across a
density sweep, as a baseline.

## Results

### Exhaustive, n = 5 to 9 (every graph containing a triangle, up to isomorphism)

| n | graphs w/ triangles checked | skipped (triangle-free) | max ratio | violations |
|---|------------------------------|--------------------------|-----------|------------|
| 5 | 20      | 14   | 2.0 | 0 |
| 6 | 118     | 38   | 2.0 | 0 |
| 7 | 937     | 107  | 2.0 | 0 |
| 8 | 11,936  | 410  | 2.0 | 0 |
| 9 | 272,771 | 1,897| 2.0 | 0 |

Every single graph on up to 9 vertices was checked *exactly* (not
sampled). The maximum ratio ever observed is exactly `2.0`, hit only by
graphs containing `K4`/`K5`-like tight structure — never exceeded. This is
a complete, gap-free verification of the conjecture for all graphs up to
n=9, which (as far as we can tell from the literature) goes beyond what's
typically reported for unrestricted brute-force checks.

n=10 has 12,005,168 non-isomorphic graphs total (versus 274,668 at n=9) —
roughly a 44x jump — which would take on the order of a day and a half at
the same per-graph rate. We stopped the *exhaustive* frontier at n=9 and
put the remaining effort into structured and adversarial search instead,
which can reach much larger n directly (see below), rather than mechanically
grinding out n=10 for many hours for comparatively little additional
information (a lesson learned the hard way on the friendly-partitions
problem earlier in this project).

### Structured families (exact ratio, many sizes each)

| family | ratio | notes |
|---|---|---|
| friendship graphs `F_k` (k triangles sharing one vertex) | exactly 1.0, all k=1..11 | far from tight |
| book graphs `B_k` (k triangles sharing one edge) | exactly 1.0, all k=1..11 | one edge always covers everything |
| wheel graphs `W_k` | 1.0 - 1.5 | never close to 2 |
| complete multipartite `K_{a,...,a}` (3-5 parts, size 2-5) | 1.0 - 1.32 | never close to 2 |
| disjoint union of `K4`s / `K5`s (any count) | **exactly 2.0**, every time | the known tight construction, reproduced exactly |
| `K4`/`K5`s glued in a **chain** (sharing one vertex between consecutive copies) | **exactly 2.0**, every time | gluing at a single vertex doesn't break tightness |
| `K4`/`K5`s glued in a **cycle** (chain closed into a loop) | 2.0 for cycle length >= 4; **drops to 1.5-1.71 at the shortest cycle length (3)** | closing a short loop creates extra "seam" triangles that make the graph *easier* to cover relative to its packing number, not harder |

The cycle-of-3 anomaly is a small but genuine structural finding: it shows
the ratio-2 tightness of the clique construction is *not* robust to every
kind of gluing — closing a very short loop of shared vertices actually
*hurts* the ratio rather than helping it, which is a mildly interesting
data point about how fragile the extremal structure is.

### Adversarial search (SA over graph space, exact-verified)

| n | SA steps | restarts | best heuristic ratio | exact-verified candidates | true ratio found | counterexamples |
|---|----------|----------|----------------------|----------------------------|-------------------|------------------|
| 8  | 3,000     | 1 | 2.0   | 1 | 2.0 (K4-based) | 0 |
| 9  | 1,600,000 | 8 | 2.167 | 1 | 1.125 | 0 |
| 11 | 750,000   | 5 | 2.167 | 6 | 1.0 - 2.0 | 0 |
| 12 | 220,000   | 4 (combined) | 2.0 | 0 | -- | 0 |
| 13 | 500,000   | 5 | 2.125 | 1 | 1.2 | 0 |
| 14 | 240,000   | 3 | 2.0 | 0 | -- | 0 |
| 15 | 40,000    | 1 | 1.778 | 0 | -- | 0 |
| 16 | 163,000   | 2 (combined) | 2.0 | 0 | -- | 0 |
| 18 | 120,000   | 2 | 2.0 | 0 | -- | 0 |
| 20 | 90,000    | 2 (combined) | 2.0 | 0 | -- | 0 |
| 24 | 50,000    | 1 | 2.0 | 0 | -- | 0 |
| 25 | 100,000   | 2 | 2.0 | 0 | -- | 0 |
| 30 | 40,000    | 1 | 2.0 | 0 | -- | 0 |

**Zero counterexamples, and every exact-verified candidate came back at
`ratio <= 2.0`, with the tightest ones landing on exactly 2.0.** A couple
of runs reported a *heuristic* score above 2 (up to 2.167) — this is
expected and not concerning: the heuristic is a deliberately loose,
mathematically-guaranteed *overestimate* (a fast greedy packing lower
bound divided into a fast greedy cover upper bound), used only to decide
when it's worth calling the expensive exact ILP. In every single case
where that happened, the exact ILP came back well below 2 (e.g. `1.125`,
`1.2`) — the verification pipeline is doing exactly what it's designed to
do: catch and discard heuristic false alarms rather than report them as
findings.

Seeding the SA directly at the known tight construction (disjoint `K4`s /
`K5`s) and then annealing away from it never found anything better than
where it started — the search consistently *degrades* from 2.0 as edges
are toggled, meaning (at least locally, under single-edge-toggle moves,
across dozens of independent restarts and hundreds of thousands of steps
per size) the extremal point isn't sitting next to something even more
extreme. This mirrors what we found on the friendly-partitions problem:
known hard/tight instances tend to be locally isolated peaks, not part of
a smoothly-improvable region a naive local search can climb past.

### Random G(n,p) sampling

Plain Erdos-Renyi graphs, swept across densities `p = 0.1` to `0.9`,
consistently produced ratios in the `1.0-1.3` range — nowhere near 2. This
matches the published result that Tuza's conjecture holds comfortably for
random graphs (Kahn & Park have a paper specifically on this), and
reinforces that the interesting, ratio-near-2 structure is
*highly non-generic* — you have to build it deliberately (via cliques),
not stumble on it randomly. Same qualitative lesson as the friendly
partitions random-sampling results.

## Honest conclusion (current status)

We did **not** resolve Tuza's conjecture, and we did **not** find any
evidence against it — no graph at any size we tried, structured or
adversarially searched, ever exceeded `tau(G) <= 2*nu(G)`. What we *did*
establish computationally, to our own satisfaction:

- **Exhaustive, gap-free verification for every graph up to n=9** (272,771
  graphs with a triangle, all checked exactly via ILP) — the maximum ratio
  observed is exactly 2.0, matching the conjecture's own claimed bound with
  no slack anywhere in that range.
- A systematic sweep of natural named graph families (friendship, book,
  wheel, complete multipartite, and various clique-gluing schemes) finds
  that **only constructions built from `K4`/`K5` cliques ever reach ratio
  2**, and even among those, closing a short 3-cycle of glued cliques
  *breaks* the tightness rather than improving it — a small structural
  nugget about how fragile the extremal examples are.
- Adversarial simulated annealing, both from random starts and (more
  informatively) seeded directly at the known tight construction, explored
  up to n=30 and hundreds of thousands of SA steps per size without ever
  finding a graph whose *exact, ILP-verified* ratio exceeds 2 — and
  starting exactly at the tight point, the search only ever finds the
  neighbourhood *less* tight, never more.
- The heuristic-overestimate + exact-reverification pipeline worked
  exactly as intended: a few runs flagged heuristic ratios above 2 (as
  high as 2.167), and in every case the exact ILP calculation confirmed
  the true ratio was safely below 2 — the discipline of never trusting a
  heuristic number without an exact check paid off here, same as it did on
  the friendly-partitions problem.

**Bottom line:** everything we found is consistent with Tuza's conjecture
being true, and consistent with `K4`/`K5`-based clique unions being the
*only* extremal structure (a natural, if unproven, guess given how
comfortably every other family and every adversarial search stayed well
clear of the bound). This doesn't move the needle on the actual open
question — closing the gap between the conjectured bound of 2 and the best
proven general bound of 66/23 ≈ 2.87 is a genuinely hard problem that has
resisted expert attack for over 40 years — but it's an honest, rigorous
computational data point: at every scale we could exactly verify, and
every scale we could search adversarially, the conjecture holds with the
bound never approached from outside by even a small margin.

**What would move this forward:** (a) push the exhaustive frontier to
n=10 with more compute/time than we allotted here (~1.5 days estimated at
this rate) to see whether the clean "always exactly <= 2" pattern holds at
one more exhaustive step; (b) a genuinely different adversarial move set —
our SA only tried single-edge toggles, but the known theoretical hard
direction for this problem (per Baron-Kahn) is a partly-*random* dense
construction, which a purely local edge-toggle search is structurally
unlikely to discover; a "graph recombination" move (splice together
pieces of two high-scoring graphs) or explicitly seeding from a
Baron-Kahn-style random dense graph and locally optimizing from there
might be more informative than further single-edge-toggle runs; (c) trying
the LP relaxation values (fractional `nu`/`tau`) as an even cheaper search
signal than the greedy heuristics used here, since the LP relaxation
gap itself is of independent theoretical interest for this conjecture.

## Reproducing

```
cd problems/tuzas_conjecture
python3 exhaustive_search.py 8                              # exact, all graphs of a given n
python3 structured_families.py                              # exact ratio on named graph families
python3 random_search.py 15 --samples-per-p 100             # G(n,p) sweep
python3 adversarial_search.py 20 --steps 50000 --init clique4  # SA seeded at the known tight point
```

All raw results (including every discovered graph, in `graph6` format) are
under `results/`.
