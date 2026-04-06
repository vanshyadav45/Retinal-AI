from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="patient", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    image_path: Mapped[str] = mapped_column(Text)
    dr_grade: Mapped[int] = mapped_column(Integer)
    glaucoma: Mapped[int] = mapped_column(Integer)
    cdr: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="scans")
    report = relationship("Report", back_populates="scan", uselist=False)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    report_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="report")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    version: Mapped[str] = mapped_column(String(64), index=True)
    auc: Mapped[float] = mapped_column(Float)
    qwk: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
