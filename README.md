# Open Problem Exploration

This repository is a computational research log: pick genuinely **open**
(unsolved) problems from mathematical sources such as
[Open Problem Garden](https://www.openproblemgarden.org/), that are precise
enough to check by computer and not absurdly out of reach, then throw
unorthodox computational search at them — heuristic local search, simulated
annealing over the *space of graphs itself*, exact SAT solving as a
rigor-check — looking for a proof, a disproof, a counterexample, or at
least solid new empirical evidence one way or the other.

Every problem attempted gets its own folder under `problems/`, with:

- the code used to attack it,
- a `results/` folder of raw output (JSON logs, discovered graphs, etc.),
- a `FINDINGS.md` write-up in plain English of what was tried, what was
  found, and what (if anything) is new or noteworthy.

## Methodology, in plain terms

For a "does every graph in this family have property P" type conjecture,
the general playbook used here is:

1. **Exhaustive check for small cases.** Generate every non-isomorphic
   instance up to some size (using [nauty](https://pallini.di.uniroma1.it/)
   where applicable) and check each one exactly.
2. **Fast heuristic search** (local search / hill-climbing with random
   restarts and perturbation) to quickly find witnesses (e.g. a partition
   with the required property) for larger instances where exhaustive
   search is no longer possible.
3. **Exact SAT-based oracle** as a rigor check: whenever the heuristic
   fails to find a witness, hand the instance to a SAT solver, which gives
   a mathematically airtight yes/no answer (not just "the heuristic gave
   up"). This is what turns a heuristic failure into a *genuine*, checkable
   counterexample when one is found.
4. **Adversarial / evolutionary search over the space of instances itself**
   (not just over witnesses for a fixed instance): simulated annealing
   where the *state* is an entire graph and moves are small structural
   edits (edge swaps, moving "missing" edges around), with an objective
   that rewards getting closer to violating the conjecture. This is the
   "unorthodox" part — instead of waiting to randomly stumble on a rare
   adversarial structure, we actively search for it.

## Problems attempted

| Problem | Status | Write-up |
|---|---|---|
| Friendly (internal) partitions of 5-regular graphs | see write-up | [`problems/friendly_partitions_5regular/FINDINGS.md`](problems/friendly_partitions_5regular/FINDINGS.md) |
| Seymour's Second Neighborhood Conjecture (oriented graphs) | see write-up | [`problems/second_neighborhood_conjecture/FINDINGS.md`](problems/second_neighborhood_conjecture/FINDINGS.md) |
| Tuza's Conjecture (triangle packing vs. covering) | see write-up | [`problems/tuzas_conjecture/FINDINGS.md`](problems/tuzas_conjecture/FINDINGS.md) |
| The Ramsey number R(3,10) | see write-up | [`problems/ramsey_3_10/FINDINGS.md`](problems/ramsey_3_10/FINDINGS.md) |
| Snake-in-the-box (longest induced path in the hypercube) | see write-up (negative result) | [`problems/snake_in_the_box/FINDINGS.md`](problems/snake_in_the_box/FINDINGS.md) |
| Van der Waerden number W(2,7) | see write-up (method didn't scale) | [`problems/vdw_2_7/FINDINGS.md`](problems/vdw_2_7/FINDINGS.md) |
| The Ramsey number R(4,6) | see write-up | [`problems/ramsey_4_6/FINDINGS.md`](problems/ramsey_4_6/FINDINGS.md) |
| The Ramsey number R(4,7) | see write-up (partial, 3.5% coverage) | [`problems/ramsey_4_7/FINDINGS.md`](problems/ramsey_4_7/FINDINGS.md) |

## Environment

Python 3.11, `networkx`, `numpy`, `python-sat` (Glucose backend), `pulp`
(bundled CBC solver, used for exact integer-programming oracles), and the
`nauty` package (`nauty-geng`) for exhaustive small-graph generation. All
code is pure computation — no destructive or unsafe operations.
