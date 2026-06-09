# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/detector.py
Detects which AI tools are installed on this machine.
"""
from __future__ import annotations
from pathlib import Path


def detect() -> list[str]:
    """
    Return list of detected AI tool names.
    Checks known config/binary locations — no subprocess needed.
    """
    found = []

    # Claude Code — has ~/.claude directory
    if (Path.home() / ".claude").exists():
        found.append("claude")

    # Cursor — has ~/.cursor directory
    if (Path.home() / ".cursor").exists():
        found.append("cursor")

    # Gemini CLI / Antigravity — has ~/.gemini directory
    if (Path.home() / ".gemini").exists():
        found.append("gemini")

    # VS Code Copilot — check for .github/copilot-instructions.md or vscode settings
    if (Path.home() / ".vscode").exists():
        found.append("vscode")

    return found
