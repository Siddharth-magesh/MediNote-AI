"use client";

import { cn } from "@/lib/utils";
import { Mic, Square, Pause, Play, Loader2 } from "lucide-react";

type RecordingStatus =
  | "idle"
  | "connecting"
  | "recording"
  | "paused"
  | "processing"
  | "completed"
  | "error";

interface RecordButtonProps {
  status: RecordingStatus;
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: {
    main: "w-14 h-14",
    mainIcon: "h-6 w-6",
    secondary: "w-10 h-10",
    secondaryIcon: "h-4 w-4",
  },
  md: {
    main: "w-20 h-20",
    mainIcon: "h-8 w-8",
    secondary: "w-14 h-14",
    secondaryIcon: "h-6 w-6",
  },
  lg: {
    main: "w-24 h-24",
    mainIcon: "h-10 w-10",
    secondary: "w-16 h-16",
    secondaryIcon: "h-7 w-7",
  },
};

export function RecordButton({
  status,
  onStart,
  onStop,
  onPause,
  onResume,
  disabled = false,
  size = "md",
}: RecordButtonProps) {
  const isRecording = status === "recording";
  const isPaused = status === "paused";
  const isConnecting = status === "connecting";
  const isProcessing = status === "processing";
  const isActive = isRecording || isPaused;
  const sizes = sizeClasses[size];

  const handleMainClick = () => {
    if (disabled || isConnecting || isProcessing) return;

    if (isActive) {
      onStop();
    } else {
      onStart();
    }
  };

  const handleSecondaryClick = () => {
    if (disabled || isConnecting || isProcessing) return;

    if (isPaused) {
      onResume();
    } else if (isRecording) {
      onPause();
    }
  };

  return (
    <div className="flex items-center justify-center gap-4">
      {/* Main Record/Stop Button */}
      <button
        onClick={handleMainClick}
        disabled={disabled || isConnecting || isProcessing}
        className={cn(
          "relative rounded-full flex items-center justify-center transition-all shadow-lg",
          "focus:outline-none focus:ring-4 focus:ring-offset-2",
          sizes.main,
          isActive
            ? "bg-destructive hover:bg-destructive/90 focus:ring-destructive/50"
            : "bg-primary hover:bg-primary/90 focus:ring-primary/50",
          (disabled || isConnecting || isProcessing) &&
            "opacity-50 cursor-not-allowed",
          !disabled && !isConnecting && !isProcessing && "hover:shadow-xl hover:scale-105"
        )}
        aria-label={isActive ? "Stop recording" : "Start recording"}
      >
        {/* Pulse Animation for Recording */}
        {isRecording && (
          <span className="absolute inset-0 rounded-full bg-destructive animate-ping opacity-25" />
        )}

        {/* Icon */}
        {isConnecting || isProcessing ? (
          <Loader2 className={cn(sizes.mainIcon, "text-white animate-spin")} />
        ) : isActive ? (
          <Square className={cn(sizes.mainIcon, "text-white")} />
        ) : (
          <Mic className={cn(sizes.mainIcon, "text-white")} />
        )}
      </button>

      {/* Pause/Resume Button */}
      {isActive && (
        <button
          onClick={handleSecondaryClick}
          disabled={disabled}
          className={cn(
            "rounded-full bg-secondary hover:bg-secondary/80 flex items-center justify-center shadow-md transition-all",
            "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary",
            sizes.secondary,
            !disabled && "hover:scale-105"
          )}
          aria-label={isPaused ? "Resume recording" : "Pause recording"}
        >
          {isPaused ? (
            <Play className={cn(sizes.secondaryIcon, "ml-0.5")} />
          ) : (
            <Pause className={sizes.secondaryIcon} />
          )}
        </button>
      )}
    </div>
  );
}
