import bcrypt
from datetime import date
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
        assert client.post("/api/assistant/start").status_code == 401


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


def test_medication_due_uses_browser_local_time(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "med-due.db"))
    db.init_db()
    with db.connect() as conn:
        make_user(conn, "dueuser")
    with TestClient(app) as client:
        headers = auth(client, "dueuser")
        today = date.today().isoformat()
        saved = client.post("/api/medications", headers=headers, json={
            "name": "Thuốc kiểm thử", "instructions": "Theo đơn",
            "schedule_times": ["08:00"], "start_date": today,
            "repeat_rule": "daily"
        })
        assert saved.status_code == 200, saved.text
        due = client.get("/api/medications/due?local_time=" + today + "T08:00", headers=headers)
        assert due.status_code == 200, due.text
        assert len(due.json()) == 1
        invalid = client.get("/api/medications/due?local_time=bad-time", headers=headers)
        assert invalid.status_code == 400


def test_personal_chatbot_analyzes_saved_health_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "insights.db"))
    db.init_db()
    with db.connect() as conn:
        uid = make_user(conn, "insightuser")
        conn.execute(
            "INSERT INTO profiles(user_id,birth_date,sex,health_goals) VALUES(?,?,?,?)",
            (uid, "1998-06-01", "Nam", "Theo dõi cân nặng")
        )
        for value, stamp in ((70, "2026-11-19T08:00:00+00:00"),
                             (71, "2026-11-20T08:00:00+00:00"),
                             (72, "2026-11-21T08:00:00+00:00")):
            conn.execute(
                "INSERT INTO metrics(user_id,metric,value,unit,measured_at) VALUES(?,?,?,?,?)",
                (uid, "weight", value, "kg", stamp)
            )
    with TestClient(app) as client:
        headers = auth(client, "insightuser")
        sid = client.post("/api/assistant/start", headers=headers).json()["session_id"]
        response = client.post("/api/assistant/message", headers=headers, json={
            "session_id": sid, "message": "Hãy phân tích xu hướng các chỉ số sức khỏe của tôi"
        })
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["loai"] == "tu_van_ca_nhan"
        weight = next(item for item in payload["health_insights"] if item["metric"] == "weight")
        assert weight["trend"] == "tăng"
        assert weight["record_count"] == 3
