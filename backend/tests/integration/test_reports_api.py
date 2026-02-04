"""Integration tests for reports API."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
class TestReportGeneration:
    """Tests for report generation endpoint."""

    async def test_generate_report_visit_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test report generation with non-existent visit."""
        response = await authenticated_client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": "full",
                "format": "pdf",
            },
        )

        assert response.status_code == 404

    async def test_generate_report_invalid_type(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test report generation with invalid report type."""
        response = await authenticated_client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": "invalid_type",
                "format": "pdf",
            },
        )

        assert response.status_code == 422

    async def test_generate_report_unauthorized(
        self,
        client: AsyncClient,
    ):
        """Test report generation without authentication."""
        response = await client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": "full",
            },
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestReportRetrieval:
    """Tests for report retrieval endpoints."""

    async def test_get_report_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test getting non-existent report."""
        response = await authenticated_client.get(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    async def test_download_report_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test downloading non-existent report."""
        response = await authenticated_client.get(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000/download"
        )

        assert response.status_code == 404

    async def test_preview_report_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test previewing non-existent report."""
        response = await authenticated_client.get(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000/preview"
        )

        assert response.status_code == 404

    async def test_list_reports_empty(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test listing reports when empty."""
        response = await authenticated_client.get("/api/v1/reports")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data


@pytest.mark.asyncio
class TestReportVerification:
    """Tests for report verification endpoint."""

    async def test_verify_report_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test verifying non-existent report."""
        response = await authenticated_client.get(
            "/api/v1/reports/verify/RPT-9999-99999"
        )

        assert response.status_code == 404

    async def test_verify_report_invalid_format(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test verifying with invalid report number format."""
        response = await authenticated_client.get(
            "/api/v1/reports/verify/INVALID"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestReportDeletion:
    """Tests for report deletion endpoint."""

    async def test_delete_report_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test deleting non-existent report."""
        response = await authenticated_client.delete(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestReportTypes:
    """Tests for different report types."""

    @pytest.mark.parametrize(
        "report_type",
        ["full", "prescription_only", "diet_only", "care_only"],
    )
    async def test_valid_report_types(
        self,
        authenticated_client: AsyncClient,
        report_type: str,
    ):
        """Test that valid report types are accepted (validation only)."""
        # This just tests the validation - actual generation would need a real visit
        response = await authenticated_client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": report_type,
                "format": "pdf",
            },
        )

        # Should fail with 404 (visit not found) not 422 (validation error)
        assert response.status_code == 404


@pytest.mark.asyncio
class TestReportFormats:
    """Tests for different report formats."""

    @pytest.mark.parametrize(
        "format_type",
        ["pdf", "html"],
    )
    async def test_valid_formats(
        self,
        authenticated_client: AsyncClient,
        format_type: str,
    ):
        """Test that valid formats are accepted (validation only)."""
        response = await authenticated_client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": "full",
                "format": format_type,
            },
        )

        # Should fail with 404 (visit not found) not 422 (validation error)
        assert response.status_code == 404

    async def test_invalid_format(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test that invalid format is rejected."""
        response = await authenticated_client.post(
            "/api/v1/reports/generate",
            json={
                "visit_id": "00000000-0000-0000-0000-000000000000",
                "report_type": "full",
                "format": "docx",  # Invalid
            },
        )

        assert response.status_code == 422
