# Frontend Architecture

## Overview
Modern React-based frontend built with Next.js 14, TypeScript, and Tailwind CSS.

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Next.js 14 | React framework with App Router |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| shadcn/ui | UI components |
| Zustand | Global state |
| TanStack Query | Server state |
| React Hook Form | Forms |
| Zod | Validation |

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/              # Auth route group
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/         # Protected routes
│   │   │   ├── dashboard/
│   │   │   ├── patients/
│   │   │   ├── recording/
│   │   │   ├── reports/
│   │   │   ├── settings/
│   │   │   └── layout.tsx
│   │   ├── api/                 # API routes (if needed)
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   └── globals.css
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── common/              # Shared components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── auth/                # Auth components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── AuthGuard.tsx
│   │   ├── patients/            # Patient components
│   │   │   ├── PatientSearch.tsx
│   │   │   ├── PatientCard.tsx
│   │   │   ├── PatientForm.tsx
│   │   │   ├── PatientProfile.tsx
│   │   │   └── PatientHistory.tsx
│   │   ├── recording/           # Recording components
│   │   │   ├── RecordButton.tsx
│   │   │   ├── PauseButton.tsx
│   │   │   ├── WaveformDisplay.tsx
│   │   │   ├── TranscriptDisplay.tsx
│   │   │   └── LanguageSelector.tsx
│   │   └── reports/             # Report components
│   │       ├── ReportPreview.tsx
│   │       ├── ReportEditor.tsx
│   │       └── PrescriptionTable.tsx
│   │
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── usePatients.ts
│   │   ├── useRecording.ts
│   │   ├── useWebSocket.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── lib/                     # Utilities
│   │   ├── api.ts              # API client
│   │   ├── utils.ts            # Helper functions
│   │   ├── constants.ts        # App constants
│   │   └── validators.ts       # Zod schemas
│   │
│   ├── stores/                  # Zustand stores
│   │   ├── authStore.ts
│   │   ├── patientStore.ts
│   │   ├── recordingStore.ts
│   │   └── uiStore.ts
│   │
│   ├── types/                   # TypeScript types
│   │   ├── api.ts
│   │   ├── patient.ts
│   │   ├── prescription.ts
│   │   └── user.ts
│   │
│   └── styles/                  # Additional styles
│       └── print.css
│
├── public/
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.local
├── .env.example
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── README.md
```

## Component Architecture

### Component Hierarchy
```
App
├── RootLayout
│   ├── Providers (Auth, Query, Theme)
│   └── Children
│       ├── AuthLayout
│       │   ├── LoginPage
│       │   └── RegisterPage
│       └── DashboardLayout
│           ├── Header
│           ├── Sidebar
│           └── MainContent
│               ├── DashboardPage
│               ├── PatientsPage
│               ├── RecordingPage
│               ├── ReportsPage
│               └── SettingsPage
```

### Component Guidelines

#### 1. Atomic Design
```
atoms/       → Button, Input, Label
molecules/   → FormField, SearchBar, PatientCard
organisms/   → PatientForm, RecordingPanel, ReportPreview
templates/   → DashboardLayout, AuthLayout
pages/       → Dashboard, Patients, Recording
```

#### 2. Component Template
```typescript
// components/patients/PatientCard.tsx
'use client';

import { memo } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Patient } from '@/types/patient';
import { cn } from '@/lib/utils';

interface PatientCardProps {
  patient: Patient;
  onClick?: (patient: Patient) => void;
  className?: string;
}

export const PatientCard = memo(function PatientCard({
  patient,
  onClick,
  className,
}: PatientCardProps) {
  return (
    <Card
      className={cn('cursor-pointer hover:shadow-md transition', className)}
      onClick={() => onClick?.(patient)}
    >
      <CardHeader>
        <h3>{patient.first_name} {patient.last_name}</h3>
        <p className="text-sm text-muted-foreground">{patient.patient_id}</p>
      </CardHeader>
      <CardContent>
        <p>{patient.phone_primary}</p>
        <p>{patient.age} years, {patient.gender}</p>
      </CardContent>
    </Card>
  );
});
```

## State Management

### Global State (Zustand)
```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (credentials) => {
        const response = await api.auth.login(credentials);
        set({
          user: response.user,
          token: response.token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    { name: 'auth-storage' }
  )
);
```

### Server State (TanStack Query)
```typescript
// hooks/usePatients.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function usePatients(searchQuery?: string) {
  return useQuery({
    queryKey: ['patients', searchQuery],
    queryFn: () => api.patients.search(searchQuery),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.patients.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
}
```

## API Client

```typescript
// lib/api.ts
import axios from 'axios';

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export const api = {
  auth: {
    login: (data: LoginCredentials) => client.post('/auth/login', data),
    register: (data: RegisterData) => client.post('/auth/register', data),
  },
  patients: {
    search: (query?: string) => client.get('/patients/search', { params: { q: query } }),
    get: (id: string) => client.get(`/patients/${id}`),
    create: (data: CreatePatientData) => client.post('/patients', data),
    update: (id: string, data: UpdatePatientData) => client.patch(`/patients/${id}`, data),
  },
  // ... other endpoints
};
```

## Routing

### Route Groups
```
(auth)/      → Public auth pages
(dashboard)/ → Protected dashboard pages
```

### Route Protection
```typescript
// components/auth/AuthGuard.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null; // Or loading spinner
  }

  return <>{children}</>;
}
```

## Forms & Validation

### Form with React Hook Form + Zod
```typescript
// components/patients/PatientForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const patientSchema = z.object({
  first_name: z.string().min(2).max(50),
  last_name: z.string().min(2).max(50),
  phone_primary: z.string().regex(/^\+?[0-9]{10,15}$/),
  date_of_birth: z.string().datetime(),
  gender: z.enum(['male', 'female', 'other']),
  blood_group: z.string().optional(),
});

type PatientFormData = z.infer<typeof patientSchema>;

export function PatientForm({ onSubmit }: { onSubmit: (data: PatientFormData) => void }) {
  const form = useForm<PatientFormData>({
    resolver: zodResolver(patientSchema),
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

## Styling Guidelines

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          foreground: '#ffffff',
        },
        // ... other colors
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

### CSS Variables (shadcn/ui)
```css
/* globals.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... */
  }
}
```

## Performance Optimization

### Code Splitting
```typescript
// Dynamic imports for large components
const ReportPreview = dynamic(() => import('@/components/reports/ReportPreview'), {
  loading: () => <LoadingSpinner />,
});
```

### Image Optimization
```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="MediNote AI"
  width={200}
  height={50}
  priority
/>
```

### Memoization
```typescript
const MemoizedPatientCard = memo(PatientCard);
const memoizedValue = useMemo(() => computeExpensiveValue(data), [data]);
const memoizedCallback = useCallback(() => doSomething(id), [id]);
```

## Testing Strategy

### Unit Tests (Vitest)
```typescript
// tests/unit/PatientCard.test.tsx
import { render, screen } from '@testing-library/react';
import { PatientCard } from '@/components/patients/PatientCard';

describe('PatientCard', () => {
  it('renders patient name', () => {
    const patient = { first_name: 'John', last_name: 'Doe', ... };
    render(<PatientCard patient={patient} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)
```typescript
// tests/e2e/recording.spec.ts
test('complete recording flow', async ({ page }) => {
  await page.goto('/recording');
  await page.click('[data-testid="record-button"]');
  // ... test recording flow
});
```

## Related Documentation
- [Component Library](./components.md)
- [State Management](./state-management.md)
- [API Integration](./api-integration.md)
