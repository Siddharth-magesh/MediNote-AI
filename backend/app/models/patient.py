"""Patient model."""

from datetime import date
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ARRAY, Date, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit


class Patient(Base, UUIDMixin, TimestampMixin):
    """Patient model."""

    __tablename__ = "patients"

    # Unique patient identifier
    patient_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # PAT-2024-00001

    # Personal Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Contact
    phone_primary: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    phone_secondary: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Address (JSONB)
    address: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # {
    #   "line1": "123 Main St",
    #   "line2": "Apt 4B",
    #   "city": "Mumbai",
    #   "state": "Maharashtra",
    #   "postal_code": "400001",
    #   "country": "India"
    # }

    # Emergency Contact (JSONB)
    emergency_contact: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # {
    #   "name": "Jane Doe",
    #   "relation": "Spouse",
    #   "phone": "+919876543210"
    # }

    # Medical Info
    allergies: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    chronic_conditions: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    current_medications: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, inactive, archived

    # Relationships
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="patient",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> Optional[int]:
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None

    def __repr__(self) -> str:
        return f"<Patient {self.patient_id}: {self.full_name}>"
