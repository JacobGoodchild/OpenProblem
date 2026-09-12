"""
Sequenceable groups (Keedwell's conjecture territory): a finite group G
of order n is SEQUENCEABLE if its elements can be ordered
g_1=identity, g_2, ..., g_n such that the partial products
p_1=g_1, p_2=g_1*g_2, p_3=g_1*g_2*g_3, ..., p_n=g_1*...*g_n
are ALL DISTINCT (i.e. p_1,...,p_n is a permutation of G).

Keedwell's conjecture: every non-abelian group is sequenceable EXCEPT
D6 (order 6), D8 (order 8), Q8 (order 8). Proven true for non-abelian
groups of order 10 <= n <= 32 (and some other special families:
dihedral groups of ALL orders, A5, S5, solvable groups with a unique
element of order 2). Order 33+ (excluding those proven families) is
open -- this module builds and searches concrete non-abelian groups in
that unexplored range.

We represent a group abstractly via its multiplication table (a list of
lists: mult[i][j] = index of g_i * g_j), which lets the search code be
completely generic (doesn't need to know if the group is a semidirect
product, dihedral, etc.) -- only the group CONSTRUCTION functions below
need to know the specific algebraic structure.
"""
def isprime(n):
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


def semidirect_zq_zp_table(p, q):
    """Construct the (unique, for a fixed choice of automorphism order)
    non-abelian semidirect product Z_q ⋊ Z_p, valid when p | (q-1) and
    both p,q prime, p<q. This is a standard, simple-to-construct family
    of non-abelian groups of order p*q, genuinely different from the
    dihedral family (which has order 2*n and is already fully proven
    sequenceable) whenever p > 2.

    Elements: (a,b) with a in Z_p, b in Z_q, encoded as a*q+b (0-indexed).
    Multiplication: find r, a primitive p-th root of unity mod q (i.e.
    r^p = 1 mod q, r != 1), then (a1,b1)*(a2,b2) = (a1+a2 mod p,
    b1 + r^a1 * b2 mod q). Identity = (0,0).

    Returns (mult_table, identity_index, n) or None if p does not
    divide q-1 (no such nonabelian group exists) or p,q aren't prime.
    """
    if not (isprime(p) and isprime(q)):
        return None
    if (q - 1) % p != 0:
        return None

    # find r: an element of order exactly p in (Z_q)^*
    r = None
    for cand in range(2, q):
        if pow(cand, p, q) == 1 and cand != 1:
            r = cand
            break
    if r is None:
        return None

    n = p * q

    def idx(a, b):
        return a * q + b

    def elem(i):
        return divmod(i, q)

    mult = [[0] * n for _ in range(n)]
    r_pow = [pow(r, a, q) for a in range(p)]
    for i in range(n):
        a1, b1 = elem(i)
        for j in range(n):
            a2, b2 = elem(j)
            a3 = (a1 + a2) % p
            b3 = (b1 + r_pow[a1] * b2) % q
            mult[i][j] = idx(a3, b3)

    return mult, idx(0, 0), n


def dicyclic_table(n):
    """Dicyclic (generalized quaternion when n is a power of 2) group
    of order 4n, presentation <a,b | a^(2n)=1, b^2=a^n, b^-1 a b = a^-1>.
    Just used for validation (Q8 = dicyclic_table(2), known NON-sequenceable)."""
    order = 4 * n
    # elements: a^i for i in 0..2n-1, and a^i * b for i in 0..2n-1
    # encode: index i (0<=i<2n) = a^i ; index 2n+i = a^i * b
    def mult_pair(x, y):
        # x,y are ('a', i) or ('b', i) meaning a^i or a^i*b
        xt, xi = x
        yt, yi = y
        if xt == 'a':
            if yt == 'a':
                return ('a', (xi + yi) % (2 * n))
            else:
                return ('b', (xi + yi) % (2 * n))
        else:
            if yt == 'a':
                # a^xi * b * a^yi = a^xi * a^{-yi} * b = a^{xi-yi} b
                return ('b', (xi - yi) % (2 * n))
            else:
                # a^xi * b * a^yi * b = a^xi * a^{-yi} * b*b = a^{xi-yi+n} (b^2=a^n)
                return ('a', (xi - yi + n) % (2 * n))

    elems = [('a', i) for i in range(2 * n)] + [('b', i) for i in range(2 * n)]
    idx_of = {e: k for k, e in enumerate(elems)}
    order_total = len(elems)
    mult = [[0] * order_total for _ in range(order_total)]
    for i, ei in enumerate(elems):
        for j, ej in enumerate(elems):
            mult[i][j] = idx_of[mult_pair(ei, ej)]
    return mult, idx_of[('a', 0)], order_total


def verify_group_table(mult, identity, n):
    """Sanity checks: identity behaves correctly, and every row/column
    of the multiplication table is a permutation of 0..n-1 (closure +
    each element has unique inverse -- necessary for a valid group)."""
    for i in range(n):
        if mult[identity][i] != i or mult[i][identity] != i:
            return False
    for i in range(n):
        if sorted(mult[i]) != list(range(n)):
            return False
        if sorted(mult[k][i] for k in range(n)) != list(range(n)):
            return False
    return True


def find_sequencing(mult, identity, n, time_limit_nodes=50_000_000):
    """Backtracking search for a sequencing: order g_1=identity,
    g_2,...,g_n such that partial products are all distinct. Returns
    the sequence of element indices if found, else None (either proven
    no sequencing exists via exhaustive search, or the node budget was
    exhausted -- caller should check the returned 'exhausted' flag)."""
    used_elements = [False] * n
    used_elements[identity] = True
    used_partial_products = [False] * n
    used_partial_products[identity] = True  # p_1 = g_1 = identity

    sequence = [identity]
    nodes = [0]
    partial_holder = [identity]

    def backtrack2():
        nodes[0] += 1
        if nodes[0] > time_limit_nodes:
            return 'exhausted'
        if len(sequence) == n:
            return True
        cur_partial = partial_holder[0]
        for g in range(n):
            if used_elements[g]:
                continue
            new_partial = mult[cur_partial][g]
            if used_partial_products[new_partial]:
                continue
            used_elements[g] = True
            used_partial_products[new_partial] = True
            sequence.append(g)
            partial_holder[0] = new_partial
            result = backtrack2()
            if result is True:
                return True
            sequence.pop()
            used_elements[g] = False
            used_partial_products[new_partial] = False
            partial_holder[0] = cur_partial
            if result == 'exhausted':
                return 'exhausted'
        return False

    result = backtrack2()
    if result is True:
        return list(sequence), nodes[0], False
    elif result == 'exhausted':
        return None, nodes[0], True
    else:
        return None, nodes[0], False  # exhaustively proven NO sequencing exists


def verify_sequencing(mult, identity, n, sequence):
    """Independent from-scratch check that `sequence` is a valid
    sequencing: uses all n elements exactly once, starts at identity,
    and all partial products are distinct."""
    if sorted(sequence) != list(range(n)):
        return False
    if sequence[0] != identity:
        return False
    partial = identity
    seen = set()
    for i, g in enumerate(sequence):
        if i == 0:
            p = g
        else:
            p = mult[partial][g]
        if p in seen:
            return False
        seen.add(p)
        partial = p
    return len(seen) == n
