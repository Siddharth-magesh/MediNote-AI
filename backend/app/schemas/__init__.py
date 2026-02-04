"""Pydantic Schemas."""

from app.schemas.auth import (
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    RefreshToken,
    Token,
    TokenPayload,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserProfile
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
    PatientListResponse,
)
from app.schemas.visit import (
    VisitCreate,
    VisitResponse,
    VisitUpdate,
    VisitDetailResponse,
    VisitListResponse,
)
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse,
    PrescriptionUpdate,
)

__all__ = [
    # Auth
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    "RefreshToken",
    "Token",
    "TokenPayload",
    "UserLogin",
    "UserRegister",
    # User
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserProfile",
    # Patient
    "PatientCreate",
    "PatientResponse",
    "PatientUpdate",
    "PatientListResponse",
    # Visit
    "VisitCreate",
    "VisitResponse",
    "VisitUpdate",
    "VisitDetailResponse",
    "VisitListResponse",
    # Prescription
    "PrescriptionCreate",
    "PrescriptionResponse",
    "PrescriptionUpdate",
]
