def build_recommendations(dr_grade: int, glaucoma: int, cdr: float, risk_score: float) -> list[str]:
    recs: list[str] = []
    if dr_grade >= 3:
        recs.append("Your scan shows signs that may need urgent eye specialist review.")
    elif dr_grade >= 1:
        recs.append("Please plan an eye check-up in the next 3 to 6 months.")
    else:
        recs.append("No major warning signs were seen. Continue regular yearly eye screening.")

    if glaucoma == 1 or cdr >= 0.6:
        recs.append("The scan suggests possible pressure-related optic nerve stress. Ask for glaucoma testing.")

    if risk_score >= 75:
        recs.append("Overall risk is high. Try to see an eye specialist this week.")
    elif risk_score >= 50:
        recs.append("Overall risk is moderate. Do not delay your next eye consultation.")

    if not recs:
        recs.append("No immediate concern detected. Keep routine monitoring.")

    return recs


def build_patient_summary(dr_grade: int, glaucoma: int, cdr: float, risk_score: float) -> str:
    dr_text = [
        "No diabetic eye damage seen",
        "Very mild diabetic eye changes",
        "Mild diabetic eye changes",
        "Moderate diabetic eye changes",
        "Severe diabetic eye changes",
    ][dr_grade]

    glaucoma_text = "possible glaucoma risk" if glaucoma == 1 else "low glaucoma risk"
    risk_band = "high" if risk_score >= 75 else "moderate" if risk_score >= 50 else "low"

    return (
        f"Summary: {dr_text}, with {glaucoma_text}. "
        f"Estimated cup-to-disc ratio is {cdr:.2f}. "
        f"Overall risk is {risk_band} ({risk_score:.1f}/100)."
    )


def build_next_steps(risk_score: float) -> list[str]:
    if risk_score >= 75:
        return [
            "Book an eye specialist appointment within 7 days.",
            "Carry this report during your visit.",
            "Seek urgent care if vision suddenly worsens.",
        ]
    if risk_score >= 50:
        return [
            "Book an eye check-up in the next 2 to 4 weeks.",
            "Repeat scan during follow-up visit.",
            "Control diabetes and blood pressure carefully.",
        ]
    return [
        "Continue regular annual eye screening.",
        "Repeat scan earlier if symptoms appear.",
        "Maintain healthy blood sugar and blood pressure levels.",
    ]
