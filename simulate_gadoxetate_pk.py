"""First-pass human gadoxetate PK model for the manuscript.

Amounts are in mmol for a 70 kg adult. The model is deliberately small:
plasma -> hepatocyte -> bile, with parallel renal clearance and reversible
sinusoidal return. Regulatory values anchor dose, clearance, and the normal
roughly 50:50 renal/hepatobiliary split. This is a calibration scaffold, not a
validated patient-specific model.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "biliary_clearance"
OUT.mkdir(parents=True, exist_ok=True)

BODY_MASS = 70.0
DOSE = 0.025 * BODY_MASS  # mmol/kg * kg
VP = 0.21 * BODY_MASS  # L, label Vdss approximation
CL_TOTAL = 0.250 * 60.0  # L/h
CL_RENAL = 0.120 * 60.0  # L/h
CL_HEPATIC = CL_TOTAL - CL_RENAL
T = np.linspace(0.0, 24.0, 2401)

SCENARIOS = {
    # Bile rates are tuned so the 24 h healthy recovery is close to the
    # regulatory approximately 50:50 renal/hepatobiliary split.
    "healthy": {"uptake": 1.10, "back": 0.12, "bile": 0.112, "renal": 1.00},
    "MASL/MASH exploratory": {"uptake": 0.88, "back": 0.16, "bile": 0.090, "renal": 1.00},
    "severe hepatic impairment": {"uptake": 0.35, "back": 0.24, "bile": 0.025, "renal": 1.30},
}


def simulate(label, pars):
    # Rates are scaled so the healthy profile is consistent with rapid plasma
    # clearance and approximately equal renal/hepatobiliary elimination.
    renal = (CL_RENAL / VP) * pars["renal"]
    uptake = pars["uptake"]
    back = pars["back"]
    bile = pars["bile"]
    y0 = np.array([DOSE, 0.0, 0.0])

    def rhs(t, y):
        plasma, hepatocyte, bile_amount = np.maximum(y, 0.0)
        return [
            -renal * plasma - uptake * plasma + back * hepatocyte,
            uptake * plasma - (back + bile) * hepatocyte,
            bile * hepatocyte,
        ]

    sol = solve_ivp(rhs, (T[0], T[-1]), y0, t_eval=T, rtol=1e-8, atol=1e-10)
    if not sol.success:
        raise RuntimeError(sol.message)
    return {"label": label, "t": sol.t, "y": sol.y}


def metrics(result):
    t = result["t"]
    plasma, hepatocyte, bile = result["y"]
    return {
        "scenario": result["label"],
        "dose_mmol": DOSE,
        "plasma_cmax_mmol": float(plasma.max()),
        "hepatocyte_cmax_mmol": float(hepatocyte.max()),
        "bile_amount_24h_mmol": float(bile[-1]),
        "bile_fraction_24h": float(bile[-1] / DOSE),
        "mass_recovered_24h": float((plasma[-1] + hepatocyte[-1] + bile[-1]) / DOSE),
    }


def main():
    results = [simulate(label, pars) for label, pars in SCENARIOS.items()]
    lines = [
        "scenario,dose_mmol,plasma_cmax_mmol,hepatocyte_cmax_mmol,bile_amount_24h_mmol,bile_fraction_24h,mass_recovered_24h"
    ]
    for result in results:
        m = metrics(result)
        lines.append(",".join(str(m[k]) for k in (
            "scenario", "dose_mmol", "plasma_cmax_mmol", "hepatocyte_cmax_mmol",
            "bile_amount_24h_mmol", "bile_fraction_24h", "mass_recovered_24h")))
    (OUT / "gadoxetate_pk_scenarios.csv").write_text("\n".join(lines) + "\n", encoding="ascii")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), constrained_layout=True)
    colors = {"healthy": "#1f77b4", "MASL/MASH exploratory": "#d62728", "severe hepatic impairment": "#9467bd"}
    for result in results:
        color = colors[result["label"]]
        t = result["t"]
        plasma, hepatocyte, bile = result["y"]
        axes[0].plot(t, plasma, color=color, label=result["label"])
        axes[1].plot(t, hepatocyte, color=color)
        axes[2].plot(t, bile, color=color)
    axes[0].set_title("Plasma amount", fontsize=14, fontweight="bold")
    axes[1].set_title("Hepatocyte amount", fontsize=14, fontweight="bold")
    axes[2].set_title("Bile amount", fontsize=14, fontweight="bold")
    for ax in axes:
        ax.set_xlabel("time (h)", fontsize=12, fontweight="bold")
        ax.set_ylabel("amount (mmol)", fontsize=12, fontweight="bold")
        ax.tick_params(axis="both", labelsize=11)
        ax.grid(alpha=0.25)
    axes[0].legend(fontsize=10, prop={"weight": "bold"})
    fig.suptitle("Gadoxetate first-pass PK scaffold anchored to human label values", fontsize=16, fontweight="bold")
    fig.savefig(OUT / "figure_gadoxetate_pk.png", dpi=240)
    plt.close(fig)
    print("Wrote", OUT / "figure_gadoxetate_pk.png")
    print("Wrote", OUT / "gadoxetate_pk_scenarios.csv")


if __name__ == "__main__":
    main()
