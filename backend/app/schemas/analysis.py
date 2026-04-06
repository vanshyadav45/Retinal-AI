from pydantic import BaseModel, Field


class QualityChecks(BaseModel):
    blur_score: float
    brightness_score: float
    retinal_detected: bool


class ScanDetails(BaseModel):
    analyzed_region: str
    scanned_area_percent: float = Field(ge=0.0, le=100.0)
    optic_disc_center: tuple[int, int]
    optic_disc_radius: int
    vessel_density_percent: float = Field(ge=0.0, le=100.0)
    quality_checks: QualityChecks
    limitations: list[str]


class DiseasePrediction(BaseModel):
    disease: str
    status: str
    severity: str
    confidence_percent: float = Field(ge=0.0, le=100.0)


class ProviderEntry(BaseModel):
    name: str
    type: str
    city: str
    specialties: list[str]
    contact: str
    address: str
    notes: str


class AnalysisResponse(BaseModel):
    dr_grade: int = Field(ge=0, le=4)
    glaucoma: int = Field(ge=0, le=1)
    cdr: float = Field(ge=0.0, le=2.0)
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    gradcam_base64: str
    lesion_base64: str
    optic_disc_base64: str
    uncertainty_mean: float
    uncertainty_std: float
    recommendations: list[str]
    patient_summary: str
    next_steps: list[str]
    scan_details: ScanDetails
    primary_diagnosis: str
    dr_stage_label: str
    glaucoma_label: str
    disease_predictions: list[DiseasePrediction]
    treatment_suggestions: list[str]
    suggested_providers: list[ProviderEntry]
