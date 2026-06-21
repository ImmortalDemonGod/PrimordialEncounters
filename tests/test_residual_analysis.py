"""
RED tests for F022: calculate_q_fom is entirely unimplemented.

Each test names the bug from residual_analysis.bug-catalog.md it would catch.
Interface under test:
    calculate_q_fom(residuals, sigmas) -> float
    residuals : ndarray shape (n_steps, n_bodies), scalar position residual per body per timestep
    sigmas    : ndarray shape (n_bodies,), per-body measurement noise (same units)
    returns   : float, q_fom = max_t sqrt( sum_i (residuals[t,i] / sigmas[i])^2 )
    (paper arXiv:2312.17217v3 Eq. 17; pseudocode docs/pseudocode.md:316-338)

ALL tests are expected RED because calculate_q_fom does not exist (B1).
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.residual_analysis as _mod


def _require_q_fom():
    """Fails immediately with a clear message if the function is still absent (B1)."""
    fn = getattr(_mod, "calculate_q_fom", None)
    if fn is None:
        pytest.fail(
            "B1 (F022): calculate_q_fom not found in src.residual_analysis — "
            "the function is entirely unimplemented (src/residual_analysis.py:238-240)"
        )
    return fn


def test_q_fom_function_exists():
    """B1: calculate_q_fom missing from module — guards against F022 remaining unimplemented."""
    assert hasattr(_mod, "calculate_q_fom"), (
        "B1 (F022): src.residual_analysis has no attribute 'calculate_q_fom'; "
        "the function is commented out at src/residual_analysis.py:238-240"
    )


def test_q_fom_zero_residuals_returns_zero():
    """B1+B4: zero residuals must yield q_fom==0 — guards against missing function and missing sigma normalisation."""
    calculate_q_fom = _require_q_fom()
    n_steps, n_bodies = 10, 3
    residuals = np.zeros((n_steps, n_bodies))
    sigmas = np.array([1e-6, 2e-6, 3e-6])
    result = calculate_q_fom(residuals, sigmas)
    assert result == pytest.approx(0.0, abs=1e-12), (
        f"B1+B4: expected q_fom=0 for zero residuals, got {result!r}"
    )


def test_q_fom_uniform_residuals_equals_k_sqrt_N():
    """B1+B2+B4: residual==k*sigma for all N bodies at all timesteps must give q_fom==k*sqrt(N).

    Derivation: q(t) = sqrt( sum_i (k*sigma_i / sigma_i)^2 ) = sqrt(N*k^2) = k*sqrt(N)
    q_fom = max_t q(t) = k*sqrt(N).
    A missing sqrt (B2) would give k^2*N; missing sigma division (B4) would give a different value.
    """
    calculate_q_fom = _require_q_fom()
    N = 3
    k = 2.5
    sigmas = np.array([1e-6, 2e-6, 0.5e-6])
    # residuals[t, i] = k * sigmas[i] for all t
    residuals = np.outer(np.ones(7), k * sigmas)  # shape (7, 3)
    expected = k * np.sqrt(N)
    result = calculate_q_fom(residuals, sigmas)
    assert result == pytest.approx(expected, rel=1e-10), (
        f"B1+B2+B4: expected q_fom={expected:.6f} (k*sqrt(N)={k}*sqrt({N})), got {result!r}. "
        "A value of k^2*N would indicate missing sqrt (B2); "
        "a value not matching k*sqrt(N) indicates missing sigma normalisation (B4)."
    )


def test_q_fom_hand_computed_small_case():
    """B1+B2+B3+B4: hand-verified 2-body 2-timestep case catches wrong formula, wrong aggregation, and missing normalisation.

    Setup:
      sigmas = [1e-6, 2e-6]
      t=0: residuals = [1e-6, 2e-6]  -> ratios [1, 1] -> q(0) = sqrt(2) ≈ 1.4142
      t=1: residuals = [2e-6, 0.0]   -> ratios [2, 0] -> q(1) = sqrt(4) = 2.0
    q_fom = max(sqrt(2), 2.0) = 2.0
    """
    calculate_q_fom = _require_q_fom()
    residuals = np.array([[1e-6, 2e-6], [2e-6, 0.0]])
    sigmas = np.array([1e-6, 2e-6])
    expected = 2.0
    result = calculate_q_fom(residuals, sigmas)
    assert result == pytest.approx(expected, rel=1e-10), (
        f"B1+B2+B3+B4: expected q_fom=2.0 for hand-computed case, got {result!r}. "
        "Possible causes: missing sqrt (B2), using mean instead of max (B3), "
        "missing sigma normalisation (B4)."
    )


def test_q_fom_returns_finite_scalar():
    """B1+B5: q_fom must be a finite Python/numpy scalar, not an array — guards against returning the full timeseries."""
    calculate_q_fom = _require_q_fom()
    rng = np.random.default_rng(42)
    residuals = rng.random((20, 4)) * 1e-5
    sigmas = np.array([1e-6, 1e-6, 1e-6, 1e-6])
    result = calculate_q_fom(residuals, sigmas)
    assert isinstance(result, (float, np.floating)), (
        f"B1+B5: expected a scalar float, got {type(result).__name__!r} — "
        "B5 would produce an ndarray if the timeseries is returned instead of its max"
    )
    assert np.isfinite(result), (
        f"B1+B5: expected a finite value, got {result!r}"
    )


def test_q_fom_is_time_maximum_not_mean():
    """B1+B3: a single spike at one timestep must dominate — mean would return ~1/n_steps of the spike value.

    Setup: 5 time steps, 2 bodies, all-zero except one spike of 5.0 at t=4 for body0.
    sigma=[1,1] so q(4)=5.0, q(t<4)=0. q_fom must be 5.0, not 5/5=1.0 (mean) or 1.0 (sum/5).
    """
    calculate_q_fom = _require_q_fom()
    n_steps = 5
    residuals = np.zeros((n_steps, 2))
    sigmas = np.array([1.0, 1.0])
    residuals[4, 0] = 5.0  # spike only at final timestep
    expected = 5.0
    result = calculate_q_fom(residuals, sigmas)
    assert result == pytest.approx(expected, rel=1e-10), (
        f"B1+B3: expected q_fom=5.0 (max over time), got {result!r}. "
        "A value near 1.0 indicates time-mean is used instead of time-max (B3)."
    )


# --- Plan §12 required test functions (write-code stage) ---

def test_zero_residuals():
    """Plan §12: zero residuals with unit sigmas must yield q_fom == 0.0 (exact)."""
    residuals = np.zeros((5, 3))
    sigmas = np.ones(3)
    result = _mod.calculate_q_fom(residuals, sigmas)
    assert result == 0.0


def test_analytic_uniform():
    """Plan §12: residual==k*sigma uniformly over N bodies → q_fom == k*sqrt(N).

    k=3, N=4, 1 timestep → expected = 3*sqrt(4) = 6.0 (locked by D2, sqrt form).
    """
    k = 3.0
    N = 4
    sigmas = np.ones(N)
    residuals = np.array([k * sigmas])  # shape (1, 4)
    result = _mod.calculate_q_fom(residuals, sigmas)
    assert abs(result - 6.0) < 1e-10


def test_invalid_zero_sigma():
    """Plan §12 / D3: zero sigma must raise ValueError (division by zero is not silent)."""
    residuals = np.ones((2, 2))
    sigmas = np.array([1.0, 0.0])
    with pytest.raises(ValueError):
        _mod.calculate_q_fom(residuals, sigmas)


def test_empty_timesteps():
    """Plan §12 / D4: empty timestep axis must return 0.0 immediately."""
    residuals = np.zeros((0, 3))
    sigmas = np.ones(3)
    result = _mod.calculate_q_fom(residuals, sigmas)
    assert result == 0.0


def test_single_sso_single_timestep():
    """Plan §12: 1 SSO, 1 timestep, res=2.0, sigma=1.0 → sqrt(2^2) = 2.0 (D2 sqrt form)."""
    residuals = np.array([[2.0]])
    sigmas = np.array([1.0])
    result = _mod.calculate_q_fom(residuals, sigmas)
    assert abs(result - 2.0) < 1e-10
