# API Documentation

## Overview
RESTful API built with FastAPI. All endpoints return JSON responses.

## Base URL
```
Development: http://localhost:8000/api/v1
Production:  https://api.medinote.ai/api/v1
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Response Format

### Success Response
```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Paginated Response
```json
{
  "results": [...],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

---

## API Endpoints Summary

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new doctor |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout |
| POST | `/auth/password-reset` | Request password reset |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update current user |
| POST | `/users/me/signature` | Upload signature |

### Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients` | List all patients |
| POST | `/patients` | Create new patient |
| GET | `/patients/search` | Search patients |
| GET | `/patients/{id}` | Get patient by ID |
| PATCH | `/patients/{id}` | Update patient |
| DELETE | `/patients/{id}` | Delete patient |
| GET | `/patients/{id}/history` | Get patient history |

### Recording
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recording/start` | Start recording session |
| POST | `/recording/{id}/stop` | Stop recording |
| GET | `/recording/{id}` | Get recording details |
| WS | `/ws/recording/{id}` | WebSocket for live transcription |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reports/generate` | Generate report from visit |
| GET | `/reports` | List reports |
| GET | `/reports/{id}` | Get report details |
| GET | `/reports/{id}/download` | Download PDF |
| GET | `/reports/{id}/preview` | Preview report |

### Visits
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visits` | List visits |
| POST | `/visits` | Create new visit |
| GET | `/visits/{id}` | Get visit details |
| PATCH | `/visits/{id}` | Update visit |

---

## Detailed Endpoint Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "name": "Dr. John Smith",
  "password": "SecurePass123!",
  "hospital_name": "City Hospital",
  "qualification": "MBBS, MD",
  "registration_number": "MCI-12345"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "doctor@hospital.com",
  "name": "Dr. John Smith",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=doctor@hospital.com&password=SecurePass123!

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Patient Endpoints

#### Create Patient
```http
POST /api/v1/patients
Authorization: Bearer <token>
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
  },
  "allergies": ["Penicillin"],
  "emergency_contact": {
    "name": "Jane Doe",
    "relation": "Spouse",
    "phone": "+919876543211"
  }
}

Response: 201 Created
{
  "id": "uuid",
  "patient_id": "PAT-2024-00001",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

#### Search Patients
```http
GET /api/v1/patients/search?q=john&limit=20&offset=0
Authorization: Bearer <token>

Response: 200 OK
{
  "results": [
    {
      "id": "uuid",
      "patient_id": "PAT-2024-00001",
      "first_name": "John",
      "last_name": "Doe",
      "phone_primary": "+919876543210",
      "age": 40,
      "gender": "male"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### Recording Endpoints

#### Start Recording Session
```http
POST /api/v1/recording/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "uuid",
  "language": "en"
}

Response: 201 Created
{
  "session_id": "uuid",
  "websocket_url": "wss://api.medinote.ai/ws/recording/uuid",
  "status": "active"
}
```

#### WebSocket Protocol
```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://api.medinote.ai/ws/recording/{session_id}');

// Send audio chunk
ws.send(JSON.stringify({
  type: 'audio_chunk',
  data: 'base64_encoded_audio',
  sequence: 1
}));

// Receive transcript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   type: 'transcript',
  //   text: 'Hello, how are you?',
  //   is_final: false,
  //   confidence: 0.95
  // }
};
```

#### Stop Recording
```http
POST /api/v1/recording/{session_id}/stop
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "audio_url": "/storage/recordings/uuid.wav",
  "transcript": "Doctor: Hello, how are you today?...",
  "duration_seconds": 300,
  "status": "completed"
}
```

### Report Endpoints

#### Generate Report
```http
POST /api/v1/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "visit_id": "uuid",
  "report_type": "full",
  "include_sections": ["prescription", "diet_plan", "care_instructions"]
}

Response: 202 Accepted
{
  "report_id": "uuid",
  "status": "processing",
  "message": "Report generation started"
}
```

#### Download Report
```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer <token>

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="prescription_PAT001_2024-01-15.pdf"

<binary PDF data>
```

### Visit Endpoints

#### Create Visit
```http
POST /api/v1/visits
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "uuid",
  "chief_complaint": "Fever and body pain for 3 days",
  "symptoms": [
    {
      "description": "Fever",
      "duration": "3 days",
      "severity": "moderate"
    },
    {
      "description": "Body pain",
      "duration": "3 days",
      "severity": "mild"
    }
  ]
}

Response: 201 Created
{
  "id": "uuid",
  "visit_number": "VIS-2024-00001",
  "patient_id": "uuid",
  "doctor_id": "uuid",
  "visit_date": "2024-01-15T10:00:00Z",
  "chief_complaint": "Fever and body pain for 3 days",
  "status": "in_progress"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Access token has expired |
| `AUTH_INVALID_TOKEN` | 401 | Invalid token format |
| `FORBIDDEN` | 403 | Not enough permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `DUPLICATE_ENTRY` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| `/auth/login` | 5 requests/minute |
| `/auth/register` | 3 requests/minute |
| `/recording/*` | 10 requests/minute |
| All other endpoints | 100 requests/minute |

---

## OpenAPI Specification

Full OpenAPI spec available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON: `http://localhost:8000/api/v1/openapi.json`

---

## Related Documentation
- [Backend Architecture](../backend/architecture.md)
- [Authentication](../backend/authentication.md)
- [WebSocket Guide](./websocket.md)
