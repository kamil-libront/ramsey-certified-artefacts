"""One-vertex extension test: can a known (r,s)-free coloring of K_n be extended
to K_{n+1}?

Given a verified (r,s)-free coloring G of K_n, adding vertex w means choosing its
RED neighbour set Y (n booleans) such that:
  * no red K_r:  for every red (r-1)-clique T of G:  NOT all y_v (v in T)
  * no blue K_s: for every blue (s-1)-clique T of G: at least one y_v (v in T)
(every other mono clique lies inside G and is already absent).  So this is a tiny
SAT instance with n variables.  SAT => the extended graph is (r,s)-free on n+1
vertices => R(r,s) >= n+2.  UNSAT => this particular graph is maximal.

Usage: extend_ramsey.py <r> <s> <coloring_file> [solver]
"""
import sys, os, json
from itertools import combinations
from pysat.solvers import Solver

try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
except Exception:
    pass

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
    path = sys.argv[3]
    solver_name = sys.argv[4] if len(sys.argv) > 4 else "cadical300"
    n, red = load_coloring(path)
    redadj = [[False] * n for _ in range(n)]
    for a, b in red:
        redadj[a][b] = redadj[b][a] = True
    blueadj = [[(not redadj[i][j]) and i != j for j in range(n)] for i in range(n)]

    def cliques(adj, k):
        out = []
        for T in combinations(range(n), k):
            if all(adj[a][b] for a, b in combinations(T, 2)):
                out.append(T)
        return out

    red_cl = cliques(redadj, r - 1)
    blue_cl = cliques(blueadj, s - 1)
    print(f"n={n}: red K{r-1}s={len(red_cl)} blue K{s-1}s={len(blue_cl)}", flush=True)
    clauses = [list(-(v + 1) for v in T) for T in red_cl]      # not all red to w
    clauses += [list(v + 1 for v in T) for T in blue_cl]       # not all blue to w

    with Solver(name=solver_name, bootstrap_with=clauses) as sv:
        res = sv.solve()
        if res:
            model = sv.get_model()
            new_red = set(red)
            for v in range(n):
                if model[v] > 0:
                    new_red.add((v, n))
            ok, wit = check_coloring(n + 1, sorted(new_red), r, s)
            fn = os.path.join(os.environ.get("RAMSEY_OUT", "."),
                              f"ramsey_{r}_{s}_{n+1}_free_extended.txt")
            with open(fn, "w") as f:
                f.write(f"# (r,s)-free coloring of K_{n+1}  n={n+1}  r={r} s={s}\n")
                f.write(f"# red edges below => R({r},{s}) >= {n+2}\n")
                f.write(f"# built by one-vertex extension of {os.path.basename(path)}; verified={ok}\n")
                for i, j in sorted(new_red):
                    f.write(f"{i} {j}\n")
            print(f"EXTENDS: verified={ok} witness={wit} file={fn}", flush=True)
            return 0 if ok else 30
        print(f"NO EXTENSION of this graph (UNSAT) => {os.path.basename(path)} is maximal",
              flush=True)
        return 11


if __name__ == "__main__":
    sys.exit(main())
