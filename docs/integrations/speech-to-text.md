# Speech-to-Text Integration

## Overview
Integration with Google Cloud Speech-to-Text API for audio transcription.

## Configuration

### Google Cloud Setup
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Service Implementation
```python
# app/services/transcription.py
from google.cloud import speech
from google.cloud.speech import RecognitionConfig, StreamingRecognitionConfig
import asyncio

class TranscriptionService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def get_config(self, language: str = "en-US") -> RecognitionConfig:
        """Get recognition config for language."""
        language_map = {
            "en": "en-US",
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "bn": "bn-IN",
        }

        return RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_map.get(language, "en-US"),
            enable_automatic_punctuation=True,
            model="latest_long",  # Better for conversations
            use_enhanced=True,
        )

    async def transcribe_audio(self, audio_content: bytes, language: str) -> str:
        """Transcribe audio bytes to text."""
        audio = speech.RecognitionAudio(content=audio_content)
        config = self.get_config(language)

        response = self.client.recognize(config=config, audio=audio)

        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "

        return transcript.strip()
```

## Streaming Transcription

```python
# app/services/streaming_transcription.py
import asyncio
from google.cloud import speech

class StreamingTranscriptionService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def get_streaming_config(self, language: str = "en-US"):
        """Get streaming config."""
        recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language,
            enable_automatic_punctuation=True,
            interim_results=True,  # Enable partial results
        )

        return speech.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True,
        )

    async def stream_transcribe(self, audio_generator, language: str = "en-US"):
        """
        Stream audio and yield transcription results.

        Args:
            audio_generator: Async generator yielding audio chunks
            language: Language code

        Yields:
            dict: {"text": str, "is_final": bool, "confidence": float}
        """
        config = self.get_streaming_config(language)

        def request_generator():
            yield speech.StreamingRecognizeRequest(streaming_config=config)
            for chunk in audio_generator:
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

        responses = self.client.streaming_recognize(requests=request_generator())

        for response in responses:
            for result in response.results:
                yield {
                    "text": result.alternatives[0].transcript,
                    "is_final": result.is_final,
                    "confidence": result.alternatives[0].confidence if result.is_final else None,
                }
```

## WebSocket Integration

```python
# app/api/v1/recording.py
from fastapi import WebSocket
from app.services.streaming_transcription import StreamingTranscriptionService

@router.websocket("/ws/recording/{session_id}")
async def recording_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    transcription_service = StreamingTranscriptionService()
    audio_queue = asyncio.Queue()

    async def receive_audio():
        """Receive audio chunks from client."""
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "audio_chunk":
                audio_bytes = base64.b64decode(data["data"])
                await audio_queue.put(audio_bytes)
            elif data.get("type") == "stop":
                await audio_queue.put(None)
                break

    async def audio_generator():
        """Generate audio chunks for transcription."""
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            yield chunk

    # Start receiving audio
    receive_task = asyncio.create_task(receive_audio())

    # Stream transcription
    async for result in transcription_service.stream_transcribe(audio_generator()):
        await websocket.send_json({
            "type": "transcript",
            "text": result["text"],
            "is_final": result["is_final"],
            "confidence": result.get("confidence"),
        })

    await receive_task
    await websocket.close()
```

## Language Support

| Language | Code | Region | Notes |
|----------|------|--------|-------|
| English | en-US | US | Primary |
| Hindi | hi-IN | India | Good support |
| Tamil | ta-IN | India | Good support |
| Telugu | te-IN | India | Good support |
| Bengali | bn-IN | India | Good support |
| Marathi | mr-IN | India | Available |

## Audio Requirements

| Parameter | Requirement |
|-----------|-------------|
| Sample Rate | 16000 Hz |
| Channels | Mono |
| Bit Depth | 16-bit |
| Encoding | LINEAR16 (PCM) |
| Max Duration | 480 minutes (streaming) |

## Error Handling

```python
from google.api_core import exceptions as google_exceptions

class TranscriptionService:
    async def transcribe_with_retry(self, audio: bytes, language: str, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return await self.transcribe_audio(audio, language)
            except google_exceptions.ResourceExhausted:
                # Rate limit
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
            except google_exceptions.InvalidArgument as e:
                # Audio format issue
                raise ValueError(f"Invalid audio format: {e}")
            except google_exceptions.DeadlineExceeded:
                # Timeout
                if attempt < max_retries - 1:
                    continue
                raise
```

## Pricing

| Feature | Price |
|---------|-------|
| Standard recognition | $0.006/15 seconds |
| Enhanced recognition | $0.009/15 seconds |
| Streaming | $0.006/15 seconds |

## Best Practices

1. **Use enhanced model** for better accuracy
2. **Enable punctuation** for readable transcripts
3. **Chunk audio** at silence boundaries
4. **Handle interruptions** gracefully
5. **Cache results** when possible

## Related Documentation
- [Audio Recording Feature](../features/audio-recording.md)
- [Recording API](../api/recording.md)
