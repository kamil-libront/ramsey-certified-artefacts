#!/usr/bin/env python3
"""Emit the one-vertex-extension SAT instance as DIMACS CNF.

  emit_cnf.py <r> <s> <coloring_file> <out.cnf>
"""
import sys
from itertools import combinations


def load_coloring(path):
    n, red = None, set()
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                if "n=" in line:
                    n = int(line.split("n=")[1].split()[0])
                continue
            a, b = (int(x) for x in line.split())
            red.add((min(a, b), max(a, b)))
    return n, red


def main():
    r, s = int(sys.argv[1]), int(sys.argv[2])
    path, out = sys.argv[3], sys.argv[4]
    n, red = load_coloring(path)
    redadj = [[False] * n for _ in range(n)]
    for a, b in red:
        redadj[a][b] = redadj[b][a] = True
    blueadj = [[(not redadj[i][j]) and i != j for j in range(n)] for i in range(n)]

    def cliques(adj, k):
        return [T for T in combinations(range(n), k) if all(adj[a][b] for a, b in combinations(T, 2))]

    red_cl, blue_cl = cliques(redadj, r - 1), cliques(blueadj, s - 1)
    clauses = [list(-(v + 1) for v in T) for T in red_cl]
    clauses += [list(v + 1 for v in T) for T in blue_cl]
    with open(out, "w") as f:
        f.write(f"c one-vertex extension of {path}: can the (r,s)-free coloring of K_{n} be extended to K_{n+1}?\n")
        f.write(f"c red K{r-1} cliques: {len(red_cl)}, blue K{s-1} cliques: {len(blue_cl)}\n")
        f.write(f"p cnf {n} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")
    print(f"wrote {out}: vars={n} clauses={len(clauses)}")


if __name__ == "__main__":
    main()
