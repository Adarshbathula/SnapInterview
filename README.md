# SnapInterview

**Private, offline-first interview practice — designed for hardware-independent local AI.**

SnapInterview is a local web application for practicing technical and behavioral interviews. Its architecture separates the interview workflow from AI task interfaces and runtime providers, so CPU reference execution can be developed first and device-specific execution can be added without changing the UI or interview engine.

> **Current build status:** This repository contains a working product prototype with a React interface, local FastAPI service, SQLite persistence, adaptive rubric-based follow-ups, resume keyword extraction, local hardware/runtime discovery, and tests. It does **not** include speech-recognition weights, a local LLM, or a Snapdragon implementation. It bundles MediaPipe Face Landmarker assets for optional browser-local camera signals. The current answer evaluator is a transparent deterministic keyword rubric—not an LLM and not validated grading. No Snapdragon benchmark has been measured.

## Problem and solution

Interview practice benefits from repetition and evidence-based feedback, but voice, webcam, resume, and answer data are sensitive. SnapInterview is designed to process session content on-device after required model assets are installed. It provides a private local practice workflow and an extensible path toward local speech, language, and vision models.

## Architecture

```text
React + Vite UI
     │ local HTTP API
FastAPI application ─ SQLite / local resume context
     │ contracts only
SpeechRecognizer · LLMProvider · EmbeddingProvider · VisionAnalyzer
     │ provider selection
CPU reference providers · future ONNX/QNN providers
     │
Intel CPU / available runtime ─ future Snapdragon CPU/GPU/NPU runtime
```

Business logic calls task interfaces, never a model SDK directly. Backend selection is configuration-driven (`AI_BACKEND`). An unavailable backend falls back to the implemented local development evaluator and the runtime endpoint reports that fallback. See [architecture](docs/architecture.md) and [runtime notes](docs/ai-runtime.md).

## Features in this prototype

- Interview setup across ten configurable topic categories and three difficulty levels.
- Question-by-question practice and rubric-generated follow-up prompts.
- Transcript text entry and answer feedback with score components and transcript-linked evidence.
- Resume text input, local keyword skill extraction, and resume-aware question prompts.
- Microphone capture with browser permission, local audio recording, optional CPU Whisper Tiny transcription, transcript editing, WPM/filler-word metrics, and long-pause estimates when word timestamps are available. ASR model weights are an optional one-time local download.
- Optional webcam preview and local MediaPipe Face Landmarker signals: face-in-frame, face centering, and approximate head-position stability. Camera frames are not uploaded or stored; only the explicit session summary metrics are saved.
- SQLite session/answer/visual-summary persistence; resume content is held in browser local storage while extracted skills are stored locally by the API.
- Runtime/device page that inspects the current host and installed ONNX Runtime execution providers when available.
- Responsive dashboard, results, device status, and configuration screens.
- Tests for provider-independent business contracts, metrics, question catalog, and state transitions.

## Privacy and offline behavior

The application API makes no cloud inference calls. When run locally, session answers and camera summary metrics are stored in SQLite, while pasted resume text is held in that browser profile's local storage. Microphone clips are held in browser memory; when the optional local Whisper model is ready, a clip is sent only to the local API, written to a temporary file for inference, then deleted. With ASR unavailable, clips are not uploaded and can be previewed/downloaded from the browser tab. Webcam frames are processed in-browser by the bundled MediaPipe model and are never sent to the API; only summary percentages are saved after the user stops analysis. **Do not enter real sensitive data into the hosted development preview:** that preview runs in the Agent Mode sandbox, not on your laptop. For private use, run the app locally and review your local storage/backups.

Speech model weights are not bundled; see [speech setup](docs/speech-setup.md) for one-time local model installation. Do not treat rubric scores or webcam measurements as objective assessments of a candidate's ability or psychological state.

## Quick start

Requirements: Python 3.11+ and Node.js 20+.

1. Create and activate a virtual environment; install the backend requirements.
2. Start the API from the `backend` directory.
3. In another terminal, install frontend dependencies and start Vite.

```bash
cd backend
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: enable on-device microphone transcription (download before going offline)
# pip install -r requirements-speech.txt
# python scripts/download_speech_model.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). Vite proxies `/api` to the local FastAPI service. API docs are available at `http://127.0.0.1:8000/docs`.

For offline deployment, install dependencies and model assets before disconnecting from the internet. This prototype's implemented rubric and app do not require model downloads.

## Configuration

Copy `.env.example` to `.env` if you need overrides. The service reads `AI_BACKEND` and `OFFLINE_MODE`; an unimplemented specialized backend is not silently presented as active. Model data, user content, and local secrets should not be committed.

## Tests and build

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## Models and runtime

See [model manifest](models/manifests/registry.json), [runtime architecture](docs/ai-runtime.md), and [Snapdragon deployment plan](docs/snapdragon.md). Candidate models must be selected from the current official target-device catalog and then checked for license, accuracy, memory, latency, and runtime support. Model presence in a catalog does not imply this repository has installed or validated it.

For Snapdragon deployment, use Qualcomm AI Hub and official Qualcomm documentation as the source of truth. On-device compilation, provider compatibility, model correctness, and performance must be validated on the intended HP Snapdragon PC. No Qualcomm-specific runtime package or API is assumed here.

## Benchmarks

The benchmark directory contains a harness and reporting template; it does not include fabricated results. A valid result requires a named model, backend, machine, warm-up policy, input set, repeated timing, and memory measurement. Snapdragon benchmark status remains **Not yet measured**.

## Limitations and next steps

1. Install the optional local Whisper package and model weights to activate speech transcription; validate quality and speed on the development laptop.
2. Add a local structured-output LLM provider and schema validation; calibrate the evaluation rubric.
3. Improve resume parsing and semantic project extraction.
4. Validate the bundled browser-local face metrics across browsers, camera conditions, and accessibility needs; add no psychological interpretation.
5. Implement Snapdragon adapters after verifying the specific HP device, supported models, runtime, and official documentation.
6. Expand API integration tests, packaging, and repeatable hardware benchmarks.

## License

MIT. See [LICENSE](LICENSE).
