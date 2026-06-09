# 💡 Residue: Market Analysis & Feature Ideas

Residue successfully solves the core problem of **context loss between AI coding sessions** through an invisible, global persistence layer. However, looking at the broader market of developer productivity tools (like Linear, Notion, Todoist) and AI agent frameworks, there are several key areas where Residue can expand to become a complete developer ecosystem.

Below is an analysis of what is currently missing and proposed features for future development.

---

## 1. Contextual Awareness & Workspaces

**The Problem:** Currently, all tasks are dumped into a single global list. If a developer works on 4 different repositories in a day, the AI will pull up backend tasks while they are working on a frontend repository.

**Feature Ideas:**
- **Repository / Workspace Tagging:** Automatically tag tasks with the current working directory or Git repository name when the AI creates them. 
- **Smart Fetching:** `get_pending_tasks` should take an optional `workspace_path` parameter. When you start Claude Code in `~/Codes/frontend`, the AI only reminds you about frontend tasks.
- **Custom Labels / Tags:** Allow the AI to attach tags like `#bug`, `#refactor`, or `#research` so users can filter `residue list --tag bug`.

## 2. Environment Snapshots (State Resumption)

**The Problem:** Knowing *what* to do is only half the battle. The AI (and developer) also needs to remember *where* they were.

**Feature Ideas:**
- **Git Branch Tracking:** When a task is added, Residue automatically records the current Git branch.
- **Open Files Snapshot:** Record which files were actively open or being edited when the task was deferred. 
- **"Resume Task" Command:** When the user says *"Resume task 3"*, the AI not only marks it as active but automatically runs `git checkout <branch>` and opens the relevant files in the IDE to restore the exact state.

## 3. Advanced Task Relationships

**The Problem:** Real-world software engineering involves complex, multi-step features, not just flat checklists.

**Feature Ideas:**
- **Subtasks & Checklists:** Allow `add_task` to accept an array of sub-steps. The AI can check them off incrementally.
- **Blockers / Dependencies:** Mark Task B as "blocked by" Task A. The AI won't remind you about Task B until Task A is completed.

## 4. Git & CI/CD Integrations

**The Problem:** Developers shouldn't have to manually tell the AI they finished a task if their code already proves it.

**Feature Ideas:**
- **Pre-commit / Post-commit Hooks:** Residue can scan git commit messages. If it sees `Fixes residue-5`, it automatically calls `complete_task(5)` in the background.
- **PR Generation:** A command like `residue summarize 3` where the AI reads a completed task and automatically generates a detailed GitHub Pull Request description based on the task history.


## 6. Cross-Device Synchronization

**The Problem:** The current `tasks.db` is strictly local. Developers who switch between a work laptop and a personal desktop will have disjointed task lists.

**Feature Ideas:**
- **Bring-Your-Own-Cloud (BYOC):** Support storing the SQLite database in iCloud Drive, Dropbox, or Google Drive folders.
- **Encrypted Gist Sync:** A lightweight sync engine that pushes an encrypted JSON representation of the tasks to a private GitHub Gist, allowing secure, serverless syncing across machines.

## 6. Time Management & Analytics

**The Problem:** It's hard to measure productivity or know when tasks are becoming stale.

**Feature Ideas:**
- **Auto-Staling (Decay):** If a task has been snoozed 5 times or is older than 2 weeks, the AI proactively asks: *"Task 2 has been pending for a long time. Should we just drop it?"*
- **Developer Velocity Reports:** A Friday afternoon hook where the AI says: *"Happy Friday! You completed 12 tasks this week and dropped 2. Here's a summary of what you shipped..."*
- **Calendar Integrations:** Two-way sync with Apple Calendar or Google Calendar so high-urgency tasks physically block out time on the developer's schedule.
