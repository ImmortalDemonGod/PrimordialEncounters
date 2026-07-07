# AIV Evidence File (v1.0)

**File:** `tests/primordial-f004-walk.bug-catalog.md`
**Commit:** `659fd42`
**Generated:** 2026-07-07T16:05:08Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/primordial-f004-walk.bug-catalog.md"
  classification_rationale: "R1"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-07T16:05:08Z"
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

**Scope Inventory** (SHA: [`659fd42`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/659fd42e56f35a9c1e7d3886f172e19bc4c051b2))

- [`tests/primordial-f004-walk.bug-catalog.md#L1-L15`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/659fd42e56f35a9c1e7d3886f172e19bc4c051b2/tests/primordial-f004-walk.bug-catalog.md#L1-L15)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | RED test pins the finding's defect against the cited baselin... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

primordial-f004-walk.bug-catalog.md for the finding
