# Frontend Components

## UI Component Library (shadcn/ui)

### Installation
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card dialog table form
```

### Required Components
| Component | Purpose |
|-----------|---------|
| Button | Primary, Secondary, Destructive actions |
| Input | Text, Number, Phone inputs |
| Select | Dropdowns (Language, Blood Group) |
| Card | Patient cards, Dashboard cards |
| Dialog | Modals (Confirmation, Forms) |
| Table | Prescription table, Patient list |
| Form | Patient registration, Settings |
| Toast | Notifications |
| Tabs | Report sections |
| Badge | Status indicators |
| Avatar | User/Patient photos |
| Skeleton | Loading states |

---

## Custom Components

### 1. Header Component
```typescript
// components/common/Header.tsx
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Stethoscope, Bell, Settings, LogOut } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuthStore();
  const [notifications, setNotifications] = useState(3);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="p-2 bg-primary rounded-lg">
            <Stethoscope className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold">MediNote AI</span>
        </Link>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            {notifications > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-destructive text-xs flex items-center justify-center text-white">
                {notifications}
              </span>
            )}
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar_url} />
                  <AvatarFallback>{user?.name?.charAt(0)}</AvatarFallback>
                </Avatar>
                <span className="hidden md:inline">{user?.name}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
```

### 2. Sidebar Component
```typescript
// components/common/Sidebar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  Mic,
  FileText,
  Settings,
  History,
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/patients', icon: Users, label: 'Patients' },
  { href: '/recording', icon: Mic, label: 'Recording' },
  { href: '/reports', icon: FileText, label: 'Reports' },
  { href: '/history', icon: History, label: 'History' },
  { href: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-muted/40 min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
              pathname === item.href
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted'
            )}
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

### 3. Patient Search Component
```typescript
// components/patients/PatientSearch.tsx
'use client';

import { useState, useCallback } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { usePatients } from '@/hooks/usePatients';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { PatientCard } from './PatientCard';
import { Search, UserPlus, Loader2 } from 'lucide-react';

interface PatientSearchProps {
  onSelect: (patient: Patient) => void;
  onAddNew: () => void;
}

export function PatientSearch({ onSelect, onAddNew }: PatientSearchProps) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  const { data, isLoading, error } = usePatients(debouncedQuery);

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search by name, phone, or patient ID..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Results */}
      <div className="space-y-2">
        {isLoading && (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        )}

        {error && (
          <div className="text-center py-8 text-destructive">
            Error loading patients. Please try again.
          </div>
        )}

        {data?.results?.length === 0 && query && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">No patients found for "{query}"</p>
            <Button onClick={onAddNew}>
              <UserPlus className="mr-2 h-4 w-4" />
              Add New Patient
            </Button>
          </div>
        )}

        {data?.results?.map((patient) => (
          <PatientCard
            key={patient.id}
            patient={patient}
            onClick={onSelect}
          />
        ))}
      </div>
    </div>
  );
}
```

### 4. Recording Panel Component
```typescript
// components/recording/RecordingPanel.tsx
'use client';

import { useState } from 'react';
import { useRecording } from '@/hooks/useRecording';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RecordButton } from './RecordButton';
import { WaveformDisplay } from './WaveformDisplay';
import { TranscriptDisplay } from './TranscriptDisplay';
import { FileText, Languages } from 'lucide-react';

interface RecordingPanelProps {
  patientId: string;
  onComplete: (transcript: string) => void;
}

const languages = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
];

export function RecordingPanel({ patientId, onComplete }: RecordingPanelProps) {
  const [language, setLanguage] = useState('en');
  const {
    status,
    duration,
    transcript,
    audioLevel,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
  } = useRecording({ patientId, language });

  const handleGenerateReport = () => {
    onComplete(transcript.map(t => t.text).join(' '));
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Voice Recording</span>
          <Select value={language} onValueChange={setLanguage} disabled={status === 'recording'}>
            <SelectTrigger className="w-40">
              <Languages className="mr-2 h-4 w-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {languages.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Waveform */}
        <WaveformDisplay audioLevel={audioLevel} isRecording={status === 'recording'} />

        {/* Controls */}
        <div className="flex justify-center items-center gap-4">
          <RecordButton
            status={status}
            onStart={startRecording}
            onStop={stopRecording}
            onPause={pauseRecording}
            onResume={resumeRecording}
          />
        </div>

        {/* Duration */}
        {(status === 'recording' || status === 'paused') && (
          <div className="text-center text-2xl font-mono">
            {formatDuration(duration)}
          </div>
        )}

        {/* Transcript */}
        {transcript.length > 0 && (
          <TranscriptDisplay segments={transcript} />
        )}

        {/* Generate Report Button */}
        {status === 'completed' && transcript.length > 0 && (
          <Button onClick={handleGenerateReport} className="w-full">
            <FileText className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
```

