import json
import sqlite3
from datetime import datetime, timezone
from app.core.config import DB_PATH, DATA_DIR


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS interviews (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL,
          difficulty TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
          completed_at TEXT, resume_skills TEXT NOT NULL DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS answers (
          id INTEGER PRIMARY KEY AUTOINCREMENT, interview_id TEXT NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
          question_index INTEGER NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL,
          evaluation TEXT NOT NULL, duration_seconds REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS resumes (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, skills TEXT NOT NULL,
          text_length INTEGER NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS visual_metrics (
          interview_id TEXT PRIMARY KEY REFERENCES interviews(id) ON DELETE CASCADE,
          metrics TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)


def row_dict(row):
    return dict(row) if row is not None else None


def json_load(value, default=None):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default if default is not None else []
