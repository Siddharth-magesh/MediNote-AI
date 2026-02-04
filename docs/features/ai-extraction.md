# AI Data Extraction Feature

## Overview
Intelligent extraction of structured medical data from conversation transcripts using Large Language Models.

## Extraction Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Transcript │ →  │  Pre-proc   │ →  │  LLM Call   │ →  │  Validate   │
│    Input    │    │  & Clean    │    │  (Groq)     │    │  & Parse    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Store     │ ←  │  Calculate  │ ←  │  Enrich     │ ←  │  Structured │
│   to DB     │    │  BMI, etc   │    │  Data       │    │    JSON     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Extracted Data Schemas

### 1. Patient Personal Details
```json
{
  "name": "string",
  "age": "integer",
  "gender": "enum(male, female, other)",
  "blood_group": "enum(A+, A-, B+, B-, O+, O-, AB+, AB-)",
  "weight_kg": "float",
  "height_cm": "float",
  "contact_number": "string",
  "allergies": ["string"],
  "emergency_contact": {
    "name": "string",
    "relation": "string",
    "phone": "string"
  }
}
```

### 2. Symptoms & Complaints
```json
{
  "chief_complaint": "string",
  "symptoms": [
    {
      "description": "string",
      "duration": "string",
      "severity": "enum(mild, moderate, severe)",
      "location": "string | null",
      "aggravating_factors": ["string"],
      "relieving_factors": ["string"]
    }
  ],
  "history_of_present_illness": "string"
}
```

### 3. Prescription Details
```json
{
  "medications": [
    {
      "name": "string",
      "type": "enum(tablet, capsule, syrup, injection, topical, other)",
      "dosage": "string",
      "frequency": "string",
      "timing": "enum(morning, afternoon, evening, night, as_needed)",
      "relation_to_food": "enum(before, after, with, any)",
      "duration_days": "integer",
      "special_instructions": "string | null"
    }
  ],
  "injections": [
    {
      "name": "string",
      "dosage": "string",
      "frequency": "string",
      "route": "enum(IM, IV, SC)",
      "duration": "string"
    }
  ],
  "investigations": ["string"],
  "follow_up": {
    "duration": "string",
    "date": "date | null",
    "notes": "string | null"
  }
}
```

### 4. Diet Plan
```json
{
  "breakfast": {
    "items": ["string"],
    "timing": "string",
    "portion_guidance": "string | null"
  },
  "lunch": {
    "items": ["string"],
    "timing": "string",
    "portion_guidance": "string | null"
  },
  "dinner": {
    "items": ["string"],
    "timing": "string",
    "portion_guidance": "string | null"
  },
  "snacks": {
    "items": ["string"],
    "timing": "string"
  },
  "foods_to_avoid": ["string"],
  "hydration_advice": "string",
  "dietary_restrictions": ["string"]
}
```

### 5. Care Management
```json
{
  "lifestyle_recommendations": ["string"],
  "exercise_plan": {
    "type": ["string"],
    "frequency": "string",
    "duration": "string",
    "precautions": ["string"]
  },
  "sleep_recommendations": "string",
  "stress_management": "string",
  "warning_signs": ["string"],
  "when_to_seek_help": ["string"],
  "additional_notes": "string"
}
```

## LLM Prompts

### Patient Details Extraction Prompt
```
You are a medical data extraction assistant. Extract patient details from the following doctor-patient conversation.

Return a JSON object with these exact fields:
- name: Patient's full name (string)
- age: Patient's age in years (integer)
- gender: "male", "female", or "other"
- blood_group: Blood group if mentioned (A+, A-, B+, B-, O+, O-, AB+, AB-)
- weight_kg: Weight in kilograms (number)
- height_cm: Height in centimeters (number)
- contact_number: Phone number (string)
- allergies: List of known allergies (array of strings)

If a field is not mentioned, use null.
Do not include any text outside the JSON object.

Conversation:
{transcript}
```

### Prescription Extraction Prompt
```
You are a medical prescription extraction assistant. Extract all medication and treatment details from the following conversation.

Return a JSON object with:
- medications: Array of prescribed medicines with:
  - name: Medicine name
  - type: tablet/capsule/syrup/injection/topical/other
  - dosage: Dosage amount (e.g., "500mg", "10ml")
  - frequency: How often (e.g., "twice daily", "once a day")
  - timing: morning/afternoon/evening/night/as_needed
  - relation_to_food: before/after/with/any
  - duration_days: Number of days to take
  - special_instructions: Any special notes

- injections: Array of injections with:
  - name: Injection name
  - dosage: Amount
  - frequency: How often
  - route: IM/IV/SC
  - duration: How long

- investigations: Array of tests/investigations ordered
- follow_up: When to return for follow-up

If not mentioned, use null for optional fields.
Only output valid JSON.

Conversation:
{transcript}
```

## Validation Rules

### Patient Details
| Field | Validation |
|-------|------------|
| age | 0-150 |
| weight_kg | 0.5-500 |
| height_cm | 20-300 |
| contact_number | Valid phone format |
| blood_group | Must be valid type |

### Prescription
| Field | Validation |
|-------|------------|
| medication.name | Non-empty string |
| medication.dosage | Contains number |
| duration_days | 1-365 |

## Calculated Fields

### BMI Calculation
```python
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    category = (
        "Underweight" if bmi < 18.5 else
        "Normal" if bmi < 25 else
        "Overweight" if bmi < 30 else
        "Obese"
    )

    return {
        "value": round(bmi, 2),
        "category": category
    }
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| LLM returns invalid JSON | Retry with refined prompt |
| Missing required fields | Mark for manual review |
| Validation failure | Log and request correction |
| API timeout | Retry with backoff |
| Rate limit | Queue and retry later |

## Confidence Scoring

Each extraction includes a confidence score:
- **High (0.9-1.0)**: All fields clearly stated
- **Medium (0.7-0.9)**: Some inference required
- **Low (<0.7)**: Significant ambiguity

Low confidence extractions are flagged for doctor review.

## API Endpoints

### Extract All Data
```http
POST /api/v1/extraction/full
Content-Type: application/json

{
  "transcript": "Doctor: Hello...",
  "visit_id": "uuid",
  "language": "en"
}

Response:
{
  "patient_details": {...},
  "symptoms": {...},
  "prescription": {...},
  "diet_plan": {...},
  "care_management": {...},
  "confidence_scores": {
    "patient_details": 0.95,
    "prescription": 0.88,
    ...
  },
  "requires_review": false
}
```

## Performance Metrics

| Metric | Target |
|--------|--------|
| Extraction latency | < 5 seconds |
| Accuracy (validated) | > 95% |
| JSON parse success | > 99% |

## Related Documentation
- [LLM Integration](../integrations/groq-llm.md)
- [Data Validation](../backend/validation.md)
- [Report Generation](./report-generation.md)
