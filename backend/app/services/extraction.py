"""AI extraction service for extracting structured medical data from transcripts."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.care_instructions import CareInstructions
from app.models.diet_plan import DietPlan
from app.models.prescription import Prescription
from app.models.visit import Visit
from app.schemas.extraction import (
    BMIResult,
    CareInstructionsExtracted,
    ConfidenceScores,
    DietPlanExtracted,
    ExtractionRequest,
    ExtractionResponse,
    PatientDetailsExtracted,
    PrescriptionExtracted,
    SymptomsExtracted,
    VitalsExtracted,
)
from app.services.llm import get_llm_service


# ============================================================================
# Prompt Templates
# ============================================================================

PATIENT_DETAILS_PROMPT = """Extract patient details from the following doctor-patient conversation.

Return a JSON object with these fields:
- name: Patient's full name (string or null)
- age: Patient's age in years (integer or null)
- gender: "male", "female", or "other" (or null)
- blood_group: Blood group - A+, A-, B+, B-, O+, O-, AB+, AB- (or null)
- weight_kg: Weight in kilograms (number or null)
- height_cm: Height in centimeters (number or null)
- contact_number: Phone number (string or null)
- allergies: List of known allergies (array of strings or null)
- emergency_contact: Object with name, relation, phone (or null)

Only include information that is explicitly mentioned. Use null for unknown fields.

Conversation:
{transcript}"""

SYMPTOMS_PROMPT = """Extract symptoms and complaints from the following doctor-patient conversation.

Return a JSON object with:
- chief_complaint: The main reason for the visit (string or null)
- symptoms: Array of symptom objects, each with:
  - description: What the symptom is (required string)
  - duration: How long they've had it (string or null)
  - severity: "mild", "moderate", or "severe" (or null)
  - location: Body part affected (string or null)
  - aggravating_factors: What makes it worse (array or null)
  - relieving_factors: What makes it better (array or null)
- history_of_present_illness: Summary of the illness history (string or null)

Only include information explicitly mentioned in the conversation.

Conversation:
{transcript}"""

PRESCRIPTION_PROMPT = """Extract prescription details from the following doctor-patient conversation.

Return a JSON object with:
- medications: Array of prescribed medicines, each with:
  - name: Medicine name (required string)
  - type: "tablet", "capsule", "syrup", "injection", "topical", or "other" (or null)
  - dosage: Amount per dose like "500mg" or "10ml" (string or null)
  - frequency: How often like "twice daily" (string or null)
  - timing: "morning", "afternoon", "evening", "night", or "as_needed" (or null)
  - relation_to_food: "before", "after", "with", or "any" (or null)
  - duration_days: Number of days to take (integer or null)
  - special_instructions: Any special notes (string or null)

- injections: Array of injections, each with:
  - name: Injection name (required string)
  - dosage: Amount (string or null)
  - frequency: How often (string or null)
  - route: "IM", "IV", or "SC" (or null)
  - duration: How long (string or null)

- investigations: Array of tests/labs ordered (array of strings or null)

- follow_up: Object with:
  - duration: When to return like "2 weeks" (string or null)
  - date: Specific date if mentioned in YYYY-MM-DD format (string or null)
  - notes: Any follow-up notes (string or null)

Only include explicitly mentioned information.

Conversation:
{transcript}"""

DIET_PLAN_PROMPT = """Extract diet plan from the following doctor-patient conversation.

Return a JSON object with:
- breakfast: Object with items (array), timing (string), portion_guidance (string) - or null
- lunch: Object with items (array), timing (string), portion_guidance (string) - or null
- dinner: Object with items (array), timing (string), portion_guidance (string) - or null
- snacks: Object with items (array), timing (string) - or null
- foods_to_avoid: Array of foods to avoid (array of strings or null)
- hydration_advice: Water/fluid recommendations (string or null)
- dietary_restrictions: Any dietary restrictions (array of strings or null)

Only include diet information that was explicitly discussed.

Conversation:
{transcript}"""

CARE_INSTRUCTIONS_PROMPT = """Extract care instructions and lifestyle recommendations from the following conversation.

Return a JSON object with:
- lifestyle_recommendations: General lifestyle advice (array of strings or null)
- exercise_plan: Object with:
  - type: Types of exercise (array of strings or null)
  - frequency: How often (string or null)
  - duration: How long per session (string or null)
  - precautions: Exercise precautions (array of strings or null)
- sleep_recommendations: Sleep advice (string or null)
- stress_management: Stress management tips (string or null)
- warning_signs: Symptoms to watch for (array of strings or null)
- when_to_seek_help: When to come back or go to hospital (array of strings or null)
- additional_notes: Any other care notes (string or null)

Only include information explicitly mentioned.

Conversation:
{transcript}"""

VITALS_PROMPT = """Extract vital signs from the following doctor-patient conversation.

