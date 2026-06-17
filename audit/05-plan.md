# 05 — Execution-Ready Plan

_Stage 5. Ordered, dependency-aware change items closing the gap to the Stage-4 goal. Every item links to a finding/goal, names a location, and carries a verification signal. Generated 2026-06-17T19:21:51.289Z._

| ID | Pri | Title | Links | Location | Depends on |
| --- | --- | --- | --- | --- | --- |
| C1 | P0 | Make src/ a real importable package | F049, F030 | `src/__init__.py (new file)` | — |
| C2 | P0 | Convert all intra-package imports to explicit relative imports | F008, F019, F045 | `src/n_body_simulation.py:4; src/simulation_runner.py (imports of n_body_simulation/analytic_impulse); src/ensemble_runner.py (imports of simulation_runner/parameter_sampler); src/visualization.py:510; src/synthetic_data.py (import residual_analysis)` | C1 |
| C3 | P0 | Fix setup.py packaging and remove test tools from runtime deps | F030, F029, F049 | `setup.py:9,10-17` | C1 |
| C4 | P0 | Declare tqdm in requirements.txt | F039 | `requirements.txt:1-5 (Core Dependencies block)` | — |
| C5 | P0 | Fix PBH mass key mismatch between sampler and runner | F004, F016 | `src/simulation_runner.py:84` | C2 |
| C6 | P0 | Fix impact-parameter key so sampled value is not silently discarded | F005 | `src/simulation_runner.py:91` | C2 |
| C7 | P0 | Correct km/s -> AU/day conversion constant (~86x error) | F003, F017 | `src/parameter_sampler.py:11` | C2 |
| C8 | P0 | Restore REBOUND 5.x API compatibility for body setup and particle naming | F009, F006 | `src/n_body_simulation.py: add_solar_system (~line 90-99), add_pbh, apply_analytic_kick (label lookup ~line 214), get_particle_data` | C2 |
| C20 | P0 | Remove nested multiprocessing in ensemble members (daemon crash) | F038 | `src/ensemble_runner.py:64 (run_ensemble_member) and src/simulation_runner.py run_parallel_simulations` | C5, C6, C8 |
| C21 | P0 | Add missing return statement to run_ensemble | F007, F015 | `src/ensemble_runner.py: end of run_ensemble (~line 277)` | C20 |
| C9 | P1 | Stop swallowing body-setup exceptions silently | F009 | `src/n_body_simulation.py:97-99 (add_solar_system try/except)` | C8 |
| C10 | P1 | Remove hardcoded 'body_3' kick target; derive target from configured bodies | F006, F021 | `src/simulation_runner.py:104` | C8 |
| C11 | P1 | Fix inverted analytic velocity-kick direction (repulsive -> attractive) | F011 | `src/analytic_impulse.py:66` | C2 |
| C12 | P1 | Correct unphysical example PBH velocity (~820x too large) | F018 | `src/analytic_impulse.py:104-105` | C7, C11 |
| C13 | P1 | Eliminate PBH perturbation double-counting (live mass AND impulse) | F040 | `src/simulation_runner.py:94-116` | C8, C10, C11 |
| C14 | P1 | Compute physical PBH initial position from encounter geometry | F010, F020 | `src/simulation_runner.py:89-91` | C6, C13, C15 |
| C15 | P1 | Sample PBH approach-direction angles so encounter geometry is complete | F037 | `src/parameter_sampler.py: generate_pbh_sample (~line 85)` | C7 |
| C18 | P1 | Preserve pre-encounter (t_start) state across post-kick array reallocation | F041 | `src/simulation_runner.py:126-133` | C13 |
| C22 | P1 | Make summaries/checkpoints/results JSON-serializable (numpy types) | F012 | `src/ensemble_runner.py:136, 249, 263 (json.dump calls)` | C20 |
| C23 | P1 | Fix detection-rate denominator inflation by unclassifiable members | F046 | `src/ensemble_runner.py:367-372 (calculate_detection_rates)` | C21 |
| C25 | P1 | Remove eval() on metadata loaded from .npz (arbitrary code execution) | F001, F026 | `src/residual_analysis.py:215 (and save_residuals metadata serialization ~line 138)` | C2 |
| C27 | P1 | Implement q_fom figure-of-merit (paper Eq. 17) | F022 | `src/residual_analysis.py:233-240 (commented-out stub)` | C2 |
| C33 | P1 | Replace single-flyby example stub with a real end-to-end demo | F014, F025 | `examples/single_flyby_example.py:18-34` | C5, C6, C7, C8, C10, C11, C13, C14, C18 |
| C36 | P1 | Add substantive physics-correctness tests (replace bare-pass test) | F034 | `tests/test_n_body_simulation.py:23 and new tests/test_physics.py` | C7, C11, C23, C5, C8 |
| C40 | P1 | Point npm scripts at the task-master CLI and un-ignore scripts/ (TaskMaster seed) | F053 | `package.json:8-11; .gitignore:199` | — |
| C42 | P1 | Remove hardcoded developer username from run-task-master.bat | F050 | `run-task-master.bat:7-8` | — |
| C16 | P2 | Guard dt_rebound against None when dt_years is falsy | F043 | `src/simulation_runner.py:38 and the integration loop ~line 144` | C2 |
| C24 | P2 | Compute true 3D peak displacement instead of norm of per-dimension maxima | F048 | `src/ensemble_runner.py:316 (is_detected) and src/residual_analysis.py:calculate_peak` | C21 |
| C26 | P2 | Avoid unsafe allow_pickle deserialization of .npz files | F002 | `src/residual_analysis.py:206 (np.load)` | C25 |
| C28 | P2 | Warn/handle np.interp boundary clipping in compute_residuals | F042 | `src/residual_analysis.py:98` | C2 |
| C29 | P2 | Move residual-stats calculation out of the failure-only else branch | F027 | `src/residual_analysis.py:394-410 (__main__)` | C2 |
| C31 | P2 | Make plot functions headless-safe (no unconditional plt.show) | F028 | `src/visualization.py:76,175,314,384` | C2 |
| C32 | P2 | Fix mislabeled residual time-series plot (index basis mismatch) | F047 | `src/visualization.py:137` | C2 |
| C34 | P2 | Implement spectral analysis of residuals (documented, missing module) | F032 | `src/spectral_analysis.py (new file); referenced by README.md:58 and docs/pseudocode.md:282-308` | C2 |
| C35 | P2 | Implement parameter-recovery / likelihood-ratio module (documented, missing) | F031 | `src/parameter_recovery.py (new file); referenced by README.md:53-57 and docs/pseudocode.md:429-475` | C27, C25 |
| C37 | P2 | Correct README project-structure module listing | F023 | `README.md:128-132` | C34, C35 |
| C38 | P2 | Fix README Usage section to reference real interfaces | F024 | `README.md:98-99 (and surrounding Usage examples)` | C33 |
| C39 | P2 | Add the LICENSE file referenced by README | F033 | `LICENSE (new file at repo root); referenced by README.md:159-160` | — |
| C41 | P2 | Document TaskMaster bootstrap so contributors regenerate the task DB | F053 | `docs/onboarding-guide.md (TaskMaster workflow section); README.md (setup)` | C40 |
| C43 | P2 | Consolidate the three inconsistent run-task-master wrapper versions | F051 | `run-task-master.bat:1-8; docs/onboarding-guide.md:112-115; docs/task-master-windows-guide.md:65-72` | C42 |
| C44 | P2 | Replace invalid Claude model ID in all TaskMaster .env examples | F052 | `docs/onboarding-guide.md:102; docs/task-master-guide.md:59; docs/task-master-windows-guide.md:50,320` | — |
| C45 | P2 | Make onboarding guide cross-platform (not Windows .bat only) | F056 | `docs/onboarding-guide.md:147,150,153,157,165,169,183,207,211,346,397,404,409` | C43 |
| C17 | P3 | Make mid-loop particle-count resize lossless with consistent allocation | F013 | `src/simulation_runner.py:151-161` | C13 |
| C19 | P3 | Reconcile apply_analytic_kick docstring with implementation | F044 | `src/n_body_simulation.py:201-215` | C8 |
| C30 | P3 | Implement or remove the dead CSV save path | F036 | `src/residual_analysis.py:6 (FORMAT_CSV) and the CSV branch ~line 154-177` | C2 |
| C46 | P3 | Fix redundant clone+upstream remote instructions | F057 | `docs/onboarding-guide.md:72-80` | — |
| C47 | P3 | Fix contradictory tasks.json location in windows guide | F058 | `docs/task-master-windows-guide.md:331-333` | — |
| C48 | P3 | Un-ignore .cursor so shared workflow rules are version-controlled | F054 | `.gitignore:201` | — |
| C49 | P3 | Repair truncated/broken Paper 9 ADS link in rebound_readme.md | F055 | `rebound_readme.md:115` | — |
| C50 | P3 | Remove unused scipy.stats import from parameter_sampler | F035 | `src/parameter_sampler.py:2` | C2 |

### C1 [P0] — Make src/ a real importable package

- **Closes:** F049, F030
- **Location:** `src/__init__.py (new file)`
- **Change:** Create an empty (or docstring-only) src/__init__.py so src/ stops being a namespace package and setuptools find_packages() can discover it. Add a one-line module docstring; no executable code.
- **Verification signal:** `python -c "import importlib,os; print(os.path.exists('src/__init__.py'))"` prints True; `python -c "from setuptools import find_packages; print(find_packages())"` now includes 'src' (previously returned only ['tests']).
- **Depends on:** nothing

### C2 [P0] — Convert all intra-package imports to explicit relative imports

- **Closes:** F008, F019, F045
- **Location:** `src/n_body_simulation.py:4; src/simulation_runner.py (imports of n_body_simulation/analytic_impulse); src/ensemble_runner.py (imports of simulation_runner/parameter_sampler); src/visualization.py:510; src/synthetic_data.py (import residual_analysis)`
- **Change:** Replace every bare absolute intra-project import with a package-relative form: in n_body_simulation.py:4 change `from analytic_impulse import calculate_velocity_kick, G as analytic_G` to `from .analytic_impulse import calculate_velocity_kick, G as analytic_G`. Apply the same `.module` prefix to simulation_runner.py, ensemble_runner.py, the `from ensemble_runner import calculate_detection_rates` at visualization.py:510, and synthetic_data.py's `import residual_analysis`. For the `__main__` blocks that must still run as scripts, guard the relative import with a try/except ImportError falling back to the absolute import, OR document running them only via `python -m src.<module>`.
- **Verification signal:** `python -m src.simulation_runner` and `python -m src.ensemble_runner` no longer raise `ModuleNotFoundError: No module named 'analytic_impulse'` / `ImportError: attempted relative import with no known parent package`; `python -m src.visualization` no longer prints 'Skipping binned rate plot example (requires ensemble_runner module)'.
- **Depends on:** C1

### C3 [P0] — Fix setup.py packaging and remove test tools from runtime deps

- **Closes:** F030, F029, F049
- **Location:** `setup.py:9,10-17`
- **Change:** Change `packages=find_packages()` to `packages=find_packages(include=['src', 'src.*'])` (now resolvable thanks to C1). Remove 'pytest' and 'pytest-cov' from install_requires (line 15-16) and instead add `extras_require={'test': ['pytest', 'pytest-cov']}`. Add the actually-imported runtime deps to install_requires: add 'tqdm' (used at ensemble_runner.py:6). Keep numpy, matplotlib, scipy, rebound.
- **Verification signal:** `pip install .` succeeds; `python -c "import pkg_resources; d=pkg_resources.get_distribution('primordial_encounters'); print([str(r) for r in d.requires()])"` shows pytest/pytest-cov absent from the default requires; `python -c "from setuptools import find_packages; print(find_packages(include=['src','src.*']))"` includes 'src'.
- **Depends on:** C1

