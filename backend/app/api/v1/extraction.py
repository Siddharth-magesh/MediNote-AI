"""AI Extraction API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.extraction import (
    BMIResult,
    CareInstructionsExtracted,
    DietPlanExtracted,
    ExtractionRequest,
    ExtractionResponse,
    PatientDetailsExtracted,
    PrescriptionExtracted,
    SymptomsExtracted,
)
from app.services.extraction import ExtractionService, calculate_bmi

router = APIRouter(prefix="/extraction", tags=["AI Extraction"])


@router.post("/full", response_model=ExtractionResponse)
async def extract_full(
    request: ExtractionRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Extract all medical data from a transcript.

    Extracts:
    - Patient details (name, age, gender, vitals, allergies)
    - Symptoms and chief complaint
    - Prescription (medications, injections, investigations, follow-up)
    - Diet plan (meals, foods to avoid, hydration)
    - Care instructions (lifestyle, exercise, warning signs)

    Also calculates BMI if weight and height are found.

    **Request:**
    - **transcript**: The conversation transcript (required, min 10 chars)
    - **visit_id**: Optional visit ID to save extracted data
    - **language**: Language of transcript (default: en)
    - **extract_***: Flags to control what to extract

    **Response:**
    - Extracted data for each category
    - Confidence scores (0-1) for each extraction
    - requires_review flag if confidence is low
    """
    service = ExtractionService(db)

    try:
        extraction = await service.extract_all(request)

        # If visit_id provided, save to database
        if request.visit_id:
            await service.save_extraction_to_visit(request.visit_id, extraction)

        return extraction

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


@router.post("/patient-details", response_model=PatientDetailsExtracted)
async def extract_patient_details(
    transcript: str,
    current_user: CurrentUser,
):
    """
    Extract only patient details from a transcript.

    Returns patient name, age, gender, weight, height, allergies, etc.
    """
    service = ExtractionService()
    result, confidence = await service._extract_patient_details(transcript)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract patient details from transcript",
        )

    return result


@router.post("/symptoms", response_model=SymptomsExtracted)
async def extract_symptoms(
    transcript: str,
    current_user: CurrentUser,
):
    """
    Extract only symptoms from a transcript.

    Returns chief complaint, symptoms list with severity/duration, and history.
    """
    service = ExtractionService()
    result, confidence = await service._extract_symptoms(transcript)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract symptoms from transcript",
        )

    return result


@router.post("/prescription", response_model=PrescriptionExtracted)
async def extract_prescription(
    transcript: str,
    current_user: CurrentUser,
):
    """
    Extract only prescription from a transcript.

    Returns medications, injections, investigations, and follow-up details.
    """
    service = ExtractionService()
    result, confidence = await service._extract_prescription(transcript)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract prescription from transcript",
        )

    return result


@router.post("/diet-plan", response_model=DietPlanExtracted)
async def extract_diet_plan(
    transcript: str,
    current_user: CurrentUser,
):
    """
    Extract only diet plan from a transcript.

    Returns meal plans, foods to avoid, and hydration advice.
    """
    service = ExtractionService()
    result, confidence = await service._extract_diet_plan(transcript)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract diet plan from transcript",
        )

    return result


@router.post("/care-instructions", response_model=CareInstructionsExtracted)
async def extract_care_instructions(
    transcript: str,
    current_user: CurrentUser,
):
    """
    Extract only care instructions from a transcript.

    Returns lifestyle recommendations, exercise plan, and warning signs.
    """
    service = ExtractionService()
    result, confidence = await service._extract_care_instructions(transcript)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract care instructions from transcript",
        )

    return result


@router.post("/bmi", response_model=BMIResult)
async def calculate_bmi_endpoint(
    weight_kg: float,
    height_cm: float,
    current_user: CurrentUser,
):
    """
    Calculate BMI from weight and height.

    - **weight_kg**: Weight in kilograms (required)
    - **height_cm**: Height in centimeters (required)

    Returns BMI value and category (Underweight/Normal/Overweight/Obese).
    """
    if weight_kg <= 0 or weight_kg > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid weight: must be between 0 and 500 kg",
        )

    if height_cm <= 0 or height_cm > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid height: must be between 0 and 300 cm",
        )

    return calculate_bmi(weight_kg, height_cm)


@router.post("/visit/{visit_id}/extract")
async def extract_and_save_to_visit(
    visit_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Extract data from a visit's recording transcript and save to database.

    This endpoint:
    1. Gets the recording for the visit
    2. Extracts all data from the transcript
    3. Saves extracted data to prescription, diet_plan, care_instructions
    4. Updates visit with symptoms and vitals

    Returns the extraction result with confidence scores.
    """
    from sqlalchemy import select
    from app.models.visit import Visit
    from app.models.recording import Recording

    # Get the visit
    result = await db.execute(select(Visit).where(Visit.id == visit_id))
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visit {visit_id} not found",
        )

    # Get the recording for this visit
    recording_result = await db.execute(
        select(Recording).where(Recording.visit_id == visit_id)
    )
    recording = recording_result.scalar_one_or_none()

    if not recording or not recording.transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No transcript found for visit {visit_id}",
        )

    # Create extraction request
    request = ExtractionRequest(
        transcript=recording.transcript,
        visit_id=visit_id,
        language=recording.language or "en",
    )

    # Run extraction
    service = ExtractionService(db)
    extraction = await service.extract_all(request)

    # Save to database
    saved = await service.save_extraction_to_visit(visit_id, extraction)

    if not saved:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save extraction results",
        )

    return {
        "visit_id": str(visit_id),
        "extraction": extraction,
        "saved": True,
    }
