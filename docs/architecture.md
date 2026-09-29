# Architecture

## Data flow

```text
Microphone clip → local FastAPI ASR adapter → editable transcript ─┐
Webcam frames → browser-local MediaPipe → summary metrics ─────────┤
Typed answers / resume ─────────────────────────────────────────────┘
                                   ↓
React client → FastAPI local API → interview service/state machine
                                      ├─ SQLite repository
                                      ├─ communication metrics
                                      └─ AI capability interfaces
                                           ├─ LLMProvider
                                           ├─ SpeechRecognizer
                                           ├─ EmbeddingProvider
                                           └─ VisionAnalyzer
```

The interface module is provider-neutral. Providers return app-owned data structures; they do not expose runtime sessions, tensors, device contexts, or vendor types to the interview engine.

## State model

The target interview flow is `CREATED → QUESTION_ASKED → RECORDING → TRANSCRIBING → ANALYZING → FOLLOWUP_DECISION → QUESTION_ASKED/COMPLETE`. Typed-answer operation skips audio states. The transition table is independently tested in `backend/app/interview/state_machine.py`.

## Storage

The API stores interviews, answers, extracted resume skill summaries, and optional visual summary metrics in SQLite under the repository's ignored local `data/` directory (override with `SNAPINTERVIEW_DATA_DIR`). The prototype holds pasted resume text in browser local storage. Raw microphone audio is processed through a temporary file deleted after ASR; webcam frames stay in the browser and are never sent to the API. Use a local browser profile and review backups. The API does not log answer/resume/audio content intentionally.

## Trust boundaries

The app is designed for a local process. The Vite dev server proxies API requests so the browser uses relative paths. Local API CORS is restricted to the local dev origin. Before LAN or public deployment, add authentication, CSRF protections where applicable, stronger file validation, and an explicit data-retention model.
