"""Report model for generated PDF reports."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.visit import Visit


class Report(Base, UUIDMixin, TimestampMixin):
    """Report model for generated PDF reports."""

    __tablename__ = "reports"

    # Unique report identifier
    report_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )  # RPT-2024-00001

    # Relations
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Report Details
    report_type: Mapped[str] = mapped_column(
        String(50), default="full"
    )  # full, prescription_only, diet_only
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Verification
    qr_code_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="generated"
    )  # generated, downloaded, shared

    # Timestamps
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    visit: Mapped["Visit"] = relationship("Visit", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report {self.report_number}>"
