"""
Provenance tests for src/constants.py.

Every value must match its official source (scipy.constants: CODATA values and
the IAU 2012 exact astronomical unit), guarding against regressions of the
F017 class (hand-typed constants drifting from the authoritative value).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scipy import constants as sc

import src.constants as constants


def test_astronomical_unit_is_iau_2012_exact():
    """constants: AU must be the IAU 2012 Resolution B2 exact value (149 597 870 700 m)."""
    assert constants.ASTRONOMICAL_UNIT_KM == 149_597_870.7
    assert constants.ASTRONOMICAL_UNIT_KM == sc.au / 1000.0


def test_seconds_per_day_is_si_exact():
    """constants: the day is exactly 86 400 SI seconds."""
    assert constants.SECONDS_PER_DAY == 86_400.0
    assert constants.SECONDS_PER_DAY == sc.day


def test_days_per_julian_year_is_iau_exact():
    """constants: the IAU Julian year is exactly 365.25 days."""
    assert constants.DAYS_PER_JULIAN_YEAR == 365.25
    assert constants.DAYS_PER_JULIAN_YEAR == sc.Julian_year / sc.day


def test_derived_km_s_to_au_day_conversion_is_consistent():
    """constants: the km/s -> AU/day factor is derived, not typed, and ~5.7755e-4."""
    assert (
        constants.KILOMETERS_PER_SECOND_TO_ASTRONOMICAL_UNITS_PER_DAY
        == constants.SECONDS_PER_DAY / constants.ASTRONOMICAL_UNIT_KM
    )
    assert constants.KILOMETERS_PER_SECOND_TO_ASTRONOMICAL_UNITS_PER_DAY == pytest.approx(5.7755e-4, rel=1e-3)
