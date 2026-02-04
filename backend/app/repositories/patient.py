"""Patient repository."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Patient, db)

    async def get_by_patient_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by patient_id (PAT-YYYY-XXXXX)."""
        result = await self.db.execute(
            select(Patient).where(Patient.patient_id == patient_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by primary phone number."""
        result = await self.db.execute(
            select(Patient).where(Patient.phone_primary == phone)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Patient]:
        """Search patients by name, phone, or patient_id."""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(Patient)
            .where(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.phone_primary.ilike(search_term),
                    Patient.patient_id.ilike(search_term),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Patient.created_at.desc())
        )
        return list(result.scalars().all())

    async def generate_patient_id(self) -> str:
        """Generate a unique patient ID in format PAT-YYYY-XXXXX."""
        year = datetime.now().year

        # Get the last patient ID for this year
        result = await self.db.execute(
            select(Patient)
            .where(Patient.patient_id.like(f"PAT-{year}-%"))
            .order_by(Patient.patient_id.desc())
            .limit(1)
        )
        last_patient = result.scalar_one_or_none()

        if last_patient:
            # Extract the sequence number and increment
            last_num = int(last_patient.patient_id.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"PAT-{year}-{new_num:05d}"

    async def count_by_status(self, status: str) -> int:
        """Count patients by status."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Patient)
            .where(Patient.status == status)
        )
        return result.scalar_one()