### 5. Record Button Component
```typescript
// components/recording/RecordButton.tsx
'use client';

import { cn } from '@/lib/utils';
import { Mic, Square, Pause, Play } from 'lucide-react';

interface RecordButtonProps {
  status: 'idle' | 'recording' | 'paused' | 'processing' | 'completed';
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
}

export function RecordButton({
  status,
  onStart,
  onStop,
  onPause,
  onResume,
}: RecordButtonProps) {
  const isRecording = status === 'recording';
  const isPaused = status === 'paused';

  return (
    <div className="flex items-center gap-4">
      {/* Main Record/Stop Button */}
      <button
        onClick={isRecording || isPaused ? onStop : onStart}
        className={cn(
          'relative w-20 h-20 rounded-full flex items-center justify-center transition-all',
          isRecording
            ? 'bg-destructive hover:bg-destructive/90'
            : 'bg-primary hover:bg-primary/90',
          'shadow-lg hover:shadow-xl'
        )}
        disabled={status === 'processing'}
      >
        {/* Pulse Animation */}
        {isRecording && (
          <span className="absolute inset-0 rounded-full bg-destructive animate-ping opacity-25" />
        )}

        {isRecording || isPaused ? (
          <Square className="h-8 w-8 text-white" />
        ) : (
          <Mic className="h-8 w-8 text-white" />
        )}
      </button>

      {/* Pause/Resume Button */}
      {(isRecording || isPaused) && (
        <button
          onClick={isPaused ? onResume : onPause}
          className="w-14 h-14 rounded-full bg-secondary hover:bg-secondary/80 flex items-center justify-center shadow-md"
        >
          {isPaused ? (
            <Play className="h-6 w-6" />
          ) : (
            <Pause className="h-6 w-6" />
          )}
        </button>
      )}
    </div>
  );
}
```

### 6. Prescription Table Component
```typescript
// components/reports/PrescriptionTable.tsx
'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Medication } from '@/types/prescription';

interface PrescriptionTableProps {
  medications: Medication[];
  editable?: boolean;
  onEdit?: (index: number, medication: Medication) => void;
  onDelete?: (index: number) => void;
}

export function PrescriptionTable({
  medications,
  editable = false,
  onEdit,
  onDelete,
}: PrescriptionTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-12">#</TableHead>
          <TableHead>Medicine</TableHead>
          <TableHead>Dosage</TableHead>
          <TableHead>Timing</TableHead>
          <TableHead>Duration</TableHead>
          <TableHead>Instructions</TableHead>
          {editable && <TableHead className="w-20">Actions</TableHead>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {medications.map((med, index) => (
          <TableRow key={index}>
            <TableCell className="font-medium">{index + 1}</TableCell>
            <TableCell>
              <div>
                <span className="font-medium">{med.name}</span>
                <Badge variant="outline" className="ml-2 text-xs">
                  {med.type}
                </Badge>
              </div>
            </TableCell>
            <TableCell>{med.dosage}</TableCell>
            <TableCell>
              <div className="space-y-1">
                <Badge variant="secondary">{med.timing}</Badge>
                <span className="text-xs text-muted-foreground block">
                  {med.relation_to_food} food
                </span>
              </div>
            </TableCell>
            <TableCell>{med.duration_days} days</TableCell>
            <TableCell className="text-sm text-muted-foreground">
              {med.special_instructions || '-'}
            </TableCell>
            {editable && (
              <TableCell>
                {/* Edit/Delete buttons */}
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

### 7. Report Preview Component
```typescript
// components/reports/ReportPreview.tsx
'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PrescriptionTable } from './PrescriptionTable';
import { Download, Printer, Edit, Share2 } from 'lucide-react';
import { Report } from '@/types/report';

interface ReportPreviewProps {
  report: Report;
  onEdit?: () => void;
  onDownload?: () => void;
}

export function ReportPreview({ report, onEdit, onDownload }: ReportPreviewProps) {
  return (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="flex justify-end gap-2">
        <Button variant="outline" size="sm" onClick={onEdit}>
          <Edit className="mr-2 h-4 w-4" />
          Edit
        </Button>
        <Button variant="outline" size="sm">
          <Share2 className="mr-2 h-4 w-4" />
          Share
        </Button>
        <Button variant="outline" size="sm">
          <Printer className="mr-2 h-4 w-4" />
          Print
        </Button>
        <Button size="sm" onClick={onDownload}>
          <Download className="mr-2 h-4 w-4" />
          Download PDF
        </Button>
      </div>

      {/* Report Sections */}
      <Tabs defaultValue="prescription">
        <TabsList>
          <TabsTrigger value="prescription">Prescription</TabsTrigger>
          <TabsTrigger value="diet">Diet Plan</TabsTrigger>
          <TabsTrigger value="care">Care Instructions</TabsTrigger>
        </TabsList>

        <TabsContent value="prescription">
          <Card>
            <CardHeader>
              <CardTitle>Prescription</CardTitle>
            </CardHeader>
            <CardContent>
              <PrescriptionTable medications={report.prescription.medications} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diet">
          {/* Diet Plan Content */}
        </TabsContent>

        <TabsContent value="care">
          {/* Care Instructions Content */}
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## Component Index

| Component | Path | Description |
|-----------|------|-------------|
| Header | `components/common/Header.tsx` | Top navigation bar |
| Sidebar | `components/common/Sidebar.tsx` | Side navigation |
| PatientSearch | `components/patients/PatientSearch.tsx` | Patient lookup |
| PatientCard | `components/patients/PatientCard.tsx` | Patient info card |
| PatientForm | `components/patients/PatientForm.tsx` | Registration form |
| RecordingPanel | `components/recording/RecordingPanel.tsx` | Main recording UI |
| RecordButton | `components/recording/RecordButton.tsx` | Record/Stop button |
| WaveformDisplay | `components/recording/WaveformDisplay.tsx` | Audio visualizer |
| TranscriptDisplay | `components/recording/TranscriptDisplay.tsx` | Live transcript |
| ReportPreview | `components/reports/ReportPreview.tsx` | Report viewer |
| PrescriptionTable | `components/reports/PrescriptionTable.tsx` | Medications table |

## Related Documentation
- [Frontend Architecture](./architecture.md)
- [State Management](./state-management.md)
- [Styling Guide](./styling.md)
