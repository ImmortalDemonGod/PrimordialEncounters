# AIV Evidence File (v1.0)

**File:** `src/simulation_runner.py`
**Commit:** `3b347fc`
**Generated:** 2026-07-07T16:26:03Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/simulation_runner.py"
  classification_rationale: "R1"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-07T16:26:03Z"
```

## Claim(s)

1. implements the converged plan for the finding per its acceptance condition
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L21](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L21)
- **Requirements Verified:** write-code: implement the converged plan within scope

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3b347fc`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/3b347fc89792f2563ac8274dde7c73c49cc9551a))

- [`src/simulation_runner.py#L84`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/3b347fc89792f2563ac8274dde7c73c49cc9551a/src/simulation_runner.py#L84)
- [`src/simulation_runner.py#L91`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/3b347fc89792f2563ac8274dde7c73c49cc9551a/src/simulation_runner.py#L91)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`run_single_simulation`** (L84): PASS -- 1 test(s) call `run_single_simulation` directly
  - `tests/test_primordial_f004_walk.py::test_run_single_simulation_pbh_key_aliasing`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 49 error(s)
- **mypy:** Found 3 errors in 2 files (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | implements the converged plan for the finding per its accept... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

simulation_runner.py for the finding
