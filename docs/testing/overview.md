# Testing Documentation

## Overview
Comprehensive testing strategy for MediNote-AI covering unit, integration, and E2E tests.

## Testing Stack

| Type | Tool | Location |
|------|------|----------|
| Backend Unit | pytest | `backend/tests/unit/` |
| Backend Integration | pytest + httpx | `backend/tests/integration/` |
| Frontend Unit | Vitest | `frontend/tests/unit/` |
| Frontend Component | React Testing Library | `frontend/tests/components/` |
| E2E | Playwright | `frontend/tests/e2e/` |

---

## Backend Testing

### Project Structure
```
backend/tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_auth.py
│   ├── test_patient.py
│   ├── test_extraction.py
│   └── test_validators.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_patient_api.py
│   ├── test_recording_api.py
│   └── test_report_api.py
└── fixtures/
    ├── transcripts.json
    └── test_audio.wav
```

### Conftest Setup
```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.main import app
from app.db.session import get_db
from app.models.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_medinote"

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(engine):
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def authenticated_client(client):
    # Register and login
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Test Doctor",
        "password": "TestPass123!",
    })
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "TestPass123!",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
```

### Unit Test Example
```python
# backend/tests/unit/test_auth.py
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token

class TestPasswordHashing:
    def test_hash_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("WrongPassword", hashed) is False

class TestJWTToken:
    def test_create_access_token(self):
        user_id = "test-user-id"
        token = create_access_token(user_id)
        assert token is not None
        assert len(token) > 0
```

### Integration Test Example
```python
# backend/tests/integration/test_patient_api.py
import pytest

class TestPatientAPI:
    @pytest.mark.asyncio
    async def test_create_patient(self, authenticated_client):
        response = await authenticated_client.post("/api/v1/patients", json={
            "first_name": "John",
            "last_name": "Doe",
            "phone_primary": "+919876543210",
            "date_of_birth": "1984-05-15",
            "gender": "male",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert "patient_id" in data
        assert data["patient_id"].startswith("PAT-")

    @pytest.mark.asyncio
    async def test_create_patient_duplicate_phone(self, authenticated_client):
        # Create first patient
        await authenticated_client.post("/api/v1/patients", json={
            "first_name": "John",
            "last_name": "Doe",
            "phone_primary": "+919876543210",
        })

        # Try to create with same phone
        response = await authenticated_client.post("/api/v1/patients", json={
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_primary": "+919876543210",
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_search_patients(self, authenticated_client):
        # Create test patient
        await authenticated_client.post("/api/v1/patients", json={
            "first_name": "John",
            "last_name": "Smith",
            "phone_primary": "+919876543211",
        })

        response = await authenticated_client.get("/api/v1/patients/search?q=John")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
```

---

## Frontend Testing

### Project Structure
```
frontend/tests/
├── setup.ts              # Test setup
├── unit/
│   ├── authStore.test.ts
│   ├── api.test.ts
│   └── validators.test.ts
├── components/
│   ├── LoginForm.test.tsx
│   ├── PatientCard.test.tsx
│   └── RecordButton.test.tsx
└── e2e/
    ├── auth.spec.ts
    ├── patient.spec.ts
    └── recording.spec.ts
```

### Vitest Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Component Test Example
```typescript
// frontend/tests/components/PatientCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { PatientCard } from '@/components/patients/PatientCard';

const mockPatient = {
  id: '1',
  patient_id: 'PAT-2024-00001',
  first_name: 'John',
  last_name: 'Doe',
  phone_primary: '+919876543210',
  age: 40,
  gender: 'male',
};

describe('PatientCard', () => {
  it('renders patient name', () => {
    render(<PatientCard patient={mockPatient} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('renders patient ID', () => {
    render(<PatientCard patient={mockPatient} />);
    expect(screen.getByText('PAT-2024-00001')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<PatientCard patient={mockPatient} onClick={handleClick} />);

    fireEvent.click(screen.getByRole('article'));
    expect(handleClick).toHaveBeenCalledWith(mockPatient);
  });
});
```

### E2E Test Example
```typescript
// frontend/tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid email or password')).toBeVisible();
  });

  test('should logout', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Logout');

    await expect(page).toHaveURL('/login');
  });
});
```

---

## Running Tests

### Backend
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific file
pytest tests/unit/test_auth.py

# Run with verbose
pytest -v

# Run only failed
pytest --lf
```

### Frontend
```bash
# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E in headed mode
npm run test:e2e -- --headed

# Run specific test file
npm run test -- tests/components/PatientCard.test.tsx
```

---

## Coverage Goals

| Area | Target |
|------|--------|
| Backend Unit | 80% |
| Backend Integration | 70% |
| Frontend Unit | 70% |
| Frontend Components | 60% |
| E2E Critical Paths | 100% |

---

## Related Documentation
- [Testing Tracking](../tasks/testing-tracking.md)
- [CI/CD Pipeline](../deployment/overview.md)
