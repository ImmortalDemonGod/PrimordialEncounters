# AIV Evidence File (v1.0)

**File:** `src/residual_analysis.py`
**Commit:** `fe7840a`
**Generated:** 2026-06-21T07:00:37Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/residual_analysis.py"
  classification_rationale: "R1: single new function in production module; no call sites modified; blast radius is component-scoped (residual_analysis module)"
  classified_by: "Claude"
  classified_at: "2026-06-21T07:00:37Z"
```

## Claim(s)

1. calculate_q_fom returns callable float; zero residuals → 0.0; k=3 N=4 uniform → 6.0; zero sigma → ValueError
2. calculate_q_fom uses sqrt(sum((res/sigma)^2)) max over time (D2 locked form from finding GOAL + pseudocode.md:333)
3. Input validation raises ValueError for wrong ndim, shape mismatch, or non-positive sigma (D3/D5 locked)
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36)
- **Requirements Verified:** F022 (high/code-intent-mismatch): calculate_q_fom figure-of-merit (paper Eq. 17) is entirely unimplemented — core detection metric missing; audit line 36 records this defect and requires the function be implemented returning a finite scalar

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`fe7840a`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/fe7840a495f976278aa7f8ff44e4168a019f1139))

- [`src/residual_analysis.py#L238-L272`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/fe7840a495f976278aa7f8ff44e4168a019f1139/src/residual_analysis.py#L238-L272)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`calculate_q_fom`** (L238-L272): PASS -- 10 test(s) call `calculate_q_fom` directly
  - `tests/test_residual_analysis.py::test_q_fom_zero_residuals_returns_zero`
  - `tests/test_residual_analysis.py::test_q_fom_uniform_residuals_equals_k_sqrt_N`
  - `tests/test_residual_analysis.py::test_q_fom_hand_computed_small_case`
  - `tests/test_residual_analysis.py::test_q_fom_returns_finite_scalar`
  - `tests/test_residual_analysis.py::test_q_fom_is_time_maximum_not_mean`
  - `tests/test_residual_analysis.py::test_zero_residuals`
  - `tests/test_residual_analysis.py::test_analytic_uniform`
  - `tests/test_residual_analysis.py::test_invalid_zero_sigma`
  - `tests/test_residual_analysis.py::test_empty_timesteps`
  - `tests/test_residual_analysis.py::test_single_sso_single_timestep`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | calculate_q_fom returns callable float; zero residuals → 0.0... | symbol | 10 test(s) call `calculate_q_fom` | PASS VERIFIED |
| 2 | calculate_q_fom uses sqrt(sum((res/sigma)^2)) max over time ... | symbol | 10 test(s) call `calculate_q_fom` | PASS VERIFIED |
| 3 | Input validation raises ValueError for wrong ndim, shape mis... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Implement calculate_q_fom as q_fom=max_t sqrt(sum_i(res[t,i]/sigma[i])^2) per arXiv:2312.17217v3 Eq.17
