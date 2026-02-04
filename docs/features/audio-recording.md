# Audio Recording Feature

## Overview
Real-time audio capture and processing for doctor-patient conversation recording.

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Recording Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Select Patient  →  2. Choose Language  →  3. Start Recording │
│         │                      │                      │          │
│         ▼                      ▼                      ▼          │
│  [Patient Info       [Language Dropdown]    [Mic Button]        │
│   Displayed]          en/hi/ta/...          Animated]           │
│                                                                  │
│  4. Recording Active  →  5. Live Transcript  →  6. Stop/Pause   │
│         │                       │                     │          │
│         ▼                       ▼                     ▼          │
│  [Waveform            [Real-time text       [Stop Button]       │
│   Visualization]       appearing]            Save Audio]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Specifications

### Audio Capture
| Parameter | Value |
|-----------|-------|
| Sample Rate | 16000 Hz (optimal for speech) |
| Channels | Mono |
| Bit Depth | 16-bit |
| Format | WAV (raw), WebM (compressed) |
| Chunk Duration | 250ms (for streaming) |

### Browser Support
| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | Full | Recommended |
| Firefox | Full | - |
| Safari | Full | Requires user gesture |
| Edge | Full | - |
| Mobile Chrome | Full | - |
| Mobile Safari | Partial | iOS 14.5+ |

## Component Architecture

```typescript
// Frontend Components
AudioRecorder/
├── RecordButton.tsx      // Main record/stop button
├── PauseButton.tsx       // Pause/resume control
├── WaveformDisplay.tsx   // Real-time audio visualization
├── TranscriptDisplay.tsx // Live transcript feed
├── LanguageSelector.tsx  // Language dropdown
└── hooks/
    ├── useAudioRecorder.ts   // Recording logic
    ├── useWebSocket.ts       // Real-time streaming
    └── useTranscript.ts      // Transcript management
```

## API Endpoints

### Start Recording Session
```http
POST /api/v1/recording/start
Content-Type: application/json

{
  "patient_id": "uuid",
  "language": "en",
  "doctor_id": "uuid"
}

Response:
{
  "session_id": "uuid",
  "websocket_url": "wss://api.example.com/ws/recording/{session_id}"
}
```

### WebSocket Protocol
```javascript
// Client → Server (Audio Chunk)
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio",
  "sequence": 1,
  "timestamp": 1234567890
}

// Server → Client (Transcript Update)
{
  "type": "transcript",
  "text": "The patient reports...",
  "is_final": false,
  "confidence": 0.95
}
```

### Stop Recording
```http
POST /api/v1/recording/{session_id}/stop

Response:
{
  "session_id": "uuid",
  "audio_url": "/storage/recordings/{id}.wav",
  "transcript": "Full conversation text...",
  "duration_seconds": 300
}
```

## State Management

```typescript
interface RecordingState {
  status: 'idle' | 'recording' | 'paused' | 'processing' | 'completed';
  sessionId: string | null;
  startTime: Date | null;
  duration: number;
  transcript: TranscriptSegment[];
  audioLevel: number; // 0-100 for visualization
  error: string | null;
}

interface TranscriptSegment {
  id: string;
  text: string;
  timestamp: number;
  isFinal: boolean;
  confidence: number;
  language: string;
}
```

## Error Handling

| Error Code | Description | User Message | Recovery |
|------------|-------------|--------------|----------|
| MIC_DENIED | Microphone permission denied | "Please allow microphone access" | Show permission guide |
| MIC_NOT_FOUND | No microphone detected | "No microphone found" | Check device |
| WS_DISCONNECTED | WebSocket connection lost | "Connection lost, reconnecting..." | Auto-retry 3x |
| STT_ERROR | Speech-to-text service error | "Transcription temporarily unavailable" | Queue for retry |
| QUOTA_EXCEEDED | API quota exceeded | "Service limit reached" | Contact admin |

## Quality Considerations

### Audio Quality
- Implement noise suppression using Web Audio API
- Show audio level indicator to user
- Warn if audio level too low/high
- Support external microphone selection

### Network Handling
- Buffer audio locally during network issues
- Automatic reconnection with exponential backoff
- Save recording locally as backup
- Resume capability after disconnection

## Security

- Audio data encrypted in transit (TLS 1.3)
- Audio files encrypted at rest (AES-256)
- Session tokens expire after 1 hour
- Automatic cleanup of temporary audio files

## Testing Checklist

- [ ] Recording starts/stops correctly
- [ ] Pause/resume works
- [ ] Audio quality acceptable
- [ ] Transcript appears in real-time
- [ ] Language switching works
- [ ] Error states handled gracefully
- [ ] Works on all supported browsers
- [ ] Mobile recording works
- [ ] Long recording (30+ min) stable

## Related Documentation
- [Speech-to-Text Integration](../integrations/speech-to-text.md)
- [WebSocket Implementation](../backend/websocket.md)
- [Audio Storage](../backend/file-storage.md)
