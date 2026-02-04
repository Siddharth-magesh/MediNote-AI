"""Diet plan model."""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ARRAY, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit


class DietPlan(Base, UUIDMixin, TimestampMixin):
    """Diet plan model for nutritional recommendations."""

    __tablename__ = "diet_plans"

    # Relations
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Meals (JSONB)
    breakfast: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # {
    #   "items": ["Oatmeal", "Fruits", "Milk"],
    #   "timing": "7:00 AM - 9:00 AM",
    #   "portion_guidance": "1 cup oatmeal, 1 fruit",
    #   "notes": "Avoid sugar"
    # }

    lunch: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    dinner: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    snacks: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Restrictions
    foods_to_avoid: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    dietary_restrictions: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    hydration_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    visit: Mapped["Visit"] = relationship("Visit", back_populates="diet_plan")

    def __repr__(self) -> str:
        return f"<DietPlan for Visit {self.visit_id}>"
