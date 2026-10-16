import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("consent.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consent (
                physician_id TEXT NOT NULL,
                hospital_id TEXT NOT NULL,
                granted INTEGER NOT NULL,
                PRIMARY KEY (physician_id, hospital_id)
            )
        """)

        conn.executemany("""
            INSERT OR IGNORE INTO consent
            (physician_id, hospital_id, granted)
            VALUES (?, ?, ?)
        """, [
            ("Krishna", "hospital_a", 1),
            ("Advaita", "hospital_b", 1)
        ])


def has_consent(physician_id: str, hospital_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT granted
            FROM consent
            WHERE physician_id = ? AND hospital_id = ?
        """, (physician_id, hospital_id)).fetchone()

    return bool(row[0]) if row else False


def revoke_consent(physician_id: str, hospital_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            UPDATE consent
            SET granted = 0
            WHERE physician_id = ? AND hospital_id = ?
        """, (physician_id, hospital_id))

        return cursor.rowcount > 0

def grant_consent(physician_id: str, hospital_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO consent (physician_id, hospital_id, granted)
            VALUES (?, ?, 1)
            ON CONFLICT(physician_id, hospital_id)
            DO UPDATE SET granted = 1
        """, (physician_id, hospital_id))

        return cursor.rowcount > 0