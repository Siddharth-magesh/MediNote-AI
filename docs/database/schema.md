# Database Schema

## Overview
PostgreSQL database with SQLAlchemy ORM. All tables use UUIDs for primary keys.

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    patients     │       │     visits      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ email           │       │ patient_id      │       │ patient_id (FK) │
│ name            │──┐    │ first_name      │──────▶│ doctor_id (FK)  │
│ hashed_password │  │    │ last_name       │       │ visit_date      │
│ hospital_name   │  │    │ date_of_birth   │       │ chief_complaint │
│ qualification   │  │    │ gender          │       │ transcript      │
│ is_active       │  │    │ phone_primary   │       │ status          │
└─────────────────┘  │    │ blood_group     │       └────────┬────────┘
                     │    │ address         │                │
                     │    └─────────────────┘                │
                     │                                       │
                     │    ┌─────────────────┐                │
                     │    │   recordings    │                │
                     │    ├─────────────────┤                │
                     │    │ id (PK)         │◀───────────────┤
                     │    │ visit_id (FK)   │                │
                     └───▶│ doctor_id (FK)  │                │
                          │ audio_url       │                │
                          │ transcript      │                │
                          │ language        │                │
                          │ duration        │                ▼
                          └─────────────────┘       ┌─────────────────┐
                                                    │  prescriptions  │
┌─────────────────┐       ┌─────────────────┐       ├─────────────────┤
│   diet_plans    │       │ care_instructions│      │ id (PK)         │
├─────────────────┤       ├─────────────────┤       │ visit_id (FK)   │
│ id (PK)         │       │ id (PK)         │       │ medications     │
│ visit_id (FK)   │       │ visit_id (FK)   │       │ injections      │
│ breakfast       │       │ recommendations │       │ follow_up_date  │
│ lunch           │       │ exercise_plan   │       │ follow_up_notes │
│ dinner          │       │ warning_signs   │       └─────────────────┘
│ restrictions    │       └─────────────────┘
└─────────────────┘
```

## Table Definitions

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,

    -- Doctor Profile
    hospital_name VARCHAR(255),
    hospital_address TEXT,
    qualification VARCHAR(255),
    registration_number VARCHAR(100),
    department VARCHAR(100),
    signature_url VARCHAR(500),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT users_email_key UNIQUE (email)
);

CREATE INDEX idx_users_email ON users(email);
```

### Patients Table
```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(20) NOT NULL UNIQUE,  -- PAT-2024-00001

    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    blood_group VARCHAR(10),

    -- Contact
    phone_primary VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    email VARCHAR(255),

    -- Address (JSONB)
    address JSONB,
    -- {
    --   "line1": "123 Main St",
    --   "line2": "Apt 4B",
    --   "city": "Mumbai",
    --   "state": "Maharashtra",
    --   "postal_code": "400001",
    --   "country": "India"
    -- }

    -- Emergency Contact (JSONB)
    emergency_contact JSONB,
    -- {
    --   "name": "Jane Doe",
    --   "relation": "Spouse",
    --   "phone": "+919876543210"
    -- }

    -- Medical Info
    allergies TEXT[],
    chronic_conditions TEXT[],
    current_medications TEXT[],

    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, archived

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT patients_patient_id_key UNIQUE (patient_id),
    CONSTRAINT patients_phone_key UNIQUE (phone_primary)
);

CREATE INDEX idx_patients_phone ON patients(phone_primary);
CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_patients_name ON patients USING gin(
    to_tsvector('english', first_name || ' ' || last_name)
);
```

### Visits Table
```sql
CREATE TABLE visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_number VARCHAR(20) NOT NULL UNIQUE,  -- VIS-2024-00001

    -- Relations
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES users(id),

    -- Visit Details
    visit_date TIMESTAMPTZ DEFAULT NOW(),
    chief_complaint TEXT,
    symptoms JSONB,
    -- [
    --   {
    --     "description": "Fever",
    --     "duration": "3 days",
    --     "severity": "moderate"
    --   }
    -- ]

    diagnosis TEXT,
    notes TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, cancelled

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_visits_patient ON visits(patient_id);
CREATE INDEX idx_visits_doctor ON visits(doctor_id);
CREATE INDEX idx_visits_date ON visits(visit_date);
```

### Recordings Table
```sql
CREATE TABLE recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    visit_id UUID NOT NULL REFERENCES visits(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES users(id),

    -- Audio
    audio_url VARCHAR(500) NOT NULL,
    audio_format VARCHAR(20) DEFAULT 'wav',
    duration_seconds INTEGER,
    file_size_bytes BIGINT,

    -- Transcription
    language VARCHAR(10) DEFAULT 'en',
    transcript TEXT,
    transcript_segments JSONB,
    -- [
    --   {
    --     "text": "Hello, how are you?",
    --     "start": 0.0,
    --     "end": 2.5,
    --     "confidence": 0.95
    --   }
    -- ]

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_recordings_visit ON recordings(visit_id);
CREATE INDEX idx_recordings_status ON recordings(status);
```

