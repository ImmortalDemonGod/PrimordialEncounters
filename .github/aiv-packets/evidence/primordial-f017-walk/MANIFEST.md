# Evidence Manifest for F017: KM_S_TO_AU_DAY Conversion Constant Fix

**Cited Baseline**: `origin/master` at `a849b88a021ebbf97bb5178d2c159ab79ed97c45` (audit/02-static-audit.md#L24)
**Fixed Branch**: `fix/primordial-f017-walk` at HEAD
**Canonical Intent (Class E)**: https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24

---

## Artifacts

| Path | SHA256 | Claim Supported | Cited Baseline Ref |
|------|--------|-----------------|-------------------|
| `baseline_output.txt` | `90e545114aed8d898f34a72b867ebe71f95c752d18b6d40f5b13d02524281e5e` | C1: Baseline produces velocity magnitudes ~10-25 AU/day (buggy) | `origin/master:a849b88` src/parameter_sampler.py:11 |
| `head_output.txt` | `467281575ded04a6ed77485f3ea64aa24ab79af3bec8da39e9cabee1933d9be2` | C2: HEAD produces velocity magnitudes ~0.1-0.25 AU/day (fixed) | HEAD src/parameter_sampler.py:11 |
| `baseline_constant.txt` | `67566679cbdde37506e4bf6d8add69cb22a9b00f4f07695c2d460bc5d39bb40c` | C3: Baseline constant = 0.0499... (wrong by ~86x) | `origin/master:a849b88` src/parameter_sampler.py:11 |
| `constant_verification.txt` | `38dd9388645c08b3d7c4e394a0e506bc8bebd917d98db39788439c93c7d1aea3` | C4: Correct constant = 86400/1.496e8 ≈ 5.78e-4 | `python -c "print(86400/1.496e8)"` |
| `baseline_tests.txt` | `d1997f3d92811c62821e64d0643c14ca10f88a1ada61f9c3f27be83ccc5ce764` | C5: Baseline tests FAIL (exposing the bug) | `origin/master:a849b88` tests/test_parameter_sampler.py |
| `head_tests.txt` | `b2bf1d539bd03cd4e05a9922306ab9efac7219eca05727e6187d05ed8e399184` | C6: HEAD tests PASS (fix verified) | HEAD tests/test_parameter_sampler.py |

---

## Behavioral Claims (from Finding F017)

| Claim ID | Claim | Baseline Behavior | HEAD Behavior | Status |
|----------|-------|-------------------|---------------|--------|
| C1 | `python -m src.parameter_sampler` produces sampled velocity magnitudes ~10-25 AU/day for sigma_v~200 km/s | ✓ Confirmed (baseline_output.txt) | — | **PASS** |
| C2 | `python -m src.parameter_sampler` produces sampled velocity magnitudes ~0.1-0.25 AU/day for sigma_v~200 km/s | — | ✓ Confirmed (head_output.txt) | **PASS** |
| C3 | Baseline KM_S_TO_AU_DAY = 1.0/1.731e6 * 86400 ≈ 0.0499 (wrong by ~86x) | ✓ Confirmed (baseline_constant.txt) | — | **PASS** |
| C4 | Correct KM_S_TO_AU_DAY = 86400/1.496e8 ≈ 5.78e-4 | — | ✓ Confirmed (constant_verification.txt) | **PASS** |
| C5 | Design tests FAIL on baseline (exposing the ~86x bug) | ✓ Confirmed (baseline_tests.txt) | — | **PASS** |
| C6 | Design tests PASS on HEAD (fix verified) | — | ✓ Confirmed (head_tests.txt) | **PASS** |

---

## AIV Evidence Class Binding

| Class | Artifact(s) | Status |
|-------|-------------|--------|
| **A (Execution)** | `head_tests.txt`, `baseline_tests.txt`, `head_output.txt`, `baseline_output.txt` | Real test runs & module executions captured |
| **B (Referential)** | All artifacts SHA256-pinned; claim→artifact map in table above | Line-anchored to cited baseline SHA `a849b88` |
| **C (Negative)** | `baseline_tests.txt` shows all 3 design tests FAIL on baseline; no other failure modes found in searched paths (`src/parameter_sampler.py`, `tests/test_parameter_sampler.py`) | Scope searched: `src/parameter_sampler.py`, `tests/test_parameter_sampler.py` |
| **D (Differential)** | Before/after pairs: `baseline_output.txt` vs `head_output.txt`, `baseline_constant.txt` vs `constant_verification.txt`, `baseline_tests.txt` vs `head_tests.txt` | All bound to base SHA `a849b88` and HEAD |
| **E (Intent)** | Canonical finding: https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24 | Immutable at cited SHA |
| **F (Provenance)** | This MANIFEST.md + sha256 hashes above; git worktree for baseline at `origin/master:a849b88` | Full chain-of-custody via worktree + hash manifest |

---

## Anti-Theater Verification (Gate 3)

- **Adversarial probe**: Baseline module execution (`baseline_output.txt`) produces velocities ~10-25 AU/day — confirmed ~86x higher than physical expectation (~0.1-0.25 AU/day). No adjacent code path produces this artifact; it exercises the exact `sample_velocity()` → `KM_S_TO_AU_DAY` multiplication at line 43-45 of `src/parameter_sampler.py`.
- **Independent assessor (cold read)**: Artifacts `baseline_output.txt` vs `head_output.txt` show velocity vectors dropping from O(10) to O(0.1) AU/day — a factor of ~86, matching the constant ratio `0.0499 / 0.000578 ≈ 86.4`. The constant verification artifacts confirm the exact mathematical error (1.731e6 vs 1.496e8 denominator).
- **No component-stub theater**: All executions run the composed system (`python -m src.parameter_sampler`, `pytest tests/test_parameter_sampler.py`) against real installed package, not mocked units.

---

## Per-Claim Verdict

| Claim | Verdict | Artifact |
|-------|---------|----------|
| C1: Baseline buggy velocities ~10-25 AU/day | **PASS** | `baseline_output.txt` |
| C2: HEAD fixed velocities ~0.1-0.25 AU/day | **PASS** | `head_output.txt` |
| C3: Baseline constant wrong (~0.0499) | **PASS** | `baseline_constant.txt` |
| C4: Correct constant ~5.78e-4 | **PASS** | `constant_verification.txt` |
| C5: Baseline tests FAIL | **PASS** | `baseline_tests.txt` |
| C6: HEAD tests PASS | **PASS** | `head_tests.txt` |

**Unverified count: 0** — All 6 behavioral claims have independently verifiable artifacts.