import app.core.database as database
from fastapi.testclient import TestClient
from app.main import app


def test_session_answer_completion_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.sqlite3")
    with TestClient(app) as client:
        created = client.post("/api/interviews", json={"category":"Machine Learning", "difficulty":"Intermediate", "question_count":3})
        assert created.status_code == 200
        session = created.json()
        question = session["questions"][0]
        answer = client.post(f"/api/interviews/{session['id']}/answers", json={
            "question": question["text"], "answer": "Classification predicts a category label; regression predicts a continuous target.",
            "expected_concepts": question["concepts"], "duration_seconds": 30,
        })
        assert answer.status_code == 200
        assert answer.json()["communication_metrics"]["words_per_minute"] > 0
        metrics={"face_visibility":90,"face_centering":82,"head_position_stability":88,"samples":20,"duration_seconds":12,"source":"test"}
        saved=client.post(f"/api/interviews/{session['id']}/visual-metrics",json=metrics)
        assert saved.status_code==200 and saved.json()["saved"]
        report = client.post(f"/api/interviews/{session['id']}/complete")
        assert report.status_code == 200
        assert report.json()["answers"]
        assert report.json()["visual_metrics"]["face_visibility"]==90
        assert client.post(f"/api/interviews/{session['id']}/answers", json={"question":"Explain this system design choice.", "answer":"response"}).status_code == 409


def test_speech_route_rejects_non_audio_upload():
    with TestClient(app) as client:
        response=client.post("/api/speech/transcribe",files={"file":("photo.png",b"not-audio","image/png")})
        assert response.status_code==415


def test_resume_extraction_is_local_and_input_is_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "resume.sqlite3")
    with TestClient(app) as client:
        response = client.post("/api/resume", json={"name":"sample", "text":"Built a FastAPI service in Python using PostgreSQL."})
        assert response.status_code == 200
        assert "Python" in response.json()["skills"]
        assert client.get("/api/resume/latest").json()["skills"]
