from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "manuscript_second_paper_reviewer_revision.docx"

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(8.5)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def figure(doc, path, caption, width=6.2):
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    match = re.match(r"^(Fig\. \d+)(.*)$", caption)
    if match:
        r = p.add_run(match.group(1))
        r.bold = True
        r.italic = True
        r.font.size = Pt(9)
        r = p.add_run(match.group(2))
    else:
        r = p.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)

def refs(doc):
    items = [
        "1. Li Z, Luo G, Gan C, et al. Spatially resolved multi-omics of human metabolic dysfunction-associated steatotic liver disease. Nature Genetics. 2025;57:3112-3125. https://doi.org/10.1038/s41588-025-02407-8",
        "2. Samarah LZ, Zheng C, Xing X, Lee WD, Afriat A, Chitra U, et al. Spatial metabolic gradients in the liver and small intestine. Nature. 2025;648:182-190. https://doi.org/10.1038/s41586-025-09616-5",
        "3. Trauner M, Boyer JL. Bile salt transporters: molecular characterization, function, and regulation. Physiological Reviews. 2003;83:633-671. https://doi.org/10.1152/physrev.00027.2002",
        "4. Buechler C, et al. Current and advanced applications of gadoxetic acid-enhanced MRI in hepatobiliary disorders. RadioGraphics. 2023;43:e220087. https://doi.org/10.1148/rg.220087",
        "5. U.S. Food and Drug Administration. EOVIST (gadoxetate disodium) prescribing information. Revised 2026.",
        "6. Sourbron SP, et al. Quantitative assessment of liver function using gadoxetate-enhanced magnetic resonance imaging. Investigative Radiology. 2016;51:410-419.",
        "7. He J, et al. Involvement of multiple transporters in the hepatobiliary transport of rosuvastatin. Drug Metabolism and Disposition. 2008;36:1614-1623. https://doi.org/10.1124/dmd.108.020370",
        "8. Ben-Moshe S, Itzkovitz S. Spatial heterogeneity in the mammalian liver. Nature Reviews Gastroenterology & Hepatology. 2019;16:395-410.",
        "9. Hanke N, et al. Physiologically based pharmacokinetic modeling of rosuvastatin to predict transporter-mediated drug-drug interactions. Pharmaceutical Research. 2021;38:1645-1661. https://doi.org/10.1007/s11095-021-03109-6",
        "10. Hildebrandt F, et al. Spatial transcriptomics to define transcriptional patterns of zonation and structural components in the mouse liver. Nature Communications. 2021;12:7046. https://doi.org/10.1038/s41467-021-27354-w",
        "11. Tachikawa M, et al. Liver zonation index of drug transporter and metabolizing enzyme protein expressions in mouse liver acinus. Drug Metabolism and Disposition. 2018;46:610-618. https://doi.org/10.1124/dmd.117.079244",
        "12. Scotcher D, et al. Physiologically based pharmacokinetic modeling of transporter-mediated hepatic disposition of imaging biomarker gadoxetate in rats. Molecular Pharmaceutics. 2021;18:2997-3009. https://doi.org/10.1021/acs.molpharmaceut.1c00206",
        "13. Chu X, et al. Clinical probes and endogenous biomarkers as substrates for transporter drug-drug interaction evaluation: perspectives from the International Transporter Consortium. Clinical Pharmacology & Therapeutics. 2019;105:917-929. https://doi.org/10.1002/cpt.1215",
        "14. U.S. Food and Drug Administration. M12 Drug Interaction Studies: Guidance for Industry. 2024.",
        "15. Costales C, et al. Quantitative prediction of breast cancer resistance protein mediated drug-drug interactions using physiologically-based pharmacokinetic modeling. CPT: Pharmacometrics & Systems Pharmacology. 2021;10:1018-1031. https://doi.org/10.1002/psp4.12672",
    ]
    for item in items:
        p = doc.add_paragraph(item)
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
p.add_run("Testing the pharmacological consequences of liver zonation in MASLD using a spatial PK/PD framework")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Spatially resolved hepatobiliary PK/PD model")
r.italic = True
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Harvey Ho")
r.bold = True
r.font.size = Pt(11)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Rātā BioSim Lab, Auckland, New Zealand")
r.font.size = Pt(10)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("harvey@ratalab.nz")
r.font.size = Pt(10)

