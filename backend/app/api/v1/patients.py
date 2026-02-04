"""Patient API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.schemas.visit import VisitResponse
from app.services.patient import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Create a new patient.

    - **first_name**: Patient's first name (required)
    - **last_name**: Patient's last name (required)
    - **phone_primary**: Primary phone number (required, must be unique)
    - **date_of_birth**: Date of birth (optional)
    - **gender**: Gender - male, female, or other (optional)
    - **blood_group**: Blood group - A+, A-, B+, B-, AB+, AB-, O+, O- (optional)
    - **email**: Email address (optional)
    - **address**: Address object (optional)
    - **emergency_contact**: Emergency contact object (optional)
    - **allergies**: List of allergies (optional)
    - **chronic_conditions**: List of chronic conditions (optional)
    - **current_medications**: List of current medications (optional)
    """
    service = PatientService(db)
    try:
        patient = await service.create(data, doctor_id=current_user.id)
        return patient
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("", response_model=PatientListResponse)
async def list_patients(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    status: Optional[str] = Query(
        None,
        pattern="^(active|inactive|archived)$",
        description="Filter by status",
    ),
):
    """
    List all patients with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    - **status**: Filter by patient status (active, inactive, archived)
    """
    service = PatientService(db)
    patients, total = await service.get_all(skip=skip, limit=limit, status=status)

    return PatientListResponse(
        results=patients,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=PatientListResponse)
async def search_patients(
    db: DBSession,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
):
    """
    Search patients by name, phone number, or patient ID.

    - **q**: Search query (searches first name, last name, phone, patient ID)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    """
    service = PatientService(db)
    patients, total = await service.search(query=q, skip=skip, limit=limit)

    return PatientListResponse(
        results=patients,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/check-phone")
async def check_phone_duplicate(
    db: DBSession,
    current_user: CurrentUser,
    phone: str = Query(..., description="Phone number to check"),
    exclude_id: Optional[UUID] = Query(None, description="Patient ID to exclude"),
):
    """
    Check if a phone number is already registered.

    Useful for validating phone numbers before creating/updating a patient.
    """
    service = PatientService(db)
    is_duplicate = await service.check_duplicate_phone(phone, exclude_id)

    return {
        "phone": phone,
        "is_duplicate": is_duplicate,
    }


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a patient by ID.

    - **patient_id**: Patient ID (PAT-YYYY-XXXXX format) or UUID
    """
    service = PatientService(db)
    try:
        # Try to parse as UUID first
        try:
            patient_uuid = UUID(patient_id)
            patient = await service.get_by_id(patient_uuid)
        except ValueError:
            # If not a valid UUID, treat as patient_id string
            patient = await service.get_by_patient_id(patient_id)

        return patient
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update a patient.

    - **patient_id**: Patient ID (PAT-YYYY-XXXXX format) or UUID
    - Only provided fields will be updated
    """
    service = PatientService(db)
    try:
        # Get patient first
        try:
            patient_uuid = UUID(patient_id)
        except ValueError:
            # If not a valid UUID, get by patient_id first
            patient = await service.get_by_patient_id(patient_id)
            patient_uuid = patient.id

        patient = await service.update(patient_uuid, data)
        return patient
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Delete a patient (soft delete - archives the patient).

    - **patient_id**: Patient ID (PAT-YYYY-XXXXX format) or UUID
    """
    service = PatientService(db)
    try:
        # Get patient first
        try:
            patient_uuid = UUID(patient_id)
        except ValueError:
            # If not a valid UUID, get by patient_id first
            patient = await service.get_by_patient_id(patient_id)
            patient_uuid = patient.id

        await service.delete(patient_uuid)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{patient_id}/history")
async def get_patient_history(
    patient_id: str,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
):
    """
    Get patient visit history.

    - **patient_id**: Patient ID (PAT-YYYY-XXXXX format) or UUID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    """
    service = PatientService(db)
    try:
        # Get patient UUID
        try:
            patient_uuid = UUID(patient_id)
        except ValueError:
            patient = await service.get_by_patient_id(patient_id)
            patient_uuid = patient.id

        visits, total = await service.get_patient_history(
            patient_uuid, skip=skip, limit=limit
        )

        return {
            "results": visits,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
