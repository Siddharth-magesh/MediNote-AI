# Groq LLM Integration

## Overview
Integration with Groq's high-performance LLM API for medical data extraction.

## Configuration

### API Setup
```python
# app/services/llm.py
from groq import Groq
from app.config import settings

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.temperature = 0.1  # Low for structured output
        self.max_tokens = 4096

    async def extract(self, prompt: str, transcript: str) -> dict:
        """Extract structured data from transcript."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical data extraction assistant. Extract information accurately and return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt.format(transcript=transcript)
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return self._parse_response(response.choices[0].message.content)

    def _parse_response(self, content: str) -> dict:
        """Parse JSON from LLM response."""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("No valid JSON found in response")
```

## Extraction Prompts

### Patient Details
```python
PATIENT_DETAILS_PROMPT = """
Extract patient details from this doctor-patient conversation.
Return a JSON object with:
- name: string or null
- age: integer or null
- gender: "male", "female", "other", or null
- blood_group: string or null
- weight_kg: number or null
- height_cm: number or null
- contact_number: string or null
- allergies: array of strings or []

Only include fields mentioned in the conversation.
Output valid JSON only, no other text.

Conversation:
{transcript}
"""
```

### Prescription Details
```python
PRESCRIPTION_PROMPT = """
Extract prescription details from this conversation.
Return a JSON object with:
- medications: array of objects with:
  - name: medicine name
  - type: tablet/capsule/syrup/injection/topical
  - dosage: dosage amount
  - frequency: how often
  - timing: when to take
  - relation_to_food: before/after/with
  - duration_days: number of days
- injections: array of objects with:
  - name: injection name
  - dosage: amount
  - frequency: how often
- follow_up: object with date and notes

Output valid JSON only.

Conversation:
{transcript}
"""
```

## Error Handling

```python
from groq import APIError, RateLimitError, APIConnectionError

class LLMService:
    async def extract_with_retry(self, prompt: str, transcript: str, max_retries: int = 3):
        """Extract with automatic retry on failure."""
        for attempt in range(max_retries):
            try:
                return await self.extract(prompt, transcript)
            except RateLimitError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except APIConnectionError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                raise
            except json.JSONDecodeError:
                # Retry with modified prompt for better JSON
                if attempt < max_retries - 1:
                    prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON, nothing else."
                    continue
                raise
```

## Rate Limits

| Plan | Requests/min | Tokens/min |
|------|--------------|------------|
| Free | 30 | 6,000 |
| Pro | 100 | 100,000 |
| Enterprise | Custom | Custom |

## Best Practices

1. **Use low temperature** (0.1) for consistent structured output
2. **Validate JSON** responses before using
3. **Implement retries** for rate limits
4. **Log all requests** for debugging
5. **Cache repeated extractions** if transcript unchanged

## Related Documentation
- [AI Extraction Feature](../features/ai-extraction.md)
- [Backend Architecture](../backend/architecture.md)
