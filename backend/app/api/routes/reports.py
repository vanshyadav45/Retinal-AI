from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Patient, Report, Scan
from app.schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from app.services.pdf_service import generate_report_pdf


router = APIRouter(tags=["reports"])


@router.post("/report/generate", response_model=ReportGenerateResponse)
def generate_report(payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == payload.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    patient = db.query(Patient).filter(Patient.id == scan.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    reports_dir = Path(settings.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"report_{scan.id}_{ts}.pdf"

    image_path = Path(scan.image_path)
    heatmap_path = image_path.with_name(image_path.name.replace("_image", "_gradcam"))

    diagnosis = f"DR Grade {scan.dr_grade}, Glaucoma {'Positive' if scan.glaucoma == 1 else 'Negative'}, CDR={scan.cdr:.2f}"
    recommendations = [
        "Follow specialist guidance for treatment planning.",
        "Repeat retinal imaging in follow-up as advised.",
        "Correlate with visual acuity and IOP findings.",
    ]

    generate_report_pdf(
        output_path=report_path,
        patient_name=patient.full_name,
        image_path=image_path,
        heatmap_path=heatmap_path,
        diagnosis=diagnosis,
        risk_score=scan.risk_score,
        recommendations=recommendations,
    )

    report = Report(scan_id=scan.id, report_path=str(report_path))
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportGenerateResponse(report_id=report.id, report_path=report.report_path)
