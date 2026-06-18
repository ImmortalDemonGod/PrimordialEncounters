# 01 — Comprehensive Understanding

_Stage 1 of the forensic audit. Coverage denominator for all later stages. Generated 2026-06-17T14:23:24.888Z._

## Provisional intent (PROVISIONAL — refined in Stage 4)

> PROVISIONAL: PrimordialEncounters exists to provide a complete, modular computational pipeline for simulating and detecting asteroid-mass primordial black hole (PBH) flybys through the Solar System, replicating and extending the methodology of Tran et al. (arXiv:2312.17217v3). The project intends to enable researchers to: (1) run N-body simulations of PBH encounters using REBOUND with impulse-approximation shortcuts; (2) compute orbital residuals against a baseline Solar System to quantify PBH-induced perturbations; (3) run large Monte Carlo ensembles to estimate detection rates as a function of PBH mass; and (4) generate synthetic observations with noise for parameter recovery testing. The project appears to be in active early-stage development, with core physics modules implemented but a nearly absent test suite, several placeholder/stub sections in the simulation pipeline (notably PBH initial position calculation and q_fom figure-of-merit), and no evidence of end-to-end integration tests or production run scripts beyond the per-module __main__ blocks and one stub example.

## Architecture

PrimordialEncounters is a Python scientific computing framework organized as a flat src/ library with seven modules, one examples script, and a minimal test suite, plus a Node.js task management layer. The simulation pipeline flows as follows:

1. PARAMETER SAMPLING (src/parameter_sampler.py): Generates Monte Carlo PBH encounter parameter sets (mass, impact parameter, velocity vector, encounter time) with physically motivated distributions. No dependencies on other project modules.

2. N-BODY SIMULATION ENGINE (src/n_body_simulation.py): The NBodySimulation class wraps the REBOUND integrator. It can populate the Solar System from JPL Horizons via rebound.add_solar_system(), add arbitrary particles (including a PBH) with add_pbh(), advance time with integrate_to_time() or run_simulation(), and apply analytic impulse kicks via apply_analytic_kick() which calls into analytic_impulse.py.

3. ANALYTIC IMPULSE APPROXIMATION (src/analytic_impulse.py): Provides calculate_velocity_kick() implementing delta_v = 2GM/(b*v_rel) in REBOUND units (AU, Msun, yr/2pi, G=4*pi^2) and apply_kick() to update body state dicts. Used by NBodySimulation.apply_analytic_kick().

4. SIMULATION RUNNER (src/simulation_runner.py): Orchestrates paired baseline + perturbed simulation runs via run_single_simulation() (single process) and run_parallel_simulations() (two processes via multiprocessing.Pool). Each perturbed run adds a PBH, applies the analytic kick, then integrates to completion. NOTE: PBH initial position calculation from encounter parameters is an incomplete placeholder.

5. RESIDUAL ANALYSIS (src/residual_analysis.py): Takes (times, positions, velocities) tuples from both runs, interpolates the perturbed data onto the baseline time grid, and computes position and velocity residuals (perturbed - baseline). Provides calculate_rms(), calculate_peak(), calculate_residual_stats(), save_residuals() (.npz format), and load_residuals(). The figure-of-merit q_fom (Eq.17 of the paper) is stubbed as a TODO.

6. ENSEMBLE RUNNER (src/ensemble_runner.py): Drives large-scale Monte Carlo ensembles. It calls parameter_sampler.generate_pbh_sample() for N sets of PBH parameters, then fans out over them with multiprocessing.Pool calling run_ensemble_member() for each. Each member runs simulation_runner.run_parallel_simulations() and residual_analysis.compute_residuals(), then saves per-member residual .npz files and JSON summaries with checkpoint support. Post-processing functions is_detected() and calculate_detection_rates() (with optional log-spaced mass binning) aggregate results into detection rate statistics.

7. SYNTHETIC DATA (src/synthetic_data.py): Loads ideal residuals from .npz, adds independent Gaussian noise to position and velocity residuals via add_gaussian_noise(), and saves synthetic observations. Intended for parameter recovery testing.

8. VISUALIZATION (src/visualization.py): Matplotlib-based rendering: plot_trajectories_2d() for orbital paths, plot_residual_timeseries() for time-domain residual components, plot_detection_scatter() for ensemble detection metric vs. PBH parameters, and plot_binned_detection_rate() for rate-vs-mass curves with binomial error bars.

