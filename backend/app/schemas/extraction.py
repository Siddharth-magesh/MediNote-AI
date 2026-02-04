"""Schemas for AI extraction service."""

from datetime import date
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Patient Details Extraction
# ============================================================================

class EmergencyContactExtracted(BaseModel):
    """Extracted emergency contact."""

    name: Optional[str] = None
    relation: Optional[str] = None
    phone: Optional[str] = None


class PatientDetailsExtracted(BaseModel):
    """Extracted patient details from transcript."""

    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    blood_group: Optional[str] = Field(
        None, pattern="^(A|B|AB|O)[+-]$"
    )
    weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    contact_number: Optional[str] = None
    allergies: Optional[list[str]] = None
    emergency_contact: Optional[EmergencyContactExtracted] = None


# ============================================================================
# Symptoms Extraction
# ============================================================================

class SymptomExtracted(BaseModel):
    """Extracted symptom."""

    description: str
    duration: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(mild|moderate|severe)$")
    location: Optional[str] = None
    aggravating_factors: Optional[list[str]] = None
    relieving_factors: Optional[list[str]] = None


class SymptomsExtracted(BaseModel):
    """Extracted symptoms from transcript."""

    chief_complaint: Optional[str] = None
    symptoms: Optional[list[SymptomExtracted]] = None
    history_of_present_illness: Optional[str] = None


# ============================================================================
# Prescription Extraction
# ============================================================================

class MedicationExtracted(BaseModel):
    """Extracted medication."""

    name: str
    type: Optional[str] = Field(
        None, pattern="^(tablet|capsule|syrup|injection|topical|other)$"
    )
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    timing: Optional[str] = Field(
        None, pattern="^(morning|afternoon|evening|night|as_needed)$"
    )
    relation_to_food: Optional[str] = Field(
        None, pattern="^(before|after|with|any)$"
    )
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    special_instructions: Optional[str] = None


class InjectionExtracted(BaseModel):
    """Extracted injection."""

    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = Field(None, pattern="^(IM|IV|SC)$")
    duration: Optional[str] = None


class FollowUpExtracted(BaseModel):
    """Extracted follow-up details."""

    duration: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None


class PrescriptionExtracted(BaseModel):
    """Extracted prescription from transcript."""

    medications: Optional[list[MedicationExtracted]] = None
    injections: Optional[list[InjectionExtracted]] = None
    investigations: Optional[list[str]] = None
    follow_up: Optional[FollowUpExtracted] = None


# ============================================================================
# Diet Plan Extraction
# ============================================================================

class MealExtracted(BaseModel):
    """Extracted meal plan."""

    items: Optional[list[str]] = None
    timing: Optional[str] = None
    portion_guidance: Optional[str] = None


class DietPlanExtracted(BaseModel):
    """Extracted diet plan from transcript."""

    breakfast: Optional[MealExtracted] = None
    lunch: Optional[MealExtracted] = None
    dinner: Optional[MealExtracted] = None
    snacks: Optional[MealExtracted] = None
    foods_to_avoid: Optional[list[str]] = None
    hydration_advice: Optional[str] = None
    dietary_restrictions: Optional[list[str]] = None


# ============================================================================
# Care Instructions Extraction
# ============================================================================

class ExercisePlanExtracted(BaseModel):
    """Extracted exercise plan."""

    type: Optional[list[str]] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    precautions: Optional[list[str]] = None


class CareInstructionsExtracted(BaseModel):
    """Extracted care instructions from transcript."""

    lifestyle_recommendations: Optional[list[str]] = None
    exercise_plan: Optional[ExercisePlanExtracted] = None
    sleep_recommendations: Optional[str] = None
    stress_management: Optional[str] = None
    warning_signs: Optional[list[str]] = None
    when_to_seek_help: Optional[list[str]] = None
    additional_notes: Optional[str] = None


# ============================================================================
# BMI Calculation
# ============================================================================

class BMIResult(BaseModel):
    """BMI calculation result."""

    value: float = Field(..., ge=0, le=100)
    category: str


# ============================================================================
# Confidence Scores
# ============================================================================

class ConfidenceScores(BaseModel):
    """Confidence scores for each extraction category."""

    patient_details: float = Field(0.0, ge=0, le=1)
    symptoms: float = Field(0.0, ge=0, le=1)
    prescription: float = Field(0.0, ge=0, le=1)
    diet_plan: float = Field(0.0, ge=0, le=1)
    care_instructions: float = Field(0.0, ge=0, le=1)
    overall: float = Field(0.0, ge=0, le=1)


# ============================================================================
# Full Extraction Request/Response
# ============================================================================

class ExtractionRequest(BaseModel):
    """Request for data extraction."""

    transcript: str = Field(..., min_length=10)
    visit_id: Optional[UUID] = None
    language: str = Field(default="en")
    extract_patient_details: bool = True
    extract_symptoms: bool = True
    extract_prescription: bool = True
    extract_diet_plan: bool = True
    extract_care_instructions: bool = True


class ExtractionResponse(BaseModel):
    """Response from data extraction."""

    patient_details: Optional[PatientDetailsExtracted] = None
    symptoms: Optional[SymptomsExtracted] = None
    prescription: Optional[PrescriptionExtracted] = None
    diet_plan: Optional[DietPlanExtracted] = None
    care_instructions: Optional[CareInstructionsExtracted] = None
    bmi: Optional[BMIResult] = None
    confidence_scores: ConfidenceScores
    requires_review: bool = False
    review_reasons: Optional[list[str]] = None


class VitalsExtracted(BaseModel):
    """Extracted vitals from transcript."""

    weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    bmi: Optional[float] = None
    blood_pressure: Optional[str] = None
    pulse: Optional[int] = Field(None, gt=0, lt=300)
    temperature: Optional[float] = Field(None, gt=30, lt=45)
    spo2: Optional[int] = Field(None, ge=0, le=100)
