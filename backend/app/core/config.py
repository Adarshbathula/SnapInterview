import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(os.getenv("SNAPINTERVIEW_DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "snapinterview.sqlite3"
AI_BACKEND = os.getenv("AI_BACKEND", "auto")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"
MAX_RESUME_CHARS = 100_000
