"""
Tests for F017: the km/s -> AU/day conversion constant was wrong by a factor of ~86.

The constant under test was named KM_S_TO_AU_DAY when the finding was filed; it is
now `kilometers_per_second_to_astro_units_per_day` and is derived from official
values in src/constants.py (scipy.constants: IAU 2012 exact astronomical unit),
rather than hand-typed.

Each test names the bug from parameter_sampler.bug-catalog.md it would catch.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.constants as constants
import src.parameter_sampler as ps


@pytest.fixture
def seeded_global_rng():
    """Seed the GLOBAL numpy RNG.

    sample_velocity reads np.random directly (not a passed-in Generator), so a
    default_rng instance cannot influence it — seeding must happen on the global
    state for sampling tests to be deterministic (CodeRabbit finding on PR #14).
    """
    np.random.seed(42)


def test_conversion_constant_derives_from_official_sources():
    """parameter_sampler: km/s->AU/day constant equals the scipy.constants-derived
    value (IAU 2012 exact au) — a hand-typed approximation cannot satisfy this (F017)."""
    assert (
        ps.kilometers_per_second_to_astro_units_per_day
        == constants.KILOMETERS_PER_SECOND_TO_AU_PER_DAY
    )
    expected = constants.SECONDS_PER_DAY / constants.ASTRONOMICAL_UNIT_KM
    assert ps.kilometers_per_second_to_astro_units_per_day == pytest.approx(expected, rel=1e-12)
    # Magnitude sanity: ~5.78e-4. The pre-fix value (86400/1.731e6 ~= 0.0499, ~86x
    # too large) can never pass this.
    assert ps.kilometers_per_second_to_astro_units_per_day == pytest.approx(5.7755e-4, rel=1e-3)


def test_sample_velocity_magnitude_matches_physical_expectation(seeded_global_rng):
    """parameter_sampler: sample_velocity with sigma_v=200 km/s should yield speed
    magnitudes ~0.1-0.25 AU/day (buggy 86x constant gave ~10-25 AU/day)."""
    n_samples = 10000
    sigma_v = 200.0  # km/s

    velocities = ps.sample_velocity(n_samples=n_samples, sigma_v_km_s=sigma_v)
    speeds_au_day = np.linalg.norm(velocities, axis=1)  # AU/day

    # Maxwell-Boltzmann mean speed = 2*sigma*sqrt(2/pi) ~= 319 km/s for sigma=200;
    # with the official conversion that is ~0.184 AU/day.
    expected_mean = 2 * sigma_v * np.sqrt(2 / np.pi) * constants.KILOMETERS_PER_SECOND_TO_AU_PER_DAY
    assert 0.1 <= expected_mean <= 0.25  # the window below encodes the same physics

    assert 0.1 <= np.mean(speeds_au_day) <= 0.25, (
        f"Mean speed magnitude = {np.mean(speeds_au_day):.3f} AU/day "
        f"(expected ~0.1-0.25 AU/day for sigma_v={sigma_v} km/s). "
        f"If you see ~10-25 AU/day, the conversion constant is wrong by ~86x."
    )


def test_conversion_round_trip():
    """parameter_sampler: km/s -> AU/day -> km/s must return exactly 1, using the
    same official AU value in both directions."""
    au_day_to_km_s = constants.ASTRONOMICAL_UNIT_KM / constants.SECONDS_PER_DAY
    round_trip = ps.kilometers_per_second_to_astro_units_per_day * au_day_to_km_s
    assert round_trip == pytest.approx(1.0, rel=1e-12)


def test_sample_velocity_rejects_negative_sigma():
    """edge case (issue #25): a negative dispersion propagates numpy's ValueError
    rather than being silently accepted."""
    with pytest.raises(ValueError):
        ps.sample_velocity(n_samples=3, sigma_v_km_s=-1.0)


def test_sample_velocity_zero_sigma_yields_zero_velocities():
    """edge case (issue #25): sigma=0 is degenerate but well-defined — every
    component is exactly 0.0 with shape (n, 3)."""
    v = ps.sample_velocity(n_samples=5, sigma_v_km_s=0.0)
    assert v.shape == (5, 3)
    assert np.all(v == 0.0)


def test_sample_velocity_output_finite_and_shaped(seeded_global_rng):
    """sample_velocity returns finite (n, 3) AU/day values for normal input."""
    v = ps.sample_velocity(n_samples=100, sigma_v_km_s=200.0)
    assert v.shape == (100, 3)
    assert np.all(np.isfinite(v))


if __name__ == "__main__":
    # Simple test runner for manual verification
    test_conversion_constant_derives_from_official_sources()
    print("+ test_conversion_constant_derives_from_official_sources")

    np.random.seed(42)
    test_sample_velocity_magnitude_matches_physical_expectation(None)
    print("+ test_sample_velocity_magnitude_matches_physical_expectation")

    test_conversion_round_trip()
    print("+ test_conversion_round_trip")

    print("\nAll tests passed!")
