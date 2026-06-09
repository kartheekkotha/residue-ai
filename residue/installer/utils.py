# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/utils.py
Shared utilities for all platform installers.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

# Marker used to find/replace residue sections in shared config files
_SECTION_MARKER = "## residue"
_SECTION_END = "<!-- residue-end -->"


def read_always_on(filename: str) -> str:
    """Read a packaged always_on instruction file from residue/always_on/."""
    path = Path(__file__).parent.parent / "always_on" / filename
    if not path.exists():
        raise FileNotFoundError(f"always_on file not found: {path}")
    return path.read_text(encoding="utf-8")


def replace_or_append_section(content: str, new_section: str) -> str:
    """
    Idempotently update or append a residue-owned section in a config file.
    - If the marker exists: replace the block between marker and end-marker.
    - If not: append the new section to the end.
    Running this twice on the same file produces no duplicates.
    """
    wrapped = f"{new_section.strip()}\n{_SECTION_END}\n"
    if _SECTION_MARKER in content:
        # Replace existing section
        updated = re.sub(
            rf"{re.escape(_SECTION_MARKER)}.*?{re.escape(_SECTION_END)}\n?",
            wrapped,
            content,
            flags=re.DOTALL,
        )
        return updated
    # Append new section
    return content.rstrip() + "\n\n" + wrapped


def read_json_safe(path: Path) -> dict:
    """Read a JSON file, return {} on missing or corrupt."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: dict) -> None:
    """Write data as pretty JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def mcp_server_entry() -> dict:
    """Standard MCP server entry for residue.

    Prefers the installed `residue` CLI script (e.g. from pipx or pip)
    so the path is portable across machines. Falls back to
    `sys.executable -m residue serve` only when the CLI is not on PATH.
    """
    import shutil
    import sys

    residue_bin = shutil.which("residue")
    if residue_bin:
        return {
            "command": residue_bin,
            "args": ["serve"],
            "env": {},
        }

    # Fallback: use the current Python interpreter (may be a venv path)
    return {
        "command": sys.executable,
        "args": ["-m", "residue", "serve"],
        "env": {},
    }