### C4 [P0] — Declare tqdm in requirements.txt

- **Closes:** F039
- **Location:** `requirements.txt:1-5 (Core Dependencies block)`
- **Change:** Add `tqdm` to the Core Dependencies section of requirements.txt (it is imported unconditionally at ensemble_runner.py:6 but currently absent). Keep the line in the core block, not the optional block, since ensemble_runner imports it at module load.
- **Verification signal:** `grep -i '^tqdm' requirements.txt` returns a match; in a fresh venv `pip install -r requirements.txt && python -c 'import src.ensemble_runner'` completes without `ModuleNotFoundError: No module named 'tqdm'`.
- **Depends on:** nothing

### C5 [P0] — Fix PBH mass key mismatch between sampler and runner

- **Closes:** F004, F016
- **Location:** `src/simulation_runner.py:84`
- **Change:** Change the lookup `pbh_params['mass']` to `pbh_params['mass_msun']` to match the key emitted by parameter_sampler.generate_pbh_sample. Alternatively standardize on a single contract by normalizing keys at the runner boundary, but the minimal correct diff is to read 'mass_msun'.
- **Verification signal:** Calling `run_single_simulation(..., pbh_params=generate_pbh_sample(1)[0])` no longer raises `KeyError: 'mass'` at line 84; the perturbed branch proceeds past mass extraction.
- **Depends on:** C2

### C6 [P0] — Fix impact-parameter key so sampled value is not silently discarded

- **Closes:** F005
- **Location:** `src/simulation_runner.py:91`
- **Change:** Change `pbh_params.get('impact_param', 100.0)` to `pbh_params['impact_param_au']` (or `.get('impact_param_au')` with an explicit error if missing) so the sampled impact parameter is used instead of the silent 100.0 AU default.
- **Verification signal:** With pbh_params containing impact_param_au=0.5, the value used in the PBH initial-position calculation is 0.5 (not 100.0); add a temporary assert/print to confirm, or unit-test that the consumed b equals the sampled impact_param_au.
- **Depends on:** C2

### C7 [P0] — Correct km/s -> AU/day conversion constant (~86x error)

- **Closes:** F003, F017
- **Location:** `src/parameter_sampler.py:11`
- **Change:** Replace `KM_S_TO_AU_DAY = 1.0/1.731e6*86400.0` (=4.99e-2) with the correct constant: 1 km/s = 86400 km/day / 1.496e8 km/AU = 5.7754e-4 AU/day. Set `KM_S_TO_AU_DAY = 86400.0 / 1.496e8`. Add an inline comment showing the derivation.
- **Verification signal:** `python -m src.parameter_sampler` produces sampled velocity magnitudes ~0.1-0.25 AU/day for sigma_v~200 km/s (was ~10-25 AU/day); `python -c "print(86400/1.496e8)"` ~5.78e-4 matches the new constant.
- **Depends on:** C2

### C8 [P0] — Restore REBOUND 5.x API compatibility for body setup and particle naming

- **Closes:** F009, F006
- **Location:** `src/n_body_simulation.py: add_solar_system (~line 90-99), add_pbh, apply_analytic_kick (label lookup ~line 214), get_particle_data`
- **Change:** REBOUND 5.x removed `Simulation.add_solar_system()` and the `label` particle kwarg, and exposes particle identity via `p.name`. (1) In add_solar_system, replace the removed `sim.add_solar_system()` call with explicit particle additions (sim.add(m=..., x=..., v=...)) or an `astroquery.jplhorizons`-sourced state set; if a quick fix is wanted, add the Sun + planets explicitly with masses. (2) Everywhere particles are created with `label=...`, use `name=...`. (3) Replace `getattr(p, 'label', None)` lookups with `p.name`. Keep the public method signatures stable.
- **Verification signal:** `python -m src.n_body_simulation` no longer prints `'Simulation' object has no attribute 'add_solar_system'` nor `TypeError: Particle.__init__() got an unexpected keyword argument 'label'`; add_pbh adds the particle and apply_analytic_kick can locate bodies by name (returns True for a valid target).
- **Depends on:** C2

### C20 [P0] — Remove nested multiprocessing in ensemble members (daemon crash)

- **Closes:** F038
- **Location:** `src/ensemble_runner.py:64 (run_ensemble_member) and src/simulation_runner.py run_parallel_simulations`
- **Change:** Inside run_ensemble_member, replace the call to `simulation_runner.run_parallel_simulations(...)` (which spawns its own multiprocessing.Pool inside an already-daemonic pool worker) with two sequential calls to `run_single_simulation` (baseline, then perturbed). The outer ensemble Pool provides the parallelism; the inner per-member work must be serial. Keep run_parallel_simulations for standalone (non-ensemble) use only.
- **Verification signal:** Running run_ensemble with >=1 member no longer prints `AssertionError: daemonic processes are not allowed to have children`; each member completes its baseline+perturbed sims.
- **Depends on:** C5, C6, C8

### C21 [P0] — Add missing return statement to run_ensemble

- **Closes:** F007, F015
- **Location:** `src/ensemble_runner.py: end of run_ensemble (~line 277)`
- **Change:** Add `return ensemble_results` (the accumulated list of per-member summary dicts) at the end of run_ensemble so the caller's `for r in ensemble_results` and downstream detection-rate analysis receive a list instead of None. Confirm the variable holding the collected member summaries is the one returned.
- **Verification signal:** `results = run_ensemble(...)` returns a list whose length equals the number of members (not None); `len(results)` and iteration succeed; the __main__ block's `for r in ensemble_results` no longer raises TypeError.
- **Depends on:** C20

### C9 [P1] — Stop swallowing body-setup exceptions silently

- **Closes:** F009
- **Location:** `src/n_body_simulation.py:97-99 (add_solar_system try/except)`
- **Change:** Replace the broad `try/except Exception: print(...)` that lets the simulation continue with 0 particles. Either re-raise after logging, or raise a clear RuntimeError('Failed to initialize Solar System bodies: ...') so callers cannot proceed with an empty simulation. Do not return normally on failure.
- **Verification signal:** Forcing a setup failure (e.g. invalid integrator) causes add_solar_system to raise/propagate rather than printing an error and continuing; a subsequent run_simulation does not execute on a 0-particle simulation.
- **Depends on:** C8

### C10 [P1] — Remove hardcoded 'body_3' kick target; derive target from configured bodies

- **Closes:** F006, F021
- **Location:** `src/simulation_runner.py:104`
- **Change:** Replace the hardcoded `target_body_label='body_3'` with a parameter (e.g. `target_body` argument threaded from the caller / config) or a lookup that selects the intended planet by name present in the configured body set. Validate the target exists in the simulation (raise a clear error if get_particle_state returns None) instead of silently producing (None, None).
- **Verification signal:** Running the perturbed path on the configured body set (Sun, body_1, body_2) no longer returns (None, None) from get_particle_state for the kick target; the kick is applied to an existing body, and an invalid target name raises a descriptive error.
- **Depends on:** C8

### C11 [P1] — Fix inverted analytic velocity-kick direction (repulsive -> attractive)

- **Closes:** F011
- **Location:** `src/analytic_impulse.py:66`
- **Change:** Change `kick_direction = -r_ca / b` to `kick_direction = +r_ca / b` (or equivalently remove the leading minus) so the gravitational impulse points TOWARD the PBH at closest approach. r_ca is the vector from target to PBH at closest approach; an attractive impulse must be parallel to it.
- **Verification signal:** In the analytic_impulse __main__ probe, `np.dot(delta_v/|delta_v|, r_ca/|r_ca|)` returns +1.0 (was -1.0); the kicked body's velocity change points toward the PBH.
- **Depends on:** C2

### C12 [P1] — Correct unphysical example PBH velocity (~820x too large)

- **Closes:** F018
- **Location:** `src/analytic_impulse.py:104-105`
- **Change:** Replace the hardcoded velocity `5510` AU/(yr/2pi) and its wrong comment. For 200 km/s: 1 AU/(yr/2pi) = 29.79 km/s, so 200 km/s = 6.71 AU/(yr/2pi). Set the example velocity to ~6.71 and fix the comment chain (200 km/s -> 0.1155 AU/day -> 6.71 AU/(yr/2pi)). Prefer computing it from KM_S_TO_AU_DAY (after C7) rather than a magic number.
- **Verification signal:** `python src/analytic_impulse.py` uses a PBH speed of ~6.7 AU/(yr/2pi) (well below c); the resulting delta_v magnitude is physically plausible and the inline comment's intermediate values are self-consistent.
- **Depends on:** C7, C11

### C13 [P1] — Eliminate PBH perturbation double-counting (live mass AND impulse)

- **Closes:** F040
- **Location:** `src/simulation_runner.py:94-116`
- **Change:** Choose ONE perturbation model per the paper's impulse approximation: either (A) add the PBH as a live gravitating body and run full N-body WITHOUT also calling apply_analytic_kick, or (B) do NOT add the PBH mass to the integrator and apply only the analytic impulse kick to the target. Implement (B) as the default to match the impulse-approximation methodology: skip add_pbh's gravitational contribution (mass=0 or omit the body) when the analytic kick is used. Gate the choice behind an explicit `method` flag.
- **Verification signal:** Inspecting the perturbed run: exactly one of {PBH live gravitational mass in the integrator, analytic impulse applied} is active for a given method; a test comparing residual magnitude to the analytic single-kick prediction agrees to within integrator tolerance (not ~2x).
- **Depends on:** C8, C10, C11

### C14 [P1] — Compute physical PBH initial position from encounter geometry

- **Closes:** F010, F020
- **Location:** `src/simulation_runner.py:89-91`
- **Change:** Replace the placeholder `pbh_initial_pos = np.array([-1000.0, impact_param, 0.0])` with a position derived from the sampled encounter parameters: given impact parameter b (impact_param_au, C6), incoming velocity vector v_inf (velocity_au_day), encounter time t_encounter, and approach angles (theta, phi from C15), place the PBH back-tracked along -v_inf from the closest-approach point so that at t_encounter it reaches closest approach at distance b from the target. Document the geometry in a comment.
- **Verification signal:** The PBH's straight-line trajectory passes within b of the target at the sampled t_encounter (assert min distance over the integration window equals impact_param_au within tolerance); the initial position varies with t_encounter and v_inf (no longer constant -1000 AU).
- **Depends on:** C6, C13, C15

### C15 [P1] — Sample PBH approach-direction angles so encounter geometry is complete

- **Closes:** F037
- **Location:** `src/parameter_sampler.py: generate_pbh_sample (~line 85)`
- **Change:** Add isotropic sampling of the PBH approach direction: sample two angles (theta from arccos(uniform(-1,1)) for polar, phi from uniform(0,2pi) for azimuth) and emit them in each sample dict (e.g. keys 'approach_theta_rad','approach_phi_rad'), and/or emit a unit approach-direction vector. These define the velocity-vector orientation consumed by C14.
- **Verification signal:** `generate_pbh_sample(n)` dicts contain the new angle/direction keys; sampled polar angles are distributed as sin(theta) (isotropic) over many draws; simulation_runner can construct the full 3D incoming velocity from sampled speed + direction.
- **Depends on:** C7

