"""Integration tests for recording API."""

import base64
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


@pytest.fixture
async def test_patient(authenticated_client: AsyncClient):
    """Create a test patient for recording tests."""
    response = await authenticated_client.post(
        "/api/v1/patients",
        json={
            "first_name": "Recording",
            "last_name": "TestPatient",
            "phone_primary": "+919876543300",
        },
    )
    return response.json()


@pytest.mark.asyncio
class TestRecordingSessionStart:
    """Tests for starting recording sessions."""

    async def test_start_session_success(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
    ):
        """Test successful session start."""
        response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "en",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "visit_id" in data
        assert "websocket_url" in data
        assert data["language"] == "en"
        assert "/ws/" in data["websocket_url"]

    async def test_start_session_with_hindi(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
    ):
        """Test session start with Hindi language."""
        response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "hi",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "hi"

    async def test_start_session_invalid_language(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
    ):
        """Test session start with invalid language."""
        response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "invalid",
            },
        )

        assert response.status_code == 422

    async def test_start_session_unauthorized(
        self,
        client: AsyncClient,
        test_patient: dict,
    ):
        """Test session start without authentication."""
        response = await client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "en",
            },
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestRecordingSessionStop:
    """Tests for stopping recording sessions."""

    async def test_stop_session_success(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
    ):
        """Test successful session stop."""
        # Start a session first
        start_response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "en",
            },
        )
        session_id = start_response.json()["session_id"]

        # Mock storage service to avoid actual MinIO calls
        with patch("app.services.recording.get_storage_service") as mock_storage:
            mock_service = MagicMock()
            mock_service.upload_audio.return_value = "recordings/2024/01/01/test.wav"
            mock_storage.return_value = mock_service

            # Stop the session
            response = await authenticated_client.post(
                f"/api/v1/recording/{session_id}/stop",
                json={"save_audio": True},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "completed"
        assert "duration_seconds" in data

    async def test_stop_session_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test stopping non-existent session."""
        response = await authenticated_client.post(
            "/api/v1/recording/00000000-0000-0000-0000-000000000000/stop",
            json={"save_audio": True},
        )

        assert response.status_code == 404

    async def test_stop_session_no_save(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
    ):
        """Test stopping session without saving audio."""
        # Start a session
        start_response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": "en",
            },
        )
        session_id = start_response.json()["session_id"]

        # Mock storage service
        with patch("app.services.recording.get_storage_service") as mock_storage:
            mock_service = MagicMock()
            mock_storage.return_value = mock_service

            # Stop without saving
            response = await authenticated_client.post(
                f"/api/v1/recording/{session_id}/stop",
                json={"save_audio": False},
            )

        assert response.status_code == 200


@pytest.mark.asyncio
class TestRecordingCRUD:
    """Tests for recording CRUD operations."""

    async def test_get_recording_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test getting non-existent recording."""
        response = await authenticated_client.get(
            "/api/v1/recording/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    async def test_get_recording_by_visit_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test getting recording by non-existent visit."""
        response = await authenticated_client.get(
            "/api/v1/recording/visit/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    async def test_delete_recording_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test deleting non-existent recording."""
        response = await authenticated_client.delete(
            "/api/v1/recording/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestRecordingAudioURL:
    """Tests for audio URL endpoints."""

    async def test_get_audio_url_not_found(
        self,
        authenticated_client: AsyncClient,
    ):
        """Test getting audio URL for non-existent recording."""
        response = await authenticated_client.get(
            "/api/v1/recording/00000000-0000-0000-0000-000000000000/audio-url"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestRecordingLanguages:
    """Tests for multi-language support."""

    @pytest.mark.parametrize(
        "language",
        ["en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu", "pa"],
    )
    async def test_supported_languages(
        self,
        authenticated_client: AsyncClient,
        test_patient: dict,
        language: str,
    ):
        """Test all supported languages can start sessions."""
        response = await authenticated_client.post(
            "/api/v1/recording/start",
            json={
                "patient_id": test_patient["id"],
                "language": language,
            },
        )

        assert response.status_code == 201
        assert response.json()["language"] == language
