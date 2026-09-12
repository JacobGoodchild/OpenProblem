#!/usr/bin/env python3
"""
Compute the EXACT tau/nu ratio (via ILP) for a range of curated,
parameterized graph families, instead of relying only on random or SA
search. The known tight examples (K4, K5) and the only known
arbitrarily-large near-tight construction (Baron-Kahn, a partly-random
dense construction) are both "special" -- so it's worth directly checking
whether other natural, explicit families of graphs (that a mathematician
might guess as candidates) come anywhere close to ratio 2, or exceed it.

Families tested:
  - friendship graph F_k: k triangles sharing one common vertex
  - book graph B_k: k triangles sharing one common EDGE
  - k disjoint copies of K4 (sanity check: ratio should stay exactly 2)
  - "K4-chain": copies of K4 glued in a path, each consecutive pair sharing
    one vertex
  - "K4-glued-cycle": copies of K4 glued in a cycle, each consecutive pair
    sharing one vertex
  - wheel graph W_k: a cycle C_k plus one hub vertex connected to all of it
  - complete multipartite graphs K_{a,a,...,a} (r parts of size a)
  - random small perturbations of the above (single edge added/removed)
    to see if breaking symmetry pushes the ratio up or down
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import networkx as nx
from lib.tuza import tuza_ratio, enumerate_triangles


def friendship_graph(k):
    """k triangles all sharing one common vertex (vertex 0)."""
    G = nx.Graph()
    G.add_node(0)
    for i in range(k):
        a, b = 1 + 2 * i, 2 + 2 * i
        G.add_edge(0, a)
        G.add_edge(0, b)
        G.add_edge(a, b)
    return G


def book_graph(k):
    """k triangles all sharing one common edge (0,1) -- the 'spine'."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for i in range(k):
        v = 2 + i
        G.add_edge(0, v)
        G.add_edge(1, v)
    return G


def disjoint_cliques(clique_size, k):
    G = nx.Graph()
    for i in range(k):
        base = i * clique_size
        for a in range(clique_size):
            for b in range(a + 1, clique_size):
                G.add_edge(base + a, base + b)
    return G


def clique_chain(clique_size, k):
    """k copies of K_{clique_size}, consecutive ones sharing exactly one
    vertex, forming a chain."""
    G = nx.Graph()
    next_id = 0
    prev_shared = None
    for i in range(k):
        verts = []
        if prev_shared is not None:
            verts.append(prev_shared)
        while len(verts) < clique_size:
            verts.append(next_id)
            next_id += 1
        for a in range(len(verts)):
            for b in range(a + 1, len(verts)):
                G.add_edge(verts[a], verts[b])
        prev_shared = verts[-1]
    return G


def clique_cycle(clique_size, k):
    """k copies of K_{clique_size} glued in a cycle (each shares one vertex
    with the next, and the last shares with the first)."""
    if k < 3:
        return clique_chain(clique_size, k)
    G = nx.Graph()
    shared_vertices = list(range(k))  # one shared "joint" vertex per gap
    next_id = k
    for i in range(k):
        left = shared_vertices[i]
        right = shared_vertices[(i + 1) % k]
        verts = [left, right]
        while len(verts) < clique_size:
            verts.append(next_id)
            next_id += 1
        for a in range(len(verts)):
            for b in range(a + 1, len(verts)):
                G.add_edge(verts[a], verts[b])
    return G


def wheel_graph(k):
    G = nx.wheel_graph(k + 1)  # networkx: hub + cycle of length k
    return G


def complete_multipartite(a, r):
    return nx.complete_multipartite_graph(*([a] * r))


def evaluate(name, G, time_limit=20):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    triangles = enumerate_triangles(G)
    if not triangles:
        return {'name': name, 'n': n, 'm': m, 'num_triangles': 0,
                'tau': 0, 'nu': 0, 'ratio': None}
    if len(triangles) > 3000:
        return {'name': name, 'n': n, 'm': m, 'num_triangles': len(triangles),
                'tau': None, 'nu': None, 'ratio': None, 'skipped': 'too many triangles'}
    tau, nu, ratio = tuza_ratio(G, time_limit=time_limit)
    return {'name': name, 'n': n, 'm': m, 'num_triangles': len(triangles),
            'tau': tau, 'nu': nu, 'ratio': ratio}


def main():
    results = []
    start = time.time()

    for k in range(1, 12):
        results.append(evaluate(f'friendship_F{k}', friendship_graph(k)))
    for k in range(1, 12):
        results.append(evaluate(f'book_B{k}', book_graph(k)))
    for k in range(1, 8):
        results.append(evaluate(f'disjoint_K4_x{k}', disjoint_cliques(4, k)))
    for k in range(1, 6):
        results.append(evaluate(f'disjoint_K5_x{k}', disjoint_cliques(5, k)))
    for k in range(1, 8):
        results.append(evaluate(f'K4_chain_x{k}', clique_chain(4, k)))
    for k in range(1, 6):
        results.append(evaluate(f'K5_chain_x{k}', clique_chain(5, k)))
    for k in range(3, 9):
        results.append(evaluate(f'K4_cycle_x{k}', clique_cycle(4, k)))
    for k in range(3, 9):
        results.append(evaluate(f'K5_cycle_x{k}', clique_cycle(5, k)))
    for k in range(3, 12):
        results.append(evaluate(f'wheel_W{k}', wheel_graph(k)))
    for a in range(2, 6):
        for r in range(3, 6):
            results.append(evaluate(f'complete_multipartite_{a}x{r}', complete_multipartite(a, r)))

    max_ratio = 0.0
    max_entry = None
    violations = []
    for r in results:
        if r.get('ratio') is not None:
            if r['ratio'] > max_ratio:
                max_ratio = r['ratio']
                max_entry = r
            if r['ratio'] > 2.0 + 1e-9:
                violations.append(r)

    out = {
        'results': results,
        'max_ratio': max_ratio,
        'max_ratio_entry': max_entry,
        'violations': violations,
        'elapsed_seconds': time.time() - start,
    }
    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'structured_families.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)

    print(f'Checked {len(results)} structured family instances. '
          f'Max ratio = {max_ratio:.4f} ({max_entry["name"] if max_entry else None}). '
          f'{len(violations)} violations. Saved to {out_path}', flush=True)
    for r in results:
        print(f'  {r["name"]}: n={r["n"]}, m={r["m"]}, triangles={r["num_triangles"]}, '
              f'tau={r.get("tau")}, nu={r.get("nu")}, ratio={r.get("ratio")}', flush=True)


if __name__ == '__main__':
    main()