### C18 [P1] — Preserve pre-encounter (t_start) state across post-kick array reallocation

- **Closes:** F041
- **Location:** `src/simulation_runner.py:126-133`
- **Change:** Stop overwriting step-0 (the t=0/t_start pre-encounter state captured at lines ~67-75) when arrays are reallocated after the kick. Record the kicked state as a NEW step rather than overwriting index 0, or store pre-encounter and post-kick states in separate slots so the baseline-vs-perturbed residual at t_start is genuinely zero.
- **Verification signal:** In a perturbed run, positions_out[0] equals the captured pre-encounter state (not zeros and not the t_ca state); residual at t_start computed against baseline is ~0.
- **Depends on:** C13

### C22 [P1] — Make summaries/checkpoints/results JSON-serializable (numpy types)

- **Closes:** F012
- **Location:** `src/ensemble_runner.py:136, 249, 263 (json.dump calls)`
- **Change:** Add a numpy-aware JSON encoder (subclass json.JSONEncoder converting np.ndarray->tolist(), np.integer->int, np.floating->float) and pass `cls=NpEncoder` (or `default=` callable) to every json.dump/json.dumps. Apply at member-summary save (136), checkpoint (249), and final-results (263). Ensure pbh_params['velocity_au_day'] (an ndarray) serializes.
- **Verification signal:** run_ensemble completes without `TypeError: Object of type ndarray is not JSON serializable`; the per-member summary JSON and final results JSON files are written and re-loadable with json.load.
- **Depends on:** C20

### C23 [P1] — Fix detection-rate denominator inflation by unclassifiable members

- **Closes:** F046
- **Location:** `src/ensemble_runner.py:367-372 (calculate_detection_rates)`
- **Change:** Reorder so total_completed is incremented only for classifiable members. Move the `total_completed += 1` (line 367) to AFTER the is_detected check, and `continue` (skip) members where is_detected returns None WITHOUT counting them in the denominator. Equivalently, count only members with non-None stats in total_completed.
- **Verification signal:** Harness test (1 unclassifiable + 1 detected) yields rate 1.0 (was 0.5); total_completed excludes members with stats=None; aggregate rate equals sum over bins.
- **Depends on:** C21

### C25 [P1] — Remove eval() on metadata loaded from .npz (arbitrary code execution)

- **Closes:** F001, F026
- **Location:** `src/residual_analysis.py:215 (and save_residuals metadata serialization ~line 138)`
- **Change:** Stop using `eval(metadata_str)` to deserialize metadata. Change save_residuals to store metadata as a JSON string (json.dumps(meta_dict)) instead of str(dict), and change load_residuals to parse it with json.loads(). If legacy str(dict) files must still be read, use ast.literal_eval (safe, no code execution) as a fallback — never eval().
- **Verification signal:** `grep -n 'eval(' src/residual_analysis.py` returns no eval() on loaded data; load_residuals round-trips metadata via json.loads; a crafted .npz whose metadata string contains `__import__('os').system(...)` does NOT execute (raises a parse error instead).
- **Depends on:** C2

### C27 [P1] — Implement q_fom figure-of-merit (paper Eq. 17)

- **Closes:** F022
- **Location:** `src/residual_analysis.py:233-240 (commented-out stub)`
- **Change:** Implement calculate_q_fom(residuals, noise) replacing the commented-out stub. Per Tran et al. (arXiv:2312.17217v3) Eq. (17), compute the signal-to-noise figure-of-merit as the quadrature sum over observations of (residual / measurement uncertainty), i.e. q_fom = sqrt( sum_i (r_i / sigma_i)^2 ) using the residual time series and the per-observation noise floor (sigma supplied by caller / synthetic_data). Wire it in as the detection statistic used by ensemble detection logic instead of the raw peak-residual proxy. Document the exact equation mapping in the docstring.
- **Verification signal:** calculate_q_fom returns a finite scalar for a residual+noise input; for zero residuals q_fom==0; for residual==k*sigma uniformly over N points q_fom==k*sqrt(N); a unit test against a hand-computed small case matches.
- **Depends on:** C2

### C33 [P1] — Replace single-flyby example stub with a real end-to-end demo

- **Closes:** F014, F025
- **Location:** `examples/single_flyby_example.py:18-34`
- **Change:** Replace the placeholder print-only function with a runnable demo that: imports the package modules; builds a small body set; samples or hardcodes one PBH encounter (mass_msun, impact_param_au, velocity, t_encounter, approach angles); runs baseline + perturbed simulations via simulation_runner; computes residuals via residual_analysis; and prints/saves the position residual time series (optionally plots via visualization with show=False). No 'will:' placeholder text.
- **Verification signal:** `python examples/single_flyby_example.py` runs a real simulation and outputs a residual time series (array shapes printed, optional .npz/.png saved); the placeholder lines 'This is a placeholder example. The actual implementation will:' are gone.
- **Depends on:** C5, C6, C7, C8, C10, C11, C13, C14, C18

### C36 [P1] — Add substantive physics-correctness tests (replace bare-pass test)

- **Closes:** F034
- **Location:** `tests/test_n_body_simulation.py:23 and new tests/test_physics.py`
- **Change:** Replace the bare `pass` test_initialization body with real assertions, and add tests covering verified invariants: (1) calculate_velocity_kick magnitude scales linearly with PBH mass and as 1/(b*v) (paper Eq. 2); (2) kick direction points toward the PBH (np.dot(dv_hat, r_ca_hat)==+1, regression for F011); (3) KM_S_TO_AU_DAY equals 86400/1.496e8 (regression for F003); (4) baseline-vs-baseline residuals are exactly zero; (5) calculate_detection_rates excludes unclassifiable members (regression for F046). Use numpy.testing.assert_allclose with explicit tolerances.
- **Verification signal:** `python -m pytest -q` collects and PASSES the new physics tests (not skipped); test_initialization no longer a bare pass; tests fail if C7/C11/C46-fixes are reverted (true regression guards).
- **Depends on:** C7, C11, C23, C5, C8

### C40 [P1] — Point npm scripts at the task-master CLI and un-ignore scripts/ (TaskMaster seed)

- **Closes:** F053
- **Location:** `package.json:8-11; .gitignore:199`
- **Change:** Resolvable fix that needs no unknown dev.js content: (1) In package.json change the four scripts from `node scripts/dev.js [...]` to invoke the installed task-master-ai CLI directly: `"dev": "task-master next"`, `"list": "task-master list"`, `"generate": "task-master generate"`, `"parse-prd": "task-master parse-prd"` (the `task-master` binary is provided by the task-master-ai dependency in node_modules/.bin, so `npm run` resolves it; subcommands list/generate/parse-prd/next were confirmed present via `task-master --help`). (2) In .gitignore remove (or comment) line 199 `scripts/` so any future generated seed (e.g. a committed PRD) CAN be version-controlled. This eliminates the dependence on the absent scripts/dev.js without inventing its contents.
- **Verification signal:** `npm install` then `npm run list` no longer fails with `Cannot find module .../scripts/dev.js`; it invokes the task-master CLI (prints the task list or a clean 'no tasks file found' message). `grep -n '^scripts/' .gitignore` returns nothing.
- **Depends on:** nothing

### C42 [P1] — Remove hardcoded developer username from run-task-master.bat

- **Closes:** F050
- **Location:** `run-task-master.bat:7-8`
- **Change:** Replace the hardcoded `C:\Users\Shadow\AppData\Roaming\npm` paths with the portable `%USERNAME%` / `%APPDATA%` form (e.g. `%APPDATA%\npm`) or, preferably, delegate to `npx task-master-ai %*` which needs no PATH hardcoding. Remove all literal 'Shadow' references.
- **Verification signal:** `grep -i 'Shadow' run-task-master.bat` returns nothing; the wrapper uses %APPDATA%/%USERNAME% or npx so it runs under any Windows user account.
- **Depends on:** nothing

### C16 [P2] — Guard dt_rebound against None when dt_years is falsy

- **Closes:** F043
- **Location:** `src/simulation_runner.py:38 and the integration loop ~line 144`
- **Change:** Change `dt_rebound = dt_years * 2 * np.pi if dt_years else None` so that a falsy/zero dt_years either raises a clear ValueError('dt_years must be positive') or falls back to a sane default, never None. Ensure the loop at ~line 144 (`sim_instance.sim.t + dt_rebound`) can never dereference None.
- **Verification signal:** Calling run_single_simulation with dt_years=0 raises a descriptive ValueError instead of `TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'`; with a valid dt_years the loop runs unchanged.
- **Depends on:** C2

### C24 [P2] — Compute true 3D peak displacement instead of norm of per-dimension maxima

- **Closes:** F048
- **Location:** `src/ensemble_runner.py:316 (is_detected) and src/residual_analysis.py:calculate_peak`
- **Change:** The detection magnitude must be the maximum over time of the per-timestep 3D displacement norm, not the norm of per-dimension temporal maxima. Add/use a statistic = max_t( sqrt(dx_t^2+dy_t^2+dz_t^2) ) computed from the full residual time series, and have is_detected use it. Either add a 'peak_disp_au' stat in calculate_residual_stats (from the time series) or recompute in is_detected from stored residuals.
- **Verification signal:** For the documented case (peak_x at t1, peak_y at t2) the detection magnitude equals the true max 3D displacement (e.g. 1e-5), not sqrt(2)*1e-5; a unit test on a synthetic residual series confirms peak == max over time of pointwise norm.
- **Depends on:** C21

### C26 [P2] — Avoid unsafe allow_pickle deserialization of .npz files

- **Closes:** F002
- **Location:** `src/residual_analysis.py:206 (np.load)`
- **Change:** Stop relying on `np.load(filepath, allow_pickle=True)`. Once metadata is stored as a JSON string (C25), arrays and the metadata string can be loaded with `np.load(filepath)` (allow_pickle=False, the safe default). Store metadata as a 0-d string array or a sidecar .json so pickled Python objects are never required.
- **Verification signal:** `np.load(path)` (default allow_pickle=False) succeeds for files written by the updated save_residuals; `grep -n 'allow_pickle=True' src/residual_analysis.py` returns nothing.
- **Depends on:** C25

### C28 [P2] — Warn/handle np.interp boundary clipping in compute_residuals

- **Closes:** F042
- **Location:** `src/residual_analysis.py:98`
- **Change:** np.interp silently clamps to boundary values when the perturbed/baseline time ranges do not overlap. Either restrict the residual computation to the overlapping time window, or detect out-of-range query times and emit a warning (warnings.warn) / set those residuals to NaN rather than silently clipping. Document the chosen behavior.
- **Verification signal:** For non-overlapping time ranges (e.g. base_times=[0,0.5], pert_times=[0.1,0.4]) compute_residuals emits a warning or returns NaN outside the overlap, instead of silently returning clipped boundary values; a unit test asserts the warning/NaN.
- **Depends on:** C2

### C29 [P2] — Move residual-stats calculation out of the failure-only else branch

- **Closes:** F027
- **Location:** `src/residual_analysis.py:394-410 (__main__)`
- **Change:** The calculate_residual_stats block (lines ~397-410) sits inside the `else:` branch that only runs when compute_residuals FAILS, so it is dead code on success. Move the stats calculation into the success path (the `if` branch) so statistics are computed and printed when residuals are produced.
- **Verification signal:** `python src/residual_analysis.py` (success path) now prints 'Calculating Residual Statistics' / the stats output in the main block; the stats block executes when compute_residuals succeeds.
- **Depends on:** C2

### C31 [P2] — Make plot functions headless-safe (no unconditional plt.show)

