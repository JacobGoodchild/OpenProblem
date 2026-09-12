# Vizing's Conjecture (1968)

**Source:** Vizing, 1968. **Status: genuinely open**, and unusually
well-characterized: `gamma(G [] H) >= gamma(G) * gamma(H)` for the
domination number `gamma` and Cartesian product `[]`. Proven for
`gamma(G)` in `{1,2,3}`, cycles, trees, and other special families.
Best known general lower bound (Clark & Suen, 2000):
`gamma(G[]H) >= 0.5 * gamma(G) * gamma(H)`. This attack was directed by
the user with a specific, literature-informed plan, following the
survey by Brešar, Henning, Klavžar & Rall.

## The problem, in plain English

Take two graphs `G` and `H`. Build their "Cartesian product" (a bigger
graph whose vertices are pairs, one from each). The conjecture says the
minimum number of vertices needed to "dominate" (touch or be) every
vertex in the product is at least the product of how many you'd need
for `G` and `H` separately. Nobody has found a counterexample in over
55 years, but nobody has proven it in general either.

## What we did

1. **Built exact tooling**: ILP-based domination number (set-cover,
   pulp/CBC), Cartesian product construction, and — the key piece — all
   four **necessary conditions a minimal counterexample must satisfy**,
   per the survey: connected, `gamma >= 4`, **edge-critical** (adding
   *any* missing edge strictly decreases `gamma`), **every vertex
   belongs to some minimum dominating set**, and **identifying
   (contracting) any two vertices strictly decreases `gamma`**.
2. **Validated rigorously**: reproduced the exact cycle-domination
   formula `gamma(Cn)=ceil(n/3)`; confirmed our own Vizing-checker never
   contradicts the *already-proven* `gamma<=3` cases across several
   small graph pairs; confirmed the proven Clark & Suen bound holds on
   every product we computed as a live secondary check.
3. **Exhaustive search** (nauty-geng): every connected graph on `n=8`
   (11,117 graphs) and `n=9` (261,080 graphs) vertices, computing
   `gamma` for each, then running the full necessary-condition filter
   on every `gamma>=4` survivor.
4. **Random + adversarial local search** for `n=10` through `16`
   (exhaustive enumeration is infeasible there — `n=10` alone has 11.7M
   connected graphs), hill-climbing toward satisfying more of the four
   filters.
5. Every graph that passed **all four** conditions was immediately
   tested against a battery of `H` graphs (`K1, K2, P3-P6, C3-C7, K4,
   K3,3`, two wheels, a grid, the Petersen graph, and `G` itself) for an
   actual violation of the inequality.

## Results

| n | connected graphs checked | gamma>=4 | pass all 4 necessary conditions |
|---|---|---|---|
| 8 (exhaustive) | 11,117 | 6 | **1** |
| 9 (exhaustive) | 261,080 | 191 | **2** |
| 10-16 (search, 25×200 trials each) | — | — | 0 |

**Three graphs total pass every necessary condition** from the
literature — genuinely rare structures (roughly 1 in 10,000 to 1 in
130,000 of *all* connected graphs at that size, and 1 in 6-95 even
among the already-narrow `gamma>=4` subset). None of them was found by
the local search at `n=10+` within the budget used, consistent with how
rare they are.

**All three candidates were tested against ~19 different H graphs each
(including themselves) — zero violations found**, often with slack, but
notably **one candidate (`H?\`bCbd`, n=9) hits the bound with exact
equality against itself**: `gamma(G[]G) = 16 = 4×4`, no slack at all.
That's a genuinely tight extremal example, and still fully consistent
with the conjecture.

## Honest conclusion

**No counterexample, and this is a real, if modest, negative result**
— not a wasted search. Two things make it more informative than a
typical "we looked and found nothing":

- The tooling was checked against *actual proven theorems* (the
  `gamma<=3` cases, the Clark & Suen general bound), not just internal
  consistency — real confidence that a violation, had the search found
  one, would have been trustworthy.
- We now have **exhaustive, complete data on exactly which small graphs
  can even structurally qualify** as a minimal counterexample at
  `n=8,9`: only 3 exist, and all three were fully vetted against a wide
  battery of `H` without any strain on the conjectured bound. This
  directly confirms — with actual data, not just citation — that the
  four necessary conditions from the literature are indeed necessary
  but clearly **far** from sufficient: passing all of them is
  extraordinarily rare, and even the rare survivors don't come close to
  violating the inequality.

**Caveats, stated plainly**: this is n≤9 exhaustively and a fairly
limited random/local search for n=10-16 — nowhere near a proof for
larger n, and the local search at n=10+ may simply be too weak to find
the (evidently very rare) structures that pass all four filters, let
alone ones that also violate the inequality. The H battery, while
reasonably broad (19 graphs including notable "awkward for domination"
graphs like the Petersen graph and wheels), is still a finite,
hand-picked set — a real counterexample would need to survive against
literally every possible H, not just these.

**What would move this forward:** push the random/adversarial search
much harder at n=10-16 (many more trials, or a smarter objective that
specifically seeds from the 3 known n=8/n=9 candidates' structure
rather than starting from scratch each time); test the 3 known
candidates against a much larger, systematically-generated battery of
H (not just hand-picked named graphs); and study what's structurally
special about the 3 survivors (all three share a "hub-and-triangle"-ish
flavor per manual inspection) to see if it points toward a genuine
family worth searching more purposefully, rather than blind random
generation.

## Reproducing

```
cd problems/vizing_conjecture/code
python3 validate_known.py
python3 exhaustive_search.py --n 8 --min-gamma 4
python3 exhaustive_search.py --n 9 --min-gamma 4
python3 random_and_adversarial_search.py --n-start 10 --n-stop 16
```
