# AIV Evidence File (v1.0)

**File:** `tests/parameter_sampler.bug-catalog.md`
**Commit:** `1ef895e`
**Generated:** 2026-07-05T08:00:42Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/parameter_sampler.bug-catalog.md"
  classification_rationale: "critical - wrong constant invalidates all downstream N-body simulations"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-05T08:00:42Z"
```

## Claim(s)

1. The bug catalog enumerates 4 bugs in parameter_sampler.py, with the primary bug being KM_S_TO_AU_DAY constant off by ~86x (F017)
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24)
- **Requirements Verified:** F017: KM_S_TO_AU_DAY conversion constant is wrong by a factor of ~86

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`1ef895e`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/1ef895e58d4b2f1950d89db4109f801ca88600ce))

- [`tests/parameter_sampler.bug-catalog.md#L1-L104`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/1ef895e58d4b2f1950d89db4109f801ca88600ce/tests/parameter_sampler.bug-catalog.md#L1-L104)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | The bug catalog enumerates 4 bugs in parameter_sampler.py, w... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for parameter_sampler F017 velocity conversion bug
