from datetime import datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    patient_code: str = Field(min_length=2, max_length=64)
    full_name: str = Field(min_length=2, max_length=255)
    age: int = Field(ge=0, le=120)
    sex: str = Field(min_length=1, max_length=16)


class PatientRead(BaseModel):
    id: int
    patient_code: str
    full_name: str
    age: int
    sex: str
    created_at: datetime

    class Config:
        from_attributes = True


class PatientHistoryItem(BaseModel):
    scan_id: int
    dr_grade: int
    glaucoma: int
    cdr: float
    risk_score: float
    confidence: float
    image_path: str
    summary: str
    created_at: datetime
