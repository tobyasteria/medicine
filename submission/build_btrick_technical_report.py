from pathlib import Path
import json
import shutil
import subprocess
import sys

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


TEAM_NAME = "Btrick"
ROOT = Path(__file__).resolve().parents[1]

ASSET_DIR = ROOT / "prelim_submission_prep" / "report_assets"
LOCK_PATH = ROOT / "cv_outputs" / "final_ensemble_lock" / "locked_pipeline.json"
HOLDOUT_PATH = ROOT / "holdout_outputs" / "locked_pipeline_v1" / "holdout_evaluation.json"
OUT_DIR = ROOT / "final_submission"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DOCX_PATH = OUT_DIR / "Btrick_Technical_Report.docx"

ASSETS = {
    "loss": ASSET_DIR / "01_loss_curve.png",
    "accuracy": ASSET_DIR / "02_accuracy_curve.png",
    "cm": ASSET_DIR / "03_confusion_matrix.png",
    "roc": ASSET_DIR / "04_roc_auc_curve.png",
    "f1": ASSET_DIR / "05_f1_score_table.csv",
    "pipeline": ASSET_DIR / "06_system_pipeline_diagram.png",
    "architecture": ASSET_DIR / "07_model_architecture_diagram.png",
}


def require(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")


for p in [LOCK_PATH, HOLDOUT_PATH, *ASSETS.values()]:
    require(p)

with open(LOCK_PATH, "r", encoding="utf-8") as f:
    lock = json.load(f)

with open(HOLDOUT_PATH, "r", encoding="utf-8") as f:
    holdout = json.load(f)

oof = lock["oof_metrics"]
hm = holdout["metrics"]
f1_df = pd.read_csv(ASSETS["f1"])


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9)
    return p


def add_bullet(doc, text, level=0):
    style = "List Bullet" if level == 0 else "List Bullet 2"
    p = doc.add_paragraph(style=style)
    p.add_run(text)
    return p


