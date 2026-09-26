from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "manuscript_first_draft.docx"

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def set_cell(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(8.5)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def add_figure(doc, path, caption, width=6.2):
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)

def add_refs(doc):
    refs = [
        "1. Li Z, Luo G, Gan C, et al. Spatially resolved multi-omics of human metabolic dysfunction-associated steatotic liver disease. Nature Genetics. 2025;57:3112-3125. doi:10.1038/s41588-025-02407-8.",
        "2. Meyer K, et al. A predictive 3D multi-scale model of biliary fluid dynamics in the liver lobule. Cell Systems. 2017. doi:10.1016/j.cels.2017.02.008.",
        "3. Segovia-Miranda F, et al. Three-dimensional spatially resolved geometrical and functional models of human liver tissue reveal new aspects of NAFLD progression. Nature Medicine. 2019. doi:10.1038/s41591-019-0660-7.",
        "4. Trauner M, Boyer JL. Bile salt transporters: molecular characterization, function, and regulation. Physiological Reviews. 2003;83:633-671. doi:10.1152/physrev.00027.2002.",
        "5. Buechler C, et al. Current and advanced applications of gadoxetic acid-enhanced MRI in hepatobiliary disorders. RadioGraphics. 2023;43:e220087. doi:10.1148/rg.220087.",
        "6. U.S. Food and Drug Administration. EOVIST (gadoxetate disodium) prescribing information. Revised 2026.",
        "7. Sourbron SP, et al. Quantitative assessment of liver function using gadoxetate-enhanced magnetic resonance imaging: monitoring transporter-mediated processes in healthy volunteers. Investigative Radiology. 2016;51:410-419.",
        "8. He J, et al. Involvement of multiple transporters in the hepatobiliary transport of rosuvastatin. Drug Metabolism and Disposition. 2008;36:1614-1623. doi:10.1124/dmd.108.020370.",
        "9. Kuecken M. bileflow. Public research repository. https://github.com/MichaelKuecken/bileflow.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.7)
sec.bottom_margin = Inches(0.7)
sec.left_margin = Inches(0.8)
sec.right_margin = Inches(0.8)
styles = doc.styles
styles["Normal"].font.name = "Arial"
styles["Normal"].font.size = Pt(9.5)
styles["Normal"].paragraph_format.space_after = Pt(5)
styles["Normal"].paragraph_format.line_spacing = 1.08
for name in ("Title", "Heading 1", "Heading 2"):
    styles[name].font.name = "Arial"
    styles[name].font.color.rgb = RGBColor(0, 0, 0)
styles["Title"].font.size = Pt(19)
styles["Heading 1"].font.size = Pt(13)
styles["Heading 2"].font.size = Pt(10.5)

p = doc.add_paragraph(style="Title")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("A zonated computational framework for hepatobiliary transport in a human biliary network")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("First integrated draft")
r.italic = True

doc.add_heading("Abstract", level=1)
doc.add_paragraph(
    "The liver couples spatially organized hepatocyte transport to flow through a branched biliary network. "
    "This study develops a reproducible computational framework that links a human biliary-tree geometry to reduced bile-flow, transient solute-transport, and zonated transporter models. "
    "The supplied geometry contains 408 nodes and 327 connected duct elements with nodal radius, flow, and speed fields. "
    "A public bile-flow formulation is used as the carrier model, and a four-zone human spatial multi-omics framework is added to represent portal, periportal, midlobular, and central states across control, MASL, and MASH conditions. "
    "The model includes hepatocyte uptake through SLC10A1, SLCO1B1, and SLCO1B3; canalicular export through ABCB11, ABCC2, and ABCB4; and compensatory basolateral export through ABCC3 and ABCC4. "
    "Scenario simulations show that reduced export and obstruction increase bile-borne exposure and injury burden in the current normalized model. "
    "Gadoxetate is proposed as a clinically grounded validation tracer because it undergoes hepatocyte uptake and biliary excretion, while rosuvastatin provides a complementary transporter-mediated drug-disposition probe. "
    "The framework is hypothesis-generating; quantitative clinical prediction requires subject-specific flow, transporter expression, and concentration-time calibration."
)
doc.add_paragraph("Keywords: biliary network; hepatobiliary transport; liver zonation; MASLD; gadoxetate; rosuvastatin; computational pharmacology")

doc.add_heading("1 Introduction", level=1)
doc.add_paragraph(
    "Bile formation is a multiscale process. Hepatocytes take up bile acids and organic solutes from sinusoidal blood, export bile salts and conjugated metabolites across the canalicular membrane, and pass the resulting fluid through progressively larger ducts. "
    "The process is therefore not represented adequately by a single well-mixed liver compartment. Bile-flow models have shown that local pressure, epithelial properties, osmotic effects, and canalicular contractility can generate spatial gradients in bile velocity and concentration [2]. "
    "At the tissue scale, hepatocyte function is zonated along the portal-to-central axis."
)
doc.add_paragraph(
    "Recent human spatial multi-omics provides a useful state-of-the-art reference. Li et al. profiled 61 individuals across control, metabolic dysfunction-associated steatotic liver (MASL), and metabolic dysfunction-associated steatohepatitis (MASH), combining single-cell transcriptomics, Visium spatial transcriptomics, spatial metabolomics, and spatial proteomics [1]. "
    "Their analysis ordered spatial spots into portal, periportal, mid, and central zones. The atlas also identified disease-associated spatial metabolic programs and regional changes in immune, endothelial, and stromal organization."
)
doc.add_paragraph(
    "This work combines that spatial framework with a human biliary-tree geometry and a reduced bile-flow carrier. The goal is not to claim that the atlas directly measures ductal flow. Instead, it provides a modern spatial coordinate system for assigning transporter and injury capacities to the flow model, creating a bridge between anatomical network simulation and pharmacokinetic/pharmacodynamic reasoning."
)

doc.add_heading("2 Materials and methods", level=1)
doc.add_heading("2.1 Biliary network geometry", level=2)
doc.add_paragraph(
    "The network was read from exnode and exelem files. The exnode file stores nodal fields and derivatives, including Cartesian coordinates, radius, flow, and speed. The exelem file defines the connected duct elements and their node incidence. The working geometry contains 408 nodes and 327 connected elements. The files are preserved as source geometry, while downstream calculations use a graph representation consisting of nodes, edges, coordinates, radius, and scalar fields."
)
doc.add_paragraph(
    "For visualization, each element centreline is rendered as a tube whose radius is interpolated from the nodal radius field. Flow and speed are mapped to independent colour scales. The browser view uses an orthographic camera, a white background, orbit rotation, zoom, and mouse-drag panning."
)
doc.add_heading("2.2 Reduced bile-flow carrier", level=2)
doc.add_paragraph(
    "The public bileflow repository provides normal-control and steatosis input profiles for a one-dimensional lobular carrier [9]. We use those profiles to define a normalized spatial velocity field for a ten-position reduced model. This is a coupling prototype rather than a replacement for the original high-resolution solver. Model outputs are consequently reported in normalized units unless a future calibration supplies physical concentration and clearance parameters."
)
doc.add_heading("2.3 Human zonation and transporter fields", level=2)
doc.add_paragraph(
    "The 2025 Nature Genetics atlas supplies four spatial states: portal, periportal, mid, and central [1]. The ten-position reduced model is mapped from central to portal using two central positions, three mid positions, two periportal positions, and three portal positions. Three disease labels are supported: control, MASL, and MASH."
)
table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = "Table Grid"
for c, text in zip(table.rows[0].cells, ("Transport step", "Genes used", "Model role")):
    set_cell(c, text, bold=True)
    shade(c, "1F4E79")
for row in [
    ("Sinusoidal uptake", "SLC10A1, SLCO1B1, SLCO1B3", "Entry of bile acids or tracer/drug into hepatocytes"),
    ("Canalicular export", "ABCB11, ABCC2, ABCB4", "Delivery of bile salts, conjugates, and phospholipids to bile"),
    ("Basolateral escape", "ABCC3, ABCC4", "Blood-facing compensation during cholestatic stress"),
    ("Cholangiocyte modification", "CFTR, SLC4A2", "Bicarbonate-rich ductular secretion; future duct-wall module"),
]:
    cells = table.add_row().cells
    for c, text in zip(cells, row):
        set_cell(c, text)
doc.add_paragraph(
    "Relative zonal capacities are treated as hypothesis parameters. The atlas reports spatial expression and metabolite patterns, but does not provide a universal compound-specific clearance coefficient. The gene fields are therefore exposed in a separate table so they can later be replaced by normalized atlas expression scores or proteomic measurements without changing the transport solver."
)
doc.add_heading("2.4 Transient tracer and drug scenarios", level=2)
doc.add_paragraph(
    "A short input pulse is applied to the reduced model. Parent compound enters each position, is transformed by a zonated metabolism term, and produces a bile-borne species that is advected along the carrier field. MRP2 activity and obstruction are varied in scenario and Latin-hypercube analyses. Injury is represented as a normalized feedback state that decreases local effective flow and increases the contribution of accumulated bile-side material to the injury signal."
)
doc.add_paragraph(
    "Gadoxetate is selected as the first translational tracer. It is taken up by hepatocytes primarily through OATP1B1/OATP1B3 and exported into bile through MRP2, while a substantial fraction is eliminated renally [5,6]. It therefore tests the uptake-to-bile pathway without requiring a complicated metabolic network. Rosuvastatin is retained as a second candidate because it has human transporter and PET data and is used as a clinical probe for OATP1B and BCRP pathways [8]."
)
doc.add_heading("2.5 Gadoxetate pharmacokinetic parameterization", level=2)
doc.add_paragraph(
    "The initial gadoxetate parameterization is based on the product label and human tracer-kinetic studies rather than on the normalized bile-flow units. The recommended clinical dose is 0.025 mmol/kg (0.1 mL/kg). Pharmacokinetics are dose-linear up to 0.1 mmol/kg, the steady-state distribution volume is approximately 0.21 L/kg, plasma protein binding is less than 10%, and gadoxetate is not metabolized [6]."
)
pk = doc.add_table(rows=1, cols=3)
pk.alignment = WD_TABLE_ALIGNMENT.CENTER
pk.style = "Table Grid"
for c, text in zip(pk.rows[0].cells, ("Parameter", "Human reference value", "Use in model")):
    set_cell(c, text, bold=True)
    shade(c, "1F4E79")
for row in [
    ("Recommended IV dose", "0.025 mmol/kg", "Bolus input"),
    ("Terminal half-life", "0.91-0.95 h in healthy adults", "Plasma elimination check"),
    ("Total clearance", "about 250 mL/min", "Whole-body clearance"),
    ("Renal clearance", "about 120 mL/min", "Parallel renal route"),
    ("Hepatobiliary elimination", "approximately 50% in normal liver and kidney function", "Bile delivery target"),
    ("Severe hepatic impairment", "hepatobiliary excretion approximately 5% of dose", "Disease stress scenario"),
]:
    cells = pk.add_row().cells
    for c, text in zip(cells, row):
        set_cell(c, text)
doc.add_paragraph(
    "The published human tracer-kinetic model estimates an aggregate hepatic uptake rate and intracellular efflux rate from dynamic MRI, combining the contributions of OATP1B1, OATP1B3, NTCP, and MRP2 [7]. We will use those quantities as calibration targets when a patient or volunteer time series is available. Until then, the present network simulation should be interpreted as a structural transport experiment, not a fitted clinical PK model."
)

doc.add_heading("3 Results", level=1)
doc.add_heading("3.1 Network visualization", level=2)
doc.add_paragraph(
    "The browser visualization reconstructs the complete connected network from the exnode/exelem pair. The original geometry is not symmetric and is consistent with a branched vascular or ductal network rather than a regularized tree. Flow and speed are displayed in separate panels with white backgrounds and continuous colour bars. These views are descriptive and do not imply that the exnode units are already calibrated to millilitres per minute or metres per second."
)
add_figure(doc, ROOT / "fig1a.png", "Figure 1. Source geometry used for network reconstruction. The connected branched geometry and its scalar fields are retained separately from the rendering layer.")
doc.add_heading("3.2 Flow and speed fields", level=2)
doc.add_paragraph(
    "The full-tree rendering preserves low-flow branches that become difficult to see under a single global scale. Flow and speed are therefore shown independently, with the colour bar reporting the displayed scalar range. The two views use the same reconstructed geometry but independent scalar fields."
)
add_figure(doc, ROOT / "outputs" / "figures" / "figure2_combined_flow_speed.png", "Figure 2. Full network visualization. Left: flow field. Right: speed field.")
doc.add_heading("3.3 Zonated transporter and obstruction scenarios", level=2)
doc.add_paragraph(
    "The atlas-informed model predicts larger bile-borne exposure in the MASL and MASH scenarios than in the control carrier. In the current normalized runs, the control baseline had a bile-borne Cmax of 22.12 and an exposure AUC of 192.23 model units. The MASL baseline produced a Cmax of 98.52 and an AUC of 3487.60, while the MASH baseline produced a Cmax of 95.94 and an AUC of 3445.83. These values are model outputs, not clinical concentrations."
)
doc.add_paragraph(
    "Obstruction increased exposure in each state. For example, the control AUC increased from 192.23 to 384.65 with 50% obstruction, and the MASL AUC increased from 3487.60 to 4076.91. Peak normalized injury increased in parallel. The disease-state comparison should be interpreted as a sensitivity result because the current MASH simulation uses the available steatosis carrier profile and changes the zonated transporter and injury fields."
)
add_figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_jpkpd_sensitivity.png", "Figure 3. PK/PD-style sensitivity analysis of bile-borne exposure and injury as functions of obstruction and MRP2 activity. Values are normalized model outputs.")
doc.add_heading("3.4 Gadoxetate PK scaffold", level=2)
doc.add_paragraph(
    "A separate three-compartment scaffold was parameterized with the recommended 0.025 mmol/kg intravenous dose and label-level distribution and clearance values. The healthy scenario recovered 50.1% of the dose through the modeled hepatobiliary route by 24 h, close to the reported approximately 50% fraction. The exploratory MASL/MASH scenario recovered 37.6%, whereas the severe hepatic-impairment scenario recovered 4.8%, consistent with the label's report that hepatobiliary excretion can fall to approximately 5% in severe impairment. These are calibration checks rather than independent clinical predictions."
)
add_figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_gadoxetate_pk.png", "Figure 4. First-pass gadoxetate PK scaffold anchored to human dose, clearance, half-life, and route-of-excretion data. Curves show plasma, hepatocyte, and bile amounts for healthy, exploratory MASL/MASH, and severe hepatic impairment scenarios.")
doc.add_heading("3.5 Translational tracer design", level=2)
doc.add_paragraph(
    "Gadoxetate provides a clinically interpretable next experiment. The simulated parent concentration can be compared with plasma and liver time courses, while the bile-side state can be compared with delayed hepatobiliary-phase enhancement and, where available, biliary excretion measurements. The expected direction is a faster reduction of hepatocyte uptake or canalicular export in disease and obstruction, with compensatory redistribution toward renal or basolateral clearance. The regulatory PK values provide independent checks on dose, terminal half-life, total clearance, and the approximate 50:50 renal/hepatobiliary split [6]."
)

doc.add_heading("4 Discussion", level=1)
doc.add_paragraph(
    "The central contribution is an explicit connection between a branching biliary geometry, a bile-flow carrier, and spatially organized hepatobiliary transport. The approach is modular. Geometry is stored independently of the browser renderer; the carrier can be replaced by the full bileflow solver; and the gene fields can be updated when atlas-level expression values are extracted. This is important because the Nature Genetics atlas and the network files describe different biological scales."
)
doc.add_paragraph(
    "The transporter layer distinguishes normal physiology from cholestatic adaptation. ABCB11, ABCC2, and ABCB4 represent canalicular delivery, whereas ABCC3 and ABCC4 provide alternative basolateral routes that become important when canalicular secretion is impaired. CFTR and SLC4A2 are included for a future cholangiocyte compartment and are not yet used to claim a resolved epithelial secretion field."
)
doc.add_paragraph(
    "Several limitations remain. The supplied flow units are not established, so the current outputs cannot be interpreted as patient-specific concentrations or bile-flow rates. The reduced carrier has ten positions, whereas the anatomical network has hundreds of nodes and elements; a future version should project lobular transporter states onto spatially registered network segments. The relative gene capacities are transparent hypotheses rather than measured fold changes. The model does not yet include explicit plasma, hepatocyte, bile, and cholangiocyte compartments for gadoxetate or rosuvastatin with experimentally fitted parameters."
)
doc.add_paragraph(
    "The next validation step should be a gadoxetate simulation with a defined intravenous bolus, plasma clearance, hepatocyte uptake, MRP2-mediated biliary export, and renal elimination. A second step can use rosuvastatin to test transporter-mediated drug disposition and drug-drug interaction scenarios. Together these experiments would make the framework relevant to both hepatobiliary imaging and quantitative pharmacology."
)
doc.add_heading("5 Conclusions", level=1)
doc.add_paragraph(
    "A reproducible computational framework has been assembled for linking a human biliary network to bile flow, transient solute transport, and four-zone human liver biology. The Nature Genetics 2025 atlas supplies a state-of-the-art spatial disease framework, while gadoxetate offers the most direct clinical tracer for validating hepatocyte uptake and biliary export. The present results are exploratory but provide a concrete route toward calibrated, transporter-resolved hepatobiliary pharmacology."
)
doc.add_heading("References", level=1)
add_refs(doc)
doc.save(OUT)
print(OUT)