- **Closes:** F028
- **Location:** `src/visualization.py:76,175,314,384`
- **Change:** Add a `show=False` (or `save_path`) parameter to each plot function; call plt.show() only when show=True. Default to saving to file and not blocking. This lets batch/headless ensemble runs generate plots without a blocking GUI call.
- **Verification signal:** With show=False (the default for batch use), plot functions return/save without calling plt.show(); `grep -n 'plt.show' src/visualization.py` shows each call guarded by a conditional; `python -m src.visualization` under a non-Agg backend does not block.
- **Depends on:** C2

### C32 [P2] — Fix mislabeled residual time-series plot (index basis mismatch)

- **Closes:** F047
- **Location:** `src/visualization.py:137`
- **Change:** plot_residual_timeseries uses residuals-array-local indices (valid_indices 0..n-1) to index a labels list documented as indexed by original particle indices. Fix by indexing labels with the ORIGINAL particle indices (e.g. `plot_labels = [labels[orig_idx] for orig_idx in particle_indices]`) rather than the array-local positions, OR clearly redefine `labels` to be array-local and document it. Ensure each plotted line gets its correct body label.
- **Verification signal:** With particle_indices=[0,1] and labels=['Sun','Earth','PlanetX'], the line for the body at original index 1 is labeled 'Earth' (not 'Sun'); a unit/visual check confirms label-to-curve correspondence.
- **Depends on:** C2

### C34 [P2] — Implement spectral analysis of residuals (documented, missing module)

- **Closes:** F032
- **Location:** `src/spectral_analysis.py (new file); referenced by README.md:58 and docs/pseudocode.md:282-308`
- **Change:** Create src/spectral_analysis.py implementing FFT/periodogram analysis of the residual time series to characterize the near-monochromatic orbital deviation (paper Fig. 3): a function taking residual_times + position_residuals and returning frequency, power spectrum, and dominant-frequency estimate. Use numpy.fft (and optionally scipy.signal.periodogram). Expose a plotting helper or integrate with visualization.
- **Verification signal:** `python -c "from src import spectral_analysis"` imports; feeding a synthetic sinusoidal residual returns a spectrum whose peak frequency matches the input frequency within bin resolution; a unit test asserts the recovered dominant frequency.
- **Depends on:** C2

### C35 [P2] — Implement parameter-recovery / likelihood-ratio module (documented, missing)

- **Closes:** F031
- **Location:** `src/parameter_recovery.py (new file); referenced by README.md:53-57 and docs/pseudocode.md:429-475`
- **Change:** Create src/parameter_recovery.py that fits PBH parameters (mass, impact parameter, velocity/trajectory) from (synthetic) residuals and performs a likelihood-ratio test of the PBH-present model vs a no-PBH null. Use the already-declared emcee (MCMC posterior) and/or dynesty (nested-sampling evidence) dependencies; define a Gaussian likelihood from residuals + noise (sigma from synthetic_data) and a forward model calling the analytic impulse. Return best-fit parameters and the likelihood-ratio / log-evidence statistic.
- **Verification signal:** `python -c "from src import parameter_recovery"` imports; on synthetic data generated with known PBH parameters the recovery returns posterior medians within stated tolerance of the truth, and the likelihood-ratio favors PBH-present over null for a detectable injection; `grep -n 'import emcee\|import dynesty' src/parameter_recovery.py` confirms an inference library is actually used.
- **Depends on:** C27, C25

### C37 [P2] — Correct README project-structure module listing

- **Closes:** F023
- **Location:** `README.md:128-132`
- **Change:** Replace the nonexistent module names (nbody.py, pbhsampler.py, residuals.py, parameter_recovery.py) with the actual src/ contents: analytic_impulse.py, ensemble_runner.py, n_body_simulation.py, parameter_sampler.py, residual_analysis.py, simulation_runner.py, synthetic_data.py, visualization.py, plus the newly added spectral_analysis.py and parameter_recovery.py (C34/C35).
- **Verification signal:** Every module path listed in README.md project structure exists on disk (`ls src/<name>` succeeds for each); no listed file is missing.
- **Depends on:** C34, C35

### C38 [P2] — Fix README Usage section to reference real interfaces

- **Closes:** F024
- **Location:** `README.md:98-99 (and surrounding Usage examples)`
- **Change:** Replace the invented CLI invocations (`python scripts/single_flyby.py --mass ... --r0 ... --alpha ... --beta ...`, ensemble_flyby.py, param_recovery.py) with the actual runnable entry points: `python examples/single_flyby_example.py` (after C33) and `python -m src.ensemble_runner` / documented function-call usage. Remove flags that match no implemented argparse interface, or add an argparse CLI if flags are desired and document the real flag names.
- **Verification signal:** Every command shown in README Usage runs as written (no MODULE_NOT_FOUND, no unrecognized-argument errors); referenced script paths exist.
- **Depends on:** C33

### C39 [P2] — Add the LICENSE file referenced by README

- **Closes:** F033
- **Location:** `LICENSE (new file at repo root); referenced by README.md:159-160`
- **Change:** Create a LICENSE file containing the MIT License text (the README links to an MIT License), with the copyright holder set to the project author (ImmortalDemonGod) and year 2025/2026. If MIT is not intended, update README to reference the actual chosen license instead — but the README currently states MIT, so add MIT.
- **Verification signal:** `os.path.exists('LICENSE')` is True and the file contains the MIT License header; the README.md:160 link target resolves to an existing file.
- **Depends on:** nothing

### C41 [P2] — Document TaskMaster bootstrap so contributors regenerate the task DB

- **Closes:** F053
- **Location:** `docs/onboarding-guide.md (TaskMaster workflow section); README.md (setup)`
- **Change:** Add an explicit bootstrap step instructing contributors to generate the local TaskMaster state themselves rather than relying on a committed scripts/dev.js: `npx task-master-ai init` (scaffolds config), then `task-master parse-prd <path-to-PRD>` to build tasks. State that scripts/ is now committable (after C40) so a shared PRD can be checked in. This closes the gap left by the absent generated files using only determinable CLI commands.
- **Verification signal:** docs/onboarding-guide.md contains a step-by-step TaskMaster init/parse-prd bootstrap using `npx task-master-ai init` and `task-master parse-prd`; following it on a clean checkout produces a tasks file without referencing scripts/dev.js.
- **Depends on:** C40

### C43 [P2] — Consolidate the three inconsistent run-task-master wrapper versions

- **Closes:** F051
- **Location:** `run-task-master.bat:1-8; docs/onboarding-guide.md:112-115; docs/task-master-windows-guide.md:65-72`
- **Change:** Pick one canonical wrapper definition (recommend the simple `npx task-master-ai %*` form, consistent with C42) and make all three locations match it verbatim. Update the onboarding guide and windows guide to show the identical command as the actual run-task-master.bat.
- **Verification signal:** The wrapper command shown in run-task-master.bat, docs/onboarding-guide.md, and docs/task-master-windows-guide.md is byte-for-byte identical; no divergent PATH-hardcoded variants remain.
- **Depends on:** C42

### C44 [P2] — Replace invalid Claude model ID in all TaskMaster .env examples

- **Closes:** F052
- **Location:** `docs/onboarding-guide.md:102; docs/task-master-guide.md:59; docs/task-master-windows-guide.md:50,320`
- **Change:** Replace the invalid `claude-3-5-sonnet-20240229` with a valid current Claude model ID. Use `claude-sonnet-4-6` (a current, valid model) for the MODEL setting in every .env example; update all four locations consistently.
- **Verification signal:** `grep -rn 'claude-3-5-sonnet-20240229' docs/` returns nothing; every MODEL= example references a valid model id (claude-sonnet-4-6) consistently.
- **Depends on:** nothing

### C45 [P2] — Make onboarding guide cross-platform (not Windows .bat only)

- **Closes:** F056
- **Location:** `docs/onboarding-guide.md:147,150,153,157,165,169,183,207,211,346,397,404,409`
- **Change:** For each Windows-only `.\run-task-master.bat <cmd>` invocation, add the Unix/macOS equivalent (`npx task-master-ai <cmd>` or `./run-task-master.sh <cmd>`) alongside it, or replace .bat-specific calls with the platform-neutral `npx task-master-ai <cmd>` form. Ensure the guide does not assume cmd.exe/PowerShell syntax for Linux/macOS contributors.
- **Verification signal:** Every TaskMaster command in docs/onboarding-guide.md shows a non-Windows-only form (npx or .sh); a Linux/macOS contributor can follow the guide without translating .bat syntax.
- **Depends on:** C43

### C17 [P3] — Make mid-loop particle-count resize lossless with consistent allocation

- **Closes:** F013
- **Location:** `src/simulation_runner.py:151-161`
- **Change:** Use a consistent initial allocation sized to the final particle count (or a list-of-steps appended then stacked at the end) so that resizing when particle count changes does not zero-fill and discard previously recorded steps. Preserve all recorded timesteps across the resize boundary.
- **Verification signal:** A run where particle count changes mid-integration preserves all earlier-step position/velocity data (no zero rows introduced); the output array length equals the number of integration steps recorded.
- **Depends on:** C13

### C19 [P3] — Reconcile apply_analytic_kick docstring with implementation

- **Closes:** F044
- **Location:** `src/n_body_simulation.py:201-215`
- **Change:** Fix the contract mismatch: either change the docstring (lines ~202-204) to state that the kick is computed at the current simulation time (matching the implementation at ~214), or enforce the documented t=0 precondition with an assertion. Make docstring and behavior agree.
- **Verification signal:** Docstring statement about simulation time matches the code path actually taken; if an assertion is added, calling apply_analytic_kick at t!=0 raises the documented error.
- **Depends on:** C8

### C30 [P3] — Implement or remove the dead CSV save path

- **Closes:** F036
- **Location:** `src/residual_analysis.py:6 (FORMAT_CSV) and the CSV branch ~line 154-177`
- **Change:** Resolve the FORMAT_CSV dead path: either implement CSV writing (flatten residual arrays to columns and np.savetxt / csv.writer, return True on success) or remove the FORMAT_CSV constant and its branch entirely so save_residuals does not advertise an unsupported format that always returns False.
- **Verification signal:** Either save_residuals(..., format=FORMAT_CSV) writes a readable .csv and returns True, or FORMAT_CSV is gone and `grep -n 'FORMAT_CSV' src/residual_analysis.py` returns nothing; no code path silently returns False for an advertised format.
- **Depends on:** C2

### C46 [P3] — Fix redundant clone+upstream remote instructions

- **Closes:** F057
- **Location:** `docs/onboarding-guide.md:72-80`
- **Change:** Correct the remote setup: either (A) describe the real fork workflow (fork on GitHub, clone the fork as origin, add the canonical repo as upstream), or (B) drop the `git remote add upstream <same-url-as-origin>` step entirely since it currently points upstream at the same URL as origin. Make origin/upstream meaningfully distinct or remove the redundant remote.
- **Verification signal:** docs/onboarding-guide.md no longer instructs adding an upstream remote identical to origin; the documented remotes are either a fork+upstream pair with distinct URLs or origin only.
- **Depends on:** nothing

### C47 [P3] — Fix contradictory tasks.json location in windows guide

- **Closes:** F058
- **Location:** `docs/task-master-windows-guide.md:331-333`
- **Change:** Resolve the contradiction between the diagram (tasks.json at root) and the comment ('in tasks/ directory'). Make the diagram position and the comment agree on a single canonical location for tasks.json (match wherever task-master actually writes it — typically tasks/tasks.json), and fix the tree indentation accordingly.
- **Verification signal:** In docs/task-master-windows-guide.md the tasks.json tree position and its inline comment describe the same directory; no longer 'at root' while commented 'in tasks/'.
- **Depends on:** nothing

