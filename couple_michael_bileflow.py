"""Couple the public Michael Kuecken bileflow inputs to drug transport.

The original C++ program solves the detailed bile-flow ODE on 10,000 points.
This adapter uses the repository's published ten-point input profiles to
construct a reduced 10-zone transport model. It preserves the normal-control
versus steatosis parameterisation while adding parent-drug uptake, metabolism,
MRP2 export, axial bile advection, and injury feedback. It can also apply the
four-zone human MASLD atlas structure reported by Wang et al. (Nature Genetics,
2025): portal, periportal, mid, and central.

This is a coupling prototype, not a replacement for compiling the original
C++ solver. The output is therefore reported in normalised model units.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

from zonated_transport_genes import aggregate_capacity, expanded_fields


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "biliary_clearance"
OUT.mkdir(parents=True, exist_ok=True)

# Columns are copied from Michael Kuecken's public input files:
# A, K, epithelial volume fraction, connectivity.
INPUTS = {
    "normal control": np.array([
        [58330.830006862, 206648970055.495, 0.03938394, 0.771937],
        [58015.388588617, 231569264913.359, 0.03587129, 0.871142],
        [60348.151684306, 197300375839.951, 0.03761081, 0.961986],
        [55483.976968513, 241224419088.036, 0.03386869, 0.893793],
        [50809.783814712, 275488406384.075, 0.03104042, 0.860450],
        [56828.282906523, 206761011090.678, 0.03528613, 0.951386],
        [62337.113701067, 201794172784.439, 0.03826954, 0.931587],
        [62899.959125262, 158125453407.200, 0.04185398, 0.962679],
        [57073.753149704, 183625132414.640, 0.03722097, 0.982438],
        [61712.335315994, 158677801762.008, 0.04129924, 0.969123],
    ]),
    "steatosis": np.array([
        [5511.002276664, 422261517689169, 0.00287280, 0.010000],
        [15457.000640061, 7808057239592.060, 0.00912449, 0.122726],
        [27433.939406344, 1381210730104.080, 0.01747601, 0.313083],
        [32671.532844937, 521494282429.810, 0.02145090, 0.659835],
        [45737.348181548, 224778325302.931, 0.03310722, 0.775967],
        [52698.541743688, 142309810288.964, 0.04105153, 0.850081],
        [51010.540328028, 163176507439.641, 0.03915229, 0.767174],
        [46481.072530957, 181169167061.438, 0.03378744, 0.897114],
        [51182.608531234, 150523599528.307, 0.03812766, 0.943592],
        [53032.451806259, 152542928220.661, 0.03950027, 0.888000],
    ]),
}

T = np.linspace(0.0, 60.0, 1201)

# Atlas structure from the 2025 human MASLD spatial multi-omics study. The
# supplied Michael profile has ten CV-to-PV positions, so these labels map the
# reduced positions onto the four published lobular zones. The relative
# factors below are explicit hypothesis parameters, not measurements from the
# atlas; they are kept here so future gene-level extraction can replace them
# without changing the solver.
ATLAS_ZONE_LABELS = np.array([
    "central", "central", "mid", "mid", "mid",
    "periportal", "periportal", "portal", "portal", "portal",
])
ATLAS_PROFILES = {
    "control": {
        "metabolism": {"portal": 1.00, "periportal": 1.05, "mid": 1.00, "central": 0.95},
        "export": {"portal": 1.00, "periportal": 1.00, "mid": 1.00, "central": 1.00},
        "injury": {"portal": 1.00, "periportal": 1.00, "mid": 1.00, "central": 1.00},
    },
    "MASL": {
        "metabolism": {"portal": 0.95, "periportal": 0.92, "mid": 0.88, "central": 0.82},
        "export": {"portal": 1.00, "periportal": 0.97, "mid": 0.92, "central": 0.88},
        "injury": {"portal": 1.00, "periportal": 1.05, "mid": 1.10, "central": 1.15},
    },
    "MASH": {
        "metabolism": {"portal": 0.90, "periportal": 0.85, "mid": 0.78, "central": 0.68},
        "export": {"portal": 1.00, "periportal": 0.92, "mid": 0.82, "central": 0.72},
        "injury": {"portal": 1.05, "periportal": 1.15, "mid": 1.30, "central": 1.45},
    },
}


def atlas_factors(state, n):
    """Expand four-zone atlas factors to the reduced CV-to-PV mesh."""
    profile = ATLAS_PROFILES[state]
    factors = {}
    for name, values in profile.items():
        factors[name] = np.array([values[z] for z in ATLAS_ZONE_LABELS[:n]])
    return factors


def michael_profile(table):
    """Return the reduced velocity profile implied by A, K, and e.

    The C++ solver uses A, K, and e in its local pressure/velocity equations.
    Here their conductance-to-volume combination supplies the spatial carrier
    field for the coupled transport prototype; its median is normalised to 1.
    """
    A, K, e, connectivity = table.T
    conductance = A / K
    velocity = conductance / np.maximum(e, 1.0e-12)
    velocity *= connectivity / np.maximum(connectivity.mean(), 1.0e-12)
    return velocity / np.median(velocity)


def simulate(label, table, mrp2=1.0, obstruction=0.0, atlas_state=None,
             spatial_mode="zonated", uptake_inhibition=1.0):
    n = len(table)
    velocity = michael_profile(table) * (1.0 - obstruction)
    A, K, e, connectivity = table.T
    cyp = np.linspace(1.35, 0.70, n)
    gsh = np.linspace(0.70, 1.25, n)
    factors = atlas_factors(atlas_state, n) if atlas_state else None
    if factors:
        if spatial_mode == "well_mixed":
            factors = {name: np.full(n, np.mean(values))
                       for name, values in factors.items()}
        cyp *= factors["metabolism"]
        export_factor = factors["export"]
        injury_factor = factors["injury"]
        gene_capacity = aggregate_capacity(atlas_state, ATLAS_ZONE_LABELS[:n])
        if spatial_mode == "well_mixed":
            gene_capacity = {name: np.full(n, np.mean(values))
                             for name, values in gene_capacity.items()}
        uptake_factor = gene_capacity["uptake"]
        canalicular_factor = gene_capacity["canalicular"]
        escape_factor = gene_capacity["escape"]
    else:
        export_factor = np.ones(n)
        injury_factor = np.ones(n)
        uptake_factor = np.ones(n)
        canalicular_factor = np.ones(n)
        escape_factor = np.ones(n)
    y0 = np.zeros(4 * n)

    def f(t, y):
        p = np.maximum(y[0:n], 0.0)
        m = np.maximum(y[n:2 * n], 0.0)
        bile = np.maximum(y[2 * n:3 * n], 0.0)
        injury = np.maximum(y[3 * n:4 * n], 0.0)
        dydt = np.zeros_like(y)

        input_rate = 1.0 if t <= 2.0 else 0.0
        uptake = (0.10 * uptake_inhibition * uptake_factor * input_rate
                  * np.exp(-1.7 * np.arange(n) / n))
        metabolism = 0.40 * cyp * p / (0.35 + p)
        export = mrp2 * canalicular_factor * export_factor * 0.30 * m / (0.25 + m)
        local_flow = np.maximum(0.08, velocity * (1.0 - 0.80 * injury))

        # Parent and metabolite dynamics in each CV-to-PV zone.
        dydt[0:n] = uptake - metabolism - 0.025 * p
        dydt[n:2 * n] = metabolism - export - 0.020 * m

        # Upwind advection of bile-borne metabolite toward the portal side.
        advective = np.zeros(n)
        advective[0] = -local_flow[0] * bile[0]
        advective[1:] = local_flow[:-1] * bile[:-1] - local_flow[1:] * bile[1:]
        dydt[2 * n:3 * n] = export / np.maximum(e, 1.0e-3) + advective

        # Bile-side accumulation is an additional cholestatic stress signal;
        # this is the explicit interface to Michael's bile concentration field.
        toxic_load = np.maximum(0.0, m - 0.05 * gsh) + 0.003 * bile
        cholestatic_escape = 0.003 * escape_factor * injury
        dydt[3 * n:4 * n] = 0.020 * injury_factor * toxic_load - 0.004 * injury + cholestatic_escape
        return dydt

    sol = solve_ivp(f, (T[0], T[-1]), y0, t_eval=T, rtol=1.0e-7, atol=1.0e-9)
    if not sol.success:
        raise RuntimeError(sol.message)
    return {"label": label, "velocity": velocity, "t": sol.t, "y": sol.y}


RESULTS = []
for tissue, table in INPUTS.items():
    RESULTS.append(simulate(f"{tissue}: baseline", table))
    RESULTS.append(simulate(f"{tissue}: MRP2 inhibition", table, mrp2=0.35))
    RESULTS.append(simulate(f"{tissue}: 50% obstruction", table, obstruction=0.50))


def write_summary():
    lines = ["scenario,max_bile_metabolite,peak_total_injury,terminal_total_injury"]
    for result in RESULTS:
        y = result["y"]
        bile = y[20:30]
        injury = y[30:40]
        lines.append(
            f"{result['label']},{bile.max():.8g},{injury.sum(axis=0).max():.8g},"
            f"{injury.sum(axis=0)[-1]:.8g}"
        )
    (OUT / "michael_bileflow_coupled_summary.csv").write_text(
        "\n".join(lines) + "\n", encoding="ascii"
    )


def make_figure():
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    colors = {"normal control": "#1f77b4", "steatosis": "#d62728"}
    styles = {"baseline": "-", "MRP2 inhibition": "--", "50% obstruction": ":"}

    for result in RESULTS:
        tissue, scenario = result["label"].split(": ")
        y = result["y"]
        bile = y[20:30].sum(axis=0)
        injury = y[30:40].sum(axis=0)
        axes[0, 1].plot(result["t"], bile, color=colors[tissue],
                         linestyle=styles[scenario], label=result["label"])
        axes[1, 0].plot(result["t"], injury, color=colors[tissue],
                         linestyle=styles[scenario])

    for tissue, table in INPUTS.items():
        axes[0, 0].plot(np.linspace(0, 1, len(table)), michael_profile(table),
                        color=colors[tissue], marker="o", label=tissue)

    for result in RESULTS:
        if result["label"].endswith("baseline"):
            tissue = result["label"].split(": ")[0]
            axes[1, 1].plot(np.linspace(0, 1, 10), result["y"][30:40, :].max(axis=1),
                            color=colors[tissue], marker="o", label=tissue)

    axes[0, 0].set_title("Reduced Michael bileflow carrier profile")
    axes[0, 1].set_title("Bile-borne drug/metabolite exposure")
    axes[1, 0].set_title("Total injury burden")
    axes[1, 1].set_title("Baseline peak injury along CV–PV axis")
    axes[0, 0].set_ylabel("normalised velocity")
    axes[0, 1].set_ylabel("normalised concentration")
    axes[1, 0].set_ylabel("normalised injury")
    axes[1, 1].set_ylabel("normalised injury")
    axes[0, 0].set_xlabel("normalised CV–PV position")
    axes[1, 1].set_xlabel("normalised CV–PV position")
    for ax in axes.flat:
        ax.grid(alpha=0.25)
        ax.set_xlabel(ax.get_xlabel() or "time (model units)")
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].legend(fontsize=7)
    axes[1, 1].legend(fontsize=8)
    fig.suptitle("First coupling of Michael Kuecken bileflow inputs to drug transport")
    fig.savefig(OUT / "figure_michael_bileflow_coupled.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    write_summary()
    make_figure()
    print("Wrote", OUT / "figure_michael_bileflow_coupled.png")
    print("Wrote", OUT / "michael_bileflow_coupled_summary.csv")