doc.add_heading("Abstract", level=1)
doc.add_paragraph(
    "Drug disposition in the liver is shaped by spatially organized uptake, metabolism, canalicular export, and disease-dependent adaptation. "
    "We develop a lobule-scale computational pharmacokinetic/pharmacodynamic (PK/PD) framework using human spatial multi-omics to represent portal, periportal, mid, and central liver states across control, metabolic dysfunction-associated steatotic liver disease (MASLD), MASL, and MASH conditions. "
    "The model includes sinusoidal uptake through SLC10A1, SLCO1B1, and SLCO1B3; canalicular export through ABCB11, ABCC2, and ABCB4; and compensatory basolateral routes through ABCC3 and ABCC4. "
    "We use gadoxetate as a clinically anchored tracer for uptake and hepatobiliary clearance, and retain rosuvastatin as a candidate transporter-sensitive probe for exposure and drug-drug interaction (DDI) analysis. "
    "A counterfactual analysis using identical mean transporter capacities shows that spatial zonation changes predicted MASH bile exposure by approximately 15% relative to a well-mixed liver and changes hepatocyte exposure by approximately 10%. "
    "A pilot sensitivity analysis also predicts increased injury under reduced export and obstruction-like stress. "
    "The framework is designed to answer pharmacology questions: how disease changes exposure, which transporters control clearance, what perturbations increase DDI risk, and how exposure may be linked to efficacy or toxicity. "
    "The current results are exploratory and require compound-specific calibration before clinical prediction."
)
doc.add_paragraph("Keywords: hepatobiliary pharmacokinetics; pharmacodynamics; MASLD; liver zonation; transporter-mediated DDI; gadoxetate")

doc.add_heading("Introduction", level=1)
doc.add_paragraph(
    "Many organ-scale liver PK models intentionally summarize lobular heterogeneity into effective parameters even though hepatocytes occupy distinct microenvironments along the portal-central axis. Spatial organization affects oxygen exposure, substrate availability, metabolic capacity, bile-acid handling, and susceptibility to injury. This is especially relevant in MASLD, where steatosis, inflammation, fibrosis, and transporter adaptation can change both efficacy-relevant exposure and safety margins."
)
doc.add_paragraph(
    "The 2025 Nature Genetics human MASLD atlas provides a current spatial reference for this problem. It combines single-cell transcriptomics, spatial transcriptomics, spatial metabolomics, and spatial proteomics across 61 individuals, including control, MASL, and MASH cohorts [1]. The study orders spatial transcriptomic spots into portal, periportal, mid, and central zones and identifies disease-associated spatial metabolic programs. A complementary 2025 Nature study uses spatial metabolic gradients and bile-acid signals to define portal-to-central metabolic organization [2]."
)
doc.add_paragraph(
    "The pharmacological opportunity is to use these spatial states as model coordinates rather than as descriptive labels. A zonated model can propagate a compound through uptake, intracellular effect or metabolism, canalicular export, and compensatory basolateral clearance. It can then generate exposure, effect, toxicity, and DDI hypotheses that can later be tested with compound-specific data."
)
doc.add_paragraph(
    "This study extends, rather than replaces, the state of the art in transporter PBPK. Rosuvastatin PBPK models have already been qualified against large clinical datasets, including plasma, urine, feces, PET liver measurements, and multiple clinical DDI studies [9]. Their strength is quantitative whole-body prediction; their usual limitation is that hepatic transporter capacity is represented as a lumped organ-level quantity. The unresolved question addressed here is whether the spatial placement of that capacity changes disease- and inhibitor-dependent predictions even when the organ-level mean is unchanged."
)
doc.add_paragraph(
    "This study therefore asks a pharmacology-facing question: when disease and transporter activity have the same organ-level mean, does their lobular placement alter exposure, injury, or DDI-relevant outputs? We address that question with a four-zone model, using gadoxetate as a calibration anchor and rosuvastatin as a transporter-sensitive drug probe."
)
doc.add_paragraph(
    "Accordingly, we test three linked propositions. First, redistributing identical mean transporter capacities changes predicted bile and hepatocyte exposure. Second, disease and export perturbations amplify that spatial effect and can separate plasma, intracellular, and bile-side signals. Third, a clinically anchored gadoxetate scaffold can define measurable qualification targets before compound-specific DDI or efficacy models are attempted."
)
doc.add_paragraph(
    "Several developments make this problem timely. First, liver zonation is not only a metabolic description: spatial transcriptomics shows coordinated gradients in hepatocyte programs and structural components across the lobule [4,10]. Second, drug transporters themselves can be spatially biased. Quantitative proteomics has identified periportal-to-pericentral differences for sinusoidal transporters, while not all canalicular proteins show the same degree of zonation [11]. This creates an important distinction between a model that distributes every capacity uniformly and one that assigns each mechanism its own spatial pattern. Third, transporter-mediated DDIs can change tissue exposure without producing an equally informative change in plasma exposure. Regulatory guidance and transporter-consortium recommendations therefore emphasize mechanistic interpretation, clinical probes, and tissue-relevant evidence rather than plasma AUC alone [13,14]."
)
doc.add_paragraph(
    "The state of the art is consequently strong but fragmented. Spatial omics provides human disease maps; transporter PBPK provides qualified whole-body disposition and DDI prediction; and gadoxetate-enhanced MRI provides a clinically usable readout of hepatic uptake and biliary function [6-9,12]. What is missing is a transparent intermediate layer that preserves lobular organization while remaining compatible with compound-specific PK/PD endpoints. The present framework is intended to occupy that layer. It does not claim that transcript abundance is transport capacity, or that a four-zone model replaces a clinical PBPK model. Its narrower claim is that the placement of capacity can be tested as a causal model feature, with the total mean capacity held fixed."
)

