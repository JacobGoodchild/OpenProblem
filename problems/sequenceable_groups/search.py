#!/usr/bin/env python3
"""
THE ACTUAL ATTACK: Keedwell's conjecture says every non-abelian group is
sequenceable except D6, D8, Q8. Proven for orders 10-32, plus separately
for the dihedral family (all orders), A5, S5, and solvable groups with
a unique element of order 2. Order 33+ is open in general.

We target non-abelian semidirect product groups Z_q ⋊ Z_p for ODD
primes p < q with p | (q-1): these groups have ODD order (p*q), so by
Cauchy's theorem they contain NO element of order 2 at all -- meaning
they can't be dihedral (always even order) and don't fit the "unique
element of order 2" proven family either (which concerns groups that
actually HAVE such an involution). This makes them a genuinely
untouched test family for order > 32, not a rediscovery of an
already-covered case.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.sequenceable_groups import semidirect_zq_zp_table, verify_group_table, find_sequencing, verify_sequencing


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-order', type=int, default=33)
    ap.add_argument('--max-order', type=int, default=200)
    ap.add_argument('--node-budget', type=int, default=30_000_000)
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    results = []

    # enumerate odd primes p<q with p|(q-1) and p*q in [min_order,max_order]
    candidates = []
    for p in range(3, args.max_order, 2):
        if not is_prime(p):
            continue
        for q in range(p + 1, args.max_order // p + 1):
            if not is_prime(q):
                continue
            if (q - 1) % p != 0:
                continue
            order = p * q
            if args.min_order <= order <= args.max_order:
                candidates.append((p, q, order))
    candidates.sort(key=lambda x: x[2])

    print(f'Testing {len(candidates)} odd-order semidirect-product groups '
          f'(orders {args.min_order}-{args.max_order}, outside all currently-proven families):', flush=True)

    for p, q, order in candidates:
        built = semidirect_zq_zp_table(p, q)
        if built is None:
            continue
        mult, ident, n = built
        assert n == order
        if not verify_group_table(mult, ident, n):
            print(f'  p={p},q={q} (order {order}): INVALID GROUP TABLE, skipping', flush=True)
            continue

        t0 = time.time()
        seq, nodes, exhausted = find_sequencing(mult, ident, n, time_limit_nodes=args.node_budget)
        elapsed = time.time() - t0

        if seq is not None:
            ok = verify_sequencing(mult, ident, n, seq)
            status = 'sequenceable' if ok else 'BUG-invalid-sequence-returned'
            print(f'  p={p},q={q} (order {order}): SEQUENCEABLE (independently verified: {ok}), '
                  f'{nodes} nodes, {elapsed:.2f}s', flush=True)
        elif exhausted:
            status = 'inconclusive_node_budget_exhausted'
            print(f'  p={p},q={q} (order {order}): inconclusive (node budget {args.node_budget} '
                  f'exhausted without resolving), {elapsed:.2f}s', flush=True)
        else:
            status = 'NOT_SEQUENCEABLE_exhaustively_proven'
            print(f'  p={p},q={q} (order {order}): *** NOT SEQUENCEABLE (exhaustively proven, '
                  f'{nodes} nodes) -- POTENTIAL COUNTEREXAMPLE TO KEEDWELL\'S CONJECTURE *** '
                  f'{elapsed:.2f}s', flush=True)

        results.append({'p': p, 'q': q, 'order': order, 'status': status,
                         'nodes': nodes, 'elapsed': elapsed,
                         'sequence': seq if seq is not None else None})

        with open(os.path.join(out_dir, 'search_results.json'), 'w') as f:
            json.dump(results, f, indent=2)

    n_seq = sum(1 for r in results if r['status'] == 'sequenceable')
    n_counter = sum(1 for r in results if 'NOT_SEQUENCEABLE' in r['status'])
    n_inconclusive = sum(1 for r in results if 'inconclusive' in r['status'])
    print(f'\nDONE. {len(results)} groups tested: {n_seq} sequenceable, '
          f'{n_counter} potential counterexamples, {n_inconclusive} inconclusive.', flush=True)


if __name__ == '__main__':
    main()
