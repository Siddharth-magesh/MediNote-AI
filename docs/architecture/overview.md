# MediNote-AI Architecture Overview

## System Architecture

MediNote-AI is a modern, scalable healthcare documentation platform built with a microservices-inspired architecture, separating concerns between frontend, backend API, AI services, and data storage.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Next.js Frontend (React)                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │   │
│  │  │  Auth    │  │ Dashboard│  │ Recording│  │ Report Generator │    │   │
│  │  │  Module  │  │  Module  │  │  Module  │  │     Module       │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend Server                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │   │
│  │  │  Auth    │  │ Patient  │  │  Audio   │  │    AI/LLM        │    │   │
│  │  │  API     │  │   API    │  │   API    │  │   Service API    │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│   DATABASE LAYER     │  │  EXTERNAL APIs   │  │    FILE STORAGE      │
│  ┌────────────────┐  │  │  ┌────────────┐  │  │  ┌────────────────┐  │
│  │   PostgreSQL   │  │  │  │ Groq LLM   │  │  │  │  MinIO/S3      │  │
│  │   (Primary DB) │  │  │  │   API      │  │  │  │  (Audio/PDF)   │  │
│  └────────────────┘  │  │  └────────────┘  │  │  └────────────────┘  │
│  ┌────────────────┐  │  │  ┌────────────┐  │  └──────────────────────┘
│  │     Redis      │  │  │  │  Google    │  │
│  │   (Caching)    │  │  │  │ Speech API │  │
│  └────────────────┘  │  │  └────────────┘  │
└──────────────────────┘  └──────────────────┘
```

## Core Components

### 1. Frontend (Next.js + React + TypeScript)
- **Technology**: Next.js 14 with App Router
- **UI Framework**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand / React Query
- **Real-time**: WebSocket for live transcription

### 2. Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Authentication**: JWT + OAuth2 (Google/Microsoft)
- **Validation**: Pydantic v2
- **Background Tasks**: Celery + Redis

### 3. Database Layer
- **Primary**: PostgreSQL 15+
- **Cache**: Redis 7+
- **ORM**: SQLAlchemy 2.0 with async support

### 4. AI/ML Services
- **LLM Provider**: Groq (Llama-3.3-70B)
- **Speech-to-Text**: Google Cloud Speech / Whisper
- **Translation**: Google Cloud Translate

### 5. File Storage
- **Development**: Local filesystem
- **Production**: MinIO / AWS S3

## Design Principles

### 1. Separation of Concerns
- Each module handles a specific domain
- Clear boundaries between layers
- Independent scaling capabilities

### 2. Security First
- End-to-end encryption for sensitive data
- HIPAA compliance considerations
- Role-based access control (RBAC)

### 3. Scalability
- Stateless API design
- Horizontal scaling support
- Database connection pooling

### 4. Reliability
- Comprehensive error handling
- Automatic retries for external services
- Health check endpoints

## Data Flow

### Recording & Transcription Flow
```
User clicks Record → WebSocket opens → Audio chunks sent to backend
    → Audio saved to storage → Speech-to-Text API called
    → Real-time transcript returned → Displayed to user
```

### Report Generation Flow
```
User clicks Generate → Backend receives transcript
    → LLM extracts structured data → Data validated & saved
    → Report template populated → PDF generated → Returned to user
```

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Frontend Framework | Next.js | SSR, great DX, built-in routing |
| Backend Framework | FastAPI | Async, auto-docs, type hints |
| Database | PostgreSQL | ACID compliance, JSON support |
| Cache | Redis | Fast, pub/sub for real-time |
| LLM | Groq | Fast inference, good Llama models |
| File Storage | MinIO | S3-compatible, self-hosted option |

## Environment Configuration

```
Development  → Local PostgreSQL, Local Redis, Local MinIO
Staging      → Docker Compose stack
Production   → Kubernetes / Docker Swarm
```

## Related Documentation
- [Frontend Architecture](../frontend/architecture.md)
- [Backend Architecture](../backend/architecture.md)
- [Database Schema](../database/schema.md)
- [API Documentation](../api/overview.md)
