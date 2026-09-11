#!/bin/bash
cd "$(dirname "$0")"
for n in 10 15 20 30 50 80 120 200; do
  for m in 1 2 3 5 8 15; do
    if [ $m -ge $n ]; then continue; fi
    python3 -u adversarial_search.py $n $m --steps 60000 --seed 42
  done
done
