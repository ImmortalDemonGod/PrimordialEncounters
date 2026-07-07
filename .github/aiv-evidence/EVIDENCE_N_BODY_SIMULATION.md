# AIV Evidence File (v1.0)

**File:** `src/n_body_simulation.py`
**Commit:** `cd48eb7`
**Previous:** `659fd42`
**Generated:** 2026-07-07T16:25:56Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/n_body_simulation.py"
  classification_rationale: "R1"
  classified_by: "Miguel Ingram"
  classified_at: "2026-07-07T16:25:56Z"
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

**Scope Inventory** (SHA: [`cd48eb7`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc))

- [`src/n_body_simulation.py#L31-L32`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L31-L32)
- [`src/n_body_simulation.py#L88-L89`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L88-L89)
- [`src/n_body_simulation.py#L91-L96`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L91-L96)
- [`src/n_body_simulation.py#L117`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L117)
- [`src/n_body_simulation.py#L119-L120`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L119-L120)
- [`src/n_body_simulation.py#L182-L183`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L182-L183)
- [`src/n_body_simulation.py#L269-L272`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L269-L272)
- [`src/n_body_simulation.py#L274`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/cd48eb7733d60a0e56b09dcd4a232d1f63e277dc/src/n_body_simulation.py#L274)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`NBodySimulation`** (L31-L32): FAIL -- WARNING: 1 file(s) import `NBodySimulation` but 0 tests call it directly
  - Imported by: `tests/test_n_body_simulation.py`
- **`NBodySimulation.__init__`** (L88-L89): FAIL -- WARNING: No tests import or call `__init__`
- **`NBodySimulation.add_solar_system`** (L91-L96): FAIL -- WARNING: No tests import or call `add_solar_system`
- **`NBodySimulation.add_pbh`** (L117): FAIL -- WARNING: No tests import or call `add_pbh`
- **`NBodySimulation.get_particle_state`** (L119-L120): FAIL -- WARNING: No tests import or call `get_particle_state`
- **`NBodySimulation.apply_analytic_kick`** (L182-L183): FAIL -- WARNING: No tests import or call `apply_analytic_kick`

**Coverage summary:** 0/6 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 35 error(s)
- **mypy:** Found 1 error in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | implements the converged plan for the finding per its accept... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/6 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

n_body_simulation.py for the finding
