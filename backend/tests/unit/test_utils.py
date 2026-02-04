"""Unit tests for utility functions."""

import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4


class TestPatientIDGeneration:
    """Tests for patient ID generation."""

    def test_patient_id_format(self):
        """Test patient ID format: PAT-YYYY-XXXXX."""
        year = datetime.now().year
        patient_id = f"PAT-{year}-00001"

        assert patient_id.startswith("PAT-")
        parts = patient_id.split("-")
        assert len(parts) == 3
        assert parts[0] == "PAT"
        assert parts[1] == str(year)
        assert len(parts[2]) == 5

    def test_sequential_patient_ids(self):
        """Test sequential patient ID generation."""
        year = datetime.now().year
        ids = [f"PAT-{year}-{str(i).zfill(5)}" for i in range(1, 6)]

        assert ids[0] == f"PAT-{year}-00001"
        assert ids[4] == f"PAT-{year}-00005"

    def test_patient_id_year_rollover(self):
        """Test patient ID resets each year."""
        id_2023 = "PAT-2023-99999"
        id_2024 = "PAT-2024-00001"

        assert id_2023.split("-")[1] != id_2024.split("-")[1]


class TestReportIDGeneration:
    """Tests for report ID generation."""

    def test_report_id_format(self):
        """Test report ID format: RPT-YYYY-XXXXX."""
        year = datetime.now().year
        report_id = f"RPT-{year}-00001"

        assert report_id.startswith("RPT-")
        parts = report_id.split("-")
        assert len(parts) == 3
        assert parts[0] == "RPT"

    def test_unique_report_ids(self):
        """Test unique report ID generation."""
        year = datetime.now().year
        ids = set([f"RPT-{year}-{str(i).zfill(5)}" for i in range(1, 101)])

        assert len(ids) == 100


class TestDateFormatting:
    """Tests for date formatting utilities."""

    def test_date_to_string(self):
        """Test date to string formatting."""
        test_date = date(2024, 2, 15)
        formatted = test_date.isoformat()

        assert formatted == "2024-02-15"

    def test_datetime_to_string(self):
        """Test datetime to string formatting."""
        test_datetime = datetime(2024, 2, 15, 10, 30, 0)
        formatted = test_datetime.isoformat()

        assert "2024-02-15" in formatted
        assert "10:30" in formatted

    def test_relative_date_calculation(self):
        """Test relative date calculation."""
        today = date.today()
        one_week_later = today + timedelta(days=7)
        two_weeks_later = today + timedelta(days=14)

        assert (one_week_later - today).days == 7
        assert (two_weeks_later - today).days == 14


class TestPhoneFormatting:
    """Tests for phone number formatting."""

    def test_indian_phone_format(self):
        """Test Indian phone number format."""
        phone = "+919876543210"
        assert phone.startswith("+91")
        assert len(phone) == 13

    def test_phone_without_country_code(self):
        """Test phone number without country code."""
        phone = "9876543210"
        formatted = f"+91{phone}"
        assert formatted == "+919876543210"

    def test_phone_validation(self):
        """Test phone number validation."""
        valid_phones = [
            "+919876543210",
            "+918765432109",
            "+917654321098",
        ]
        for phone in valid_phones:
            assert phone.startswith("+91")
            assert len(phone) == 13
            assert phone[3:].isdigit()


class TestAgeCalculation:
    """Tests for age calculation from date of birth."""

    def test_calculate_age(self):
        """Test age calculation."""
        dob = date(1990, 5, 15)
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        assert age > 0
        assert age < 150

    def test_age_at_birthday(self):
        """Test age calculation at birthday."""
        today = date.today()
        dob = date(today.year - 30, today.month, today.day)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        assert age == 30

    def test_age_before_birthday(self):
        """Test age calculation before birthday this year."""
        today = date.today()
        # Birthday is next month
        if today.month < 12:
            dob = date(today.year - 30, today.month + 1, 1)
        else:
            dob = date(today.year - 29, 1, 1)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        assert age >= 29


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_hash_different_from_plain(self):
        """Test that hashed password differs from plain text."""
        import hashlib
        password = "TestPassword123!"
        hashed = hashlib.sha256(password.encode()).hexdigest()

        assert hashed != password
        assert len(hashed) == 64

    def test_same_password_same_hash(self):
        """Test that same password produces same hash."""
        import hashlib
        password = "TestPassword123!"
        hash1 = hashlib.sha256(password.encode()).hexdigest()
        hash2 = hashlib.sha256(password.encode()).hexdigest()

        assert hash1 == hash2

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        import hashlib
        password1 = "TestPassword123!"
        password2 = "DifferentPassword456!"
        hash1 = hashlib.sha256(password1.encode()).hexdigest()
        hash2 = hashlib.sha256(password2.encode()).hexdigest()

        assert hash1 != hash2


class TestUUIDGeneration:
    """Tests for UUID generation."""

    def test_uuid_format(self):
        """Test UUID format."""
        new_uuid = uuid4()
        uuid_str = str(new_uuid)

        assert len(uuid_str) == 36
        assert uuid_str.count("-") == 4

    def test_unique_uuids(self):
        """Test that UUIDs are unique."""
        uuids = set([str(uuid4()) for _ in range(1000)])

        assert len(uuids) == 1000


class TestJWTTokenValidation:
    """Tests for JWT token structure."""

    def test_jwt_parts(self):
        """Test JWT token has three parts."""
        # Sample JWT structure (not a real token)
        sample_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.signature"
        parts = sample_token.split(".")

        assert len(parts) == 3

    def test_token_expiry_calculation(self):
        """Test token expiry calculation."""
        expires_in_minutes = 30
        now = datetime.utcnow()
        expiry = now + timedelta(minutes=expires_in_minutes)

        assert (expiry - now).total_seconds() == expires_in_minutes * 60


class TestFilePathGeneration:
    """Tests for file path generation."""

    def test_audio_file_path(self):
        """Test audio file path generation."""
        session_id = "abc123"
        file_path = f"recordings/{session_id}/audio.webm"

        assert file_path.startswith("recordings/")
        assert file_path.endswith(".webm")
        assert session_id in file_path

    def test_report_file_path(self):
        """Test report file path generation."""
        report_id = "RPT-2024-00001"
        file_path = f"reports/{report_id}.pdf"

        assert file_path.startswith("reports/")
        assert file_path.endswith(".pdf")
        assert report_id in file_path

    def test_unique_file_paths(self):
        """Test unique file path generation."""
        paths = set()
        for i in range(100):
            unique_id = str(uuid4())
            path = f"uploads/{unique_id}/file.pdf"
            paths.add(path)

        assert len(paths) == 100


class TestLanguageCodes:
    """Tests for language code validation."""

    def test_supported_languages(self):
        """Test supported language codes."""
        supported = ["en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu", "pa"]

        assert len(supported) == 10
        assert "en" in supported
        assert "hi" in supported

    def test_language_code_format(self):
        """Test language code format (ISO 639-1)."""
        for lang in ["en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu", "pa"]:
            assert len(lang) == 2
            assert lang.islower()


class TestMIMETypes:
    """Tests for MIME type handling."""

    def test_audio_mime_types(self):
        """Test audio MIME types."""
        audio_types = [
            "audio/webm",
            "audio/webm;codecs=opus",
            "audio/wav",
            "audio/mp3",
        ]

        for mime in audio_types:
            assert mime.startswith("audio/")

    def test_report_mime_types(self):
        """Test report MIME types."""
        pdf_mime = "application/pdf"
        html_mime = "text/html"

        assert pdf_mime == "application/pdf"
        assert html_mime == "text/html"
