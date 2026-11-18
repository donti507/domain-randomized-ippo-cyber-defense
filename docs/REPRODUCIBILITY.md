# Reproducibility

## Environment
* Python 3.10–3.12, CPU only. `numpy==1.26.4` and `gymnasium==0.29.1` are pinned by CyberBattleSim; Stable-Baselines3 2.3.2.
* CyberBattleSim is installed from GitHub (`requirements.txt`). For exact long-term reproducibility, pin it to a commit: `pip install git+https://github.com/microsoft/CyberBattleSim.git@<commit>` (the original experiments used the then-current `main`).
* Colab tip: after installing, restart the runtime so the pinned numpy is the one imported (the original notebook fought this numpy conflict at length).

## Seeds
| Component | Seed |
|---|---|
| Detector PPO | `s` ∈ {0,1,2} |
| Responder PPO | `s + 1` |
| DR controller | `7 + s` |
| Topology generator | fixed per variant (101, 202, 303, 404, 505) |
| Evaluation episodes | 0 … 19, deterministic policies |

## What maps to what in the paper
| Paper item | Command | Output |
|---|---|---|
| Table III / Fig. 5 | `train.py` (both methods, seeds 0 1 2) → `evaluate.py --mode multiseed` | `results/multiseed_results.json` |
| Table II / Figs. 3–4 | `train.py` → `evaluate.py --mode matrix --seed 0` | `results/matrix_seed0.csv` |
| Fig. 2 | `scripts/make_architecture_diagram.py` | `results/figures/architecture_diagram.png` |
| All figures from the *paper's* numbers | `scripts/make_figures.py results` | `results/figures/` |

## Honest provenance notes
1. **Table II was produced by an earlier, unseeded training run** in the development notebook (trainer called with no seed; DR controller seed 7). The seeded `train.py` pipeline was introduced for the 3-seed study (Table III). Re-running `--seed 0` therefore reproduces the qualitative result (DR contains everywhere on seen profiles; baseline mostly fails; both collapse on `cloud_pivot`) but individual cells may differ. The paper's exact Table II numbers are archived in `results/paper_table2_single_seed.csv`.
2. The Table II baseline numbers coincide with the seed-0 baseline of Table III on topo_1, but the DR column does not (e.g. 238 vs 258 on topo_1) — consistent with note 1.
3. Both defenders are evaluated deterministically on 20 episodes; this measures the trained policy pair, not statistical significance over many environment seeds.
4. `results/paper_*` are never overwritten by new runs.

## From the notebook to this repository
The research was done interactively in a Colab notebook (`notebooks/archive/cyberproject2_original_devlog.ipynb`, ≈420 cells), where modules were written with `%%writefile`, repeatedly appended to (`-a`) and patched by helper scripts. This repository contains the **final state** of those modules, reconstructed by replaying the notebook's file-writing and patch cells in order and then refactored into an importable package (`exec(open(...))` / `sys.modules` hacks replaced by imports). Logic was kept verbatim; changes were limited to imports, docstrings, removal of debug prints, and the CLI wrappers. Topologies B and C, early baseline/debug scripts and diagnostic cells from the notebook are not part of the final pipeline and live only in the archive.

| Notebook module | Repository module |
|---|---|
| `topology_generator.py` | `src/cyberdr/topology.py` |
| `topology_A.py` | `src/cyberdr/handcrafted.py` |
| `profiles.py` | `src/cyberdr/profiles.py` |
| `multi_agent_env.py` | `src/cyberdr/multi_agent_env.py` |
| `fixed_size_env.py` | `src/cyberdr/fixed_size_env.py` |
| `independent_ppo_env.py` | `src/cyberdr/role_env.py` |
| `dr_controller.py` | `src/cyberdr/dr_controller.py` |
| `independent_ppo_trainer.py` (+ `patch_trainer_seed.py`) | `src/cyberdr/training.py` |
| `evaluate_ippo.py` | `src/cyberdr/evaluation.py` |
| `train_multiseed.py`, `evaluate_multiseed.py`, `run_full_evaluation.py` | `scripts/train.py`, `scripts/evaluate.py` |
| `make_*chart.py`, `make_corrected_diagram.py` | `scripts/make_figures.py`, `scripts/make_architecture_diagram.py` |

## Verification status
When this repository was assembled (Python 3.11, CPU, numpy 1.26.4, gymnasium 0.29.1, SB3 2.3.2, torch 2.15, CyberBattleSim `main` @ `aebf185`), the following was actually executed from a clean checkout:

* `pytest -q` → 9 passed.
* `scripts/train.py` for baseline and DR, seeds 0–2 (≈ 2 min per seed for both methods on 2 CPU cores).
* `scripts/evaluate.py --mode multiseed` and `--mode matrix --seed 0`. Outputs are saved in `results/reproduction/`.

| | Paper (Table III) | Fresh re-run |
|---|---|---|
| Baseline, all 5 topologies (mean ± std) | −142.7±14.6, −134.7±9.4, −27.0±172.7, −152.0±12.8, −39.3±166.2 | **identical** |
| DR topo_1 / 2 / 3 / 4 / 5 | 264.7±9.4, 259.0±0.0, 261.3±9.4, 238.0±16.3, 259.0±0.0 | 258.0±16.3, 259.0±0.0, 241.3±9.4, 238.0±0.0, 259.0±0.0 |

* The **baseline reproduces exactly**. The **DR numbers differ by a few reward points on some topologies** (e.g. topo_3: 261.3 vs 241.3) but show the same behaviour: positive reward on every topology, std ≤ 16.3. The small differences are likely due to library-version / nondeterminism effects in PPO training and/or the DR run having been produced before a later notebook patch; this has not been traced to a single cause.
* In the seed-0 matrix, DR achieves **100 % containment on all 15 seen-profile conditions including topo_4/topo_5**, the baseline contains **0 %**, and both defenders score **−107.0 / 0 %** on every `cloud_pivot` condition, which matches the paper's conclusions. (The paper's Table II shows baseline 100 % on topo_2 because it came from a different, unseeded run; see note 1.)
