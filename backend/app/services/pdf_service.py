from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def generate_report_pdf(
    output_path: Path,
    patient_name: str,
    image_path: Path,
    heatmap_path: Path,
    diagnosis: str,
    risk_score: float,
    recommendations: list[str],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, "RetinalAI Clinical Report")

    c.setFont("Helvetica", 11)
    c.drawString(40, height - 70, f"Patient: {patient_name}")
    c.drawString(40, height - 90, f"Diagnosis: {diagnosis}")
    c.drawString(40, height - 110, f"Risk Score: {risk_score:.2f}/100")

    try:
        c.drawImage(ImageReader(str(image_path)), 40, height - 370, width=240, height=240, preserveAspectRatio=True)
        c.drawImage(ImageReader(str(heatmap_path)), 300, height - 370, width=240, height=240, preserveAspectRatio=True)
    except Exception:
        c.drawString(40, height - 150, "Image rendering failed.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 400, "Recommendations")
    c.setFont("Helvetica", 10)

    y = height - 420
    for rec in recommendations[:8]:
        c.drawString(50, y, f"- {rec}")
        y -= 18

    c.save()
