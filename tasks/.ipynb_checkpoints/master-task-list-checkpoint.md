# MediNote-AI Master Task List

## Project Overview
Complete rebuild of MediNote-AI with modern architecture and best practices.

---

## Phase 1: Project Setup & Infrastructure
**Status:** NOT STARTED
**Reference Docs:** [Architecture](../docs/architecture/overview.md), [Deployment](../docs/deployment/overview.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P1-001 | Create project repository structure | Pending | - | Backend + Frontend folders |
| P1-002 | Setup Docker Compose for development | Pending | - | PostgreSQL, Redis, MinIO |
| P1-003 | Configure environment variables | Pending | - | .env.example file |
| P1-004 | Setup CI/CD pipeline (GitHub Actions) | Pending | - | Test, Build, Deploy |
| P1-005 | Configure linting and formatting | Pending | - | ESLint, Prettier, Black, Ruff |

---

## Phase 2: Backend Foundation
**Status:** NOT STARTED
**Reference Docs:** [Backend Architecture](../docs/backend/architecture.md), [Database Schema](../docs/database/schema.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P2-001 | Initialize FastAPI project | Pending | - | Project structure |
| P2-002 | Setup SQLAlchemy with async support | Pending | - | Database session |
| P2-003 | Create database models | Pending | - | User, Patient, Visit, etc. |
| P2-004 | Setup Alembic migrations | Pending | - | Initial migration |
| P2-005 | Implement authentication system | Pending | - | JWT, login, register |
| P2-006 | Create base repository pattern | Pending | - | CRUD operations |
| P2-007 | Setup Pydantic schemas | Pending | - | Request/Response models |
| P2-008 | Implement error handling | Pending | - | Custom exceptions |
| P2-009 | Add logging configuration | Pending | - | Structured logging |
| P2-010 | Write unit tests for auth | Pending | - | Pytest |

---

## Phase 3: Patient Management API
**Status:** NOT STARTED
**Reference Docs:** [Patient Management](../docs/features/patient-management.md), [API Overview](../docs/api/overview.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P3-001 | Patient CRUD endpoints | Pending | - | Create, Read, Update, Delete |
| P3-002 | Patient search functionality | Pending | - | By name, phone, ID |
| P3-003 | Patient ID generation | Pending | - | PAT-YYYY-XXXXX format |
| P3-004 | Duplicate detection | Pending | - | Phone number check |
| P3-005 | Patient history endpoint | Pending | - | List all visits |
| P3-006 | Write integration tests | Pending | - | API tests |

---

## Phase 4: Recording & Transcription
**Status:** NOT STARTED
**Reference Docs:** [Audio Recording](../docs/features/audio-recording.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P4-001 | Setup WebSocket endpoint | Pending | - | Real-time audio streaming |
| P4-002 | Integrate Google Speech-to-Text | Pending | - | STT service |
| P4-003 | Implement audio chunk processing | Pending | - | Streaming transcription |
| P4-004 | Audio file storage (MinIO/S3) | Pending | - | Save recordings |
| P4-005 | Transcript storage | Pending | - | Save to database |
| P4-006 | Multi-language support | Pending | - | en, hi, ta |
| P4-007 | Translation service | Pending | - | Non-English to English |
| P4-008 | Recording session management | Pending | - | Start, stop, pause |

---

## Phase 5: AI Extraction Service
**Status:** NOT STARTED
**Reference Docs:** [AI Extraction](../docs/features/ai-extraction.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P5-001 | Setup Groq API integration | Pending | - | LLM client |
| P5-002 | Patient details extraction | Pending | - | Name, age, etc. |
| P5-003 | Prescription extraction | Pending | - | Medications, dosages |
| P5-004 | Diet plan extraction | Pending | - | Meals, restrictions |
| P5-005 | Care instructions extraction | Pending | - | Lifestyle advice |
| P5-006 | JSON validation & parsing | Pending | - | Structured output |
| P5-007 | BMI calculation | Pending | - | Auto-calculate |
| P5-008 | Confidence scoring | Pending | - | Flag low confidence |
| P5-009 | Error handling & retries | Pending | - | API resilience |

---

## Phase 6: Report Generation
**Status:** NOT STARTED
**Reference Docs:** [Report Generation](../docs/features/report-generation.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P6-001 | Create HTML report templates | Pending | - | Jinja2 templates |
| P6-002 | PDF generation (WeasyPrint) | Pending | - | HTML to PDF |
| P6-003 | QR code generation | Pending | - | Verification link |
| P6-004 | Report storage | Pending | - | Save PDF files |
| P6-005 | Download endpoint | Pending | - | Serve PDF |
| P6-006 | Preview endpoint | Pending | - | HTML preview |
| P6-007 | Template customization | Pending | - | Doctor branding |

---

## Phase 7: Frontend Foundation
**Status:** NOT STARTED
**Reference Docs:** [Frontend Architecture](../docs/frontend/architecture.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P7-001 | Initialize Next.js project | Pending | - | TypeScript, Tailwind |
| P7-002 | Setup shadcn/ui components | Pending | - | Install components |
| P7-003 | Configure Zustand store | Pending | - | Auth, UI state |
| P7-004 | Setup TanStack Query | Pending | - | API data fetching |
| P7-005 | Create API client | Pending | - | Axios wrapper |
| P7-006 | Implement auth context | Pending | - | Token management |
| P7-007 | Create layout components | Pending | - | Header, Sidebar |

---

## Phase 8: Frontend Pages
**Status:** NOT STARTED
**Reference Docs:** [Frontend Pages](../docs/frontend/pages.md), [Components](../docs/frontend/components.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P8-001 | Landing page | Pending | - | Public page |
| P8-002 | Login page | Pending | - | Auth form |
| P8-003 | Register page | Pending | - | Doctor registration |
| P8-004 | Dashboard page | Pending | - | Overview, stats |
| P8-005 | Patients list page | Pending | - | Search, list |
| P8-006 | Patient detail page | Pending | - | Profile, history |
| P8-007 | New patient form | Pending | - | Registration form |
| P8-008 | Recording page | Pending | - | Audio recording UI |
| P8-009 | Reports list page | Pending | - | Report history |
| P8-010 | Report preview page | Pending | - | View, download |
| P8-011 | Settings page | Pending | - | User profile |

---

## Phase 9: Recording UI
**Status:** NOT STARTED
**Reference Docs:** [Audio Recording](../docs/features/audio-recording.md), [Components](../docs/frontend/components.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P9-001 | Recording button component | Pending | - | Start/stop |
| P9-002 | Waveform visualization | Pending | - | Audio levels |
| P9-003 | Live transcript display | Pending | - | Real-time text |
| P9-004 | Language selector | Pending | - | Dropdown |
| P9-005 | WebSocket integration | Pending | - | Audio streaming |
| P9-006 | Recording state management | Pending | - | Zustand store |
| P9-007 | Error handling UI | Pending | - | Connection errors |

---

## Phase 10: Testing & QA
**Status:** NOT STARTED
**Reference Docs:** [Testing](../docs/testing/overview.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P10-001 | Backend unit tests | Pending | - | Pytest |
| P10-002 | Backend integration tests | Pending | - | API tests |
| P10-003 | Frontend unit tests | Pending | - | Vitest |
| P10-004 | E2E tests | Pending | - | Playwright |
| P10-005 | Performance testing | Pending | - | Load tests |
| P10-006 | Security audit | Pending | - | OWASP checks |

---

## Phase 11: Deployment
**Status:** NOT STARTED
**Reference Docs:** [Deployment](../docs/deployment/overview.md)

| Task ID | Task | Status | Assignee | Notes |
|---------|------|--------|----------|-------|
| P11-001 | Production Docker images | Pending | - | Optimized builds |
| P11-002 | Nginx configuration | Pending | - | Reverse proxy |
| P11-003 | SSL certificate setup | Pending | - | Let's Encrypt |
| P11-004 | Database backup setup | Pending | - | Automated backups |
| P11-005 | Monitoring setup | Pending | - | Prometheus/Grafana |
| P11-006 | Logging aggregation | Pending | - | Centralized logs |

---

## Progress Summary

| Phase | Total Tasks | Completed | In Progress | Pending |
|-------|-------------|-----------|-------------|---------|
| Phase 1: Setup | 5 | 0 | 0 | 5 |
| Phase 2: Backend | 10 | 0 | 0 | 10 |
| Phase 3: Patients | 6 | 0 | 0 | 6 |
| Phase 4: Recording | 8 | 0 | 0 | 8 |
| Phase 5: AI | 9 | 0 | 0 | 9 |
| Phase 6: Reports | 7 | 0 | 0 | 7 |
| Phase 7: Frontend | 7 | 0 | 0 | 7 |
| Phase 8: Pages | 11 | 0 | 0 | 11 |
| Phase 9: Recording UI | 7 | 0 | 0 | 7 |
| Phase 10: Testing | 6 | 0 | 0 | 6 |
| Phase 11: Deployment | 6 | 0 | 0 | 6 |
| **TOTAL** | **82** | **0** | **0** | **82** |

---

## Legend
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Done and tested
- **Blocked**: Waiting on dependency

---

## Notes
- Update this file as tasks are completed
- Reference the appropriate documentation for each phase
- Create detailed sub-task files for complex tasks
