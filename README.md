# Spatial PK/PD framework for MASLD

Code, input data, figures, manuscript files, and supplementary materials for the spatially resolved hepatobiliary PK/PD framework described in:

**Testing the pharmacological consequences of liver zonation in MASLD using a spatial PK/PD framework**

The project combines a ten-position bile-flow transport prototype with four biological liver zones, zonated transporter-capacity hypotheses, obstruction and injury feedback, a separate gadoxetate calibration scaffold, and transporter stress-test analyses.

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

Run the numerical scripts first, then regenerate the manuscript and supplement from the project root. Detailed parameter values, equations, scenario definitions, and implementation notes are provided in the supplementary document under `outputs/`.
