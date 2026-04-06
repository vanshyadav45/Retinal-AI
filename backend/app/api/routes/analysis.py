from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ml.explainability import fake_lesion_mask, gradcam_like_overlay
from app.ml.inference import RetinalInferenceEngine
from app.ml.preprocessing import detect_optic_disc, preprocess_full_pipeline
from app.models.entities import Patient, Scan
from app.schemas.analysis import AnalysisResponse, QualityChecks, ScanDetails
from app.services.care_navigation_service import (
    build_disease_predictions,
    build_dr_stage_label,
    build_glaucoma_label,
    build_primary_diagnosis,
    build_suggested_providers,
    build_treatment_suggestions,
)
from app.services.recommendation_service import build_next_steps, build_patient_summary, build_recommendations
from app.utils.image_io import (
    ALLOWED_EXTENSIONS,
    blur_score,
    brightness_score,
    image_to_base64,
    read_image_bytes,
    validate_retinal_fundus,
)


router = APIRouter(tags=["analysis"])
engine = RetinalInferenceEngine()

UPLOAD_DIR = Path("data/processed/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    image: UploadFile = File(...),
    patient_id: int | None = Form(default=None),
    mode: str = Form(default="combined"),
    db: Session = Depends(get_db),
):
    extension = Path(image.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    content = await image.read()
    try:
        rgb = read_image_bytes(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    is_retinal, retinal_message = validate_retinal_fundus(rgb)
    if not is_retinal:
        raise HTTPException(status_code=422, detail=retinal_message)

    blur = blur_score(rgb)
    brightness = brightness_score(rgb)
    if blur < 3:
        raise HTTPException(status_code=422, detail="Image quality too low: blur detected")
    if brightness < 20 or brightness > 235:
        raise HTTPException(status_code=422, detail="Image quality failed: brightness out of range")

    prep = preprocess_full_pipeline(rgb)
    inference = engine.predict(prep["processed"], prep["cdr"], prep["visual"], prep["vessel"])

    gradcam = gradcam_like_overlay(prep["visual"], prep["fundus_mask"])
    lesion = fake_lesion_mask(prep["visual"], prep["fundus_mask"])

    mask = prep["fundus_mask"]
    scanned_area_percent = float(round(100.0 * float((mask > 0).mean()), 2))
    vessel_density_percent = float(round(100.0 * float((prep["vessel"] > 35).mean()), 2))
    disc_x, disc_y, disc_r = detect_optic_disc(prep["visual"])

    scan_details = ScanDetails(
        analyzed_region="Retinal fundus region only (non-retinal area excluded)",
        scanned_area_percent=scanned_area_percent,
        optic_disc_center=(int(disc_x), int(disc_y)),
        optic_disc_radius=int(disc_r),
        vessel_density_percent=vessel_density_percent,
        quality_checks=QualityChecks(
            blur_score=float(round(blur, 2)),
            brightness_score=float(round(brightness, 2)),
            retinal_detected=True,
        ),
        limitations=[
            "This is AI-assisted screening, not a final medical diagnosis.",
            "Image quality, reflections, and camera angle can affect results.",
            "Please confirm findings with an ophthalmologist.",
        ],
    )

    uid = str(uuid4())
    image_path = UPLOAD_DIR / f"{uid}_image.png"
    heatmap_path = UPLOAD_DIR / f"{uid}_gradcam.png"
    lesion_path = UPLOAD_DIR / f"{uid}_lesion.png"

    cv2.imwrite(str(image_path), cv2.cvtColor(prep["visual"], cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(heatmap_path), cv2.cvtColor(gradcam, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(lesion_path), cv2.cvtColor(lesion, cv2.COLOR_RGB2BGR))

    recommendations = build_recommendations(
        dr_grade=inference.dr_grade,
        glaucoma=inference.glaucoma,
        cdr=inference.cdr,
        risk_score=inference.risk_score,
    )
    patient_summary = build_patient_summary(
        dr_grade=inference.dr_grade,
        glaucoma=inference.glaucoma,
        cdr=inference.cdr,
        risk_score=inference.risk_score,
    )
    next_steps = build_next_steps(inference.risk_score)
    primary_diagnosis = build_primary_diagnosis(inference.dr_grade, inference.glaucoma)
    dr_stage_label = build_dr_stage_label(inference.dr_grade)
    glaucoma_label = build_glaucoma_label(inference.glaucoma, inference.cdr)
    disease_predictions = build_disease_predictions(
        dr_grade=inference.dr_grade,
        glaucoma=inference.glaucoma,
        confidence=inference.confidence,
        cdr=inference.cdr,
    )
    treatment_suggestions = build_treatment_suggestions(
        dr_grade=inference.dr_grade,
        glaucoma=inference.glaucoma,
        risk_score=inference.risk_score,
    )
    suggested_providers = build_suggested_providers(inference.risk_score)

    if patient_id is not None:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found. Please create/select a valid patient.")

        scan = Scan(
            patient_id=patient_id,
            image_path=str(image_path),
            dr_grade=inference.dr_grade,
            glaucoma=inference.glaucoma,
            cdr=inference.cdr,
            risk_score=inference.risk_score,
            confidence=inference.confidence,
        )
        db.add(scan)
        db.commit()

    return AnalysisResponse(
        dr_grade=inference.dr_grade,
        glaucoma=inference.glaucoma,
        cdr=inference.cdr,
        confidence=inference.confidence,
        risk_score=inference.risk_score,
        gradcam_base64=image_to_base64(gradcam),
        lesion_base64=image_to_base64(lesion),
        optic_disc_base64=image_to_base64(prep["optic_disc"]),
        uncertainty_mean=inference.uncertainty_mean,
        uncertainty_std=inference.uncertainty_std,
        recommendations=recommendations,
        patient_summary=patient_summary,
        next_steps=next_steps,
        scan_details=scan_details,
        primary_diagnosis=primary_diagnosis,
        dr_stage_label=dr_stage_label,
        glaucoma_label=glaucoma_label,
        disease_predictions=disease_predictions,
        treatment_suggestions=treatment_suggestions,
        suggested_providers=suggested_providers,
    )
