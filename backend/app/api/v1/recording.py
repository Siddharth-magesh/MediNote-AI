"""Recording API endpoints including WebSocket for real-time streaming."""

import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundError
from app.schemas.recording import (
    RecordingResponse,
    RecordingSessionResponse,
    RecordingSessionStart,
    RecordingStop,
    RecordingStopResponse,
    RecordingUpdate,
)
from app.services.recording import RecordingService, session_manager

router = APIRouter(prefix="/recording", tags=["Recording"])


@router.post("/start", response_model=RecordingSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_recording_session(
    data: RecordingSessionStart,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Start a new recording session.

    Creates a new visit (if visit_id not provided) and returns a WebSocket URL
    for streaming audio.

    - **patient_id**: UUID of the patient
    - **visit_id**: Optional UUID of existing visit
    - **language**: Recording language (en, hi, ta, etc.)
    """
    service = RecordingService(db)

    try:
        session = await service.start_session(
            patient_id=data.patient_id,
            doctor_id=current_user.id,
            language=data.language,
            visit_id=data.visit_id,
        )

        # Generate WebSocket URL (relative path)
        websocket_url = f"/api/v1/recording/ws/{session.session_id}"

        return RecordingSessionResponse(
            session_id=session.session_id,
            visit_id=session.visit_id,
            websocket_url=websocket_url,
            language=session.language,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{session_id}/stop", response_model=RecordingStopResponse)
async def stop_recording_session(
    session_id: UUID,
    data: RecordingStop,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Stop a recording session.

    Saves the audio file and returns the final transcript.

    - **session_id**: UUID of the recording session
    - **save_audio**: Whether to save the audio file (default: true)
    """
    service = RecordingService(db)

    recording = await service.stop_session(
        session_id=session_id,
        save_audio=data.save_audio,
    )

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording session {session_id} not found",
        )

    return RecordingStopResponse(
        session_id=session_id,
        audio_url=recording.audio_url if recording.audio_url else None,
        transcript=recording.transcript,
        duration_seconds=recording.duration_seconds or 0,
        status=recording.status,
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a recording by ID.

    - **recording_id**: UUID of the recording
    """
    service = RecordingService(db)
    recording = await service.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )

    return recording


@router.get("/visit/{visit_id}", response_model=RecordingResponse)
async def get_recording_by_visit(
    visit_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get recording for a visit.

    - **visit_id**: UUID of the visit
    """
    service = RecordingService(db)
    recording = await service.get_recording_by_visit(visit_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording for visit {visit_id} not found",
        )

    return recording


@router.patch("/{recording_id}", response_model=RecordingResponse)
async def update_recording(
    recording_id: UUID,
    data: RecordingUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update a recording.

    - **recording_id**: UUID of the recording
    """
    service = RecordingService(db)
    recording = await service.update_recording(recording_id, data)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )

    return recording


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Delete a recording.

    - **recording_id**: UUID of the recording
    """
    service = RecordingService(db)
    deleted = await service.delete_recording(recording_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )


@router.get("/{recording_id}/audio-url")
async def get_audio_download_url(
    recording_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    expiry_hours: int = Query(default=1, ge=1, le=24),
):
    """
    Get a presigned URL for downloading audio.

    - **recording_id**: UUID of the recording
    - **expiry_hours**: URL expiry time in hours (1-24, default: 1)
    """
    service = RecordingService(db)
    url = await service.get_audio_url(recording_id)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio for recording {recording_id} not found",
        )

    return {"audio_url": url, "expires_in_hours": expiry_hours}


@router.websocket("/ws/{session_id}")
async def websocket_recording(
    websocket: WebSocket,
    session_id: UUID,
):
    """
    WebSocket endpoint for real-time audio streaming.

    Protocol:
    - Client sends: {"type": "audio_chunk", "data": "<base64>", "sequence": 1, "timestamp": 123}
    - Server sends: {"type": "transcript", "text": "...", "is_final": false, "confidence": 0.95}
    - Server sends: {"type": "error", "code": "...", "message": "..."}
    """
    # Verify session exists
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    await websocket.accept()

    # Send initial confirmation
    await websocket.send_json({
        "type": "session_started",
        "session_id": str(session_id),
        "language": session.language,
    })

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "audio_chunk":
                    # Process audio chunk
                    audio_data = message.get("data", "")
                    sequence = message.get("sequence", 0)

                    # Store the chunk
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    session.add_audio_chunk(audio_bytes, sequence)

                    # Acknowledge receipt
                    await websocket.send_json({
                        "type": "chunk_received",
                        "sequence": sequence,
                    })

                    # For real STT, we would stream to Google here
                    # and send back interim results. For now, we just
                    # accumulate audio for batch processing.

                elif msg_type == "pause":
                    session.status = "paused"
                    await websocket.send_json({
                        "type": "status",
                        "status": "paused",
                    })

                elif msg_type == "resume":
                    session.status = "active"
                    await websocket.send_json({
                        "type": "status",
                        "status": "active",
                    })

                elif msg_type == "stop":
                    # Session will be stopped via HTTP endpoint
                    await websocket.send_json({
                        "type": "status",
                        "status": "stopping",
                    })
                    break

                else:
                    await websocket.send_json({
                        "type": "error",
                        "code": "UNKNOWN_MESSAGE_TYPE",
                        "message": f"Unknown message type: {msg_type}",
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "code": "INVALID_JSON",
                    "message": "Invalid JSON message",
                })

    except WebSocketDisconnect:
        # Client disconnected
        session.status = "disconnected"
    except Exception as e:
        # Send error and close
        try:
            await websocket.send_json({
                "type": "error",
                "code": "SERVER_ERROR",
                "message": str(e),
            })
        except Exception:
            pass
        finally:
            await websocket.close()
