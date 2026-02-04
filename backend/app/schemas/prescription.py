"""Prescription schemas."""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MedicationSchema(BaseModel):
    """Schema for medication."""

    name: str
    type: str = Field(..., pattern="^(tablet|capsule|syrup|injection|topical|drops|inhaler|other)$")
    dosage: str  # e.g., "500mg"
    frequency: str  # e.g., "twice daily"
    timing: Optional[str] = None  # e.g., "morning, night"
    relation_to_food: Optional[str] = Field(None, pattern="^(before|after|with|empty_stomach)$")
    duration_days: Optional[int] = Field(None, gt=0)
    special_instructions: Optional[str] = None


class InjectionSchema(BaseModel):
    """Schema for injection."""

    name: str
    dosage: str
    frequency: str
    route: str = Field(..., pattern="^(IM|IV|SC|ID)$")
    special_instructions: Optional[str] = None


class PrescriptionBase(BaseModel):
    """Base prescription schema."""

    medications: list[MedicationSchema] = []
    injections: Optional[list[InjectionSchema]] = None
    investigations: Optional[list[str]] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    """Schema for creating a prescription."""

    visit_id: UUID


class PrescriptionUpdate(BaseModel):
    """Schema for updating a prescription."""

    medications: Optional[list[MedicationSchema]] = None
    injections: Optional[list[InjectionSchema]] = None
    investigations: Optional[list[str]] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


class PrescriptionResponse(BaseModel):
    """Schema for prescription response."""

    id: UUID
    visit_id: UUID
    medications: list[dict[str, Any]]
    injections: Optional[list[dict[str, Any]]] = None
    investigations: Optional[list[str]] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
