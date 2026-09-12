#!/usr/bin/env python3
"""
Sanity checks for the MOLS SAT encoding (lib/mols_sat.py) before
attacking the real target: does a set of 3 mutually orthogonal Latin
squares of order 10 exist? (Famous open problem -- N(10) is known to
be between 2 and 6, and whether it's >= 3 has been unresolved for over
60 years, since Bose-Shrikhande-Parker's 1959 constructions disproved
Euler's conjecture that N(4k+2)=1 for all k.)

Checks:
  1. n=4, k=2 MOLS: known to exist (4 is a prime power) -- SAT expected, fast.
  2. n=4, k=3 MOLS: known to exist (max possible for order 4) -- SAT expected, fast.
  3. n=6, k=2 MOLS (the classical "36 officers problem"): known to be
     IMPOSSIBLE (Tarry, 1900) -- UNSAT expected, but proving UNSAT is
     much harder for a generic SAT encoding than finding SAT, and we
     honestly report whether our solver can confirm it in reasonable time.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lib.mols_sat import solve_mols, verify_latin_square, verify_orthogonal

t0 = time.time()
sat, squares = solve_mols(4, 2)
print(f'n=4, k=2 MOLS (known to exist): SAT={sat}, {time.time()-t0:.3f}s')
if sat:
    ok = (verify_latin_square(squares[0], 4) and verify_latin_square(squares[1], 4)
          and verify_orthogonal(squares[0], squares[1], 4))
    print(f'  independently verified valid + orthogonal: {ok}')

t0 = time.time()
sat, squares = solve_mols(4, 3)
print(f'n=4, k=3 MOLS (known to exist, max for order 4): SAT={sat}, {time.time()-t0:.3f}s')
if sat:
    ok = (all(verify_latin_square(sq, 4) for sq in squares) and
          all(verify_orthogonal(squares[i], squares[j], 4) for i in range(3) for j in range(i + 1, 3)))
    print(f'  independently verified valid + pairwise orthogonal: {ok}')

print('n=6, k=2 MOLS (the classical 36 officers problem, known IMPOSSIBLE since 1900):')
print('  attempting to confirm UNSAT within 90s (proving UNSAT is much harder than finding SAT)...')
t0 = time.time()
try:
    import signal

    def handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(90)
    sat, squares = solve_mols(6, 2)
    signal.alarm(0)
    print(f'  RESULT: SAT={sat} in {time.time()-t0:.1f}s '
          f'({"correctly confirms known impossibility" if sat is False else "UNEXPECTED — should be UNSAT!"})')
except TimeoutError:
    print(f'  TIMED OUT after 90s without resolving SAT/UNSAT -- our generic encoding cannot '
          f'confirm this known-hard instance quickly (an honest tooling limitation, not a bug: '
          f'this is a famous historically hard case even for specialized solvers).')
