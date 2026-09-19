# Reproducibility - certified proof package (math-attack, arXiv note v0.2, 2026-09-20)

English companion to the arXiv note `ramsey_certified_note.tex`
(the Polish mirror `ramsey_certified_note_PL.tex` shares the same structure).
Everything here runs locally. Every negative statement carries a DRAT proof
checked with the independent checker `drat-trim` (commit 2e3b2dc0,
2024-11-25;build:`gcc -D_GNU_SOURCE -O2 -o drat-trim drat-trim.c`);
every positive colouring is re-verified with the brute-force verifier
`ramsey_enc.py`,whose logic is the defining condition itself. No
computational result is quoted as a "search finding": the package is entirely
exhaustive enumeration + DRAT certificates + brute-force verification.

## What is claimed,and how to check it

| claim | method A (exhaustive) | method B (independent, certified) |
|---|---|---|
| no cyclic (5,5)-free K_n,n=42..48;exactly 20 free K_41 (difference classes given)|`cyclic_ramsey.py 5 5 <n>`(zeta transform over chord classes)|`cyclic_sat.py`->CNF->CDCL->DRAT->`drat-trim`(n=42..48:VERIFIED)|
| no cyclic (4,6)-free K_n,n=34..40 |`cyclic_ramsey.py  4  6 <n>`|`cyclic_sat.py`->CNF->CDCL->DRAT->`drat-trim`(n=34..40:VERIFIED)|
| Exoo 42-v (5,5)-free graph does not extend to 43 (maximal)|`extend_ramsey.py`(UNSAT)|`emit_cnf.py`+`certify_ext.py`->DRAT->`drat-trim`(VERIFIED,three solvers)|
| published witnesses(42-v (5,5)-free;35-v (4,6)-free)are truly free|brute-force `check_coloring`(the definition itself)|not applicable (no search code involved)|

A sceptical reader needs only the commands below -- not the hashes -- and should
re-run every check independently

## Commands

```bash
# (5,5) A. exhaustive cyclic enumeration (n=41 ~6.5 s ... n=48 ~22.6 s, one core)
python3 cyclic_ramsey.py  5     5     43

#(5,5) B. certified CNF + DRAT + independent verification
cd tools
python3 cyclic_sat.py  5     5     43 glucose4 cyc_43.cnf cyc_43.drat
./drat-trim/drat-trim cyc_43.cnf cyc_43.drat         # -> s VERIFIED

#(4,6) A./B. same pipeline (the scripts are general in (r,s,n))
python3 cyclic_ramsey.py  4     6     36
python3 cyclic_sat.py   4     6     36 glucose4 cyc46_36.cnf cyc46_36.drat
./drat-trim/drat-trim cyc46_36.cnf cyc46_36.drat     # -> s VERIFIED

# C. Exoo extension instance and its certificate
python3 emit_cnf.py  5     5     ../data/ramsey_5_5_42_free_exoo.txt ext42.cnf
python3 certify_ext.py  5     5     ../data/ramsey_5_5_42_free_exoo.txt glucose4 prova_glucose4.drat
./drat-trim/drat-trim ext42.cnf prova_glucose4.drat    # -> s VERIFIED

# D. positive re-verification (brute force, independent of any search}
python3 ../ramsey55/ramsey_enc.py check  41 <witness.txt.txt>  5     5
python3 ../verify_exoo.py                                  # both published witnesses -> verified=True
```

Hardware:the above runs in seconds-to-minutes on a laptop;no cluster
needed. The searches that carried no certificate (reported as non-results in
the note)needed the two-socket workstation and are deliberately excluded from
this package.

## Artefact manifest - SHA-256 (full)

### Witnesses (published data, re-verified by brute force}
```
92549d13efc6dbfb98837d396c41e7059d62a8bc8f9453a5b3504d236b4b8e76  data/ramsey_5_5_42_free_exoo.txt     (42 v, 435 red edges}
ad43f25945f5eef733467e31523b69a6a00d0acf01e8f7d4e162e92ba3d2053b   data/ramsey_4_6_35_free_exoo.txt     (35 v, (4,6)-free)
16879a94aae15b7c3f0ccbccef7aa8ad6d7f8dcf762c578cc0500863a29a3417   data/ramsey_4_6_36_seed_from35.txt   (seed used in the non-certified method-A run}
```

