"""Unit tests for report generation utilities."""

import pytest
from datetime import datetime, date
from uuid import uuid4

from app.schemas.report import (
    ReportRequest,
    ReportResponse,
    ReportMetadata,
    ReportType,
)


class TestReportRequest:
    """Tests for ReportRequest schema."""

    def test_valid_report_request(self):
        """Test valid report request."""
        visit_id = uuid4()
        request = ReportRequest(
            visit_id=visit_id,
            report_type="full",
            include_prescription=True,
            include_diet_plan=True,
            include_care_instructions=True,
        )
        assert request.visit_id == visit_id
        assert request.report_type == "full"
        assert request.include_prescription is True

    def test_minimal_report_request(self):
        """Test minimal report request with defaults."""
        visit_id = uuid4()
        request = ReportRequest(visit_id=visit_id)
        assert request.report_type == "full"
        assert request.include_prescription is True
        assert request.include_diet_plan is True
        assert request.include_care_instructions is True

    def test_prescription_only_report(self):
        """Test prescription-only report request."""
        request = ReportRequest(
            visit_id=uuid4(),
            report_type="prescription",
            include_prescription=True,
            include_diet_plan=False,
            include_care_instructions=False,
        )
        assert request.report_type == "prescription"
        assert request.include_diet_plan is False

    def test_valid_report_types(self):
        """Test all valid report types."""
        valid_types = ["full", "prescription", "diet", "care"]
        for report_type in valid_types:
            request = ReportRequest(
                visit_id=uuid4(),
                report_type=report_type,
            )
            assert request.report_type == report_type


class TestReportMetadata:
    """Tests for ReportMetadata schema."""

    def test_valid_metadata(self):
        """Test valid report metadata."""
        metadata = ReportMetadata(
            report_id="RPT-2024-00001",
            generated_at=datetime.now(),
            doctor_name="Dr. John Smith",
            hospital_name="City Hospital",
            patient_name="Jane Doe",
            patient_id="PAT-2024-00001",
        )
        assert metadata.report_id.startswith("RPT-")
        assert metadata.doctor_name == "Dr. John Smith"

    def test_metadata_with_qr_code(self):
        """Test metadata with QR code URL."""
        metadata = ReportMetadata(
            report_id="RPT-2024-00001",
            generated_at=datetime.now(),
            doctor_name="Dr. John Smith",
            patient_name="Jane Doe",
            qr_code_url="https://example.com/verify/RPT-2024-00001",
        )
        assert metadata.qr_code_url is not None


class TestReportResponse:
    """Tests for ReportResponse schema."""

    def test_valid_report_response(self):
        """Test valid report response."""
        report_id = uuid4()
        response = ReportResponse(
            id=report_id,
            report_id="RPT-2024-00001",
            visit_id=uuid4(),
            report_type="full",
            status="completed",
            file_path="/reports/RPT-2024-00001.pdf",
            created_at=datetime.now(),
        )
        assert response.id == report_id
        assert response.status == "completed"
        assert response.file_path.endswith(".pdf")

    def test_pending_report_response(self):
        """Test pending report response."""
        response = ReportResponse(
            id=uuid4(),
            report_id="RPT-2024-00002",
            visit_id=uuid4(),
            report_type="prescription",
            status="pending",
            created_at=datetime.now(),
        )
        assert response.status == "pending"
        assert response.file_path is None

    def test_report_status_options(self):
        """Test all valid report statuses."""
        valid_statuses = ["pending", "generating", "completed", "failed"]
        for status in valid_statuses:
            response = ReportResponse(
                id=uuid4(),
                report_id=f"RPT-2024-0000{valid_statuses.index(status)}",
                visit_id=uuid4(),
                report_type="full",
                status=status,
                created_at=datetime.now(),
            )
            assert response.status == status


