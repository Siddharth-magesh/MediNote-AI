# Security Documentation

## Overview
Security measures and best practices for MediNote-AI, with considerations for healthcare data protection.

## Security Principles

1. **Defense in Depth** - Multiple security layers
2. **Least Privilege** - Minimal access rights
3. **Data Encryption** - At rest and in transit
4. **Audit Logging** - Track all sensitive operations
5. **Input Validation** - Sanitize all inputs

---

## Authentication Security

### Password Policy
```python
# Minimum requirements
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGIT = True
REQUIRE_SPECIAL_CHAR = True

# Password validation
def validate_password(password: str) -> bool:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

### Password Hashing
```python
# Using bcrypt with cost factor 12
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
```

### JWT Configuration
```python
# Token configuration
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Token payload
{
    "sub": "user_id",
    "exp": expiration_timestamp,
    "iat": issued_at_timestamp,
    "type": "access|refresh",
    "jti": "unique_token_id"  # For token revocation
}
```

### Account Protection
- Account lockout after 5 failed login attempts
- Lockout duration: 15 minutes
- Email verification required
- Password reset via secure link (expires in 1 hour)

---

## Data Encryption

### At Rest
```python
# Database encryption
# PostgreSQL with pgcrypto extension

# Encrypting sensitive fields
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Encrypt patient contact info, medical history, etc.
```

### In Transit
- TLS 1.3 for all connections
- HTTPS enforced (redirect HTTP to HTTPS)
- Secure WebSocket (WSS) for real-time features

### Encryption Keys
- Stored in environment variables or secrets manager
- Rotated every 90 days
- Different keys for different data types

---

## API Security

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply rate limits
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login():
    ...

@app.post("/api/v1/auth/register")
@limiter.limit("3/minute")
async def register():
    ...
```

### Input Validation
```python
from pydantic import BaseModel, validator, EmailStr
import bleach

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        # Remove HTML tags and limit length
        v = bleach.clean(v, strip=True)
        if len(v) > 100:
            raise ValueError('Name too long')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters')
        return v
```

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://medinote.ai"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Security Headers
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

---

## Role-Based Access Control (RBAC)

### User Roles
```python
from enum import Enum

class UserRole(str, Enum):
    DOCTOR = "doctor"
    ADMIN = "admin"
    STAFF = "staff"

# Permissions
PERMISSIONS = {
    UserRole.DOCTOR: [
        "read:patients",
        "write:patients",
        "read:own_recordings",
        "write:own_recordings",
        "read:own_reports",
        "write:own_reports",
    ],
    UserRole.ADMIN: [
        "read:patients",
        "write:patients",
        "read:all_recordings",
        "write:all_recordings",
        "read:all_reports",
        "write:all_reports",
        "manage:users",
    ],
    UserRole.STAFF: [
        "read:patients",
        "read:reports",
    ],
}
```

### Permission Decorator
```python
from functools import wraps
from fastapi import HTTPException, status

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            user_permissions = PERMISSIONS.get(current_user.role, [])
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.delete("/patients/{patient_id}")
@require_permission("write:patients")
async def delete_patient(patient_id: str, current_user: CurrentUser):
    ...
```

---

## Audit Logging

### Audit Log Schema
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID, ForeignKey("users.id"))
    action = Column(String(50))  # create, read, update, delete
    resource_type = Column(String(50))  # patient, recording, report
    resource_id = Column(UUID)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_body = Column(JSONB)  # Encrypted sensitive data
    response_status = Column(Integer)
```

### Audit Middleware
```python
class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Log sensitive endpoints
        if request.url.path.startswith("/api/v1/patients"):
            await self.log_audit(
                request=request,
                response=response,
                resource_type="patient"
            )

        return response

    async def log_audit(self, request, response, resource_type):
        audit_log = AuditLog(
            user_id=request.state.user_id if hasattr(request.state, 'user_id') else None,
            action=self.get_action(request.method),
            resource_type=resource_type,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            response_status=response.status_code,
        )
        # Save to database
```

---

## Data Privacy (HIPAA Considerations)

### PHI (Protected Health Information) Handling
- Encrypt all PHI at rest
- Minimize PHI collection
- Implement data retention policies
- Provide patient data access/deletion

### Data Retention
```python
# Data retention policies
RETENTION_POLICIES = {
    "recordings": 365,      # 1 year
    "reports": 365 * 7,     # 7 years
    "audit_logs": 365 * 7,  # 7 years
    "session_data": 1,      # 1 day
}

# Scheduled cleanup task
@celery_app.task
def cleanup_expired_data():
    for resource, days in RETENTION_POLICIES.items():
        delete_older_than(resource, days)
```

### Data Export (Patient Request)
```python
@router.get("/patients/{patient_id}/export")
async def export_patient_data(patient_id: str, current_user: CurrentUser):
    """Export all patient data (GDPR/HIPAA compliance)"""
    patient = await get_patient(patient_id)

    # Collect all patient data
    data = {
        "personal_info": patient.dict(),
        "visits": await get_patient_visits(patient_id),
        "recordings": await get_patient_recordings(patient_id),
        "reports": await get_patient_reports(patient_id),
    }

    # Generate secure download
    return create_secure_download(data)
```

---

## File Upload Security

```python
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".pdf", ".png", ".jpg"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

async def validate_upload(file: UploadFile):
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "File type not allowed")

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    # Validate file content (magic bytes)
    if not validate_file_signature(content, ext):
        raise HTTPException(400, "Invalid file content")

    await file.seek(0)  # Reset file pointer
    return file
```

---

## Security Checklist

### Development
- [ ] Environment variables for secrets
- [ ] No hardcoded credentials
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention

### Deployment
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Database connections encrypted

### Operations
- [ ] Regular security updates
- [ ] Log monitoring
- [ ] Backup encryption
- [ ] Access key rotation
- [ ] Penetration testing

---

## Incident Response

### Security Incident Procedure
1. **Detect** - Monitor logs and alerts
2. **Contain** - Isolate affected systems
3. **Investigate** - Determine scope and impact
4. **Eradicate** - Remove threat
5. **Recover** - Restore services
6. **Review** - Post-incident analysis

### Contact
- Security Team: security@medinote.ai
- Emergency: +1-XXX-XXX-XXXX

---

## Related Documentation
- [Authentication](../backend/authentication.md)
- [API Security](../api/security.md)
- [Deployment](../deployment/overview.md)
