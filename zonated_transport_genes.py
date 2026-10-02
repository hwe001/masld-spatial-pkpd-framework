"""Human-profile hepatobiliary transporter fields for the zonated pilot model.

The profile framework is organized around three human evidence layers:
healthy spatial organization (Yakubovsky et al., Nature 2026), protein-level
zonation and architectural vulnerability (Weiss et al., Nature Metabolism
2026), and disease-associated remodeling across control, MASL, and MASH (Li
et al., Nature Genetics 2025). The control profiles for proteins quantified in
the Weiss et al. human spatial-proteomics resource are derived from its
reported zonation coefficients. These are protein-abundance gradients, not
compound-specific functional transport constants. Genes not quantified in that
resource retain neutral profiles and are flagged in PROFILE_METADATA. Disease
profiles remain hypothesis profiles until matched MASLD transporter
measurements are available. Rodent studies motivate mechanisms but are not
imported as human fold changes.
"""

import numpy as np

ZONES = ("portal", "periportal", "mid", "central")

# Human spatial-proteomics coefficients (Weiss et al., Nat Metab 2026,
# PXD062231; human_controls/results_1_cutoff=0.7.tsv). The source defines the
# coefficient as the effect size along the central-to-portal spatial axis.
# We map that gradient to four model zones and mean-normalize it so the
# zonated and well-mixed counterfactuals have identical mean capacity.
HUMAN_PROTEOMICS_COEFFICIENTS = {
    "ABCB11": 0.47649577262518444,
    "ABCB4": 0.5389872255753327,
    "SLCO1B1": -0.3128739928109853,
}


def _human_profile(coefficient):
    central_to_portal = np.array([1.0, 1.0 / 3.0, -1.0 / 3.0, -1.0])
    profile = np.exp(coefficient * central_to_portal)
    return tuple((profile / profile.mean()).round(8))


# Relative expression/capacity fields. Disease values remain transparent
# hypothesis profiles; the control values for the three measured proteins are
# replaced below with the derived human profiles.
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

# Replace the three healthy/control fields with the measured human profiles.
for _gene, _coefficient in HUMAN_PROTEOMICS_COEFFICIENTS.items():
    GENE_FIELDS["control"][_gene] = _human_profile(_coefficient)

PROFILE_METADATA = {
    "source": "Weiss et al., Nature Metabolism 2026, PXD062231",
    "source_file": "human_controls/results_1_cutoff=0.7.tsv",
    "coefficient_definition": "effect size along the central-to-portal spatial axis",
    "profile_transform": "exp(coefficient * central_to_portal_position), then mean-normalized",
    "measured_human_proteins": sorted(HUMAN_PROTEOMICS_COEFFICIENTS),
    "unsupported_genes": sorted(set(GENE_FIELDS["control"]) - set(HUMAN_PROTEOMICS_COEFFICIENTS)),
    "disease_state_status": "hypothesis profiles; no matched MASLD functional transporter dataset was used",
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
