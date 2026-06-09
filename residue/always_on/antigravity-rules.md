---
trigger: always_on
description: Check for pending residue tasks at the start of every session.
---

## residue

You are connected to **residue**, a global session task reminder via MCP.

Rules:
- If `get_pending_tasks` returns a task with `owner: 'ai'`, evaluate if it is already obsolete or completed based on your context. If it is obviously done or irrelevant, silently call `complete_task_tool` to close it. For all other tasks, ask the user what to do.
- When you create a task for YOURSELF to verify a background process later, set `owner='ai'`.
- At the start of every new conversation, call `get_pending_tasks_tool`. If tasks are returned, display them as a short numbered list before your main reply. If empty, say nothing about residue.
- When the user defers or pauses something ("I'll check later", "remind me", "let's come back to this", "waiting for results", "running a build"), silently call `add_task_tool`. Do NOT announce it.
- When the user confirms a deferred task is done, call `complete_task_tool`.
- When the user says "not now" or "remind me later", call `snooze_task_tool`.
- When the user wants to permanently remove a task without doing it, call `delete_task_tool` or `reject_task_tool`.
- When the user wants to change a task's title, description, or urgency, call `edit_task_tool`.

### Slash Commands
You must immediately execute the corresponding tool if the user uses these slash commands:
- `/residue list`: Call `list_all_tasks_tool`
- `/residue add <task>`: Call `add_task_tool`
- `/residue drop <id>`: Call `reject_task_tool` or `delete_task_tool`
- `/residue edit <id>`: Call `edit_task_tool`
- `/residue notify [on|off]`: Call `set_notifications_tool`
