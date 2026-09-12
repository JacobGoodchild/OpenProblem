"""
Extends lib/cyclotomic_ramsey.py from prime moduli to PRIME POWER moduli
q = p^k (k > 1), using proper finite field GF(q) arithmetic (via the
`galois` package) instead of plain modular arithmetic. This covers a
strictly larger algebraic family of cyclotomic constructions than
lib/cyclotomic_ramsey.py alone -- some real literature Ramsey lower
bound constructions are built over GF(p^k) rather than GF(p), so this
is a direct, motivated extension of the prime-only sweep
(problems/cyclotomic_sweep), not a repeat of it.

Same idea as before: GF(q)^* is cyclic of order q-1, so if r | (q-1),
there's an index-r subgroup giving r cosets that partition GF(q)^*. If
-1 is in the subgroup, the cosets are closed under negation and can be
used as connection sets for an r-coloring of the Cayley graph on the
ADDITIVE group of GF(q) (vertices = field elements, edge {a,b} iff a-b
is in a given coset).
"""
import galois

from lib.circulant_ramsey import is_clique_free


def prime_power_factorization(q):
    """Returns (p, k) if q = p^k for a prime p and k>=1, else None."""
    if q < 2:
        return None
    for p in range(2, int(q ** 0.5) + 2):
        if q % p == 0:
            k = 0
            qq = q
            while qq % p == 0:
                qq //= p
                k += 1
            if qq == 1:
                return (p, k)
            return None
    return (q, 1)  # q itself is prime


def gf_cyclotomic_cosets(q, r):
    """Build the r cosets of the index-r subgroup of GF(q)^*, mapped to
    plain integers 0..q-1 (the `galois` package's integer representation
    of field elements) so we can reuse the existing is_clique_free
    machinery unchanged (it only needs a difference/membership relation
    and a modulus-like "negation" -- both of which we handle here via
    the field's own arithmetic, translated to a simple lookup table)."""
    if (q - 1) % r != 0:
        return None
    pf = prime_power_factorization(q)
    if pf is None:
        return None
    p, k = pf
    if k < 2:
        return None  # plain primes are handled by lib/cyclotomic_ramsey.py

    try:
        GF = galois.GF(q)
    except Exception:
        return None

    g = GF.primitive_element
    subgroup_gen = g ** r
    subgroup = set()
    x = GF(1)
    for _ in range((q - 1) // r):
        subgroup.add(int(x))
        x = x * subgroup_gen
    if len(subgroup) != (q - 1) // r:
        return None

    neg_one = int(-GF(1))
    if neg_one not in subgroup:
        return None  # cosets not negation-closed

    cosets = [subgroup]
    covered = set(subgroup)
    gi = GF(1)
    coset_reps_tried = 0
    elem = 2
    while len(cosets) < r and coset_reps_tried < q:
        if elem not in covered and elem < q:
            new_coset = set(int(GF(elem) * GF(s)) for s in subgroup)
            if not (new_coset & covered):
                cosets.append(new_coset)
                covered |= new_coset
        elem += 1
        coset_reps_tried += 1
    if covered != set(range(1, q)):
        return None
    return cosets, GF


def try_gf_cyclotomic(q, r, clique_sizes):
    """Same interface as lib.cyclotomic_ramsey.try_cyclotomic but for
    prime power q. Builds difference sets using additive-group structure
    of GF(q) (via a "distance" mapping: two elements a<b are the same
    "distance class" iff b-a and a-b land in the same coset -- since
    cosets are negation-closed by construction, this partitions the
    q-1 nonzero field elements into (q-1)/2... 'ish groups similar to
    the prime case, but we instead directly build the Cayley graph edges
    via field subtraction and check clique-freeness with a small
    adapted backtracking routine (reusing the same recursion shape as
    is_clique_free, just with GF subtraction instead of mod-n subtraction).
    """
    result = gf_cyclotomic_cosets(q, r)
    if result is None:
        return None, None
    cosets, GF = result

    def clique_free_gf(D, size):
        D_list = sorted(D)

        def extends(clique, cand):
            for c in clique:
                diff = int(GF(cand) - GF(c))
                if diff not in D and int(-GF(diff)) not in D:
                    return False
            return True

        def backtrack(start_idx, clique):
            if len(clique) == size - 1:
                return True
            for i in range(start_idx, len(D_list)):
                cand = D_list[i]
                if extends(clique, cand):
                    if backtrack(i + 1, clique + [cand]):
                        return True
            return False

        return not backtrack(0, [])

    ok = all(clique_free_gf(cosets[i], clique_sizes[i]) for i in range(r))
    return ok, (cosets if ok else None)


def search_gf_cyclotomic_range(clique_sizes, q_min, q_max):
    """Exhaustively check every eligible prime power q (non-prime, i.e.
    k>=2) in [q_min, q_max]."""
    r = len(clique_sizes)
    checked = []
    found = []
    for q in range(q_min, q_max + 1):
        pf = prime_power_factorization(q)
        if pf is None or pf[1] < 2:
            continue
        ok, D = try_gf_cyclotomic(q, r, clique_sizes)
        if ok is None:
            continue
        checked.append(q)
        if ok:
            found.append((q, D))
    return checked, found
