#!/bin/bash
cd "$(dirname "$0")"
for n in 20 30 50 100; do
  for frac in 4 2 1; do
    m=$((n / frac))
    if [ $m -lt 1 ]; then continue; fi
    python3 -u adversarial_search.py $n $m --steps 80000 --seed 77
  done
done
