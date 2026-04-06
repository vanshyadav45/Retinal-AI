from app.schemas.analysis import DiseasePrediction, ProviderEntry


DR_LABELS = {
    0: "No diabetic retinopathy",
    1: "Mild non-proliferative diabetic retinopathy",
    2: "Moderate non-proliferative diabetic retinopathy",
    3: "Severe non-proliferative diabetic retinopathy",
    4: "Proliferative diabetic retinopathy",
}


def build_primary_diagnosis(dr_grade: int, glaucoma: int) -> str:
    if dr_grade >= 3 and glaucoma == 1:
        return "High-risk diabetic retinopathy with glaucoma suspicion"
    if dr_grade >= 3:
        return "Advanced diabetic retinopathy pattern"
    if dr_grade >= 1 and glaucoma == 1:
        return "Early diabetic retinopathy with glaucoma suspicion"
    if dr_grade >= 1:
        return "Early diabetic retinopathy changes"
    if glaucoma == 1:
        return "Glaucoma suspicion"
    return "No major disease signal detected"


def build_dr_stage_label(dr_grade: int) -> str:
    return DR_LABELS.get(dr_grade, "Unknown DR grade")


def build_glaucoma_label(glaucoma: int, cdr: float) -> str:
    if glaucoma == 1 or cdr >= 0.6:
        return "Glaucoma suspect"
    return "Low glaucoma risk"


def build_disease_predictions(dr_grade: int, glaucoma: int, confidence: float, cdr: float) -> list[DiseasePrediction]:
    dr_conf = max(35.0, min(99.0, confidence * 100.0))
    glaucoma_conf = max(35.0, min(99.0, confidence * 100.0 - 5.0 + (8.0 if cdr >= 0.6 else 0.0)))
    return [
        DiseasePrediction(
            disease="Diabetic Retinopathy",
            status="Detected" if dr_grade > 0 else "Not Detected",
            severity=build_dr_stage_label(dr_grade),
            confidence_percent=round(dr_conf, 1),
        ),
        DiseasePrediction(
            disease="Glaucoma",
            status="Suspected" if glaucoma == 1 or cdr >= 0.6 else "Not Suspected",
            severity="High concern" if glaucoma == 1 or cdr >= 0.6 else "Low concern",
            confidence_percent=round(glaucoma_conf, 1),
        ),
    ]


def build_treatment_suggestions(dr_grade: int, glaucoma: int, risk_score: float) -> list[str]:
    suggestions: list[str] = [
        "Keep blood sugar, blood pressure, and cholesterol in target range under physician supervision.",
        "Do not self-medicate eye drops; treatment should be prescribed after complete eye examination.",
    ]

    if dr_grade >= 3:
        suggestions.append("Discuss urgent retinal treatment options such as laser photocoagulation or intravitreal injections.")
    elif dr_grade >= 1:
        suggestions.append("Schedule retina follow-up and monitor for progression with repeat fundus imaging.")

    if glaucoma == 1:
        suggestions.append("Request IOP, gonioscopy, OCT RNFL, and visual field tests to confirm glaucoma and guide therapy.")

    if risk_score >= 75:
        suggestions.append("Seek specialist consultation within 7 days due to high combined risk.")
    elif risk_score >= 50:
        suggestions.append("Arrange specialist consultation within 2 to 4 weeks due to moderate risk.")

    suggestions.append("Maintain smoking cessation, regular exercise, and follow-up frequency advised by your ophthalmologist.")
    return suggestions


def provider_directory() -> list[ProviderEntry]:
    return [
        ProviderEntry(
            name="Dr. Ananya Sharma",
            type="Doctor",
            city="Delhi",
            specialties=["Retina", "Diabetic Eye Disease"],
            contact="+91-11-4000-1111",
            address="VisionCare Eye Center, Connaught Place, Delhi",
            notes="Handles diabetic retinopathy workup and treatment planning.",
        ),
        ProviderEntry(
            name="Dr. Rajiv Menon",
            type="Doctor",
            city="Bengaluru",
            specialties=["Glaucoma", "Optic Nerve Evaluation"],
            contact="+91-80-4200-2233",
            address="Nethra Specialty Clinic, Indiranagar, Bengaluru",
            notes="Focuses on glaucoma screening and long-term pressure management.",
        ),
        ProviderEntry(
            name="Apex Retina Institute",
            type="Hospital",
            city="Mumbai",
            specialties=["Retina Surgery", "Laser Therapy"],
            contact="+91-22-6100-7788",
            address="Lower Parel, Mumbai",
            notes="Comprehensive retina diagnostics and procedural care.",
        ),
        ProviderEntry(
            name="City Eye & Glaucoma Hospital",
            type="Hospital",
            city="Hyderabad",
            specialties=["Glaucoma", "OCT", "Visual Fields"],
            contact="+91-40-3300-2211",
            address="Banjara Hills, Hyderabad",
            notes="Provides full glaucoma pathway including diagnostics and surgery.",
        ),
        ProviderEntry(
            name="Dr. Meera Nair",
            type="Doctor",
            city="Chennai",
            specialties=["Medical Retina", "Tele-ophthalmology"],
            contact="+91-44-5000-9191",
            address="EyeAxis Clinic, Anna Nagar, Chennai",
            notes="Good option for follow-up and chronic diabetic eye monitoring.",
        ),
    ]


def build_suggested_providers(risk_score: float, top_n: int = 3) -> list[ProviderEntry]:
    providers = provider_directory()
    if risk_score >= 75:
        # Prioritize hospitals for high-risk pathways.
        ordered = sorted(providers, key=lambda p: 0 if p.type == "Hospital" else 1)
    else:
        ordered = providers
    return ordered[:top_n]