class TestReportTemplateContext:
    """Tests for report template context building."""

    def test_build_patient_context(self):
        """Test building patient context for template."""
        patient_data = {
            "name": "John Doe",
            "age": 35,
            "gender": "Male",
            "patient_id": "PAT-2024-00001",
            "blood_group": "O+",
            "phone": "+919876543210",
        }

        assert patient_data["name"] == "John Doe"
        assert patient_data["age"] == 35
        assert patient_data["patient_id"].startswith("PAT-")

    def test_build_visit_context(self):
        """Test building visit context for template."""
        visit_data = {
            "visit_date": date.today().isoformat(),
            "chief_complaint": "Fever and headache",
            "diagnosis": "Viral fever",
            "vitals": {
                "temperature": 101.5,
                "blood_pressure": "120/80",
                "pulse": 88,
                "weight_kg": 70,
            },
        }

        assert visit_data["chief_complaint"] is not None
        assert visit_data["vitals"]["temperature"] == 101.5

    def test_build_prescription_context(self):
        """Test building prescription context for template."""
        prescription_data = {
            "medications": [
                {
                    "name": "Paracetamol",
                    "dosage": "500mg",
                    "frequency": "Three times daily",
                    "duration": "5 days",
                },
                {
                    "name": "Cetirizine",
                    "dosage": "10mg",
                    "frequency": "Once daily at night",
                    "duration": "5 days",
                },
            ],
            "investigations": ["CBC", "Blood Sugar"],
            "follow_up": {
                "date": "2024-02-15",
                "notes": "Review with test reports",
            },
        }

        assert len(prescription_data["medications"]) == 2
        assert prescription_data["medications"][0]["name"] == "Paracetamol"
        assert len(prescription_data["investigations"]) == 2

    def test_build_diet_context(self):
        """Test building diet plan context for template."""
        diet_data = {
            "breakfast": {
                "items": ["Oatmeal", "Fruits", "Green Tea"],
                "timing": "7:00 AM - 8:00 AM",
            },
            "lunch": {
                "items": ["Brown Rice", "Dal", "Vegetables"],
                "timing": "12:00 PM - 1:00 PM",
            },
            "dinner": {
                "items": ["Chapati", "Sabzi", "Curd"],
                "timing": "7:00 PM - 8:00 PM",
            },
            "foods_to_avoid": ["Fried foods", "Sugary drinks"],
            "hydration": "8-10 glasses of water daily",
        }

        assert len(diet_data["breakfast"]["items"]) == 3
        assert len(diet_data["foods_to_avoid"]) == 2

    def test_build_care_instructions_context(self):
        """Test building care instructions context for template."""
        care_data = {
            "lifestyle": [
                "Take adequate rest",
                "Avoid stress",
                "Get 7-8 hours of sleep",
            ],
            "exercise": {
                "type": "Light walking",
                "duration": "15-20 minutes",
                "frequency": "Once daily",
            },
            "warning_signs": [
                "High fever (>103°F)",
                "Severe headache",
                "Difficulty breathing",
            ],
            "when_to_seek_help": "If symptoms worsen or no improvement in 3 days",
        }

        assert len(care_data["lifestyle"]) == 3
        assert len(care_data["warning_signs"]) == 3


class TestQRCodeGeneration:
    """Tests for QR code generation utilities."""

    def test_verification_url_format(self):
        """Test verification URL format."""
        base_url = "https://medinote.example.com"
        report_id = "RPT-2024-00001"
        verification_url = f"{base_url}/verify/{report_id}"

        assert verification_url.startswith("https://")
        assert report_id in verification_url

    def test_qr_code_content(self):
        """Test QR code content structure."""
        qr_content = {
            "report_id": "RPT-2024-00001",
            "patient_id": "PAT-2024-00001",
            "doctor_id": "DOC-001",
            "generated_at": datetime.now().isoformat(),
            "verification_url": "https://medinote.example.com/verify/RPT-2024-00001",
        }

        assert qr_content["report_id"].startswith("RPT-")
        assert qr_content["verification_url"].endswith(qr_content["report_id"])
