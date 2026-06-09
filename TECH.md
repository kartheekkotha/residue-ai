# ⚙️ Residue Technical Architecture

This document explains how `residue` is implemented under the hood. It is intended for software engineers contributing to the project or looking to understand how to build cross-platform AI plugins.

## 1. Core Data Layer
All tasks are stored in a local SQLite database at `~/.residue/tasks.db`. 
- **Schema:** Contains a single `tasks` table with columns `id`, `title`, `description`, `status` (pending, completed, snoozed, rejected), `urgency`, `source_tool`, `owner` (user or ai), `created_at`, `updated_at`, and `snooze_until`.
- **Interface:** `residue/db/queries.py` uses raw SQL (via Python's built-in `sqlite3` module) to manage CRUD operations.

## 2. Model Context Protocol (MCP) Server
The core mechanism that allows AIs to interact with the database is an MCP server.
- **Implementation:** Built using the official `mcp` Python SDK package.
- **Transport:** Runs over standard input/output (stdio) using JSON-RPC.
- **Autonomous AI Logic:** The `add_task_tool` accepts an `owner` property. If the user defers a task, `owner="user"`. If the AI defers a task for itself (like verifying a background process), `owner="ai"`. When the AI boots up and calls `get_pending_tasks_tool`, it uses its LLM reasoning to quietly close out any `owner="ai"` tasks that it realizes are already obsolete, enabling seamless contextual auto-resolution without bothering the user.
- **Tools Exposed:**
  - `get_pending_tasks_tool`
  - `add_task_tool`
  - `complete_task_tool`
  - `snooze_task_tool`
  - `reject_task_tool`
  - `delete_task_tool`
  - `edit_task_tool`

When an AI wants to modify your tasks, it makes a tool call to this local Python MCP server process.

## 3. Platform Integrations (The Installer)
The magic of `residue` is that it injects itself into every AI tool automatically. This is handled by `residue install` which runs scripts in `residue/installer/platforms/`.

### 3.1 Claude Code & Codex
*Codex is a fork of Claude Code, so their plugin architectures are identical.*
- **MCP Registration:** Appends the `residue serve` command to `~/.claude/claude_desktop_config.json` (or `~/.codex/...`).
- **Implicit Memory:** Appends a prompt block to `~/.claude/CLAUDE.md`. This prompt instructs the AI to call `get_pending_tasks` at the start of every session.
- **Slash Commands:** Generates individual Markdown files (e.g., `~/.claude/skills/residue-list/SKILL.md`). These files contain YAML frontmatter and a `# /residue-list` header which the Claude/Codex CLI parses to populate its interactive UI autocomplete dropdown menu.

### 3.2 Gemini CLI & Antigravity IDE
- **Hooks:** Modifies `~/.gemini/settings.json` to add a `BeforeTool` hook (`residue check`). This forces the CLI to print pending tasks to the terminal right before the AI takes its first action.
- **MCP Registration:** Adds the MCP server directly into `~/.gemini/settings.json`.
- **System Prompts:** Appends memory rules to `~/.gemini/GEMINI.md` and generates `.agents/rules/residue.md`.
- **IDE Slash Commands:** Creates specific skill definitions inside `~/.gemini/config/plugins/residue/skills/`. The Antigravity IDE natively maps these to `/` commands in its chat interface.

### 3.3 Cursor
- **MCP Registration:** Modifies `.cursor/mcp.json` to register the local Python MCP server.
- **System Prompts:** Generates a `.cursor/rules/residue.mdc` (Cursor Rules file) which instructs the Cursor Composer to manage open loops silently via the MCP tools.

## 4. macOS Push Notifications
Residue includes an opt-in background daemon to remind you of tasks even when your terminal is closed.
- **Installation (`residue notify --on`):** Generates an XML property list (`.plist`) file and saves it to `~/Library/LaunchAgents/com.residue.notifier.plist`.
- **Execution:** Registers the daemon with macOS `launchctl`. It wakes up every 300 seconds (5 minutes) and runs `residue notify`.
- **UI:** The `residue notify` command queries the SQLite database. If tasks are pending, it uses native AppleScript (`osascript -e 'display notification...'`) to trigger a standard macOS banner notification.

## 5. Global Command Line Interface (CLI)
While the AI manages tasks automatically, humans need a way to interact with the system manually.
- **Implementation:** Built using the `click` library in `residue/__main__.py`.
- **Cross-Platform Scripts:** The `pyproject.toml` file uses the `[project.scripts]` directive to map specific Python functions to global shell commands (e.g., `residue-list`, `residue-add`). 
- **Global Availability:** When installed via `pipx install .`, Python automatically generates binary wrapper scripts for these commands and places them in `~/.local/bin/`, making them globally available in the user's `$PATH`.
