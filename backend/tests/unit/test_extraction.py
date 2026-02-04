"""Unit tests for extraction service and utilities."""

import pytest

from app.schemas.extraction import (
    BMIResult,
    PatientDetailsExtracted,
    SymptomsExtracted,
    PrescriptionExtracted,
    DietPlanExtracted,
    CareInstructionsExtracted,
    MedicationExtracted,
    SymptomItem,
    FollowUp,
    MealPlan,
    ExercisePlan,
    ExtractionRequest,
    ConfidenceScores,
)
from app.services.extraction import calculate_bmi


class TestBMICalculation:
    """Tests for BMI calculation."""

    def test_underweight_bmi(self):
        """Test BMI calculation for underweight category."""
        result = calculate_bmi(weight_kg=45, height_cm=170)
        assert result.category == "Underweight"
        assert result.value < 18.5
        assert round(result.value, 2) == 15.57

    def test_normal_bmi(self):
        """Test BMI calculation for normal category."""
        result = calculate_bmi(weight_kg=70, height_cm=175)
        assert result.category == "Normal"
        assert 18.5 <= result.value < 25
        assert round(result.value, 2) == 22.86

    def test_overweight_bmi(self):
        """Test BMI calculation for overweight category."""
        result = calculate_bmi(weight_kg=85, height_cm=175)
        assert result.category == "Overweight"
        assert 25 <= result.value < 30
        assert round(result.value, 2) == 27.76

    def test_obese_bmi(self):
        """Test BMI calculation for obese category."""
        result = calculate_bmi(weight_kg=100, height_cm=165)
        assert result.category == "Obese"
        assert result.value >= 30
        assert round(result.value, 2) == 36.73

    def test_bmi_edge_cases(self):
        """Test BMI at category boundaries."""
        # Exactly at normal lower boundary
        result = calculate_bmi(weight_kg=53.5, height_cm=170)
        assert result.value >= 18.5

        # At overweight boundary
        result = calculate_bmi(weight_kg=72.25, height_cm=170)
        assert result.value >= 25


class TestPatientDetailsSchema:
    """Tests for PatientDetailsExtracted schema."""

    def test_valid_patient_details(self):
        """Test valid patient details."""
        data = PatientDetailsExtracted(
            name="John Doe",
            age=35,
            gender="male",
            blood_group="O+",
            weight_kg=75.5,
            height_cm=180,
            contact_number="+919876543210",
            allergies=["Penicillin", "Dust"],
        )
        assert data.name == "John Doe"
        assert data.age == 35
        assert data.gender == "male"
        assert len(data.allergies) == 2

    def test_all_optional_fields(self):
        """Test that all fields are truly optional."""
        data = PatientDetailsExtracted()
        assert data.name is None
        assert data.age is None
        assert data.gender is None
        assert data.blood_group is None
        assert data.weight_kg is None
        assert data.height_cm is None

    def test_emergency_contact(self):
        """Test emergency contact nested object."""
        data = PatientDetailsExtracted(
            name="Jane Doe",
            emergency_contact={
                "name": "John Doe",
                "relation": "Spouse",
                "phone": "+919876543210"
            }
        )
        assert data.emergency_contact["name"] == "John Doe"


class TestSymptomsSchema:
    """Tests for SymptomsExtracted schema."""

    def test_valid_symptoms(self):
        """Test valid symptoms extraction."""
        data = SymptomsExtracted(
            chief_complaint="Fever and headache for 3 days",
            symptoms=[
                SymptomItem(
                    description="Fever",
                    duration="3 days",
                    severity="moderate",
                ),
                SymptomItem(
                    description="Headache",
                    severity="mild",
                    location="frontal",
                ),
            ],
            history_of_present_illness="Patient developed fever 3 days ago",
        )
        assert len(data.symptoms) == 2
        assert data.symptoms[0].description == "Fever"
        assert data.symptoms[1].location == "frontal"

    def test_symptom_aggravating_factors(self):
        """Test symptom with aggravating and relieving factors."""
        symptom = SymptomItem(
            description="Lower back pain",
            severity="severe",
            aggravating_factors=["Bending", "Lifting"],
            relieving_factors=["Rest", "Hot compress"],
        )
        assert len(symptom.aggravating_factors) == 2
        assert "Rest" in symptom.relieving_factors


