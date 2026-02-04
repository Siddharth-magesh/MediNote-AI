"use client";

import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

interface WaveformDisplayProps {
  audioLevel: number;
  isRecording: boolean;
  isPaused?: boolean;
  barCount?: number;
  className?: string;
}

export function WaveformDisplay({
  audioLevel,
  isRecording,
  isPaused = false,
  barCount = 24,
  className,
}: WaveformDisplayProps) {
  const [bars, setBars] = useState<number[]>([]);
  const animationRef = useRef<number>();
  const previousLevelsRef = useRef<number[]>([]);

  useEffect(() => {
    // Initialize bars with base height
    if (previousLevelsRef.current.length === 0) {
      previousLevelsRef.current = new Array(barCount).fill(8);
    }

    const animate = () => {
      const newBars = previousLevelsRef.current.map((prevHeight, i) => {
        if (!isRecording || isPaused) {
          // Animate back to base height when not recording
          return prevHeight > 8 ? prevHeight * 0.9 : 8;
        }

        // Calculate target height based on audio level and position
        const center = barCount / 2;
        const distanceFromCenter = Math.abs(i - center);
        const positionFactor = 1 - distanceFromCenter / center;

        // Add some randomness for natural look
        const randomFactor = 0.7 + Math.random() * 0.6;
        const targetHeight = Math.max(
          8,
          8 + audioLevel * 48 * positionFactor * randomFactor
        );

        // Smooth transition
        const smoothing = 0.3;
        return prevHeight + (targetHeight - prevHeight) * smoothing;
      });

      previousLevelsRef.current = newBars;
      setBars(newBars);

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioLevel, isRecording, isPaused, barCount]);

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-1 h-20 bg-muted/50 rounded-lg px-4",
        className
      )}
      role="img"
      aria-label={
        isRecording
          ? isPaused
            ? "Recording paused"
            : "Recording in progress"
          : "Ready to record"
      }
    >
      {bars.map((height, i) => (
        <div
          key={i}
          className={cn(
            "w-1.5 rounded-full transition-colors duration-200",
            isRecording && !isPaused
              ? "bg-primary"
              : isPaused
              ? "bg-muted-foreground/50"
              : "bg-muted-foreground/30"
          )}
          style={{
            height: `${Math.min(height, 56)}px`,
            transition: "height 50ms ease-out",
          }}
        />
      ))}
    </div>
  );
}

// Static waveform for completed recordings
interface StaticWaveformProps {
  className?: string;
}

export function StaticWaveform({ className }: StaticWaveformProps) {
  // Generate a static pattern that looks like a completed waveform
  const bars = Array.from({ length: 24 }, (_, i) => {
    const center = 12;
    const distance = Math.abs(i - center);
    const base = 20 + Math.random() * 20;
    return base * (1 - distance / center) + 8;
  });

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-1 h-20 bg-muted/50 rounded-lg px-4",
        className
      )}
    >
      {bars.map((height, i) => (
        <div
          key={i}
          className="w-1.5 rounded-full bg-green-500/60"
          style={{ height: `${height}px` }}
        />
      ))}
    </div>
  );
}
