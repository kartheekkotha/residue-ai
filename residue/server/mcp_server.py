# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/server/mcp_server.py
The MCP server — exposes tools to AI models.
Run via: residue serve
"""
from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP

from residue.db.queries import (
    add_task,
    get_pending_tasks,
    complete_task,
    snooze_task,
    reject_task,
    edit_task,
    delete_task,
)

mcp = FastMCP("residue")


@mcp.tool()
def get_pending_tasks_tool() -> str:
    """
    Get all pending tasks. Tasks are GLOBAL across ALL tools and workspaces — not scoped to the current project.
    IMPORTANT: Call this at the START of every new conversation before responding, regardless of which workspace or project is open.
    Show ALL returned tasks to the user — do NOT filter or skip tasks based on their workspace field.
    Returns a compact JSON list of pending tasks (max 5), sorted by urgency.
    If the list is empty, do not mention residue at all.
    """
    tasks = get_pending_tasks()
    if not tasks:
        return json.dumps({"pending": [], "count": 0})
    # NOTE: workspace is intentionally excluded from the compact response.
    # Tasks are GLOBAL — the AI must show them regardless of the current working directory.
    compact = [
        {"id": t["id"], "title": t["title"], "urgency": t["urgency"], "owner": t["owner"]}
        for t in tasks
    ]
    return json.dumps({"pending": compact, "count": len(compact)})


@mcp.tool()
def list_all_tasks_tool() -> str:
    """
    Get all tasks, including both pending and snoozed tasks. Tasks are GLOBAL across all tools and workspaces.
    Call this when the user explicitly asks to view all tasks or uses /residue list.
    """
    from residue.db.queries import get_all_tasks
    tasks = get_all_tasks()
    # Filter to only pending and snoozed
    active = [t for t in tasks if t["status"] in ("pending", "snoozed")]
    compact = [
        {
            "id": t["id"],
            "title": t["title"],
            "status": t["status"],
            "urgency": t["urgency"],
            "snooze_until": t["snooze_until"],
            "owner": t["owner"],
            "workspace": t["workspace"],   # included here for user reference only
        }
        for t in active
    ]
    return json.dumps({"tasks": compact, "count": len(compact)})


@mcp.tool()
def add_task_tool(title: str, description: str = "", urgency: str = "medium", delay_hours: int = 0, owner: str = "user", workspace: str = "") -> str:
    """
    Save an open loop as a pending task. The task is stored GLOBALLY and will be visible in ALL tools and workspaces.
    Call this SILENTLY when the user defers something:
    - "I'll check this later"
    - "remind me about X"
    - "let's come back to this"
    - "running a build / waiting for results"
    Do NOT announce to the user that you are saving a task unless they ask.
    urgency must be one of: low, medium, high
    delay_hours: Number of hours to wait before reminding the user. Default 0 means remind next session.
    owner: Set to 'ai' if you are creating this task for YOURSELF to verify or check something later (like a background build). Leave as 'user' if the user deferred it.
    workspace: The current project path — stored as origin metadata only, NOT used to filter task visibility.
    """
    import os
    if not workspace:
        workspace = os.getcwd()
    task_id = add_task(title=title, description=description, urgency=urgency, delay_hours=delay_hours, owner=owner, workspace=workspace)
    return json.dumps({"saved": True, "id": task_id, "title": title, "owner": owner})


@mcp.tool()
def complete_task_tool(task_id: int) -> str:
    """
    Mark a task as complete.
    Call this when the user confirms a previously deferred action is done.
    """
    ok = complete_task(task_id)
    return json.dumps({"completed": ok, "id": task_id})


@mcp.tool()
def snooze_task_tool(task_id: int, hours: int = 2) -> str:
    """
    Snooze a task for N hours (default 2).
    Call this when the user says 'not now', 'later', or 'remind me in X hours'.
    """
    ok = snooze_task(task_id, hours)
    return json.dumps({"snoozed": ok, "id": task_id, "hours": hours})


@mcp.tool()
def reject_task_tool(task_id: int) -> str:
    """
    Reject or drop a task completely.
    Call this when the user indicates they no longer want to do the task or it's no longer relevant.
    """
    ok = reject_task(task_id)
    return json.dumps({"rejected": ok, "id": task_id})


@mcp.tool()
def edit_task_tool(task_id: int, title: str = None, description: str = None, urgency: str = None) -> str:
    """
    Edit an existing task's title, description, or urgency.
    """
    ok = edit_task(task_id, title=title, description=description, urgency=urgency)
    return json.dumps({"edited": ok, "id": task_id})


@mcp.tool()
def delete_task_tool(task_id: int) -> str:
    """
    Permanently delete a task from the database.
    """
    ok = delete_task(task_id)
    return json.dumps({"deleted": ok, "id": task_id})


@mcp.tool()
def set_notifications_tool(enabled: bool) -> str:
    """
    Enable or disable background OS notifications for pending tasks.
    Call this when the user asks to turn notifications on or off (e.g. /residue-notify on, /residue notify off).
    """
    import sys
    is_windows = sys.platform == "win32"
    if is_windows:
        from residue.installer.platforms import windows as os_installer
    else:
        from residue.installer.platforms import macos as os_installer

    try:
        if enabled:
            actions = os_installer.install()
            return json.dumps({"notifications": "on", "actions": actions})
        else:
            actions = os_installer.uninstall()
            return json.dumps({"notifications": "off", "actions": actions})
    except Exception as e:
        return json.dumps({"error": str(e)})


def run():
    """Entry point for the MCP server process."""
    mcp.run()
