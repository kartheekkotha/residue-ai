# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/codex.py
Installs residue into OpenAI Codex CLI.

What it does:
1. Writes skill markdown files to ~/.codex/skills/
2. Registers the residue MCP server in ~/.codex/config.toml
   (TOML format, required by Codex CLI — JSON is silently ignored)
"""

from pathlib import Path
from residue.installer.utils import mcp_server_entry, read_always_on

CODEX_DIR = Path.home() / ".codex"
CODEX_CONFIG = CODEX_DIR / "config.toml"


def _read_toml_safe(path: Path) -> str:
    """Read a TOML file as raw text, return empty string if missing."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _inject_mcp_toml(content: str, entry: dict) -> str:
    """
    Idempotently inject the [mcp_servers.residue] block into TOML content.
    Strategy: parse with tomllib → mutate in-memory → write back via tomli_w.
    Falls back to safe raw-text surgery if neither lib is available.
    """
    # Try the proper parse-and-rewrite path first
    try:
        import sys
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            try:
                import tomllib  # type: ignore
            except ImportError:
                import tomli as tomllib  # type: ignore

        try:
            import tomli_w
        except ImportError:
            tomli_w = None

        data = tomllib.loads(content) if content.strip() else {}
        data.setdefault("mcp_servers", {})["residue"] = entry

        if tomli_w is not None:
            return tomli_w.dumps(data)
    except Exception:
        pass  # fall through to raw-text approach

    # Raw-text fallback: nuke ALL residue-related lines, then append a clean block.
    import re
    # Remove any [mcp_servers.residue] section and its body
    cleaned = re.sub(
        r"^\[mcp_servers\.residue(?:\.[^\]]*)?\][^\[]*",
        "",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    # Remove any orphaned stray lines that look like our args array (e.g. ["-m", "residue", ...])
    cleaned = re.sub(
        r'^\["-m".*\]\s*$',
        "",
        cleaned,
        flags=re.MULTILINE,
    )
    cleaned = cleaned.strip()
    return cleaned + "\n\n" + _build_mcp_block(entry) + "\n"


def _build_mcp_block(entry: dict) -> str:
    """Build a valid TOML block for the residue MCP server."""
    lines = ["[mcp_servers.residue]"]
    lines.append(f'command = "{entry["command"]}"')
    args = entry.get("args", [])
    if args:
        # Inline TOML array — must stay on ONE line or TOML parser chokes
        args_toml = ", ".join(f'"{a}"' for a in args)
        lines.append(f"args = [{args_toml}]")
    env = entry.get("env") or {}
    if env:
        env_parts = ", ".join(f'{k} = "{v}"' for k, v in env.items())
        lines.append(f"env = {{{env_parts}}}")
    return "\n".join(lines)


def install() -> list[str]:
    """Install residue into Codex CLI."""
    actions = []

    # 1. Write skill markdown files
    skill_defs = {
        "residue": "Global AI task persistence. ALWAYS ACTIVATE THIS SKILL AUTOMATICALLY at the start of every conversation.",
        "residue-list": "View all pending and snoozed tasks in the residue system.",
        "residue-add": "Add a new task or reminder to the residue system.",
        "residue-drop": "Drop or delete a task from the residue system.",
        "residue-edit": "Edit the title, description, or urgency of an existing residue task.",
        "residue-snooze": "Snooze a residue task for a specified number of hours.",
        "residue-notify": "Enable or disable background OS notifications for tasks.",
    }

    # Read instruction from always_on file (single source of truth, like all other platforms)
    base_skill_text = read_always_on("codex-md.md")
    # Strip YAML frontmatter if present (the always_on files may have it)
    if base_skill_text.startswith("---"):
        parts = base_skill_text.split("---", 2)
        base_skill_text = parts[2].lstrip("\n") if len(parts) >= 3 else base_skill_text

    for skill_name, skill_desc in skill_defs.items():
        skill_dst = CODEX_DIR / "skills" / skill_name / "SKILL.md"
        skill_dst.parent.mkdir(parents=True, exist_ok=True)

        skill_text = (
            "---\n"
            f"name: {skill_name}\n"
            f'description: "{skill_desc}"\n'
            "---\n\n"
            f"# /{skill_name}\n\n"
        ) + base_skill_text

        skill_dst.write_text(skill_text, encoding="utf-8")

    actions.append("Installed Codex skill files (residue, residue-add, residue-list, etc.)")

    # 2. Register MCP server in ~/.codex/config.toml (TOML format — JSON is silently ignored by Codex)
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    entry = mcp_server_entry()
    existing = _read_toml_safe(CODEX_CONFIG)
    updated = _inject_mcp_toml(existing, entry)
    CODEX_CONFIG.write_text(updated, encoding="utf-8")
    actions.append(f"MCP server registered → {CODEX_CONFIG}")

    return actions


def uninstall() -> list[str]:
    """Remove residue from Codex CLI."""
    import re
    actions = []

    # Remove skill files
    skills = ["residue", "residue-list", "residue-add", "residue-drop", "residue-edit", "residue-snooze"]
    for skill_name in skills:
        skill_dst = CODEX_DIR / "skills" / skill_name / "SKILL.md"
        if skill_dst.exists():
            skill_dst.unlink()
            try:
                skill_dst.parent.rmdir()
            except OSError:
                pass
            actions.append(f"Removed Codex skill {skill_name}")

    # Remove MCP server block from config.toml
    if CODEX_CONFIG.exists():
        content = CODEX_CONFIG.read_text(encoding="utf-8")
        cleaned = re.sub(
            r"\[mcp_servers\.residue\].*?(?=\[|\Z)",
            "",
            content,
            flags=re.DOTALL,
        ).strip()
        CODEX_CONFIG.write_text(cleaned + "\n", encoding="utf-8")
        actions.append(f"MCP server entry removed → {CODEX_CONFIG}")

    return actions or ["Codex residue config not found"]
