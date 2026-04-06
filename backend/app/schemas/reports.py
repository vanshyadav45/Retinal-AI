from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    scan_id: int = Field(ge=1)


class ReportGenerateResponse(BaseModel):
    report_id: int
    report_path: str
