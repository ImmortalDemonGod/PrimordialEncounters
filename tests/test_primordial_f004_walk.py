"""
RED test for F004: PBH mass key mismatch.

The sampler (generate_pbh_sample) produces keys: 'mass_msun', 'impact_param_au',
'velocity_au_day', 't_encounter_years'.

The runner (run_single_simulation) reads: 'mass', 'impact_param' (with default),
'velocity_au_day'.

This test asserts that run_single_simulation accepts the sampler's output directly
without KeyError — the correct behavior after the fix.
"""

import numpy as np
import pytest
from src.simulation_runner import run_single_simulation
from src.parameter_sampler import generate_pbh_sample


def test_run_single_simulation_pbh_key_aliasing():
    """
    Calling run_single_simulation with pbh_params from generate_pbh_sample
    should not raise KeyError on 'mass' or 'impact_param'.
    """
    # Minimal dummy initial conditions for a 3-body system (Sun + 2 planets)
    masses = np.array([1.0, 1e-6, 1e-5])  # M_sun
    positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 5.0, 0.0]])  # AU
    # Circular orbit velocities in REBOUND units (AU / (yr/2pi))
    G_sim = 4 * np.pi**2
    v1 = np.sqrt(G_sim * masses[0] / 1.0)
    v2 = np.sqrt(G_sim * masses[0] / 5.0)
    velocities_rebound = np.array([[0.0, 0.0, 0.0], [0.0, v1, 0.0], [-v2, 0.0, 0.0]])
    # Convert to AU/day for runner input
    from src.n_body_simulation import VELOCITY_DAY_TO_REBOUND
    velocities_au_day = velocities_rebound / VELOCITY_DAY_TO_REBOUND

    t_start = 0.0
    t_end = 0.1  # Short duration
    dt = 0.001
    integrator = 'leapfrog'

    # Generate PBH params from the sampler (produces 'mass_msun', 'impact_param_au', etc.)
    pbh_params = generate_pbh_sample(1)[0]

    # This should NOT raise KeyError: 'mass' or KeyError: 'impact_param'
    # The runner should accept the sampler's key names directly
    args = (positions, velocities_au_day, masses, t_start, t_end, dt, integrator, pbh_params)
    times, positions_out, velocities_out = run_single_simulation(args)

    # Assert the simulation completed (not failed with None returns)
    assert times is not None, "Simulation should complete without KeyError"
    assert positions_out is not None, "Simulation should return positions"
    assert velocities_out is not None, "Simulation should return velocities"
    assert len(times) > 0, "Should have at least one time step"