# Ramsey certified-artefact package (v0.2, 2026-09-20)

Independently verifiable computational artefacts for the arXiv note
`ramsey_certified_note.tex`: no cyclic (5,5)-free K_n for n=42..48 and
none cyclic (4,6)-free for n=34..40); Exoo's 42-vertex (5,5)-free
graph is maximal (no one-vertex extension to 43); both published
witnesses (42-v (5,5)-free, 35-v (4,6)-free) are re-verified by
brute force.

Every negative statement carries a DRAT proof checked with the independent
checker `checker/drat-trim/drat-trim`; every positive colouring is re-verified
with `scripts/ramsey_enc.py` (brute force, its logic is the definition itself)。
SHA-256 digests of the whole tree are in `SHA256SUMS`.

**Run the whole verification with ONE command:**
```bash
bash checks.sh
```
Expect: `PASS=19 FAIL=0` and `ALL CERTIFIED ARTEFACTS VERIFIED`.

Full manifest, commands and honest limits: see `REPRODUCE.md`.

## License
- Code (Python scripts, drat-trim checker): MIT — see `LICENSE`.
- Data (edge lists, CNF instances, DRAT proofs, digests): CC0 1.0, public domain — see `DATA-LICENSE`.