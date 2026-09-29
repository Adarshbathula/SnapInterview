"""Optional CPU Whisper adapter. Loads only a local model directory; never downloads on inference."""
import os
import tempfile
from pathlib import Path
from app.ai.interfaces.contracts import SpeechRecognizer
from app.core.config import ROOT

class LocalWhisperProvider:
    name = "faster-whisper-local-cpu"
    def __init__(self, model_path: str | None = None):
        self.model_path=Path(model_path or os.getenv("SPEECH_MODEL_PATH",ROOT/"models"/"cache"/"whisper-tiny"))
        self._model=None

    def ready(self) -> bool:
        return self.model_path.is_dir() and (self.model_path/"model.bin").is_file()

    def _load(self):
        if not self.ready():
            raise RuntimeError("Local Whisper model is not installed. Follow docs/speech-setup.md to download it before going offline.")
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("Optional speech dependencies are missing. Install backend/requirements-speech.txt.") from exc
            self._model=WhisperModel(str(self.model_path),device="cpu",compute_type=os.getenv("SPEECH_COMPUTE_TYPE","int8"),cpu_threads=max(1,int(os.getenv("SPEECH_CPU_THREADS",str(os.cpu_count() or 4)))))
        return self._model

    def transcribe(self, audio: bytes, content_type: str, language: str | None = None) -> dict:
        if not audio:
            raise ValueError("The audio recording is empty.")
        suffix={"audio/webm":".webm","audio/ogg":".ogg","audio/wav":".wav","audio/x-wav":".wav","audio/mp4":".mp4","audio/mpeg":".mp3","audio/aac":".aac"}.get(content_type.split(";")[0].strip().lower(),".audio")
        handle=tempfile.NamedTemporaryFile(prefix="snapinterview-",suffix=suffix,delete=False)
        path=Path(handle.name)
        try:
            with handle: handle.write(audio)
            model=self._load()
            segments,info=model.transcribe(str(path),language=None if not language or language=="auto" else language,vad_filter=True,word_timestamps=True)
            word_spans=[]
            text_parts=[]
            for segment in segments:
                text_parts.append(segment.text.strip())
                if segment.words:
                    for word in segment.words:
                        word_spans.append({"start":round(float(word.start),3),"end":round(float(word.end),3),"text":word.word.strip()})
                else:
                    word_spans.append({"start":round(float(segment.start),3),"end":round(float(segment.end),3),"text":segment.text.strip()})
            return {"text":" ".join(part for part in text_parts if part).strip(),"language":getattr(info,"language",None),"duration_seconds":round(float(getattr(info,"duration",0) or 0),2),"segments":word_spans,"model":"Whisper Tiny (local CPU)","provider":self.name}
        finally:
            try: path.unlink(missing_ok=True)
            except OSError: pass
