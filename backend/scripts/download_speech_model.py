"""One-time model setup for local offline ASR. Run while online; inference is local thereafter."""
from pathlib import Path
from huggingface_hub import snapshot_download
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/"models"/"cache"/"whisper-tiny"
DEST.mkdir(parents=True,exist_ok=True)
print("Downloading Systran/faster-whisper-tiny into",DEST)
snapshot_download(repo_id="Systran/faster-whisper-tiny",local_dir=str(DEST))
print("Model files installed locally. Set SPEECH_MODEL_PATH to",DEST)
