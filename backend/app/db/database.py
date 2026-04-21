import os
import re
import sqlite3
from hashlib import sha256
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = f"sqlite:///{BASE_DIR}/jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def _build_job_fingerprint(company, title, description):
    normalized_company = (company or "").strip().lower()
    normalized_title = (title or "").strip().lower()
    normalized_description = re.sub(r"\s+", " ", (description or "")).strip().lower()
    payload = f"{normalized_company}|{normalized_title}|{normalized_description}"
    return sha256(payload.encode("utf-8")).hexdigest()


def ensure_sqlite_schema():
    db_path = os.path.join(BASE_DIR, "jobs.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(jobs)")
    existing_columns = {row[1] for row in cur.fetchall()}

    required_columns = {
        "fingerprint": "TEXT",
        "source": "TEXT DEFAULT 'MANUAL'",
        "resume_path": "TEXT",
        "tracking_status": "TEXT DEFAULT 'NEW'",
        "times_seen": "INTEGER DEFAULT 1",
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
        "last_seen_at": "DATETIME",
    }

    for column, definition in required_columns.items():
        if column not in existing_columns:
            cur.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

    cur.execute("UPDATE jobs SET source = 'MANUAL' WHERE source IS NULL")
    cur.execute("UPDATE jobs SET tracking_status = 'NEW' WHERE tracking_status IS NULL")
    cur.execute("UPDATE jobs SET times_seen = 1 WHERE times_seen IS NULL")
    cur.execute("UPDATE jobs SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    cur.execute("UPDATE jobs SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
    cur.execute("UPDATE jobs SET last_seen_at = CURRENT_TIMESTAMP WHERE last_seen_at IS NULL")

    cur.execute("SELECT id, company, title, description FROM jobs WHERE fingerprint IS NULL OR fingerprint = ''")
    for job_id, company, title, description in cur.fetchall():
        fingerprint = _build_job_fingerprint(company, title, description)
        cur.execute("UPDATE jobs SET fingerprint = ? WHERE id = ?", (fingerprint, job_id))

    cur.execute("CREATE INDEX IF NOT EXISTS ix_jobs_fingerprint ON jobs (fingerprint)")
    conn.commit()
    conn.close()
