"""Translation service using Google Cloud Translation API."""

from typing import Optional

from app.core.config import settings


class TranslationService:
    """Service for translating text using Google Cloud Translation API."""

    def __init__(self):
        self._client = None

    async def _get_client(self):
        """Get or create the Translation client."""
        if self._client is None:
            try:
                from google.cloud import translate_v2 as translate

                self._client = translate.Client()
            except ImportError:
                raise ImportError(
                    "google-cloud-translate is not installed. "
                    "Install it with: pip install google-cloud-translate"
                )
        return self._client

    async def translate_to_english(
        self,
        text: str,
        source_language: Optional[str] = None,
    ) -> dict:
        """
        Translate text to English.

        Args:
            text: The text to translate
            source_language: Source language code (optional, will be detected if not provided)

        Returns:
            Dictionary with translated text and detected language
        """
        if not text.strip():
            return {
                "translated_text": "",
                "source_language": source_language or "unknown",
                "detected_language": None,
            }

        try:
            client = await self._get_client()

            result = client.translate(
                text,
                target_language="en",
                source_language=source_language,
            )

            return {
                "translated_text": result["translatedText"],
                "source_language": source_language,
                "detected_language": result.get("detectedSourceLanguage"),
            }

        except Exception as e:
            print(f"Translation error: {e}")
            return {
                "translated_text": text,  # Return original on error
                "source_language": source_language,
                "detected_language": None,
                "error": str(e),
            }

    async def detect_language(self, text: str) -> dict:
        """
        Detect the language of text.

        Returns:
            Dictionary with detected language and confidence
        """
        if not text.strip():
            return {"language": "unknown", "confidence": 0.0}

        try:
            client = await self._get_client()
            result = client.detect_language(text)

            return {
                "language": result["language"],
                "confidence": result["confidence"],
            }

        except Exception as e:
            print(f"Language detection error: {e}")
            return {"language": "unknown", "confidence": 0.0, "error": str(e)}


class MockTranslationService:
    """Mock translation service for development/testing."""

    async def translate_to_english(
        self,
        text: str,
        source_language: Optional[str] = None,
    ) -> dict:
        """Return mock translation (no actual translation)."""
        return {
            "translated_text": f"[Mock translation of: {text[:50]}...]"
            if len(text) > 50
            else f"[Mock translation of: {text}]",
            "source_language": source_language,
            "detected_language": source_language or "hi",
        }

    async def detect_language(self, text: str) -> dict:
        """Return mock language detection."""
        return {"language": "en", "confidence": 0.95}


def get_translation_service() -> TranslationService | MockTranslationService:
    """Get the appropriate translation service based on configuration."""
    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        return TranslationService()
    return MockTranslationService()