DEPENDENCY GRAPH: parameter_sampler (standalone) -> simulation_runner -> n_body_simulation -> analytic_impulse; ensemble_runner -> parameter_sampler + simulation_runner + residual_analysis; synthetic_data -> residual_analysis; visualization -> ensemble_runner (at runtime). The examples/ script is standalone. The tests/ directory only superficially tests project structure and NBodySimulation instantiation.

INFRASTRUCTURE LAYER: A Node.js task-master-ai layer (package.json, run-task-master.bat) provides AI-assisted project management (task parsing from PRD, status tracking, subtask expansion). Orchestrator_Task_Template_ROO is a prompt template for AI coding agents. The docs/ directory contains onboarding, TaskMaster usage, and pseudocode documentation. The data/ directory is empty (placeholder) and would hold ephemeris or output data.

## Coverage

- Denominator (files, excl. `audit/`): **27**
- Classified: **27**
- Visitation-evidenced via tool activity: **27**
- Unknown role: **0**

## Entry points

| Name | Kind | Location | Description |
| --- | --- | --- | --- |
| `run_single_flyby_example` | __main__ script | `examples/single_flyby_example.py:18` | Standalone example demonstrating a single PBH flyby; currently a stub that only prints parameter values. |
| `analytic_impulse __main__` | __main__ block | `src/analytic_impulse.py:99` | Demonstrates calculate_velocity_kick() and apply_kick() with a hardcoded PBH approaching Earth. |
| `ensemble_runner __main__` | __main__ block | `src/ensemble_runner.py:415` | Runs a small 10-member ensemble example with dummy initial conditions and prints detection rate statistics. |
| `n_body_simulation __main__` | __main__ block | `src/n_body_simulation.py:327` | Initializes REBOUND with JPL Solar System bodies, adds a PBH, applies analytic kick to Earth, then continues simulation. |
| `parameter_sampler __main__` | __main__ block | `src/parameter_sampler.py:123` | Generates and prints 5 default and 2 custom PBH parameter samples to demonstrate the sampling functions. |
| `residual_analysis __main__` | __main__ block | `src/residual_analysis.py:334` | Creates dummy baseline/perturbed results, computes residuals, saves/loads .npz, and computes stats. |
| `simulation_runner __main__` | __main__ block | `src/simulation_runner.py:237` | Runs a parallel baseline + perturbed simulation example with 3 bodies and a dummy PBH encounter. |
| `synthetic_data __main__` | __main__ block | `src/synthetic_data.py:120` | Loads ideal residuals from examples/residuals_example.npz, adds Gaussian noise, and saves synthetic output. |
| `visualization __main__` | __main__ block | `src/visualization.py:387` | Exercises all three plot functions (trajectories, residuals, detection scatter, binned rate) with dummy data. |
| `npm run dev / list / generate / parse-prd` | npm script | `package.json:9` | Node.js TaskMaster CLI entry points delegating to scripts/dev.js (not present in denominator); support list, generate, parse-prd sub-commands. |
| `run-task-master.bat` | CLI shell script | `run-task-master.bat:1` | Windows batch entry point forwarding all arguments to the globally-installed task-master.cmd for AI-assisted task management. |

## File inventory by role

### source (9)

| Path | Note |
| --- | --- |
| `examples/single_flyby_example.py` | Runnable example script demonstrating a single PBH flyby; currently a stub that prints placeholder text instead of invoking real simulation modules. |
| `src/analytic_impulse.py` | Implements the impulse approximation: calculate_velocity_kick() computes delta-v vector and time of closest approach; apply_kick() updates a body state dict. Uses G=4pi^2 in AU/Msun/(yr/2pi) units. |
| `src/ensemble_runner.py` | Orchestrates parallel Monte Carlo ensembles of PBH flyby simulations via multiprocessing.Pool; provides run_ensemble(), is_detected(), and calculate_detection_rates() with mass binning. |
| `src/n_body_simulation.py` | NBodySimulation class wrapping REBOUND: add_solar_system() (JPL Horizons), add_pbh(), run_simulation(), integrate_to_time(), apply_analytic_kick(), get_particle_data(). Core simulation engine. |
| `src/parameter_sampler.py` | Samples PBH encounter parameters: mass (log-uniform), impact parameter (area-uniform), velocity (Maxwell-Boltzmann in 3D, AU/day output), encounter time (uniform); generates list-of-dicts via generate_pbh_sample(). |
| `src/residual_analysis.py` | Computes position/velocity residuals (perturbed minus baseline) with time interpolation; calculates RMS and peak stats; saves/loads .npz files; q_fom calculation is stubbed as a TODO. |
| `src/simulation_runner.py` | Wraps NBodySimulation into run_single_simulation() and run_parallel_simulations() (baseline + perturbed in parallel); handles PBH placement (position calculation is currently a placeholder) and analytic kick application. |
| `src/synthetic_data.py` | Generates synthetic observed residuals by loading ideal .npz residuals and adding Gaussian noise via add_gaussian_noise(); saves synthetic output for parameter recovery testing. |
| `src/visualization.py` | Matplotlib visualization: plot_trajectories_2d(), plot_residual_timeseries() (3 component subplots), plot_detection_scatter() (ensemble scatter with log color), plot_binned_detection_rate() (errorbar plot). |