### C48 [P3] — Un-ignore .cursor so shared workflow rules are version-controlled

- **Closes:** F054
- **Location:** `.gitignore:201`
- **Change:** Remove (or narrow) the `.cursor` entry in .gitignore so the project's Cursor workflow rules can be shared. If only local state should be ignored, replace the blanket `.cursor` with a narrower pattern (e.g. `.cursor/cache/`) and keep `.cursor/rules` tracked.
- **Verification signal:** `grep -n '^\.cursor$' .gitignore` returns nothing (or only a narrowed sub-path remains); `git check-ignore .cursor/rules` reports it is no longer ignored.
- **Depends on:** nothing

### C49 [P3] — Repair truncated/broken Paper 9 ADS link in rebound_readme.md

- **Closes:** F055
- **Location:** `rebound_readme.md:115`
- **Change:** Fix the truncated `https://ui.adsabs.harvard.edu/abs/` URL by appending the correct ADS bibcode for Paper 9 (matching the completeness of Papers 1-8 which include full bibcodes). If the exact bibcode cannot be determined, replace with the paper's arXiv/DOI link so the reference resolves to the specific paper rather than the ADS search page.
- **Verification signal:** rebound_readme.md:115 contains a complete URL with a bibcode/identifier (not ending at '/abs/'); following the link resolves to a specific paper, not the ADS search homepage.
- **Depends on:** nothing

### C50 [P3] — Remove unused scipy.stats import from parameter_sampler

- **Closes:** F035
- **Location:** `src/parameter_sampler.py:2`
- **Change:** Either remove the unused `import scipy.stats as stats` (no `stats.<fn>` is called anywhere in the module) or, if scipy distributions are intended for the sampling (e.g. truncated Maxwellian velocity), actually use them. Minimal fix: delete the unused import.
- **Verification signal:** `grep -n 'scipy' src/parameter_sampler.py` shows no unused import (either gone, or scipy.stats is now actually called); `python -m pyflakes src/parameter_sampler.py` reports no 'imported but unused' for scipy.stats.
- **Depends on:** C2



<details><summary>machine-readable JSON (source of truth)</summary>

