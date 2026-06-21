# Bug Catalog — `src/residual_analysis.py` (F022: `calculate_q_fom`)

_Built for finding F022 (high / code-intent-mismatch). Source: [audit/02-static-audit.md L36](https://github.com/ImmortalDemonGod/PrimordialEncounters/blob/7cccbb1f12e1a24566140dce248c07548d7b867b/audit/02-static-audit.md#L36)_

---

## 1. Code summary

**Public interface of `src/residual_analysis.py`:**
- `compute_residuals(baseline_results, perturbed_results, particle_indices=None)` → `(times, pos_res, vel_res)`
- `save_residuals(filepath, times, pos_residuals, vel_residuals, metadata=None, format=FORMAT_NPZ)` → `bool`
- `load_residuals(filepath)` → `(times, pos_res, vel_res, metadata)`
- `calculate_rms(data_residuals)` → `ndarray | None`
- `calculate_peak(data_residuals)` → `ndarray | None`
- `calculate_residual_stats(pos_residuals, vel_residuals)` → `dict`
- **`calculate_q_fom` — commented-out stub at line 238–240; not callable.**

**Load-bearing comments:** Lines 233–240 carry two commented-out stub definitions (the `# TODO` intent). No load-bearing invariant comments exist for `calculate_q_fom` because the function body is absent.

**IO boundaries:** `save_residuals`/`load_residuals` touch the filesystem and use `eval()` on metadata (F001/F026, out of scope here). `calculate_q_fom` is pure numeric computation — no IO.

**Branching points of interest (for `calculate_q_fom` once implemented):**
- Zero-residuals fast path (may short-circuit or produce NaN)
- Time-axis aggregation: `max` vs `mean` vs `sum`
- Formula: `sqrt(sum squares)` vs `sum squares` (paper eq. 17 ambiguity noted in pseudocode)
- Division by sigma: normalization missing entirely

**Type contract:** Pseudocode takes `Residuals` (dict-of-arrays) and `MeasurementSigmas` (dict-of-scalars). Tests adopt a numpy-array interface matching the existing module style:
- `residuals: ndarray, shape (n_steps, n_bodies)` — scalar position residual per body per timestep
- `sigmas: ndarray, shape (n_bodies,)` — per-body measurement noise (same units)
- returns `float` — `q_fom = max_t sqrt( Σᵢ (residuals[t,i]/sigmas[i])² )`

**Existing tests:** `tests/test_n_body_simulation.py` contains only directory-existence checks and a bare-pass placeholder. No physics or numerical tests exist anywhere.

---

## 2. Bug catalog

### B1 — `calculate_q_fom` does not exist (PRIMARY — F022 root cause)

| Field | Value |
|---|---|
| **Bug** | `calculate_q_fom` is entirely absent from `src.residual_analysis`; any import or call raises `AttributeError`/`ImportError`. |
| **Blast radius** | Every downstream consumer (ensemble_runner detection pipeline, parameter recovery, detection rate estimation) cannot call the paper's Eq. 17 detection metric. The substitute peak-threshold in `ensemble_runner.is_detected` is not the paper's methodology. |
| **Why plausible** | Lines 233–240 are commented-out stubs; the function was never written. |
| **Test type** | Captured bug / existence contract pin |
| **Self-critique** | Would this pass for wrong-but-stable output? No — `hasattr` check fails hard. Would this fail under a behavior-preserving refactor? No — a refactor that keeps the function callable passes. |

### B2 — Missing sqrt: returning q² instead of q

| Field | Value |
|---|---|
| **Bug** | Implementation sums squares but omits `sqrt`, returning `Σᵢ (rᵢ/σᵢ)²` instead of `sqrt(Σᵢ (rᵢ/σᵢ)²)`. |
| **Blast radius** | `q_fom` values are squared, invalidating all threshold comparisons and the survival-function fit. For the uniform case the return would be `k²·N` instead of `k·√N`. |
| **Why plausible** | Pseudocode notes "Paper eq. (17) might define q_fom²" — ambiguity invites wrong-direction omission. |
| **Test type** | Captured bug / invariant (uniform-residuals property check) |
| **Self-critique** | Would this pass for wrong-but-stable output? No — `k²·N ≠ k·√N` for k≠1, N>1. |

### B3 — Time-axis mean instead of max

| Field | Value |
|---|---|
| **Bug** | Implementation uses `np.mean(q_timeseries)` or `np.sum(q_timeseries)` instead of `np.max(q_timeseries)`. |
| **Blast radius** | `q_fom` underestimates the true peak signal; detections requiring a sharp transient spike are missed; detection rates are biased low. |
| **Why plausible** | RMS aggregation is a common convention; `calculate_rms` (already implemented in this module) uses `mean` — a copy-paste reflex could use mean here too. |
| **Test type** | Decision table / invariant (time-maximum property) |
| **Self-critique** | A spike at one timestep with mean~0 clearly distinguishes max from mean. Would not fail under a refactor that keeps max semantics. |

### B4 — Missing sigma normalization (divides by 1.0 or omits division)

| Field | Value |
|---|---|
| **Bug** | Implementation computes `Σᵢ rᵢ²` without dividing by `σᵢ²`, treating all bodies as having unit noise. |
| **Blast radius** | `q_fom` is noise-model-agnostic; bodies with large orbits dominate regardless of observational precision, corrupting detection significance. |
| **Why plausible** | Normalization step is easy to overlook when scaffolding the sum loop; the pseudocode variable `sigma_r` must be explicitly threaded through. |
| **Test type** | Differential / invariant (different sigmas produce different q_fom) |
| **Self-critique** | Using sigmas of different magnitudes and checking the ratio catches this. Would pass only if normalization is correctly applied. |

### B5 — Returns a time-series array instead of a scalar

| Field | Value |
|---|---|
| **Bug** | Implementation returns `q_timeseries` (array of shape `(n_steps,)`) rather than `float(max(q_timeseries))`. |
| **Blast radius** | Callers that compare `q_fom > threshold` get `array > threshold` (element-wise bool array), silently producing wrong detection decisions. |
| **Why plausible** | Easy to forget the final `max()` reduction; returning intermediate arrays is a common first draft. |
| **Test type** | Contract pin (return-type check) |
| **Self-critique** | `isinstance(result, (float, np.floating))` is a behavioral assertion on the documented contract, not an implementation detail. |

---

## 3. Skipped bugs (negative space)

| Bug considered | Reason skipped |
|---|---|
| NaN/Inf in input residuals | Edge case outside the F022 scope; the function's invariant under valid inputs is the primary deliverable |
| Zero sigma (division by zero) | Measurement sigmas are caller-supplied and guaranteed positive by the physical model; no defensive check needed inside the core formula |
| Non-numpy dict interface (pseudocode style) | The existing module uses numpy arrays; a dict API would require a separate adaptor layer not implied by F022 |
| Negative residuals | Squared inside the formula; sign is irrelevant to the output |
| Performance / large-array timing | Not a correctness concern for this finding |

---

## 4. Test ↔ bug mapping

| Test | Bug caught |
|---|---|
| `test_q_fom_function_exists` | B1 |
| `test_q_fom_zero_residuals_returns_zero` | B1, B4 |
| `test_q_fom_uniform_residuals_equals_k_sqrt_N` | B1, B2, B4 |
| `test_q_fom_hand_computed_small_case` | B1, B2, B3, B4 |
| `test_q_fom_returns_finite_scalar` | B1, B5 |
| `test_q_fom_is_time_maximum_not_mean` | B1, B3 |

---

## 5. Evaluation (to be filled after test run)

- **Bugs caught** (test failed first run, fix needed): _[to be filled]_
- **Bugs characterized** (test passed first run, behavior pinned): _[to be filled]_
- **Bugs discovered during writing not in original catalog**: _[to be filled]_

---

## 6. Investigation notes

No pass+suspect items; all tests are expected RED because the function is absent (B1 subsumes all others). Once implemented, re-evaluate B2–B5 individually.