### test (3)

| Path | Note |
| --- | --- |
| `tests/__init__.py` | Empty package initializer making tests/ a Python package. |
| `tests/conftest.py` | pytest conftest that inserts the project root into sys.path so src modules are importable during test runs. |
| `tests/test_n_body_simulation.py` | TestNBodySimulation: test_initialization() is a placeholder pass; test_project_structure() verifies src/, tests/, examples/, data/ directories exist. No substantive logic tests yet. |

### doc (7)

| Path | Note |
| --- | --- |
| `Orchestrator_Task_Template_ROO` | Prompt template for AI orchestrator agents (Roo/Claude) describing how to scope, decompose, and delegate development tasks. |
| `README.md` | Main project README describing PrimordialEncounters framework, features, usage commands, and directory structure. |
| `docs/onboarding-guide.md` | Comprehensive contributor onboarding guide covering environment setup, TaskMaster workflow, commit conventions, testing standards, and PR procedures. |
| `docs/pseudocode.md` | Detailed module-by-module pseudocode for the full PBH simulation pipeline, closely mapping to arXiv:2312.17217v3 sections and equations. |
| `docs/task-master-guide.md` | Summary guide for the Claude Task Master AI task management system: commands, configuration, Cursor AI integration. |
| `docs/task-master-windows-guide.md` | Windows-specific setup and usage guide for Task Master, including Node.js installation, batch file setup, and troubleshooting. |
| `rebound_readme.md` | Verbatim copy of the REBOUND N-body library upstream README included as project reference documentation. |

### config (7)

| Path | Note |
| --- | --- |
| `.gitignore` | Standard Python/Node gitignore augmented with Task Master additions (logs, node_modules, tasks.json, scripts/). |
| `data/.gitkeep` | Empty placeholder file keeping the data/ directory tracked in git; comments say to remove once real data files exist. |
| `package.json` | npm package manifest declaring Node.js dependencies (task-master-ai, @anthropic-ai/sdk, etc.) and scripts (dev, list, generate, parse-prd) pointing to scripts/dev.js. |
| `pytest.ini` | pytest configuration: testpaths=tests, file/class/function naming conventions, --verbose flag. |
| `requirements.txt` | Python dependency list: rebound, numpy, scipy, matplotlib (core) plus optional jupyter, emcee, dynesty. |
| `run-task-master.bat` | Windows batch script that checks for Node.js, sets PATH, and forwards all arguments to task-master.cmd; entry point for TaskMaster CLI on Windows. |
| `setup.py` | setuptools setup script declaring Python package primordial_encounters, its dependencies, and metadata for pip-installable distribution. |

### generated (1)

| Path | Note |
| --- | --- |
| `package-lock.json` | npm lock file auto-generated from package.json; pins exact versions of Node.js dependencies including task-master-ai and @anthropic-ai/sdk. |



<details><summary>machine-readable JSON (source of truth)</summary>

