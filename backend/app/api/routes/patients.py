from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Patient, Scan
from app.schemas.patients import PatientCreate, PatientHistoryItem, PatientRead
from app.services.recommendation_service import build_patient_summary


router = APIRouter(tags=["patients"])


@router.get("/patients", response_model=list[PatientRead])
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).order_by(Patient.created_at.desc()).all()


@router.post("/patients", response_model=PatientRead)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    exists = db.query(Patient).filter(Patient.patient_code == payload.patient_code).first()
    if exists:
        raise HTTPException(status_code=409, detail="Patient code already exists")

    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/patients/{patient_id}/history", response_model=list[PatientHistoryItem])
def patient_history(patient_id: int, db: Session = Depends(get_db)):
    scans = (
        db.query(Scan)
        .filter(Scan.patient_id == patient_id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    return [
        PatientHistoryItem(
            scan_id=s.id,
            dr_grade=s.dr_grade,
            glaucoma=s.glaucoma,
            cdr=s.cdr,
            risk_score=s.risk_score,
            confidence=s.confidence,
            image_path=s.image_path,
            summary=build_patient_summary(s.dr_grade, s.glaucoma, s.cdr, s.risk_score),
            created_at=s.created_at,
        )
        for s in scans
    ]
