"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RecordButton } from "./RecordButton";
import { WaveformDisplay } from "./WaveformDisplay";
import { TranscriptDisplay, EditableTranscript } from "./TranscriptDisplay";
import { LanguageSelector } from "./LanguageSelector";
import { RecordingError, ConnectionStatus, InlineError } from "./RecordingError";
import { useRecording } from "@/hooks/useRecording";
import { formatDuration } from "@/lib/utils";
import { cn } from "@/lib/utils";
import {
  Clock,
  FileText,
  CheckCircle,
  XCircle,
  Edit3,
  Save,
  RotateCcw
} from "lucide-react";

interface RecordingPanelProps {
  patientId: string;
  patientName?: string;
  onComplete?: (transcript: string) => void;
  onCancel?: () => void;
  className?: string;
}

export function RecordingPanel({
  patientId,
  patientName,
  onComplete,
  onCancel,
  className,
}: RecordingPanelProps) {
  const [language, setLanguage] = useState("en");
  const [isEditing, setIsEditing] = useState(false);
  const [editedTranscript, setEditedTranscript] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected" | "error"
  >("disconnected");

  const {
    status,
    duration,
    transcript,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    reset,
  } = useRecording({
    patientId,
    language,
    onTranscript: () => {
      // Transcript updates handled by the hook
    },
    onError: (err) => {
      console.error("Recording error:", err);
      setConnectionStatus("error");
    },
    onComplete: (fullTranscript) => {
      setEditedTranscript(fullTranscript);
    },
  });

  // Track connection status based on recording status
  const updateConnectionStatus = useCallback(() => {
    if (status === "connecting") {
      setConnectionStatus("connecting");
    } else if (status === "recording" || status === "paused") {
      setConnectionStatus("connected");
    } else if (status === "error") {
      setConnectionStatus("error");
    } else {
      setConnectionStatus("disconnected");
    }
  }, [status]);

  // Update connection status when recording status changes
  useState(() => {
    updateConnectionStatus();
  });

  const handleStart = useCallback(() => {
    setEditedTranscript("");
    setIsEditing(false);
    startRecording();
  }, [startRecording]);

  const handleStop = useCallback(() => {
    stopRecording();
  }, [stopRecording]);

  const handlePause = useCallback(() => {
    pauseRecording();
  }, [pauseRecording]);

  const handleResume = useCallback(() => {
    resumeRecording();
  }, [resumeRecording]);

  const handleReset = useCallback(() => {
    reset();
    setEditedTranscript("");
    setIsEditing(false);
    setConnectionStatus("disconnected");
  }, [reset]);

  const handleSaveTranscript = useCallback(() => {
    setIsEditing(false);
    onComplete?.(editedTranscript);
  }, [editedTranscript, onComplete]);

  const handleCancel = useCallback(() => {
    handleReset();
    onCancel?.();
  }, [handleReset, onCancel]);

  const isRecording = status === "recording";
  const isPaused = status === "paused";
  const isCompleted = status === "completed";
  const hasError = status === "error";
  const isIdle = status === "idle";

  // Get full transcript text
  const fullTranscript = transcript
    .filter((s) => s.isFinal)
    .map((s) => s.text)
    .join(" ");

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header with patient info and language */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Recording Session</h2>
          {patientName && (
            <p className="text-sm text-muted-foreground">
              Patient: {patientName}
            </p>
          )}
        </div>
        <div className="flex items-center gap-4">
          <ConnectionStatus status={connectionStatus} />
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={!isIdle}
          />
        </div>
      </div>

      {/* Error display */}
      {hasError && error && (
        <RecordingError
          error={error}
          errorType="generic"
          onRetry={handleReset}
          onDismiss={handleReset}
        />
      )}

      {/* Main recording card */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              {isCompleted ? "Recording Complete" : "Voice Recording"}
            </CardTitle>
            {(isRecording || isPaused) && (
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4" />
                <span className="font-mono">{formatDuration(duration)}</span>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Waveform visualization */}
          {(isRecording || isPaused) && (
            <WaveformDisplay
              audioLevel={audioLevel}
              isRecording={isRecording}
              isPaused={isPaused}
              barCount={40}
              className="h-24"
            />
          )}

          {/* Recording controls */}
          <div className="flex flex-col items-center gap-4">
            <RecordButton
              status={status}
              onStart={handleStart}
              onStop={handleStop}
              onPause={handlePause}
              onResume={handleResume}
              size="lg"
            />

            {isIdle && (
              <p className="text-sm text-muted-foreground text-center">
                Click to start recording the consultation
              </p>
            )}

            {(isRecording || isPaused) && (
              <p className="text-sm text-muted-foreground text-center">
                {isRecording
                  ? "Recording in progress..."
                  : "Recording paused"}
              </p>
            )}
          </div>

          {/* Live transcript */}
          {(isRecording || isPaused) && transcript.length > 0 && (
            <div className="pt-4 border-t">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="h-4 w-4" />
                <span className="text-sm font-medium">Live Transcript</span>
              </div>
              <TranscriptDisplay
                segments={transcript}
                isRecording={isRecording}
                showTimestamps
                maxHeight="200px"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Post-recording review */}
      {isCompleted && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <CardTitle className="text-base">Review Transcript</CardTitle>
              </div>
              <div className="flex items-center gap-2">
                {!isEditing ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsEditing(true);
                      if (!editedTranscript) {
                        setEditedTranscript(fullTranscript);
                      }
                    }}
                  >
                    <Edit3 className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsEditing(false);
                      setEditedTranscript(fullTranscript);
                    }}
                  >
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancel Edit
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <EditableTranscript
                text={editedTranscript}
                onChange={setEditedTranscript}
              />
            ) : (
              <div className="bg-muted/30 rounded-lg p-4">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {editedTranscript || fullTranscript || "No transcript available"}
                </p>
              </div>
            )}

            {/* Recording stats */}
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>Duration: {formatDuration(duration)}</span>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>
                  {(editedTranscript || fullTranscript).split(/\s+/).filter(Boolean).length} words
                </span>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex justify-between pt-4 border-t">
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleReset}>
                  <RotateCcw className="mr-2 h-4 w-4" />
                  New Recording
                </Button>
                <Button variant="ghost" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
              <Button onClick={handleSaveTranscript}>
                <Save className="mr-2 h-4 w-4" />
                Generate Report
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Inline error for minor issues */}
      {!hasError && error && (
        <InlineError message={error} onDismiss={() => {}} />
      )}
    </div>
  );
}

