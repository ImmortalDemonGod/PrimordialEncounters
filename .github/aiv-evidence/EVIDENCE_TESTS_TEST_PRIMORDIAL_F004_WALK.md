# AIV Evidence File (v1.0)

**File:** `tests/test_primordial_f004_walk.py`
**Commit:** `546fe629995f`
**Generated:** 2026-07-07T16:05:12Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_primordial_f004_walk.py"
  classification_rationale: "R1"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-07T16:05:12Z"
```

## Claim(s)

1. RED test pins the finding's defect against the cited baseline
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L21](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L21)
- **Requirements Verified:** design-tests: a failing test that names the finding's defect

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`546fe629995f`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/546fe629995f26fd26addb769ee4fb373b72594b0f5e0))

- [`tests/test_primordial_f004_walk.py#L1-L54`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/546fe629995f26fd26addb769ee4fb373b72594b0f5e0/tests/test_primordial_f004_walk.py#L1-L54)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_run_single_simulation_pbh_key_aliasing`** (L1-L54): FAIL -- WARNING: No tests import or call `test_run_single_simulation_pbh_key_aliasing`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 13 error(s)
- **mypy:** Found 5 errors in 3 files (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | RED test pins the finding's defect against the cited baselin... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

test_primordial_f004_walk.py for the finding
