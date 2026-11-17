"""
database.py - Tiny SQLite helper for the portal.

SQLite stores everything in ONE file (default: instance/portal.db).
Because the data lives in a file on disk, submissions survive an
application restart.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name        TEXT NOT NULL,
    registration_number TEXT NOT NULL,
    assignment_title    TEXT NOT NULL,
    submission_url      TEXT NOT NULL,
    submitted_at        TEXT NOT NULL      -- ISO-8601 timestamp in UTC
);
"""


@contextmanager
def connect(db_path):
    """Open a connection, commit on success, and ALWAYS close it.

    Closing matters on Windows: an open handle would lock the .db file.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path):
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def add_submission(db_path, data):
    """Insert one validated submission and return its new id."""
    submitted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO submissions "
            "(student_name, registration_number, assignment_title, submission_url, submitted_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                data["student_name"],
                data["registration_number"],
                data["assignment_title"],
                data["submission_url"],
                submitted_at,
            ),
        )
        return cur.lastrowid


def list_submissions(db_path):
    """Return all submissions, newest first."""
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM submissions ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def count_submissions(db_path):
    with connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