### Scripts and verifier
```
269a88b09eb6c23d58cd652408d2deb5118b57ffebf3e826be45b5385597abb5  ramsey55/cyclic_ramsey.py       (exhaustive zeta enumeration,general (r,s))
1b150c653fcd0871fe3eab236d4c6cfd861bde764c7644e502777ff17cbbbb40  ramsey55/extend_ramsey.py       (extension UNSAT,method A}
bba3da8e1023aeae92b2cbcd028b02986a60080e4c68c3a6f24708d69935f3c9  ramsey55/ramsey_enc.py           (brute-force verifier;tools/ramsey_enc.py is byte-identical)
3c08163c75a31eb1674abda7c0574b6ab8827f1e88b44c32ce83c322f0683292  tools/cyclic_sat.py              (CDCL + DRAT emit;general (r,s,n))
23da360bc6f9d694de4a1a34c42b43ccb4c65555170493125fbd6f692e4e8508  tools/emit_cnf.py                 (extension instance)
73f56b3656fe020e4e81128ee61203fd2c4e9da1efdd455eae76c655b77c4344  tools/certify_ext.py               (extension DRAT emit)
```

### (5,5)-cyclic instances and certificates (n=42..48 UNSAT;DRAT VERIFIED}
```
504e65b38ccb5748e8b28fcb394fd97b18beacfd6722b8ecc587835803ff44f6   tools/cyc_41.cnf   (SAT model; 20 free colourings}
5dd03b68c9b61cf9286dcc17b8015f0ded324bdab20de67f69019ad4a6422b29   tools/cyc_42.cnf   (21 vars,18122 clauses)
af96648547940f56a90d75c5da5b5ccc3814a1fcf07e120bfec8b8e80ad73836   tools/cyc_43.cnf   (21 vars,20874 clauses)
53bfe42a467d30c5de28b1dd542af6185d5f3f2c2515512263bd104a6f086fb7   tools/cyc_44.cnf
b37f1bdc1a31f014421c2b7077231fb4a0489f3205cfdde97c568147a7a0307e   tools/cyc_45.cnf
145830e6217ab84904fb2973dd435602aced629de6fce06648b9f11e149b8dd6   tools/cyc_46.cnf
7854fddefe2da3ef8b4d35f36c24de8d1ee8fe43f599f16ec2939bf06b4410d8   tools/cyc_47.cnf
f13c0d8e37b665785da57c7d9c6a98dd92bb52504656adbfdedcb6de31ce0484   tools/cyc_48.cnf   (24 vars,32976 clauses}

e7db6b9d89a9e5dde8b559d1edbaf58d99be6588602cb316015526757edb0a96   tools/cyc_42.drat   (1187 lines) VERIFIED
4e27cbd985506d1ea946db2f3f58ca5d2b7577562e6190d8b4b5cc6c6918a0ea   tools/cyc_43.drat   (3011 lines) VERIFIED
40b2de33b4b37dcfbd03be7505d59e710e4a77fbf6be93b750c99c297c207b83   tools/cyc_44.drat               VERIFIED
a2f588c3b60a504f79f0662c729d1ae03dd4c5d5722806080be8da8d3dbde311   tools/cyc_45.drat               VERIFIED
46e74ae965af1d7e772a7ae3709f2747e26ecb12a37fd158ef154fa015755da1   tools/cyc_46.drat               VERIFIED
9a511db9edb688b5f1f0b58567d239880f297b37af8e9a033175dfef69e9a43e   tools/cyc_47.drat               VERIFIED
30691b1698fcb19a4034a2a63718220f5e7807d316994d5078530e1d3501df24   tools/cyc_48.drat   (1611 lines) VERIFIED
```

