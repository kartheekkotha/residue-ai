# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/db/queries.py
All database read/write operations for tasks.
"""
from __future__ import annotations
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

from .schema import get_connection

VALID_URGENCY = {"low", "medium", "high"}
VALID_STATUS = {"pending", "snoozed", "done", "rejected"}


def add_task(title: str, description: str = "", urgency: str = "medium", source_tool: str = "unknown", delay_hours: int = 0, owner: str = "user", workspace: str = "", metadata: str = "{}") -> int:
    """
    Insert a new pending task. Returns the new task ID.
    Called by the AI when it detects an open loop.
    If delay_hours > 0, the task is created as snoozed.
    """
    urgency = urgency if urgency in VALID_URGENCY else "medium"
    status = "snoozed" if delay_hours > 0 else "pending"
    snooze_until = None
    if delay_hours > 0:
        snooze_until = (datetime.now(timezone.utc) + timedelta(hours=delay_hours)).isoformat()
        
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, description, urgency, source_tool, status, snooze_until, owner, workspace, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title.strip(), description.strip(), urgency, source_tool, status, snooze_until, owner, workspace, metadata),
        )
        conn.commit()
        return cur.lastrowid


def get_pending_tasks() -> list[dict]:
    """
    Return all tasks that are currently active (pending or snooze expired).
    Called by the AI at the start of every session.
    Capped at 5 to keep token usage minimal.
    """
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, description, urgency, source_tool, created_at, owner, workspace, metadata
            FROM tasks
            WHERE status = 'pending'
               OR (status = 'snoozed' AND snooze_until <= ?)
            ORDER BY
                CASE urgency WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                created_at ASC
            LIMIT 5
            """,
            (now,),
        ).fetchall()
    return [dict(r) for r in rows]


def complete_task(task_id: int) -> bool:
    """
    Mark a task as done. Returns True if a row was updated.
    Called by the AI when the user confirms something is finished.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE tasks SET status = 'done', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def reject_task(task_id: int) -> bool:
    """
    Mark a task as rejected. Returns True if a row was updated.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE tasks SET status = 'rejected', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def delete_task(task_id: int) -> bool:
    """
    Physically delete a task from the database.
    """
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cur.rowcount > 0


def edit_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None, urgency: Optional[str] = None) -> bool:
    """
    Edit task fields.
    """
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title.strip())
    if description is not None:
        updates.append("description = ?")
        params.append(description.strip())
    if urgency is not None and urgency in VALID_URGENCY:
        updates.append("urgency = ?")
        params.append(urgency)

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(task_id)

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"

    with get_connection() as conn:
        cur = conn.execute(query, tuple(params))
        conn.commit()
        return cur.rowcount > 0


def snooze_task(task_id: int, hours: int = 2) -> bool:
    """
    Snooze a task for N hours. Returns True if a row was updated.
    Called by the AI when the user says 'not now' or 'remind me later'.
    """
    hours = max(1, min(hours, 168))  # clamp: 1h to 1 week
    snooze_until = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            UPDATE tasks
            SET status = 'snoozed', snooze_until = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (snooze_until, task_id),
        )
        conn.commit()
        return cur.rowcount > 0


def get_all_tasks() -> list[dict]:
    """Return all tasks for CLI display."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def clear_done_tasks() -> int:
    """Remove all done/snoozed/rejected tasks. Returns count deleted."""
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM tasks WHERE status IN ('done', 'snoozed', 'rejected')"
        )
        conn.commit()
        return cur.rowcount


def reset_tasks() -> int:
    """Completely wipe all tasks from the database (truncate). Returns count deleted."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks")
        # Optional: reset autoincrement
        conn.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        conn.commit()
        return cur.rowcount