doc.add_heading("Theoretical", level=1)
doc.add_paragraph(
    "The theoretical premise is that lobular position is a causal coordinate for drug disposition. Transporter pathways are coupled across sinusoidal and canalicular membranes, and their protein abundances need not share one common spatial pattern [3,11]. A compound entering from the sinusoidal side therefore encounters zone-dependent uptake, intracellular transformation or effect, canalicular export, and basolateral escape. If these processes are nonlinear or unequally perturbed by disease, redistributing the same mean capacity can change exposure even when an organ-level clearance estimate is unchanged. The model therefore treats spatial arrangement as a testable hypothesis rather than as a visual annotation."
)

doc.add_heading("Methods", level=1)
doc.add_heading("Spatial disease-state representation", level=2)
doc.add_paragraph(
    "The model uses four lobular zones: portal, periportal, mid, and central. Disease states are control, MASL, and MASH, matching the human spatial atlas [1]. Each zone carries relative capacities for uptake, canalicular export, basolateral escape, metabolism, and injury susceptibility. The capacities are dimensionless until replaced by normalized expression, proteomic, or functional measurements. The numerical transport mesh has ten positions, not ten independently measured biological zones: each position inherits one of the four zone labels, so the ten-position representation provides transport resolution without claiming additional atlas resolution."
)
doc.add_heading("Transporter mechanisms", level=2)
table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = "Table Grid"
for c, t in zip(table.rows[0].cells, ("Mechanism", "Genes", "Pharmacological interpretation")):
    cell_text(c, t, bold=True)
    shade(c, "1F4E79")
for row in [
    ("Hepatic uptake", "SLC10A1, SLCO1B1, SLCO1B3", "Controls entry from portal blood and hepatic extraction"),
    ("Canalicular export", "ABCB11, ABCC2, ABCB4", "Controls delivery to bile and biliary clearance"),
    ("Basolateral escape", "ABCC3, ABCC4", "Alternative blood-facing clearance during cholestatic stress"),
    ("Cholangiocyte modification", "CFTR, SLC4A2", "Optional ductular secretion module; not used in the present PK core"),
]:
    cells = table.add_row().cells
    for c, t in zip(cells, row):
        cell_text(c, t)
