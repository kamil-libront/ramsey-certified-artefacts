#!/usr/bin/env bash
# checks.sh -- independent verifier for the Ramsey certified-artefact package (v0.2, 2026-09-20)
# Runs from anywhere and verifies in one shot:
 #  (a) every DRAT proof -> drat-trim prints VERIFIED;
#  (b) both published witnesses -> brute-force ramsey_enc prints verified=True;
#  (c) whole-tree bit-integrity -> sha256sum -c SHA256SUMS
set -u
cd "$(dirname "$0")" || exit 2
PASS=0; FAIL=0
ok(){   PASS=$((PASS+1)); printf '   [PASS] %s\n' "$*"; }
fail(){  FAIL=$((FAIL+1)); printf '   [FAIL] %s\n' "$*"; }

echo "== (a) DRAT proofs, independent checker drat-trim =="
# (5,5)-cyclic: cyc_42..cyc_48 (cyc_41 is a SAT model, no UNSAT proof)
for n in 42 43 44 45 46 47 48; do
  if ./checker/drat-trim/drat-trim "proofs/cyc_$n.cnf" "proofs/cyc_$n.drat" 2>/dev/null | grep -q VERIFIED; then ok "cyc_$n.drat"; else fail "cyc_$n.drat"; fi
done
#(4,6)-cyclic: cyc46_34..cyc46_40
for n in 34 35 36 37 38 39 40; do
  if ./checker/drat-trim/drat-trim "proofs/cyc46_$n.cnf" "proofs/cyc46_$n.drat" 2>/dev/null | grep -q VERIFIED; then ok "cyc46_$n.drat"; else fail "cyc46_$n.drat"; fi
done
# Exoo-extension: 3 independent proofs (different solvers same instance
for p in prova_glucose4 prova_lingeling prova_maplechrono; do
  if ./checker/drat-trim/drat-trim "proofs/ext42.cnf" "proofs/$p.drat" 2>/dev/null | grep -q VERIFIED; then ok "$p.drat"; else fail "$p.drat"; fi
done

echo "== (b) published witnesses, brute-force re-verification =="
out=$(python3 scripts/verify_exoo.py 2>&1); rc=$?
n=$(printf '%s\n' "$out" | grep -c 'verified=True')
if [ "${n:-0}" -ge 2 ]; then ok "witness re-check (2/2 verified=True)"; else fail "witness re-check (saw ${n:-0}/2)"; fi

echo "== (c) integrity, sha256sum -c SHA256SUMS =="
if sha256sum -c SHA256SUMS >/dev/null 2>&1; then ok "SHA256SUMS"; else fail "SHA256SUMS (integrity mismatch)"; fi

echo "== summary: PASS=$PASS FAIL=$FAIL =="
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CERTIFIED ARTEFACTS VERIFIED -- package is self-consistent."
  exit 0
fi
exit 1