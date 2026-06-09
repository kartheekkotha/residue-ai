# 🧠 residue

> Your AI remembers what you forgot.

<video src="https://raw.githubusercontent.com/kartheekkotha/residue/demo-video/public/demo/residue-demo.mp4" controls="controls" muted="muted" style="max-width: 100%;"></video>

**residue** is a global, invisible, AI-driven task persistence layer that works across every major AI coding tool — Claude Code, Cursor, Antigravity, Gemini CLI, Codex, and more.

Instead of managing a separate to-do app or losing track of half-finished ideas across different terminal sessions, Residue turns your AI assistants into your personal project managers. You never create a reminder manually; your AI simply notices when you leave something unfinished, saves it silently, and tells you about it the next time you start a session — **in any tool**.

---

## Introduction & Why Residue?

When coding with AI, conversations are ephemeral. You might be deep in a debugging session in Claude Code and say, *"Let's pause this and check the API docs tomorrow."* The next day, you open Cursor, and the context is completely lost.

Residue solves this by providing a unified **Model Context Protocol (MCP)** server and automated hooks that sync your open loops across all your tools automatically. 

- **Invisible:** You don't manage it. The AI manages it.
- **Universal:** Start a task in Gemini CLI, get reminded about it in Cursor.
- **Local:** All data is stored locally in SQLite (`~/.residue/tasks.db`). No cloud tracking.

---

## How To Use It (Examples)

Using Residue requires zero friction. You interact with your AI naturally, and it handles the rest.

### Scenario 1: Implicit Deferral
You're working late in **Cursor** and hit a roadblock.
**You:** *"This build is taking too long. Let's look at the failing tests tomorrow morning."*
*(Behind the scenes, Cursor silently calls `residue add_task("Fix failing tests")`)*

The next morning, you open your terminal and start **Claude Code** (or Antigravity/Codex) for a new task.
**Claude Code:** *"Before we start — you have a pending task from your last session: 'Fix failing tests'. Would you like to work on that now, or snooze it?"*

### Scenario 2: Direct Command
You realize you need to refactor a component but don't want to break your current flow.
**You:** *"Hey, add a residue task to refactor the Auth component later."*
*(The AI confirms it has added the task)*

### Scenario 3: Snoozing & Completing
When the AI reminds you of a task, you can easily manage it conversationally:
**You:** *"Snooze the auth refactor for 4 hours."*
**You:** *"I actually finished the failing tests manually, go ahead and drop that task."*

You can also use explicit **Slash Commands** inside compatible terminals (like Antigravity or Codex):
- Type `/residue-list` to instantly view all tasks.
- Type `/residue-add Check the database logs` to manually save an idea.

### Scenario 4: Autonomous AI Auto-Resolution
The AI also uses Residue to leave reminders for itself! 
If the AI kicks off a long-running Vercel deployment, it might quietly add a task: `owner="ai", title="Verify Vercel build"`.
The next day, when you open your IDE, the AI boots up and reads its pending tasks. It sees the AI-owned verification task, checks the Vercel API internally, realizes the build succeeded, and **silently closes the task** without ever bothering you! It only interrupts you if it needs your help.

---

## Install

> **Note:** residue is now available on PyPI!

### Requirements
- Python 3.10+
- One or more of: Claude Code, Cursor, Gemini CLI, Antigravity

### Step 1 — Install Globally

We recommend using `pipx` to install `residue` globally. This ensures the CLI is available everywhere and avoids virtual environment path issues.

```bash
pipx install residue-ai
```

Alternatively, you can install it into a specific environment:

```bash
# Using standard pip
pip install residue-ai

# Using uv
uv pip install residue-ai
```

Or clone and install in editable mode (for contributors):

```bash
git clone https://github.com/kartheekkotha/residue.git
cd residue
pip install -e .
```

### Step 2 — Wire up your AI tools

```bash
# Auto-detect and install into all tools found on your machine
residue install

# Or target a specific tool
residue install --platform claude
residue install --platform gemini
residue install --platform cursor
```

That's it. Restart your AI tool and it will start reminding you of pending tasks at the beginning of every session.

---

## CLI Commands

You can use the main `residue` command or use the standalone global commands (useful for quick execution or within AI terminal interfaces like Codex):

```bash
residue install          # Wire all detected AI tools
residue serve            # Start MCP server (auto-called by AI tools)
residue notify --on      # Enable OS push notifications (runs daemon on macOS or Windows)
residue notify --off     # Disable OS push notifications (rely only on chat reminders)

# Main commands (also available as standalone residue-* commands)
residue list             # or: residue-list
residue add <title>      # or: residue-add <title>
residue edit <id>        # or: residue-edit <id>
residue done <id>        # or: residue-done <id>
residue snooze <id> <h>  # or: residue-snooze <id> <h>
residue reject <id>      # or: residue-drop <id>
residue delete <id>      # or: residue-delete <id>
residue clear            # clear all done/snoozed/rejected tasks
```

---

## MCP Tools (used by AI, not by you)

| Tool                | What it does                               |
| ---------------------| --------------------------------------------|
| `get_pending_tasks` | Returns all pending tasks at session start and prompts AI to ask you what to do |
| `add_task`          | AI saves an open loop silently (supports `delay_hours`) |
| `complete_task`     | AI marks task done when you confirm        |
| `snooze_task`       | AI snoozes when you say "not now"          |
| `reject_task`       | AI drops a task you no longer want to do   |

---

## Supported Platforms

| Tool | Status |
|------|--------|
| Claude Code | ✅ Phase 1 |
| Gemini CLI / Antigravity | ✅ Phase 1 |
| Cursor | ✅ Phase 1 |
| VS Code Copilot | ✅ Phase 1 |
| Codex / OpenCode | ✅ Phase 1 |

### Operating Systems
- **macOS:** Native desktop notifications via `osascript` & background daemon via `launchctl`.
- **Windows:** Native Windows 10/11 Toast Notifications via PowerShell & background daemon via Task Scheduler (`schtasks`).
- **Linux:** CLI works natively, but desktop notifications and daemon are pending.

---

## Storage

All tasks are stored locally at `~/.residue/tasks.db` (SQLite). No cloud, no accounts, no tracking.

---

## License

MIT
