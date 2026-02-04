"""Integration tests for authentication API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRegistration:
    """Tests for user registration endpoint."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "TestPass123!",
                "name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email."""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "TestPass123!",
                "name": "First User",
            },
        )

        # Second registration with same email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "TestPass123!",
                "name": "Second User",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPass123!",
                "name": "Test User",
            },
        )

        assert response.status_code == 422

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "name": "Test User",
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthLogin:
    """Tests for user login endpoint."""

    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        # First register
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "TestPass123!",
                "name": "Login User",
            },
        )

        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": "TestPass123!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password."""
        # First register
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "TestPass123!",
                "name": "Test User",
            },
        )

        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "wrongpass@example.com",
                "password": "WrongPassword!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "TestPass123!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthMe:
    """Tests for /auth/me endpoint."""

    async def test_get_current_user(self, authenticated_client: AsyncClient):
        """Test getting current user info."""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test Doctor"

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    async def test_refresh_token_success(self, client: AsyncClient):
        """Test successful token refresh."""
        # First register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "TestPass123!",
                "name": "Refresh User",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "refresh@example.com",
                "password": "TestPass123!",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = login_response.json()

        # Refresh tokens
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )

        assert response.status_code == 200
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401
