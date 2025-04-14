# PrimordialEncounters

A comprehensive **simulation and analysis framework** for detecting primordial black hole (PBH) flybys in the Solar System. Inspired by the methodology in the paper “[Close Encounters of the Primordial Kind](https://arxiv.org/abs/2312.17217v3),” this repository implements:

- **N-body simulations** (e.g., with [REBOUND](https://github.com/hannorein/rebound))
- **Analytic impulse approximations** for PBH encounters
- **Ensemble detection rate estimation** using sampled PBH parameters
- **Parameter recovery** and significance testing to distinguish genuine PBH flybys from null hypotheses
- **Optional** spectral analysis of orbital perturbations

## Table of Contents

- [Background](#background)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Background

Asteroid-mass primordial black holes (PBHs) remain a viable dark matter candidate. If they account for a significant fraction of dark matter, their abundance implies at least one PBH might cross the inner Solar System per decade, leaving small but **potentially detectable perturbations** in planetary ephemerides.

**PrimordialEncounters** provides code to **simulate** these flybys, **quantify** the orbital perturbations, and **evaluate** the detection rates and statistical significance of PBH-like signals in a realistic Solar System model.

Key reference:
- *Close Encounters of the Primordial Kind: a new observable for primordial black holes as dark matter*
  [Tran *et al.*, arXiv:2312.17217v3]

---

## Features

1. **Modular N-Body Simulation**
   - Leverages high-precision integrators (e.g., WHFast / IAS15)
   - Imports or approximates ephemerides for the Sun, planets, and selected minor bodies

2. **Impulse Approximation**
   - Quick analytic estimates for PBH-induced velocity “kicks”
   - Useful for preliminary feasibility studies

3. **Residual Computation**
   - Compare baseline vs. PBH-perturbed orbits for Mercury, Venus, Earth, Mars, etc.
   - Compute distance residuals and time-series signatures

4. **Ensemble Detection Rate**
   - Sample PBH approach parameters (impact parameter, direction, velocity)
   - Evaluate figure-of-merit \(q_{\mathrm{fom}}\) for detection
   - Fit distribution to power laws for PBH detectability

5. **Parameter Recovery & Statistical Testing**
   - Recover PBH mass and trajectory from synthetic “observed” orbital perturbations
   - Perform likelihood ratio tests vs. a “no PBH” null hypothesis

6. **Spectral Analysis** (Optional)
   - Fourier methods to confirm the near-monochromatic nature of orbital deviations
   - Potential for advanced matched-filter approaches

---

## Getting Started

### Prerequisites

- Python 3.8+ (or your preferred language environment)
- [REBOUND](https://github.com/hannorein/rebound) or an equivalent N-body library
- [NumPy](https://numpy.org/), [SciPy](https://www.scipy.org/), [Matplotlib](https://matplotlib.org/) (for analysis and plotting)

_Optional_:
- [Jupyter Notebooks](https://jupyter.org/) for interactive exploration
- MCMC or Global Optimization libraries (e.g., `emcee`, `dynesty`) if you plan to do advanced parameter recovery

### Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/YourUserName/PrimordialEncounters.git
   cd PrimordialEncounters
   ```
2. **Install dependencies** (example using pip):
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure you have a suitable **N-body integrator** installed or accessible (e.g., `pip install rebound`).

---

## Usage

1. **Configure** your solar system model:
   - By default, scripts in `examples/` might load approximate ephemeris data.
   - Or retrieve high-precision positions/velocities from [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/app.html).

2. **Run a Single Flyby Simulation** (example call):
   ```bash
   python scripts/single_flyby.py --mass 1e-9 --r0 450 --alpha 0.004 --beta 3.1415
   ```
   - Outputs residual data, optional plots.

3. **Ensemble Analysis**:
   ```bash
   python scripts/ensemble_flyby.py --n 100000 --mass-base 1e-6
   ```
   - Samples many PBH parameters, computes detection rates, etc.

4. **Parameter Recovery**:
   ```bash
   python scripts/param_recovery.py --input residual_data.npz
   ```
   - Fits a model to “observed” residuals, returning best-fit PBH mass and significance.

For more examples and a guided walkthrough, see the [examples/](./examples) directory.

---

## Project Structure

```plaintext
PrimordialEncounters/
│
├── README.md               # This file
├── requirements.txt        # Dependencies
├── .gitignore              # Git ignore file
├── src/                    # Core library code
│   ├── nbody.py            # N-body integration wrappers
│   ├── pbhsampler.py       # PBH parameter sampling
│   ├── residuals.py        # Residual computations, q_fom, etc.
│   ├── parameter_recovery.py
│   └── ...
├── scripts/                # Command-line scripts
│   ├── single_flyby.py
│   ├── ensemble_flyby.py
│   └── param_recovery.py
├── examples/               # Example notebooks or demonstration configs
│   ├── SingleFlyby.ipynb
│   └── ...
├── tests/                  # Unit and integration tests
│   └── ...
└── data/                   # Optional folder for ephemeris data
```

---

## Contributing

Contributions are welcome!
1. **Fork** the repo and create a new branch for your feature/fix.
2. **Open a Pull Request** with a clear description of changes.
3. We may request additional tests or documentation before merging.

For major changes, please open an issue first to discuss the proposed idea.

---

## License

This project is offered under the [MIT License](LICENSE). For the original paper’s text and figures, refer to its arXiv license terms.

---

*Enjoy simulating your own cosmic close encounters!*