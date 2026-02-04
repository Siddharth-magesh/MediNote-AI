"""Integration tests for AI extraction API."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock


# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
Doctor: Good morning, how are you feeling today?

Patient: Good morning doctor. I'm not feeling well. I've had a headache for the past 3 days
and some fever too.

Doctor: I see. Can you tell me about the headache? Where exactly does it hurt?

Patient: It's mostly on the front of my head, and it's a throbbing pain. The pain is moderate
to severe, especially in the evenings.

Doctor: Are you taking any medications for it?

Patient: I took some Paracetamol yesterday but it didn't help much.

Doctor: Let me check your vitals. Your temperature is 101°F, blood pressure is 120/80, and
pulse is 82. Your weight is 70 kg and height is 175 cm.

Patient: My name is Rahul Sharma, I'm 35 years old. My phone number is 9876543210.

Doctor: Do you have any allergies?

Patient: Yes, I'm allergic to penicillin.

Doctor: Based on my examination, you seem to have a viral infection. I'm prescribing you
Paracetamol 500mg tablets, take one tablet twice daily after food for 5 days. Also take
Cetirizine 10mg once at night for the allergy symptoms.

For your diet, avoid spicy and oily food. Have light meals like khichdi, soup, and fruits.
Drink plenty of water, at least 8 glasses a day.

Get proper rest, sleep for at least 8 hours. Avoid screen time before bed. If you have
high fever above 103°F or the headache becomes severe, come back immediately.

Come back for a follow-up in one week if symptoms persist.
"""


@pytest.mark.asyncio
class TestFullExtraction:
    """Tests for full extraction endpoint."""

    async def test_extract_full_success(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test successful full extraction."""
        # Mock the LLM service to return predictable results
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        name="Rahul Sharma",
                        age=35,
                        gender="male",
                        weight_kg=70,
                        height_cm=175,
                        allergies=["penicillin"],
                    ),
                    0.9,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/full",
                json={
                    "transcript": SAMPLE_TRANSCRIPT,
                    "language": "en",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "confidence_scores" in data
        assert "requires_review" in data

    async def test_extract_full_short_transcript(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test extraction with too short transcript."""
        response = await authenticated_client.post(
            "/api/v1/extraction/full",
            json={
                "transcript": "Hi",
                "language": "en",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_extract_full_unauthorized(
        self,
        client: AsyncClient,
    ):
        """Test extraction without authentication."""
        response = await client.post(
            "/api/v1/extraction/full",
            json={
                "transcript": SAMPLE_TRANSCRIPT,
            },
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestBMICalculation:
    """Tests for BMI calculation endpoint."""

    async def test_calculate_bmi_normal(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation for normal weight."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=70&height_cm=175"
        )

        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert "category" in data
        assert data["category"] == "Normal"
        assert 22 < data["value"] < 24  # BMI for 70kg, 175cm

    async def test_calculate_bmi_underweight(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation for underweight."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=45&height_cm=175"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Underweight"

    async def test_calculate_bmi_overweight(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation for overweight."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=85&height_cm=175"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Overweight"

    async def test_calculate_bmi_obese(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation for obese."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=110&height_cm=175"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Obese"

    async def test_calculate_bmi_invalid_weight(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation with invalid weight."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=-10&height_cm=175"
        )

        assert response.status_code == 400

    async def test_calculate_bmi_invalid_height(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test BMI calculation with invalid height."""
        response = await authenticated_client.post(
            "/api/v1/extraction/bmi?weight_kg=70&height_cm=0"
        )

        assert response.status_code == 400


@pytest.mark.asyncio
class TestIndividualExtractions:
    """Tests for individual extraction endpoints."""

    async def test_extract_patient_details(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test patient details extraction."""
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        name="Test Patient",
                        age=30,
                        gender="male",
                        weight_kg=None,
                        height_cm=None,
                        allergies=None,
                        blood_group=None,
                        contact_number=None,
                        emergency_contact=None,
                    ),
                    0.85,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/patient-details",
                params={"transcript": SAMPLE_TRANSCRIPT},
            )

        assert response.status_code == 200

    async def test_extract_symptoms(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test symptoms extraction."""
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        chief_complaint="Headache and fever",
                        symptoms=[],
                        history_of_present_illness=None,
                    ),
                    0.8,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/symptoms",
                params={"transcript": SAMPLE_TRANSCRIPT},
            )

        assert response.status_code == 200

    async def test_extract_prescription(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test prescription extraction."""
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        medications=[],
                        injections=None,
                        investigations=None,
                        follow_up=None,
                    ),
                    0.75,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/prescription",
                params={"transcript": SAMPLE_TRANSCRIPT},
            )

        assert response.status_code == 200

    async def test_extract_diet_plan(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test diet plan extraction."""
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        breakfast=None,
                        lunch=None,
                        dinner=None,
                        snacks=None,
                        foods_to_avoid=["spicy food", "oily food"],
                        hydration_advice="8 glasses of water",
                        dietary_restrictions=None,
                    ),
                    0.7,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/diet-plan",
                params={"transcript": SAMPLE_TRANSCRIPT},
            )

        assert response.status_code == 200

    async def test_extract_care_instructions(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test care instructions extraction."""
        with patch("app.services.extraction.get_llm_service") as mock_llm:
            mock_service = MagicMock()
            mock_service.extract_json = AsyncMock(
                return_value=(
                    MagicMock(
                        lifestyle_recommendations=["Get proper rest"],
                        exercise_plan=None,
                        sleep_recommendations="8 hours",
                        stress_management=None,
                        warning_signs=["High fever above 103°F"],
                        when_to_seek_help=["If headache becomes severe"],
                        additional_notes=None,
                    ),
                    0.8,
                )
            )
            mock_llm.return_value = mock_service

            response = await authenticated_client.post(
                "/api/v1/extraction/care-instructions",
                params={"transcript": SAMPLE_TRANSCRIPT},
            )

        assert response.status_code == 200


@pytest.mark.asyncio
class TestExtractionWithVisit:
    """Tests for extraction with visit save."""

    async def test_extract_and_save_visit_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test extraction with non-existent visit."""
        response = await authenticated_client.post(
            "/api/v1/extraction/visit/00000000-0000-0000-0000-000000000000/extract"
        )

        assert response.status_code == 404
