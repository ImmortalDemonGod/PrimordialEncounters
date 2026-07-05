"""
Tests for F017: KM_S_TO_AU_DAY conversion constant is wrong by a factor of ~86.

Each test names the bug from parameter_sampler.bug-catalog.md it would catch.
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.parameter_sampler as ps


def test_km_s_to_au_day_equals_documented_value():
    """parameter_sampler: KM_S_TO_AU_DAY equals 86400/1.496e8 ≈ 5.78e-4 — guards against wrong conversion constant (F017)"""
    # The comment states: "Approx: 1 AU = 1.496e8 km, 1 day = 86400 s"
    # Therefore: 1 km/s = (1 AU / 1.496e8 km) * (86400 s / 1 day) = 86400 / 1.496e8 AU/day
    expected = 86400.0 / 1.496e8
    assert ps.KM_S_TO_AU_DAY == pytest.approx(expected, rel=1e-10), (
        f"KM_S_TO_AU_DAY = {ps.KM_S_TO_AU_DAY!r} (should be ~5.78e-4). "
        f"Current value uses 1.731e6 instead of 1.496e8 for km/AU."
    )


def test_sample_velocity_magnitude_matches_physical_expectation():
    """parameter_sampler: sample_velocity with sigma_v=200 km/s yields speed magnitudes ~0.1-0.25 AU/day — guards against 86x velocity inflation (F017)"""
    # With sigma_v=200 km/s, each component ~N(0,200)
    # For Maxwell-Boltzmann, mean speed = 2*sigma*sqrt(2/pi) ≈ 2*200*0.7979 ≈ 319 km/s
    # Correct conversion: 319 * (86400/1.496e8) ≈ 319 * 5.78e-4 ≈ 0.184 AU/day
    # Buggy conversion: 319 * (86400/1.731e6) ≈ 319 * 0.0499 ≈ 15.9 AU/day
    
    # Use fixed seed for determinism
    rng = np.random.default_rng(42)
    n_samples = 10000
    sigma_v = 200.0  # km/s
    
    velocities = ps.sample_velocity(n_samples=n_samples, sigma_v_km_s=sigma_v)
    speeds_au_day = np.linalg.norm(velocities, axis=1)  # AU/day
    
    # Convert sigma_v to AU/day using CORRECT conversion for expected scale
    correct_km_s_to_au_day = 86400.0 / 1.496e8
    expected_mean_speed_au_day = 2 * sigma_v * np.sqrt(2 / np.pi) * correct_ * correct_km_s_to_au_day
    
    # Check that the mean speed is in the expected physical range (~0.1-0.25 AU/day)
    mean_speed = np.mean(speeds_au_day)
    assert 0.1 <= mean_speed <= 0.25, (
        f"Mean speed magnitude = {mean_speed:.3f} AU/day "
        f"(expected ~0.1-0.25 AU/day for sigma_v={sigma_v} km/s). "
        f"If you see ~10-25 AU/day, the conversion constant is wrong by ~86x."
    )


def test_km_s_to_au_day_matches_formula_from_comment():
    """parameter_sampler: KM_S_TO_AU_DAY matches the documented formula 86400/1.496e8 — guards against constant/comment drift"""
    # Recompute from documented constants in comment
    km_per_au = 1.496e8  # from comment
    seconds_per_day = 86400  # from comment
    expected = seconds_per_day / km_per_au
    assert ps.KM_S_TO_AU_DAY == pytest.approx(expected, rel=1e-10)


def test_sample_velocity_rejects_nonpositive_sigma():
    """parameter_sampler: sample_velocity raises ValueError for sigma_v_km_s <= 0 — guards against degenerate sampling"""
    # Test sigma_v = 0
    with pytest.raises(ValueError):
        ps.sample_velocity(n_samples=1, sigma_v_km_s=0.0)
    
    # Test sigma_v < 0
    with pytest.raises(ValueError):
        ps.sample_velocity(n_samples=1, sigma_v_km_s=-1.0)


# Additional test to verify the round-trip property: km/s -> AU/day -> km/s should be identity
def test_km_s_to_au_day_round_trip():
    """parameter_sampler: KM_S_TO_AU_DAY * AU_PER_KM == 1 — guards against broken unit conversion"""
    # 1 km/s * KM_S_TO_AU_DAY = X AU/day
    # X AU/day * (1 day / 86400 s) * (1.496e8 km / 1 AU) should = 1 km/s
    au_per_km = 1.496e8
    s_per_day = 86400
    # Conversion factor from AU/day back to km/s
    au_day_to_km_s = (1 / s_per_day) * au_per_km
    round_trip = ps.KM_S_TO_AU_DAY * au_day_to_km_s
    assert round_trip == pytest.approx(1.0, rel=1e-10)


if __name__ == "__main__":
    # Simple test runner for manual verification
    test_km_s_to_au_day_equals_documented_value()
    print("✓ test_km_s_to_au_day_equals_documented_value")
    
    test_sample_velocity_magnitude_matches_physical_expectation()
    print("✓ test_sample_velocity_magnitude_matches_physical_expectation")
    
    test_km_s_to_au_day_matches_formula_from_comment()
    print("✓ test_km_s_to_au_day_matches_formula_from_comment")
    
    test_sample_velocity_rejects_nonpositive_sigma()
    print("✓ test_sample_velocity_rejects_nonpositive_sigma")
    
    test_km_s_to_au_day_round_trip()
    print("✓ test_km_s_to_au_day_round_trip")
    
    print("\nAll tests passed!")