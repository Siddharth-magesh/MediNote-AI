"""Unit tests for patient schemas and validation."""

import pytest
from pydantic import ValidationError

from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientAddress,
    EmergencyContact,
    PatientResponse,
)


class TestPatientAddress:
    """Tests for PatientAddress schema."""

    def test_valid_address(self):
        """Test valid address creation."""
        address = PatientAddress(
            street="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            country="India",
        )
        assert address.street == "123 Main Street"
        assert address.city == "Mumbai"

    def test_minimal_address(self):
        """Test address with only required fields."""
        address = PatientAddress(
            city="Mumbai",
            state="Maharashtra",
        )
        assert address.city == "Mumbai"
        assert address.street is None

    def test_all_optional_fields(self):
        """Test that all fields are optional."""
        address = PatientAddress()
        assert address.street is None
        assert address.city is None
        assert address.country is None


class TestEmergencyContact:
    """Tests for EmergencyContact schema."""

    def test_valid_emergency_contact(self):
        """Test valid emergency contact."""
        contact = EmergencyContact(
            name="Jane Doe",
            relation="Spouse",
            phone="+919876543210",
        )
        assert contact.name == "Jane Doe"
        assert contact.relation == "Spouse"

    def test_partial_emergency_contact(self):
        """Test partial emergency contact."""
        contact = EmergencyContact(
            name="John Doe",
        )
        assert contact.name == "John Doe"
        assert contact.relation is None
        assert contact.phone is None


class TestPatientCreate:
    """Tests for PatientCreate schema."""

    def test_valid_patient_create(self):
        """Test valid patient creation."""
        data = PatientCreate(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-05-15",
            gender="male",
            phone_primary="+919876543210",
            email="john@example.com",
        )
        assert data.first_name == "John"
        assert data.last_name == "Doe"
        assert data.gender == "male"

    def test_minimal_patient_create(self):
        """Test patient creation with minimal required fields."""
        data = PatientCreate(
            first_name="John",
            last_name="Doe",
            gender="male",
            phone_primary="+919876543210",
        )
        assert data.first_name == "John"
        assert data.date_of_birth is None
        assert data.email is None

    def test_patient_with_address(self):
        """Test patient creation with address."""
        data = PatientCreate(
            first_name="John",
            last_name="Doe",
            gender="male",
            phone_primary="+919876543210",
            address=PatientAddress(
                city="Mumbai",
                state="Maharashtra",
            ),
        )
        assert data.address.city == "Mumbai"

    def test_patient_with_emergency_contact(self):
        """Test patient creation with emergency contact."""
        data = PatientCreate(
            first_name="John",
            last_name="Doe",
            gender="male",
            phone_primary="+919876543210",
            emergency_contact=EmergencyContact(
                name="Jane Doe",
                relation="Spouse",
                phone="+919876543211",
            ),
        )
        assert data.emergency_contact.name == "Jane Doe"

    def test_valid_genders(self):
        """Test all valid gender options."""
        for gender in ["male", "female", "other"]:
            data = PatientCreate(
                first_name="Test",
                last_name="User",
                gender=gender,
                phone_primary="+919876543210",
            )
            assert data.gender == gender

    def test_blood_groups(self):
        """Test valid blood group options."""
        valid_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        for blood_group in valid_groups:
            data = PatientCreate(
                first_name="Test",
                last_name="User",
                gender="male",
                phone_primary="+919876543210",
                blood_group=blood_group,
            )
            assert data.blood_group == blood_group

    def test_medical_history_fields(self):
        """Test medical history fields."""
        data = PatientCreate(
            first_name="John",
            last_name="Doe",
            gender="male",
            phone_primary="+919876543210",
            allergies=["Penicillin", "Peanuts"],
            chronic_conditions=["Diabetes", "Hypertension"],
            current_medications=["Metformin", "Lisinopril"],
        )
        assert len(data.allergies) == 2
        assert "Diabetes" in data.chronic_conditions
        assert len(data.current_medications) == 2

    def test_missing_required_fields(self):
        """Test validation error on missing required fields."""
        with pytest.raises(ValidationError):
            PatientCreate(
                first_name="John",
                # Missing last_name, gender, phone_primary
            )


class TestPatientUpdate:
    """Tests for PatientUpdate schema."""

    def test_partial_update(self):
        """Test partial patient update."""
        data = PatientUpdate(
            first_name="Jane",
        )
        assert data.first_name == "Jane"
        assert data.last_name is None

    def test_update_multiple_fields(self):
        """Test updating multiple fields."""
        data = PatientUpdate(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
        )
        assert data.first_name == "Jane"
        assert data.last_name == "Smith"
        assert data.email == "jane.smith@example.com"

    def test_update_with_address(self):
        """Test updating address."""
        data = PatientUpdate(
            address=PatientAddress(
                city="Delhi",
                state="Delhi",
            ),
        )
        assert data.address.city == "Delhi"

    def test_update_status(self):
        """Test updating patient status."""
        for status in ["active", "inactive", "archived"]:
            data = PatientUpdate(status=status)
            assert data.status == status

    def test_empty_update(self):
        """Test empty update (all None)."""
        data = PatientUpdate()
        assert data.first_name is None
        assert data.last_name is None
        assert data.address is None


class TestPatientResponse:
    """Tests for PatientResponse schema."""

    def test_full_patient_response(self):
        """Test full patient response."""
        from datetime import datetime
        from uuid import uuid4

        patient_id = uuid4()
        data = PatientResponse(
            id=patient_id,
            patient_id="PAT-2024-00001",
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-05-15",
            gender="male",
            phone_primary="+919876543210",
            email="john@example.com",
            blood_group="O+",
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert str(data.id) == str(patient_id)
        assert data.patient_id.startswith("PAT-")
        assert data.status == "active"

    def test_patient_response_with_nested_objects(self):
        """Test patient response with address and emergency contact."""
        from datetime import datetime
        from uuid import uuid4

        data = PatientResponse(
            id=uuid4(),
            patient_id="PAT-2024-00002",
            first_name="Jane",
            last_name="Doe",
            gender="female",
            phone_primary="+919876543210",
            status="active",
            created_at=datetime.now(),
            address={
                "city": "Mumbai",
                "state": "Maharashtra",
            },
            emergency_contact={
                "name": "John Doe",
                "relation": "Spouse",
            },
        )
        assert data.address["city"] == "Mumbai"
        assert data.emergency_contact["name"] == "John Doe"