```json
{
  "items": [
    {
      "id": "C1",
      "title": "Make src/ a real importable package",
      "links_to": [
        "F049",
        "F030"
      ],
      "location": "src/__init__.py (new file)",
      "change": "Create an empty (or docstring-only) src/__init__.py so src/ stops being a namespace package and setuptools find_packages() can discover it. Add a one-line module docstring; no executable code.",
      "verification_signal": "`python -c \"import importlib,os; print(os.path.exists('src/__init__.py'))\"` prints True; `python -c \"from setuptools import find_packages; print(find_packages())\"` now includes 'src' (previously returned only ['tests']).",
      "depends_on": [],
      "priority": "P0"
    },
    {
      "id": "C2",
      "title": "Convert all intra-package imports to explicit relative imports",
      "links_to": [
        "F008",
        "F019",
        "F045"
      ],
      "location": "src/n_body_simulation.py:4; src/simulation_runner.py (imports of n_body_simulation/analytic_impulse); src/ensemble_runner.py (imports of simulation_runner/parameter_sampler); src/visualization.py:510; src/synthetic_data.py (import residual_analysis)",
      "change": "Replace every bare absolute intra-project import with a package-relative form: in n_body_simulation.py:4 change `from analytic_impulse import calculate_velocity_kick, G as analytic_G` to `from .analytic_impulse import calculate_velocity_kick, G as analytic_G`. Apply the same `.module` prefix to simulation_runner.py, ensemble_runner.py, the `from ensemble_runner import calculate_detection_rates` at visualization.py:510, and synthetic_data.py's `import residual_analysis`. For the `__main__` blocks that must still run as scripts, guard the relative import with a try/except ImportError falling back to the absolute import, OR document running them only via `python -m src.<module>`.",
      "verification_signal": "`python -m src.simulation_runner` and `python -m src.ensemble_runner` no longer raise `ModuleNotFoundError: No module named 'analytic_impulse'` / `ImportError: attempted relative import with no known parent package`; `python -m src.visualization` no longer prints 'Skipping binned rate plot example (requires ensemble_runner module)'.",
      "depends_on": [
        "C1"
      ],
      "priority": "P0"
    },
    {
      "id": "C3",
      "title": "Fix setup.py packaging and remove test tools from runtime deps",
      "links_to": [
        "F030",
        "F029",
        "F049"
      ],
      "location": "setup.py:9,10-17",
      "change": "Change `packages=find_packages()` to `packages=find_packages(include=['src', 'src.*'])` (now resolvable thanks to C1). Remove 'pytest' and 'pytest-cov' from install_requires (line 15-16) and instead add `extras_require={'test': ['pytest', 'pytest-cov']}`. Add the actually-imported runtime deps to install_requires: add 'tqdm' (used at ensemble_runner.py:6). Keep numpy, matplotlib, scipy, rebound.",
      "verification_signal": "`pip install .` succeeds; `python -c \"import pkg_resources; d=pkg_resources.get_distribution('primordial_encounters'); print([str(r) for r in d.requires()])\"` shows pytest/pytest-cov absent from the default requires; `python -c \"from setuptools import find_packages; print(find_packages(include=['src','src.*']))\"` includes 'src'.",
      "depends_on": [
        "C1"
      ],
      "priority": "P0"
    },
    {
      "id": "C4",
      "title": "Declare tqdm in requirements.txt",
      "links_to": [
        "F039"
      ],
      "location": "requirements.txt:1-5 (Core Dependencies block)",
      "change": "Add `tqdm` to the Core Dependencies section of requirements.txt (it is imported unconditionally at ensemble_runner.py:6 but currently absent). Keep the line in the core block, not the optional block, since ensemble_runner imports it at module load.",
      "verification_signal": "`grep -i '^tqdm' requirements.txt` returns a match; in a fresh venv `pip install -r requirements.txt && python -c 'import src.ensemble_runner'` completes without `ModuleNotFoundError: No module named 'tqdm'`.",
      "depends_on": [],
      "priority": "P0"
    },
    {
      "id": "C5",
      "title": "Fix PBH mass key mismatch between sampler and runner",
      "links_to": [
        "F004",
        "F016"
      ],
      "location": "src/simulation_runner.py:84",
      "change": "Change the lookup `pbh_params['mass']` to `pbh_params['mass_msun']` to match the key emitted by parameter_sampler.generate_pbh_sample. Alternatively standardize on a single contract by normalizing keys at the runner boundary, but the minimal correct diff is to read 'mass_msun'.",
      "verification_signal": "Calling `run_single_simulation(..., pbh_params=generate_pbh_sample(1)[0])` no longer raises `KeyError: 'mass'` at line 84; the perturbed branch proceeds past mass extraction.",
      "depends_on": [
        "C2"
      ],
      "priority": "P0"
    },
    {
      "id": "C6",
      "title": "Fix impact-parameter key so sampled value is not silently discarded",
      "links_to": [
        "F005"
      ],
      "location": "src/simulation_runner.py:91",
      "change": "Change `pbh_params.get('impact_param', 100.0)` to `pbh_params['impact_param_au']` (or `.get('impact_param_au')` with an explicit error if missing) so the sampled impact parameter is used instead of the silent 100.0 AU default.",
      "verification_signal": "With pbh_params containing impact_param_au=0.5, the value used in the PBH initial-position calculation is 0.5 (not 100.0); add a temporary assert/print to confirm, or unit-test that the consumed b equals the sampled impact_param_au.",
      "depends_on": [
        "C2"
      ],
      "priority": "P0"
    },
    {
      "id": "C7",
      "title": "Correct km/s -> AU/day conversion constant (~86x error)",
      "links_to": [
        "F003",
        "F017"
      ],
      "location": "src/parameter_sampler.py:11",
      "change": "Replace `KM_S_TO_AU_DAY = 1.0/1.731e6*86400.0` (=4.99e-2) with the correct constant: 1 km/s = 86400 km/day / 1.496e8 km/AU = 5.7754e-4 AU/day. Set `KM_S_TO_AU_DAY = 86400.0 / 1.496e8`. Add an inline comment showing the derivation.",
      "verification_signal": "`python -m src.parameter_sampler` produces sampled velocity magnitudes ~0.1-0.25 AU/day for sigma_v~200 km/s (was ~10-25 AU/day); `python -c \"print(86400/1.496e8)\"` ~5.78e-4 matches the new constant.",
      "depends_on": [
        "C2"
      ],
      "priority": "P0"
    },
    {
      "id": "C8",
      "title": "Restore REBOUND 5.x API compatibility for body setup and particle naming",
      "links_to": [
        "F009",
        "F006"
      ],
      "location": "src/n_body_simulation.py: add_solar_system (~line 90-99), add_pbh, apply_analytic_kick (label lookup ~line 214), get_particle_data",
      "change": "REBOUND 5.x removed `Simulation.add_solar_system()` and the `label` particle kwarg, and exposes particle identity via `p.name`. (1) In add_solar_system, replace the removed `sim.add_solar_system()` call with explicit particle additions (sim.add(m=..., x=..., v=...)) or an `astroquery.jplhorizons`-sourced state set; if a quick fix is wanted, add the Sun + planets explicitly with masses. (2) Everywhere particles are created with `label=...`, use `name=...`. (3) Replace `getattr(p, 'label', None)` lookups with `p.name`. Keep the public method signatures stable.",
      "verification_signal": "`python -m src.n_body_simulation` no longer prints `'Simulation' object has no attribute 'add_solar_system'` nor `TypeError: Particle.__init__() got an unexpected keyword argument 'label'`; add_pbh adds the particle and apply_analytic_kick can locate bodies by name (returns True for a valid target).",
      "depends_on": [
        "C2"
      ],
      "priority": "P0"
    },
    {
      "id": "C9",
      "title": "Stop swallowing body-setup exceptions silently",
      "links_to": [
        "F009"
      ],
      "location": "src/n_body_simulation.py:97-99 (add_solar_system try/except)",
      "change": "Replace the broad `try/except Exception: print(...)` that lets the simulation continue with 0 particles. Either re-raise after logging, or raise a clear RuntimeError('Failed to initialize Solar System bodies: ...') so callers cannot proceed with an empty simulation. Do not return normally on failure.",
      "verification_signal": "Forcing a setup failure (e.g. invalid integrator) causes add_solar_system to raise/propagate rather than printing an error and continuing; a subsequent run_simulation does not execute on a 0-particle simulation.",
      "depends_on": [
        "C8"
      ],
      "priority": "P1"
    },
    {
      "id": "C10",
      "title": "Remove hardcoded 'body_3' kick target; derive target from configured bodies",
      "links_to": [
        "F006",
        "F021"
      ],
      "location": "src/simulation_runner.py:104",
      "change": "Replace the hardcoded `target_body_label='body_3'` with a parameter (e.g. `target_body` argument threaded from the caller / config) or a lookup that selects the intended planet by name present in the configured body set. Validate the target exists in the simulation (raise a clear error if get_particle_state returns None) instead of silently producing (None, None).",
      "verification_signal": "Running the perturbed path on the configured body set (Sun, body_1, body_2) no longer returns (None, None) from get_particle_state for the kick target; the kick is applied to an existing body, and an invalid target name raises a descriptive error.",
      "depends_on": [
        "C8"
      ],
      "priority": "P1"
    },
    {
      "id": "C11",
      "title": "Fix inverted analytic velocity-kick direction (repulsive -> attractive)",
      "links_to": [
        "F011"
      ],
      "location": "src/analytic_impulse.py:66",
      "change": "Change `kick_direction = -r_ca / b` to `kick_direction = +r_ca / b` (or equivalently remove the leading minus) so the gravitational impulse points TOWARD the PBH at closest approach. r_ca is the vector from target to PBH at closest approach; an attractive impulse must be parallel to it.",
      "verification_signal": "In the analytic_impulse __main__ probe, `np.dot(delta_v/|delta_v|, r_ca/|r_ca|)` returns +1.0 (was -1.0); the kicked body's velocity change points toward the PBH.",
      "depends_on": [
        "C2"
      ],
      "priority": "P1"
    },
    {
      "id": "C12",
      "title": "Correct unphysical example PBH velocity (~820x too large)",
      "links_to": [
        "F018"
      ],
      "location": "src/analytic_impulse.py:104-105",
      "change": "Replace the hardcoded velocity `5510` AU/(yr/2pi) and its wrong comment. For 200 km/s: 1 AU/(yr/2pi) = 29.79 km/s, so 200 km/s = 6.71 AU/(yr/2pi). Set the example velocity to ~6.71 and fix the comment chain (200 km/s -> 0.1155 AU/day -> 6.71 AU/(yr/2pi)). Prefer computing it from KM_S_TO_AU_DAY (after C7) rather than a magic number.",
      "verification_signal": "`python src/analytic_impulse.py` uses a PBH speed of ~6.7 AU/(yr/2pi) (well below c); the resulting delta_v magnitude is physically plausible and the inline comment's intermediate values are self-consistent.",
      "depends_on": [
        "C7",
        "C11"
      ],
      "priority": "P1"
    },
    {
      "id": "C13",
      "title": "Eliminate PBH perturbation double-counting (live mass AND impulse)",
      "links_to": [
        "F040"
      ],
      "location": "src/simulation_runner.py:94-116",
      "change": "Choose ONE perturbation model per the paper's impulse approximation: either (A) add the PBH as a live gravitating body and run full N-body WITHOUT also calling apply_analytic_kick, or (B) do NOT add the PBH mass to the integrator and apply only the analytic impulse kick to the target. Implement (B) as the default to match the impulse-approximation methodology: skip add_pbh's gravitational contribution (mass=0 or omit the body) when the analytic kick is used. Gate the choice behind an explicit `method` flag.",
      "verification_signal": "Inspecting the perturbed run: exactly one of {PBH live gravitational mass in the integrator, analytic impulse applied} is active for a given method; a test comparing residual magnitude to the analytic single-kick prediction agrees to within integrator tolerance (not ~2x).",
      "depends_on": [
        "C8",
        "C10",
        "C11"
      ],
      "priority": "P1"
    },
    {
      "id": "C14",
      "title": "Compute physical PBH initial position from encounter geometry",
      "links_to": [
        "F010",
        "F020"
      ],
      "location": "src/simulation_runner.py:89-91",
      "change": "Replace the placeholder `pbh_initial_pos = np.array([-1000.0, impact_param, 0.0])` with a position derived from the sampled encounter parameters: given impact parameter b (impact_param_au, C6), incoming velocity vector v_inf (velocity_au_day), encounter time t_encounter, and approach angles (theta, phi from C15), place the PBH back-tracked along -v_inf from the closest-approach point so that at t_encounter it reaches closest approach at distance b from the target. Document the geometry in a comment.",
      "verification_signal": "The PBH's straight-line trajectory passes within b of the target at the sampled t_encounter (assert min distance over the integration window equals impact_param_au within tolerance); the initial position varies with t_encounter and v_inf (no longer constant -1000 AU).",
      "depends_on": [
        "C6",
        "C13",
        "C15"
      ],
      "priority": "P1"
    },
    {
      "id": "C15",
      "title": "Sample PBH approach-direction angles so encounter geometry is complete",
      "links_to": [
        "F037"
      ],
      "location": "src/parameter_sampler.py: generate_pbh_sample (~line 85)",
      "change": "Add isotropic sampling of the PBH approach direction: sample two angles (theta from arccos(uniform(-1,1)) for polar, phi from uniform(0,2pi) for azimuth) and emit them in each sample dict (e.g. keys 'approach_theta_rad','approach_phi_rad'), and/or emit a unit approach-direction vector. These define the velocity-vector orientation consumed by C14.",
      "verification_signal": "`generate_pbh_sample(n)` dicts contain the new angle/direction keys; sampled polar angles are distributed as sin(theta) (isotropic) over many draws; simulation_runner can construct the full 3D incoming velocity from sampled speed + direction.",
      "depends_on": [
        "C7"
      ],
      "priority": "P1"
    },
    {
      "id": "C16",
      "title": "Guard dt_rebound against None when dt_years is falsy",
      "links_to": [
        "F043"
      ],
      "location": "src/simulation_runner.py:38 and the integration loop ~line 144",
      "change": "Change `dt_rebound = dt_years * 2 * np.pi if dt_years else None` so that a falsy/zero dt_years either raises a clear ValueError('dt_years must be positive') or falls back to a sane default, never None. Ensure the loop at ~line 144 (`sim_instance.sim.t + dt_rebound`) can never dereference None.",
      "verification_signal": "Calling run_single_simulation with dt_years=0 raises a descriptive ValueError instead of `TypeError: unsupported operand type(s) for +: 'NoneType' and 'float'`; with a valid dt_years the loop runs unchanged.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C17",
      "title": "Make mid-loop particle-count resize lossless with consistent allocation",
      "links_to": [
        "F013"
      ],
      "location": "src/simulation_runner.py:151-161",
      "change": "Use a consistent initial allocation sized to the final particle count (or a list-of-steps appended then stacked at the end) so that resizing when particle count changes does not zero-fill and discard previously recorded steps. Preserve all recorded timesteps across the resize boundary.",
      "verification_signal": "A run where particle count changes mid-integration preserves all earlier-step position/velocity data (no zero rows introduced); the output array length equals the number of integration steps recorded.",
      "depends_on": [
        "C13"
      ],
      "priority": "P3"
    },
    {
      "id": "C18",
      "title": "Preserve pre-encounter (t_start) state across post-kick array reallocation",
      "links_to": [
        "F041"
      ],
      "location": "src/simulation_runner.py:126-133",
      "change": "Stop overwriting step-0 (the t=0/t_start pre-encounter state captured at lines ~67-75) when arrays are reallocated after the kick. Record the kicked state as a NEW step rather than overwriting index 0, or store pre-encounter and post-kick states in separate slots so the baseline-vs-perturbed residual at t_start is genuinely zero.",
      "verification_signal": "In a perturbed run, positions_out[0] equals the captured pre-encounter state (not zeros and not the t_ca state); residual at t_start computed against baseline is ~0.",
      "depends_on": [
        "C13"
      ],
      "priority": "P1"
    },
    {
      "id": "C19",
      "title": "Reconcile apply_analytic_kick docstring with implementation",
      "links_to": [
        "F044"
      ],
      "location": "src/n_body_simulation.py:201-215",
      "change": "Fix the contract mismatch: either change the docstring (lines ~202-204) to state that the kick is computed at the current simulation time (matching the implementation at ~214), or enforce the documented t=0 precondition with an assertion. Make docstring and behavior agree.",
      "verification_signal": "Docstring statement about simulation time matches the code path actually taken; if an assertion is added, calling apply_analytic_kick at t!=0 raises the documented error.",
      "depends_on": [
        "C8"
      ],
      "priority": "P3"
    },
    {
      "id": "C20",
      "title": "Remove nested multiprocessing in ensemble members (daemon crash)",
      "links_to": [
        "F038"
      ],
      "location": "src/ensemble_runner.py:64 (run_ensemble_member) and src/simulation_runner.py run_parallel_simulations",
      "change": "Inside run_ensemble_member, replace the call to `simulation_runner.run_parallel_simulations(...)` (which spawns its own multiprocessing.Pool inside an already-daemonic pool worker) with two sequential calls to `run_single_simulation` (baseline, then perturbed). The outer ensemble Pool provides the parallelism; the inner per-member work must be serial. Keep run_parallel_simulations for standalone (non-ensemble) use only.",
      "verification_signal": "Running run_ensemble with >=1 member no longer prints `AssertionError: daemonic processes are not allowed to have children`; each member completes its baseline+perturbed sims.",
      "depends_on": [
        "C5",
        "C6",
        "C8"
      ],
      "priority": "P0"
    },
    {
      "id": "C21",
      "title": "Add missing return statement to run_ensemble",
      "links_to": [
        "F007",
        "F015"
      ],
      "location": "src/ensemble_runner.py: end of run_ensemble (~line 277)",
      "change": "Add `return ensemble_results` (the accumulated list of per-member summary dicts) at the end of run_ensemble so the caller's `for r in ensemble_results` and downstream detection-rate analysis receive a list instead of None. Confirm the variable holding the collected member summaries is the one returned.",
      "verification_signal": "`results = run_ensemble(...)` returns a list whose length equals the number of members (not None); `len(results)` and iteration succeed; the __main__ block's `for r in ensemble_results` no longer raises TypeError.",
      "depends_on": [
        "C20"
      ],
      "priority": "P0"
    },
    {
      "id": "C22",
      "title": "Make summaries/checkpoints/results JSON-serializable (numpy types)",
      "links_to": [
        "F012"
      ],
      "location": "src/ensemble_runner.py:136, 249, 263 (json.dump calls)",
      "change": "Add a numpy-aware JSON encoder (subclass json.JSONEncoder converting np.ndarray->tolist(), np.integer->int, np.floating->float) and pass `cls=NpEncoder` (or `default=` callable) to every json.dump/json.dumps. Apply at member-summary save (136), checkpoint (249), and final-results (263). Ensure pbh_params['velocity_au_day'] (an ndarray) serializes.",
      "verification_signal": "run_ensemble completes without `TypeError: Object of type ndarray is not JSON serializable`; the per-member summary JSON and final results JSON files are written and re-loadable with json.load.",
      "depends_on": [
        "C20"
      ],
      "priority": "P1"
    },
    {
      "id": "C23",
      "title": "Fix detection-rate denominator inflation by unclassifiable members",
      "links_to": [
        "F046"
      ],
      "location": "src/ensemble_runner.py:367-372 (calculate_detection_rates)",
      "change": "Reorder so total_completed is incremented only for classifiable members. Move the `total_completed += 1` (line 367) to AFTER the is_detected check, and `continue` (skip) members where is_detected returns None WITHOUT counting them in the denominator. Equivalently, count only members with non-None stats in total_completed.",
      "verification_signal": "Harness test (1 unclassifiable + 1 detected) yields rate 1.0 (was 0.5); total_completed excludes members with stats=None; aggregate rate equals sum over bins.",
      "depends_on": [
        "C21"
      ],
      "priority": "P1"
    },
    {
      "id": "C24",
      "title": "Compute true 3D peak displacement instead of norm of per-dimension maxima",
      "links_to": [
        "F048"
      ],
      "location": "src/ensemble_runner.py:316 (is_detected) and src/residual_analysis.py:calculate_peak",
      "change": "The detection magnitude must be the maximum over time of the per-timestep 3D displacement norm, not the norm of per-dimension temporal maxima. Add/use a statistic = max_t( sqrt(dx_t^2+dy_t^2+dz_t^2) ) computed from the full residual time series, and have is_detected use it. Either add a 'peak_disp_au' stat in calculate_residual_stats (from the time series) or recompute in is_detected from stored residuals.",
      "verification_signal": "For the documented case (peak_x at t1, peak_y at t2) the detection magnitude equals the true max 3D displacement (e.g. 1e-5), not sqrt(2)*1e-5; a unit test on a synthetic residual series confirms peak == max over time of pointwise norm.",
      "depends_on": [
        "C21"
      ],
      "priority": "P2"
    },
    {
      "id": "C25",
      "title": "Remove eval() on metadata loaded from .npz (arbitrary code execution)",
      "links_to": [
        "F001",
        "F026"
      ],
      "location": "src/residual_analysis.py:215 (and save_residuals metadata serialization ~line 138)",
      "change": "Stop using `eval(metadata_str)` to deserialize metadata. Change save_residuals to store metadata as a JSON string (json.dumps(meta_dict)) instead of str(dict), and change load_residuals to parse it with json.loads(). If legacy str(dict) files must still be read, use ast.literal_eval (safe, no code execution) as a fallback — never eval().",
      "verification_signal": "`grep -n 'eval(' src/residual_analysis.py` returns no eval() on loaded data; load_residuals round-trips metadata via json.loads; a crafted .npz whose metadata string contains `__import__('os').system(...)` does NOT execute (raises a parse error instead).",
      "depends_on": [
        "C2"
      ],
      "priority": "P1"
    },
    {
      "id": "C26",
      "title": "Avoid unsafe allow_pickle deserialization of .npz files",
      "links_to": [
        "F002"
      ],
      "location": "src/residual_analysis.py:206 (np.load)",
      "change": "Stop relying on `np.load(filepath, allow_pickle=True)`. Once metadata is stored as a JSON string (C25), arrays and the metadata string can be loaded with `np.load(filepath)` (allow_pickle=False, the safe default). Store metadata as a 0-d string array or a sidecar .json so pickled Python objects are never required.",
      "verification_signal": "`np.load(path)` (default allow_pickle=False) succeeds for files written by the updated save_residuals; `grep -n 'allow_pickle=True' src/residual_analysis.py` returns nothing.",
      "depends_on": [
        "C25"
      ],
      "priority": "P2"
    },
    {
      "id": "C27",
      "title": "Implement q_fom figure-of-merit (paper Eq. 17)",
      "links_to": [
        "F022"
      ],
      "location": "src/residual_analysis.py:233-240 (commented-out stub)",
      "change": "Implement calculate_q_fom(residuals, noise) replacing the commented-out stub. Per Tran et al. (arXiv:2312.17217v3) Eq. (17), compute the signal-to-noise figure-of-merit as the quadrature sum over observations of (residual / measurement uncertainty), i.e. q_fom = sqrt( sum_i (r_i / sigma_i)^2 ) using the residual time series and the per-observation noise floor (sigma supplied by caller / synthetic_data). Wire it in as the detection statistic used by ensemble detection logic instead of the raw peak-residual proxy. Document the exact equation mapping in the docstring.",
      "verification_signal": "calculate_q_fom returns a finite scalar for a residual+noise input; for zero residuals q_fom==0; for residual==k*sigma uniformly over N points q_fom==k*sqrt(N); a unit test against a hand-computed small case matches.",
      "depends_on": [
        "C2"
      ],
      "priority": "P1"
    },
    {
      "id": "C28",
      "title": "Warn/handle np.interp boundary clipping in compute_residuals",
      "links_to": [
        "F042"
      ],
      "location": "src/residual_analysis.py:98",
      "change": "np.interp silently clamps to boundary values when the perturbed/baseline time ranges do not overlap. Either restrict the residual computation to the overlapping time window, or detect out-of-range query times and emit a warning (warnings.warn) / set those residuals to NaN rather than silently clipping. Document the chosen behavior.",
      "verification_signal": "For non-overlapping time ranges (e.g. base_times=[0,0.5], pert_times=[0.1,0.4]) compute_residuals emits a warning or returns NaN outside the overlap, instead of silently returning clipped boundary values; a unit test asserts the warning/NaN.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C29",
      "title": "Move residual-stats calculation out of the failure-only else branch",
      "links_to": [
        "F027"
      ],
      "location": "src/residual_analysis.py:394-410 (__main__)",
      "change": "The calculate_residual_stats block (lines ~397-410) sits inside the `else:` branch that only runs when compute_residuals FAILS, so it is dead code on success. Move the stats calculation into the success path (the `if` branch) so statistics are computed and printed when residuals are produced.",
      "verification_signal": "`python src/residual_analysis.py` (success path) now prints 'Calculating Residual Statistics' / the stats output in the main block; the stats block executes when compute_residuals succeeds.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C30",
      "title": "Implement or remove the dead CSV save path",
      "links_to": [
        "F036"
      ],
      "location": "src/residual_analysis.py:6 (FORMAT_CSV) and the CSV branch ~line 154-177",
      "change": "Resolve the FORMAT_CSV dead path: either implement CSV writing (flatten residual arrays to columns and np.savetxt / csv.writer, return True on success) or remove the FORMAT_CSV constant and its branch entirely so save_residuals does not advertise an unsupported format that always returns False.",
      "verification_signal": "Either save_residuals(..., format=FORMAT_CSV) writes a readable .csv and returns True, or FORMAT_CSV is gone and `grep -n 'FORMAT_CSV' src/residual_analysis.py` returns nothing; no code path silently returns False for an advertised format.",
      "depends_on": [
        "C2"
      ],
      "priority": "P3"
    },
    {
      "id": "C31",
      "title": "Make plot functions headless-safe (no unconditional plt.show)",
      "links_to": [
        "F028"
      ],
      "location": "src/visualization.py:76,175,314,384",
      "change": "Add a `show=False` (or `save_path`) parameter to each plot function; call plt.show() only when show=True. Default to saving to file and not blocking. This lets batch/headless ensemble runs generate plots without a blocking GUI call.",
      "verification_signal": "With show=False (the default for batch use), plot functions return/save without calling plt.show(); `grep -n 'plt.show' src/visualization.py` shows each call guarded by a conditional; `python -m src.visualization` under a non-Agg backend does not block.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C32",
      "title": "Fix mislabeled residual time-series plot (index basis mismatch)",
      "links_to": [
        "F047"
      ],
      "location": "src/visualization.py:137",
      "change": "plot_residual_timeseries uses residuals-array-local indices (valid_indices 0..n-1) to index a labels list documented as indexed by original particle indices. Fix by indexing labels with the ORIGINAL particle indices (e.g. `plot_labels = [labels[orig_idx] for orig_idx in particle_indices]`) rather than the array-local positions, OR clearly redefine `labels` to be array-local and document it. Ensure each plotted line gets its correct body label.",
      "verification_signal": "With particle_indices=[0,1] and labels=['Sun','Earth','PlanetX'], the line for the body at original index 1 is labeled 'Earth' (not 'Sun'); a unit/visual check confirms label-to-curve correspondence.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C33",
      "title": "Replace single-flyby example stub with a real end-to-end demo",
      "links_to": [
        "F014",
        "F025"
      ],
      "location": "examples/single_flyby_example.py:18-34",
      "change": "Replace the placeholder print-only function with a runnable demo that: imports the package modules; builds a small body set; samples or hardcodes one PBH encounter (mass_msun, impact_param_au, velocity, t_encounter, approach angles); runs baseline + perturbed simulations via simulation_runner; computes residuals via residual_analysis; and prints/saves the position residual time series (optionally plots via visualization with show=False). No 'will:' placeholder text.",
      "verification_signal": "`python examples/single_flyby_example.py` runs a real simulation and outputs a residual time series (array shapes printed, optional .npz/.png saved); the placeholder lines 'This is a placeholder example. The actual implementation will:' are gone.",
      "depends_on": [
        "C5",
        "C6",
        "C7",
        "C8",
        "C10",
        "C11",
        "C13",
        "C14",
        "C18"
      ],
      "priority": "P1"
    },
    {
      "id": "C34",
      "title": "Implement spectral analysis of residuals (documented, missing module)",
      "links_to": [
        "F032"
      ],
      "location": "src/spectral_analysis.py (new file); referenced by README.md:58 and docs/pseudocode.md:282-308",
      "change": "Create src/spectral_analysis.py implementing FFT/periodogram analysis of the residual time series to characterize the near-monochromatic orbital deviation (paper Fig. 3): a function taking residual_times + position_residuals and returning frequency, power spectrum, and dominant-frequency estimate. Use numpy.fft (and optionally scipy.signal.periodogram). Expose a plotting helper or integrate with visualization.",
      "verification_signal": "`python -c \"from src import spectral_analysis\"` imports; feeding a synthetic sinusoidal residual returns a spectrum whose peak frequency matches the input frequency within bin resolution; a unit test asserts the recovered dominant frequency.",
      "depends_on": [
        "C2"
      ],
      "priority": "P2"
    },
    {
      "id": "C35",
      "title": "Implement parameter-recovery / likelihood-ratio module (documented, missing)",
      "links_to": [
        "F031"
      ],
      "location": "src/parameter_recovery.py (new file); referenced by README.md:53-57 and docs/pseudocode.md:429-475",
      "change": "Create src/parameter_recovery.py that fits PBH parameters (mass, impact parameter, velocity/trajectory) from (synthetic) residuals and performs a likelihood-ratio test of the PBH-present model vs a no-PBH null. Use the already-declared emcee (MCMC posterior) and/or dynesty (nested-sampling evidence) dependencies; define a Gaussian likelihood from residuals + noise (sigma from synthetic_data) and a forward model calling the analytic impulse. Return best-fit parameters and the likelihood-ratio / log-evidence statistic.",
      "verification_signal": "`python -c \"from src import parameter_recovery\"` imports; on synthetic data generated with known PBH parameters the recovery returns posterior medians within stated tolerance of the truth, and the likelihood-ratio favors PBH-present over null for a detectable injection; `grep -n 'import emcee\\|import dynesty' src/parameter_recovery.py` confirms an inference library is actually used.",
      "depends_on": [
        "C27",
        "C25"
      ],
      "priority": "P2"
    },
    {
      "id": "C36",
      "title": "Add substantive physics-correctness tests (replace bare-pass test)",
      "links_to": [
        "F034"
      ],
      "location": "tests/test_n_body_simulation.py:23 and new tests/test_physics.py",
      "change": "Replace the bare `pass` test_initialization body with real assertions, and add tests covering verified invariants: (1) calculate_velocity_kick magnitude scales linearly with PBH mass and as 1/(b*v) (paper Eq. 2); (2) kick direction points toward the PBH (np.dot(dv_hat, r_ca_hat)==+1, regression for F011); (3) KM_S_TO_AU_DAY equals 86400/1.496e8 (regression for F003); (4) baseline-vs-baseline residuals are exactly zero; (5) calculate_detection_rates excludes unclassifiable members (regression for F046). Use numpy.testing.assert_allclose with explicit tolerances.",
      "verification_signal": "`python -m pytest -q` collects and PASSES the new physics tests (not skipped); test_initialization no longer a bare pass; tests fail if C7/C11/C46-fixes are reverted (true regression guards).",
      "depends_on": [
        "C7",
        "C11",
        "C23",
        "C5",
        "C8"
      ],
      "priority": "P1"
    },
    {
      "id": "C37",
      "title": "Correct README project-structure module listing",
      "links_to": [
        "F023"
      ],
      "location": "README.md:128-132",
      "change": "Replace the nonexistent module names (nbody.py, pbhsampler.py, residuals.py, parameter_recovery.py) with the actual src/ contents: analytic_impulse.py, ensemble_runner.py, n_body_simulation.py, parameter_sampler.py, residual_analysis.py, simulation_runner.py, synthetic_data.py, visualization.py, plus the newly added spectral_analysis.py and parameter_recovery.py (C34/C35).",
      "verification_signal": "Every module path listed in README.md project structure exists on disk (`ls src/<name>` succeeds for each); no listed file is missing.",
      "depends_on": [
        "C34",
        "C35"
      ],
      "priority": "P2"
    },
    {
      "id": "C38",
      "title": "Fix README Usage section to reference real interfaces",
      "links_to": [
        "F024"
      ],
      "location": "README.md:98-99 (and surrounding Usage examples)",
      "change": "Replace the invented CLI invocations (`python scripts/single_flyby.py --mass ... --r0 ... --alpha ... --beta ...`, ensemble_flyby.py, param_recovery.py) with the actual runnable entry points: `python examples/single_flyby_example.py` (after C33) and `python -m src.ensemble_runner` / documented function-call usage. Remove flags that match no implemented argparse interface, or add an argparse CLI if flags are desired and document the real flag names.",
      "verification_signal": "Every command shown in README Usage runs as written (no MODULE_NOT_FOUND, no unrecognized-argument errors); referenced script paths exist.",
      "depends_on": [
        "C33"
      ],
      "priority": "P2"
    },
    {
      "id": "C39",
      "title": "Add the LICENSE file referenced by README",
      "links_to": [
        "F033"
      ],
      "location": "LICENSE (new file at repo root); referenced by README.md:159-160",
      "change": "Create a LICENSE file containing the MIT License text (the README links to an MIT License), with the copyright holder set to the project author (ImmortalDemonGod) and year 2025/2026. If MIT is not intended, update README to reference the actual chosen license instead — but the README currently states MIT, so add MIT.",
      "verification_signal": "`os.path.exists('LICENSE')` is True and the file contains the MIT License header; the README.md:160 link target resolves to an existing file.",
      "depends_on": [],
      "priority": "P2"
    },
    {
      "id": "C40",
      "title": "Point npm scripts at the task-master CLI and un-ignore scripts/ (TaskMaster seed)",
      "links_to": [
        "F053"
      ],
      "location": "package.json:8-11; .gitignore:199",
      "change": "Resolvable fix that needs no unknown dev.js content: (1) In package.json change the four scripts from `node scripts/dev.js [...]` to invoke the installed task-master-ai CLI directly: `\"dev\": \"task-master next\"`, `\"list\": \"task-master list\"`, `\"generate\": \"task-master generate\"`, `\"parse-prd\": \"task-master parse-prd\"` (the `task-master` binary is provided by the task-master-ai dependency in node_modules/.bin, so `npm run` resolves it; subcommands list/generate/parse-prd/next were confirmed present via `task-master --help`). (2) In .gitignore remove (or comment) line 199 `scripts/` so any future generated seed (e.g. a committed PRD) CAN be version-controlled. This eliminates the dependence on the absent scripts/dev.js without inventing its contents.",
      "verification_signal": "`npm install` then `npm run list` no longer fails with `Cannot find module .../scripts/dev.js`; it invokes the task-master CLI (prints the task list or a clean 'no tasks file found' message). `grep -n '^scripts/' .gitignore` returns nothing.",
      "depends_on": [],
      "priority": "P1"
    },
    {
      "id": "C41",
      "title": "Document TaskMaster bootstrap so contributors regenerate the task DB",
      "links_to": [
        "F053"
      ],
      "location": "docs/onboarding-guide.md (TaskMaster workflow section); README.md (setup)",
      "change": "Add an explicit bootstrap step instructing contributors to generate the local TaskMaster state themselves rather than relying on a committed scripts/dev.js: `npx task-master-ai init` (scaffolds config), then `task-master parse-prd <path-to-PRD>` to build tasks. State that scripts/ is now committable (after C40) so a shared PRD can be checked in. This closes the gap left by the absent generated files using only determinable CLI commands.",
      "verification_signal": "docs/onboarding-guide.md contains a step-by-step TaskMaster init/parse-prd bootstrap using `npx task-master-ai init` and `task-master parse-prd`; following it on a clean checkout produces a tasks file without referencing scripts/dev.js.",
      "depends_on": [
        "C40"
      ],
      "priority": "P2"
    },
    {
      "id": "C42",
      "title": "Remove hardcoded developer username from run-task-master.bat",
      "links_to": [
        "F050"
      ],
      "location": "run-task-master.bat:7-8",
      "change": "Replace the hardcoded `C:\\Users\\Shadow\\AppData\\Roaming\\npm` paths with the portable `%USERNAME%` / `%APPDATA%` form (e.g. `%APPDATA%\\npm`) or, preferably, delegate to `npx task-master-ai %*` which needs no PATH hardcoding. Remove all literal 'Shadow' references.",
      "verification_signal": "`grep -i 'Shadow' run-task-master.bat` returns nothing; the wrapper uses %APPDATA%/%USERNAME% or npx so it runs under any Windows user account.",
      "depends_on": [],
      "priority": "P1"
    },
    {
      "id": "C43",
      "title": "Consolidate the three inconsistent run-task-master wrapper versions",
      "links_to": [
        "F051"
      ],
      "location": "run-task-master.bat:1-8; docs/onboarding-guide.md:112-115; docs/task-master-windows-guide.md:65-72",
      "change": "Pick one canonical wrapper definition (recommend the simple `npx task-master-ai %*` form, consistent with C42) and make all three locations match it verbatim. Update the onboarding guide and windows guide to show the identical command as the actual run-task-master.bat.",
      "verification_signal": "The wrapper command shown in run-task-master.bat, docs/onboarding-guide.md, and docs/task-master-windows-guide.md is byte-for-byte identical; no divergent PATH-hardcoded variants remain.",
      "depends_on": [
        "C42"
      ],
      "priority": "P2"
    },
    {
      "id": "C44",
      "title": "Replace invalid Claude model ID in all TaskMaster .env examples",
      "links_to": [
        "F052"
      ],
      "location": "docs/onboarding-guide.md:102; docs/task-master-guide.md:59; docs/task-master-windows-guide.md:50,320",
      "change": "Replace the invalid `claude-3-5-sonnet-20240229` with a valid current Claude model ID. Use `claude-sonnet-4-6` (a current, valid model) for the MODEL setting in every .env example; update all four locations consistently.",
      "verification_signal": "`grep -rn 'claude-3-5-sonnet-20240229' docs/` returns nothing; every MODEL= example references a valid model id (claude-sonnet-4-6) consistently.",
      "depends_on": [],
      "priority": "P2"
    },
    {
      "id": "C45",
      "title": "Make onboarding guide cross-platform (not Windows .bat only)",
      "links_to": [
        "F056"
      ],
      "location": "docs/onboarding-guide.md:147,150,153,157,165,169,183,207,211,346,397,404,409",
      "change": "For each Windows-only `.\\run-task-master.bat <cmd>` invocation, add the Unix/macOS equivalent (`npx task-master-ai <cmd>` or `./run-task-master.sh <cmd>`) alongside it, or replace .bat-specific calls with the platform-neutral `npx task-master-ai <cmd>` form. Ensure the guide does not assume cmd.exe/PowerShell syntax for Linux/macOS contributors.",
      "verification_signal": "Every TaskMaster command in docs/onboarding-guide.md shows a non-Windows-only form (npx or .sh); a Linux/macOS contributor can follow the guide without translating .bat syntax.",
      "depends_on": [
        "C43"
      ],
      "priority": "P2"
    },
    {
      "id": "C46",
      "title": "Fix redundant clone+upstream remote instructions",
      "links_to": [
        "F057"
      ],
      "location": "docs/onboarding-guide.md:72-80",
      "change": "Correct the remote setup: either (A) describe the real fork workflow (fork on GitHub, clone the fork as origin, add the canonical repo as upstream), or (B) drop the `git remote add upstream <same-url-as-origin>` step entirely since it currently points upstream at the same URL as origin. Make origin/upstream meaningfully distinct or remove the redundant remote.",
      "verification_signal": "docs/onboarding-guide.md no longer instructs adding an upstream remote identical to origin; the documented remotes are either a fork+upstream pair with distinct URLs or origin only.",
      "depends_on": [],
      "priority": "P3"
    },
    {
      "id": "C47",
      "title": "Fix contradictory tasks.json location in windows guide",
      "links_to": [
        "F058"
      ],
      "location": "docs/task-master-windows-guide.md:331-333",
      "change": "Resolve the contradiction between the diagram (tasks.json at root) and the comment ('in tasks/ directory'). Make the diagram position and the comment agree on a single canonical location for tasks.json (match wherever task-master actually writes it — typically tasks/tasks.json), and fix the tree indentation accordingly.",
      "verification_signal": "In docs/task-master-windows-guide.md the tasks.json tree position and its inline comment describe the same directory; no longer 'at root' while commented 'in tasks/'.",
      "depends_on": [],
      "priority": "P3"
    },
    {
      "id": "C48",
      "title": "Un-ignore .cursor so shared workflow rules are version-controlled",
      "links_to": [
        "F054"
      ],
      "location": ".gitignore:201",
      "change": "Remove (or narrow) the `.cursor` entry in .gitignore so the project's Cursor workflow rules can be shared. If only local state should be ignored, replace the blanket `.cursor` with a narrower pattern (e.g. `.cursor/cache/`) and keep `.cursor/rules` tracked.",
      "verification_signal": "`grep -n '^\\.cursor$' .gitignore` returns nothing (or only a narrowed sub-path remains); `git check-ignore .cursor/rules` reports it is no longer ignored.",
      "depends_on": [],
      "priority": "P3"
    },
    {
      "id": "C49",
      "title": "Repair truncated/broken Paper 9 ADS link in rebound_readme.md",
      "links_to": [
        "F055"
      ],
      "location": "rebound_readme.md:115",
      "change": "Fix the truncated `https://ui.adsabs.harvard.edu/abs/` URL by appending the correct ADS bibcode for Paper 9 (matching the completeness of Papers 1-8 which include full bibcodes). If the exact bibcode cannot be determined, replace with the paper's arXiv/DOI link so the reference resolves to the specific paper rather than the ADS search page.",
      "verification_signal": "rebound_readme.md:115 contains a complete URL with a bibcode/identifier (not ending at '/abs/'); following the link resolves to a specific paper, not the ADS search homepage.",
      "depends_on": [],
      "priority": "P3"
    },
    {
      "id": "C50",
      "title": "Remove unused scipy.stats import from parameter_sampler",
      "links_to": [
        "F035"
      ],
      "location": "src/parameter_sampler.py:2",
      "change": "Either remove the unused `import scipy.stats as stats` (no `stats.<fn>` is called anywhere in the module) or, if scipy distributions are intended for the sampling (e.g. truncated Maxwellian velocity), actually use them. Minimal fix: delete the unused import.",
      "verification_signal": "`grep -n 'scipy' src/parameter_sampler.py` shows no unused import (either gone, or scipy.stats is now actually called); `python -m pyflakes src/parameter_sampler.py` reports no 'imported but unused' for scipy.stats.",
      "depends_on": [
        "C2"
      ],
      "priority": "P3"
    }
  ]
}
```
</details>
