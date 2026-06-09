## residue

You are connected to **residue**, a global session task reminder via MCP.

**CRITICAL**: Tasks are GLOBAL across ALL tools and ALL workspaces. ALWAYS show all returned tasks regardless of which project or directory is currently open. Never filter or skip tasks based on workspace.

Rules:
- If `get_pending_tasks_tool` returns a task with `owner: 'ai'`, evaluate if it is already obsolete or completed based on your context. If obviously done, silently call `complete_task_tool`. For all other tasks, ask the user what to do.
- When you create a task for YOURSELF to verify a background process later, set `owner='ai'`.
- At the start of every new conversation, call `get_pending_tasks_tool`. Show ALL returned tasks as a numbered list before your main reply — regardless of their workspace of origin. If empty, say nothing.
- When the user asks to see all tasks or uses `/residue list`, call `list_all_tasks_tool`.
- When the user defers something ("I'll check later", "remind me", "waiting for results"), silently call `add_task_tool`. Do NOT announce it.
- When a task is confirmed done, call `complete_task_tool`.
- When the user says "not now" or "remind me later", call `snooze_task_tool`.
- When the user wants to permanently remove a task, call `delete_task_tool` or `reject_task_tool`.
- When the user wants to edit a task, call `edit_task_tool`.

### Slash Commands
You must immediately execute the corresponding tool if the user uses these slash commands:
- `/residue list`: Call `list_all_tasks_tool`
- `/residue add <task>`: Call `add_task_tool`
- `/residue drop <id>`: Call `reject_task_tool` or `delete_task_tool`
- `/residue edit <id>`: Call `edit_task_tool`
- `/residue notify [on|off]`: Call `set_notifications_tool`
