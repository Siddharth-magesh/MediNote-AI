# Backend Architecture

## Overview
FastAPI-based backend with async support, following clean architecture principles.

## Technology Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| Python 3.11+ | Programming language |
| SQLAlchemy 2.0 | ORM (async) |
| PostgreSQL | Primary database |
| Redis | Caching & sessions |
| Celery | Background tasks |
| Pydantic v2 | Validation |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration management
│   │
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main API router
│   │       ├── auth.py         # Auth endpoints
│   │       ├── patients.py     # Patient endpoints
│   │       ├── recording.py    # Recording endpoints
│   │       ├── reports.py      # Report endpoints
│   │       └── users.py        # User endpoints
│   │
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── middleware.py       # Custom middleware
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py             # Base model
│   │   ├── user.py             # User model
│   │   ├── patient.py          # Patient model
│   │   ├── visit.py            # Visit model
│   │   ├── prescription.py     # Prescription model
│   │   └── recording.py        # Recording model
│   │
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── prescription.py
│   │   ├── recording.py
│   │   └── report.py
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication service
│   │   ├── patient.py          # Patient service
│   │   ├── recording.py        # Recording service
│   │   ├── transcription.py    # Speech-to-text
│   │   ├── extraction.py       # AI extraction
│   │   └── report.py           # Report generation
│   │
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   ├── user.py
│   │   ├── patient.py
│   │   └── visit.py
│   │
│   ├── db/                      # Database
│   │   ├── __init__.py
│   │   ├── session.py          # Database session
│   │   └── migrations/         # Alembic migrations
│   │
│   ├── workers/                 # Celery tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Celery configuration
│   │   └── tasks.py            # Background tasks
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── storage.py          # File storage
│       ├── pdf.py              # PDF generation
│       └── helpers.py          # Helper functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                     # Migrations
│   ├── versions/
│   └── env.py
│
├── scripts/
│   ├── seed_db.py              # Database seeding
│   └── create_admin.py         # Create admin user
│
├── .env.example
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  Auth    │ │ Patients │ │Recording │ │     Reports      │   │
│  │  Router  │ │  Router  │ │  Router  │ │     Router       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                      Service Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  Auth    │ │ Patient  │ │Transcript│ │    Extraction    │   │
│  │ Service  │ │ Service  │ │ Service  │ │    Service       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    Repository Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  User    │ │ Patient  │ │  Visit   │ │   Prescription   │   │
│  │  Repo    │ │   Repo   │ │   Repo   │ │      Repo        │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                      Model Layer                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  User    │ │ Patient  │ │  Visit   │ │   Prescription   │   │
│  │  Model   │ │  Model   │ │  Model   │ │     Model        │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                      Database Layer                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL + Redis                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Entry (`main.py`)
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import engine
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="MediNote AI API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2. Configuration (`config.py`)
```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MediNote AI"
    DEBUG: bool = False
    SECRET_KEY: str

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs
    GROQ_API_KEY: str
    GOOGLE_CLOUD_PROJECT: str

    # Storage
    STORAGE_BACKEND: str = "local"  # local, s3, minio
    STORAGE_PATH: str = "./storage"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 3. Dependencies (`deps.py`)
```python
# app/api/deps.py
from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.db.session import async_session
from app.models.user import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> Generator[AsyncSession, None, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user

# Type aliases for cleaner code
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### 4. Base Repository
```python
# app/repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: str) -> Optional[ModelType]:
        return await self.db.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: str) -> bool:
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
```

### 5. Service Example
```python
# app/services/patient.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.repositories.patient import PatientRepository

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PatientRepository(db)

    async def create_patient(self, data: PatientCreate) -> Patient:
        # Check for duplicate phone
        existing = await self.get_by_phone(data.phone_primary)
        if existing:
            raise ValueError("Patient with this phone already exists")

        # Generate patient ID
        patient_id = await self._generate_patient_id()

        patient_data = data.model_dump()
        patient_data["patient_id"] = patient_id

        return await self.repo.create(patient_data)

    async def get_patient(self, id: str) -> Optional[Patient]:
        return await self.repo.get(id)

    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        result = await self.db.execute(
            select(Patient).where(Patient.phone_primary == phone)
        )
        return result.scalar_one_or_none()

    async def search_patients(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Patient]:
        stmt = select(Patient).where(
            or_(
                Patient.first_name.ilike(f"%{query}%"),
                Patient.last_name.ilike(f"%{query}%"),
                Patient.phone_primary.contains(query),
                Patient.patient_id.ilike(f"%{query}%"),
            )
        ).offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def _generate_patient_id(self) -> str:
        from datetime import datetime
        year = datetime.now().year

        result = await self.db.execute(
            select(Patient).where(
                Patient.patient_id.like(f"PAT-{year}-%")
            ).order_by(Patient.created_at.desc()).limit(1)
        )
        last_patient = result.scalar_one_or_none()

        if last_patient:
            last_num = int(last_patient.patient_id.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"PAT-{year}-{new_num:05d}"
```

### 6. API Endpoint Example
```python
# app/api/v1/patients.py
from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from app.api.deps import DBSession, CurrentUser
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)
from app.services.patient import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create a new patient."""
    service = PatientService(db)
    try:
        patient = await service.create_patient(data)
        return patient
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=PatientListResponse)
async def search_patients(
    db: DBSession,
    current_user: CurrentUser,
    q: str = Query(default="", min_length=0),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Search patients by name, phone, or ID."""
    service = PatientService(db)
    patients = await service.search_patients(q, limit, offset)
    return {"results": patients, "total": len(patients)}

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get patient by ID."""
    service = PatientService(db)
    patient = await service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update patient details."""
    service = PatientService(db)
    patient = await service.update_patient(patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
```

## Error Handling

```python
# app/core/exceptions.py
from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundError(AppException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)

class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)

class ForbiddenError(AppException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)

class ValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_422_UNPROCESSABLE_ENTITY)
```

## Background Tasks (Celery)

```python
# app/workers/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "medinote",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# app/workers/tasks.py
from app.workers.celery_app import celery_app

@celery_app.task
def process_audio_transcription(recording_id: str):
    """Background task to transcribe audio."""
    # Implementation
    pass

@celery_app.task
def generate_report_pdf(report_id: str):
    """Background task to generate PDF."""
    # Implementation
    pass
```

## Related Documentation
- [API Documentation](../api/overview.md)
- [Database Schema](../database/schema.md)
- [Authentication](./authentication.md)
