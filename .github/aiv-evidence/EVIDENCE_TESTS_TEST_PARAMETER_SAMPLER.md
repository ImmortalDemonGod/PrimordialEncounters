# AIV Evidence File (v1.0)

**File:** `tests/test_parameter_sampler.py`
**Commit:** `1ef895e`
**Generated:** 2026-07-05T08:04:59Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_parameter_sampler.py"
  classification_rationale: "critical - wrong constant invalidates all downstream N-body simulations"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-05T08:04:59Z"
```

## Claim(s)

1. Tests verify KM_S_TO_AU_DAY constant is correct (should be 86400/1.496e8 ≈ 5.78e-4, not 86400/1.731e6 ≈ 0.05)
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24)
- **Requirements Verified:** F017: KM_S_TO_AU_DAY conversion constant is wrong by a factor of ~86

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`1ef895e`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/1ef895e58d4b2f1950d89db4109f801ca88600ce))

- [`tests/test_parameter_sampler.py#L1-L107`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/1ef895e58d4b2f1950d89db4109f801ca88600ce/tests/test_parameter_sampler.py#L1-L107)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_km_s_to_au_day_equals_documented_value`** (L1-L107): FAIL -- WARNING: No tests import or call `test_km_s_to_au_day_equals_documented_value`
- **`test_sample_velocity_magnitude_matches_physical_expectation`** (unknown): FAIL -- WARNING: No tests import or call `test_sample_velocity_magnitude_matches_physical_expectation`
- **`test_km_s_to_au_day_matches_formula_from_comment`** (unknown): FAIL -- WARNING: No tests import or call `test_km_s_to_au_day_matches_formula_from_comment`
- **`test_sample_velocity_rejects_nonpositive_sigma`** (unknown): FAIL -- WARNING: No tests import or call `test_sample_velocity_rejects_nonpositive_sigma`
- **`test_km_s_to_au_day_round_trip`** (unknown): FAIL -- WARNING: No tests import or call `test_km_s_to_au_day_round_trip`

**Coverage summary:** 0/5 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 36 error(s)
- **mypy:** Found 2 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Tests verify KM_S_TO_AU_DAY constant is correct (should be 8... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/5 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Unit tests for parameter_sampler F017 velocity conversion bug
