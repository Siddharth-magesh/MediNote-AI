"""Unit tests for security module."""

import pytest
from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_correct_password(self):
        """Test verifying correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test verifying wrong password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token(self):
        """Test creating access token."""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)

        assert token is not None
        assert len(token) > 0
        assert token.count(".") == 2  # JWT format: header.payload.signature

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)

        assert token is not None
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding valid token."""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"

    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        payload = decode_token("invalid.token.here")

        assert payload is None

    def test_verify_access_token(self):
        """Test verifying access token."""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        result = verify_token(token, token_type="access")

        assert result == user_id

    def test_verify_refresh_token(self):
        """Test verifying refresh token."""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)
        result = verify_token(token, token_type="refresh")

        assert result == user_id

    def test_verify_wrong_token_type(self):
        """Test verifying token with wrong type."""
        user_id = "test-user-id"
        access_token = create_access_token(subject=user_id)

        # Try to verify access token as refresh token
        result = verify_token(access_token, token_type="refresh")

        assert result is None

    def test_token_with_custom_expiry(self):
        """Test creating token with custom expiry."""
        user_id = "test-user-id"
        expires = timedelta(minutes=5)
        token = create_access_token(subject=user_id, expires_delta=expires)
        payload = decode_token(token)

        assert payload is not None
        assert payload.get("sub") == user_id
