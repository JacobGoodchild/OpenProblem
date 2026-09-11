"""
Exact (decidable, not just heuristic) friendly-partition checker using a
SAT encoding. This is the authoritative oracle used whenever the local
search in friendly_partitions.py fails to find a witness -- if the SAT
solver also returns UNSAT, we have a mathematically rigorous proof that
the graph has NO friendly partition (a genuine exception / potential
counterexample to finiteness of the exception set).

Encoding
--------
One boolean variable x_v per vertex (True = side A).
One boolean variable s_e per edge e=(u,v): s_e <-> (x_u == x_v)
    (s_e = 1 means the edge is monochromatic, i.e. "at home" for both endpoints)
For each vertex v of degree d, with incident edge-variables s_1..s_d:
    at-least-ceil(d/2) of them must be true.
Non-triviality: fix x_(first vertex) = True, and require at least one
other x_v = False (excludes the all-True and all-False partitions, which
trivially "work" but are not genuine friendly partitions since a side must
be non-empty on both ends).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Glucose4


@dataclass
class SATResult:
    sat: bool           # True = friendly partition exists, False = proven none exists
    partition: Optional[dict] = None
    solve_time: float = 0.0


def sat_friendly_partition(G: nx.Graph, timeout: Optional[float] = None) -> SATResult:
    import time
    t0 = time.time()

    nodes = list(G.nodes())
    pool = IDPool()
    xvar = {v: pool.id(("x", v)) for v in nodes}
    evar = {}
    for u, v in G.edges():
        evar[frozenset((u, v))] = pool.id(("s", u, v))

    cnf_clauses = []

    # s_e <-> (x_u == x_v)   i.e.  s <-> NOT(x_u XOR x_v)
    for edge_key, s in evar.items():
        u, v = tuple(edge_key)
        xu, xv = xvar[u], xvar[v]
        # s -> (xu <-> xv):  (-s, -xu, xv) and (-s, xu, -xv)
        cnf_clauses.append([-s, -xu, xv])
        cnf_clauses.append([-s, xu, -xv])
        # (xu <-> xv) -> s:  (xu, xv, s)  ... wait derive properly below
        # (NOT xu OR NOT xv OR s) and (xu OR xv OR s) together with above give iff:
        cnf_clauses.append([xu, xv, s])
        cnf_clauses.append([-xu, -xv, s])

    top = pool.top  # running counter for fresh auxiliary-variable ids used by CardEnc
    for v in nodes:
        d = G.degree(v)
        need = math.ceil(d / 2)
        lits = [evar[frozenset((v, w))] for w in G.neighbors(v)]
        card = CardEnc.atleast(lits=lits, bound=need, top_id=top, encoding=EncType.seqcounter)
        cnf_clauses.extend(card.clauses)
        top = max(top, card.nv)

    # non-triviality
    if len(nodes) >= 2:
        cnf_clauses.append([xvar[nodes[0]]])          # fix first vertex True
        cnf_clauses.append([-xvar[v] for v in nodes[1:]])  # at least one False among the rest

    solver = Glucose4(bootstrap_with=cnf_clauses)
    is_sat = solver.solve()
    result = SATResult(sat=is_sat, solve_time=time.time() - t0)
    if is_sat:
        model = set(solver.get_model())
        partition = {v: (1 if xvar[v] in model else 0) for v in nodes}
        result.partition = partition
    solver.delete()
    return result
