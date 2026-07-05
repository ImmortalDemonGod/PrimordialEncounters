# AIV Evidence File (v1.0)

**File:** `tests/test_parameter_sampler.py`
**Commit:** `62956b5`
**Previous:** `62956b5`
**Generated:** 2026-07-05T08:05:40Z
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
  classified_at: "2026-07-05T08:05:40Z"
```

## Claim(s)

1. Fixed typo in variable name that caused NameError
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24)
- **Requirements Verified:** F017: KM_S_TO_AU_DAY conversion constant is wrong by a factor of ~86

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`62956b5`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/62956b5a7187d78213dd08361f1e8ed16d2e2248))

- [`tests/test_parameter_sampler.py#L46`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/62956b5a7187d78213dd08361f1e8ed16d2e2248/tests/test_parameter_sampler.py#L46)
- [`tests/test_parameter_sampler.py#L49-L50`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/62956b5a7187d78213dd08361f1e8ed16d2e2248/tests/test_parameter_sampler.py#L49-L50)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_sample_velocity_magnitude_matches_physical_expectation`** (L46): FAIL -- WARNING: No tests import or call `test_sample_velocity_magnitude_matches_physical_expectation`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 25 error(s)
- **mypy:** Found 2 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Fixed typo in variable name that caused NameError | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Fix test variable name typo
