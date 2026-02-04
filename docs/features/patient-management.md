# Patient Management Feature

## Overview
Comprehensive patient lifecycle management including registration, search, history tracking, and data management.

## Patient Data Model

### Core Patient Entity
```typescript
interface Patient {
  id: string;                    // UUID
  patient_id: string;            // Human-readable ID (PAT-2024-001)
  created_at: Date;
  updated_at: Date;

  // Personal Information
  first_name: string;
  last_name: string;
  date_of_birth: Date;
  gender: 'male' | 'female' | 'other';
  blood_group: string | null;

  // Contact Information
  phone_primary: string;
  phone_secondary: string | null;
  email: string | null;
  address: Address;

  // Emergency Contact
  emergency_contact: EmergencyContact | null;

  // Medical Information
  allergies: string[];
  chronic_conditions: string[];
  current_medications: string[];

  // Status
  status: 'active' | 'inactive' | 'archived';
}

interface Address {
  line1: string;
  line2: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

interface EmergencyContact {
  name: string;
  relation: string;
  phone: string;
}
```

## User Flows

### Patient Registration Flow
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Patient Registration Flow                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Click "New Patient"                                              │
│         │                                                            │
│         ▼                                                            │
│  2. Enter Phone Number                                               │
│         │                                                            │
│         ▼                                                            │
│  3. System checks if phone exists ──── Yes ──→ Show existing patient │
│         │                                       "Did you mean...?"   │
│         No                                                           │
│         ▼                                                            │
│  4. Display Registration Form                                        │
│     - Personal Details                                               │
│     - Contact Information                                            │
│     - Medical History (optional)                                     │
│         │                                                            │
│         ▼                                                            │
│  5. Validate & Submit                                                │
│         │                                                            │
│         ▼                                                            │
│  6. Generate Patient ID (PAT-YYYY-XXXXX)                            │
│         │                                                            │
│         ▼                                                            │
│  7. Redirect to Patient Profile / Start Recording                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Patient Search Flow
```
┌─────────────────────────────────────────────────────────────────────┐
│                      Patient Search Flow                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Search Input: [___________________________] [Search]                │
│                                                                      │
│  Search by:  ○ Phone  ○ Name  ○ Patient ID  ○ All                   │
│                                                                      │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  Results:                                                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ PAT-2024-001 │ John Doe │ M/40 │ 9876543210 │ [View] [Select] │  │
│  │ PAT-2024-015 │ Jane Doe │ F/35 │ 9876543211 │ [View] [Select] │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  [No results? Add New Patient]                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Create Patient
```http
POST /api/v1/patients
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1984-05-15",
  "gender": "male",
  "phone_primary": "+919876543210",
  "blood_group": "O+",
  "address": {
    "line1": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "country": "India"
  }
}

