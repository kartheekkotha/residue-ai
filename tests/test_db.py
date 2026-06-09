"""
tests/test_db.py
Unit tests for the database layer.
"""
import pytest
from pathlib import Path
import os

# Use a temp DB for tests — don't touch ~/.residue/tasks.db
os.environ["RESIDUE_TEST_MODE"] = "1"


def test_add_and_get_task(tmp_path, monkeypatch):
    """Adding a task and retrieving it should work."""
    # Patch DB path to tmp
    import residue.db.schema as schema
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(schema, "DB_DIR", tmp_path)

    from residue.db.queries import add_task, get_pending_tasks

    task_id = add_task("Check experiment results", "QML run from Tuesday", "high")
    assert isinstance(task_id, int)
    assert task_id > 0

    tasks = get_pending_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Check experiment results"
    assert tasks[0]["urgency"] == "high"


def test_complete_task(tmp_path, monkeypatch):
    import residue.db.schema as schema
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(schema, "DB_DIR", tmp_path)

    from residue.db.queries import add_task, complete_task, get_pending_tasks

    task_id = add_task("Deploy to prod")
    complete_task(task_id)

    tasks = get_pending_tasks()
    assert len(tasks) == 0


def test_snooze_task(tmp_path, monkeypatch):
    import residue.db.schema as schema
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(schema, "DB_DIR", tmp_path)

    from residue.db.queries import add_task, snooze_task, get_pending_tasks

    task_id = add_task("Check migration status")
    snooze_task(task_id, hours=4)

    # Should not appear in pending (snoozed into the future)
    tasks = get_pending_tasks()
    assert len(tasks) == 0


def test_invalid_urgency_defaults_to_medium(tmp_path, monkeypatch):
    import residue.db.schema as schema
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(schema, "DB_DIR", tmp_path)

    from residue.db.queries import add_task, get_pending_tasks

    add_task("Some task", urgency="INVALID")
    tasks = get_pending_tasks()
    assert tasks[0]["urgency"] == "medium"


def test_get_pending_capped_at_five(tmp_path, monkeypatch):
    import residue.db.schema as schema
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(schema, "DB_DIR", tmp_path)

    from residue.db.queries import add_task, get_pending_tasks

    for i in range(10):
        add_task(f"Task {i}")

    tasks = get_pending_tasks()
    assert len(tasks) <= 5
