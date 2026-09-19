#!/usr/bin/env python3
"""Certified non-extensibility test.

Builds the same one-vertex-extension SAT instance as extend_ramsey.py, but asks
the solver for a DRAT proof of UNSAT and writes it to a file so that an
INDEPENDENT checker (drat-trim) can validate it.

  certify_ext.py <r> <s> <coloring_file> <solver> <proof.drat>

UNSAT + valid DRAT proof = machine-checkable proof that the given (r,s)-free
coloring of K_n cannot be extended to K_{n+1}.
"""
import sys, os, json, hashlib
from itertools import combinations
from pysat.solvers import Solver
from ramsey_enc import check_coloring


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
    path, solver_name, out = sys.argv[3], sys.argv[4], sys.argv[5]
    n, red = load_coloring(path)
    ok, wit = check_coloring(n, sorted(red), r, s)
    print(f"input {os.path.basename(path)}: n={n} red_edges={len(red)} verified={ok} {wit}", flush=True)
    if not ok:
        print("INPUT COLORING INVALID - abort")
        return 2
    redadj = [[False] * n for _ in range(n)]
    for a, b in red:
        redadj[a][b] = redadj[b][a] = True
    blueadj = [[(not redadj[i][j]) and i != j for j in range(n)] for i in range(n)]

    def cliques(adj, k):
        return [T for T in combinations(range(n), k) if all(adj[a][b] for a, b in combinations(T, 2))]

    red_cl, blue_cl = cliques(redadj, r - 1), cliques(blueadj, s - 1)
    print(f"clauses: red K{r-1}={len(red_cl)} blue K{s-1}={len(blue_cl)} vars={n}", flush=True)
    clauses = [list(-(v + 1) for v in T) for T in red_cl]
    clauses += [list(v + 1 for v in T) for T in blue_cl]

    with Solver(name=solver_name, with_proof=True, bootstrap_with=clauses) as sv:
        res = sv.solve()
        print(f"solver={solver_name} sat={res}", flush=True)
        if res:
            print("EXTENDS (unexpected here): SAT model exists")
            return 1
        try:
            proof = sv.get_proof()
        except Exception as e:
            print(f"NO PROOF from this solver: {e}")
            return 3
    lines = []
    for cl in proof:
        if isinstance(cl, (list, tuple)):
            if cl and cl[0] == "d":
                lines.append("d " + " ".join(str(x) for x in cl[1:]) + " 0")
            else:
                lines.append(" ".join(str(x) for x in cl) + " 0")
        else:
            lines.append(str(cl))
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote DRAT proof: {out} lines={len(lines)} bytes={os.path.getsize(out)} sha256={h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
