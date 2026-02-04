# Frontend Pages

## Page Overview

| Route | Page | Description |
|-------|------|-------------|
| `/` | Landing | Public landing page |
| `/login` | Login | Doctor authentication |
| `/register` | Register | Doctor registration |
| `/dashboard` | Dashboard | Main dashboard |
| `/patients` | Patients | Patient management |
| `/patients/[id]` | Patient Detail | Patient profile |
| `/patients/new` | New Patient | Patient registration |
| `/recording` | Recording | Voice recording |
| `/reports` | Reports | Report history |
| `/reports/[id]` | Report Detail | Single report view |
| `/settings` | Settings | User settings |

---

## Page Implementations

### 1. Landing Page (`/`)
```typescript
// app/page.tsx
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Stethoscope, Mic, FileText, Shield } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/10 to-background">
      {/* Hero Section */}
      <section className="container py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight mb-6">
          MediNote AI
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Transform doctor-patient conversations into structured medical reports
          with AI-powered precision.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/register">Get Started</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Sign In</Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={Mic}
            title="Voice Recording"
            description="Record consultations with real-time transcription in multiple languages."
          />
          <FeatureCard
            icon={FileText}
            title="Smart Reports"
            description="AI extracts prescriptions, diet plans, and care instructions automatically."
          />
          <FeatureCard
            icon={Shield}
            title="Secure & Compliant"
            description="HIPAA-ready with encrypted storage and access controls."
          />
        </div>
      </section>
    </div>
  );
}
```

### 2. Login Page (`/login`)
```typescript
// app/(auth)/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Loader2 } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError(null);
    try {
      await login(data);
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
          <CardDescription>Sign in to continue to MediNote AI</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              {error && (
                <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                  {error}
                </div>
              )}

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="doctor@hospital.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Sign In
              </Button>
            </form>
          </Form>

          <div className="mt-6 text-center text-sm">
            Don't have an account?{' '}
            <Link href="/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 3. Dashboard Page (`/dashboard`)
```typescript
// app/(dashboard)/dashboard/page.tsx
'use client';

import { useAuthStore } from '@/stores/authStore';
import { useRecentPatients, useTodayStats } from '@/hooks/useDashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PatientCard } from '@/components/patients/PatientCard';
import { Users, Mic, FileText, Clock } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data: stats } = useTodayStats();
  const { data: recentPatients } = useRecentPatients();

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold">Welcome back, {user?.name}</h1>
        <p className="text-muted-foreground">Here's your overview for today</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Patients"
          value={stats?.totalPatients || 0}
          icon={Users}
        />
        <StatCard
          title="Today's Recordings"
          value={stats?.todayRecordings || 0}
          icon={Mic}
        />
        <StatCard
          title="Reports Generated"
          value={stats?.reportsGenerated || 0}
          icon={FileText}
        />
        <StatCard
          title="Avg. Session Time"
          value={`${stats?.avgSessionTime || 0} min`}
          icon={Clock}
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Button asChild>
            <Link href="/recording">
              <Mic className="mr-2 h-4 w-4" />
              Start Recording
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/patients/new">
              <Users className="mr-2 h-4 w-4" />
              Add Patient
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Recent Patients */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Patients</CardTitle>
          <Button variant="link" asChild>
            <Link href="/patients">View All</Link>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {recentPatients?.map((patient) => (
              <PatientCard key={patient.id} patient={patient} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ title, value, icon: Icon }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
          <Icon className="h-8 w-8 text-muted-foreground" />
        </div>
      </CardContent>
    </Card>
  );
}
```

### 4. Recording Page (`/recording`)
```typescript
// app/(dashboard)/recording/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { PatientSearch } from '@/components/patients/PatientSearch';
import { RecordingPanel } from '@/components/recording/RecordingPanel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, User } from 'lucide-react';
import { Patient } from '@/types/patient';

type Step = 'select-patient' | 'recording';

export default function RecordingPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('select-patient');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const handlePatientSelect = (patient: Patient) => {
    setSelectedPatient(patient);
    setStep('recording');
  };

  const handleRecordingComplete = (transcript: string) => {
    // Navigate to report generation with transcript
    router.push(`/reports/new?patient=${selectedPatient?.id}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        {step === 'recording' && (
          <Button variant="ghost" onClick={() => setStep('select-patient')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        )}
        <h1 className="text-2xl font-bold">
          {step === 'select-patient' ? 'Select Patient' : 'Recording Session'}
        </h1>
      </div>

      {/* Step 1: Patient Selection */}
      {step === 'select-patient' && (
        <Card>
          <CardHeader>
            <CardTitle>Search for a patient</CardTitle>
          </CardHeader>
          <CardContent>
            <PatientSearch
              onSelect={handlePatientSelect}
              onAddNew={() => router.push('/patients/new?return=/recording')}
            />
          </CardContent>
        </Card>
      )}

      {/* Step 2: Recording */}
      {step === 'recording' && selectedPatient && (
        <div className="space-y-6">
          {/* Patient Info Banner */}
          <Card>
            <CardContent className="py-4">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">
                    {selectedPatient.first_name} {selectedPatient.last_name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedPatient.patient_id} • {selectedPatient.age} years • {selectedPatient.gender}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recording Panel */}
          <RecordingPanel
            patientId={selectedPatient.id}
            onComplete={handleRecordingComplete}
          />
        </div>
      )}
    </div>
  );
}
```

### 5. Patients Page (`/patients`)
```typescript
// app/(dashboard)/patients/page.tsx
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePatients } from '@/hooks/usePatients';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PatientCard } from '@/components/patients/PatientCard';
import { Search, UserPlus, Loader2 } from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce';

export default function PatientsPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const { data, isLoading } = usePatients(debouncedSearch);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Patients</h1>
        <Button asChild>
          <Link href="/patients/new">
            <UserPlus className="mr-2 h-4 w-4" />
            Add Patient
          </Link>
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search patients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Patient Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data?.results.map((patient) => (
            <Link key={patient.id} href={`/patients/${patient.id}`}>
              <PatientCard patient={patient} />
            </Link>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && data?.results.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No patients found</p>
          <Button asChild>
            <Link href="/patients/new">Add New Patient</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
```

### 6. Settings Page (`/settings`)
```typescript
// app/(dashboard)/settings/page.tsx
'use client';

import { useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Doctor Profile</CardTitle>
              <CardDescription>
                Update your professional information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" defaultValue={user?.name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="qualification">Qualification</Label>
                  <Input id="qualification" placeholder="MBBS, MD" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="registration">Registration Number</Label>
                  <Input id="registration" placeholder="MCI-12345" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Input id="department" placeholder="General Medicine" />
                </div>
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="account">
          {/* Account settings */}
        </TabsContent>

        <TabsContent value="preferences">
          {/* Preference settings */}
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## Page Layout Structure

### Dashboard Layout
```typescript
// app/(dashboard)/layout.tsx
import { AuthGuard } from '@/components/auth/AuthGuard';
import { Header } from '@/components/common/Header';
import { Sidebar } from '@/components/common/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
```

### Auth Layout
```typescript
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 to-background">
      {children}
    </div>
  );
}
```

## Related Documentation
- [Frontend Architecture](./architecture.md)
- [Components](./components.md)
- [Routing](./routing.md)
