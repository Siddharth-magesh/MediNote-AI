"""Speech-to-Text service using Google Cloud Speech API."""

import asyncio
import base64
import io
from typing import AsyncGenerator, Optional

from app.core.config import settings


# Language code mapping for Google Speech API
LANGUAGE_CODES = {
    "en": "en-IN",  # English (India)
    "hi": "hi-IN",  # Hindi
    "ta": "ta-IN",  # Tamil
    "te": "te-IN",  # Telugu
    "ml": "ml-IN",  # Malayalam
    "kn": "kn-IN",  # Kannada
    "bn": "bn-IN",  # Bengali
    "mr": "mr-IN",  # Marathi
    "gu": "gu-IN",  # Gujarati
    "pa": "pa-IN",  # Punjabi
}


class TranscriptResult:
    """Result from speech recognition."""

    def __init__(
        self,
        text: str,
        is_final: bool = False,
        confidence: float = 0.0,
        language: Optional[str] = None,
    ):
        self.text = text
        self.is_final = is_final
        self.confidence = confidence
        self.language = language


class SpeechToTextService:
    """Service for speech-to-text using Google Cloud Speech API."""

    def __init__(self, language: str = "en"):
        self.language = language
        self.language_code = LANGUAGE_CODES.get(language, "en-IN")
        self._client = None
        self._streaming_config = None

    async def _get_client(self):
        """Get or create the Speech client."""
        if self._client is None:
            try:
                from google.cloud import speech_v1 as speech

                self._client = speech.SpeechAsyncClient()

                # Configure recognition
                recognition_config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=self.language_code,
                    enable_automatic_punctuation=True,
                    model="latest_long",
                    use_enhanced=True,
                    # Enable word-level confidence and timing
                    enable_word_confidence=True,
                    enable_word_time_offsets=True,
                )

                self._streaming_config = speech.StreamingRecognitionConfig(
                    config=recognition_config,
                    interim_results=True,
                    single_utterance=False,
                )
            except ImportError:
                raise ImportError(
                    "google-cloud-speech is not installed. "
                    "Install it with: pip install google-cloud-speech"
                )

        return self._client

    async def transcribe_audio(self, audio_data: bytes) -> TranscriptResult:
        """Transcribe a complete audio file."""
        try:
            from google.cloud import speech_v1 as speech

            client = await self._get_client()

            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
            )

            response = await client.recognize(config=config, audio=audio)

            if response.results:
                result = response.results[-1]
                alternative = result.alternatives[0]
                return TranscriptResult(
                    text=alternative.transcript,
                    is_final=True,
                    confidence=alternative.confidence,
                    language=self.language,
                )

            return TranscriptResult(text="", is_final=True, confidence=0.0)

        except Exception as e:
            # Return empty result on error, logging will be handled upstream
            print(f"Speech-to-text error: {e}")
            return TranscriptResult(text="", is_final=True, confidence=0.0)

    async def stream_transcribe(
        self,
        audio_generator: AsyncGenerator[bytes, None],
    ) -> AsyncGenerator[TranscriptResult, None]:
        """Stream audio and yield transcript results in real-time."""
        try:
            from google.cloud import speech_v1 as speech

            client = await self._get_client()

            async def request_generator():
                # First request must contain the config
                yield speech.StreamingRecognizeRequest(
                    streaming_config=self._streaming_config
                )

                # Subsequent requests contain audio
                async for chunk in audio_generator:
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)

            responses = await client.streaming_recognize(
                requests=request_generator()
            )

            async for response in responses:
                for result in response.results:
                    if result.alternatives:
                        alternative = result.alternatives[0]
                        yield TranscriptResult(
                            text=alternative.transcript,
                            is_final=result.is_final,
                            confidence=alternative.confidence if result.is_final else 0.0,
                            language=self.language,
                        )

        except Exception as e:
            print(f"Streaming transcription error: {e}")
            yield TranscriptResult(
                text="",
                is_final=True,
                confidence=0.0,
                language=self.language,
            )


class MockSpeechToTextService:
    """Mock STT service for development/testing without Google Cloud."""

    def __init__(self, language: str = "en"):
        self.language = language

    async def transcribe_audio(self, audio_data: bytes) -> TranscriptResult:
        """Return mock transcription."""
        return TranscriptResult(
            text="[Mock transcription - Google Cloud Speech not configured]",
            is_final=True,
            confidence=1.0,
            language=self.language,
        )

    async def stream_transcribe(
        self,
        audio_generator: AsyncGenerator[bytes, None],
    ) -> AsyncGenerator[TranscriptResult, None]:
        """Yield mock transcript results."""
        # Consume the audio generator
        chunk_count = 0
        async for _ in audio_generator:
            chunk_count += 1
            if chunk_count % 4 == 0:  # Every ~1 second (4 chunks at 250ms each)
                yield TranscriptResult(
                    text=f"[Mock transcript - chunk {chunk_count}]",
                    is_final=False,
                    confidence=0.9,
                    language=self.language,
                )

        # Final result
        yield TranscriptResult(
            text="[Mock transcription complete]",
            is_final=True,
            confidence=1.0,
            language=self.language,
        )


def get_stt_service(language: str = "en") -> SpeechToTextService | MockSpeechToTextService:
    """Get the appropriate STT service based on configuration."""
    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        return SpeechToTextService(language)
    return MockSpeechToTextService(language)
