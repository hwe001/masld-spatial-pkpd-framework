"""Exploratory zonated biliary drug-clearance model.

This is a reproducible revival of the unpublished CFDA enzyme/transporter
model found in the Drive manuscript. It is deliberately dimensionless until
the original parameter table and experimental units are verified. The model
has three lobular zones (peri-central, mid-lobular, peri-portal) and tracks:

  plasma parent -> intracellular parent -> intracellular metabolite -> bile

The extension adds flow impairment, MRP2 inhibition, and a simple injury
feedback on biliary conductance. Outputs are scenario comparisons, not
patient-calibrated predictions.
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "biliary_clearance"
OUT.mkdir(parents=True, exist_ok=True)

ZONES = ("peri-central", "mid-lobular", "peri-portal")
T_END = 60.0
T = np.linspace(0.0, T_END, 1201)


def michaelis_menten(substrate, vmax, km):
    return vmax * substrate / (km + max(substrate, 1.0e-12))


def rhs(t, y, scenario):
    """ODE right-hand side for one scenario.

    State layout: plasma parent, then for each zone parent, metabolite,
    biliary metabolite, and injury burden.
    """
    parent_blood = max(y[0], 0.0)
    dydt = np.zeros_like(y)

    # A short IV-like exposure provides a reproducible transient stimulus.
    input_rate = 1.0 if t <= 2.0 else 0.0
    uptake = 0.45 * parent_blood
    dydt[0] = input_rate - uptake - 0.08 * parent_blood

    flow_factor = scenario["flow_factor"]
    mrp2_factor = scenario["mrp2_factor"]
    obstruction = scenario["obstruction"]

    # Zonal gradients reflect the earlier work: CYP and MRP2 are higher
    # peri-centrally, while protective GSH is lower there.
    cyp = np.array([1.45, 1.0, 0.65])
    mrp2 = mrp2_factor * np.array([1.35, 1.0, 0.70])
    gsh = np.array([0.65, 1.0, 1.30])
    zone_flow = flow_factor * np.array([0.65, 0.90, 1.15])

    for iz in range(3):
        base = 1 + 4 * iz
        p, m, b, injury = np.maximum(y[base:base + 4], 0.0)

        parent_uptake = (0.55 / 3.0) * parent_blood
        metabolism = michaelis_menten(p, 0.42 * cyp[iz], 0.45)
        biliary_export = michaelis_menten(m, 0.33 * mrp2[iz], 0.35)
        washout = 0.10 * zone_flow[iz] * b

        # Injury rises when metabolite exposure exceeds the local protective
        # capacity and slowly recovers. It feeds back on local bile conductance.
        toxic_load = max(0.0, m - 0.30 * gsh[iz])
        injury_gain = 0.035 * toxic_load
        recovery = 0.004 * injury
        effective_flow = max(0.05, zone_flow[iz] * (1.0 - obstruction * injury))
        washout = 0.10 * effective_flow * b

        dydt[base] = parent_uptake - metabolism - 0.03 * p
        dydt[base + 1] = metabolism - biliary_export - 0.025 * m
        dydt[base + 2] = biliary_export - washout
        dydt[base + 3] = injury_gain - recovery

        # A small amount of downstream metabolite transfer approximates
        # advection through the three connected biliary zones.
        if iz < 2:
            downstream = 0.06 * effective_flow * b
            dydt[base + 2] -= downstream
            dydt[base + 5] += downstream

    return dydt


def simulate(name, **kwargs):
    scenario = {
        "flow_factor": kwargs.get("flow_factor", 1.0),
        "mrp2_factor": kwargs.get("mrp2_factor", 1.0),
        "obstruction": kwargs.get("obstruction", 0.0),
    }
    y0 = np.zeros(13)
    sol = solve_ivp(lambda t, y: rhs(t, y, scenario), (0.0, T_END), y0,
                    t_eval=T, rtol=1.0e-7, atol=1.0e-9)
    if not sol.success:
        raise RuntimeError(sol.message)
    return {"name": name, "scenario": scenario, "t": sol.t, "y": sol.y}


SCENARIOS = [
    simulate("baseline"),
    simulate("MRP2 inhibition", mrp2_factor=0.35),
    simulate("50% flow reduction", flow_factor=0.50),
    simulate("combined stress", flow_factor=0.50, mrp2_factor=0.35,
             obstruction=0.75),
]


def write_summary(results):
    rows = ["scenario,biliary_metabolite_auc,peak_total_injury,final_total_injury"]
    for result in results:
        y = result["y"]
        bile = y[[3, 7, 11], :].sum(axis=0)
        injury = y[[4, 8, 12], :].sum(axis=0)
        exposure = np.trapezoid(bile, result["t"])
        rows.append(f"{result['name']},{exposure:.8g},{injury.max():.8g},{injury[-1]:.8g}")
    (OUT / "scenario_summary.csv").write_text("\n".join(rows) + "\n", encoding="ascii")


def make_figure(results):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    for result, color in zip(results, colors):
        t, y = result["t"], result["y"]
        bile = y[[3, 7, 11], :].sum(axis=0)
        injury = y[[4, 8, 12], :].sum(axis=0)
        axes[0, 0].plot(t, y[0], color=color, label=result["name"])
        axes[0, 1].plot(t, bile, color=color, label=result["name"])
        axes[1, 0].plot(t, injury, color=color, label=result["name"])
        axes[1, 1].bar(
            np.arange(3) + (len(axes[1, 1].containers) * 0.18),
            y[[4, 8, 12], :].max(axis=1), width=0.17, color=color,
            label=result["name"])

    axes[0, 0].set_title("Plasma parent exposure")
    axes[0, 1].set_title("Total biliary metabolite")
    axes[1, 0].set_title("Total injury burden")
    axes[1, 1].set_title("Peak injury by zone")
    axes[1, 1].set_xticks(np.arange(3) + 0.27)
    axes[1, 1].set_xticklabels(ZONES, rotation=20, ha="right")
    for ax in axes.flat:
        ax.set_xlabel("time (model units)")
        ax.grid(alpha=0.25)
    axes[0, 0].set_ylabel("normalised concentration")
    axes[0, 1].set_ylabel("normalised concentration")
    axes[1, 0].set_ylabel("normalised injury")
    axes[1, 1].set_ylabel("normalised injury")
    axes[1, 1].set_xlabel("lobular zone")
    axes[1, 1].legend(fontsize=8)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Exploratory zonated biliary clearance and cholestatic injury")
    fig.savefig(OUT / "figure_biliary_clearance_scenarios.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    write_summary(SCENARIOS)
    make_figure(SCENARIOS)
    print("Wrote", OUT / "figure_biliary_clearance_scenarios.png")
    print("Wrote", OUT / "scenario_summary.csv")
