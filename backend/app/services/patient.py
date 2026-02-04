"""Patient service."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.patient import Patient
from app.models.visit import Visit
from app.repositories.patient import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    """Service for patient operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PatientRepository(db)

    async def create(self, data: PatientCreate, doctor_id: UUID) -> Patient:
        """Create a new patient."""
        # Check for duplicate phone number
        existing = await self.repository.get_by_phone(data.phone_primary)
        if existing:
            raise AlreadyExistsError(
                f"Patient with phone number {data.phone_primary} already exists"
            )

        # Generate patient ID
        patient_id = await self.repository.generate_patient_id()

        # Create patient
        patient_data = data.model_dump()

        # Convert nested schemas to dict
        if patient_data.get("address"):
            patient_data["address"] = (
                patient_data["address"].model_dump()
                if hasattr(patient_data["address"], "model_dump")
                else patient_data["address"]
            )
        if patient_data.get("emergency_contact"):
            patient_data["emergency_contact"] = (
                patient_data["emergency_contact"].model_dump()
                if hasattr(patient_data["emergency_contact"], "model_dump")
                else patient_data["emergency_contact"]
            )

        patient = Patient(
            patient_id=patient_id,
            **patient_data,
        )

        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)

        return patient

    async def get_by_id(self, patient_uuid: UUID) -> Patient:
        """Get patient by UUID."""
        patient = await self.repository.get(patient_uuid)
        if not patient:
            raise NotFoundError(f"Patient with ID {patient_uuid} not found")
        return patient

    async def get_by_patient_id(self, patient_id: str) -> Patient:
        """Get patient by patient_id (PAT-YYYY-XXXXX)."""
        patient = await self.repository.get_by_patient_id(patient_id)
        if not patient:
            raise NotFoundError(f"Patient with ID {patient_id} not found")
        return patient

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[Patient], int]:
        """Get all patients with pagination."""
        # Build query
        query = select(Patient)
        count_query = select(func.count()).select_from(Patient)

        if status:
            query = query.where(Patient.status == status)
            count_query = count_query.where(Patient.status == status)

        # Get total count
        result = await self.db.execute(count_query)
        total = result.scalar_one()

        # Get patients
        query = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        patients = list(result.scalars().all())

        return patients, total

    async def update(self, patient_uuid: UUID, data: PatientUpdate) -> Patient:
        """Update a patient."""
        patient = await self.get_by_id(patient_uuid)

        # Update fields
        update_data = data.model_dump(exclude_unset=True)

        # Convert nested schemas to dict if present
        if "address" in update_data and update_data["address"]:
            update_data["address"] = (
                update_data["address"].model_dump()
                if hasattr(update_data["address"], "model_dump")
                else update_data["address"]
            )
        if "emergency_contact" in update_data and update_data["emergency_contact"]:
            update_data["emergency_contact"] = (
                update_data["emergency_contact"].model_dump()
                if hasattr(update_data["emergency_contact"], "model_dump")
                else update_data["emergency_contact"]
            )

        for field, value in update_data.items():
            setattr(patient, field, value)

        await self.db.commit()
        await self.db.refresh(patient)

        return patient

    async def delete(self, patient_uuid: UUID) -> None:
        """Delete a patient (soft delete by setting status to archived)."""
        patient = await self.get_by_id(patient_uuid)
        patient.status = "archived"
        await self.db.commit()

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Patient], int]:
        """Search patients by name, phone, or patient_id."""
        patients = await self.repository.search(query, skip, limit)

        # Get total count for search
        from sqlalchemy import or_
        search_term = f"%{query}%"
        count_result = await self.db.execute(
            select(func.count())
            .select_from(Patient)
            .where(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.phone_primary.ilike(search_term),
                    Patient.patient_id.ilike(search_term),
                )
            )
        )
        total = count_result.scalar_one()

        return patients, total

    async def check_duplicate_phone(self, phone: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a phone number already exists."""
        patient = await self.repository.get_by_phone(phone)
        if not patient:
            return False
        if exclude_id and patient.id == exclude_id:
            return False
        return True

    async def get_patient_history(
        self,
        patient_uuid: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Visit], int]:
        """Get patient visit history."""
        patient = await self.get_by_id(patient_uuid)

        # Get visits with pagination
        query = (
            select(Visit)
            .where(Visit.patient_id == patient.id)
            .order_by(Visit.visit_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        visits = list(result.scalars().all())

        # Get total count
        count_result = await self.db.execute(
            select(func.count())
            .select_from(Visit)
            .where(Visit.patient_id == patient.id)
        )
        total = count_result.scalar_one()

        return visits, total
