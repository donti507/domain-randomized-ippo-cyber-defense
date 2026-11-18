import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

def box(x, y, w, h, text, color="#dbe9f6", fontsize=8):
    ax.add_patch(plt.Rectangle((x, y), w, h, edgecolor="black", facecolor=color, linewidth=1.2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize)

def group(x, y, w, h, title):
    ax.add_patch(plt.Rectangle((x, y), w, h, edgecolor="gray", facecolor="none",
                                linewidth=1.0, linestyle="--"))
    ax.text(x + 0.1, y + h - 0.15, title, fontsize=8, style="italic", color="dimgray")

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1))

# --- Left column: inputs ---
group(0.2, 6.8, 3.2, 2.0, "Attacker Profiles")
box(0.4, 7.8, 2.8, 0.7, "Aggressive / Stealthy / Opportunistic\n(seen, used in training)")
box(0.4, 6.9, 2.8, 0.7, "Cloud Pivot\n(held out - true zero-day)")

group(0.2, 4.3, 3.2, 2.2, "Topology Variants (procedural)")
box(0.4, 5.4, 2.8, 0.9, "topo_1, topo_2, topo_3\n(seen - DR training pool)")
box(0.4, 4.4, 2.8, 0.9, "topo_4, topo_5\n(unseen - held out)")

# --- Center: DR controller + training env ---
box(3.9, 5.2, 2.2, 1.2, "Domain Randomization\nController\n(samples topology + profile\n+ seed each episode)")
box(6.6, 5.2, 2.6, 1.2, "CyberBattleSim Env\n(FixedSizeDefenderEnv,\npadded to max_nodes=10)")
box(6.6, 3.4, 2.6, 1.0, "Scripted Attacker\n(profile-driven,\ndiscovery-chain based)")

group(9.6, 4.9, 3.2, 1.9, "Defender: Independent PPO")
box(9.8, 5.7, 2.8, 0.9, "Detector Policy\n(own network, own reward)")
box(9.8, 5.0, 2.8, 0.6, "Responder Policy\n(own network, own reward)")

box(3.9, 1.2, 5.3, 1.4, "Alternating self-play training:\nfreeze one policy, train the other,\nswap, repeat (10 rounds x 5000 steps)")

box(9.6, 1.2, 3.2, 1.4, "Evaluation:\nseen vs. unseen topology x\nseen vs. unseen profile\n(mean reward, containment rate)")

# arrows
arrow(3.4, 7.9, 3.9, 6.0)
arrow(3.4, 5.2, 3.9, 5.8)
arrow(6.1, 5.8, 6.6, 5.8)
arrow(7.9, 5.2, 7.9, 4.4)
arrow(9.2, 5.8, 9.6, 5.8)
arrow(6.6, 1.9, 6.6, 2.6)
arrow(6.6, 2.6, 9.6, 2.6)
arrow(11.2, 4.9, 11.2, 2.6)

plt.title("Domain-Randomized Independent PPO Defender for Zero-Day Generalization", fontsize=11)
plt.tight_layout()
plt.savefig("results/figures/architecture_diagram.png", dpi=200, bbox_inches="tight")
print("Saved corrected_architecture_diagram.png")
