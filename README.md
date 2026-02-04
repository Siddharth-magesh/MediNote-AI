# MediNote-AI

**AI-Powered Healthcare Documentation Platform**

Transform doctor-patient conversations into structured medical reports with AI precision.

---

## Overview

MediNote-AI is a modern healthcare documentation platform that:
- Records doctor-patient consultations
- Transcribes conversations in real-time (multi-language support)
- Extracts structured medical data using AI
- Generates professional prescription reports

---

## Quick Links

### Documentation
- [Architecture Overview](./docs/architecture/overview.md)
- [Technology Stack](./docs/architecture/tech-stack.md)
- [Features Overview](./docs/features/overview.md)
- [API Documentation](./docs/api/overview.md)
- [Deployment Guide](./docs/deployment/overview.md)

### Development
- [Frontend Architecture](./docs/frontend/architecture.md)
- [Backend Architecture](./docs/backend/architecture.md)
- [Database Schema](./docs/database/schema.md)
- [Security Guidelines](./docs/security/overview.md)

### Task Tracking
- [Master Task List](./tasks/master-task-list.md)
- [Frontend Tracking](./tasks/frontend-tracking.md)
- [Backend Tracking](./tasks/backend-tracking.md)
- [Testing Tracking](./tasks/testing-tracking.md)
- [Deployment Tracking](./tasks/deployment-tracking.md)

---

## Technology Stack

### Frontend
- Next.js 14 (React)
- TypeScript
- Tailwind CSS + shadcn/ui
- Zustand + TanStack Query

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL + Redis

### AI/ML
- Groq (Llama-3.3-70B)
- Google Cloud Speech-to-Text
- Google Cloud Translate

---

## Project Structure

```
MediNote-AI/
├── docs/
│   ├── architecture/      # System architecture docs
│   ├── features/          # Feature specifications
│   ├── frontend/          # Frontend documentation
│   ├── backend/           # Backend documentation
│   ├── database/          # Database schema & migrations
│   ├── api/               # API documentation
│   ├── deployment/        # Deployment guides
│   ├── security/          # Security documentation
│   ├── testing/           # Testing guidelines
│   └── integrations/      # Third-party integrations
├── tasks/
│   ├── master-task-list.md
│   ├── frontend-tracking.md
│   ├── backend-tracking.md
│   ├── testing-tracking.md
│   └── deployment-tracking.md
└── README.md
```

---

## Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project Setup & Infrastructure | Not Started |
| 2 | Backend Foundation | Not Started |
| 3 | Patient Management API | Not Started |
| 4 | Recording & Transcription | Not Started |
| 5 | AI Extraction Service | Not Started |
| 6 | Report Generation | Not Started |
| 7 | Frontend Foundation | Not Started |
| 8 | Frontend Pages | Not Started |
| 9 | Recording UI | Not Started |
| 10 | Testing & QA | Not Started |
| 11 | Deployment | Not Started |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+ (or via Docker)
- Redis 7+ (or via Docker)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/medinote-ai.git
cd medinote-ai

# Start infrastructure
docker compose up -d postgres redis minio

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables
See `.env.example` for required environment variables.

---

## Key Features

### Voice Recording
- Real-time audio capture
- Multi-language support (English, Hindi, Tamil)
- Live transcription display
- Noise suppression

### AI Data Extraction
- Patient information extraction
- Prescription details parsing
- Diet plan generation
- Care instructions extraction

### Report Generation
- Professional PDF reports
- Customizable templates
- QR code verification
- Digital signatures

### Patient Management
- Patient registration
- Medical history tracking
- Visit management
- Search functionality

---

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User authentication |
| `/patients` | GET/POST | Patient management |
| `/recording/start` | POST | Start recording |
| `/reports/generate` | POST | Generate report |

Full API documentation: [API Overview](./docs/api/overview.md)

---

## Contributing

1. Check the task tracking files for available tasks
2. Reference the appropriate documentation
3. Follow the coding guidelines
4. Write tests for new features
5. Update documentation as needed

---

## License

MIT License - See LICENSE file for details.

---

## Contact

- **Project Lead:** [Name]
- **Documentation:** [docs@medinote.ai]
- **Support:** [support@medinote.ai]
