"""User schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    hospital_name: Optional[str] = Field(None, max_length=255)
    hospital_address: Optional[str] = None
    qualification: Optional[str] = Field(None, max_length=255)
    registration_number: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    hospital_name: Optional[str] = Field(None, max_length=255)
    hospital_address: Optional[str] = None
    qualification: Optional[str] = Field(None, max_length=255)
    registration_number: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    signature_url: Optional[str] = Field(None, max_length=500)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    email: EmailStr
    name: str
    phone: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    qualification: Optional[str] = None
    registration_number: Optional[str] = None
    department: Optional[str] = None
    signature_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """Extended user profile with additional details."""

    updated_at: Optional[datetime] = None
