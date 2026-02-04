"""Visit model for patient consultations."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.recording import Recording
    from app.models.prescription import Prescription
    from app.models.diet_plan import DietPlan
    from app.models.care_instructions import CareInstructions
    from app.models.report import Report


class Visit(Base, UUIDMixin, TimestampMixin):
    """Visit model for patient consultations."""

    __tablename__ = "visits"

    # Unique visit identifier
    visit_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # VIS-2024-00001

    # Relations
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Visit Details
    visit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    symptoms: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    # [
    #   {
    #     "description": "Fever",
    #     "duration": "3 days",
    #     "severity": "moderate"
    #   }
    # ]

    diagnosis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Vitals (JSONB)
    vitals: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # {
    #   "weight_kg": 70,
    #   "height_cm": 175,
    #   "bmi": 22.9,
    #   "blood_pressure": "120/80",
    #   "pulse": 72,
    #   "temperature": 98.6,
    #   "spo2": 98
    # }

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress"
    )  # in_progress, completed, cancelled

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="visits")
    doctor: Mapped["User"] = relationship("User", back_populates="visits")
    recording: Mapped[Optional["Recording"]] = relationship(
        "Recording",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    prescription: Mapped[Optional["Prescription"]] = relationship(
        "Prescription",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    diet_plan: Mapped[Optional["DietPlan"]] = relationship(
        "DietPlan",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    care_instructions: Mapped[Optional["CareInstructions"]] = relationship(
        "CareInstructions",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="visit",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Visit {self.visit_number}>"
