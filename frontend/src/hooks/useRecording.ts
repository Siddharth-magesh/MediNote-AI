"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRecordingStore } from "@/stores/recordingStore";
import { recordingApi } from "@/lib/api";

interface UseRecordingOptions {
  patientId: string;
  language?: string;
  onTranscript?: (text: string, isFinal: boolean) => void;
  onError?: (error: string) => void;
  onComplete?: (transcript: string) => void;
}

interface TranscriptSegment {
  text: string;
  timestamp: number;
  isFinal: boolean;
}

export function useRecording({
  patientId,
  language = "en",
  onTranscript,
  onError,
  onComplete,
}: UseRecordingOptions) {
  const {
    status,
    duration,
    transcript,
    audioLevel,
    setStatus,
    incrementDuration,
    addTranscript,
    updateLastTranscript,
    setAudioLevel,
    setWsConnected,
    reset,
  } = useRecordingStore();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Start recording session
  const startRecording = useCallback(async () => {
    try {
      reset();
      setError(null);
      setStatus("connecting");

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Setup audio context for level monitoring
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      // Start level monitoring
      const monitorLevel = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average / 255);
        }
        animationFrameRef.current = requestAnimationFrame(monitorLevel);
      };
      monitorLevel();

      // Start API session
      const response = await recordingApi.startSession({
        patient_id: patientId,
        language,
      });

      setSessionId(response.session_id);

      // Connect WebSocket
      const wsUrl = response.websocket_url.replace("http", "ws");
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setWsConnected(true);
        setStatus("recording");

        // Start duration timer
        timerRef.current = setInterval(() => {
          incrementDuration();
        }, 1000);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === "transcript") {
            const segment: TranscriptSegment = {
              text: message.text,
              timestamp: Date.now(),
              isFinal: message.is_final,
            };

            if (message.is_final) {
              addTranscript(segment);
            } else {
              updateLastTranscript(message.text, false);
            }

            onTranscript?.(message.text, message.is_final);
          } else if (message.type === "error") {
            setError(message.message);
            onError?.(message.message);
          }
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
        }
      };

      wsRef.current.onerror = () => {
        setError("Connection error");
        onError?.("Connection error");
      };

      wsRef.current.onclose = () => {
        setWsConnected(false);
      };

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (
          event.data.size > 0 &&
          wsRef.current?.readyState === WebSocket.OPEN
        ) {
          wsRef.current.send(event.data);
        }
      };

      mediaRecorderRef.current.start(250); // Send chunks every 250ms
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to start recording";
      setError(message);
      setStatus("error");
      onError?.(message);
    }
  }, [
    patientId,
    language,
    reset,
    setStatus,
    setAudioLevel,
    setWsConnected,
    incrementDuration,
    addTranscript,
    updateLastTranscript,
    onTranscript,
    onError,
  ]);

  // Stop recording
  const stopRecording = useCallback(async () => {
    // Stop timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Stop level monitoring
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    // Stop media recorder
    if (mediaRecorderRef.current?.state !== "inactive") {
      mediaRecorderRef.current?.stop();
      mediaRecorderRef.current?.stream.getTracks().forEach((track) => track.stop());
    }

    // Close audio context
    audioContextRef.current?.close();

    // Close WebSocket
    wsRef.current?.close();

    // Stop API session
    if (sessionId) {
      try {
        await recordingApi.stopSession(sessionId);
      } catch (e) {
        console.error("Failed to stop session:", e);
      }
    }

    setStatus("completed");
    setAudioLevel(0);

    // Get full transcript
    const fullTranscript = useRecordingStore
      .getState()
      .transcript.filter((s) => s.isFinal)
      .map((s) => s.text)
      .join(" ");

    onComplete?.(fullTranscript);
  }, [sessionId, setStatus, setAudioLevel, onComplete]);

  // Pause recording
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.pause();
      setStatus("paused");

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [setStatus]);

  // Resume recording
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "paused") {
      mediaRecorderRef.current.resume();
      setStatus("recording");

      timerRef.current = setInterval(() => {
        incrementDuration();
      }, 1000);
    }
  }, [setStatus, incrementDuration]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      mediaRecorderRef.current?.stream.getTracks().forEach((track) => track.stop());
      audioContextRef.current?.close();
      wsRef.current?.close();
    };
  }, []);

  return {
    status,
    duration,
    transcript,
    audioLevel,
    error,
    sessionId,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    reset,
  };
}