Return a JSON object with:
- weight_kg: Weight in kilograms (number or null)
- height_cm: Height in centimeters (number or null)
- blood_pressure: Blood pressure like "120/80" (string or null)
- pulse: Heart rate in beats per minute (integer or null)
- temperature: Temperature in Fahrenheit or Celsius (number or null)
- spo2: Oxygen saturation percentage (integer or null)

Only include vitals that were explicitly mentioned.

Conversation:
{transcript}"""


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_bmi(weight_kg: float, height_cm: float) -> BMIResult:
    """Calculate BMI and determine category."""
    height_m = height_cm / 100
    bmi_value = weight_kg / (height_m ** 2)

    if bmi_value < 18.5:
        category = "Underweight"
    elif bmi_value < 25:
        category = "Normal"
    elif bmi_value < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return BMIResult(value=round(bmi_value, 2), category=category)


# ============================================================================
# Extraction Service
# ============================================================================

class ExtractionService:
    """Service for AI-powered data extraction from transcripts."""

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.llm = get_llm_service()

    async def extract_all(
        self,
        request: ExtractionRequest,
    ) -> ExtractionResponse:
        """Extract all data from a transcript."""
        confidence_scores = ConfidenceScores()
        review_reasons = []

        # Extract patient details
        patient_details = None
        if request.extract_patient_details:
            patient_details, conf = await self._extract_patient_details(
                request.transcript
            )
            confidence_scores.patient_details = conf
            if conf < 0.7:
                review_reasons.append("Low confidence in patient details extraction")

        # Extract symptoms
        symptoms = None
        if request.extract_symptoms:
            symptoms, conf = await self._extract_symptoms(request.transcript)
            confidence_scores.symptoms = conf
            if conf < 0.7:
                review_reasons.append("Low confidence in symptoms extraction")

        # Extract prescription
        prescription = None
        if request.extract_prescription:
            prescription, conf = await self._extract_prescription(request.transcript)
            confidence_scores.prescription = conf
            if conf < 0.7:
                review_reasons.append("Low confidence in prescription extraction")

        # Extract diet plan
        diet_plan = None
        if request.extract_diet_plan:
            diet_plan, conf = await self._extract_diet_plan(request.transcript)
            confidence_scores.diet_plan = conf
            if conf < 0.7:
                review_reasons.append("Low confidence in diet plan extraction")

        # Extract care instructions
        care_instructions = None
        if request.extract_care_instructions:
            care_instructions, conf = await self._extract_care_instructions(
                request.transcript
            )
            confidence_scores.care_instructions = conf
            if conf < 0.7:
                review_reasons.append("Low confidence in care instructions extraction")

        # Calculate BMI if we have weight and height
        bmi = None
        if patient_details and patient_details.weight_kg and patient_details.height_cm:
            bmi = calculate_bmi(patient_details.weight_kg, patient_details.height_cm)

        # Calculate overall confidence
        scores = [
            confidence_scores.patient_details,
            confidence_scores.symptoms,
            confidence_scores.prescription,
            confidence_scores.diet_plan,
            confidence_scores.care_instructions,
        ]
        non_zero_scores = [s for s in scores if s > 0]
        confidence_scores.overall = (
            sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.0
        )

        # Determine if review is required
        requires_review = confidence_scores.overall < 0.7 or len(review_reasons) > 2

        return ExtractionResponse(
            patient_details=patient_details,
            symptoms=symptoms,
            prescription=prescription,
            diet_plan=diet_plan,
            care_instructions=care_instructions,
            bmi=bmi,
            confidence_scores=confidence_scores,
            requires_review=requires_review,
            review_reasons=review_reasons if review_reasons else None,
        )

    async def _extract_patient_details(
        self, transcript: str
    ) -> tuple[Optional[PatientDetailsExtracted], float]:
        """Extract patient details from transcript."""
        prompt = PATIENT_DETAILS_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, PatientDetailsExtracted)

    async def _extract_symptoms(
        self, transcript: str
    ) -> tuple[Optional[SymptomsExtracted], float]:
        """Extract symptoms from transcript."""
        prompt = SYMPTOMS_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, SymptomsExtracted)

    async def _extract_prescription(
        self, transcript: str
    ) -> tuple[Optional[PrescriptionExtracted], float]:
        """Extract prescription from transcript."""
        prompt = PRESCRIPTION_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, PrescriptionExtracted)

    async def _extract_diet_plan(
        self, transcript: str
    ) -> tuple[Optional[DietPlanExtracted], float]:
        """Extract diet plan from transcript."""
        prompt = DIET_PLAN_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, DietPlanExtracted)

    async def _extract_care_instructions(
        self, transcript: str
    ) -> tuple[Optional[CareInstructionsExtracted], float]:
        """Extract care instructions from transcript."""
        prompt = CARE_INSTRUCTIONS_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, CareInstructionsExtracted)

    async def _extract_vitals(
        self, transcript: str
    ) -> tuple[Optional[VitalsExtracted], float]:
        """Extract vitals from transcript."""
        prompt = VITALS_PROMPT.format(transcript=transcript)
        return await self.llm.extract_json(prompt, VitalsExtracted)

    async def save_extraction_to_visit(
        self,
        visit_id: UUID,
        extraction: ExtractionResponse,
    ) -> bool:
        """Save extracted data to visit-related models."""
        if not self.db:
            return False

        from sqlalchemy import select

        # Get the visit
        result = await self.db.execute(
            select(Visit).where(Visit.id == visit_id)
        )
        visit = result.scalar_one_or_none()
        if not visit:
            return False

        # Update visit with symptoms
        if extraction.symptoms:
            if extraction.symptoms.chief_complaint:
                visit.chief_complaint = extraction.symptoms.chief_complaint
            if extraction.symptoms.symptoms:
                visit.symptoms = [s.model_dump() for s in extraction.symptoms.symptoms]

        # Update visit vitals if we have patient details
        if extraction.patient_details:
            vitals = visit.vitals or {}
            if extraction.patient_details.weight_kg:
                vitals["weight_kg"] = extraction.patient_details.weight_kg
            if extraction.patient_details.height_cm:
                vitals["height_cm"] = extraction.patient_details.height_cm
            if extraction.bmi:
                vitals["bmi"] = extraction.bmi.value
            if vitals:
                visit.vitals = vitals

        # Create or update prescription
        if extraction.prescription:
            existing_prescription = await self.db.execute(
                select(Prescription).where(Prescription.visit_id == visit_id)
            )
            prescription = existing_prescription.scalar_one_or_none()

            if not prescription:
                prescription = Prescription(visit_id=visit_id)
                self.db.add(prescription)

            if extraction.prescription.medications:
                prescription.medications = [
                    m.model_dump() for m in extraction.prescription.medications
                ]
            if extraction.prescription.injections:
                prescription.injections = [
                    i.model_dump() for i in extraction.prescription.injections
                ]
            if extraction.prescription.investigations:
                prescription.investigations = extraction.prescription.investigations
            if extraction.prescription.follow_up:
                prescription.follow_up_date = extraction.prescription.follow_up.date
                prescription.follow_up_notes = extraction.prescription.follow_up.notes

        # Create or update diet plan
        if extraction.diet_plan:
            existing_diet = await self.db.execute(
                select(DietPlan).where(DietPlan.visit_id == visit_id)
            )
            diet_plan = existing_diet.scalar_one_or_none()

            if not diet_plan:
                diet_plan = DietPlan(visit_id=visit_id)
                self.db.add(diet_plan)

            if extraction.diet_plan.breakfast:
                diet_plan.breakfast = extraction.diet_plan.breakfast.model_dump()
            if extraction.diet_plan.lunch:
                diet_plan.lunch = extraction.diet_plan.lunch.model_dump()
            if extraction.diet_plan.dinner:
                diet_plan.dinner = extraction.diet_plan.dinner.model_dump()
            if extraction.diet_plan.snacks:
                diet_plan.snacks = extraction.diet_plan.snacks.model_dump()
            if extraction.diet_plan.foods_to_avoid:
                diet_plan.foods_to_avoid = extraction.diet_plan.foods_to_avoid
            if extraction.diet_plan.hydration_advice:
                diet_plan.hydration_advice = extraction.diet_plan.hydration_advice
            if extraction.diet_plan.dietary_restrictions:
                diet_plan.dietary_restrictions = extraction.diet_plan.dietary_restrictions

        # Create or update care instructions
        if extraction.care_instructions:
            existing_care = await self.db.execute(
                select(CareInstructions).where(CareInstructions.visit_id == visit_id)
            )
            care_instructions = existing_care.scalar_one_or_none()

            if not care_instructions:
                care_instructions = CareInstructions(visit_id=visit_id)
                self.db.add(care_instructions)

            if extraction.care_instructions.lifestyle_recommendations:
                care_instructions.lifestyle_recommendations = (
                    extraction.care_instructions.lifestyle_recommendations
                )
            if extraction.care_instructions.exercise_plan:
                care_instructions.exercise_plan = (
                    extraction.care_instructions.exercise_plan.model_dump()
                )
            if extraction.care_instructions.sleep_recommendations:
                care_instructions.sleep_recommendations = (
                    extraction.care_instructions.sleep_recommendations
                )
            if extraction.care_instructions.stress_management:
                care_instructions.stress_management = (
                    extraction.care_instructions.stress_management
                )
            if extraction.care_instructions.warning_signs:
                care_instructions.warning_signs = (
                    extraction.care_instructions.warning_signs
                )
            if extraction.care_instructions.when_to_seek_help:
                care_instructions.when_to_seek_help = (
                    extraction.care_instructions.when_to_seek_help
                )
            if extraction.care_instructions.additional_notes:
                care_instructions.additional_notes = (
                    extraction.care_instructions.additional_notes
                )

        await self.db.commit()
        return True