def add_figure(doc, path, caption, width=6.6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    add_caption(doc, caption)


def add_metric_table(doc, title, metrics):
    doc.add_paragraph(title, style="Heading 3")
    rows = [
        ("Competition score P", metrics["P"]),
        ("Accuracy", metrics["Accuracy"]),
        ("Sensitivity", metrics["Sensitivity"]),
        ("Specificity", metrics["Specificity"]),
        ("F1-score", metrics["F1"]),
        ("ROC-AUC", metrics["AUROC"]),
        ("TN", metrics["TN"]),
        ("FP", metrics["FP"]),
        ("FN", metrics["FN"]),
        ("TP", metrics["TP"]),
        ("Threshold", metrics["threshold"]),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Metric"
    hdr[1].text = "Value"
    set_cell_shading(hdr[0], "D9EAF7")
    set_cell_shading(hdr[1], "D9EAF7")
    set_repeat_table_header(table.rows[0])
    for name, value in rows:
        c = table.add_row().cells
        c[0].text = str(name)
        if isinstance(value, float):
            c[1].text = f"{value:.10f}" if abs(value) < 1 else f"{value:.6f}"
        else:
            c[1].text = str(value)
        c[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        c[1].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return table


doc = Document()

# Page setup
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

styles = doc.styles
styles["Normal"].font.name = "Arial"
styles["Normal"].font.size = Pt(10.5)
styles["Title"].font.name = "Arial"
styles["Title"].font.size = Pt(24)
styles["Heading 1"].font.name = "Arial"
styles["Heading 1"].font.size = Pt(16)
styles["Heading 1"].font.color.rgb = RGBColor(31, 78, 121)
styles["Heading 2"].font.name = "Arial"
styles["Heading 2"].font.size = Pt(13)
styles["Heading 2"].font.color.rgb = RGBColor(47, 84, 150)
styles["Heading 3"].font.name = "Arial"
styles["Heading 3"].font.size = Pt(11)

# Cover
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.space_after = Pt(6)
r = p.add_run("TECHNICAL REPORT")
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = RGBColor(31, 78, 121)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Chest X-ray Classification: Normal vs Pneumonia")
r.bold = True
r.font.size = Pt(18)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(f"Team: {TEAM_NAME}")
r.bold = True
r.font.size = Pt(16)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run(
    "DenseNet121 Transfer Learning with 2-Seed, 5-Fold Weighted Ensemble"
).font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Medical Image Classification Challenge 2026").font.size = Pt(12)

doc.add_page_break()

# 1
doc.add_heading("1. Problem Statement and Objective", level=1)
doc.add_paragraph(
    "The objective is to classify chest X-ray images into two classes: Normal and "
    "Pneumonia. The final Btrick system uses transfer learning with DenseNet121 and "
    "a weighted ensemble of ten trained models. The complete development pipeline "
    "was frozen before the sealed internal holdout was opened."
)

doc.add_heading("1.1 Label convention", level=2)
add_bullet(doc, "Normal = 0")
add_bullet(doc, "Pneumonia = 1")
add_bullet(doc, "Final decision: Pneumonia if P(Pneumonia) >= 0.576; otherwise Normal.")

# 2
doc.add_heading("2. Dataset and Evaluation Protocol", level=1)
doc.add_paragraph(
    "The audited development dataset contained 5,132 readable images: 1,299 Normal "
    "and 3,833 Pneumonia images. Exact duplicate groups were detected by SHA-256 and "
    "were never split across training, validation, or holdout partitions."
)
add_bullet(doc, "15% sealed internal holdout: 770 images (195 Normal, 575 Pneumonia).")
add_bullet(doc, "Development set: 4,362 images.")
add_bullet(doc, "Five duplicate-aware cross-validation folds were constructed inside the development set.")
add_bullet(doc, "The sealed holdout was evaluated once after model/threshold/ensemble selection was locked.")

# 3
doc.add_heading("3. Image Preprocessing", level=1)
doc.add_paragraph(
    "The preprocessing pipeline was designed to standardize image geometry and input "
    "distribution while preserving the chest X-ray content used by the model."
)
steps = [
    "Convert every input image to grayscale.",
    "Replicate the grayscale image to three channels to match the ImageNet-pretrained DenseNet121 input interface.",
    "Pad the image to a square canvas using a black border, preventing geometric distortion caused by direct non-uniform resizing.",
    "Resize the square image to 224 x 224 pixels using bilinear interpolation.",
    "Convert pixels to float values in [0,1].",
    "Apply ImageNet normalization using mean [0.485, 0.456, 0.406] and standard deviation [0.229, 0.224, 0.225].",
]
for s in steps:
    add_bullet(doc, s)

doc.add_paragraph(
    "This provides the required resize operation and additional preprocessing beyond "
    "resize, while keeping validation and TEST preprocessing deterministic."
)

# 4
doc.add_heading("4. Data Augmentation", level=1)
doc.add_paragraph(
    "Augmentation was applied only to the training split. Validation, sealed holdout, "
    "and official TEST images use deterministic preprocessing without augmentation."
)
for s in [
    "Random affine rotation: +/-5 degrees.",
    "Random translation: up to 2% of image width/height.",
    "Random scale: 0.95 to 1.05.",
    "Brightness jitter: 0.08.",
    "Contrast jitter: 0.08.",
]:
    add_bullet(doc, s)

# 5
doc.add_heading("5. CNN / Transfer Learning Architecture", level=1)
doc.add_paragraph(
    "Btrick uses DenseNet121 pretrained on ImageNet. The original classifier was replaced "
    "with a two-output fully connected layer for Normal and Pneumonia classification."
)
add_figure(
    doc,
    ASSETS["architecture"],
    "Figure 1. DenseNet121 model architecture and Btrick ensemble structure.",
    width=6.6,
)
doc.add_paragraph(
    "DenseNet121 contains four dense blocks with 6, 12, 24, and 16 dense layers, "
    "respectively. The backbone is followed by batch normalization, ReLU, global "
    "average pooling, and a two-class classifier."
)

# 6
doc.add_heading("6. Training Strategy and Ensemble", level=1)
for s in [
    "Optimizer: AdamW.",
    "Learning rate: 1e-4.",
    "Weight decay: 1e-4.",
    "Maximum epochs: 8.",
    "Early-stopping patience: 3 epochs.",
    "Physical batch size: 8.",
    "Gradient accumulation: 2 (effective batch size = 16).",
    "Loss: class-weighted cross-entropy.",
    "Learning-rate scheduler: cosine annealing.",
]:
    add_bullet(doc, s)

doc.add_paragraph(
    "Two random seeds were trained independently. Each seed used five-fold cross-validation, "
    "giving ten trained DenseNet121 checkpoints in total. Prediction probabilities were averaged "
    "within each seed group, then the two groups were combined by a locked weighted average:"
)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("P_final = 0.70 x P_seed2026 + 0.30 x P_seed3407")
r.bold = True
r.font.size = Pt(12)

# 7
doc.add_heading("7. System Pipeline", level=1)
add_figure(
    doc,
    ASSETS["pipeline"],
    "Figure 2. Complete Btrick system pipeline from input X-ray to final classification.",
    width=6.6,
)
doc.add_paragraph(
    "The report pipeline is intentionally aligned with the submitted Btrick.ipynb: "
    "preprocessing is performed before model inference, augmentation is training-only, "
    "the final model is a 2-seed x 5-fold DenseNet121 ensemble, and the locked threshold is 0.576."
)

# 8
doc.add_heading("8. Internal Performance Analysis", level=1)
doc.add_paragraph(
    "The competition performance score is calculated as:"
)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("P = 0.30 Accuracy + 0.25 Sensitivity + 0.20 Specificity + 0.25 F1")
r.bold = True

add_metric_table(doc, "8.1 Locked five-fold OOF performance", oof)
doc.add_paragraph()
add_metric_table(doc, "8.2 One-time sealed holdout performance", hm)

doc.add_paragraph(
    "The sealed holdout remained strong after the pipeline was locked, with a competition "
    f"score of {hm['P']:.6f}, F1-score of {hm['F1']:.6f}, and ROC-AUC of {hm['AUROC']:.6f}. "
    "The primary degradation relative to OOF was specificity, while sensitivity remained high."
)

# 9
doc.add_heading("9. Required Result Figures", level=1)
add_figure(doc, ASSETS["loss"], "Figure 3. Training Loss Curve across the 10 DenseNet121 training runs.", width=6.2)
doc.add_paragraph(
    "The loss curve summarizes optimization behavior across the five folds of each random seed. "
    "The bold mean curve provides a compact view of convergence, while individual fold curves show training variability."
)
add_figure(doc, ASSETS["accuracy"], "Figure 4. Validation Accuracy Curve across the 10 training runs.", width=6.2)
doc.add_paragraph(
    "Validation accuracy remains high across the cross-validation folds, supporting the stability "
    "of the selected transfer-learning configuration."
)
add_figure(doc, ASSETS["cm"], "Figure 5. Confusion Matrix on the one-time sealed internal holdout.", width=5.5)
doc.add_paragraph(
    f"On the sealed holdout, the model produced TN={hm['TN']}, FP={hm['FP']}, "
    f"FN={hm['FN']}, and TP={hm['TP']}. The result shows very high sensitivity "
    "with a comparatively small number of false-positive Normal cases."
)
add_figure(doc, ASSETS["roc"], "Figure 6. ROC/AUC Curve on the sealed internal holdout.", width=5.7)
doc.add_paragraph(
    f"The sealed-holdout ROC-AUC is {hm['AUROC']:.6f}, indicating strong class separation "
    "over the full range of decision thresholds."
)

doc.add_heading("9.1 F1-score table", level=2)
table = doc.add_table(rows=1, cols=len(f1_df.columns))
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, col in enumerate(f1_df.columns):
    table.rows[0].cells[j].text = str(col)
    set_cell_shading(table.rows[0].cells[j], "D9EAF7")
set_repeat_table_header(table.rows[0])
for _, row in f1_df.iterrows():
    cells = table.add_row().cells
    for j, col in enumerate(f1_df.columns):
        value = row[col]
        if isinstance(value, float):
            cells[j].text = f"{value:.6f}"
        else:
            cells[j].text = str(value)

# 10
doc.add_heading("10. Keras Model Packaging and Reproducibility", level=1)
doc.add_paragraph(
    "The final ten-checkpoint PyTorch ensemble was converted to a single Keras model "
    "without retraining. Numerical parity tests were performed checkpoint-by-checkpoint "
    "and on the complete ensemble."
)
for s in [
    "10/10 checkpoint conversions passed.",
    "Maximum full-ensemble probability difference versus the PyTorch reference: 4.47 x 10^-8.",
    "Class agreement at threshold 0.576: 100%.",
    "Keras save -> reload output difference: 0.",
    "Final Keras model size: approximately 285.68 MiB.",
    "Keras input shape: (None, 224, 224, 3).",
    "Keras output: [P(Normal), P(Pneumonia)].",
]:
    add_bullet(doc, s)

doc.add_paragraph(
    "For the organizer's TEST set, images are downloaded and preprocessed by the team, "
    "then passed to the model loaded with tf.keras.models.load_model('Btrick.keras')."
)

# 11
doc.add_heading("11. Error Characteristics and Limitations", level=1)
doc.add_paragraph(
    "The sealed holdout results show that the model is especially strong at detecting Pneumonia, "
    "with sensitivity of "
    f"{hm['Sensitivity']:.6f}. Specificity ({hm['Specificity']:.6f}) is lower, indicating that "
    "the remaining errors are more likely to be Normal images predicted as Pneumonia. This trade-off "
    "should be considered when interpreting the model's output."
)
doc.add_paragraph(
    "The system is an image classifier and does not localize lesions or provide clinical diagnosis. "
    "Performance reported here reflects the competition dataset and the fixed internal evaluation protocol."
)

# 12
doc.add_heading("12. Conclusion", level=1)
doc.add_paragraph(
    "Btrick's final solution combines deterministic X-ray preprocessing, mild training augmentation, "
    "ImageNet-pretrained DenseNet121 transfer learning, duplicate-aware five-fold cross-validation, "
    "and a two-seed weighted ensemble. The locked system achieved strong OOF and sealed-holdout "
    "performance, and the final Keras conversion reproduced the PyTorch ensemble with negligible numerical error."
)

# Appendix rubric
doc.add_page_break()
doc.add_heading("Appendix A. Technical-Rubric Mapping", level=1)
rubric = [
    ("Reasonable preprocessing", "Resize 224x224 + grayscale/3-channel replication + square padding + ImageNet normalization", "2/2 targeted"),
    ("Data augmentation", "RandomAffine, translation, scaling, brightness and contrast jitter; training only", "2/2 targeted"),
    ("CNN / Transfer Learning", "ImageNet-pretrained DenseNet121 + custom ensemble", "1/2 guaranteed under strict rubric"),
    ("Result analysis", "Loss, accuracy, confusion matrix, F1 table, ROC/AUC", "2/2 targeted"),
    ("Pipeline presentation", "Architecture figure + system block diagram, aligned with Btrick.ipynb", "2/2 targeted"),
]
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Criterion", "Evidence", "Expected"]
for i,h in enumerate(headers):
    table.rows[0].cells[i].text = h
    set_cell_shading(table.rows[0].cells[i], "D9EAF7")
set_repeat_table_header(table.rows[0])
for row in rubric:
    c = table.add_row().cells
    for i,v in enumerate(row):
        c[i].text = v

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("End of Technical Report - Team Btrick")
r.italic = True
r.font.size = Pt(9)

doc.save(DOCX_PATH)
print("Saved:", DOCX_PATH)

# Optional local PDF conversion when LibreOffice/soffice is available.
soffice = shutil.which("soffice") or shutil.which("libreoffice")
if soffice:
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(OUT_DIR), str(DOCX_PATH)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print("PDF conversion attempted. Check:", OUT_DIR / "Btrick_Technical_Report.pdf")
    except Exception as exc:
        print("DOCX created successfully; automatic PDF conversion failed:", exc)
else:
    print("DOCX created successfully. LibreOffice/soffice not found; export PDF manually if needed.")
