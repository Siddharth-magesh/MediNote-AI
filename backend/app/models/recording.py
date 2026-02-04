"""Recording model for audio recordings and transcriptions."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.user import User


class Recording(Base, UUIDMixin, TimestampMixin):
    """Recording model for audio recordings."""

    __tablename__ = "recordings"

    # Relations
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    # Audio
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_format: Mapped[str] = mapped_column(String(20), default="wav")
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Transcription
    language: Mapped[str] = mapped_column(String(10), default="en")
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_segments: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True
    )
    # [
    #   {
    #     "text": "Hello, how are you?",
    #     "start": 0.0,
    #     "end": 2.5,
    #     "confidence": 0.95
    #   }
    # ]

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )  # pending, processing, completed, failed

    # Timestamps
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    visit: Mapped["Visit"] = relationship("Visit", back_populates="recording")
    doctor: Mapped["User"] = relationship("User", back_populates="recordings")

    def __repr__(self) -> str:
        return f"<Recording {self.id} - {self.status}>"
