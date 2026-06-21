# AIV Evidence File (v1.0)

**File:** `tests/test_residual_analysis.py`
**Commit:** `dd6e9c8`
**Generated:** 2026-06-21T06:26:27Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_residual_analysis.py"
  classification_rationale: "R1: new test file only; all 6 tests are intentionally RED (FAIL) because calculate_q_fom is unimplemented — confirmed by local pytest run showing 6 failed 0 passed"
  classified_by: "Claude"
  classified_at: "2026-06-21T06:26:27Z"
```

## Claim(s)

1. All 6 new tests in tests/test_residual_analysis.py FAIL because calculate_q_fom is absent from src.residual_analysis (src/residual_analysis.py:238-240)
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36)
- **Requirements Verified:** F022 goal: calculate_q_fom returns finite scalar; zero residuals gives 0; k*sigma uniform gives k*sqrt(N); hand-computed small case matches

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`dd6e9c8`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/dd6e9c81ff49c0ee8deb5444851e241120a262f1))

- [`tests/test_residual_analysis.py#L1-L132`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/dd6e9c81ff49c0ee8deb5444851e241120a262f1/tests/test_residual_analysis.py#L1-L132)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_require_q_fom`** (L1-L132): PASS -- 5 test(s) call `_require_q_fom` directly
  - `tests/test_residual_analysis.py::test_q_fom_zero_residuals_returns_zero`
  - `tests/test_residual_analysis.py::test_q_fom_uniform_residuals_equals_k_sqrt_N`
  - `tests/test_residual_analysis.py::test_q_fom_hand_computed_small_case`
  - `tests/test_residual_analysis.py::test_q_fom_returns_finite_scalar`
  - `tests/test_residual_analysis.py::test_q_fom_is_time_maximum_not_mean`
- **`test_q_fom_function_exists`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_function_exists`
- **`test_q_fom_zero_residuals_returns_zero`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_zero_residuals_returns_zero`
- **`test_q_fom_uniform_residuals_equals_k_sqrt_N`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_uniform_residuals_equals_k_sqrt_N`
- **`test_q_fom_hand_computed_small_case`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_hand_computed_small_case`
- **`test_q_fom_returns_finite_scalar`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_returns_finite_scalar`
- **`test_q_fom_is_time_maximum_not_mean`** (unknown): FAIL -- WARNING: No tests import or call `test_q_fom_is_time_maximum_not_mean`

**Coverage summary:** 1/7 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | All 6 new tests in tests/test_residual_analysis.py FAIL beca... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/7 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

6 RED tests for F022: zero-residuals, k-sqrt-N invariant, hand-computed case, scalar return, time-max semantics, and existence check
