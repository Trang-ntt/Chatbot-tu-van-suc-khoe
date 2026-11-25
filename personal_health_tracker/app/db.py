import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[1] / "health_tracker.db"))

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','user','viewer')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS profiles (
 user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 full_name TEXT DEFAULT '', birth_date TEXT DEFAULT '', sex TEXT DEFAULT '',
 height_cm REAL, medical_history TEXT DEFAULT '', health_goals TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS metrics (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 metric TEXT NOT NULL, value REAL, secondary_value REAL, unit TEXT NOT NULL,
 measured_at TEXT NOT NULL, note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_metrics_user_time ON metrics(user_id, measured_at);
CREATE TABLE IF NOT EXISTS thresholds (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 metric TEXT NOT NULL, min_value REAL, max_value REAL, sudden_change_pct REAL DEFAULT 20,
 source_name TEXT NOT NULL, source_url TEXT NOT NULL, context TEXT DEFAULT '',
 UNIQUE(user_id, metric)
);
CREATE TABLE IF NOT EXISTS alerts (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 metric TEXT NOT NULL, metric_id INTEGER, alert_type TEXT NOT NULL, message TEXT NOT NULL,
 severity TEXT NOT NULL DEFAULT 'warning', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 acknowledged INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS reminders (
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 reminder_type TEXT NOT NULL, title TEXT NOT NULL, due_at TEXT NOT NULL, repeat_rule TEXT DEFAULT 'none',
 active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS shares (
 id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 viewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 scope TEXT NOT NULL DEFAULT 'metrics', consented_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 revoked_at TEXT, UNIQUE(owner_id, viewer_id, scope)
);
"""

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)

def rowdict(row):
    return dict(row) if row else None
