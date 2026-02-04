# Technology Stack

## Frontend Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.x | React framework with SSR/SSG |
| React | 18.x | UI component library |
| TypeScript | 5.x | Type safety |

### UI & Styling
| Technology | Version | Purpose |
|------------|---------|---------|
| Tailwind CSS | 3.x | Utility-first CSS |
| shadcn/ui | latest | Pre-built accessible components |
| Lucide React | latest | Icon library |
| Framer Motion | 10.x | Animations |

### State & Data
| Technology | Version | Purpose |
|------------|---------|---------|
| Zustand | 4.x | Global state management |
| TanStack Query | 5.x | Server state & caching |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Schema validation |

### Audio & Media
| Technology | Version | Purpose |
|------------|---------|---------|
| Web Audio API | native | Audio recording |
| RecordRTC | 5.x | Cross-browser recording |

### Development Tools
| Technology | Purpose |
|------------|---------|
| ESLint | Code linting |
| Prettier | Code formatting |
| Husky | Git hooks |

---

## Backend Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.109+ | Web framework |
| Uvicorn | 0.27+ | ASGI server |
| Gunicorn | 21.x | Process manager |

### Database & ORM
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15+ | Primary database |
| SQLAlchemy | 2.0+ | ORM with async support |
| Alembic | 1.13+ | Database migrations |
| asyncpg | 0.29+ | Async PostgreSQL driver |

### Caching & Queue
| Technology | Version | Purpose |
|------------|---------|---------|
| Redis | 7+ | Caching & pub/sub |
| Celery | 5.x | Background task queue |

### Authentication
| Technology | Version | Purpose |
|------------|---------|---------|
| python-jose | 3.x | JWT handling |
| passlib | 1.7+ | Password hashing |
| bcrypt | 4.x | Secure hashing algorithm |

### AI/ML Integration
| Technology | Version | Purpose |
|------------|---------|---------|
| Groq SDK | latest | LLM API client |
| google-cloud-speech | 2.x | Speech-to-Text |
| google-cloud-translate | 3.x | Translation service |
| openai-whisper | latest | Alternative STT (local) |

### File Processing
| Technology | Version | Purpose |
|------------|---------|---------|
| Pillow | 10.x | Image manipulation |
| ReportLab | 4.x | PDF generation |
| WeasyPrint | 60.x | HTML to PDF |
| pydub | 0.25+ | Audio processing |

### Validation & Serialization
| Technology | Version | Purpose |
|------------|---------|---------|
| Pydantic | 2.x | Data validation |
| python-multipart | 0.x | File uploads |

---

## Infrastructure

### Containerization
| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24+ | Container runtime |
| Docker Compose | 2.x | Multi-container apps |

### Storage
| Technology | Version | Purpose |
|------------|---------|---------|
| MinIO | latest | S3-compatible storage |
| AWS S3 | - | Production file storage |

### Monitoring & Logging
| Technology | Purpose |
|------------|---------|
| Prometheus | Metrics collection |
| Grafana | Visualization |
| Sentry | Error tracking |
| structlog | Structured logging |

### CI/CD
| Technology | Purpose |
|------------|---------|
| GitHub Actions | CI/CD pipelines |
| Docker Hub | Container registry |

---

## Development Environment

### Required Software
```bash
# Core requirements
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+ (or via Docker)
- Redis 7+ (or via Docker)
```

### Recommended IDE Extensions
```
VS Code:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Thunder Client (API testing)
```

---

## Version Compatibility Matrix

| Component | Min Version | Recommended | Max Tested |
|-----------|-------------|-------------|------------|
| Python | 3.11 | 3.12 | 3.12 |
| Node.js | 18 | 20 LTS | 21 |
| PostgreSQL | 14 | 16 | 16 |
| Redis | 6 | 7 | 7 |
| Docker | 23 | 24 | 25 |

---

## External Services

### Required API Keys
| Service | Purpose | Required |
|---------|---------|----------|
| Groq | LLM inference | Yes |
| Google Cloud | Speech-to-Text, Translate | Yes |

### Optional Services
| Service | Purpose |
|---------|---------|
| Sentry | Error tracking |
| SendGrid | Email notifications |
| Twilio | SMS notifications |
