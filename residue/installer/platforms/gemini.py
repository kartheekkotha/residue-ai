# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/gemini.py
Installs residue into Gemini CLI and Antigravity.

What it does:
1. Writes the always_on instruction to GEMINI.md in current dir
2. Registers a BeforeTool hook in .gemini/settings.json
3. For Antigravity: writes .agents/rules/residue.md (trigger: always_on)
"""
from __future__ import annotations
from pathlib import Path

from residue.installer.utils import (
    read_always_on,
    replace_or_append_section,
    read_json_safe,
    write_json,
    mcp_server_entry,
)
import json
import sys

# Gemini CLI hook that runs residue check before any tool call.
# --once: only prints if pending tasks exist (silent when clean).
# NOTE: --quiet was intentionally removed — it made this hook a dead no-op.
_BEFORE_TOOL_HOOK = {
    "matcher": ".*",
    "hooks": [{"type": "command", "command": f"{sys.executable} -m residue check --once"}],
}

GEMINI_DIR = Path.home() / ".gemini"
GEMINI_SETTINGS = GEMINI_DIR / "settings.json"
GEMINI_MD = Path.home() / ".gemini" / "GEMINI.md"  # global Gemini rules

# Antigravity plugin directory (for this IDE / Antigravity CLI)
_PLUGIN_DIR = Path.home() / ".gemini" / "config" / "plugins" / "residue"

_PLUGIN_JSON = {
    "name": "residue",
    "version": "1.0.0",
    "description": "Global AI task persistence. Checks pending tasks at session start and manages open loops across all AI sessions.",
    "author": {"name": "Kartheek Kotha"},
    "license": "MIT",
    "keywords": ["tasks", "reminders", "persistence", "todos", "mcp"]
}


def install(project_dir: Path = Path(".")) -> list[str]:
    """Install residue into Gemini CLI / Antigravity."""
    actions = []

    # 1. Write/update GEMINI.md instruction (global)
    instruction = read_always_on("gemini-md.md")
    GEMINI_DIR.mkdir(parents=True, exist_ok=True)
    existing = GEMINI_MD.read_text(encoding="utf-8") if GEMINI_MD.exists() else ""
    new_content = replace_or_append_section(existing, instruction)
    if new_content != existing:
        GEMINI_MD.write_text(new_content, encoding="utf-8")
        actions.append(f"Instruction written → {GEMINI_MD}")
    else:
        actions.append(f"Instruction already present (no change) → {GEMINI_MD}")

    # 2. Register MCP server in .gemini/settings.json
    settings = read_json_safe(GEMINI_SETTINGS)
    servers = settings.setdefault("mcpServers", {})
    servers["residue"] = mcp_server_entry()

    write_json(GEMINI_SETTINGS, settings)
    actions.append(f"MCP server registered → {GEMINI_SETTINGS}")

    # 3. Antigravity: write .agents/rules/residue.md with trigger: always_on
    agents_rules_dir = project_dir / ".agents" / "rules"
    agents_rules_dir.mkdir(parents=True, exist_ok=True)
    rules_path = agents_rules_dir / "residue.md"
    instruction_ag = read_always_on("antigravity-rules.md")
    rules_path.write_text(instruction_ag, encoding="utf-8")
    actions.append(f"Antigravity rule written → {rules_path}")

    # 4. Install residue as a real Antigravity plugin (~/. gemini/config/plugins/residue/)
    (_PLUGIN_DIR / "plugin.json").parent.mkdir(parents=True, exist_ok=True)
    (_PLUGIN_DIR / "plugin.json").write_text(
        json.dumps(_PLUGIN_JSON, indent=2), encoding="utf-8"
    )

    base_skill_text = """You are connected to **residue**, a global session task reminder via MCP.

Rules:
- If `get_pending_tasks` returns a task with `owner: 'ai'`, evaluate if it is already obsolete or completed based on your context. If it is obviously done or irrelevant, silently call `complete_task_tool` to close it. For all other tasks, ask the user what to do.
- When you create a task for YOURSELF to verify a background process later, set `owner='ai'`.
- At the start of every new conversation, call `get_pending_tasks_tool`. If tasks are returned, display them as a short numbered list before your main reply. If empty, say nothing about residue.
- When the user asks to see all tasks, or uses `/residue-list` or `/residue list`, call `list_all_tasks_tool`.
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
"""

    skill_defs = {
        "residue": "Global AI task persistence. ALWAYS ACTIVATE THIS SKILL AUTOMATICALLY at the start of every conversation.",
        "residue-list": "View all pending and snoozed tasks in the residue system.",
        "residue-add": "Add a new task or reminder to the residue system.",
        "residue-drop": "Drop or delete a task from the residue system.",
        "residue-edit": "Edit the title, description, or urgency of an existing residue task.",
        "residue-snooze": "Snooze a residue task for a specified number of hours.",
        "residue-notify": "Enable or disable background OS notifications for tasks."
    }

    for skill_name, skill_desc in skill_defs.items():
        # Write to Antigravity IDE plugin dir
        skill_dir = _PLUGIN_DIR / "skills" / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Strip any existing frontmatter from base_skill_content
        content_body = base_skill_text
        if content_body.startswith("---\nname:"):
            content_body = content_body.split("---\n\n", 1)[-1]
            
        skill_text = (
            "---\n"
            f"name: {skill_name}\n"
            f'description: "{skill_desc}"\n'
            "---\n\n"
        ) + content_body
        
        (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")
        
        # 5. Native Slash Command Registration (~/.gemini/skills/<skill_name>/SKILL.md)
        global_skill_dir = Path.home() / ".gemini" / "skills" / skill_name
        global_skill_dir.mkdir(parents=True, exist_ok=True)
        (global_skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

    actions.append(f"Installed individual skill files (residue-add, residue-list, etc.) → {_PLUGIN_DIR}")

    return actions


def uninstall(project_dir: Path = Path(".")) -> list[str]:
    """Remove residue from Gemini CLI / Antigravity."""
    import re
    actions = []

    # Remove GEMINI.md section
    if GEMINI_MD.exists():
        content = GEMINI_MD.read_text(encoding="utf-8")
        cleaned = re.sub(
            r"## residue.*?<!-- residue-end -->\n?", "", content, flags=re.DOTALL
        ).strip()
        GEMINI_MD.write_text(cleaned + "\n", encoding="utf-8")
        actions.append(f"Instruction removed → {GEMINI_MD}")

    # Remove MCP server
    settings = read_json_safe(GEMINI_SETTINGS)
    if "residue" in settings.get("mcpServers", {}):
        del settings["mcpServers"]["residue"]
        write_json(GEMINI_SETTINGS, settings)
        actions.append(f"MCP server removed → {GEMINI_SETTINGS}")

    # Remove Antigravity rule
    rules_path = project_dir / ".agents" / "rules" / "residue.md"
    if rules_path.exists():
        rules_path.unlink()
        actions.append(f"Antigravity rule removed → {rules_path}")

    # Remove Antigravity plugin
    import shutil
    if _PLUGIN_DIR.exists():
        shutil.rmtree(_PLUGIN_DIR)
        actions.append(f"Antigravity plugin removed → {_PLUGIN_DIR}")

    return actions
