import bcrypt
from fastapi.testclient import TestClient
from app import db
from app.main import app

def make_user(conn, username, role="user", password="Password123!"):
    return conn.execute(
        "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
        (username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), role)
    ).lastrowid

def login(client, username, password="Password123!"):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}

def test_viewer_requires_scope_and_consent_and_can_be_revoked(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    with db.connect() as conn:
        owner = make_user(conn, "owner")
        viewer = make_user(conn, "viewer", "viewer")
        conn.execute("INSERT INTO profiles(user_id,full_name) VALUES(?,?)", (owner, "Demo Owner"))
        conn.execute(
            "INSERT INTO metrics(user_id,metric,value,unit,measured_at) VALUES(?,?,?,?,?)",
            (owner, "weight", 60.0, "kg", "2026-11-20T08:00:00+00:00")
        )
    with TestClient(app) as client:
        headers = login(client, "viewer")
        assert client.get(f"/api/shared/{owner}/metrics", headers=headers).status_code == 403
        with db.connect() as conn:
            share_id = conn.execute(
                "INSERT INTO shares(owner_id,viewer_id,scope) VALUES(?,?,?)",
                (owner, viewer, "metrics")
            ).lastrowid
        assert client.get(f"/api/shared/{owner}/metrics", headers=headers).status_code == 200
        assert client.get(f"/api/shared/{owner}/profile", headers=headers).status_code == 403
        with db.connect() as conn:
            conn.execute("UPDATE shares SET scope='profile_and_metrics' WHERE id=?", (share_id,))
        assert client.get(f"/api/shared/{owner}/profile", headers=headers).status_code == 200
        with db.connect() as conn:
            conn.execute("UPDATE shares SET revoked_at=CURRENT_TIMESTAMP WHERE id=?", (share_id,))
        assert client.get(f"/api/shared/{owner}/metrics", headers=headers).status_code == 403

def test_blood_pressure_secondary_threshold_creates_alert(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "bp.db"))
    db.init_db()
    with db.connect() as conn:
        make_user(conn, "patient")
    with TestClient(app) as client:
        headers = login(client, "patient")
        threshold = client.post("/api/thresholds", headers=headers, json={
            "metric": "blood_pressure", "min_value": 90, "max_value": 140,
            "min_secondary": 60, "max_secondary": 80, "sudden_change_pct": 20,
            "source_name": "WHO reference", "source_url": "https://www.who.int/",
            "context": "Demo configuration only"
        })
        assert threshold.status_code == 200, threshold.text
        saved = client.post("/api/metrics", headers=headers, json={
            "metric": "blood_pressure", "value": 120, "secondary_value": 90,
            "unit": "mmHg", "measured_at": "2026-11-20T08:00:00+00:00"
        })
        assert saved.status_code == 200, saved.text
        alerts = client.get("/api/alerts", headers=headers).json()
        assert any(a["alert_type"] == "threshold" for a in alerts)

def test_admin_can_assign_viewer_role_but_cannot_read_health_data(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "roles.db"))
    db.init_db()
    with db.connect() as conn:
        admin = make_user(conn, "admin", "admin")
        target = make_user(conn, "target")
    with TestClient(app) as client:
        headers = login(client, "admin")
        changed = client.put(f"/api/admin/users/{target}/role", headers=headers, json={"role": "viewer"})
        assert changed.status_code == 200, changed.text
        assert client.get("/api/profile", headers=headers).status_code == 403
        assert client.put(f"/api/admin/users/{admin}/role", headers=headers, json={"role": "admin"}).status_code == 400

def test_csv_import_uses_validation_and_reports_skipped_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "csv.db"))
    db.init_db()
    with db.connect() as conn:
        make_user(conn, "csvuser")
    with TestClient(app) as client:
        headers = login(client, "csvuser")
        csv_data = (
            "metric,value,secondary_value,unit,measured_at,note\n"
            "weight,62,,kg,2026-11-20T08:00:00+00:00,synthetic\n"
            "blood_pressure,120,,mmHg,2026-11-20T08:00:00+00:00,missing diastolic\n"
        )
        response = client.post("/api/metrics/import-csv", headers=headers, files={
            "file": ("sample.csv", csv_data.encode(), "text/csv")
        })
        assert response.status_code == 200, response.text
        assert response.json() == {"inserted": 1, "skipped": 1}
