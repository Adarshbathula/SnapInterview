# Local microphone and speech setup

The frontend records microphone audio only after the user clicks **Record** and grants browser permission. It sends the clip to the local FastAPI endpoint; the API writes a temporary audio file only for inference and deletes it afterward. Raw audio is not written to SQLite. If the ASR model is unavailable, the app does not send the clip; the transcript can still be typed. The local model status is shown in the UI.

## Install an offline CPU speech model (one-time online setup)

Use Python 3.11+, then from `backend/`:

```bash
pip install -r requirements-speech.txt
python scripts/download_speech_model.py
```

The setup script downloads `Systran/faster-whisper-tiny` (a converted Whisper Tiny model) into the ignored `models/cache/whisper-tiny/` folder. Review the upstream model license and source before redistribution. Keep the model directory available to the backend when offline. The ASR adapter checks for a local `model.bin` and never downloads weights during inference.

By default the provider loads that repository model directory with `device=cpu` and `compute_type=int8`. To override:

```bash
# macOS/Linux
export SPEECH_MODEL_PATH="/absolute/path/to/whisper-tiny"
# Windows PowerShell
$env:SPEECH_MODEL_PATH="C:\path\to\whisper-tiny"
```

Restart FastAPI afterward. Check `/api/speech/status`; it should report `ready: true` before recording a speech answer. Processing is CPU-based in this implementation; model optimization on other hardware requires its own provider and validation.

## Supported behavior and limits

- Browser MediaRecorder formats supported: WebM/Opus, OGG, WAV, MP4, MP3, and AAC, subject to the browser codec.
- Maximum upload: 25 MB. Audio is sent only to the configured local backend.
- ASR returns transcript text and word timing; answer duration, WPM, filler-word count, and pauses of at least 1.5 seconds can be calculated. Word timing can be imperfect.
- If a recording cannot be transcribed, the UI leaves it available as a local download and the candidate may type/edit the answer.
- Before going offline, install the optional Python dependencies and download the model once.
