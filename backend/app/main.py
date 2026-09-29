import json
import os
import re
import uuid
import importlib.util
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from app.ai.interfaces.contracts import EvaluationInput
from app.ai.runtime.backend_selector import select_evaluator
from app.ai.providers.local_whisper import LocalWhisperProvider
from app.analytics.communication import communication_metrics
from app.core.config import MAX_RESUME_CHARS, OFFLINE_MODE, ROOT
from app.core.database import connect, init_db, now_iso, json_load
from app.hardware.detector import detect_hardware
from app.interview.catalog import CATEGORIES, DIFFICULTIES, make_questions

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield

app = FastAPI(title="SnapInterview API", version="0.1.0", description="Local-first interview coaching API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])
evaluator, selection = select_evaluator()

class InterviewCreate(BaseModel):
    category: str = "Software Engineering"
    difficulty: str = "Intermediate"
    question_count: int = Field(default=5, ge=3, le=10)
    resume_skills: list[str] = Field(default_factory=list, max_length=20)

class SpeechSegmentIn(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    text: str = Field(default="", max_length=500)

class AnswerIn(BaseModel):
    question: str = Field(min_length=4, max_length=2000)
    answer: str = Field(min_length=1, max_length=12000)
    expected_concepts: list[str] = Field(default_factory=list, max_length=20)
    duration_seconds: float = Field(default=0, ge=0, le=7200)
    speech_segments: list[SpeechSegmentIn] = Field(default_factory=list, max_length=3000)

class VisualMetricsIn(BaseModel):
    face_visibility: int = Field(ge=0, le=100)
    face_centering: int = Field(ge=0, le=100)
    head_position_stability: int = Field(ge=0, le=100)
    samples: int = Field(ge=0, le=100000)
    duration_seconds: int = Field(ge=0, le=7200)
    source: str = Field(default="MediaPipe Face Landmarker, on-device", max_length=160)

class ResumeIn(BaseModel):
    name: str = Field(default="My resume", max_length=160)
    text: str = Field(min_length=1, max_length=MAX_RESUME_CHARS)

speech_provider = LocalWhisperProvider()
MAX_AUDIO_BYTES = 25 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/ogg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/mpeg", "audio/aac"}

def speech_status_data():
    try:
        package_installed = importlib.util.find_spec("faster_whisper") is not None
    except (ImportError, ValueError):
        package_installed = False
    model_ready = speech_provider.ready()
    return {"ready": bool(package_installed and model_ready), "package_installed": package_installed, "model_installed": model_ready, "model_name": "Whisper Tiny · local CPU" if model_ready else "Not installed", "inference": "Local CPU only; no network download during transcription", "max_audio_mb": 25}

@app.get("/api/health")
def health():
    return {"status": "ok", "offline_mode": OFFLINE_MODE, "inference": "local rule-based evaluator", "cloud_calls": False}

@app.get("/api/speech/status")
def speech_status():
    return speech_status_data()

@app.post("/api/speech/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...), language: str = Form(default="en")):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_AUDIO_BYTES + 1024 * 1024:
        raise HTTPException(413, "Recording exceeds the 25 MB limit.")
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(415, "Unsupported audio format. Use WebM, OGG, WAV, MP4, MP3, or AAC.")
    status = speech_status_data()
    if not status["ready"]:
        raise HTTPException(503, "Local speech model is not installed. See docs/speech-setup.md. The app does not forward audio to a cloud service.")
    audio = await file.read(MAX_AUDIO_BYTES + 1)
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Recording exceeds the 25 MB limit.")
    if not audio:
        raise HTTPException(400, "The recording is empty.")
    try:
        result = await run_in_threadpool(speech_provider.transcribe, audio, content_type, language)
        result["communication_metrics"] = communication_metrics(result["text"], result["duration_seconds"], result["segments"])
        return result
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422, f"Local transcription failed for this audio: {type(exc).__name__}") from exc
    finally:
        await file.close()

@app.get("/api/topics")
def topics():
    return {"categories": CATEGORIES, "difficulties": DIFFICULTIES}

@app.get("/api/runtime")
def runtime():
    info = detect_hardware()
    speech = speech_status_data()
    vision_ready = (ROOT / "frontend" / "public" / "models" / "face_landmarker.task").is_file()
    info.update({"ai_backend_setting": selection["requested"], "llm_provider": evaluator.name, "provider_fallback": selection["fallback"], "provider_message": selection["message"], "speech_model": speech["model_name"], "speech_ready": speech["ready"], "vision_model": "MediaPipe Face Landmarker · browser local" if vision_ready else "Not installed", "vision_ready": vision_ready, "loaded_models": [], "offline_mode": OFFLINE_MODE, "snapdragon_benchmark": "Not yet measured"})
    return info

@app.get("/api/resume/latest")
def latest_resume():
    with connect() as db:
        row = db.execute("SELECT name,skills,text_length,updated_at FROM resumes ORDER BY id DESC LIMIT 1").fetchone()
    return {**dict(row), "skills": json_load(row["skills"])} if row else {"name": None, "skills": [], "text_length": 0}

@app.post("/api/resume")
def save_resume(payload: ResumeIn):
    skills_pool = ["Python", "Java", "C++", "JavaScript", "TypeScript", "React", "FastAPI", "Django", "Flask", "SQL", "MongoDB", "PostgreSQL", "Machine Learning", "Deep Learning", "RAG", "LangChain", "LangGraph", "FAISS", "AWS", "Docker", "Kubernetes", "System Design", "Data Structures"]
    low = payload.text.lower()
    skills = [s for s in skills_pool if re.search(r"(?<!\w)" + re.escape(s.lower()) + r"(?!\w)", low)]
    with connect() as db:
        db.execute("INSERT INTO resumes(name,skills,text_length,updated_at) VALUES(?,?,?,?)", (payload.name.strip() or "My resume", json.dumps(skills), len(payload.text), now_iso()))
    return {"name": payload.name, "skills": skills, "text_length": len(payload.text), "processing": "local keyword extraction (development baseline)"}

@app.post("/api/interviews")
def create_interview(payload: InterviewCreate):
    if payload.category not in CATEGORIES:
        raise HTTPException(400, "Unsupported interview category")
    if payload.difficulty not in DIFFICULTIES:
        raise HTTPException(400, "Unsupported difficulty")
    interview_id = str(uuid.uuid4())
    created = now_iso()
    skills = list(dict.fromkeys(s.strip() for s in payload.resume_skills if s.strip()))
    title = f"{payload.category} practice"
    with connect() as db:
        db.execute("INSERT INTO interviews(id,title,category,difficulty,status,created_at,resume_skills) VALUES(?,?,?,?,?,?,?)", (interview_id, title, payload.category, payload.difficulty, "active", created, json.dumps(skills)))
    questions = make_questions(payload.category, payload.question_count, skills)
    return {"id": interview_id, "title": title, "category": payload.category, "difficulty": payload.difficulty, "status": "active", "created_at": created, "questions": questions}

@app.get("/api/interviews")
def list_interviews():
    with connect() as db:
        rows = db.execute("SELECT i.*, COUNT(a.id) AS answer_count FROM interviews i LEFT JOIN answers a ON a.interview_id=i.id GROUP BY i.id ORDER BY i.created_at DESC LIMIT 20").fetchall()
    return [{**dict(r), "resume_skills": json_load(r["resume_skills"])} for r in rows]

@app.post("/api/interviews/{interview_id}/answers")
def submit_answer(interview_id: str, payload: AnswerIn):
    with connect() as db:
        session = db.execute("SELECT status FROM interviews WHERE id=?", (interview_id,)).fetchone()
        if not session:
            raise HTTPException(404, "Interview not found")
        if session["status"] != "active":
            raise HTTPException(409, "Interview is already complete")
        result = evaluator.evaluate_answer(EvaluationInput(payload.question, payload.answer, payload.expected_concepts))
        data = result.__dict__
        segment_data=[segment.model_dump() for segment in payload.speech_segments]
        data["communication_metrics"] = communication_metrics(payload.answer, payload.duration_seconds, segment_data if segment_data else None)
        question_index = db.execute("SELECT COUNT(*) FROM answers WHERE interview_id=?", (interview_id,)).fetchone()[0]
        db.execute("INSERT INTO answers(interview_id,question_index,question,answer,evaluation,duration_seconds,created_at) VALUES(?,?,?,?,?,?,?)", (interview_id, question_index, payload.question, payload.answer, json.dumps(data), payload.duration_seconds, now_iso()))
    return data

@app.post("/api/interviews/{interview_id}/complete")
def complete_interview(interview_id: str):
    with connect() as db:
        session = db.execute("SELECT * FROM interviews WHERE id=?", (interview_id,)).fetchone()
        if not session:
            raise HTTPException(404, "Interview not found")
        rows = db.execute("SELECT * FROM answers WHERE interview_id=? ORDER BY id", (interview_id,)).fetchall()
        visual_row = db.execute("SELECT metrics FROM visual_metrics WHERE interview_id=?", (interview_id,)).fetchone()
        if not rows:
            raise HTTPException(400, "Answer at least one question before completing")
        answers = [{**dict(r), "evaluation": json_load(r["evaluation"], {})} for r in rows]
        keys = ["technical_accuracy", "relevance", "completeness"]
        averages = {k: round(sum(a["evaluation"].get(k, 0) for a in answers) / len(answers)) for k in keys}
        overall = round(sum(averages.values()) / len(averages))
        strengths = list(dict.fromkeys(x for a in answers for x in a["evaluation"].get("strengths", [])))[:5]
        improvements = list(dict.fromkeys(x for a in answers for x in a["evaluation"].get("improvements", [])))[:5]
        result = {"id": interview_id, "title": session["title"], "category": session["category"], "difficulty": session["difficulty"], "overall": overall, "scores": averages, "strengths": strengths, "improvements": improvements, "answers": answers, "visual_metrics": json_load(visual_row["metrics"], {}) if visual_row else None, "evaluator": evaluator.name, "created_at": session["created_at"]}
        db.execute("UPDATE interviews SET status='completed', completed_at=? WHERE id=?", (now_iso(), interview_id))
    return result

@app.post("/api/interviews/{interview_id}/visual-metrics")
def save_visual_metrics(interview_id: str, payload: VisualMetricsIn):
    with connect() as db:
        session=db.execute("SELECT status FROM interviews WHERE id=?",(interview_id,)).fetchone()
        if not session:
            raise HTTPException(404,"Interview not found")
        db.execute("INSERT INTO visual_metrics(interview_id,metrics,created_at) VALUES(?,?,?) ON CONFLICT(interview_id) DO UPDATE SET metrics=excluded.metrics,created_at=excluded.created_at",(interview_id,json.dumps(payload.model_dump()),now_iso()))
    return {"saved":True,"metrics":payload.model_dump(),"note":"Only summary metrics saved; camera frames are not stored."}

@app.get("/api/interviews/{interview_id}")
def get_interview(interview_id: str):
    with connect() as db:
        session = db.execute("SELECT * FROM interviews WHERE id=?", (interview_id,)).fetchone()
        if not session:
            raise HTTPException(404, "Interview not found")
        rows = db.execute("SELECT * FROM answers WHERE interview_id=? ORDER BY id", (interview_id,)).fetchall()
        visual_row = db.execute("SELECT metrics FROM visual_metrics WHERE interview_id=?", (interview_id,)).fetchone()
    return {**dict(session), "answers": [{**dict(r), "evaluation": json_load(r["evaluation"], {})} for r in rows], "visual_metrics": json_load(visual_row["metrics"], {}) if visual_row else None}
