"""Patient schemas."""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class AddressSchema(BaseModel):
    """Schema for address."""

    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "India"


class EmergencyContactSchema(BaseModel):
    """Schema for emergency contact."""

    name: str
    relation: Optional[str] = None
    phone: str


class PatientBase(BaseModel):
    """Base patient schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    blood_group: Optional[str] = Field(
        None, pattern="^(A|B|AB|O)[+-]$"
    )
    phone_primary: str = Field(..., min_length=10, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[AddressSchema] = None
    emergency_contact: Optional[EmergencyContactSchema] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    current_medications: Optional[list[str]] = None

    @field_validator("phone_primary", "phone_secondary")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Remove spaces and dashes
        cleaned = re.sub(r"[\s-]", "", v)
        # Validate Indian phone number format
        if not re.match(r"^\+?91?\d{10}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned


class PatientCreate(PatientBase):
    """Schema for creating a patient."""

    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    blood_group: Optional[str] = None
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[AddressSchema] = None
    emergency_contact: Optional[EmergencyContactSchema] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    current_medications: Optional[list[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")


class PatientResponse(BaseModel):
    """Schema for patient response."""

    id: UUID
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone_primary: str
    phone_secondary: Optional[str] = None
    email: Optional[str] = None
    address: Optional[dict[str, Any]] = None
    emergency_contact: Optional[dict[str, Any]] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    current_medications: Optional[list[str]] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> Optional[int]:
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


class PatientListResponse(BaseModel):
    """Schema for patient list response."""

    results: list[PatientResponse]
    total: int
    skip: int = 0
    limit: int = 20
