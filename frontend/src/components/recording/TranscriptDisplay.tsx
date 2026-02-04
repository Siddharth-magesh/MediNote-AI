"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { formatDuration } from "@/lib/utils";

interface TranscriptSegment {
  text: string;
  timestamp: number;
  isFinal: boolean;
  speaker?: string;
}

interface TranscriptDisplayProps {
  segments: TranscriptSegment[];
  isRecording?: boolean;
  showTimestamps?: boolean;
  maxHeight?: string;
  className?: string;
}

export function TranscriptDisplay({
  segments,
  isRecording = false,
  showTimestamps = false,
  maxHeight = "300px",
  className,
}: TranscriptDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const startTimeRef = useRef<number | null>(null);

  // Auto-scroll to bottom when new segments are added
  useEffect(() => {
    if (containerRef.current && isRecording) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [segments, isRecording]);

  // Track start time for relative timestamps
  useEffect(() => {
    if (segments.length > 0 && startTimeRef.current === null) {
      startTimeRef.current = segments[0].timestamp;
    }
  }, [segments]);

  const getRelativeTime = (timestamp: number): string => {
    if (!startTimeRef.current) return "00:00";
    const seconds = Math.floor((timestamp - startTimeRef.current) / 1000);
    return formatDuration(seconds);
  };

  if (segments.length === 0) {
    return (
      <div
        className={cn(
          "flex items-center justify-center p-8 text-muted-foreground bg-muted/30 rounded-lg",
          className
        )}
      >
        {isRecording ? (
          <p className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-primary rounded-full animate-pulse" />
            Listening...
          </p>
        ) : (
          <p>Start recording to see the transcript</p>
        )}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        "overflow-y-auto rounded-lg bg-muted/30 p-4 scroll-smooth",
        className
      )}
      style={{ maxHeight }}
    >
      <div className="space-y-3">
        {segments.map((segment, index) => (
          <div
            key={index}
            className={cn(
              "transition-opacity duration-300",
              !segment.isFinal && "opacity-70"
            )}
          >
            <div className="flex gap-3">
              {showTimestamps && (
                <span className="text-xs text-muted-foreground font-mono shrink-0 pt-0.5">
                  {getRelativeTime(segment.timestamp)}
                </span>
              )}
              <p
                className={cn(
                  "text-sm leading-relaxed",
                  segment.isFinal ? "text-foreground" : "text-muted-foreground italic"
                )}
              >
                {segment.speaker && (
                  <span className="font-medium text-primary mr-2">
                    {segment.speaker}:
                  </span>
                )}
                {segment.text}
                {!segment.isFinal && (
                  <span className="inline-block w-1.5 h-4 ml-1 bg-primary animate-pulse" />
                )}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Recording indicator at bottom */}
      {isRecording && segments.length > 0 && (
        <div className="mt-4 pt-3 border-t border-muted">
          <p className="text-xs text-muted-foreground flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Recording in progress...
          </p>
        </div>
      )}
    </div>
  );
}

// Editable transcript for post-recording review
interface EditableTranscriptProps {
  text: string;
  onChange: (text: string) => void;
  disabled?: boolean;
  className?: string;
}

export function EditableTranscript({
  text,
  onChange,
  disabled = false,
  className,
}: EditableTranscriptProps) {
  return (
    <div className={cn("rounded-lg border", className)}>
      <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/50">
        <span className="text-sm font-medium">Transcript</span>
        <span className="text-xs text-muted-foreground">
          {text.split(/\s+/).filter(Boolean).length} words
        </span>
      </div>
      <textarea
        value={text}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={cn(
          "w-full min-h-[200px] p-4 text-sm leading-relaxed resize-none",
          "bg-background focus:outline-none",
          disabled && "cursor-not-allowed opacity-60"
        )}
        placeholder="Transcript will appear here..."
      />
    </div>
  );
}
