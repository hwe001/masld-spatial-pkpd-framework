"""Counterfactual test of spatial zonation versus a well-mixed liver.

Both models use the same total input and the same mean transporter capacities.
Only the spatial distribution is changed. This is the central novelty test for
the second paper: does zonation alter pharmacology-facing predictions?
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from couple_michael_bileflow import INPUTS, OUT, simulate


def metrics(result):
    t = result["t"]
    y = result["y"]
    parent = y[0:10].sum(axis=0)
    bile = y[20:30].sum(axis=0)
    injury = y[30:40].sum(axis=0)
    return {
        "plasma_parent_auc": float(np.trapezoid(parent, t)),
        "hepatocyte_parent_auc": float(np.trapezoid(y[10:20].sum(axis=0), t)),
        "bile_auc": float(np.trapezoid(bile, t)),
        "peak_injury": float(injury.max()),
    }


def main():
    rows = []
    plot = []
    cases = (("normal control", "control"), ("steatosis", "MASL"),
             ("MASH", "MASH"))
    for tissue, state in cases:
        table = INPUTS["steatosis"] if tissue == "MASH" else INPUTS[tissue]
        for mode in ("zonated", "well_mixed"):
            for condition, uptake_inhibition, mrp2 in (
                ("baseline", 1.0, 1.0),
                ("50% uptake inhibition", 0.5, 1.0),
                ("65% MRP2 inhibition", 1.0, 0.35),
            ):
                label = f"{tissue}|{mode}|{condition}"
                result = simulate(label, table, atlas_state=state,
                                  spatial_mode=mode,
                                  uptake_inhibition=uptake_inhibition,
                                  mrp2=mrp2)
                m = metrics(result)
                rows.append({"tissue": tissue, "atlas_state": state,
                             "mode": mode, "condition": condition, **m})
                if tissue == "steatosis" and condition in ("baseline", "50% uptake inhibition"):
                    plot.append((result, mode, condition))

    keys = list(rows[0])
    lines = [",".join(keys)]
    for row in rows:
        lines.append(",".join(str(row[k]) for k in keys))
    (OUT / "zonated_vs_wellmixed_metrics.csv").write_text(
        "\n".join(lines) + "\n", encoding="ascii")

    def row_for(tissue, mode, condition):
        return next(r for r in rows if r["tissue"] == tissue and r["mode"] == mode
                    and r["condition"] == condition)

    labels = ["MASL baseline", "MASH baseline", "MASH MRP2 inhibition"]
    lookups = [("steatosis", "baseline"), ("MASH", "baseline"),
               ("MASH", "65% MRP2 inhibition")]
    bile_diff = []
    hep_diff = []
    for tissue, condition in lookups:
        z = row_for(tissue, "zonated", condition)
        w = row_for(tissue, "well_mixed", condition)
        bile_diff.append(100.0 * (z["bile_auc"] - w["bile_auc"]) / w["bile_auc"])
        hep_diff.append(100.0 * (z["hepatocyte_parent_auc"] - w["hepatocyte_parent_auc"]) / w["hepatocyte_parent_auc"])

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), constrained_layout=True)
    x = np.arange(len(labels))
    width = 0.36
    axes[0].bar(x - width / 2, bile_diff, width, color="#1f77b4", label="bile AUC")
    axes[0].bar(x + width / 2, hep_diff, width, color="#d62728", label="hepatocyte AUC")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_xticks(x, labels, rotation=25, ha="right")
    axes[0].set_ylabel("zonated minus well-mixed (%)", fontsize=12, fontweight="bold")
    axes[0].set_title("Prediction difference", fontsize=14, fontweight="bold")
    axes[0].tick_params(axis="both", labelsize=11)
    axes[0].legend(fontsize=10, prop={"weight": "bold"})
    for i, value in enumerate(bile_diff):
        axes[0].text(i - width / 2, value + (0.7 if value >= 0 else -1.5), f"{value:.1f}%", ha="center", fontsize=11, fontweight="bold")
    for i, value in enumerate(hep_diff):
        axes[0].text(i + width / 2, value + (0.7 if value >= 0 else -1.5), f"{value:.1f}%", ha="center", fontsize=11, fontweight="bold")

    colors = {"zonated": "#1f77b4", "well_mixed": "#7f7f7f"}
    styles = {"baseline": "-", "50% uptake inhibition": "--"}
    for result, mode, condition in plot:
        t = result["t"]
        axes[1].plot(t, result["y"][10:20].sum(axis=0), color=colors[mode],
                     linestyle=styles[condition], label=f"{mode}: {condition}")
        axes[2].plot(t, result["y"][30:40].sum(axis=0), color=colors[mode],
                     linestyle=styles[condition])
    axes[1].set_title("MASL hepatocyte exposure", fontsize=14, fontweight="bold")
    axes[2].set_title("MASL injury signal", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("normalized amount", fontsize=12, fontweight="bold")
    axes[2].set_ylabel("normalized injury", fontsize=12, fontweight="bold")
    for ax in axes[1:]:
        ax.set_xlabel("time (model units)", fontsize=12, fontweight="bold")
        ax.tick_params(axis="both", labelsize=11)
        ax.grid(alpha=0.25)
    axes[1].legend(fontsize=10, prop={"weight": "bold"})
    fig.suptitle("Spatial zonation changes pharmacology-facing predictions", fontsize=16, fontweight="bold")
    fig.savefig(OUT / "figure_zonated_vs_wellmixed.png", dpi=240)
    plt.close(fig)
    print("Wrote", OUT / "figure_zonated_vs_wellmixed.png")
    print("Wrote", OUT / "zonated_vs_wellmixed_metrics.csv")


if __name__ == "__main__":
    main()
