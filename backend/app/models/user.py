"""User model for doctors/healthcare providers."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.recording import Recording


class User(Base, UUIDMixin, TimestampMixin):
    """User model representing doctors/healthcare providers."""

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Doctor Profile
    hospital_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hospital_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qualification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    signature_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="doctor",
        lazy="selectin",
    )
    recordings: Mapped[list["Recording"]] = relationship(
        "Recording",
        back_populates="doctor",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
