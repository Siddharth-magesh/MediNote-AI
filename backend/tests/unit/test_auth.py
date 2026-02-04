"""Unit tests for authentication schemas and validation."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import PasswordChange, UserRegister


class TestUserRegisterSchema:
    """Tests for UserRegister schema validation."""

    def test_valid_registration(self):
        """Test valid registration data."""
        data = UserRegister(
            email="test@example.com",
            password="TestPass123!",
            name="Test User",
        )

        assert data.email == "test@example.com"
        assert data.name == "Test User"

    def test_invalid_email(self):
        """Test invalid email validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="invalid-email",
                password="TestPass123!",
                name="Test User",
            )

        assert "email" in str(exc_info.value)

    def test_password_too_short(self):
        """Test password too short validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="Short1!",
                name="Test User",
            )

        assert "password" in str(exc_info.value).lower()

    def test_password_no_uppercase(self):
        """Test password without uppercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="testpass123!",
                name="Test User",
            )

        assert "uppercase" in str(exc_info.value)

    def test_password_no_lowercase(self):
        """Test password without lowercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="TESTPASS123!",
                name="Test User",
            )

        assert "lowercase" in str(exc_info.value)

    def test_password_no_digit(self):
        """Test password without digit."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="TestPassword!",
                name="Test User",
            )

        assert "digit" in str(exc_info.value)

    def test_password_no_special_char(self):
        """Test password without special character."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="TestPassword123",
                name="Test User",
            )

        assert "special" in str(exc_info.value)

    def test_name_too_short(self):
        """Test name too short validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="TestPass123!",
                name="T",
            )

        assert "name" in str(exc_info.value).lower()

    def test_optional_fields(self):
        """Test optional fields."""
        data = UserRegister(
            email="test@example.com",
            password="TestPass123!",
            name="Test User",
            phone="+919876543210",
            hospital_name="Test Hospital",
            qualification="MBBS",
        )

        assert data.phone == "+919876543210"
        assert data.hospital_name == "Test Hospital"
        assert data.qualification == "MBBS"


class TestPasswordChangeSchema:
    """Tests for PasswordChange schema validation."""

    def test_valid_password_change(self):
        """Test valid password change data."""
        data = PasswordChange(
            current_password="OldPass123!",
            new_password="NewPass456!",
        )

        assert data.current_password == "OldPass123!"
        assert data.new_password == "NewPass456!"

    def test_new_password_validation(self):
        """Test new password validation."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                current_password="OldPass123!",
                new_password="weak",
            )

        assert "password" in str(exc_info.value).lower()
