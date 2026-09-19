#!/usr/bin/env python3
"""
Exhaustive search over CYCLIC 2-colorings of K_n for (r,s)-free colorings.

A cyclic coloring colors edge (i,j) by chord class d = min(|i-j|, n-|i-j|) in
1..floor(n/2), so there are only 2^floor(n/2) colorings -- these can be
enumerated EXHAUSTIVELY (only 4M for n=44/45, 8M for n=46/47).  Result is
complete inside the cyclic family:
  * FOUND   -> explicit construction, R(r,s) >= n+1
  * NO ...  -> no cyclic coloring works on n vertices (a fact, not a heuristic)

Method (avoids O(2^k * C(n,r)) brute force):
  For every r-subset S of vertices compute the bitmask C(S) of chord classes
  used by its edges.  "S is red-mono" <=> C(S) subset of R; "S is blue-mono"
  <=> C(S) subset of complement(R).  Mark all masks C(S) as 'present' and run
  a 21-bit subset(zeta) OR transform so that superset_present[R] is True iff
  some S has C(S) subset R.  Then R is bad iff superset_present[R] or
  superset_present[~R].

Usage: cyclic_ramsey.py <r> <s> <n>
"""
import sys
from itertools import combinations
import numpy as np


def chord_class_sets(n, r, s):
    """bitmask (over chord classes 1..half) for every r- and s-subset"""
    half = n // 2

    def cls(i, j):
        d = abs(i - j) % n
        d = min(d, n - d)
        return d  # 1..half

    masks_r = set()
    for S in combinations(range(n), r):
        m = 0
        for a, b in combinations(S, 2):
            m |= 1 << (cls(a, b) - 1)
        masks_r.add(m)
    masks_s = set()
    for S in combinations(range(n), s):
        m = 0
        for a, b in combinations(S, 2):
            m |= 1 << (cls(a, b) - 1)
        masks_s.add(m)
    return masks_r, masks_s, half


def superset_closure(present):
    """present: uint8 array over 2^k masks -> array where True iff some
    present mask is a subset of the index mask."""
    k = int(np.log2(len(present)))
    a = present.astype(np.uint8).copy()
    for b in range(k):
        step = 1 << b
        idx = np.arange(len(a))
        # index with bit b set -> OR in the value of index without bit b
        has = (idx >> b) & 1 == 1
        a[has] |= a[idx[has] - step]
    return a


def main():
    r, s, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    masks_r, masks_s, half = chord_class_sets(n, r, s)
    size = 1 << half
    full = size - 1
    pres_r = np.zeros(size, dtype=np.uint8)
    pres_s = np.zeros(size, dtype=np.uint8)
    for m in masks_r:
        pres_r[m] = 1
    for m in masks_s:
        pres_s[m] = 1
    sup_r = superset_closure(pres_r)   # red-mono exists if R superset of some C(S)
    sup_s = superset_closure(pres_s)
    complement = np.arange(size, dtype=np.int64) ^ full
    bad = (sup_r.astype(bool)) | (sup_s[complement].astype(bool))
    good = np.flatnonzero(~bad)
    print(f"n={n} r={r} s={s}: half={half} cyclic colorings={size} "
          f"distinct K{r}-masks={len(masks_r)} K{s}-masks={len(masks_s)}")
    if len(good) > 0:
        R = int(good[0])
        classes = sorted(d for d in range(1, half + 1) if (R >> (d - 1)) & 1)
        print(f"FOUND {len(good)} (r,s)-free cyclic colorings; example red classes={classes}")
        print(f"=> R({r},{s}) >= {n + 1}   (explicit cyclic construction)")
    else:
        print(f"NO cyclic ({r},{s})-free coloring on {n} vertices "
              f"(exhaustive within the cyclic family)")


if __name__ == "__main__":
    main()
