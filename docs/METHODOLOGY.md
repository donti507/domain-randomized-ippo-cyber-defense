# Methodology

Companion to Section 3 of the paper; every item points to the code that implements it.

## 1. Problem formulation (`multi_agent_env.py`)
Two cooperating defender agents act at every step against a scripted attacker in a fixed-horizon (50 steps) MDP.

* **State** `s_t = [o_1, f_1, …, o_N, f_N]` : `o_i` = attacker owns node *i*, `f_i` = Detector has flagged node *i*. Observations are padded with zeros to `MAX_NODES = 10` (`fixed_size_env.py`).
* **Detector action** `a_d ∈ {0..N}`: flag node *i* (index N = no-op).
* **Responder action** `a_r ∈ {0..N}`: re-image node *i* (only effective on an attacker-owned, re-imagable node; the entry point is not re-imagable).
* **Reward** `r_t = 5·I_cf + 20·I_sr − c_atk(t) − 100·I_cj`
  * `I_cf` correctly flagged an attacker-owned node (+5); `I_sr` successful re-image (+20)
  * `c_atk`: −1 per successful recon, −10 per successful lateral exploit, −30 per full remote compromise chain
  * `I_cj`: crown jewel (node value ≥ 150) compromised → −100 and termination
* **Containment**: episode truncates at 50 steps without losing the crown jewel.

## 2. Procedural topologies (`topology.py`)
`generate_topology(n_nodes, seed, branching)` builds a random rooted tree: each new node attaches to a random existing node whose fan-out is below the branching factor. The deepest node (ties broken by name, then RNG) is the **crown jewel** (value 180); other nodes get values in [10, 140]. Each non-entry node exposes one remote vulnerability drawn from an 11-entry pool (success rate 0.4–0.8) and each parent a local `Discover_*` vulnerability enabling recon.

| name | nodes | branching | seed | split |
|---|---|---|---|---|
| topo_1 | 7 | 2 | 101 | seen |
| topo_2 | 7 | 3 | 202 | seen |
| topo_3 | 8 | 2 | 303 | seen |
| topo_4 | 9 | 2 | 404 | **unseen** |
| topo_5 | 10 | 3 | 505 | **unseen** |

`handcrafted.build_topology_a()` is a hand-authored 7-node network used only by the fixed-scenario baseline.

## 3. Attacker profiles (`profiles.py`, `multi_agent_env.py`)
| profile | target order | exploits / step | role |
|---|---|---|---|
| aggressive | highest value first | unlimited | seen |
| stealthy | lowest value first | 1 | seen |
| opportunistic | random | 2 | seen |
| cloud_pivot | highest value first | unlimited | **held out** (zero-day probe) |

`cloud_pivot` is the only profile permitted to use `CloudIAMPivot` / `DiscoverCloudMisconfig`; the latter leaks a direct edge from the entry point to the crown jewel, bypassing the hop structure the defenders learned to watch. A unit test (`tests/test_framework.py`) asserts these vulnerabilities are unreachable for seen profiles and that `cloud_pivot` / `topo_4–5` are never sampled in training.

## 4. Independent PPO (`role_env.py`, `training.py`)
Detector and Responder are separate Stable-Baselines3 PPO agents (`MlpPolicy`, `n_steps=256`, `batch_size=64`, `lr=3e-4`). Training alternates for R = 10 rounds × T = 5,000 timesteps: the Detector trains against the frozen current Responder, then the Responder against the freshly updated Detector (self-play style; no shared critic). Seeds: Detector `seed`, Responder `seed+1`.

## 5. Baseline vs. DR (`dr_controller.py`, `scripts/train.py`)
Equal compute budget. **Baseline**: topology A only, aggressive attacker. **DR**: every episode the `DomainRandomizationController` draws (topology ∈ topo_1–3, profile ∈ seen profiles, episode seed) from its own seeded RNG (`7 + seed`), independent of the attacker's in-episode RNG.

## 6. Evaluation (`evaluation.py`, `scripts/evaluate.py`)
Deterministic policies, 20 episodes (seeds 0–19) per condition; metrics: mean ± std episode reward, containment rate. Matrix: {seen, unseen topology} × {seen, unseen profile}. Multi-seed: 3 training seeds × all 5 topologies vs. the aggressive profile.