```json
{
  "files": [
    {
      "path": ".gitignore",
      "role": "config",
      "note": "Standard Python/Node gitignore augmented with Task Master additions (logs, node_modules, tasks.json, scripts/)."
    },
    {
      "path": "Orchestrator_Task_Template_ROO",
      "role": "doc",
      "note": "Prompt template for AI orchestrator agents (Roo/Claude) describing how to scope, decompose, and delegate development tasks."
    },
    {
      "path": "README.md",
      "role": "doc",
      "note": "Main project README describing PrimordialEncounters framework, features, usage commands, and directory structure."
    },
    {
      "path": "data/.gitkeep",
      "role": "config",
      "note": "Empty placeholder file keeping the data/ directory tracked in git; comments say to remove once real data files exist."
    },
    {
      "path": "docs/onboarding-guide.md",
      "role": "doc",
      "note": "Comprehensive contributor onboarding guide covering environment setup, TaskMaster workflow, commit conventions, testing standards, and PR procedures."
    },
    {
      "path": "docs/pseudocode.md",
      "role": "doc",
      "note": "Detailed module-by-module pseudocode for the full PBH simulation pipeline, closely mapping to arXiv:2312.17217v3 sections and equations."
    },
    {
      "path": "docs/task-master-guide.md",
      "role": "doc",
      "note": "Summary guide for the Claude Task Master AI task management system: commands, configuration, Cursor AI integration."
    },
    {
      "path": "docs/task-master-windows-guide.md",
      "role": "doc",
      "note": "Windows-specific setup and usage guide for Task Master, including Node.js installation, batch file setup, and troubleshooting."
    },
    {
      "path": "examples/single_flyby_example.py",
      "role": "source",
      "note": "Runnable example script demonstrating a single PBH flyby; currently a stub that prints placeholder text instead of invoking real simulation modules."
    },
    {
      "path": "package-lock.json",
      "role": "generated",
      "note": "npm lock file auto-generated from package.json; pins exact versions of Node.js dependencies including task-master-ai and @anthropic-ai/sdk."
    },
    {
      "path": "package.json",
      "role": "config",
      "note": "npm package manifest declaring Node.js dependencies (task-master-ai, @anthropic-ai/sdk, etc.) and scripts (dev, list, generate, parse-prd) pointing to scripts/dev.js."
    },
    {
      "path": "pytest.ini",
      "role": "config",
      "note": "pytest configuration: testpaths=tests, file/class/function naming conventions, --verbose flag."
    },
    {
      "path": "rebound_readme.md",
      "role": "doc",
      "note": "Verbatim copy of the REBOUND N-body library upstream README included as project reference documentation."
    },
    {
      "path": "requirements.txt",
      "role": "config",
      "note": "Python dependency list: rebound, numpy, scipy, matplotlib (core) plus optional jupyter, emcee, dynesty."
    },
    {
      "path": "run-task-master.bat",
      "role": "config",
      "note": "Windows batch script that checks for Node.js, sets PATH, and forwards all arguments to task-master.cmd; entry point for TaskMaster CLI on Windows."
    },
    {
      "path": "setup.py",
      "role": "config",
      "note": "setuptools setup script declaring Python package primordial_encounters, its dependencies, and metadata for pip-installable distribution."
    },
    {
      "path": "src/analytic_impulse.py",
      "role": "source",
      "note": "Implements the impulse approximation: calculate_velocity_kick() computes delta-v vector and time of closest approach; apply_kick() updates a body state dict. Uses G=4pi^2 in AU/Msun/(yr/2pi) units."
    },
    {
      "path": "src/ensemble_runner.py",
      "role": "source",
      "note": "Orchestrates parallel Monte Carlo ensembles of PBH flyby simulations via multiprocessing.Pool; provides run_ensemble(), is_detected(), and calculate_detection_rates() with mass binning."
    },
    {
      "path": "src/n_body_simulation.py",
      "role": "source",
      "note": "NBodySimulation class wrapping REBOUND: add_solar_system() (JPL Horizons), add_pbh(), run_simulation(), integrate_to_time(), apply_analytic_kick(), get_particle_data(). Core simulation engine."
    },
    {
      "path": "src/parameter_sampler.py",
      "role": "source",
      "note": "Samples PBH encounter parameters: mass (log-uniform), impact parameter (area-uniform), velocity (Maxwell-Boltzmann in 3D, AU/day output), encounter time (uniform); generates list-of-dicts via generate_pbh_sample()."
    },
    {
      "path": "src/residual_analysis.py",
      "role": "source",
      "note": "Computes position/velocity residuals (perturbed minus baseline) with time interpolation; calculates RMS and peak stats; saves/loads .npz files; q_fom calculation is stubbed as a TODO."
    },
    {
      "path": "src/simulation_runner.py",
      "role": "source",
      "note": "Wraps NBodySimulation into run_single_simulation() and run_parallel_simulations() (baseline + perturbed in parallel); handles PBH placement (position calculation is currently a placeholder) and analytic kick application."
    },
    {
      "path": "src/synthetic_data.py",
      "role": "source",
      "note": "Generates synthetic observed residuals by loading ideal .npz residuals and adding Gaussian noise via add_gaussian_noise(); saves synthetic output for parameter recovery testing."
    },
    {
      "path": "src/visualization.py",
      "role": "source",
      "note": "Matplotlib visualization: plot_trajectories_2d(), plot_residual_timeseries() (3 component subplots), plot_detection_scatter() (ensemble scatter with log color), plot_binned_detection_rate() (errorbar plot)."
    },
    {
      "path": "tests/__init__.py",
      "role": "test",
      "note": "Empty package initializer making tests/ a Python package."
    },
    {
      "path": "tests/conftest.py",
      "role": "test",
      "note": "pytest conftest that inserts the project root into sys.path so src modules are importable during test runs."
    },
    {
      "path": "tests/test_n_body_simulation.py",
      "role": "test",
      "note": "TestNBodySimulation: test_initialization() is a placeholder pass; test_project_structure() verifies src/, tests/, examples/, data/ directories exist. No substantive logic tests yet."
    }
  ],
  "entry_points": [
    {
      "name": "run_single_flyby_example",
      "kind": "__main__ script",
      "location": "examples/single_flyby_example.py:18",
      "description": "Standalone example demonstrating a single PBH flyby; currently a stub that only prints parameter values."
    },
    {
      "name": "analytic_impulse __main__",
      "kind": "__main__ block",
      "location": "src/analytic_impulse.py:99",
      "description": "Demonstrates calculate_velocity_kick() and apply_kick() with a hardcoded PBH approaching Earth."
    },
    {
      "name": "ensemble_runner __main__",
      "kind": "__main__ block",
      "location": "src/ensemble_runner.py:415",
      "description": "Runs a small 10-member ensemble example with dummy initial conditions and prints detection rate statistics."
    },
    {
      "name": "n_body_simulation __main__",
      "kind": "__main__ block",
      "location": "src/n_body_simulation.py:327",
      "description": "Initializes REBOUND with JPL Solar System bodies, adds a PBH, applies analytic kick to Earth, then continues simulation."
    },
    {
      "name": "parameter_sampler __main__",
      "kind": "__main__ block",
      "location": "src/parameter_sampler.py:123",
      "description": "Generates and prints 5 default and 2 custom PBH parameter samples to demonstrate the sampling functions."
    },
    {
      "name": "residual_analysis __main__",
      "kind": "__main__ block",
      "location": "src/residual_analysis.py:334",
      "description": "Creates dummy baseline/perturbed results, computes residuals, saves/loads .npz, and computes stats."
    },
    {
      "name": "simulation_runner __main__",
      "kind": "__main__ block",
      "location": "src/simulation_runner.py:237",
      "description": "Runs a parallel baseline + perturbed simulation example with 3 bodies and a dummy PBH encounter."
    },
    {
      "name": "synthetic_data __main__",
      "kind": "__main__ block",
      "location": "src/synthetic_data.py:120",
      "description": "Loads ideal residuals from examples/residuals_example.npz, adds Gaussian noise, and saves synthetic output."
    },
    {
      "name": "visualization __main__",
      "kind": "__main__ block",
      "location": "src/visualization.py:387",
      "description": "Exercises all three plot functions (trajectories, residuals, detection scatter, binned rate) with dummy data."
    },
    {
      "name": "npm run dev / list / generate / parse-prd",
      "kind": "npm script",
      "location": "package.json:9",
      "description": "Node.js TaskMaster CLI entry points delegating to scripts/dev.js (not present in denominator); support list, generate, parse-prd sub-commands."
    },
    {
      "name": "run-task-master.bat",
      "kind": "CLI shell script",
      "location": "run-task-master.bat:1",
      "description": "Windows batch entry point forwarding all arguments to the globally-installed task-master.cmd for AI-assisted task management."
    }
  ],
  "architecture": "PrimordialEncounters is a Python scientific computing framework organized as a flat src/ library with seven modules, one examples script, and a minimal test suite, plus a Node.js task management layer. The simulation pipeline flows as follows:\n\n1. PARAMETER SAMPLING (src/parameter_sampler.py): Generates Monte Carlo PBH encounter parameter sets (mass, impact parameter, velocity vector, encounter time) with physically motivated distributions. No dependencies on other project modules.\n\n2. N-BODY SIMULATION ENGINE (src/n_body_simulation.py): The NBodySimulation class wraps the REBOUND integrator. It can populate the Solar System from JPL Horizons via rebound.add_solar_system(), add arbitrary particles (including a PBH) with add_pbh(), advance time with integrate_to_time() or run_simulation(), and apply analytic impulse kicks via apply_analytic_kick() which calls into analytic_impulse.py.\n\n3. ANALYTIC IMPULSE APPROXIMATION (src/analytic_impulse.py): Provides calculate_velocity_kick() implementing delta_v = 2GM/(b*v_rel) in REBOUND units (AU, Msun, yr/2pi, G=4*pi^2) and apply_kick() to update body state dicts. Used by NBodySimulation.apply_analytic_kick().\n\n4. SIMULATION RUNNER (src/simulation_runner.py): Orchestrates paired baseline + perturbed simulation runs via run_single_simulation() (single process) and run_parallel_simulations() (two processes via multiprocessing.Pool). Each perturbed run adds a PBH, applies the analytic kick, then integrates to completion. NOTE: PBH initial position calculation from encounter parameters is an incomplete placeholder.\n\n5. RESIDUAL ANALYSIS (src/residual_analysis.py): Takes (times, positions, velocities) tuples from both runs, interpolates the perturbed data onto the baseline time grid, and computes position and velocity residuals (perturbed - baseline). Provides calculate_rms(), calculate_peak(), calculate_residual_stats(), save_residuals() (.npz format), and load_residuals(). The figure-of-merit q_fom (Eq.17 of the paper) is stubbed as a TODO.\n\n6. ENSEMBLE RUNNER (src/ensemble_runner.py): Drives large-scale Monte Carlo ensembles. It calls parameter_sampler.generate_pbh_sample() for N sets of PBH parameters, then fans out over them with multiprocessing.Pool calling run_ensemble_member() for each. Each member runs simulation_runner.run_parallel_simulations() and residual_analysis.compute_residuals(), then saves per-member residual .npz files and JSON summaries with checkpoint support. Post-processing functions is_detected() and calculate_detection_rates() (with optional log-spaced mass binning) aggregate results into detection rate statistics.\n\n7. SYNTHETIC DATA (src/synthetic_data.py): Loads ideal residuals from .npz, adds independent Gaussian noise to position and velocity residuals via add_gaussian_noise(), and saves synthetic observations. Intended for parameter recovery testing.\n\n8. VISUALIZATION (src/visualization.py): Matplotlib-based rendering: plot_trajectories_2d() for orbital paths, plot_residual_timeseries() for time-domain residual components, plot_detection_scatter() for ensemble detection metric vs. PBH parameters, and plot_binned_detection_rate() for rate-vs-mass curves with binomial error bars.\n\nDEPENDENCY GRAPH: parameter_sampler (standalone) -> simulation_runner -> n_body_simulation -> analytic_impulse; ensemble_runner -> parameter_sampler + simulation_runner + residual_analysis; synthetic_data -> residual_analysis; visualization -> ensemble_runner (at runtime). The examples/ script is standalone. The tests/ directory only superficially tests project structure and NBodySimulation instantiation.\n\nINFRASTRUCTURE LAYER: A Node.js task-master-ai layer (package.json, run-task-master.bat) provides AI-assisted project management (task parsing from PRD, status tracking, subtask expansion). Orchestrator_Task_Template_ROO is a prompt template for AI coding agents. The docs/ directory contains onboarding, TaskMaster usage, and pseudocode documentation. The data/ directory is empty (placeholder) and would hold ephemeris or output data.",
  "provisional_intent": "PROVISIONAL: PrimordialEncounters exists to provide a complete, modular computational pipeline for simulating and detecting asteroid-mass primordial black hole (PBH) flybys through the Solar System, replicating and extending the methodology of Tran et al. (arXiv:2312.17217v3). The project intends to enable researchers to: (1) run N-body simulations of PBH encounters using REBOUND with impulse-approximation shortcuts; (2) compute orbital residuals against a baseline Solar System to quantify PBH-induced perturbations; (3) run large Monte Carlo ensembles to estimate detection rates as a function of PBH mass; and (4) generate synthetic observations with noise for parameter recovery testing. The project appears to be in active early-stage development, with core physics modules implemented but a nearly absent test suite, several placeholder/stub sections in the simulation pipeline (notably PBH initial position calculation and q_fom figure-of-merit), and no evidence of end-to-end integration tests or production run scripts beyond the per-module __main__ blocks and one stub example.",
  "coverage": {
    "total_files": 27,
    "classified": 27,
    "visited_evidenced": 27,
    "unknown": 0
  }
}
```
</details>
