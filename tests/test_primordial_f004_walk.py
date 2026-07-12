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

def test_particle_labels_resolve_in_particle_data():
    """
    Labels are tracked in NBodySimulation._particle_labels (REBOUND particles carry
    no label attribute), and get_particle_data must resolve from that list — not the
    old dead getattr(p, 'label') pattern that always fell back to 'particle_i'
    (PR #21 review: CodeRabbit + issues #52/#54).
    """
    from src.n_body_simulation import NBodySimulation

    sim = NBodySimulation(integrator='ias15')
    sim.add_pbh(mass=1e-12, position=[10.0, 0.0, 0.0], velocity=[0.0, 1.0, 0.0],
                label='PBH_test')
    data = sim.get_particle_data()
    assert len(data) == 1
    assert data[0]['label'] == 'PBH_test', (
        f"get_particle_data returned label {data[0]['label']!r} — labels must resolve "
        f"from _particle_labels, not a getattr fallback"
    )
    # And the state lookup path agrees
    pos, vel = sim.get_particle_state('PBH_test')
    assert pos is not None and vel is not None


def test_kick_failure_is_reported_pending_issue_31(capsys):
    """
    PINS CURRENT BEHAVIOR: the analytic kick silently no-ops because the runner
    hardcodes target 'body_3', which does not exist for a 3-body input (pre-existing
    finding F006/F021, tracked as issue #31 — out of this PR's scope).

    The perturbed run must still COMPLETE (the F004 fix), and the kick failure must
    at least be REPORTED in output. When issue #31 lands (configurable kick target),
    this test should go red — update it then to assert kick SUCCESS.
    """
    masses = np.array([1.0, 1e-6, 1e-5])
    positions = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 5.0, 0.0]])
    G_sim = 4 * np.pi**2
    v1 = np.sqrt(G_sim * masses[0] / 1.0)
    v2 = np.sqrt(G_sim * masses[0] / 5.0)
    velocities_rebound = np.array([[0.0, 0.0, 0.0], [0.0, v1, 0.0], [-v2, 0.0, 0.0]])
    from src.n_body_simulation import VELOCITY_DAY_TO_REBOUND
    velocities_au_day = velocities_rebound / VELOCITY_DAY_TO_REBOUND

    pbh_params = generate_pbh_sample(1)[0]
    args = (positions, velocities_au_day, masses, 0.0, 0.1, 0.001, 'leapfrog', pbh_params)
    times, positions_out, velocities_out = run_single_simulation(args)

    out = capsys.readouterr().out
    assert times is not None, "Perturbed run must complete despite the kick no-op"
    assert "Kick not applied" in out or "kick application failed" in out.lower(), (
        "The kick no-op (hardcoded 'body_3' target, F006/F021, issue #31) must be "
        "reported in output — silent success would mask an unphysical perturbed run. "
        "If the kick now SUCCEEDS, issue #31 was fixed: update this test to assert success."
    )
