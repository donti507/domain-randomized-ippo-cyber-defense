"""Evaluate trained defenders.

  --mode matrix     full seen/unseen topology x profile matrix for one seed  (paper Table II style)
  --mode multiseed  all topologies vs aggressive profile, mean+/-std over seeds (paper Table III)
Writes CSV/JSON into --results-dir.
"""
import argparse, csv, json
import numpy as np
from cyberdr import (PROFILES, TOPOLOGY_VARIANTS, SEEN_PROFILES, UNSEEN_PROFILE, SEEN_TOPOLOGIES,
                     UNSEEN_TOPOLOGIES, FixedSizeDefenderEnv, generate_topology)
from cyberdr.evaluation import evaluate_pair, load_pair


def builder(topo, profile):
    params, prof = TOPOLOGY_VARIANTS[topo], PROFILES[profile]
    return lambda: FixedSizeDefenderEnv(generate_topology(**params), prof, max_steps=50)


def matrix(a):
    base = load_pair(f"{a.ckpt}/baseline_seed{a.seed}", "ippo_baseline")
    dr = load_pair(f"{a.ckpt}/dr_seed{a.seed}", "ippo_dr")
    rows = []
    for tset, tl in ((SEEN_TOPOLOGIES, "seen"), (UNSEEN_TOPOLOGIES, "unseen")):
        for prof in SEEN_PROFILES + [UNSEEN_PROFILE]:
            for t in tset:
                b = evaluate_pair(*base, builder(t, prof), n_episodes=a.episodes)
                d = evaluate_pair(*dr, builder(t, prof), n_episodes=a.episodes)
                rows.append(dict(topology=t, topology_split=tl, profile=prof,
                                 profile_split="unseen" if prof == UNSEEN_PROFILE else "seen",
                                 baseline_reward=b["mean_reward"], baseline_containment=b["containment_rate"],
                                 dr_reward=d["mean_reward"], dr_containment=d["containment_rate"]))
                print(rows[-1])
    with open(f"{a.results_dir}/matrix_seed{a.seed}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)


def multiseed(a):
    res = {}
    for t in TOPOLOGY_VARIANTS:
        res[t] = {"baseline": [], "dr": []}
        for s in a.seeds:
            for m in ("baseline", "dr"):
                pair = load_pair(f"{a.ckpt}/{m}_seed{s}", f"ippo_{m}")
                res[t][m].append(evaluate_pair(*pair, builder(t, "aggressive"), n_episodes=a.episodes)["mean_reward"])
    summ = {t: {"baseline_mean": float(np.mean(v["baseline"])), "baseline_std": float(np.std(v["baseline"])),
                "dr_mean": float(np.mean(v["dr"])), "dr_std": float(np.std(v["dr"]))} for t, v in res.items()}
    for t, v in summ.items():
        print(f"{t}: baseline {v['baseline_mean']:.1f}+/-{v['baseline_std']:.1f}  dr {v['dr_mean']:.1f}+/-{v['dr_std']:.1f}")
    json.dump({"raw": res, "summary": summ}, open(f"{a.results_dir}/multiseed_results.json", "w"), indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["matrix", "multiseed"], required=True)
    ap.add_argument("--ckpt", default="checkpoints")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--episodes", type=int, default=20)
    ap.add_argument("--results-dir", default="results")
    a = ap.parse_args()
    {"matrix": matrix, "multiseed": multiseed}[a.mode](a)