doc.add_paragraph(
    "The core equations are a reduced mass-balance system. Parent compound enters the hepatocyte according to zonated uptake capacity, is transformed or acts on an intracellular target, and is cleared through canalicular and basolateral routes. DDI simulations alter transporter activity using an inhibition factor, while disease simulations alter the zonal capacity fields. This formulation allows exposure ratios, clearance changes, and effect-site differences to be compared without requiring a macroscopic biliary geometry."
)
doc.add_paragraph(
    "The ten-position carrier profile is derived from Michael Kuecken's published/input bile-flow profile, but the pharmacology layer shown here is new work from this study. Specifically, the zonated transporter fields, parent and metabolite pools, obstruction perturbation, bile-side advection, and injury feedback are implemented as a reduced adapter around those inputs; this figure is not a reproduction of the original full bile-flow solver."
)
figure(doc, ROOT / "outputs" / "supplementary_information" / "supplementary_model_diagram.png", "Fig. 1 Model architecture. The ten-position transport/obstruction prototype is a new reduced pharmacology adapter using Michael Kuecken's input profile; the gadoxetate scaffold is a separate three-compartment calibration model. The blue-shaded upper region contains the new pharmacology adapter, while the green-shaded lower region is the separate gadoxetate scaffold. Disease state and transporter fields modify uptake, export, metabolism, injury susceptibility, and basolateral escape, while obstruction scales local bile velocity. The adapter is not a reproduction of the original full bile-flow solver.")
doc.add_heading("Reduced mass-balance model", level=2)
doc.add_paragraph(
    "For each lobular zone i, the model tracks parent compound in plasma, hepatocytes, and bile. The reduced equations are written below in rendered form; all rate constants are non-negative and may depend on disease state or transporter perturbation."
)
for equation in [
    "dAₕ,ᵢ/dt = kᵤ,ᵢ Aₚ − (k𝚌,ᵢ + kᵦ,ᵢ + kₘ,ᵢ) Aₕ,ᵢ",
    "dAᵦ/dt = Σᵢ k𝚌,ᵢ Aₕ,ᵢ − kₗ Aᵦ",
    "Eᵢ = Eₘₐₓ Cₕ,ᵢ / (EC₅₀ + Cₕ,ᵢ)",
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(equation)
    r.font.name = "Cambria Math"
    r.font.size = Pt(10.5)
    r.italic = True
equation_definitions = doc.add_paragraph(
    "Here Aₚ is the circulating parent amount, Aₕ,ᵢ is the hepatocyte amount in zone i, Aᵦ is the bile amount, kᵤ is uptake, k𝚌 is canalicular export, kᵦ is basolateral escape, kₘ is intracellular metabolism or irreversible loss, and kₗ is bile-side loss. Cₕ,ᵢ is the corresponding intracellular concentration. Transporter inhibition multiplies the affected rate constant by an activity factor between zero and one."
)
equation_definitions.paragraph_format.keep_together = True
doc.add_heading("PK and PD endpoints", level=2)
doc.add_paragraph(
    "The primary PK endpoints are plasma Cmax, area under the concentration-time curve, time to maximum concentration, hepatic exposure, biliary exposure, and route-specific recovery. The principal DDI endpoint is the exposure ratio relative to the victim-drug control condition. For a therapeutic compound, efficacy can be represented with an effect-compartment or Emax relationship, in which effect increases with the active intracellular concentration and is bounded by a compound-specific maximum. Toxicity is represented separately from efficacy using a normalized injury state linked to intracellular and bile-side burden. Biologically, this injury state is a dimensionless accumulator of excess hepatocyte and bile-side stress that feeds back on local flow; it is not an ALT-like concentration, a cholestatic biomarker, or a clinical toxicity probability."
)
doc.add_heading("Gadoxetate reference calibration", level=2)
doc.add_paragraph(
    "Gadoxetate is used as a tracer calibration compound because it has a clinically characterized hepatobiliary disposition. The recommended dose is 0.025 mmol/kg intravenously. The product label reports dose-linear kinetics up to 0.1 mmol/kg, a distribution volume of approximately 0.21 L/kg, plasma protein binding below 10%, a terminal half-life of approximately 0.91-0.95 h, total clearance of about 250 mL/min, and renal clearance of about 120 mL/min [5]. In subjects with normal liver and kidney function, approximately half of the dose is eliminated hepatobiliary and half renally. Severe hepatic impairment can reduce hepatobiliary excretion to approximately 5% [5]."
)
doc.add_paragraph(
    "Human dynamic MRI studies support a two-compartment uptake and efflux interpretation, with aggregate uptake reflecting OATP1B1, OATP1B3, and NTCP contributions and intracellular efflux reflecting canalicular export dominated by MRP2 [6]. These values provide external checks on the model's dose, terminal kinetics, and route-of-excretion fractions."
)
doc.add_heading("Zonation counterfactual", level=2)
doc.add_paragraph(
    "To test whether spatial structure changes pharmacology-facing predictions, we compare the zonated model with a well-mixed counterfactual. The two models receive the same input pulse, use the same mean transporter capacities within each disease state, and differ only in whether those capacities are distributed across portal, periportal, mid, and central positions. We evaluate baseline exposure, 50% uptake inhibition, and 65% MRP2 inhibition. This isolates the contribution of spatial organization from the contribution of total clearance capacity."
)

doc.add_heading("Results", level=1)
doc.add_heading("Zonation changes pharmacology-facing predictions", level=2)
doc.add_paragraph(
    "The central counterfactual result is that spatial arrangement changes predicted exposure even when the mean transporter capacity is held constant. In the MASL baseline, bile AUC was 3071.28 normalized units in the zonated model versus 3277.67 in the well-mixed model, a 6.3% difference. In MASH, bile AUC was 2540.11 versus 2983.36, a 14.9% difference, while hepatocyte parent AUC was 1.137 versus 1.036, a 9.8% increase in the zonated model. Under 65% MRP2 inhibition, the MASH bile-AUC difference increased to 17.2%. The effect is therefore largest when disease and transporter perturbation are combined."
)
doc.add_paragraph(
    "The direction of these changes is mechanistically informative. The zonated model does not simply scale all concentrations upward or downward: it changes the sequence in which uptake, intracellular retention, and canalicular export are encountered. The resulting 6.3% MASL difference is modest, while the 14.9% MASH difference and 17.2% difference under combined disease and MRP2 inhibition are sufficiently large to motivate further sensitivity analyses. Because the two models have identical mean capacities, these contrasts isolate spatial arrangement rather than total transporter abundance. They should therefore be interpreted as a structural-sensitivity result, not as a clinical effect estimate."
)
figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_zonated_vs_wellmixed.png", "Fig. 2 Counterfactual test of spatial zonation. Blue curves use the zonated model; gray curves use a well-mixed model with identical mean capacities. Solid lines are baseline and dashed lines represent 50% uptake inhibition")
doc.add_heading("Atlas-informed transporter sensitivity", level=2)
doc.add_paragraph(
    "The atlas-informed pilot model predicts that disease-state changes in uptake and export can alter exposure even when the nominal input pulse is unchanged. In the current normalized runs, the control baseline produced a bile-associated Cmax of 21.92 and an exposure AUC of 190.16 model units. The MASL baseline produced a Cmax of 86.76 and an AUC of 3071.28, while the MASH baseline produced a Cmax of 69.96 and an AUC of 2540.11. These values are not clinical concentrations; they are sensitivity outputs showing the effect of zonated capacity assumptions."
)
doc.add_paragraph(
    "Reducing MRP2-like export from 1.0 to 0.35 increased the control peak injury signal from 0.0124 to 0.0211. A 50% obstruction increased control exposure AUC from 190.16 to 380.52 and peak injury from 0.0124 to 0.0234. These results are sensitivity outputs; the disease-state comparison should not be overinterpreted until transporter capacities are replaced with measured expression or functional data."
)
doc.add_paragraph(
    "The sensitivity analysis also clarifies why a single exposure endpoint is insufficient. Reduced uptake tends to increase systemic exposure while reducing entry into hepatocytes, whereas reduced canalicular export increases intracellular and bile-side residence. These perturbations can therefore produce different combinations of plasma AUC, hepatocyte AUC, bile exposure, and injury signal. This is aligned with the broader DDI literature, in which overlapping transporter pathways and multipathway inhibitors complicate interpretation of static cutoff rules [13-15]."
)
doc.add_paragraph(
    "The 160-sample Latin-hypercube analysis per profile is a global sensitivity analysis, not an empirical uncertainty quantification. Across the sampled MRP2 activity and obstruction ranges, the control profile had median (5th-95th percentile) bile AUC of 313 (196-669) normalized units and peak injury of 0.0226 (0.0142-0.0430). The MASL profile had bile AUC of 3280 (2924-3983) and peak injury of 0.2203 (0.2044-0.2654). These intervals describe the consequences of the specified parameter sweep; they should not be read as confidence intervals, patient variability, or validated clinical prediction intervals."
)
figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_jpkpd_sensitivity.png", "Fig. 3 Exposure and injury sensitivity to obstruction-like stress and MRP2 activity. Points show a designed global sensitivity analysis; the displayed spread is not an empirical uncertainty interval. The outputs are normalized and intended for model qualification, not clinical dosing.")
doc.add_heading("Gadoxetate PK calibration scaffold", level=2)
doc.add_paragraph(
    "The gadoxetate scaffold reproduced a 24-hour hepatobiliary recovery of 50.1% in the healthy reference condition, matching the approximate label-level 50:50 renal/hepatobiliary split. The exploratory MASL/MASH condition recovered 37.6% through the modeled hepatobiliary route, while the severe hepatic-impairment condition recovered 4.8%, consistent with the label's approximately 5% value. This gives the model a quantitative calibration target before applying it to a therapeutic drug."
)
doc.add_paragraph(
    "Gadoxetate is especially useful here because its uptake and biliary handling are mechanistically linked to OATP-family uptake and MRP-family export, and dynamic imaging can provide liver time-course information in addition to plasma measurements [7,8,12]. The present calibration is deliberately limited to route recovery and broad time-course behavior. A stronger validation would fit individual plasma and liver curves, estimate uncertainty in uptake and export parameters, and test whether the same parameterization predicts an independent dose or impairment cohort."
)
figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_gadoxetate_pk.png", "Fig. 4 Gadoxetate plasma, hepatocyte, and bile amounts under healthy, exploratory MASL/MASH, and severe hepatic-impairment scenarios")
doc.add_heading("DDI and efficacy use case", level=2)
doc.add_paragraph(
    "Rosuvastatin is retained as a future compound-qualification target because its disposition depends on hepatic uptake and efflux transporters, it undergoes limited metabolism, and it has human transporter and PET literature [7,9]. We therefore ran a normalized transporter stress test using the same zonated model: baseline activity was compared with 50% aggregate uptake activity and with MRP2-like activity reduced to 35%. Uptake inhibition reduced the bile-associated AUC ratio to 0.501, 0.502, and 0.502 in control, MASL, and MASH, respectively, and reduced the local parent-pool AUC ratio to 0.480, 0.480, and 0.482. MRP2-like inhibition left the local parent-pool AUC ratio at 1.000, while the bile-associated AUC ratio decreased to 0.964, 0.939, and 0.911 across the same states. These normalized ratios are mechanistic sensitivity outputs, not clinical DDI predictions, and the current prototype does not contain a full plasma victim-drug compartment. BCRP/ABCG2 and compound-specific plasma disposition are also not yet represented. The results therefore demonstrate mechanism separation, not rosuvastatin model qualification."
)
doc.add_paragraph(
    "For efficacy, a therapeutic compound can be assigned a target-specific effect compartment and an exposure-response relationship. The relevant comparison is not simply whether biliary concentration rises, but whether active intracellular exposure crosses the effect threshold while systemic and hepatic exposure remain below toxicity limits. This separation is the principal reason to retain the zonated lobule model for a pharmacology paper."
)
figure(doc, ROOT / "outputs" / "biliary_clearance" / "figure_ddi_efficacy_use_case.png", "Fig. 5 Transporter perturbation and the pharmacology-facing use case. Left and center panels show normalized model outputs relative to each disease-state baseline. The right panel is an illustrative efficacy-mapping extension, not a calibrated therapeutic prediction.")

doc.add_heading("Discussion", level=1)
doc.add_paragraph(
    "This second paper is centered on a pharmacology question: whether spatial liver biology changes compound exposure, effect, and DDI-relevant signals. The key contribution is narrower than a general claim to have solved spatial PBPK: it is a controlled structural-sensitivity experiment in which a human MASLD spatial frame is used to compare zonated and well-mixed models with identical mean transporter capacity. The Nature Genetics atlas supplies human disease-state organization; the 2025 spatial-gradient study supplies metabolic context; and gadoxetate provides a clinically characterized tracer for model qualification."
)
doc.add_paragraph(
    "Relative to existing work, the contribution is an interpretable bridge rather than another black-box predictor. Spatial transcriptomics and proteomics establish that lobular organization is measurable [4,10,11]. Whole-body PBPK models establish how transporter activity can be translated into plasma and tissue exposure, including rosuvastatin DDIs [9,15]. Gadoxetate models show how imaging can constrain transporter-mediated hepatic disposition [12]. The new element is to place these ideas in one controlled experiment: hold the organ-level mean constant, redistribute capacity across zones, and quantify which pharmacology-facing endpoints change. That experiment gives the spatial component a falsifiable role."
)
doc.add_paragraph(
    "The model also makes a useful mechanistic distinction between uptake limitation and export limitation. Lower OATP-mediated uptake can reduce hepatic and biliary exposure while increasing plasma exposure. Lower MRP2-like export can increase intracellular retention and injury risk, while increased ABCC3/ABCC4-like escape can partially restore blood-facing clearance. These mechanisms generate different PK signatures and therefore different DDI and safety interpretations."
)
doc.add_paragraph(
    "The primary limitations are quantitative. The current zonal transporter fields are hypothesis parameters rather than direct atlas-derived fold changes, and the 6-17% counterfactual contrasts are conditional model sensitivities rather than biological estimates of MASLD effect size. The disease states are not yet linked to individual patient covariates, and the therapeutic efficacy module requires a compound-specific target and clinical exposure-response data. Gadoxetate is a calibration tracer, not a surrogate for every drug substrate. Finally, transporter expression is not identical to functional transport capacity, so expression-based updates should be checked against hepatocyte experiments, clinical DDI studies, or imaging-derived uptake rates."
)
doc.add_paragraph(
    "There are also structural limitations. The four-zone representation is a coarse abstraction of a continuous lobular gradient and does not resolve sinusoidal flow, cell-to-cell heterogeneity, cholangiocyte transport, enterohepatic recycling, or spatially varying bile-acid feedback. The bile compartment is a pharmacokinetic sink with an explicit loss term, not a reconstructed duct system. These choices make the counterfactual easy to interpret but may understate delay, mixing, and local concentration gradients. In addition, the current injury signal is a normalized model state rather than a validated biomarker, so it should not be interpreted as a toxicity probability."
)
discussion_next = doc.add_paragraph(
    "The next development stage is a compound-centered benchmark. Rosuvastatin can test transporter-mediated disposition and DDI behavior, followed by a therapeutic candidate with a defined efficacy biomarker and exposure-response relationship. Success should be judged by prediction of plasma exposure, hepatic uptake, biliary recovery, and DDI direction across control and MASLD states, rather than by visual fidelity of an anatomical tree."
)
discussion_next.paragraph_format.keep_together = True
doc.add_paragraph(
    "A practical validation sequence follows from these limitations. First, replace the hypothesis capacity fields with zone-resolved protein or functional measurements and propagate their uncertainty rather than using single point estimates. Second, fit gadoxetate plasma and liver time courses across healthy and impaired cohorts, then test route recovery in an external cohort. Third, qualify the model with rosuvastatin using observed plasma, urine, feces, and liver data and with a small panel of OATP1B/BCRP perturbations. Fourth, compare predicted DDI direction and magnitude against clinical probe studies using the framework of ICH M12 [14]. Finally, add a therapeutic compound only after its intracellular target, effect relationship, and relevant safety biomarker are defined. This sequence separates structural validation from compound-specific validation and reduces the risk of using a spatial model to absorb poorly known drug parameters."
)

doc.add_heading("Conclusions", level=1)
doc.add_paragraph(
    "We present a spatially resolved hepatobiliary PK/PD framework for translating human MASLD zonation into drug-development hypotheses. Its testable contribution is that disease- and transporter-dependent spatial arrangement changes pharmacology-facing outputs beyond what is captured by a well-mixed liver with the same mean capacity. The framework combines a four-zone human MASLD atlas, explicit uptake and export mechanisms, gadoxetate calibration targets, and endpoints relevant to exposure, injury, efficacy, and DDI assessment. The current results establish a structural-sensitivity benchmark, not a clinically validated effect-size model, and define a practical path toward zone-resolved measurement and compound-specific validation."
)

doc.add_heading("Acknowledgments", level=1)
doc.add_paragraph("Not applicable.")

doc.add_heading("Data and code availability", level=1)
doc.add_paragraph(
    "The model code and normalized scenario outputs are maintained with the project materials. Detailed equations, parameter values, model structure, and a code map are provided in the Supplementary Information. The Nature Genetics processed spatial datasets are available through the Human MASLD Spatial Multiomics Atlas and the study accessions HRA007511, OMIX009098, OMIX010136, and OMIX009117. The current transporter coefficients are transparent hypothesis parameters and will be replaced by atlas-derived or experimentally measured values in the next calibration release."
)

doc.add_heading("References", level=1)
refs(doc)
doc.save(OUT)
print(OUT)
