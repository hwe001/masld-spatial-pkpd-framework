"""Human hepatobiliary transporter fields for the zonated pilot model.

The Nature Genetics 2025 atlas supplies the four-zone human spatial frame and
the control/MASL/MASH disease states. It does not publish compound-specific
transport constants, so these are dimensionless hypothesis fields awaiting
replacement by atlas-derived expression scores.
"""

import numpy as np

ZONES = ("portal", "periportal", "mid", "central")

# Relative expression/capacity fields. Values are deliberately modest and
# transparent; they are not presented as measured transporter fold changes.
GENE_FIELDS = {
    "control": {
        "SLC10A1": (1.00, 1.00, 0.98, 0.95),  # NTCP, sinusoidal bile-acid uptake
        "SLCO1B1": (1.00, 1.00, 1.00, 1.00),  # OATP1B1, organic-anion uptake
        "SLCO1B3": (1.00, 1.00, 1.00, 1.00),  # OATP1B3, organic-anion uptake
        "ABCB11": (1.00, 1.00, 1.00, 1.00),  # BSEP, canalicular bile salts
        "ABCC2": (1.00, 1.00, 1.00, 1.00),  # MRP2, conjugated metabolites
        "ABCB4": (1.00, 1.00, 1.00, 1.00),  # MDR3, phospholipids
        "ABCC3": (1.00, 1.00, 1.00, 1.00),  # MRP3, basolateral escape
        "ABCC4": (1.00, 1.00, 1.00, 1.00),  # MRP4, basolateral escape
        "CFTR": (1.00, 1.00, 1.00, 1.00),   # cholangiocyte bicarbonate pathway
        "SLC4A2": (1.00, 1.00, 1.00, 1.00), # AE2, cholangiocyte bicarbonate
    },
    "MASL": {
        "SLC10A1": (0.98, 0.96, 0.92, 0.88),
        "SLCO1B1": (0.98, 0.95, 0.92, 0.88),
        "SLCO1B3": (0.98, 0.95, 0.92, 0.88),
        "ABCB11": (1.00, 0.97, 0.92, 0.88),
        "ABCC2": (1.00, 0.98, 0.94, 0.90),
        "ABCB4": (1.00, 0.97, 0.93, 0.90),
        "ABCC3": (1.05, 1.08, 1.12, 1.16),
        "ABCC4": (1.05, 1.08, 1.12, 1.16),
        "CFTR": (1.00, 0.98, 0.95, 0.92),
        "SLC4A2": (1.00, 0.98, 0.95, 0.92),
    },
    "MASH": {
        "SLC10A1": (0.95, 0.90, 0.82, 0.74),
        "SLCO1B1": (0.95, 0.90, 0.82, 0.74),
        "SLCO1B3": (0.95, 0.90, 0.82, 0.74),
        "ABCB11": (1.00, 0.90, 0.78, 0.68),
        "ABCC2": (1.00, 0.92, 0.82, 0.72),
        "ABCB4": (1.00, 0.92, 0.82, 0.72),
        "ABCC3": (1.10, 1.20, 1.35, 1.50),
        "ABCC4": (1.10, 1.20, 1.35, 1.50),
        "CFTR": (1.00, 0.95, 0.88, 0.80),
        "SLC4A2": (1.00, 0.95, 0.88, 0.80),
    },
}


def expanded_fields(state, zone_labels):
    """Return gene arrays expanded from four zones to model positions."""
    return {
        gene: [GENE_FIELDS[state][gene][ZONES.index(zone)] for zone in zone_labels]
        for gene in GENE_FIELDS[state]
    }


def aggregate_capacity(state, zone_labels):
    fields = expanded_fields(state, zone_labels)
    uptake = sum((np.asarray(fields[g]) for g in ("SLC10A1", "SLCO1B1", "SLCO1B3"))) / 3.0
    canalicular = sum((np.asarray(fields[g]) for g in ("ABCB11", "ABCC2", "ABCB4"))) / 3.0
    escape = sum((np.asarray(fields[g]) for g in ("ABCC3", "ABCC4"))) / 2.0
    ductular = sum((np.asarray(fields[g]) for g in ("CFTR", "SLC4A2"))) / 2.0
    return {"uptake": uptake, "canalicular": canalicular,
            "escape": escape, "ductular": ductular}
