# Spatial PK/PD framework for MASLD

Code, input data, figures, manuscript files, and supplementary materials for the spatially resolved hepatobiliary PK/PD framework described in:

**Spatial transporter organization alters predicted hepatobiliary drug disposition in MASLD**

The project combines a ten-position bile-flow transport prototype with four human-profile regions, zonated transporter-capacity hypotheses, obstruction and injury feedback, a separate gadoxetate calibration scaffold, and transporter stress-test analyses. The primary experiment compares a human-profile zonated model with a well-mixed model having the same mean pathway capacities.

## Human spatial-profile basis

The profile framework is organized around three complementary human evidence layers:

- healthy human spatial organization from Yakubovsky et al., *Nature* (2026), doi:10.1038/s41586-026-10377-y;
- human protein-level zonation and architectural vulnerability from Weiss et al., *Nature Metabolism* (2026), doi:10.1038/s42255-026-01459-2;
- disease-associated spatial remodeling across control, MASL, and MASH from Li et al., *Nature Genetics* (2025), doi:10.1038/s41588-025-02407-8.

Rodent studies are used as mechanistic context, not as direct sources of human fold changes. The current coefficients remain transparent hypothesis parameters because the human studies do not by themselves provide compound-specific functional uptake and export rates.

## Main components

- `couple_michael_bileflow.py`: reduced transport/obstruction prototype
- `zonated_transport_genes.py`: four-zone transporter fields
- `compare_zonated_wellmixed.py`: mean-preserving spatial counterfactual
- `run_jpkpd_analysis.py`: scenario grid and Latin-hypercube sensitivity analysis
- `simulate_gadoxetate_pk.py`: gadoxetate calibration scaffold
- `render_ddi_efficacy_figure.py`: DDI and illustrative efficacy figure
- `create_second_paper_draft.py`: manuscript generation
- `create_supplementary_information.py`: supplementary-information generation

## Scope

The current transporter coefficients are transparent hypothesis parameters, not atlas-derived functional measurements. The outputs are structural-sensitivity results and are not clinical dosing, efficacy, toxicity, or DDI predictions.

## Reproducibility

Run the numerical scripts first, then regenerate the manuscript and supplement from the project root. Detailed parameter values, equations, scenario definitions, and implementation notes are provided in the supplementary document under `outputs/`. The submitted manuscript reports structural-sensitivity outputs from the current hypothesis profiles; it does not claim clinical validation.

## Public repository

The repository is publicly available at https://github.com/hwe001/masld-spatial-pkpd-framework. It contains the analysis scripts, input profiles, generated scenario outputs, and figure-generation code used for the manuscript.
