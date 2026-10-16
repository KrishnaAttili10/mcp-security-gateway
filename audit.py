import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).with_name("audit.db")


def init_audit_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hospital_id TEXT NOT NULL,
                physician_id TEXT NOT NULL,
                action TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)


def log_access(hospital_id: str, physician_id: str, result: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO audit_logs
            (timestamp, hospital_id, physician_id, action, result)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            hospital_id,
            physician_id,
            "verify_license",
            result
        ))