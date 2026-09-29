# Demo script

1. Open Dashboard and point out the local/offline status and lack of cloud inference calls.
2. Start the demo interview. The demo supplies sample Python/RAG/FastAPI skills, not a real user's resume.
3. Click **Record answer** to grant microphone permission and capture locally. With the optional Whisper model installed, review the local transcript; without it, the clip remains in browser memory for playback/download and text entry remains available.
4. Optionally enable the webcam. Explain that MediaPipe runs in-browser and reports only rough face-in-frame/centering/head-motion signals; no frames are stored or sent, and no psychological traits are inferred.
5. Submit an answer and inspect the evaluator label and transcript-based evidence.
6. Choose the adaptive follow-up and explain that the prompt is generated from rubric concepts not yet mentioned.
7. Finish the session and review category scores and answer-level evidence, plus optional visual summary metrics.
8. Open Device & AI. Show actual host/runtime detection, speech-model readiness, included local vision model, and **Not yet measured** Snapdragon status.
9. Explain the migration boundary: task interfaces and interview workflow stay stable; a target-validated provider/model changes beneath them.

Be explicit that the evaluator is a development rubric, not a local LLM, and that microphone transcription and webcam analysis are not installed in this build.
