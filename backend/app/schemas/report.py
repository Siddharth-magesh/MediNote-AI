"""Report schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    """Request schema for generating a report."""

    visit_id: UUID
    report_type: str = Field(
        default="full",
        pattern="^(full|prescription_only|diet_only|care_only)$",
    )
    format: str = Field(default="pdf", pattern="^(pdf|html)$")
    include_sections: Optional[list[str]] = None  # ["prescription", "diet", "care"]


class ReportGenerateResponse(BaseModel):
    """Response schema for report generation."""

    report_id: UUID
    report_number: str
    download_url: str
    preview_url: str
    expires_at: Optional[datetime] = None


class ReportResponse(BaseModel):
    """Response schema for a report."""

    id: UUID
    report_number: str
    visit_id: UUID
    report_type: str
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    qr_code_data: Optional[str] = None
    checksum: Optional[str] = None
    status: str
    created_at: datetime
    downloaded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Response schema for report list."""

    results: list[ReportResponse]
    total: int
    skip: int = 0
    limit: int = 20


# Template context schemas

class HospitalInfo(BaseModel):
    """Hospital/clinic information for report header."""

    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None


class DoctorInfo(BaseModel):
    """Doctor information for report header."""

    name: str
    qualification: Optional[str] = None
    registration_no: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    signature_url: Optional[str] = None


class PatientInfo(BaseModel):
    """Patient information for report."""

    id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    bmi: Optional[float] = None
    allergies: Optional[list[str]] = None


class MedicationInfo(BaseModel):
    """Medication information for prescription table."""

    name: str
    type: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    timing: Optional[str] = None
    relation_to_food: Optional[str] = None
    duration_days: Optional[int] = None
    special_instructions: Optional[str] = None


class InjectionInfo(BaseModel):
    """Injection information for prescription."""

    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    duration: Optional[str] = None


class PrescriptionInfo(BaseModel):
    """Prescription information for report."""

    medications: list[MedicationInfo] = []
    injections: Optional[list[InjectionInfo]] = None
    investigations: Optional[list[str]] = None
    follow_up_date: Optional[str] = None
    follow_up_notes: Optional[str] = None


class MealInfo(BaseModel):
    """Meal information for diet plan."""

    items: list[str] = []
    timing: Optional[str] = None
    portion_guidance: Optional[str] = None


class DietPlanInfo(BaseModel):
    """Diet plan information for report."""

    breakfast: Optional[MealInfo] = None
    lunch: Optional[MealInfo] = None
    dinner: Optional[MealInfo] = None
    snacks: Optional[MealInfo] = None
    foods_to_avoid: Optional[list[str]] = None
    hydration_advice: Optional[str] = None
    dietary_restrictions: Optional[list[str]] = None


class ExercisePlanInfo(BaseModel):
    """Exercise plan information."""

    type: Optional[list[str]] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    precautions: Optional[list[str]] = None


class CareInstructionsInfo(BaseModel):
    """Care instructions for report."""

    lifestyle_recommendations: Optional[list[str]] = None
    exercise_plan: Optional[ExercisePlanInfo] = None
    sleep_recommendations: Optional[str] = None
    stress_management: Optional[str] = None
    warning_signs: Optional[list[str]] = None
    when_to_seek_help: Optional[list[str]] = None
    additional_notes: Optional[str] = None


class ReportTemplateContext(BaseModel):
    """Full context for rendering a report template."""

    # Header
    hospital: Optional[HospitalInfo] = None
    doctor: DoctorInfo

    # Patient
    patient: PatientInfo

    # Medical data
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[PrescriptionInfo] = None
    diet_plan: Optional[DietPlanInfo] = None
    care_instructions: Optional[CareInstructionsInfo] = None

    # Metadata
    visit_date: str
    report_id: str
    report_number: str
    qr_code_url: Optional[str] = None
    qr_code_base64: Optional[str] = None

    # Sections to include
    include_prescription: bool = True
    include_diet: bool = True
    include_care: bool = True
