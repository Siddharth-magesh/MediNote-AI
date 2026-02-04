"""Care instructions model."""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ARRAY, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit


class CareInstructions(Base, UUIDMixin, TimestampMixin):
    """Care instructions model for lifestyle and care recommendations."""

    __tablename__ = "care_instructions"

    # Relations
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Recommendations
    lifestyle_recommendations: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )

    # Exercise Plan (JSONB)
    exercise_plan: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # {
    #   "type": ["walking", "swimming"],
    #   "frequency": "daily",
    #   "duration": "30 minutes",
    #   "precautions": ["Avoid heavy lifting"]
    # }

    sleep_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stress_management: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Warning Signs
    warning_signs: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    when_to_seek_help: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Additional Notes
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    visit: Mapped["Visit"] = relationship("Visit", back_populates="care_instructions")

    def __repr__(self) -> str:
        return f"<CareInstructions for Visit {self.visit_id}>"
