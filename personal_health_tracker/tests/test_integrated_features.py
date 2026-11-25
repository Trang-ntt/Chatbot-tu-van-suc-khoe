import bcrypt
from fastapi.testclient import TestClient
from app import db
from app.main import app


def make_user(conn, username, role="user"):
    return conn.execute(
        "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
        (username, bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode(), role)
    ).lastrowid


def auth(client, username):
    r = client.post("/api/auth/login", json={"username": username, "password": "Password123!"})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def test_guest_symptom_analysis_works_without_login(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "guest.db"))
    db.init_db()
    with TestClient(app) as client:
        start = client.post("/api/symptoms/start", json={"age": 23, "sex": "Nữ"})
        assert start.status_code == 200, start.text
        sid = start.json()["session_id"]
        result = client.post("/api/symptoms/message", json={
            "session_id": sid, "message": "Tôi bị sốt, ho và đau họng"
        })
        assert result.status_code == 200, result.text
        assert result.json()["loai"] in {"cau_hoi", "ket_qua"}
        assert client.post("/api/assistant/start").status_code == 403


def test_personal_assistant_is_authenticated_and_user_scoped(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "assistant.db"))
    db.init_db()
    with db.connect() as conn:
        first = make_user(conn, "first")
        second = make_user(conn, "second")
        for uid in (first, second):
            conn.execute(
                "INSERT INTO profiles(user_id,birth_date,sex) VALUES(?,?,?)",
                (uid, "2000-01-01", "Nữ")
            )
        conn.execute(
            "INSERT INTO metrics(user_id,metric,value,unit,measured_at) VALUES(?,?,?,?,?)",
            (first, "weight", 49, "kg", "2026-11-20T08:00:00+00:00")
        )
        conn.execute(
            "INSERT INTO metrics(user_id,metric,value,unit,measured_at) VALUES(?,?,?,?,?)",
            (second, "weight", 91, "kg", "2026-11-20T08:00:00+00:00")
        )
    with TestClient(app) as client:
        h1, h2 = auth(client, "first"), auth(client, "second")
        sid = client.post("/api/assistant/start", headers=h1).json()["session_id"]
        own = client.post("/api/assistant/message", headers=h1, json={
            "session_id": sid, "message": "Tôi bị sốt và ho"
        })
        assert own.status_code == 200, own.text
        assert "49" in own.json()["health_context"]
        assert "91" not in own.json()["health_context"]
        cross = client.post("/api/assistant/message", headers=h2, json={
            "session_id": sid, "message": "Tôi bị đau đầu"
        })
        assert cross.status_code == 404


def test_appointment_and_medication_workflows_are_user_scoped(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "care.db"))
    db.init_db()
    with db.connect() as conn:
        make_user(conn, "careuser")
        make_user(conn, "otheruser")
    with TestClient(app) as client:
        h1, h2 = auth(client, "careuser"), auth(client, "otheruser")
        appointment = client.post("/api/appointments", headers=h1, json={
            "specialty": "Nội tổng quát", "preferred_at": "2027-01-15T09:00:00+07:00",
            "reason": "Khám sức khỏe định kỳ"
        })
        assert appointment.status_code == 200, appointment.text
        appointment_id = appointment.json()["id"]
        assert client.get("/api/appointments", headers=h2).json() == []
        assert client.delete(f"/api/appointments/{appointment_id}", headers=h2).status_code == 404

        med = client.post("/api/medications", headers=h1, json={
            "name": "Thuốc demo", "instructions": "Theo đơn bác sĩ",
            "schedule_times": ["08:00", "20:00"], "start_date": "2026-11-25",
            "repeat_rule": "daily"
        })
        assert med.status_code == 200, med.text
        listed = client.get("/api/medications", headers=h1).json()
        assert listed[0]["name"] == "Thuốc demo"
        assert client.get("/api/medications", headers=h2).json() == []
        assert client.delete(f"/api/medications/{med.json()['id']}", headers=h2).status_code == 404


def test_assistant_requires_profile_age_and_sex(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "profile-required.db"))
    db.init_db()
    with db.connect() as conn:
        make_user(conn, "incomplete")
    with TestClient(app) as client:
        headers = auth(client, "incomplete")
        response = client.post("/api/assistant/start", headers=headers)
        assert response.status_code == 400
        assert "Hồ sơ cá nhân" in response.json()["detail"]
