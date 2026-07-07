- **Symptom**: `KeyError: 'mass'` raised at `src/simulation_runner.py:84` when calling `run_single_simulation()` with `pbh_params` from `generate_pbh_sample()`.
- **Location**: `src/simulation_runner.py:84` — `pbh_mass = pbh_params['mass']`
- **Wrong vs Correct**: Sampler produces key `'mass_msun'`; simulation runner reads `'mass'`. Should read `'mass_msun'` (or sampler should produce `'mass'`).

- **Symptom**: `KeyError: 'impact_param'` (silent fallback to default 100.0 via `.get()`) at `src/simulation_runner.py:90` when calling `run_single_simulation()` with `pbh_params` from `generate_pbh_sample()`.
- **Location**: `src/simulation_runner.py:90` — `pbh_params.get('impact_param', 100.0)`
- **Wrong vs Correct**: Sampler produces key `'impact_param_au'`; simulation runner reads `'impact_param'`. Should read `'impact_param_au'` (or sampler should produce `'impact_param'`).

- **Symptom**: Potential `KeyError: 'velocity_velocity_au_day'` if key mismatch exists there (but current code uses same key name).
- **Location**: `src/simulation_runner.py:86` — `pbh_params['velocity_au_day']`
- **Wrong vs Correct**: Sampler produces `'velocity_au_day'`; simulation runner reads `'velocity_au_day'`. Currently matching, but should be verified.

- **Symptom**: Potential `KeyError:'t_encounter_years'` if key mismatch exists there.
- **Location**: Not directly read in `run_single_simulation()` but passed to `apply_analytic_kick()`.
- **Wrong vs Correct**: Sampler produces `'t_encounter_years'`; should verify consistency with `apply_analytic_kick()` expectations.