class TestPrescriptionSchema:
    """Tests for PrescriptionExtracted schema."""

    def test_valid_prescription(self):
        """Test valid prescription extraction."""
        data = PrescriptionExtracted(
            medications=[
                MedicationExtracted(
                    name="Paracetamol",
                    type="tablet",
                    dosage="500mg",
                    frequency="three times daily",
                    timing="morning",
                    relation_to_food="after",
                    duration_days=5,
                ),
                MedicationExtracted(
                    name="Cough Syrup",
                    type="syrup",
                    dosage="10ml",
                    frequency="twice daily",
                ),
            ],
            investigations=["CBC", "Blood Sugar", "X-Ray Chest"],
            follow_up=FollowUp(
                duration="1 week",
                notes="Review with test reports",
            ),
        )
        assert len(data.medications) == 2
        assert data.medications[0].duration_days == 5
        assert len(data.investigations) == 3
        assert data.follow_up.duration == "1 week"

    def test_medication_types(self):
        """Test all medication types."""
        valid_types = ["tablet", "capsule", "syrup", "injection", "topical", "other"]
        for med_type in valid_types:
            med = MedicationExtracted(name="Test Med", type=med_type)
            assert med.type == med_type

    def test_injection_extraction(self):
        """Test injection extraction."""
        data = PrescriptionExtracted(
            injections=[
                {
                    "name": "Vitamin B12",
                    "dosage": "1000mcg",
                    "frequency": "weekly",
                    "route": "IM",
                    "duration": "4 weeks",
                }
            ]
        )
        assert len(data.injections) == 1
        assert data.injections[0]["route"] == "IM"


class TestDietPlanSchema:
    """Tests for DietPlanExtracted schema."""

    def test_valid_diet_plan(self):
        """Test valid diet plan extraction."""
        data = DietPlanExtracted(
            breakfast=MealPlan(
                items=["Oatmeal", "Fruits", "Green Tea"],
                timing="7:00 AM - 8:00 AM",
                portion_guidance="Light meal",
            ),
            lunch=MealPlan(
                items=["Brown Rice", "Dal", "Vegetables"],
                timing="12:00 PM - 1:00 PM",
            ),
            foods_to_avoid=["Fried foods", "Sugary drinks", "Red meat"],
            hydration_advice="Drink 8-10 glasses of water daily",
            dietary_restrictions=["Low sodium", "Low sugar"],
        )
        assert len(data.breakfast.items) == 3
        assert len(data.foods_to_avoid) == 3
        assert data.hydration_advice is not None

    def test_snacks_plan(self):
        """Test snacks extraction."""
        data = DietPlanExtracted(
            snacks=MealPlan(
                items=["Nuts", "Fruits"],
                timing="4:00 PM",
            )
        )
        assert data.snacks.timing == "4:00 PM"


class TestCareInstructionsSchema:
    """Tests for CareInstructionsExtracted schema."""

    def test_valid_care_instructions(self):
        """Test valid care instructions extraction."""
        data = CareInstructionsExtracted(
            lifestyle_recommendations=[
                "Avoid stress",
                "Get adequate sleep",
                "Regular exercise",
            ],
            exercise_plan=ExercisePlan(
                type=["Walking", "Yoga"],
                frequency="Daily",
                duration="30 minutes",
                precautions=["Avoid strenuous activities"],
            ),
            sleep_recommendations="7-8 hours of sleep daily",
            stress_management="Practice meditation",
            warning_signs=["High fever", "Severe pain", "Difficulty breathing"],
            when_to_seek_help=["If symptoms worsen", "If no improvement in 3 days"],
        )
        assert len(data.lifestyle_recommendations) == 3
        assert len(data.exercise_plan.type) == 2
        assert len(data.warning_signs) == 3

    def test_minimal_care_instructions(self):
        """Test minimal care instructions."""
        data = CareInstructionsExtracted(
            additional_notes="Take rest and stay hydrated",
        )
        assert data.additional_notes is not None
        assert data.lifestyle_recommendations is None


class TestExtractionRequest:
    """Tests for ExtractionRequest schema."""

    def test_default_extraction_flags(self):
        """Test default extraction flags are all True."""
        request = ExtractionRequest(transcript="Sample transcript")
        assert request.extract_patient_details is True
        assert request.extract_symptoms is True
        assert request.extract_prescription is True
        assert request.extract_diet_plan is True
        assert request.extract_care_instructions is True

    def test_selective_extraction(self):
        """Test selective extraction."""
        request = ExtractionRequest(
            transcript="Sample transcript",
            extract_patient_details=True,
            extract_prescription=True,
            extract_symptoms=False,
            extract_diet_plan=False,
            extract_care_instructions=False,
        )
        assert request.extract_symptoms is False
        assert request.extract_diet_plan is False


class TestConfidenceScores:
    """Tests for ConfidenceScores schema."""

    def test_default_confidence_scores(self):
        """Test default confidence scores are 0."""
        scores = ConfidenceScores()
        assert scores.patient_details == 0.0
        assert scores.symptoms == 0.0
        assert scores.prescription == 0.0
        assert scores.overall == 0.0

    def test_confidence_score_range(self):
        """Test confidence scores within valid range."""
        scores = ConfidenceScores(
            patient_details=0.95,
            symptoms=0.87,
            prescription=0.92,
            diet_plan=0.75,
            care_instructions=0.88,
            overall=0.87,
        )
        assert all(0 <= score <= 1 for score in [
            scores.patient_details,
            scores.symptoms,
            scores.prescription,
            scores.diet_plan,
            scores.care_instructions,
            scores.overall,
        ])
