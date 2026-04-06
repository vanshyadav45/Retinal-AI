from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Scan


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total_scans = db.query(func.count(Scan.id)).scalar() or 0
    high_risk = db.query(func.count(Scan.id)).filter(Scan.risk_score >= 75).scalar() or 0

    now = datetime.utcnow()
    timeline = []
    for i in range(7):
        day = now - timedelta(days=6 - i)
        day_count = (
            db.query(func.count(Scan.id))
            .filter(func.date(Scan.created_at) == day.date())
            .scalar()
            or 0
        )
        timeline.append({"date": day.strftime("%Y-%m-%d"), "count": day_count})

    distribution = {
        "dr_0": db.query(func.count(Scan.id)).filter(Scan.dr_grade == 0).scalar() or 0,
        "dr_1": db.query(func.count(Scan.id)).filter(Scan.dr_grade == 1).scalar() or 0,
        "dr_2": db.query(func.count(Scan.id)).filter(Scan.dr_grade == 2).scalar() or 0,
        "dr_3": db.query(func.count(Scan.id)).filter(Scan.dr_grade == 3).scalar() or 0,
        "dr_4": db.query(func.count(Scan.id)).filter(Scan.dr_grade == 4).scalar() or 0,
    }

    return {
        "total_scans": total_scans,
        "high_risk_cases": high_risk,
        "timeline": timeline,
        "disease_distribution": distribution,
    }
