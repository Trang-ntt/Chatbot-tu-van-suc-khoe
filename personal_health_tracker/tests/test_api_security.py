import bcrypt
from fastapi.testclient import TestClient
from app import db
from app.main import app

def test_viewer_requires_explicit_consent(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    with db.connect() as conn:
        owner = conn.execute(
            "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
            ("owner", bcrypt.hashpw(b"OwnerPass123", bcrypt.gensalt()).decode(), "user")
        ).lastrowid
        viewer = conn.execute(
            "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
            ("viewer", bcrypt.hashpw(b"ViewerPass123", bcrypt.gensalt()).decode(), "viewer")
        ).lastrowid
        conn.execute(
            "INSERT INTO metrics(user_id,metric,value,unit,measured_at) VALUES(?,?,?,?,?)",
            (owner, "weight", 60.0, "kg", "2026-11-20T08:00:00+00:00")
        )
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={"username":"viewer","password":"ViewerPass123"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        denied = client.get(f"/api/shared/{owner}/metrics", headers=headers)
        assert denied.status_code == 403
        with db.connect() as conn:
            conn.execute("INSERT INTO shares(owner_id,viewer_id,scope) VALUES(?,?,?)", (owner, viewer, "metrics"))
        allowed = client.get(f"/api/shared/{owner}/metrics", headers=headers)
        assert allowed.status_code == 200
        assert len(allowed.json()) == 1
        assert client.get("/api/profile", headers=headers).status_code == 403
