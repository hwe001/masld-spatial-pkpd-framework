# Nature Genetics 2025 integration

The model now uses the spatial organization and disease states reported by:

Li, Z., Luo, G., Gan, C. et al. Spatially resolved multi-omics of human
metabolic dysfunction-associated steatotic liver disease. *Nature Genetics*
57, 3112-3125 (2025). https://doi.org/10.1038/s41588-025-02407-8

## Implemented

- Four lobular positions: portal, periportal, mid, and central.
- Disease states: control, MASL, and MASH.
- Relative zone-dependent profiles for metabolism, export, and injury.
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
the source spreadsheets are imported.
