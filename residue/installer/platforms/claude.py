# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/claude.py
Installs residue into Claude Code (CLI) and Claude Desktop.

What it does:
1. Writes MCP server config to ~/.claude.json (Claude Code CLI)
2. Writes MCP server config to the platform-specific Claude Desktop config
3. Appends the always_on instruction block to ~/.claude/CLAUDE.md
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

import sys
import os

# Claude Code CLI uses ~/.claude.json for MCP server configs
CLAUDE_CODE_CONFIG = Path.home() / ".claude.json"

# Claude Code instructions/skills directory
CLAUDE_DIR = Path.home() / ".claude"
CLAUDE_MD = CLAUDE_DIR / "CLAUDE.md"

# Claude Desktop uses a platform-specific config file
if sys.platform == "win32":
    CLAUDE_DESKTOP_CONFIG = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))) / "Claude" / "claude_desktop_config.json"
elif sys.platform == "darwin":
    CLAUDE_DESKTOP_CONFIG = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
else:
    CLAUDE_DESKTOP_CONFIG = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def install() -> list[str]:
    """Install residue into Claude Code. Returns list of actions taken."""
    actions = []

    # 1. Register MCP server in Claude Code CLI config (~/.claude.json)
    #    and Claude Desktop config (platform-specific path).
    # Always overwrite the entry so stale paths (e.g. old venv) get corrected on re-install.
    for config_file in [CLAUDE_CODE_CONFIG, CLAUDE_DESKTOP_CONFIG]:
        config = read_json_safe(config_file)
        servers = config.setdefault("mcpServers", {})
        new_entry = mcp_server_entry()
        if servers.get("residue") != new_entry:
            servers["residue"] = new_entry
            write_json(config_file, config)
            actions.append(f"MCP server registered/updated → {config_file}")
        else:
            actions.append(f"MCP server already up-to-date → {config_file}")

    # 2. Inject always_on instruction into CLAUDE.md
    instruction = read_always_on("claude-md.md")
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    existing = CLAUDE_MD.read_text(encoding="utf-8") if CLAUDE_MD.exists() else ""
    new_content = replace_or_append_section(existing, instruction)
    if new_content != existing:
        CLAUDE_MD.write_text(new_content, encoding="utf-8")
        actions.append(f"Instruction injected → {CLAUDE_MD}")
    else:
        actions.append(f"Instruction already present (no change) → {CLAUDE_MD}")

    # 3. Install individual skill files to ~/.claude/skills/
    skill_defs = {
        "residue": "Global AI task persistence. ALWAYS ACTIVATE THIS SKILL AUTOMATICALLY at the start of every conversation.",
        "residue-list": "View all pending and snoozed tasks in the residue system.",
        "residue-add": "Add a new task or reminder to the residue system.",
        "residue-drop": "Drop or delete a task from the residue system.",
        "residue-edit": "Edit the title, description, or urgency of an existing residue task.",
        "residue-snooze": "Snooze a residue task for a specified number of hours.",
        "residue-notify": "Enable or disable background OS notifications for tasks."
    }

    base_skill_text = """You are connected to **residue**, a global session task reminder via MCP.

**CRITICAL**: Tasks are GLOBAL across ALL tools and ALL workspaces. ALWAYS show all returned tasks regardless of which project or directory is currently open. Never filter or skip tasks based on workspace.

Rules:
- At the start of every new conversation, call `get_pending_tasks_tool`. Show ALL returned tasks as a numbered list before your main reply — regardless of their workspace of origin. If empty, say nothing about residue.
- When the user asks to see all tasks, or uses `/residue list` or `/residue-list`, call `list_all_tasks_tool`.
- When the user defers something ("I'll check later", "remind me", "let's come back"), silently call `add_task_tool`. Do NOT announce it.
- When the user confirms a deferred task is done, call `complete_task_tool`.
- When the user says "not now", call `snooze_task_tool`.
- When the user says "edit task", call `edit_task_tool`.
- When the user says "drop task" or "delete task", call `delete_task_tool`.
- When the user wants to enable or disable background OS notifications, call `set_notifications_tool`.

### Slash Commands
You must immediately execute the corresponding tool if the user uses these slash commands:
- `/residue list`: Call `list_all_tasks_tool`
- `/residue add <task>`: Call `add_task_tool`
- `/residue drop <id>`: Call `reject_task_tool` or `delete_task_tool`
- `/residue edit <id>`: Call `edit_task_tool`
- `/residue notify [on|off]`: Call `set_notifications_tool`
"""

    for skill_name, skill_desc in skill_defs.items():
        skill_dst = CLAUDE_DIR / "skills" / skill_name / "SKILL.md"
        skill_dst.parent.mkdir(parents=True, exist_ok=True)
        
        skill_text = (
            "---\n"
            f"name: {skill_name}\n"
            f'description: "{skill_desc}"\n'
            "---\n\n"
            f"# /{skill_name}\n\n"
        ) + base_skill_text
        
        skill_dst.write_text(skill_text, encoding="utf-8")

    actions.append(f"Installed individual Claude skill files (residue-add, residue-list, etc.)")

    return actions


def uninstall() -> list[str]:
    """Remove residue from Claude Code."""
    import re
    actions = []

    # Remove MCP entry from both Claude Code CLI and Desktop configs
    for config_file in [CLAUDE_CODE_CONFIG, CLAUDE_DESKTOP_CONFIG]:
        config = read_json_safe(config_file)
        if "residue" in config.get("mcpServers", {}):
            del config["mcpServers"]["residue"]
            write_json(config_file, config)
            actions.append(f"MCP server removed → {config_file}")

    # Remove instruction block from CLAUDE.md
    if CLAUDE_MD.exists():
        content = CLAUDE_MD.read_text(encoding="utf-8")
        cleaned = re.sub(
            r"## residue.*?<!-- residue-end -->\n?", "", content, flags=re.DOTALL
        ).strip()
        CLAUDE_MD.write_text(cleaned + "\n", encoding="utf-8")
        actions.append(f"Instruction removed → {CLAUDE_MD}")

    return actions
