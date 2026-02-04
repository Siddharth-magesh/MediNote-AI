"""Recording schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """Schema for transcript segment."""

    text: str
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    language: Optional[str] = None


class RecordingSessionStart(BaseModel):
    """Schema for starting a recording session."""

    patient_id: UUID
    visit_id: Optional[UUID] = None
    language: str = Field(default="en", pattern="^(en|hi|ta|te|ml|kn|bn|mr|gu|pa)$")


class RecordingSessionResponse(BaseModel):
    """Schema for recording session response."""

    session_id: UUID
    visit_id: UUID
    websocket_url: str
    language: str


class RecordingStop(BaseModel):
    """Schema for stopping a recording."""

    save_audio: bool = True


class RecordingStopResponse(BaseModel):
    """Schema for recording stop response."""

    session_id: UUID
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    duration_seconds: int
    status: str


class AudioChunkMessage(BaseModel):
    """WebSocket message for audio chunk."""

    type: str = "audio_chunk"
    data: str  # Base64 encoded audio data
    sequence: int
    timestamp: int


class TranscriptMessage(BaseModel):
    """WebSocket message for transcript update."""

    type: str = "transcript"
    text: str
    is_final: bool = False
    confidence: float = 0.0
    language: Optional[str] = None


class ErrorMessage(BaseModel):
    """WebSocket message for errors."""

    type: str = "error"
    code: str
    message: str


class RecordingCreate(BaseModel):
    """Schema for creating a recording."""

    visit_id: UUID
    audio_url: str
    audio_format: str = "wav"
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    language: str = "en"
    transcript: Optional[str] = None
    transcript_segments: Optional[list[dict[str, Any]]] = None


class RecordingUpdate(BaseModel):
    """Schema for updating a recording."""

    transcript: Optional[str] = None
    transcript_segments: Optional[list[dict[str, Any]]] = None
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None


class RecordingResponse(BaseModel):
    """Schema for recording response."""

    id: UUID
    visit_id: UUID
    doctor_id: UUID
    audio_url: str
    audio_format: str
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    language: str
    transcript: Optional[str] = None
    transcript_segments: Optional[list[dict[str, Any]]] = None
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
