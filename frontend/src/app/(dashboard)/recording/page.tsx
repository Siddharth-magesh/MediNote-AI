"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { usePatient, usePatientSearch } from "@/hooks/usePatients";
import { useDebounce } from "@/hooks/useDebounce";
import { useRecordingStore } from "@/stores/recordingStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Search,
  User,
  Mic,
  Square,
  Pause,
  Play,
  Languages,
  FileText,
  Loader2,
  AlertCircle,
  UserPlus,
} from "lucide-react";
import { formatDuration, getInitials, formatPhone, calculateAge } from "@/lib/utils";
import type { Patient } from "@/types";

type Step = "select-patient" | "recording" | "completed";

const languages = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
  { code: "bn", label: "Bengali" },
  { code: "mr", label: "Marathi" },
  { code: "gu", label: "Gujarati" },
  { code: "kn", label: "Kannada" },
  { code: "ml", label: "Malayalam" },
  { code: "pa", label: "Punjabi" },
];

interface PatientSearchResultProps {
  patient: Patient;
  onSelect: (patient: Patient) => void;
}

function PatientSearchResult({ patient, onSelect }: PatientSearchResultProps) {
  const age = patient.date_of_birth ? calculateAge(patient.date_of_birth) : null;

  return (
    <button
      onClick={() => onSelect(patient)}
      className="w-full flex items-center gap-4 p-4 rounded-lg border hover:bg-muted transition-colors text-left"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary shrink-0">
        {getInitials(`${patient.first_name} ${patient.last_name}`)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold">
          {patient.first_name} {patient.last_name}
        </p>
        <p className="text-sm text-muted-foreground">
          {patient.patient_id} {age && `| ${age} years`}{" "}
          {patient.gender && `| ${patient.gender}`}
        </p>
        <p className="text-sm text-muted-foreground">
          {formatPhone(patient.phone_primary)}
        </p>
      </div>
      <Badge variant="outline">{patient.status}</Badge>
    </button>
  );
}

interface RecordingControlsProps {
  status: string;
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
}

function RecordingControls({
  status,
  onStart,
  onStop,
  onPause,
  onResume,
}: RecordingControlsProps) {
  const isRecording = status === "recording";
  const isPaused = status === "paused";

  return (
    <div className="flex items-center justify-center gap-4">
      {/* Main Record/Stop Button */}
      <button
        onClick={isRecording || isPaused ? onStop : onStart}
        className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-lg hover:shadow-xl ${
          isRecording
            ? "bg-destructive hover:bg-destructive/90"
            : "bg-primary hover:bg-primary/90"
        }`}
        disabled={status === "processing"}
      >
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

interface WaveformDisplayProps {
  audioLevel: number;
  isRecording: boolean;
}

function WaveformDisplay({ audioLevel, isRecording }: WaveformDisplayProps) {
  // Generate bars for visualization
  const bars = 20;
  const baseHeight = 8;

  return (
    <div className="flex items-center justify-center gap-1 h-16 bg-muted/50 rounded-lg">
      {[...Array(bars)].map((_, i) => {
        const distance = Math.abs(i - bars / 2);
        const maxHeight = isRecording
          ? Math.max(baseHeight, 48 * audioLevel * (1 - distance / (bars / 2)))
          : baseHeight;

        return (
          <div
            key={i}
            className="w-1.5 bg-primary rounded-full transition-all duration-75"
            style={{
              height: `${maxHeight}px`,
            }}
          />
        );
      })}
    </div>
  );
}

export default function RecordingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedPatientId = searchParams.get("patient");

  const [step, setStep] = useState<Step>("select-patient");
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 300);

  const {
    status,
    duration,
    language,
    transcript,
    audioLevel,
    setLanguage,
    setStatus,
    incrementDuration,
    addTranscript,
    reset,
  } = useRecordingStore();

  // Fetch preselected patient
  const { data: preselectedPatient } = usePatient(preselectedPatientId || "");
  const { data: searchData, isLoading: searchLoading } =
    usePatientSearch(debouncedSearch);
  const searchResults = searchData?.results;

  // Set preselected patient
  useEffect(() => {
    if (preselectedPatient && !selectedPatient) {
      setSelectedPatient(preselectedPatient);
      setStep("recording");
    }
  }, [preselectedPatient, selectedPatient]);

  // Timer for recording duration
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (status === "recording") {
      interval = setInterval(() => {
        incrementDuration();
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [status, incrementDuration]);

  const handlePatientSelect = (patient: Patient) => {
    setSelectedPatient(patient);
    setStep("recording");
  };

  const handleStartRecording = () => {
    reset();
    setStatus("recording");
    // In a real implementation, this would:
    // 1. Start audio recording with RecordRTC
    // 2. Connect to WebSocket for real-time transcription
    // 3. Send audio chunks to the server

    // Mock transcript for demo
    setTimeout(() => {
      addTranscript({
        text: "Patient presents with fever for the past 3 days...",
        timestamp: Date.now(),
        isFinal: true,
      });
    }, 2000);
  };

  const handleStopRecording = () => {
    setStatus("completed");
    setStep("completed");
  };

  const handlePauseRecording = () => {
    setStatus("paused");
  };

  const handleResumeRecording = () => {
    setStatus("recording");
  };

  const handleGenerateReport = () => {
    router.push(`/reports/new?patient=${selectedPatient?.id}`);
  };

  const handleNewRecording = () => {
    reset();
    setStep("select-patient");
    setSelectedPatient(null);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        {step !== "select-patient" && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              if (status === "recording") {
                handleStopRecording();
              }
              setStep("select-patient");
              setSelectedPatient(null);
              reset();
            }}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
        )}
        <div>
          <h1 className="text-2xl font-bold">
            {step === "select-patient"
              ? "Select Patient"
              : step === "recording"
              ? "Recording Session"
              : "Recording Complete"}
          </h1>
          <p className="text-muted-foreground">
            {step === "select-patient"
              ? "Choose a patient to start recording"
              : step === "recording"
              ? "Speak clearly for accurate transcription"
              : "Review and generate report"}
          </p>
        </div>
      </div>

      {/* Step 1: Patient Selection */}
      {step === "select-patient" && (
        <Card>
          <CardHeader>
            <CardTitle>Search for a patient</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, phone, or patient ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {searchLoading && (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            )}

            {!searchLoading && debouncedSearch && searchResults?.length === 0 && (
              <div className="text-center py-8 space-y-4">
                <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
                <p className="text-muted-foreground">
                  No patients found for &quot;{debouncedSearch}&quot;
                </p>
                <Button asChild>
                  <Link href="/patients/new?return=/recording">
                    <UserPlus className="mr-2 h-4 w-4" />
                    Add New Patient
                  </Link>
                </Button>
              </div>
            )}

            {searchResults && searchResults.length > 0 && (
              <div className="space-y-2">
                {searchResults.map((patient) => (
                  <PatientSearchResult
                    key={patient.id}
                    patient={patient}
                    onSelect={handlePatientSelect}
                  />
                ))}
              </div>
            )}

            {!searchQuery && (
              <div className="text-center py-8">
                <User className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Start typing to search for a patient
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Recording */}
      {step === "recording" && selectedPatient && (
        <div className="space-y-6">
          {/* Patient Info Banner */}
          <Card>
            <CardContent className="py-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                  {getInitials(
                    `${selectedPatient.first_name} ${selectedPatient.last_name}`
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold">
                    {selectedPatient.first_name} {selectedPatient.last_name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedPatient.patient_id}
                    {selectedPatient.date_of_birth &&
                      ` | ${calculateAge(selectedPatient.date_of_birth)} years`}
                    {selectedPatient.gender && ` | ${selectedPatient.gender}`}
                  </p>
                </div>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="w-36">
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
              </div>
            </CardContent>
          </Card>

          {/* Recording Panel */}
          <Card>
            <CardContent className="py-8 space-y-6">
              {/* Waveform */}
              <WaveformDisplay
                audioLevel={audioLevel}
                isRecording={status === "recording"}
              />

              {/* Controls */}
              <RecordingControls
                status={status}
                onStart={handleStartRecording}
                onStop={handleStopRecording}
                onPause={handlePauseRecording}
                onResume={handleResumeRecording}
              />

              {/* Duration */}
              {(status === "recording" || status === "paused") && (
                <div className="text-center">
                  <p className="text-3xl font-mono font-bold">
                    {formatDuration(duration)}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {status === "paused" ? "Paused" : "Recording..."}
                  </p>
                </div>
              )}

              {/* Instructions */}
              {status === "idle" && (
                <p className="text-center text-muted-foreground">
                  Press the microphone button to start recording
                </p>
              )}
            </CardContent>
          </Card>

          {/* Live Transcript */}
          {transcript.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Live Transcript</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {transcript.map((segment, i) => (
                    <p
                      key={i}
                      className={
                        segment.isFinal
                          ? "text-foreground"
                          : "text-muted-foreground italic"
                      }
                    >
                      {segment.text}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Step 3: Completed */}
      {step === "completed" && selectedPatient && (
        <div className="space-y-6">
          {/* Success Message */}
          <Card>
            <CardContent className="py-8 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <Mic className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Recording Complete</h2>
                <p className="text-muted-foreground">
                  Duration: {formatDuration(duration)}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Transcript Preview */}
          {transcript.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Transcript</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {transcript.map((segment, i) => (
                    <p key={i}>{segment.text}</p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <Button variant="outline" onClick={handleNewRecording}>
              New Recording
            </Button>
            <Button onClick={handleGenerateReport} className="flex-1">
              <FileText className="mr-2 h-4 w-4" />
              Generate Report
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
