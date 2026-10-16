import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

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
                result TEXT NOT NULL,
                previous_hash TEXT,
                record_hash TEXT
            )
        """)

        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(audit_logs)")
        }

        if "previous_hash" not in columns:
            conn.execute(
                "ALTER TABLE audit_logs ADD COLUMN previous_hash TEXT"
            )

        if "record_hash" not in columns:
            conn.execute(
                "ALTER TABLE audit_logs ADD COLUMN record_hash TEXT"
            )


def log_access(hospital_id: str, physician_id: str, result: str):
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        # Lock the database for writing
        conn.execute("BEGIN IMMEDIATE")

        # Fetch the latest record's hash
        row = conn.execute("""
            SELECT record_hash
            FROM audit_logs
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        previous_hash = row[0] if row else "GENESIS"

        if previous_hash is None:
            raise RuntimeError("Audit chain is not initialized")

        # Generate the new record's timestamp and hash
        timestamp = datetime.now(timezone.utc).isoformat()
        action = "verify_license"

        record_hash = calculate_hash(
            timestamp,
            hospital_id,
            physician_id,
            action,
            result,
            previous_hash
        )

        # Store the new record
        conn.execute("""
            INSERT INTO audit_logs (
                timestamp,
                hospital_id,
                physician_id,
                action,
                result,
                previous_hash,
                record_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            hospital_id,
            physician_id,
            action,
            result,
            previous_hash,
            record_hash
        ))



def calculate_hash(timestamp, hospital_id, physician_id,
                   action, result, previous_hash):

    record_data = {
        "timestamp": timestamp,
        "hospital_id": hospital_id,
        "physician_id": physician_id,
        "action": action,
        "result": result,
        "previous_hash": previous_hash
    }

    serialized = json.dumps(record_data, sort_keys=True)

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def backfill_hashes():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("BEGIN IMMEDIATE")

        rows = conn.execute("""
            SELECT id, timestamp, hospital_id, physician_id,
                   action, result
            FROM audit_logs
            ORDER BY id ASC
        """).fetchall()

        previous_hash = "GENESIS"

        for row in rows:
            record_id, timestamp, hospital_id, physician_id, action, result = row

            record_hash = calculate_hash(
                timestamp,
                hospital_id,
                physician_id,
                action,
                result,
                previous_hash
            )

            conn.execute("""
                UPDATE audit_logs
                SET previous_hash = ?, record_hash = ?
                WHERE id = ?
            """, (previous_hash, record_hash, record_id))

            previous_hash = record_hash


def verify_audit_chain() -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT id, timestamp, hospital_id, physician_id,
                   action, result, previous_hash, record_hash
            FROM audit_logs
            ORDER BY id ASC
        """).fetchall()

    expected_previous_hash = "GENESIS"

    for row in rows:
        (
            record_id,
            timestamp,
            hospital_id,
            physician_id,
            action,
            result,
            previous_hash,
            record_hash
        ) = row

        # Check that this record links to the previous one
        if previous_hash != expected_previous_hash:
            print(f"Broken chain at record {record_id}")
            return False

        # Recalculate the hash using the stored record data
        expected_hash = calculate_hash(
            timestamp,
            hospital_id,
            physician_id,
            action,
            result,
            previous_hash
        )

        # Check whether the record was modified
        if record_hash != expected_hash:
            print(f"Tampering detected at record {record_id}")
            return False

        expected_previous_hash = record_hash

    return True