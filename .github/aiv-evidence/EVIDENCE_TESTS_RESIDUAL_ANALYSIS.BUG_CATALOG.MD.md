# AIV Evidence File (v1.0)

**File:** `tests/residual_analysis.bug-catalog.md`
**Commit:** `007805c`
**Generated:** 2026-06-21T06:25:25Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/residual_analysis.bug-catalog.md"
  classification_rationale: "R0: documentation artifact only, no code logic, no test suite impact"
  classified_by: "Claude"
  classified_at: "2026-06-21T06:25:25Z"
```

## Claim(s)

1. Bug catalog documents 5 bugs (B1-B5) for calculate_q_fom with blast-radius rankings and test mappings
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36)
- **Requirements Verified:** F022 requires designing tests before implementing calculate_q_fom; catalog is the design artifact

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`007805c`](https://github.com/ImmortalDemonGod/PrimordialEncounters/tree/007805c05a2d3eaf9b5c32197bf47c7602e92d77))

- [`tests/residual_analysis.bug-catalog.md#L1-L126`](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/007805c05a2d3eaf9b5c32197bf47c7602e92d77/tests/residual_analysis.bug-catalog.md#L1-L126)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Bug catalog is a markdown documentation file; no code execution needed


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Bug catalog is a markdown documentation file; no code execution needed
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

F022 bug catalog: maps missing calculate_q_fom to 5 plausible bugs with 6 planned tests
