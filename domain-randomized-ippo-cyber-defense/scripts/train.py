"""Train baseline (fixed topology A, aggressive attacker) or DR Independent-PPO defenders.

    python scripts/train.py --method dr --seeds 0 1 2
    python scripts/train.py --method baseline --seeds 0 1 2

Checkpoints go to <out>/<method>_seed<k>/ . DR controller seed is 7 + k (as in the paper runs).
"""
import argparse
from cyberdr import (PROFILES, TOPOLOGY_VARIANTS, SEEN_PROFILES, SEEN_TOPOLOGIES, FixedSizeDefenderEnv,
                     DomainRandomizationController, build_topology_a, generate_topology)
from cyberdr.training import train_independent_ppo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=["baseline", "dr"], required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--out", default="checkpoints")
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--timesteps-per-round", type=int, default=5000)
    a = ap.parse_args()

    for s in a.seeds:
        if a.method == "baseline":
            topo_a = build_topology_a()
            factory = lambda: FixedSizeDefenderEnv(topo_a, PROFILES["aggressive"], max_steps=50)
        else:
            dr = DomainRandomizationController(
                topology_variants=TOPOLOGY_VARIANTS, profiles=PROFILES,
                training_profile_names=SEEN_PROFILES, training_topology_names=SEEN_TOPOLOGIES, seed=7 + s)

            def factory(dr=dr):
                cfg = dr.sample_episode_config()
                return dr.make_env(cfg, generate_topology, FixedSizeDefenderEnv, max_steps=50)

        print(f"=== {a.method} seed {s} ===")
        train_independent_ppo(factory, f"{a.out}/{a.method}_seed{s}", f"ippo_{a.method}",
                              n_rounds=a.rounds, timesteps_per_round=a.timesteps_per_round, seed=s)


if __name__ == "__main__":
    main()
