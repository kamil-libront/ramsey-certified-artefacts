"""
Ramsey SAT toolkit (portable: T460 / smocibb-Windows).

  ramsey_enc.py  -- encoder + DIMACS export + independent verifier

Encoding: x_{ij} (i<j) = 1 means edge (i,j) is RED, 0 means BLUE.
  * for every r-subset: clause  [-x_e for e in S]   (no red K_r)
  * for every s-subset: clause  [ x_e for e in S]   (no blue K_s)
So SAT  <=>  a 2-coloring of K_n with no red K_r and no blue K_s  <=>  R(r,s) > n.
UNSAT <=> R(r,s) <= n.
"""
from itertools import combinations


def var_index(n, i, j):
    if i > j:
        i, j = j, i
    return i * (n - 1) - i * (i - 1) // 2 + (j - i - 1) + 1


def encode_iter(n, r, s, perm=None):
    """Generator of clauses (memory-friendly: never materialise the whole list)."""
    idx = list(range(n)) if perm is None else list(perm)
    assert sorted(idx) == list(range(n))
    for S in combinations(range(n), r):
        yield [-var_index(n, idx[a], idx[b]) for a, b in combinations(S, 2)]
    for S in combinations(range(n), s):
        yield [var_index(n, idx[a], idx[b]) for a, b in combinations(S, 2)]


def encode(n, r, s, perm=None):
    """Return (clauses, nvars) -- materialised; use encode_iter for big n."""
    return list(encode_iter(n, r, s, perm)), n * (n - 1) // 2


def write_dimacs(path, n, clauses, nvars):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")


def model_to_red_edges(n, model):
    """model: list of signed literals from the solver (1-indexed vars)."""
    pos = set(m for m in model if m > 0)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if var_index(n, i, j) in pos]


def check_coloring(n, red_edges, r, s):
    """Independent brute-force check. Returns (ok, witness)."""
    red = [[False] * n for _ in range(n)]
    for i, j in red_edges:
        assert 0 <= i < j < n, (i, j)
        if red[i][j]:
            return False, ("duplicate edge", (i, j))
        red[i][j] = red[j][i] = True
    for S in combinations(range(n), r):
        if all(red[a][b] for a, b in combinations(S, 2)):
            return False, ("red K_%d" % r, S)
    for S in combinations(range(n), s):
        if not any(red[a][b] for a, b in combinations(S, 2)):
            return False, ("blue K_%d" % s, S)
    return True, None


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "cnf":
        r, s, n = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        out = sys.argv[5] if len(sys.argv) > 5 else f"r{r}s{s}n{n}.cnf"
        cl, nv = encode(n, r, s)
        write_dimacs(out, n, cl, nv)
        print(f"wrote {out}: nvars={nv} nclauses={len(cl)}")
    elif len(sys.argv) >= 4 and sys.argv[1] == "check":
        r, s = int(sys.argv[2]), int(sys.argv[3])
        path = sys.argv[4]
        n = None
        red = []
        with open(path) as f:
            for line in f:
                if line.startswith("#"):
                    if "n=" in line:
                        n = int(line.split("n=")[1].split()[0])
                    continue
                a, b = line.split()
                red.append((int(a), int(b)))
        ok, w = check_coloring(n, red, r, s)
        print(("OK" if ok else "FAIL"), n, len(red), w)
        sys.exit(0 if ok else 1)
