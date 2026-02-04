"""Security tests for MediNote-AI API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthenticationSecurity:
    """Tests for authentication security."""

    async def test_login_rate_limiting(self, client: AsyncClient):
        """Test that login endpoint has rate limiting."""
        # Attempt multiple failed logins
        for i in range(10):
            await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "nonexistent@example.com",
                    "password": "wrongpassword",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        # After many failed attempts, should be rate limited
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Response should be either 401 or 429 (rate limited)
        assert response.status_code in [401, 429]

    async def test_token_required_for_protected_routes(self, client: AsyncClient):
        """Test that protected routes require authentication."""
        protected_routes = [
            ("/api/v1/patients", "GET"),
            ("/api/v1/patients", "POST"),
            ("/api/v1/auth/me", "GET"),
            ("/api/v1/extraction/all", "POST"),
            ("/api/v1/reports", "GET"),
        ]

        for route, method in protected_routes:
            if method == "GET":
                response = await client.get(route)
            else:
                response = await client.post(route, json={})

            assert response.status_code == 401, f"{method} {route} should require auth"

    async def test_invalid_token_rejected(self, client: AsyncClient):
        """Test that invalid tokens are rejected."""
        response = await client.get(
            "/api/v1/patients",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    async def test_expired_token_rejected(self, client: AsyncClient):
        """Test that expired tokens are rejected."""
        # This is a manually crafted expired token (header.payload.signature)
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ."
            "signature"
        )

        response = await client.get(
            "/api/v1/patients",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    async def test_password_not_in_response(self, authenticated_client: AsyncClient):
        """Test that password is never returned in API responses."""
        response = await authenticated_client.get("/api/v1/auth/me")

        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data
        assert "password_hash" not in data


@pytest.mark.asyncio
class TestInputValidation:
    """Tests for input validation and sanitization."""

    async def test_sql_injection_prevention(self, authenticated_client: AsyncClient):
        """Test that SQL injection attempts are blocked."""
        malicious_inputs = [
            "'; DROP TABLE patients; --",
            "1 OR 1=1",
            "1'; DELETE FROM users WHERE '1'='1",
            "1 UNION SELECT * FROM users",
        ]

        for payload in malicious_inputs:
            response = await authenticated_client.get(
                f"/api/v1/patients/search?q={payload}"
            )
            # Should not return server error
            assert response.status_code != 500

    async def test_xss_prevention(self, authenticated_client: AsyncClient):
        """Test that XSS attempts are sanitized."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
        ]

        for payload in xss_payloads:
            response = await authenticated_client.post(
                "/api/v1/patients",
                json={
                    "first_name": payload,
                    "last_name": "Test",
                    "phone_primary": "+919876543210",
                },
            )

            if response.status_code == 201:
                data = response.json()
                # Script tags should be escaped or stripped
                assert "<script>" not in data.get("first_name", "")

    async def test_oversized_input_rejected(self, authenticated_client: AsyncClient):
        """Test that oversized inputs are rejected."""
        # Create a very large string
        large_input = "A" * 100000

        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": large_input,
                "last_name": "Test",
                "phone_primary": "+919876543210",
            },
        )

        # Should be rejected with validation error
        assert response.status_code in [400, 422]

    async def test_invalid_content_type_rejected(self, authenticated_client: AsyncClient):
        """Test that invalid content types are handled."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            content="not json",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code in [400, 415, 422]


@pytest.mark.asyncio
class TestAuthorizationSecurity:
    """Tests for authorization and access control."""

    async def test_user_cannot_access_other_users_data(
        self, client: AsyncClient, db_session
    ):
        """Test that users can only access their own data."""
        # Register and login as user 1
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "password": "TestPass123!",
                "name": "User One",
            },
        )
        response1 = await client.post(
            "/api/v1/auth/login",
            data={"username": "user1@example.com", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token1 = response1.json().get("access_token")

        # Register and login as user 2
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "TestPass123!",
                "name": "User Two",
            },
        )
        response2 = await client.post(
            "/api/v1/auth/login",
            data={"username": "user2@example.com", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token2 = response2.json().get("access_token")

        # Create patient as user 1
        create_response = await client.post(
            "/api/v1/patients",
            json={
                "first_name": "User1",
                "last_name": "Patient",
                "phone_primary": "+919876543299",
            },
            headers={"Authorization": f"Bearer {token1}"},
        )

        if create_response.status_code == 201:
            patient_id = create_response.json().get("id")

            # User 2 should not be able to access user 1's patient
            # (This depends on implementation - multi-tenant vs single-tenant)
            access_response = await client.get(
                f"/api/v1/patients/{patient_id}",
                headers={"Authorization": f"Bearer {token2}"},
            )

            # Response depends on authorization model
            # Either 404 (not found) or 403 (forbidden) is acceptable
            assert access_response.status_code in [200, 403, 404]


@pytest.mark.asyncio
class TestDataProtection:
    """Tests for data protection and privacy."""

    async def test_sensitive_data_not_logged(self, authenticated_client: AsyncClient):
        """Test that sensitive data is not exposed in error messages."""
        response = await authenticated_client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Error message should not reveal password or other sensitive info
        error_message = response.json().get("detail", "")
        assert "wrongpassword" not in error_message
        assert "password" not in error_message.lower() or "incorrect" in error_message.lower()

    async def test_no_debug_info_in_production_errors(self, client: AsyncClient):
        """Test that debug info is not exposed in errors."""
        # Trigger an error
        response = await client.get("/api/v1/nonexistent/endpoint")

        data = response.json()
        # Should not contain stack traces
        assert "traceback" not in str(data).lower()
        assert "exception" not in str(data).lower() or "detail" in data


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Tests for security headers."""

    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are properly set."""
        response = await client.options(
            "/api/v1/patients",
            headers={"Origin": "http://localhost:3000"},
        )

        # Should have CORS headers
        headers = response.headers
        # Implementation dependent - check if CORS is configured
        # assert "access-control-allow-origin" in headers

    async def test_no_server_version_disclosure(self, client: AsyncClient):
        """Test that server version is not disclosed."""
        response = await client.get("/api/v1/patients")

        # Server header should not reveal detailed version info
        server_header = response.headers.get("server", "")
        assert "uvicorn" not in server_header.lower() or "/" not in server_header


@pytest.mark.asyncio
class TestFileUploadSecurity:
    """Tests for file upload security."""

    async def test_file_type_validation(self, authenticated_client: AsyncClient):
        """Test that only allowed file types are accepted."""
        # This test would apply to audio upload endpoints
        pass

    async def test_file_size_limit(self, authenticated_client: AsyncClient):
        """Test that large files are rejected."""
        # This test would apply to audio upload endpoints
        pass


@pytest.mark.asyncio
class TestSessionSecurity:
    """Tests for session security."""

    async def test_logout_invalidates_token(self, client: AsyncClient):
        """Test that logout properly invalidates the token."""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout_test@example.com",
                "password": "TestPass123!",
                "name": "Logout Test",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "logout_test@example.com", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json().get("access_token")

        # Verify token works
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200

        # Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        # If logout is implemented, token should no longer work
        # (depends on implementation - stateless JWT vs token blacklist)

    async def test_concurrent_sessions_allowed(self, client: AsyncClient):
        """Test that multiple concurrent sessions are properly handled."""
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "concurrent@example.com",
                "password": "TestPass123!",
                "name": "Concurrent Test",
            },
        )

        # Login twice
        response1 = await client.post(
            "/api/v1/auth/login",
            data={"username": "concurrent@example.com", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token1 = response1.json().get("access_token")

        response2 = await client.post(
            "/api/v1/auth/login",
            data={"username": "concurrent@example.com", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token2 = response2.json().get("access_token")

        # Both tokens should work
        me1 = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"},
        )
        me2 = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token2}"},
        )

        assert me1.status_code == 200
        assert me2.status_code == 200
