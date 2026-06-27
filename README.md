# PrimordialEncounters

*If dark matter is made of primordial black holes, could we catch one crossing the Solar System?*

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Built with REBOUND](https://img.shields.io/badge/N--body-REBOUND-orange.svg)

A simulation and analysis framework for **detecting asteroid-mass primordial black hole (PBH) flybys** through the tiny perturbations they leave in Solar System orbits. It implements and builds on the method of **Tran, Geller, Lehmann & Kaiser, *Phys. Rev. D* 110, 063533 (2024)** ([arXiv:2312.17217](https://arxiv.org/abs/2312.17217)).

---

## Why this is interesting

Asteroid-mass PBHs (roughly 10^17 to 10^23 g) are one of the last surviving dark-matter candidates. If they make up much of the dark matter, about one should cross the inner Solar System per decade. And because we track planetary distances to extraordinary precision (Earth-to-Mars to about 0.1 m, via Mars orbiters and landers), such a passage could leave a **measurable fingerprint** in the planets' motion.

This project simulates those flybys, measures the resulting orbital residuals, and asks how detectable they really are.

### How it works

1. **Sample** a PBH encounter (mass, impact parameter, velocity, time) from physically motivated distributions.
2. **Simulate** the flyby with an N-body integrator ([REBOUND](https://github.com/hannorein/rebound)) plus a fast analytic impulse approximation, against an unperturbed baseline Solar System.
3. **Measure** the per-planet position residuals and reduce them to a single detection statistic.
4. **Repeat** over Monte Carlo ensembles to estimate detection *rates* as a function of PBH mass.

### The detection statistic

The figure of merit (Tran et al., Eq. 17), in `src/residual_analysis.py`:

```
q_fom = max_t  sqrt( sum_i ( delta_r_i(t) / sigma_i )^2 )
```

It is the peak over time of the quadrature-combined signal-to-noise across the inner planets (Mercury, Venus, Mars), each taken as an Earth-to-planet distance residual measured against that planet's ranging precision (`sigma_i` of about 0.1 m).

### The open question (and why this project is worth doing)

A favorable single close encounter, a heavy PBH (around 10^21 to 10^22 g) passing within roughly 1 to 2 AU, produces a raw residual of about 1 to 2 m, comfortably above the 0.1 m ranging floor. But that is the *raw* perturbed-minus-baseline signal. A real ephemeris analysis **fits** the planets' initial conditions and masses to the data, and that fit quietly absorbs much of a slow impulse, so the genuinely **detectable** signal is smaller by an amount nobody has yet quantified. Tran et al. compute the raw signal as a deliberate "proof of principle"; the independent study of [Thoss & Burkert (2025)](https://arxiv.org/abs/2409.04518) finds the *typical* (diffuse-halo) signal sits below current precision.

> **The central open problem: how much of the close-encounter signal survives a realistic ephemeris fit?** Neither the original paper nor any other public code answers this, which is exactly the gap this project is built to close.

---

## What's here

| Component | Role | |
|---|---|:--:|
| `parameter_sampler.py` | Monte Carlo PBH encounter parameters | done |
| `n_body_simulation.py` | REBOUND N-body engine (`NBodySimulation`) | done |
| `analytic_impulse.py` | Impulse approximation, dv = 2GM/(b*v) | done |
| `residual_analysis.py` | Residuals, stats, **`q_fom`** (Eq. 17) | done |
| `ensemble_runner.py` | Parallel Monte Carlo ensembles, detection rates | hardening |
| `synthetic_data.py` | Synthetic noisy observations | done |
| `visualization.py` | Trajectory, residual, and detection-rate plots | done |
| Parameter recovery | Infer PBH mass and trajectory; likelihood-ratio test vs. null | planned |
| Spectral analysis | Confirm the near-monochromatic residual signature | planned |

```
PrimordialEncounters/
├── src/
│   ├── parameter_sampler.py     # PBH encounter sampling
│   ├── n_body_simulation.py     # REBOUND wrapper / integration engine
│   ├── analytic_impulse.py      # analytic velocity-kick approximation
│   ├── simulation_runner.py     # paired baseline + perturbed runs
│   ├── residual_analysis.py     # residuals, stats, q_fom
│   ├── ensemble_runner.py       # Monte Carlo ensembles, detection rates
│   ├── synthetic_data.py        # synthetic observations
│   └── visualization.py         # plotting
├── tests/                       # pytest suite (q_fom fully covered)
├── docs/                        # design notes and pseudocode
└── requirements.txt
```

---

## Getting started

```bash
git clone https://github.com/ImmortalDemonGod/PrimordialEncounters.git
cd PrimordialEncounters
pip install -r requirements.txt        # rebound, numpy, scipy, matplotlib
```

Each module has a runnable demo, and the test suite covers the detection statistic:

```bash
python src/parameter_sampler.py        # sample and print PBH encounter parameters
python src/residual_analysis.py        # residual statistics on example data
python -m pytest tests/                # run the tests
```

> Heads-up: this is **early-stage research code**. The detection statistic and core modules are solid and tested; the full single-flyby and ensemble pipelines are still being hardened (see the roadmap) and are not yet meant for production runs.

---

## Roadmap

**Near term, to make a single flyby correct end-to-end:**
- Geometric PBH placement from the encounter parameters (impact parameter and approach direction).
- Physical-units and interface calibration between the sampler and the simulation runner.
- Validate the impulse approximation against the full N-body force.

**Then, to close the science loop:**
- Parameter recovery: MCMC mass and trajectory inference (`emcee` / `dynesty`) plus a likelihood-ratio test against a no-PBH null.
- Spectral analysis of the residual time series.
- **The realistic detectability layer:** quantify how much signal survives a full ephemeris orbit-fit. This is the open frontier described above, and the highest-value piece of work in the project.

A useful external benchmark for validation is the independent N-body study of [Thoss & Burkert (2025)](https://arxiv.org/abs/2409.04518).

---

## Get involved

This is an active project and contributions are very welcome, especially from people with an astrophysics, orbital-dynamics, or Bayesian-inference background. Good places to jump in:

- **Dynamics and numerics:** the near-term simulation-correctness items (PBH placement geometry, integrator choice for close encounters, impulse validation).
- **Statistics and inference:** the parameter-recovery and detection-significance pipeline.
- **The headline problem:** reproduce the Tran and Thoss & Burkert Earth-to-Mars result and model what survives a realistic ephemeris fit. No public code does this yet, so it is a genuine, citable contribution.

Open an issue to discuss anything substantial; small fixes and added tests can go straight to a pull request.

---

## References

- **Tran, Geller, Lehmann & Kaiser (2024).** *Close encounters of the primordial kind: a new observable for primordial black holes as dark matter.* Phys. Rev. D 110, 063533. [arXiv:2312.17217](https://arxiv.org/abs/2312.17217). The method implemented here.
- **Thoss & Burkert (2025).** *Primordial Black Holes in the Solar System.* ApJ 980, 238. [arXiv:2409.04518](https://arxiv.org/abs/2409.04518). Independent simulations; a natural validation benchmark.
- **Rein & Liu (2012).** *REBOUND: an open-source multi-purpose N-body code.* [arXiv:1110.4876](https://arxiv.org/abs/1110.4876). For close encounters the IAS15 or MERCURIUS integrators are most appropriate.
- **Carr et al. (2021).** *Constraints on Primordial Black Holes.* [arXiv:2002.12778](https://arxiv.org/abs/2002.12778). The viable asteroid-mass window.

## License

Released under the [MIT License](LICENSE).
