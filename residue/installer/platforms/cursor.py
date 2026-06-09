# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/cursor.py
Installs residue into Cursor.

What it does:
1. Registers MCP server in ~/.cursor/mcp.json
2. Writes instruction rule to ~/.cursor/rules/residue.mdc
"""
from __future__ import annotations
from pathlib import Path

from residue.installer.utils import (
    read_always_on,
    read_json_safe,
    write_json,
    mcp_server_entry,
)

import sys
import os

CURSOR_DIR = Path.home() / ".cursor"

CURSOR_MCP = CURSOR_DIR / "mcp.json"
CURSOR_RULES_DIR = CURSOR_DIR / "rules"


def install() -> list[str]:
    """Install residue into Cursor."""
    actions = []

    # 1. Register MCP server in ~/.cursor/mcp.json
    # Always overwrite the entry so stale paths (e.g. old venv from another Mac) get corrected on re-install.
    config = read_json_safe(CURSOR_MCP)
    servers = config.setdefault("mcpServers", {})
    new_entry = mcp_server_entry()
    if servers.get("residue") != new_entry:
        servers["residue"] = new_entry
        write_json(CURSOR_MCP, config)
        actions.append(f"MCP server registered/updated → {CURSOR_MCP}")
    else:
        actions.append(f"MCP server already up-to-date (no change) → {CURSOR_MCP}")

    # 2. Write instruction rule as .mdc (Cursor's native rule format)
    CURSOR_RULES_DIR.mkdir(parents=True, exist_ok=True)
    rule_path = CURSOR_RULES_DIR / "residue.mdc"
    instruction = read_always_on("claude-md.md")  # same instruction works for Cursor
    # Cursor MDC format: wrap in frontmatter
    mdc_content = f"---\nalwaysApply: true\n---\n\n{instruction.strip()}\n"
    rule_path.write_text(mdc_content, encoding="utf-8")
    actions.append(f"Rule file written → {rule_path}")

    return actions


def uninstall() -> list[str]:
    """Remove residue from Cursor."""
    actions = []

    # Remove MCP entry
    config = read_json_safe(CURSOR_MCP)
    if "residue" in config.get("mcpServers", {}):
        del config["mcpServers"]["residue"]
        write_json(CURSOR_MCP, config)
        actions.append(f"MCP server removed → {CURSOR_MCP}")

    # Remove rule file
    rule_path = CURSOR_RULES_DIR / "residue.mdc"
    if rule_path.exists():
        rule_path.unlink()
        actions.append(f"Rule file removed → {rule_path}")

    return actions
