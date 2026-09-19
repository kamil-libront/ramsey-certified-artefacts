#!/usr/bin/env python3
"""Certified exhaustion of CYCLIC (r,s)-free colorings of K_n.

Independent re-derivation of the result of cyclic_ramsey.py (which uses a
subset/zeta transform): here the same statement is encoded as a SAT instance
over the floor(n/2) chord classes and decided by CDCL, with a DRAT proof of
UNSAT emitted for external checking with drat-trim.

Variables: x_d = "chord class d is red" (d = 1..floor(n/2)).
For every 5-subset S with chord-class set C(S):
    (not all of C(S) red)   ->  clause  OR_{d in C(S)} ~x_d
    (not all of C(S) blue)  ->  clause  OR_{d in C(S)}  x_d
Only the distinct masks C(S) are needed (duplicates are redundant clauses).

  cyclic_sat.py <r> <s> <n> <solver> <out.cnf> <out.drat>
Exit codes: 0 = UNSAT (certified instance written), 10 = SAT (coloring exists),
11 = UNSAT but no proof support.
"""
import sys, os, hashlib
from itertools import combinations
from pysat.solvers import Solver

# pysat prints SAT models over these variables; keep the mapping explicit
def distinct_masks(n, r, s):
    half = n // 2

    def cls(i, j):
        d = abs(i - j) % n
        return min(d, n - d)

    mr, ms = set(), set()
    for S in combinations(range(n), r):
        m = 0
        for a, b in combinations(S, 2):
            m |= 1 << (cls(a, b) - 1)
        mr.add(m)
    for S in combinations(range(n), s):
        m = 0
        for a, b in combinations(S, 2):
            m |= 1 << (cls(a, b) - 1)
        ms.add(m)
    return sorted(mr), sorted(ms), half


def main():
    r, s, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    solver_name, cnf_out, drat_out = sys.argv[4], sys.argv[5], sys.argv[6]
    mr, ms, half = distinct_masks(n, r, s)
    clauses = []
    for m in mr:                      # no red K_r
        clauses.append([-(d + 1) for d in range(half) if (m >> d) & 1])
    for m in ms:                      # no blue K_s
        clauses.append([(d + 1) for d in range(half) if (m >> d) & 1])
    print(f"n={n} r={r} s={s}: chord classes={half} distinct masks r={len(mr)} s={len(ms)} "
          f"clauses={len(clauses)}", flush=True)
    with open(cnf_out, "w") as f:
        f.write(f"c cyclic ({r},{s})-free colorings of K_{n}: none may exist\n")
        f.write(f"c x_d = chord class d is red; red masks={len(mr)} blue masks={len(ms)}\n")
        f.write(f"p cnf {half} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")
    print(f"wrote {cnf_out} sha256={hashlib.sha256(open(cnf_out,'rb').read()).hexdigest()}", flush=True)

    with Solver(name=solver_name, with_proof=True, bootstrap_with=clauses) as sv:
        res = sv.solve()
        print(f"solver={solver_name} sat={res}", flush=True)
        if res:
            model = sv.get_model()
            classes = [d + 1 for d in range(half) if model[d] > 0]
            print(f"SAT: cyclic ({r},{s})-free coloring exists, red classes={sorted(classes)}")
            print(f"=> R({r},{s}) >= {n + 1}")
            return 10
        try:
            proof = sv.get_proof()
        except Exception as e:
            print(f"NO PROOF from {solver_name}: {e}")
            return 11
    lines = []
    for cl in proof:
        if isinstance(cl, (list, tuple)):
            if cl and cl[0] == "d":
                lines.append("d " + " ".join(str(x) for x in cl[1:]) + " 0")
            else:
                lines.append(" ".join(str(x) for x in cl) + " 0")
        else:
            lines.append(str(cl))
    with open(drat_out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {drat_out}: lines={len(lines)} bytes={os.path.getsize(drat_out)} "
          f"sha256={hashlib.sha256(open(drat_out,'rb').read()).hexdigest()}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
