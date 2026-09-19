"""Verify Exoo K_35 (4,6)-free coloring with our check_coloring (calibration)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ramsey_enc import check_coloring

def load_edges(path):
    red = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            a, b = map(int, line.split())
            red.add((min(a, b), max(a, b)))
    return sorted(red)

for path, n, r, s in [
    ("data/ramsey_4_6_35_free_exoo.txt", 35, 4, 6),
    ("data/ramsey_5_5_42_free_exoo.txt", 42, 5, 5),
]:
    red = load_edges(path)
    ok, wit = check_coloring(n, red, r, s)
    print(f"{path}: n={n} r={r} s={s} red_edges={len(red)} verified={ok} witness={wit}")
