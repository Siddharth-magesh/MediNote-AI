"""Visit schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SymptomSchema(BaseModel):
    """Schema for symptom."""

    description: str
    duration: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")


class VitalsSchema(BaseModel):
    """Schema for vitals."""

    weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    bmi: Optional[float] = None
    blood_pressure: Optional[str] = None  # "120/80"
    pulse: Optional[int] = Field(None, gt=0, lt=300)
    temperature: Optional[float] = Field(None, gt=30, lt=45)
    spo2: Optional[int] = Field(None, ge=0, le=100)


class VisitBase(BaseModel):
    """Base visit schema."""

    chief_complaint: Optional[str] = None
    symptoms: Optional[list[SymptomSchema]] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    vitals: Optional[VitalsSchema] = None


class VisitCreate(VisitBase):
    """Schema for creating a visit."""

    patient_id: UUID


class VisitUpdate(BaseModel):
    """Schema for updating a visit."""

    chief_complaint: Optional[str] = None
    symptoms: Optional[list[SymptomSchema]] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    vitals: Optional[VitalsSchema] = None
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|cancelled)$")


class VisitResponse(BaseModel):
    """Schema for visit response."""

    id: UUID
    visit_number: str
    patient_id: UUID
    doctor_id: UUID
    visit_date: datetime
    chief_complaint: Optional[str] = None
    symptoms: Optional[list[dict[str, Any]]] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    vitals: Optional[dict[str, Any]] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VisitDetailResponse(VisitResponse):
    """Detailed visit response with related data."""

    patient: Optional[dict[str, Any]] = None
    doctor: Optional[dict[str, Any]] = None
    has_recording: bool = False
    has_prescription: bool = False
    has_diet_plan: bool = False
    has_care_instructions: bool = False


class VisitListResponse(BaseModel):
    """Schema for visit list response."""

    results: list[VisitResponse]
    total: int
    skip: int = 0
    limit: int = 20
