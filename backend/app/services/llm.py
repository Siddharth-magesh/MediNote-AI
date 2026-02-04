"""LLM service using Groq API for data extraction."""

import json
import re
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Service for LLM-based data extraction using Groq."""

    def __init__(self):
        self._client = None
        self.model = "llama-3.1-70b-versatile"  # Or mixtral-8x7b-32768

    def _get_client(self):
        """Get or create the Groq client."""
        if self._client is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not configured")

            try:
                from groq import Groq

                self._client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                raise ImportError(
                    "groq is not installed. Install it with: pip install groq"
                )
        return self._client

    async def extract_json(
        self,
        prompt: str,
        schema: Type[T],
        max_retries: int = 3,
    ) -> tuple[Optional[T], float]:
        """
        Extract structured data from text using LLM.

        Args:
            prompt: The prompt to send to the LLM
            schema: Pydantic model to validate the response
            max_retries: Number of retries on failure

        Returns:
            Tuple of (parsed data, confidence score)
        """
        client = self._get_client()

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a medical data extraction assistant. "
                                "Always respond with valid JSON only, no additional text. "
                                "Use null for fields that are not mentioned in the conversation."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_tokens=4096,
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content
                if not content:
                    continue

                # Parse JSON
                data = self._parse_json(content)
                if data is None:
                    continue

                # Validate against schema
                try:
                    validated = schema.model_validate(data)
                    confidence = self._calculate_confidence(validated, data)
                    return validated, confidence
                except ValidationError as e:
                    # Try to fix common issues and retry
                    if attempt < max_retries - 1:
                        continue
                    # Return partial data on last attempt
                    return None, 0.0

            except Exception as e:
                print(f"LLM extraction error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None, 0.0

        return None, 0.0

    def _parse_json(self, content: str) -> Optional[dict]:
        """Parse JSON from LLM response, handling common issues."""
        # Try direct parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in content
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _calculate_confidence(self, validated: BaseModel, raw_data: dict) -> float:
        """Calculate confidence score based on data completeness."""
        if not raw_data:
            return 0.0

        # Count non-null fields
        total_fields = 0
        non_null_fields = 0

        def count_fields(obj: Any, prefix: str = "") -> None:
            nonlocal total_fields, non_null_fields

            if isinstance(obj, dict):
                for key, value in obj.items():
                    total_fields += 1
                    if value is not None:
                        non_null_fields += 1
                        if isinstance(value, (dict, list)):
                            count_fields(value, f"{prefix}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        count_fields(item, f"{prefix}[{i}]")

        count_fields(raw_data)

        if total_fields == 0:
            return 0.5  # Empty but valid response

        return min(non_null_fields / total_fields + 0.3, 1.0)


class MockLLMService:
    """Mock LLM service for development/testing."""

    async def extract_json(
        self,
        prompt: str,
        schema: Type[T],
        max_retries: int = 3,
    ) -> tuple[Optional[T], float]:
        """Return mock extraction result."""
        # Return empty validated schema
        try:
            return schema.model_validate({}), 0.5
        except ValidationError:
            return None, 0.0


def get_llm_service() -> LLMService | MockLLMService:
    """Get the appropriate LLM service based on configuration."""
    if settings.GROQ_API_KEY:
        return LLMService()
    return MockLLMService()
