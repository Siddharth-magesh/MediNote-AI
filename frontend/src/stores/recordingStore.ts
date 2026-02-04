import { create } from "zustand";

type RecordingStatus = "idle" | "connecting" | "recording" | "paused" | "processing" | "completed" | "error";

interface TranscriptSegment {
  text: string;
  timestamp: number;
  isFinal: boolean;
}

interface RecordingState {
  // Session
  sessionId: string | null;
  visitId: string | null;
  patientId: string | null;

  // Status
  status: RecordingStatus;
  error: string | null;

  // Recording data
  duration: number;
  language: string;
  transcript: TranscriptSegment[];
  audioLevel: number;

  // WebSocket
  wsConnected: boolean;

  // Actions
  setSession: (sessionId: string, visitId: string, patientId: string) => void;
  setStatus: (status: RecordingStatus) => void;
  setError: (error: string | null) => void;
  setDuration: (duration: number) => void;
  incrementDuration: () => void;
  setLanguage: (language: string) => void;
  addTranscript: (segment: TranscriptSegment) => void;
  updateLastTranscript: (text: string, isFinal: boolean) => void;
  clearTranscript: () => void;
  setAudioLevel: (level: number) => void;
  setWsConnected: (connected: boolean) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  visitId: null,
  patientId: null,
  status: "idle" as RecordingStatus,
  error: null,
  duration: 0,
  language: "en",
  transcript: [],
  audioLevel: 0,
  wsConnected: false,
};

export const useRecordingStore = create<RecordingState>((set) => ({
  ...initialState,

  setSession: (sessionId, visitId, patientId) =>
    set({ sessionId, visitId, patientId }),

  setStatus: (status) => set({ status }),

  setError: (error) => set({ error, status: error ? "error" : "idle" }),

  setDuration: (duration) => set({ duration }),

  incrementDuration: () =>
    set((state) => ({ duration: state.duration + 1 })),

  setLanguage: (language) => set({ language }),

  addTranscript: (segment) =>
    set((state) => ({
      transcript: [...state.transcript, segment],
    })),

  updateLastTranscript: (text, isFinal) =>
    set((state) => {
      const transcript = [...state.transcript];
      if (transcript.length > 0) {
        const lastIndex = transcript.length - 1;
        transcript[lastIndex] = {
          ...transcript[lastIndex],
          text,
          isFinal,
        };
      } else {
        transcript.push({
          text,
          timestamp: Date.now(),
          isFinal,
        });
      }
      return { transcript };
    }),

  clearTranscript: () => set({ transcript: [] }),

  setAudioLevel: (audioLevel) => set({ audioLevel }),

  setWsConnected: (wsConnected) => set({ wsConnected }),

  reset: () => set(initialState),
}));

// Selectors
export const selectSessionId = (state: RecordingState) => state.sessionId;
export const selectStatus = (state: RecordingState) => state.status;
export const selectIsRecording = (state: RecordingState) =>
  state.status === "recording";
export const selectDuration = (state: RecordingState) => state.duration;
export const selectTranscript = (state: RecordingState) => state.transcript;
export const selectFullTranscript = (state: RecordingState) =>
  state.transcript
    .filter((s) => s.isFinal)
    .map((s) => s.text)
    .join(" ");
export const selectAudioLevel = (state: RecordingState) => state.audioLevel;