Response: 201 Created
{
  "id": "uuid",
  "patient_id": "PAT-2024-00123",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

### Search Patients
```http
GET /api/v1/patients/search?q={query}&field={field}&limit=20&offset=0

Response:
{
  "results": [...],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

### Get Patient Details
```http
GET /api/v1/patients/{patient_id}

Response:
{
  "patient": {...},
  "recent_visits": [...],
  "stats": {
    "total_visits": 5,
    "last_visit": "2024-01-10"
  }
}
```

### Update Patient
```http
PATCH /api/v1/patients/{patient_id}
Content-Type: application/json

{
  "phone_secondary": "+919876543211",
  "allergies": ["Penicillin", "Dust"]
}

Response: 200 OK
{
  "patient": {...}
}
```

### Get Patient History
```http
GET /api/v1/patients/{patient_id}/history?limit=10

Response:
{
  "visits": [
    {
      "id": "uuid",
      "date": "2024-01-15",
      "doctor": {...},
      "chief_complaint": "Fever and cough",
      "prescription": {...},
      "reports": [...]
    }
  ]
}
```

## Patient ID Generation

### Format
```
PAT-{YEAR}-{SEQUENCE}

Examples:
- PAT-2024-00001
- PAT-2024-12345
```

### Generation Logic
```python
def generate_patient_id() -> str:
    year = datetime.now().year
    sequence = get_next_sequence(f"patient_{year}")
    return f"PAT-{year}-{sequence:05d}"
```

## Search Implementation

### Search Strategy
1. **Exact Match**: Phone number, Patient ID
2. **Partial Match**: Name (first/last)
3. **Fuzzy Match**: Handle typos in names

### Search Indexing
```sql
-- PostgreSQL Full-Text Search
CREATE INDEX idx_patient_search ON patients
USING gin(to_tsvector('english', first_name || ' ' || last_name));

-- Phone Index
CREATE INDEX idx_patient_phone ON patients(phone_primary);

-- Patient ID Index
CREATE INDEX idx_patient_pid ON patients(patient_id);
```

## Patient Profile View

### Sections
1. **Header**: Photo, Name, ID, Status
2. **Demographics**: Age, Gender, Blood Group, Contact
3. **Medical Summary**: Allergies, Chronic Conditions
4. **Visit History**: Timeline of all visits
5. **Documents**: Uploaded reports, prescriptions
6. **Actions**: Edit, Archive, Export

### Visit Timeline
```
┌─────────────────────────────────────────────────────────────────────┐
│                      Visit History Timeline                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Jan 15, 2024                                                        │
│  ├─ Dr. John Smith - General Medicine                               │
│  │  Chief Complaint: Fever and body pain                            │
│  │  Diagnosis: Viral fever                                          │
│  │  [View Prescription] [View Recording]                            │
│  │                                                                   │
│  Dec 28, 2023                                                        │
│  ├─ Dr. Jane Doe - Internal Medicine                                │
│  │  Chief Complaint: Routine checkup                                │
│  │  [View Prescription] [View Recording]                            │
│  │                                                                   │
│  Nov 10, 2023                                                        │
│  └─ ...                                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Privacy & Consent

### Consent Types
- [ ] Treatment consent
- [ ] Data storage consent
- [ ] Communication consent (SMS/Email)
- [ ] Data sharing consent

### Data Access Logging
All patient data access is logged:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "doc_uuid",
  "patient_id": "pat_uuid",
  "action": "view",
  "resource": "patient_profile",
  "ip_address": "192.168.1.1"
}
```

## Validation Rules

| Field | Validation |
|-------|------------|
| first_name | 2-50 chars, letters only |
| last_name | 2-50 chars, letters only |
| phone_primary | Valid phone format, unique |
| date_of_birth | Not future date, reasonable age |
| email | Valid email format |
| postal_code | Valid format for country |

## Duplicate Detection

### Detection Criteria
- Same phone number
- Same name + date of birth
- Similar name (Levenshtein distance < 3) + same DOB

### Handling Duplicates
```
┌─────────────────────────────────────────────────────────────────────┐
│            Potential Duplicate Detected                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  A patient with similar details already exists:                      │
│                                                                      │
│  Existing: John Doe (PAT-2024-00123)                                │
│  Phone: 9876543210                                                   │
│  DOB: 1984-05-15                                                    │
│                                                                      │
│  [Use Existing Patient]  [Create Anyway]  [Cancel]                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Testing Checklist

- [ ] Patient creation with all fields
- [ ] Patient creation with minimal fields
- [ ] Duplicate phone detection
- [ ] Search by phone (exact)
- [ ] Search by name (partial)
- [ ] Search with no results
- [ ] Patient profile loads correctly
- [ ] Visit history displays correctly
- [ ] Patient update works
- [ ] Patient archive works
- [ ] Data export works

## Related Documentation
- [Database Schema](../database/schema.md)
- [API Documentation](../api/patients.md)
- [Privacy & Compliance](../security/privacy.md)
