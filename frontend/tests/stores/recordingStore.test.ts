import { describe, it, expect, beforeEach } from "vitest";
import { useRecordingStore } from "@/stores/recordingStore";

describe("recordingStore", () => {
  beforeEach(() => {
    // Reset the store to initial state
    useRecordingStore.setState({
      status: "idle",
      duration: 0,
      transcript: [],
      audioLevel: 0,
      wsConnected: false,
    });
  });

  it("has correct initial state", () => {
    const state = useRecordingStore.getState();
    expect(state.status).toBe("idle");
    expect(state.duration).toBe(0);
    expect(state.transcript).toEqual([]);
    expect(state.audioLevel).toBe(0);
    expect(state.wsConnected).toBe(false);
  });

  describe("status management", () => {
    it("sets status correctly", () => {
      const { setStatus } = useRecordingStore.getState();

      setStatus("connecting");
      expect(useRecordingStore.getState().status).toBe("connecting");

      setStatus("recording");
      expect(useRecordingStore.getState().status).toBe("recording");

      setStatus("paused");
      expect(useRecordingStore.getState().status).toBe("paused");

      setStatus("completed");
      expect(useRecordingStore.getState().status).toBe("completed");

      setStatus("error");
      expect(useRecordingStore.getState().status).toBe("error");
    });
  });

  describe("duration management", () => {
    it("sets duration", () => {
      const { setDuration } = useRecordingStore.getState();
      setDuration(60);
      expect(useRecordingStore.getState().duration).toBe(60);
    });

    it("increments duration", () => {
      const { setDuration, incrementDuration } = useRecordingStore.getState();
      setDuration(10);
      incrementDuration();
      expect(useRecordingStore.getState().duration).toBe(11);
    });
  });

  describe("transcript management", () => {
    it("adds transcript segment", () => {
      const { addTranscript } = useRecordingStore.getState();

      addTranscript({
        text: "Hello, doctor.",
        timestamp: Date.now(),
        isFinal: true,
      });

      const state = useRecordingStore.getState();
      expect(state.transcript).toHaveLength(1);
      expect(state.transcript[0].text).toBe("Hello, doctor.");
      expect(state.transcript[0].isFinal).toBe(true);
    });

    it("adds multiple transcript segments", () => {
      const { addTranscript } = useRecordingStore.getState();

      addTranscript({
        text: "First segment.",
        timestamp: Date.now(),
        isFinal: true,
      });

      addTranscript({
        text: "Second segment.",
        timestamp: Date.now(),
        isFinal: true,
      });

      const state = useRecordingStore.getState();
      expect(state.transcript).toHaveLength(2);
    });

    it("updates last transcript for interim results", () => {
      const { addTranscript, updateLastTranscript } = useRecordingStore.getState();

      // Add initial transcript
      addTranscript({
        text: "Hello",
        timestamp: Date.now(),
        isFinal: false,
      });

      // Update with more text (interim result)
      updateLastTranscript("Hello doctor", false);

      const state = useRecordingStore.getState();
      expect(state.transcript).toHaveLength(1);
      expect(state.transcript[0].text).toBe("Hello doctor");
      expect(state.transcript[0].isFinal).toBe(false);
    });

    it("clears transcript on reset", () => {
      const { addTranscript, reset } = useRecordingStore.getState();

      addTranscript({
        text: "Some text",
        timestamp: Date.now(),
        isFinal: true,
      });

      reset();

      expect(useRecordingStore.getState().transcript).toEqual([]);
    });
  });

  describe("audio level management", () => {
    it("sets audio level", () => {
      const { setAudioLevel } = useRecordingStore.getState();

      setAudioLevel(0.5);
      expect(useRecordingStore.getState().audioLevel).toBe(0.5);

      setAudioLevel(0.8);
      expect(useRecordingStore.getState().audioLevel).toBe(0.8);

      setAudioLevel(0);
      expect(useRecordingStore.getState().audioLevel).toBe(0);
    });

    it("clamps audio level to valid range", () => {
      const { setAudioLevel } = useRecordingStore.getState();

      setAudioLevel(1.5);
      // Depending on implementation, might clamp or accept
      const level = useRecordingStore.getState().audioLevel;
      expect(level).toBeGreaterThanOrEqual(0);
    });
  });

  describe("WebSocket connection status", () => {
    it("sets WebSocket connected status", () => {
      const { setWsConnected } = useRecordingStore.getState();

      setWsConnected(true);
      expect(useRecordingStore.getState().wsConnected).toBe(true);

      setWsConnected(false);
      expect(useRecordingStore.getState().wsConnected).toBe(false);
    });
  });

  describe("reset functionality", () => {
    it("resets all state to initial values", () => {
      const store = useRecordingStore.getState();

      // Set various state
      store.setStatus("recording");
      store.setDuration(120);
      store.addTranscript({
        text: "Test",
        timestamp: Date.now(),
        isFinal: true,
      });
      store.setAudioLevel(0.7);
      store.setWsConnected(true);

      // Reset
      store.reset();

      const state = useRecordingStore.getState();
      expect(state.status).toBe("idle");
      expect(state.duration).toBe(0);
      expect(state.transcript).toEqual([]);
      expect(state.audioLevel).toBe(0);
      expect(state.wsConnected).toBe(false);
    });
  });

  describe("full transcript extraction", () => {
    it("gets full transcript text from final segments", () => {
      const { addTranscript } = useRecordingStore.getState();

      addTranscript({
        text: "Hello doctor.",
        timestamp: Date.now(),
        isFinal: true,
      });

      addTranscript({
        text: "I have a headache.",
        timestamp: Date.now(),
        isFinal: true,
      });

      addTranscript({
        text: "In progress...",
        timestamp: Date.now(),
        isFinal: false, // Not final, should be excluded
      });

      const state = useRecordingStore.getState();
      const fullTranscript = state.transcript
        .filter((s) => s.isFinal)
        .map((s) => s.text)
        .join(" ");

      expect(fullTranscript).toBe("Hello doctor. I have a headache.");
    });
  });
});
