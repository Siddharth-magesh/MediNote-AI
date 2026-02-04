"""Prescription model."""

import uuid
from datetime import date
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ARRAY, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit


class Prescription(Base, UUIDMixin, TimestampMixin):
    """Prescription model for medications and follow-up."""

    __tablename__ = "prescriptions"

    # Relations
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Medications (JSONB array)
    medications: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    # [
    #   {
    #     "name": "Paracetamol",
    #     "type": "tablet",
    #     "dosage": "500mg",
    #     "frequency": "twice daily",
    #     "timing": "morning, night",
    #     "relation_to_food": "after",
    #     "duration_days": 5,
    #     "special_instructions": "Take with water"
    #   }
    # ]

    # Injections (JSONB array)
    injections: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    # [
    #   {
    #     "name": "B12",
    #     "dosage": "1ml",
    #     "frequency": "once a month",
    #     "route": "IM"
    #   }
    # ]

    # Lab Tests / Investigations
    investigations: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Follow-up
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    follow_up_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    visit: Mapped["Visit"] = relationship("Visit", back_populates="prescription")

    def __repr__(self) -> str:
        return f"<Prescription for Visit {self.visit_id}>"
