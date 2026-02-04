"""Visit repository."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.visit import Visit
from app.repositories.base import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    """Repository for Visit operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Visit, db)

    async def get_with_relations(self, id: UUID) -> Optional[Visit]:
        """Get visit with all related data."""
        result = await self.db.execute(
            select(Visit)
            .options(
                selectinload(Visit.patient),
                selectinload(Visit.doctor),
                selectinload(Visit.recording),
                selectinload(Visit.prescription),
                selectinload(Visit.diet_plan),
                selectinload(Visit.care_instructions),
                selectinload(Visit.reports),
            )
            .where(Visit.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_visit_number(self, visit_number: str) -> Optional[Visit]:
        """Get visit by visit number."""
        result = await self.db.execute(
            select(Visit).where(Visit.visit_number == visit_number)
        )
        return result.scalar_one_or_none()

    async def get_by_patient(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Visit]:
        """Get all visits for a patient."""
        result = await self.db.execute(
            select(Visit)
            .where(Visit.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
            .order_by(Visit.visit_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_doctor(
        self,
        doctor_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Visit]:
        """Get all visits for a doctor."""
        result = await self.db.execute(
            select(Visit)
            .where(Visit.doctor_id == doctor_id)
            .offset(skip)
            .limit(limit)
            .order_by(Visit.visit_date.desc())
        )
        return list(result.scalars().all())

    async def generate_visit_number(self) -> str:
        """Generate a unique visit number in format VIS-YYYY-XXXXX."""
        year = datetime.now().year

        # Get the last visit number for this year
        result = await self.db.execute(
            select(Visit)
            .where(Visit.visit_number.like(f"VIS-{year}-%"))
            .order_by(Visit.visit_number.desc())
            .limit(1)
        )
        last_visit = result.scalar_one_or_none()

        if last_visit:
            last_num = int(last_visit.visit_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"VIS-{year}-{new_num:05d}"

    async def count_by_status(self, status: str) -> int:
        """Count visits by status."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Visit)
            .where(Visit.status == status)
        )
        return result.scalar_one()

    async def count_today(self, doctor_id: UUID) -> int:
        """Count today's visits for a doctor."""
        today = datetime.now().date()
        result = await self.db.execute(
            select(func.count())
            .select_from(Visit)
            .where(
                Visit.doctor_id == doctor_id,
                func.date(Visit.visit_date) == today,
            )
        )
        return result.scalar_one()
