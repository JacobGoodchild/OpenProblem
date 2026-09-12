#!/usr/bin/env python3
"""
Sanity checks before attacking order 33+:
  1. Q8 (order 8) is a known EXCEPTION -- not sequenceable. Our
     backtracking search must confirm this exhaustively (not just run
     out of budget).
  2. A semidirect-product group of order 21 (within Keedwell's PROVEN
     10-32 range) must be found sequenceable, with an independently
     verified valid sequencing.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.sequenceable_groups import (dicyclic_table, semidirect_zq_zp_table,
                                       verify_group_table, find_sequencing, verify_sequencing)

mult, ident, n = dicyclic_table(2)  # Q8
assert n == 8 and verify_group_table(mult, ident, n)
seq, nodes, exhausted = find_sequencing(mult, ident, n, time_limit_nodes=5_000_000)
print(f'Q8 (order 8, known exception): sequencing found = {seq is not None} (expect False), '
      f'exhausted-without-proof = {exhausted} (expect False -- must be a real proof), {nodes} nodes')
assert seq is None and not exhausted, 'FAILED: did not exhaustively confirm Q8 is non-sequenceable!'

mult, ident, n = semidirect_zq_zp_table(3, 7)  # order 21, in proven range
assert n == 21 and verify_group_table(mult, ident, n)
t0 = time.time()
seq, nodes, exhausted = find_sequencing(mult, ident, n, time_limit_nodes=20_000_000)
print(f'Order 21 (Keedwell-proven range): sequencing found = {seq is not None} (expect True), '
      f'{nodes} nodes, {time.time()-t0:.2f}s')
assert seq is not None, 'FAILED: order-21 group should be sequenceable per Keedwell theorem!'
assert verify_sequencing(mult, ident, n, seq), 'FAILED: returned sequence does not independently verify!'

print('\nPASS: tooling validated on both a known exception and a known-sequenceable case.')