// Compact recording widget for embedded use
interface CompactRecordingWidgetProps {
  patientId: string;
  onComplete?: (transcript: string) => void;
  className?: string;
}

export function CompactRecordingWidget({
  patientId,
  onComplete,
  className,
}: CompactRecordingWidgetProps) {
  const [language, setLanguage] = useState("en");

  const {
    status,
    duration,
    transcript,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
  } = useRecording({
    patientId,
    language,
    onComplete,
  });

  const isRecording = status === "recording";
  const isPaused = status === "paused";

  return (
    <div className={cn("p-4 rounded-lg border bg-card", className)}>
      <div className="flex items-center gap-4">
        <RecordButton
          status={status}
          onStart={startRecording}
          onStop={stopRecording}
          onPause={pauseRecording}
          onResume={resumeRecording}
          size="sm"
        />

        {(isRecording || isPaused) && (
          <div className="flex-1">
            <WaveformDisplay
              audioLevel={audioLevel}
              isRecording={isRecording}
              isPaused={isPaused}
              barCount={20}
              className="h-8"
            />
          </div>
        )}

        <div className="flex items-center gap-2">
          <span className="text-sm font-mono">{formatDuration(duration)}</span>
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={!["idle", "completed"].includes(status)}
            showIcon={false}
            className="w-24"
          />
        </div>
      </div>

      {error && (
        <InlineError message={error} className="mt-3" />
      )}

      {transcript.length > 0 && (
        <div className="mt-3 pt-3 border-t">
          <p className="text-xs text-muted-foreground line-clamp-2">
            {transcript[transcript.length - 1]?.text}
          </p>
        </div>
      )}
    </div>
  );
}
