# AIV Evidence File (v1.0)

**File:** `src/parameter_sampler.py`
**Commit:** `55658c3`
**Generated:** 2026-07-05T10:33:14Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/parameter_sampler.py"
  classification_rationale: "critical - single constant fix affects all downstream velocity sampling and ensemble runs"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-05T10:33:14Z"
```

## Claim(s)

1. KM_S_TO_AU_DAY constant changed from 1.0/1.731e6*86400.0 (~0.0499) to 86400.0/1.496e8 (~5.78e-4), fixing the ~86x velocity overestimation bug
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/a849b88a021ebbf97bb5178d2c159ab79ed97c45/audit/02-static-audit.md#L24)
- **Requirements Verified:** Fix the KM_S_TO_AU_DAY constant at src/parameter_sampler.py:11 to produce physically plausible velocity magnitudes ~0.1-0.25 AU/day for sigma_v=200 km/s

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`55658c3`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/55658c39dab7d78ce36a1937e3ef6cee386dee0f))

- [`src/parameter_sampler.py#L11`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/55658c39dab7d78ce36a1937e3ef6cee386dee0f/src/parameter_sampler.py#L11)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`<module>`** (L11): FAIL -- WARNING: No tests import or call `<module>`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 24 error(s)
- **mypy:** Found 2 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | KM_S_TO_AU_DAY constant changed from 1.0/1.731e6*86400.0 (~0... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Fixed KM_S_TO_AU_DAY constant from wrong divisor 1.731e6 to correct 1.496e8
