"""Pharmacometric endpoint and sensitivity analysis for the coupled model.

The analysis uses Michael Kuecken's normal-control and steatosis parameter
profiles and reports PK/PD-style quantities: bile-metabolite Cmax, AUC,
time-to-Cmax, and peak/terminal injury. Parameter ranges are deliberately
dimensionless until compound-specific calibration data are supplied.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from couple_michael_bileflow import INPUTS, OUT, simulate, ATLAS_ZONE_LABELS
from zonated_transport_genes import expanded_fields


RNG = np.random.default_rng(20260927)


def metrics(result):
    t = result["t"]
    bile = result["y"][20:30].sum(axis=0)
    injury = result["y"][30:40].sum(axis=0)
    imax = int(np.argmax(bile))
    return {
        "bile_cmax": float(bile[imax]),
        "bile_auc": float(np.trapezoid(bile, t)),
        "time_to_cmax": float(t[imax]),
        "peak_injury": float(injury.max()),
        "terminal_injury": float(injury[-1]),
    }


def run_scenarios():
    rows = []
    atlas_states = {"normal control": "control", "steatosis": "MASL"}
    for tissue, table in INPUTS.items():
        atlas_state = atlas_states[tissue]
        for mrp2 in (1.0, 0.35):
            for obstruction in (0.0, 0.5):
                label = f"{tissue}|atlas={atlas_state}|MRP2={mrp2:g}|obstruction={obstruction:g}"
                row = {"scenario": label, "tissue": tissue,
                       "atlas_state": atlas_state,
                       "mrp2_factor": mrp2, "obstruction": obstruction}
                row.update(metrics(simulate(label, table, mrp2=mrp2,
                                            obstruction=obstruction,
                                            atlas_state=atlas_state)))
                rows.append(row)
    # MASH is included as a published human disease state even though the
    # older Michael input table contains only normal and steatosis profiles.
    table = INPUTS["steatosis"]
    for obstruction in (0.0, 0.5):
        label = f"MASH|atlas=MASH|MRP2=1|obstruction={obstruction:g}"
        row = {"scenario": label, "tissue": "MASH", "atlas_state": "MASH",
               "mrp2_factor": 1.0, "obstruction": obstruction}
        row.update(metrics(simulate(label, table, obstruction=obstruction,
                                    atlas_state="MASH")))
        rows.append(row)
    return rows


def run_lhs(n=160):
    rows = []
    atlas_states = {"normal control": "control", "steatosis": "MASL"}
    for tissue, table in INPUTS.items():
        atlas_state = atlas_states[tissue]
        for i in range(n):
            mrp2 = RNG.uniform(0.20, 1.20)
            obstruction = RNG.uniform(0.0, 0.75)
            result = simulate(f"{tissue}|atlas={atlas_state}|sample={i}", table,
                              mrp2=mrp2, obstruction=obstruction,
                              atlas_state=atlas_state)
            row = {"sample": i, "tissue": tissue, "mrp2_factor": mrp2,
                   "atlas_state": atlas_state,
                   "obstruction": obstruction}
            row.update(metrics(result))
            rows.append(row)
    return rows


def write_csv(rows, filename):
    keys = list(rows[0])
    lines = [",".join(keys)]
    for row in rows:
        lines.append(",".join(str(row[k]) for k in keys))
    (OUT / filename).write_text("\n".join(lines) + "\n", encoding="ascii")


def write_gene_fields():
    rows = []
    for state in ("control", "MASL", "MASH"):
        fields = expanded_fields(state, ATLAS_ZONE_LABELS)
        for position, zone in enumerate(ATLAS_ZONE_LABELS):
            row = {"atlas_state": state, "position": position,
                   "zone": zone}
            row.update({gene: values[position] for gene, values in fields.items()})
            rows.append(row)
    write_csv(rows, "nature_genetics_zonated_gene_fields.csv")


def make_figure(rows):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    for tissue, color in (("normal control", "#1f77b4"), ("steatosis", "#d62728")):
        subset = [r for r in rows if r["tissue"] == tissue]
        x = np.array([r["obstruction"] for r in subset])
        y = np.array([r["bile_auc"] for r in subset])
        z = np.array([r["peak_injury"] for r in subset])
        axes[0].scatter(x, y, s=12, alpha=0.45, color=color, label=tissue)
        axes[1].scatter(x, z, s=12, alpha=0.45, color=color, label=tissue)
        axes[2].scatter(np.array([r["mrp2_factor"] for r in subset]), z,
                        s=12, alpha=0.45, color=color, label=tissue)
    for ax, title in zip(axes, ("Biliary exposure AUC", "Peak injury vs obstruction", "Peak injury vs MRP2 activity")):
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.tick_params(axis="both", labelsize=11)
    axes[0].set_xlabel("obstruction fraction", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("obstruction fraction", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("MRP2 activity factor", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("normalised concentration-time", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("normalised injury", fontsize=12, fontweight="bold")
    axes[2].set_ylabel("normalised injury", fontsize=12, fontweight="bold")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=10, prop={"weight": "bold"})
    fig.suptitle("PK/PD-style uncertainty analysis of zonated hepatobiliary transport", fontsize=16, fontweight="bold")
    fig.savefig(OUT / "figure_jpkpd_sensitivity.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    scenarios = run_scenarios()
    lhs = run_lhs()
    write_csv(scenarios, "jpkpd_scenario_metrics.csv")
    write_csv(lhs, "jpkpd_lhs_samples.csv")
    write_gene_fields()
    make_figure(lhs)
    print("Wrote", OUT / "jpkpd_scenario_metrics.csv")
    print("Wrote", OUT / "jpkpd_lhs_samples.csv")
    print("Wrote", OUT / "figure_jpkpd_sensitivity.png")
