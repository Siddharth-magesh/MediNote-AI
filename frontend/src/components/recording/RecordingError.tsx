"use client";

import { AlertCircle, Mic, MicOff, Wifi, WifiOff, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type ErrorType = "microphone" | "connection" | "permission" | "generic";

interface RecordingErrorProps {
  error: string;
  errorType?: ErrorType;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

const errorConfig: Record<
  ErrorType,
  {
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    description: string;
  }
> = {
  microphone: {
    icon: MicOff,
    title: "Microphone Error",
    description:
      "Unable to access your microphone. Please check if another application is using it.",
  },
  permission: {
    icon: Mic,
    title: "Permission Required",
    description:
      "Please allow microphone access in your browser settings to start recording.",
  },
  connection: {
    icon: WifiOff,
    title: "Connection Lost",
    description:
      "Lost connection to the server. Please check your internet connection.",
  },
  generic: {
    icon: AlertCircle,
    title: "Recording Error",
    description: "An error occurred during recording. Please try again.",
  },
};

export function RecordingError({
  error,
  errorType = "generic",
  onRetry,
  onDismiss,
  className,
}: RecordingErrorProps) {
  const config = errorConfig[errorType];
  const Icon = config.icon;

  return (
    <Card className={cn("border-destructive/50 bg-destructive/5", className)}>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="p-3 rounded-full bg-destructive/10">
            <Icon className="h-8 w-8 text-destructive" />
          </div>
          <div className="space-y-2">
            <h3 className="font-semibold text-lg">{config.title}</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              {error || config.description}
            </p>
          </div>
          <div className="flex gap-3">
            {onDismiss && (
              <Button variant="outline" onClick={onDismiss}>
                Dismiss
              </Button>
            )}
            {onRetry && (
              <Button onClick={onRetry}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Inline error message for less severe errors
interface InlineErrorProps {
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export function InlineError({ message, onDismiss, className }: InlineErrorProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg bg-destructive/10 text-destructive",
        className
      )}
      role="alert"
    >
      <AlertCircle className="h-5 w-5 shrink-0" />
      <p className="text-sm flex-1">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-destructive/70 hover:text-destructive"
          aria-label="Dismiss error"
        >
          <span className="sr-only">Dismiss</span>
          &times;
        </button>
      )}
    </div>
  );
}

// Connection status indicator
interface ConnectionStatusProps {
  status: "connecting" | "connected" | "disconnected" | "error";
  className?: string;
}

export function ConnectionStatus({ status, className }: ConnectionStatusProps) {
  const statusConfig = {
    connecting: {
      icon: Wifi,
      text: "Connecting...",
      color: "text-yellow-600",
      dot: "bg-yellow-500 animate-pulse",
    },
    connected: {
      icon: Wifi,
      text: "Connected",
      color: "text-green-600",
      dot: "bg-green-500",
    },
    disconnected: {
      icon: WifiOff,
      text: "Disconnected",
      color: "text-muted-foreground",
      dot: "bg-muted-foreground",
    },
    error: {
      icon: WifiOff,
      text: "Connection Error",
      color: "text-destructive",
      dot: "bg-destructive",
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div className={cn("flex items-center gap-2 text-sm", config.color, className)}>
      <span className={cn("w-2 h-2 rounded-full", config.dot)} />
      <Icon className="h-4 w-4" />
      <span>{config.text}</span>
    </div>
  );
}