### Prescriptions Table
```sql
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    visit_id UUID NOT NULL REFERENCES visits(id) ON DELETE CASCADE,

    -- Medications (JSONB array)
    medications JSONB NOT NULL DEFAULT '[]',
    -- [
    --   {
    --     "name": "Paracetamol",
    --     "type": "tablet",
    --     "dosage": "500mg",
    --     "frequency": "twice daily",
    --     "timing": "morning, night",
    --     "relation_to_food": "after",
    --     "duration_days": 5,
    --     "special_instructions": "Take with water"
    --   }
    -- ]

    -- Injections (JSONB array)
    injections JSONB DEFAULT '[]',
    -- [
    --   {
    --     "name": "B12",
    --     "dosage": "1ml",
    --     "frequency": "once a month",
    --     "route": "IM"
    --   }
    -- ]

    -- Lab Tests
    investigations TEXT[],

    -- Follow-up
    follow_up_date DATE,
    follow_up_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_prescriptions_visit ON prescriptions(visit_id);
```

### Diet Plans Table
```sql
CREATE TABLE diet_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    visit_id UUID NOT NULL REFERENCES visits(id) ON DELETE CASCADE,

    -- Meals (JSONB)
    breakfast JSONB,
    -- {
    --   "items": ["Oatmeal", "Fruits", "Milk"],
    --   "timing": "7:00 AM - 9:00 AM",
    --   "portion_guidance": "1 cup oatmeal, 1 fruit",
    --   "notes": "Avoid sugar"
    -- }

    lunch JSONB,
    dinner JSONB,
    snacks JSONB,

    -- Restrictions
    foods_to_avoid TEXT[],
    dietary_restrictions TEXT[],
    hydration_advice TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_diet_plans_visit ON diet_plans(visit_id);
```

### Care Instructions Table
```sql
CREATE TABLE care_instructions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    visit_id UUID NOT NULL REFERENCES visits(id) ON DELETE CASCADE,

    -- Recommendations
    lifestyle_recommendations TEXT[],

    -- Exercise Plan (JSONB)
    exercise_plan JSONB,
    -- {
    --   "type": ["walking", "swimming"],
    --   "frequency": "daily",
    --   "duration": "30 minutes",
    --   "precautions": ["Avoid heavy lifting"]
    -- }

    sleep_recommendations TEXT,
    stress_management TEXT,

    -- Warning Signs
    warning_signs TEXT[],
    when_to_seek_help TEXT[],

    -- Additional Notes
    additional_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_care_instructions_visit ON care_instructions(visit_id);
```

### Reports Table
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_number VARCHAR(20) NOT NULL UNIQUE,  -- RPT-2024-00001

    -- Relations
    visit_id UUID NOT NULL REFERENCES visits(id) ON DELETE CASCADE,

    -- Report Details
    report_type VARCHAR(50) DEFAULT 'full',  -- full, prescription_only, diet_only
    pdf_url VARCHAR(500),
    preview_url VARCHAR(500),

    -- Verification
    qr_code_data TEXT,
    checksum VARCHAR(64),

    -- Status
    status VARCHAR(20) DEFAULT 'generated',  -- generated, downloaded, shared

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    downloaded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_reports_visit ON reports(visit_id);
```

## SQLAlchemy Models

### Base Model
```python
# app/models/base.py
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Patient Model
```python
# app/models/patient.py
from sqlalchemy import Column, String, Date, ARRAY, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin

class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String(20), unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    blood_group = Column(String(10))

    phone_primary = Column(String(20), unique=True, nullable=False, index=True)
    phone_secondary = Column(String(20))
    email = Column(String(255))

    address = Column(JSONB)
    emergency_contact = Column(JSONB)

    allergies = Column(ARRAY(String))
    chronic_conditions = Column(ARRAY(String))
    current_medications = Column(ARRAY(String))

    status = Column(String(20), default="active")

    # Relationships
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return 0
```

### Visit Model
```python
# app/models/visit.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import Base, TimestampMixin

class Visit(Base, TimestampMixin):
    __tablename__ = "visits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_number = Column(String(20), unique=True, nullable=False)

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    visit_date = Column(DateTime(timezone=True), server_default=func.now())
    chief_complaint = Column(Text)
    symptoms = Column(JSONB)
    diagnosis = Column(Text)
    notes = Column(Text)

    status = Column(String(20), default="in_progress")

    # Relationships
    patient = relationship("Patient", back_populates="visits")
    doctor = relationship("User", back_populates="visits")
    recording = relationship("Recording", back_populates="visit", uselist=False)
    prescription = relationship("Prescription", back_populates="visit", uselist=False)
    diet_plan = relationship("DietPlan", back_populates="visit", uselist=False)
    care_instructions = relationship("CareInstructions", back_populates="visit", uselist=False)
    reports = relationship("Report", back_populates="visit")
```

## Migrations

### Initial Migration
```python
# alembic/versions/001_initial.py
"""Initial migration

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('hospital_name', sa.String(255)),
        sa.Column('qualification', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    # Patients table
    op.create_table(
        'patients',
        # ... columns
    )

    # ... other tables

def downgrade():
    op.drop_table('reports')
    op.drop_table('care_instructions')
    op.drop_table('diet_plans')
    op.drop_table('prescriptions')
    op.drop_table('recordings')
    op.drop_table('visits')
    op.drop_table('patients')
    op.drop_table('users')
```

## Database Session

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

## Related Documentation
- [Backend Architecture](../backend/architecture.md)
- [API Documentation](../api/overview.md)
- [Migrations Guide](./migrations.md)
