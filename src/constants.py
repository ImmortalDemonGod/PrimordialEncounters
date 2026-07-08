"""
Physical and unit-conversion constants, derived from their official sources.

Every value here comes from `scipy.constants` (already a project dependency),
which carries the CODATA-recommended values and the IAU 2012 exact definition
of the astronomical unit (Resolution B2: 1 au = 149 597 870 700 m, exactly).
No constant in this module is hand-typed from memory: audit finding F017 — a
km/s -> AU/day conversion built on a hand-derived divisor (1.731e6, ~86x off)
— is the failure mode this module exists to prevent.

Modules should import their unit conversions from here rather than re-deriving
them inline. Migration of the remaining inline constants (e.g. the ~820x
velocity constant in analytic_impulse, audit finding F018) is follow-up work.
"""

from scipy import constants as _sc

# --- Official base values ----------------------------------------------------
ASTRONOMICAL_UNIT_KM = _sc.au / 1000.0             # 149_597_870.7 km — IAU 2012 exact
SECONDS_PER_DAY = _sc.day                          # 86_400.0 s (SI)
DAYS_PER_JULIAN_YEAR = _sc.Julian_year / _sc.day   # 365.25 — IAU Julian year

# --- Derived unit conversions --------------------------------------------------
# 1 km/s expressed in AU/day: (86 400 s/day) / (149 597 870.7 km/AU) ≈ 5.7755e-4
KILOMETERS_PER_SECOND_TO_ASTRONOMICAL_UNITS_PER_DAY = SECONDS_PER_DAY / ASTRONOMICAL_UNIT_KM
