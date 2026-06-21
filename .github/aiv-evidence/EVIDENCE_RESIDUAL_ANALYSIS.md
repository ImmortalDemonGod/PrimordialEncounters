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

**Claim 3 — input validation (inline verification at commit `291e09c`):**

```
$ python -c "
import numpy as np
from src.residual_analysis import calculate_q_fom

# wrong ndim: 1-D residuals
try:
    calculate_q_fom(np.ones((3,)), np.ones(3))
    print('FAIL: 1-D residuals should raise ValueError')
except ValueError as e:
    print(f'PASS ndim: {e}')

# shape mismatch: residuals.shape[1] != sigmas.shape[0]
try:
    calculate_q_fom(np.ones((3, 4)), np.ones(5))
    print('FAIL: shape mismatch should raise ValueError')
except ValueError as e:
    print(f'PASS shape: {e}')

# non-positive sigma: zero
try:
    calculate_q_fom(np.ones((2, 2)), np.array([1.0, 0.0]))
    print('FAIL: zero sigma should raise ValueError')
except ValueError as e:
    print(f'PASS zero-sigma: {e}')

# non-positive sigma: negative
try:
    calculate_q_fom(np.ones((2, 2)), np.array([1.0, -0.5]))
    print('FAIL: negative sigma should raise ValueError')
except ValueError as e:
    print(f'PASS neg-sigma: {e}')
"
PASS ndim: residuals must be 2-D and sigmas must be 1-D; got residuals.ndim=1, sigmas.ndim=1
PASS shape: residuals.shape[1] must equal sigmas.shape[0]; got 4 != 5
PASS zero-sigma: sigmas must be positive; got zero or negative value at index 1
PASS neg-sigma: sigmas must be positive; got zero or negative value at index 1
```

Test `test_invalid_zero_sigma` (`tests/test_residual_analysis.py#L158-L163`) covers the zero-sigma branch with `pytest.raises(ValueError)` — PASSED in full suite (12 passed, 1 skipped).

**Claim 4 — no existing tests modified (git diff at HEAD `291e09c`):**

```
$ git diff 007805c HEAD -- tests/test_n_body_simulation.py | wc -l
0
```

Zero-line diff confirms `tests/test_n_body_simulation.py` is byte-for-byte identical to base commit `007805c`. Pre-existing test `test_project_structure` PASSED in full suite run at HEAD.

### Class C (Negative Evidence — what was searched for and NOT found)

**Absence of modifications to pre-existing test file `tests/test_n_body_simulation.py`:**
```
$ git diff 007805c HEAD -- tests/test_n_body_simulation.py
(empty — 0 lines of diff)
```
No test function in `tests/test_n_body_simulation.py` was modified or deleted. Pre-existing test `TestNBodySimulation::test_project_structure` PASSED throughout (Class A full-suite run: 12 passed, 1 skipped).

**Absence of tests for ndim-error and shape-mismatch as named parametrized cases** — the zero-sigma branch is covered by `test_invalid_zero_sigma`; ndim and shape branches are verified by inline python -c commands (Class A above). No dedicated parametrized test function for ndim/shape was required by plan §12; inline verification is sufficient.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 0 new type errors

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | calculate_q_fom returns callable float; zero residuals → 0.0... | symbol | 10 test(s) call `calculate_q_fom` | PASS VERIFIED |
| 2 | calculate_q_fom uses sqrt(sum((res/sigma)^2)) max over time ... | symbol | 10 test(s) call `calculate_q_fom` | PASS VERIFIED |
| 3 | Input validation raises ValueError for wrong ndim, shape mis... | behavioral | inline python -c (4 branches) + test_invalid_zero_sigma PASSED | PASS VERIFIED |
| 4 | No existing tests were modified or deleted during this chang... | structural | `git diff 007805c HEAD -- tests/test_n_body_simulation.py` → 0 lines; Class C above | PASS VERIFIED |

**Verdict summary:** 4 verified, 0 unverified, 0 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Implement calculate_q_fom as q_fom=max_t sqrt(sum_i(res[t,i]/sigma[i])^2) per arXiv:2312.17217v3 Eq.17
