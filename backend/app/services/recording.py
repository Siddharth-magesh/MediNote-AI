"""Recording service for managing audio recordings and transcriptions."""

import asyncio
import base64
import io
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.recording import Recording
from app.models.visit import Visit
from app.repositories.visit import VisitRepository
from app.schemas.recording import RecordingCreate, RecordingUpdate
from app.services.speech_to_text import get_stt_service, TranscriptResult
from app.services.storage import get_storage_service
from app.services.translation import get_translation_service


class RecordingSession:
    """Manages an active recording session."""

    def __init__(
        self,
        session_id: uuid.UUID,
        visit_id: uuid.UUID,
        doctor_id: uuid.UUID,
        language: str = "en",
    ):
        self.session_id = session_id
        self.visit_id = visit_id
        self.doctor_id = doctor_id
        self.language = language
        self.status = "active"
        self.started_at = datetime.utcnow()
        self.audio_chunks: list[bytes] = []
        self.transcript_segments: list[dict[str, Any]] = []
        self.full_transcript = ""
        self._audio_buffer = io.BytesIO()

    def add_audio_chunk(self, data: bytes, sequence: int) -> None:
        """Add an audio chunk to the session."""
        self.audio_chunks.append(data)
        self._audio_buffer.write(data)

    def add_transcript_segment(
        self,
        text: str,
        is_final: bool,
        confidence: float,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> None:
        """Add a transcript segment."""
        segment = {
            "text": text,
            "is_final": is_final,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if start_time is not None:
            segment["start"] = start_time
        if end_time is not None:
            segment["end"] = end_time

        self.transcript_segments.append(segment)

        if is_final:
            self.full_transcript += f" {text}"
            self.full_transcript = self.full_transcript.strip()

    def get_audio_data(self) -> bytes:
        """Get all audio data as bytes."""
        return self._audio_buffer.getvalue()

    @property
    def duration_seconds(self) -> int:
        """Calculate duration in seconds based on audio chunks."""
        # Each chunk is 250ms at 16kHz, 16-bit mono
        # Chunk size = 16000 * 0.25 * 2 = 8000 bytes
        total_bytes = len(self.get_audio_data())
        # 16000 samples/sec * 2 bytes/sample = 32000 bytes/sec
        return int(total_bytes / 32000)


class RecordingSessionManager:
    """Manages multiple recording sessions."""

    def __init__(self):
        self._sessions: dict[uuid.UUID, RecordingSession] = {}

    def create_session(
        self,
        visit_id: uuid.UUID,
        doctor_id: uuid.UUID,
        language: str = "en",
    ) -> RecordingSession:
        """Create a new recording session."""
        session_id = uuid.uuid4()
        session = RecordingSession(
            session_id=session_id,
            visit_id=visit_id,
            doctor_id=doctor_id,
            language=language,
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: uuid.UUID) -> Optional[RecordingSession]:
        """Get a recording session by ID."""
        return self._sessions.get(session_id)

    def end_session(self, session_id: uuid.UUID) -> Optional[RecordingSession]:
        """End and remove a recording session."""
        session = self._sessions.pop(session_id, None)
        if session:
            session.status = "completed"
        return session

    def get_active_sessions(self) -> list[RecordingSession]:
        """Get all active sessions."""
        return [s for s in self._sessions.values() if s.status == "active"]


# Global session manager
session_manager = RecordingSessionManager()


class RecordingService:
    """Service for recording operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.visit_repo = VisitRepository(db)
        self.storage = get_storage_service()

    async def start_session(
        self,
        patient_id: uuid.UUID,
        doctor_id: uuid.UUID,
        language: str = "en",
        visit_id: Optional[uuid.UUID] = None,
    ) -> RecordingSession:
        """Start a new recording session."""
        # Create or get visit
        if visit_id:
            visit = await self.visit_repo.get(visit_id)
            if not visit:
                raise NotFoundError(f"Visit {visit_id} not found")
        else:
            # Create a new visit
            visit_number = await self.visit_repo.generate_visit_number()
            visit = Visit(
                visit_number=visit_number,
                patient_id=patient_id,
                doctor_id=doctor_id,
                status="in_progress",
            )
            self.db.add(visit)
            await self.db.commit()
            await self.db.refresh(visit)

        # Create session
        session = session_manager.create_session(
            visit_id=visit.id,
            doctor_id=doctor_id,
            language=language,
        )

        return session

    async def process_audio_chunk(
        self,
        session_id: uuid.UUID,
        audio_data: str,  # Base64 encoded
        sequence: int,
    ) -> Optional[TranscriptResult]:
        """Process an audio chunk and return transcript if available."""
        session = session_manager.get_session(session_id)
        if not session:
            return None

        # Decode and store audio
        audio_bytes = base64.b64decode(audio_data)
        session.add_audio_chunk(audio_bytes, sequence)

        # For real-time transcription, we'd stream to STT service
        # Here we return None and do batch transcription at end
        return None

    async def stop_session(
        self,
        session_id: uuid.UUID,
        save_audio: bool = True,
    ) -> Optional[Recording]:
        """Stop a recording session and save the recording."""
        session = session_manager.end_session(session_id)
        if not session:
            return None

        audio_url = None
        if save_audio and session.get_audio_data():
            # Save audio to storage
            audio_data = session.get_audio_data()
            audio_url = await self.storage.upload_audio(
                audio_data,
                f"{session.session_id}.wav",
                content_type="audio/wav",
            )

        # Transcribe the full audio
        stt_service = get_stt_service(session.language)
        transcript_result = await stt_service.transcribe_audio(session.get_audio_data())

        transcript = transcript_result.text or session.full_transcript

        # Translate if not English
        if session.language != "en" and transcript:
            translation_service = get_translation_service()
            translation = await translation_service.translate_to_english(
                transcript,
                source_language=session.language,
            )
            # Store both original and translated
            translated_transcript = translation.get("translated_text", transcript)
        else:
            translated_transcript = transcript

        # Create recording record
        recording = Recording(
            visit_id=session.visit_id,
            doctor_id=session.doctor_id,
            audio_url=audio_url or "",
            audio_format="wav",
            duration_seconds=session.duration_seconds,
            file_size_bytes=len(session.get_audio_data()) if session.get_audio_data() else 0,
            language=session.language,
            transcript=translated_transcript,
            transcript_segments=session.transcript_segments if session.transcript_segments else None,
            status="completed",
            processed_at=datetime.utcnow(),
        )

        self.db.add(recording)
        await self.db.commit()
        await self.db.refresh(recording)

        return recording

    async def get_recording(self, recording_id: uuid.UUID) -> Optional[Recording]:
        """Get a recording by ID."""
        result = await self.db.execute(
            select(Recording).where(Recording.id == recording_id)
        )
        return result.scalar_one_or_none()

    async def get_recording_by_visit(self, visit_id: uuid.UUID) -> Optional[Recording]:
        """Get recording for a visit."""
        result = await self.db.execute(
            select(Recording).where(Recording.visit_id == visit_id)
        )
        return result.scalar_one_or_none()

    async def update_recording(
        self,
        recording_id: uuid.UUID,
        data: RecordingUpdate,
    ) -> Optional[Recording]:
        """Update a recording."""
        recording = await self.get_recording(recording_id)
        if not recording:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(recording, field, value)

        await self.db.commit()
        await self.db.refresh(recording)

        return recording

    async def delete_recording(self, recording_id: uuid.UUID) -> bool:
        """Delete a recording and its audio file."""
        recording = await self.get_recording(recording_id)
        if not recording:
            return False

        # Delete audio file from storage
        if recording.audio_url:
            await self.storage.delete_file(recording.audio_url)

        # Delete record
        await self.db.delete(recording)
        await self.db.commit()

        return True

    async def get_audio_url(self, recording_id: uuid.UUID) -> Optional[str]:
        """Get a presigned URL for downloading audio."""
        recording = await self.get_recording(recording_id)
        if not recording or not recording.audio_url:
            return None

        return await self.storage.get_presigned_url(recording.audio_url)
