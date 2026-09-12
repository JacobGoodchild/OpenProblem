"""
Snake-in-the-box: find long INDUCED paths in the n-dimensional hypercube
Q_n (vertices = bit strings of length n / integers 0..2^n-1, edges between
vertices differing in exactly one bit).

A "snake" is a path v_0, v_1, ..., v_L such that consecutive vertices are
hypercube-adjacent, all vertices are distinct, and NO two non-consecutive
vertices are adjacent (no "chords" -- this is what makes it an *induced*
path, and is what makes the problem hard: a long ordinary path is trivial,
but a long chord-free one is not).

Exact maximum snake length a(n) is known only for n <= 8: 0,1,2,4,7,13,
26,50,98 (a(0)=0 trivially, a(1)=1, ..., a(8)=98 -- note some sources index
so that a(n) counts EDGES, i.e. vertices-1; we follow that convention:
snake "length" = number of edges = len(path)-1). For n >= 9 only lower
bounds are known (best published records, as of recent literature:
a(9)>=191, a(10)>=379, a(11)>=746) -- finding an even longer snake for any
of these n would be a genuine, real improvement to a currently open
record.

Search method: randomized depth-first backtracking with random neighbor
order and random restarts -- the standard, long-established technique in
this literature for finding long snakes (not a proof of optimality, which
for n>=9 remains completely open; this only ever produces improving lower
bounds, same as essentially all published records in this area).
"""
import random


def neighbors(v, n):
    return [v ^ (1 << i) for i in range(n)]


def randomized_snake_search(n, rng, max_restarts=1, max_steps_per_restart=None,
                             time_budget=None, start_time_fn=None):
    """Randomized DFS with backtracking. Builds a path greedily, extending
    with a random valid neighbor; on getting stuck, backtracks. Returns the
    single longest path found across all restarts (as a list of vertex
    ints)."""
    import time
    if start_time_fn is None:
        start_time_fn = time.time

    best_path = []

    for restart in range(max_restarts):
        start_v = rng.randrange(2 ** n)
        path = [start_v]
        used = {start_v}
        # block_count[v] = number of path-INTERIOR vertices (i.e. path
        # vertices other than the current tip) that v is adjacent to.
        # v is a legal extension candidate iff block_count.get(v,0)==0 and
        # v not in used. Maintained incrementally (O(n) per push/pop)
        # instead of recomputed from scratch (O(n*len(path))) -- this is
        # the difference between a search that finishes in milliseconds
        # and one that doesn't finish at all past n~=6.
        block_count = {}

        def freedom(w, tip):
            cnt = 0
            for u in neighbors(w, n):
                if u == tip:
                    continue
                if u not in used and block_count.get(u, 0) == 0:
                    cnt += 1
            return cnt

        def compute_candidates(tip):
            cands = [w for w in neighbors(tip, n) if w not in used and block_count.get(w, 0) == 0]
            rng.shuffle(cands)
            # most-constrained-first: put LOWEST-freedom candidates at the
            # END of the list, since we .pop() from the end -- this tries
            # the most-constrained (riskiest) options first, a standard
            # heuristic that empirically finds much longer snakes before
            # needing to backtrack, versus pure random ordering
            cands.sort(key=lambda w: -freedom(w, tip))
            return cands

        candidate_stack = [compute_candidates(path[-1])]
        if len(path) > len(best_path):
            best_path = path[:]

        steps = 0
        while candidate_stack:
            steps += 1
            if max_steps_per_restart and steps > max_steps_per_restart:
                break
            if time_budget and (start_time_fn() > time_budget):
                break

            if not candidate_stack[-1]:
                # backtrack: pop tip, revert block_count contributions from
                # the vertex that will become the tip again
                candidate_stack.pop()
                if len(path) > 1:
                    removed = path.pop()
                    used.discard(removed)
                    new_tip = path[-1]
                    for u in neighbors(new_tip, n):
                        block_count[u] = block_count.get(u, 0) - 1
                        if block_count[u] <= 0:
                            del block_count[u]
                continue

            w = candidate_stack[-1].pop()
            tip = path[-1]
            for u in neighbors(tip, n):
                block_count[u] = block_count.get(u, 0) + 1
            path.append(w)
            used.add(w)
            if len(path) > len(best_path):
                best_path = path[:]
            candidate_stack.append(compute_candidates(w))

    return best_path


def greedy_walk_snake(n, rng, prefer_min_degree=True):
    """Fast, no-backtracking construction: walk greedily from a random
    start, at each step picking among the currently-valid extensions
    (using incremental O(n) block-count bookkeeping, same as the
    backtracking version) -- when there is a choice, prefer the candidate
    that itself has the FEWEST remaining valid extensions (a standard
    "most constrained first" heuristic: using up the most constrained
    vertices earliest tends to leave more freedom for later steps, so the
    walk runs longer before getting stuck). Stops the instant no valid
    extension exists (no backtracking at all) -- this trades optimality
    for raw speed, which is what makes millions of random restarts
    feasible even at n=9-11 (2^n up to 2048 vertices)."""
    start_v = rng.randrange(2 ** n)
    path = [start_v]
    used = {start_v}
    block_count = {}

    def candidates_of(tip):
        return [w for w in neighbors(tip, n) if w not in used and block_count.get(w, 0) == 0]

    while True:
        tip = path[-1]
        cands = candidates_of(tip)
        if not cands:
            break
        if prefer_min_degree and len(cands) > 1:
            # score each candidate by how many valid extensions IT would
            # have, without actually committing -- O(deg) per candidate
            def future_freedom(w):
                # temporarily count how many neighbors of w are free
                # (not used, not blocked by current interior, and not w's
                # own tip-to-be predecessor which will become blocked)
                cnt = 0
                for u in neighbors(w, n):
                    if u == tip:
                        continue
                    if u not in used and block_count.get(u, 0) == 0:
                        cnt += 1
                return cnt
            cands.sort(key=future_freedom)  # fewest-freedom first
            # small randomization: pick among the most-constrained tier
            min_freedom = future_freedom(cands[0])
            tier = [c for c in cands if future_freedom(c) == min_freedom]
            w = rng.choice(tier)
        else:
            w = rng.choice(cands)

        for u in neighbors(tip, n):
            block_count[u] = block_count.get(u, 0) + 1
        path.append(w)
        used.add(w)

    return path


def best_of_many_greedy_walks(n, rng, num_trials, prefer_min_degree=True):
    best_path = []
    for _ in range(num_trials):
        p = greedy_walk_snake(n, rng, prefer_min_degree=prefer_min_degree)
        if len(p) > len(best_path):
            best_path = p
    return best_path


def verify_snake(path, n):
    """Rigorous, from-scratch verification that `path` is a valid snake in
    Q_n: consecutive vertices differ in exactly one bit, all vertices
    distinct, and no non-consecutive pair is adjacent."""
    if len(set(path)) != len(path):
        return False, 'vertices not distinct'
    for i in range(len(path) - 1):
        diff = path[i] ^ path[i + 1]
        if bin(diff).count('1') != 1:
            return False, f'edge {i}-{i+1} not a hypercube edge (differ in {bin(diff).count("1")} bits)'
    for i in range(len(path)):
        for j in range(i + 2, len(path)):
            diff = path[i] ^ path[j]
            if bin(diff).count('1') == 1:
                return False, f'chord found between non-consecutive vertices {i} and {j}'
    return True, 'valid'