### (4,6)-cyclic instances and certificates(n=34..40 UNSAT;DRAT VERIFIED}
```
7c80120fe3f1f1da732c5f410e4e8993b49a3ce1f3af9d5afc65970ac6ddc08e  tools/cyc46_34.cnf   (17 vars,11051 clauses)
52a6ad759456b97f553f13e00961999bd87bd0ba7ba201c22b0a372d36bde0d8  tools/cyc46_35.cnf   (17 vars,12874 clauses)
8f3986e7284bb0acd0a9c2dd0455f7f513de21e6084e1e5487cf0769412e4b30  tools/cyc46_36.cnf   (18 vars,16794 clauses]
d5c8673aec754c8db99d289a6e78ea9f3fff4f2c10b5f48b40bbc19c43ce09df  tools/cyc46_37.cnf   (18 vars,20196 clauses)
8b73f4ab463da3753c5cd680b27847be36a6417443ff894dccaf3bdb453ab729  tools/cyc46_38.cnf   (19 vars,25237 clauses]
6c6b02a9eefb6b457dc2ed2103c27b089db7d3da0f16ab851d4a62b4917813e0  tools/cyc46_39.cnf   (19 vars,29888 clauses]
cf097502a548a7b1b364147df6ffa6353cdbdae08d2e417b7a1e1016d47d20fe  tools/cyc46_40.cnf   (20 vars,34834 clauses]

40c8c342cd23371245556182ba24fa657712888946387184549fa41f6de600b9  tools/cyc46_34.drat   (248 lines)   VERIFIED
07612c4359a2df946eb14017a932f515512d3fde7e2eaca802384232cd54111c  tools/cyc46_35.drat   (285 lines)   VERIFIED
9766482f9be3b18a3cf588c1667c7997666f8e1a57cb2d9d1d3596f084a210e1  tools/cyc46_36.drat   (152 lines)   VERIFIED
39feeec7b9061a1ff05d26a6f099f656489849684d2f53cb8d45a9ba6a0e9545  tools/cyc46_37.drat   (333 lines)   VERIFIED
3dc100a43188a302a8ae4a48f855b055d585ecb4d22e37e46f48bbb84ec04023  tools/cyc46_38.drat   (303 lines)   VERIFIED
77e5e9b19547840046843dd1e12421ff235f7121545903e0e9b0a3c8463c152b  tools/cyc46_39.drat   (299 lines)   VERIFIED
bfe93119c7a49f927a1a91b363e154c854f01f75e296c0bddf197c495233c151  tools/cyc46_40.drat   (276 lines)   VERIFIED
```

### Exoo-extension instance and its certificates(UNSAT,VERIFIED}
```
2b5735a4d1cd405659952c2a160f1fb568539e4b5caef25a45ddd23897fb4bfe  tools/ext42.cnf       (42 vars,2318 clauses}
683c7cf528c1c2221b8fd8585f1264fa5c35ac7a2f82174d51be6bb718dddad3  tools/prova_glucose4.drat    (92 lines) VERIFIED
2c6d2dd10f8ad01574ff8519c20bfa57bc06f180cefcb0eb31c587f6cec6baf2  tools/prova_lingeling.drat     (139 lines) VERIFIED
41886e4c5c43997853f196deffd9b1f043417c487844e5f854e64ab5cd85ec14  tools/prova_maplechrono.drat    (116 lines) VERIFIED
ddb543238b9eaa13ec1b402fc638efd2e77e522e208c24bf2405cc43fcb08f9f  tools/prova_cadical195.drat    (131 lines) NOT a valid DRAT for this checker (reported for completeness;no claim rests on it)
```

## Honest limits of this package

1. The claims concern cyclic families and one specific graph -- they do NOT
   settle R(5,5) or R(4,6).
2. DRAT certificates validate both the (5,5)-cyclic family (cyc_42..48.drat)
   and the (4,6)-cyclic family (cyc46_34..40.drat,generated 2026-09-20
   with the same pipeline),all VERIFIED with `drat-trim`.
3. The CDCL portfolio on K_43 (32 workers x 12 h ~  384 h CPU)and the local-search
   calibration runs carried NO certificate and are deliberately NOT reproducible
   takeaways;they are reported as non-results in the note,never as evidence.
4. A symmetric consequence(no vertex-transitive witnesses on 37,43,47
   vertices)comes from the prime-order circulant lemma,not from computation alone.