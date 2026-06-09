# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/__main__.py
The main CLI entry point. All commands live here.

Usage:
  residue install [--platform claude|gemini|cursor|all]
  residue serve
  residue list
  residue add <title> [description]
  residue edit <id> [--title] [--desc] [--urgency]
  residue done <id>
  residue snooze <id> [hours]
  residue reject <id>
  residue delete <id>
  residue clear
  residue reset
  residue notify            # fire a one-shot OS notification check
  residue notify-on         # enable background OS notifications
  residue notify-off        # disable background OS notifications
  residue check [--once] [--quiet]
"""
from __future__ import annotations
import sys
import json
import click
from pathlib import Path


# ─────────────────────────────────────────────
# CLI Group
# ─────────────────────────────────────────────

@click.group()
@click.version_option(package_name="residue")
def cli():
    """residue — Your AI remembers what you forgot."""
    pass


# ─────────────────────────────────────────────
# residue install
# ─────────────────────────────────────────────

@cli.command()
@click.option(
    "--platform",
    default="auto",
    show_default=True,
    help="Platform to install: claude, gemini, cursor, vscode, all, auto",
)
def install(platform: str):
    """Wire residue into your AI coding tools (auto-detects by default)."""
    from residue.installer.detector import detect
    from residue.installer.platforms import claude, gemini, cursor, codex

    _print_banner()

    if platform == "auto":
        detected = detect()
        if not detected:
            click.echo("  No AI tools detected. Use --platform to specify one manually.")
            sys.exit(1)
        click.echo(f"  Detected: {', '.join(detected)}\n")
        
        os_platform = "windows" if sys.platform == "win32" else "macos"
        platforms_to_install = detected + [os_platform]
    elif platform == "all":
        os_platform = "windows" if sys.platform == "win32" else "macos"
        platforms_to_install = ["claude", "gemini", "cursor", "codex", os_platform]
    else:
        platforms_to_install = [platform]

    for p in platforms_to_install:
        click.echo(f"  Installing for {p}...")
        try:
            if p == "claude":
                actions = claude.install()
            elif p == "gemini":
                actions = gemini.install()
            elif p == "cursor":
                actions = cursor.install()
            elif p == "codex":
                actions = codex.install()
            elif p == "macos":
                from residue.installer.platforms import macos
                actions = macos.install()
            elif p == "windows":
                from residue.installer.platforms import windows
                actions = windows.install()
            else:
                click.echo(f"    ⚠ Unknown platform: {p} — skipping")
                continue
            for action in actions:
                click.echo(f"    ✓ {action}")
        except Exception as e:
            click.echo(f"    ✗ Error installing {p}: {e}", err=True)

    click.echo()
    click.echo("  Done. Restart your AI tool and it will check for pending tasks on the next session.")
    click.echo()


# ─────────────────────────────────────────────
# residue uninstall
# ─────────────────────────────────────────────

@cli.command()
@click.option("--platform", default="all", help="Platform: claude, gemini, cursor, macos, all")
def uninstall(platform: str):
    """Remove residue from your AI coding tools and OS."""
    from residue.installer.platforms import claude, gemini, cursor, codex, macos

    platforms_to_remove = ["claude", "gemini", "cursor", "codex", "macos"] if platform == "all" else [platform]

    for p in platforms_to_remove:
        click.echo(f"  Uninstalling from {p}...")
        try:
            if p == "claude":
                actions = claude.uninstall()
            elif p == "gemini":
                actions = gemini.uninstall()
            elif p == "cursor":
                actions = cursor.uninstall()
            elif p == "codex":
                actions = codex.uninstall()
            elif p == "macos":
                actions = macos.uninstall()
            else:
                continue
            for action in actions:
                click.echo(f"    ✓ {action}")
        except Exception as e:
            click.echo(f"    ✗ Error uninstalling {p}: {e}", err=True)


# ─────────────────────────────────────────────
# residue serve
# ─────────────────────────────────────────────

@cli.command()
def serve():
    """Start the MCP server (called automatically by AI tools)."""
    from residue.server.mcp_server import run
    run()


# ─────────────────────────────────────────────
# residue list
# ─────────────────────────────────────────────

@cli.command(name="list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_tasks(as_json: bool):
    """Show all pending tasks."""
    from residue.db.queries import get_all_tasks

    tasks = get_all_tasks()
    pending = [t for t in tasks if t["status"] == "pending"]
    snoozed = [t for t in tasks if t["status"] == "snoozed"]

    if as_json:
        click.echo(json.dumps(tasks, indent=2, default=str))
        return

    if not tasks:
        click.echo("  No tasks. Your AI will add them when you leave something unfinished.")
        return

    if pending:
        click.echo("\n  📋 Pending:\n")
        for t in pending:
            urgency_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t["urgency"], "⚪")
            click.echo(f"  [{t['id']}] {urgency_icon} {t['title']}")
            if t["description"]:
                click.echo(f"       {t['description']}")

    if snoozed:
        click.echo("\n  💤 Snoozed:\n")
        for t in snoozed:
            click.echo(f"  [{t['id']}] {t['title']} (until {t['snooze_until']})")

    click.echo()


# ─────────────────────────────────────────────
# residue add <title> [description]
# ─────────────────────────────────────────────

@cli.command()
@click.argument("title")
@click.argument("description", required=False, default="")
@click.option("--urgency", default="medium", help="low, medium, high")
def add(title: str, description: str, urgency: str):
    """Add a new task manually."""
    from residue.db.queries import add_task

    task_id = add_task(title=title, description=description, urgency=urgency, source_tool="cli")
    click.echo(f"  ✓ Task {task_id} added: {title}")


# ─────────────────────────────────────────────
# residue edit <id>
# ─────────────────────────────────────────────

@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", help="New title")
@click.option("--desc", help="New description")
@click.option("--urgency", help="New urgency (low, medium, high)")
def edit(task_id: int, title: str, desc: str, urgency: str):
    """Edit an existing task."""
    from residue.db.queries import edit_task

    if not any([title, desc, urgency]):
        click.echo("  ✗ Please provide at least one field to edit (--title, --desc, --urgency).", err=True)
        sys.exit(1)

    ok = edit_task(task_id, title=title, description=desc, urgency=urgency)
    if ok:
        click.echo(f"  ✓ Task {task_id} updated.")
    else:
        click.echo(f"  ✗ Task {task_id} not found or no changes made.", err=True)
        sys.exit(1)


# ─────────────────────────────────────────────
# residue done <id>
# ─────────────────────────────────────────────

@cli.command()
@click.argument("task_id", type=int)
def done(task_id: int):
    """Mark a task as complete."""
    from residue.db.queries import complete_task

    ok = complete_task(task_id)
    if ok:
        click.echo(f"  ✓ Task {task_id} marked as done.")
    else:
        click.echo(f"  ✗ Task {task_id} not found.", err=True)
        sys.exit(1)


# ─────────────────────────────────────────────
# residue snooze <id> [hours]
# ─────────────────────────────────────────────

@cli.command()
@click.argument("task_id", type=int)
@click.argument("hours", type=int, default=2)
def snooze(task_id: int, hours: int):
    """Snooze a task for N hours (default: 2)."""
    from residue.db.queries import snooze_task

    ok = snooze_task(task_id, hours)
    if ok:
        click.echo(f"  💤 Task {task_id} snoozed for {hours} hour(s).")
    else:
        click.echo(f"  ✗ Task {task_id} not found.", err=True)
        sys.exit(1)


# ─────────────────────────────────────────────
# residue reject <id>
# ─────────────────────────────────────────────

@cli.command()
@click.argument("task_id", type=int)
def reject(task_id: int):
    """Mark a task as rejected/dropped."""
    from residue.db.queries import reject_task

    ok = reject_task(task_id)
    if ok:
        click.echo(f"  🗑️ Task {task_id} rejected.")
    else:
        click.echo(f"  ✗ Task {task_id} not found.", err=True)
        sys.exit(1)


# ─────────────────────────────────────────────
# residue delete <id>
# ─────────────────────────────────────────────

@cli.command()
@click.argument("task_id", type=int)
def delete(task_id: int):
    """Permanently delete a task."""
    from residue.db.queries import delete_task

    ok = delete_task(task_id)
    if ok:
        click.echo(f"  ✓ Task {task_id} permanently deleted.")
    else:
        click.echo(f"  ✗ Task {task_id} not found.", err=True)
        sys.exit(1)


# ─────────────────────────────────────────────
# residue clear
# ─────────────────────────────────────────────

@cli.command()
def clear():
    """Remove all done, snoozed, and rejected tasks."""
    from residue.db.queries import clear_done_tasks

    count = clear_done_tasks()
    click.echo(f"  ✓ Cleared {count} task(s).")


# ─────────────────────────────────────────────
# residue reset
# ─────────────────────────────────────────────

@cli.command()
def reset():
    """Start fresh: permanently delete ALL tasks."""
    from residue.db.queries import reset_tasks

    if click.confirm("Are you sure you want to permanently delete all tasks?"):
        count = reset_tasks()
        click.echo(f"  ✓ Completely wiped {count} task(s). Database is fresh.")
    else:
        click.echo("  Aborted.")


# ─────────────────────────────────────────────
# residue notify (used by macOS LaunchAgent)
# ─────────────────────────────────────────────

@cli.command()
@click.option("--on", is_flag=True, help="Turn OS push notifications ON")
@click.option("--off", is_flag=True, help="Turn OS push notifications OFF")
def notify(on: bool, off: bool):
    """Check tasks and send a one-shot OS notification. Use notify-on / notify-off to toggle the background daemon."""
    import subprocess
    import sys

    is_windows = sys.platform == "win32"

    if is_windows:
        from residue.installer.platforms import windows as os_installer
        os_name = "Windows"
    else:
        from residue.installer.platforms import macos as os_installer
        os_name = "macOS"

    if on:
        os_installer.install()
        click.echo(f"  ✓ {os_name} push notifications turned ON.")
        return
    if off:
        os_installer.uninstall()
        click.echo(f"  ✓ {os_name} push notifications turned OFF.")
        return

    from residue.db.queries import get_pending_tasks

    tasks = get_pending_tasks()
    if not tasks:
        return

    count = len(tasks)

    try:
        if is_windows:
            safe_titles = []
            for t in tasks:
                safe_title = t['title'].replace('"', '\\"').replace("'", "\\'")
                safe_titles.append(f"• {safe_title}")
            titles = "\\n".join(safe_titles)

            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            $xml = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>Residue: {count} Pending Task(s)</text>
                        <text>{titles}</text>
                    </binding>
                </visual>
            </toast>
"@
            $doc = New-Object Windows.Data.Xml.Dom.XmlDocument
            $doc.LoadXml($xml)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($doc)
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Residue")
            $notifier.Show($toast)
            '''
            subprocess.run(["powershell", "-Command", script], check=True)
        else:
            safe_titles = []
            for t in tasks:
                safe_title = t['title'].replace('"', '\\"')
                safe_titles.append(f"• {safe_title}")
            titles = "\\n".join(safe_titles)

            script = f'''
            display notification "{titles}" with title "Residue: {count} Pending Task(s)" sound name "Ping"
            '''
            subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        click.echo(f"Failed to send notification: {e}")


# ─────────────────────────────────────────────
# residue notify-on / notify-off
# ─────────────────────────────────────────────

@cli.command(name="notify-on")
def notify_on():
    """Enable background OS notifications (runs every 5 min, shows pending tasks)."""
    import sys
    is_windows = sys.platform == "win32"

    if is_windows:
        from residue.installer.platforms import windows as os_installer
        os_name = "Windows Task Scheduler"
    else:
        from residue.installer.platforms import macos as os_installer
        os_name = "macOS LaunchAgent"

    try:
        actions = os_installer.install()
        for action in actions:
            click.echo(f"  ✓ {action}")
        click.echo(f"\n  ✅ Background notifications enabled via {os_name}.")
        click.echo(f"     You'll get a system popup whenever you have pending tasks.\n")
    except Exception as e:
        click.echo(f"  ✗ Failed to enable notifications: {e}", err=True)


@cli.command(name="notify-off")
def notify_off():
    """Disable background OS notifications."""
    import sys
    is_windows = sys.platform == "win32"

    if is_windows:
        from residue.installer.platforms import windows as os_installer
        os_name = "Windows Task Scheduler"
    else:
        from residue.installer.platforms import macos as os_installer
        os_name = "macOS LaunchAgent"

    try:
        actions = os_installer.uninstall()
        if actions:
            for action in actions:
                click.echo(f"  ✓ {action}")
        else:
            click.echo(f"  ℹ  Notifications were already disabled.")
        click.echo(f"\n  🔕 Background notifications disabled.\n")
    except Exception as e:
        click.echo(f"  ✗ Failed to disable notifications: {e}", err=True)



# ─────────────────────────────────────────────
# residue check (used by hooks — not for humans)
# ─────────────────────────────────────────────

@cli.command()
@click.option("--once", is_flag=True, help="Only print if tasks exist")
@click.option("--quiet", is_flag=True, help="Suppress output entirely")
def check(once: bool, quiet: bool):
    """
    Check and print pending tasks. Called by AI tool hooks at session start.
    Exits with code 0 always (non-blocking).
    """
    from residue.db.queries import get_pending_tasks

    tasks = get_pending_tasks()
    if not tasks or quiet:
        return
    if once and not tasks:
        return

    click.echo("\n📌 residue — pending tasks from your last session:\n")
    for t in tasks:
        icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t["urgency"], "⚪")
        click.echo(f"  [{t['id']}] {icon} {t['title']}")
    click.echo()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _print_banner():
    click.echo()
    click.echo("  ◈ residue — Your AI remembers what you forgot.")
    click.echo()


if __name__ == "__main__":
    cli()
