from pydantic import BaseModel


class CurvePoint(BaseModel):
    x: float
    y: float


class MetricsResponse(BaseModel):
    auc_roc: float
    qwk: float
    sensitivity: float
    specificity: float
    f1_score: float
    dice_score: float
    roc_curve: list[CurvePoint]
    pr_curve: list[CurvePoint]
    calibration_curve: list[CurvePoint]
    confusion_matrix: list[list[int]]
