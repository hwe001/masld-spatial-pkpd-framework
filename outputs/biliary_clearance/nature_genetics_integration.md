# Human spatial-profile integration

The model uses three complementary human evidence layers:

1. Healthy human spatial organization from Yakubovsky et al., *Nature* (2026), doi:10.1038/s41586-026-10377-y.
2. Human protein-level zonation and vulnerability to architectural disruption from Weiss et al., *Nature Metabolism* (2026), doi:10.1038/s42255-026-01459-2.
3. Disease-associated spatial organization from:

Li, Z., Luo, G., Gan, C. et al. Spatially resolved multi-omics of human
metabolic dysfunction-associated steatotic liver disease. *Nature Genetics*
57, 3112-3125 (2025). https://doi.org/10.1038/s41588-025-02407-8

## Implemented

- Four coarse human-profile positions: portal, periportal, mid, and central.
- Disease states: control, MASL, and MASH.
- Relative zone-dependent profiles for uptake, metabolism, export, and injury.
- The older Michael Kuecken bile-flow carrier remains the transport backbone.
- MASH scenarios use the steatosis carrier profile because the Michael input
  repository does not provide a separate MASH flow profile.

## Evidence boundary

The paper reports spatial transcriptomic and metabolomic patterns, not direct
ductal flow rates or compound-specific clearance constants. Therefore the
relative factors in `couple_michael_bileflow.py` are hypothesis parameters
informed by the published zonation and disease progression, not extracted
measurements. The paper's processed data are available through the Human MASLD
Spatial Multiomics Atlas and accessions HRA007511, OMIX009098, OMIX010136, and
OMIX009117. Numeric gene-level calibration should replace these factors after
the source spreadsheets are imported. The 2026 human atlas and proteomics
papers define the biological evidence layers but do not provide
compound-specific functional transporter rates. The healthy-control profile
now incorporates three processed human protein zonation coefficients from
Weiss et al. (`ABCB11`, `ABCB4`, and `SLCO1B1`), stored in
`data/human_profiles/` with source and transform metadata. These are
protein-abundance gradients, not functional transporter rates. The MASL/MASH
profiles remain hypothesis parameters pending matched human disease-state
transporter measurements. In the rerun, the healthy-control bile-AUC contrast
changed to 5.3% (zonated 200.15 versus well-mixed 190.04); MASL/MASH outputs
were unchanged because unsupported disease coefficients were not replaced by
invented values.
