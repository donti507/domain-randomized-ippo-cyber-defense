"""Regenerate Fig. 3 (per-condition reward), Fig. 4 (containment) and Fig. 5 (multi-seed) from results/."""
import csv, json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = sys.argv[1] if len(sys.argv) > 1 else "results"
BLUE, RED = "#4f81bd", "#c0504d"

rows = list(csv.DictReader(open(f"{RES}/paper_table2_single_seed.csv")))
seen = [r for r in rows if r["profile_split"] == "seen"]
x = range(len(seen)); w = 0.38
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar([i - w/2 for i in x], [float(r["baseline_reward"]) for r in seen], w, label="Baseline (no DR)", color=RED)
ax.bar([i + w/2 for i in x], [float(r["dr_reward"]) for r in seen], w, label="Domain Randomization", color=BLUE)
ax.axhline(0, color="black", lw=0.8); ax.set_xticks(list(x))
ax.set_xticklabels([f"{r['topology']}{'*' if r['topology_split']=='unseen' else ''}\n{r['profile']}" for r in seen], fontsize=8)
ax.set_ylabel("Mean Episode Reward"); ax.set_title("Baseline vs. DR Independent PPO (* = topology unseen in DR training)")
ax.legend(); plt.tight_layout(); plt.savefig(f"{RES}/figures/results_bar_chart.png", dpi=200); plt.close()

def rate(rs, k): return 100 * sum(float(r[k]) for r in rs) / len(rs)
uns = [r for r in rows if r["profile_split"] == "unseen"]
fig, ax = plt.subplots(figsize=(8, 6))
for off, k, c, l in ((-0.2, "baseline_containment", RED, "Baseline (no DR)"), (0.2, "dr_containment", BLUE, "Domain randomization")):
    ax.bar([0 + off, 1 + off], [rate(seen, k), rate(uns, k)], 0.4, color=c, label=l)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Seen profiles", "Unseen profile (cloud_pivot)"])
ax.set_ylabel("Containment rate (%)"); ax.set_ylim(0, 110); ax.legend()
ax.set_title("Containment rate: seen vs. unseen attacker profile"); plt.tight_layout()
plt.savefig(f"{RES}/figures/containment_rate_chart.png", dpi=200); plt.close()

d = json.load(open(f"{RES}/paper_multiseed_results.json"))["summary"]; ks = list(d)
fig, ax = plt.subplots(figsize=(10, 6)); x = range(len(ks)); w = 0.35
ax.bar([i - w/2 for i in x], [d[k]["baseline_mean"] for k in ks], w, yerr=[d[k]["baseline_std"] for k in ks], capsize=5, label="Baseline (no DR)", color=RED)
ax.bar([i + w/2 for i in x], [d[k]["dr_mean"] for k in ks], w, yerr=[d[k]["dr_std"] for k in ks], capsize=5, label="Domain Randomization", color=BLUE)
ax.axhline(0, color="black", lw=0.8); ax.set_xticks(list(x)); ax.set_xticklabels([k.replace("_aggressive", "") for k in ks])
ax.set_ylabel("Mean Episode Reward (+/- std across seeds)"); ax.set_xlabel("Topology (topo_4, topo_5 unseen during DR training)")
ax.set_title("Baseline vs. DR across independent training seeds"); ax.legend(); plt.tight_layout()
plt.savefig(f"{RES}/figures/multiseed_chart.png", dpi=200)
print("figures written to", RES + "/figures")
