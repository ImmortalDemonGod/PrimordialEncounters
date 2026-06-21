# Evidence Manifest — F022 (calculate_q_fom unimplemented)

Finding: `src/residual_analysis.py:233` — `calculate_q_fom` entirely unimplemented  
Cited baseline SHA: `7cccbb1f12e1a24566140dce248c07548d7b867b` (origin/master)  
HEAD SHA at capture: `e4c38b7` (fix/primordial-F022)  
Config: `.aiv-workflow.yml` absent — defaults used (evidence_dir=`.github/aiv-packets/evidence`)  
Live-fire boundary: N/A — pure-logic function; no DB/subprocess/network/filesystem infra boundary.

## Artifacts

| Artifact | sha256 | Claim proved | Cited baseline ref | AIV class |
|---|---|---|---|---|
| `baseline_red.txt` | `e16315fff3825a02795cce30c6f44ef9d789e7f4d9e377b5c2568b7970ce9fb1` | Defect EXISTS on baseline (11/11 FAIL — `calculate_q_fom` missing/commented-out) | SHA `7cccbb1` | A, D |
| `head_green.txt` | `d7b7a7687fae2807cf4efb9abd961846313a2700c390dc4140b5c37ca887d221` | Defect GONE at HEAD (11/11 PASS — all four behavioral claims green) | SHA `e4c38b7` | A, D |
| `source_diff_base_to_head.patch` | `cca4e477ff450b6d32ee8ddacd71c509cda74ca65ef30e1eed03877f0195ba9f` | Before/after diff of `src/residual_analysis.py` pinned to baseline → HEAD | SHA `7cccbb1`→`e4c38b7` | D, F |

## Claims

| # | Claim | Artifact(s) | Verdict |
|---|---|---|---|
| C1 | `calculate_q_fom` returns a finite scalar for a residual+noise input | `head_green.txt` `test_q_fom_returns_finite_scalar` PASS | PASS |
| C2 | For zero residuals, q_fom == 0 | `head_green.txt` `test_q_fom_zero_residuals_returns_zero` + `test_zero_residuals` PASS | PASS |
| C3 | For residual==k*sigma uniformly over N points, q_fom == k*sqrt(N) | `head_green.txt` `test_q_fom_uniform_residuals_equals_k_sqrt_N` + `test_analytic_uniform` PASS | PASS |
| C4 | Unit test against hand-computed 2-body 2-timestep small case matches 2.0 | `head_green.txt` `test_q_fom_hand_computed_small_case` PASS | PASS |

## Anti-theater gate

Adversarial probe agent (`a1f5465adb2cd59b8`) ran independently on the SHIP artifacts.  
Result: `overall_theater_detected: false` — no stale .pyc, no monkey-patching, no stub-calling.  
All 4 claims: `refuted: false`.

## AIV Class Summary

| Class | Status | Evidence |
|---|---|---|
| **A** Execution | REAL | `baseline_red.txt` (11 FAIL at 7cccbb1); `head_green.txt` (11 PASS at HEAD) |
| **B** Referential | REAL | Each artifact SHA-pinned above; claim→artifact map in table |
| **C** Negative | N/A | No disallowed pattern surface in this change — pure additive function; scope searched: `src/residual_analysis.py`, `tests/test_residual_analysis.py` |
| **D** Differential | REAL | `source_diff_base_to_head.patch` (base SHA `7cccbb1` → HEAD `e4c38b7`); before: commented-out stub; after: 35-line implementation |
| **E** Intent | REAL | Finding pinned to `https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36` |
| **F** Provenance | REAL | sha256 manifest above; signing infra absent — hashes supplied |
