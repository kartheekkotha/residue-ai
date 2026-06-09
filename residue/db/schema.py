# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/db/schema.py
Sets up the SQLite database at ~/.residue/tasks.db
"""
import sqlite3
from pathlib import Path

DB_DIR = Path.home() / ".residue"
DB_PATH = DB_DIR / "tasks.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER  PRIMARY KEY AUTOINCREMENT,
    title        TEXT     NOT NULL,
    description  TEXT     DEFAULT '',
    urgency      TEXT     DEFAULT 'medium' CHECK(urgency IN ('low', 'medium', 'high')),
    status       TEXT     DEFAULT 'pending' CHECK(status IN ('pending', 'done', 'snoozed', 'rejected')),
    snooze_until DATETIME,
    source_tool  TEXT     DEFAULT 'unknown',
    owner        TEXT     DEFAULT 'user' CHECK(owner IN ('user', 'ai')),
    workspace    TEXT     DEFAULT '',
    metadata     TEXT     DEFAULT '{}',
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS tasks_updated_at
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);",
    "CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner);"
]

def get_connection() -> sqlite3.Connection:
    """Return a connection to the global residue database."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    # WAL mode: safe for concurrent reads from multiple open AI tools
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(CREATE_TABLE)
    conn.execute(CREATE_TRIGGER)
    for idx in CREATE_INDEXES:
        conn.execute(idx)
        
    conn.commit()
    return conn
