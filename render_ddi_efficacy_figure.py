from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "biliary_clearance"
OUT.mkdir(parents=True, exist_ok=True)

states = ["Control", "MASL", "MASH"]
x = np.arange(len(states))
width = 0.18

# Direct outputs from the current zonated transporter stress tests.
bile_uptake = np.array([0.501, 0.502, 0.502])
bile_mrp2 = np.array([0.964, 0.939, 0.911])
parent_uptake = np.array([0.480, 0.480, 0.482])
parent_mrp2 = np.array([1.000, 1.000, 1.000])

fig, axes = plt.subplots(1, 3, figsize=(14, 4.7), gridspec_kw={"width_ratios": [1, 1, 1.15]}, constrained_layout=True)

for ax, uptake, mrp2, title, ylabel in [
    (axes[0], bile_uptake, bile_mrp2, "Bile-associated AUC", "ratio to baseline"),
    (axes[1], parent_uptake, parent_mrp2, "Local parent-pool AUC", "ratio to baseline"),
]:
    ax.bar(x - width / 2, uptake, width, color="#2C7FB8", label="50% uptake activity")
    ax.bar(x + width / 2, mrp2, width, color="#D95F0E", label="MRP2 activity = 0.35")
    ax.axhline(1.0, color="black", linewidth=1.0)
    ax.set_xticks(x, states)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.tick_params(axis="both", labelsize=10)
    ax.grid(axis="y", alpha=0.25)
    for i, v in enumerate(uptake):
        ax.text(i - width / 2, v + 0.035, f"{v:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for i, v in enumerate(mrp2):
        ax.text(i + width / 2, v + 0.035, f"{v:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
axes[0].legend(fontsize=9, prop={"weight": "bold"}, loc="lower left")

c = np.linspace(0, 2.2, 300)
effect = c / (0.45 + c)
toxicity = np.full_like(c, 0.78)
axes[2].plot(c, effect, color="#2C7FB8", linewidth=3, label="Illustrative efficacy")
axes[2].axhline(0.65, color="#2C7FB8", linestyle="--", linewidth=1.5, label="Effect target")
axes[2].axvline(1.35, color="#D95F0E", linestyle="--", linewidth=1.5, label="Safety exposure limit")
axes[2].fill_between(c, 0.65, toxicity, where=(c <= 1.35), color="#70AD47", alpha=0.20)
axes[2].text(0.48, 0.70, "candidate\nwindow", ha="center", va="center", fontsize=10, fontweight="bold", color="#548235")
axes[2].set_title("Efficacy-facing extension", fontsize=13, fontweight="bold")
axes[2].set_xlabel("active intracellular exposure (normalized)", fontsize=11, fontweight="bold")
axes[2].set_ylabel("effect / injury scale", fontsize=11, fontweight="bold")
axes[2].set_xlim(0, 2.2)
axes[2].set_ylim(0, 1.05)
axes[2].tick_params(axis="both", labelsize=10)
axes[2].grid(alpha=0.25)
axes[2].legend(fontsize=8.5, prop={"weight": "bold"}, loc="lower right")
axes[2].text(0.03, 0.97, "Illustrative future extension;\nnot validated in this study", transform=axes[2].transAxes,
             ha="left", va="top", fontsize=8.5, color="#666666")

fig.suptitle("Transporter perturbation separates DDI signals from efficacy decisions", fontsize=16, fontweight="bold")
fig.savefig(OUT / "figure_ddi_efficacy_use_case.png", dpi=240)
plt.close(fig)
print("Wrote", OUT / "figure_ddi_efficacy_use_case.png")
