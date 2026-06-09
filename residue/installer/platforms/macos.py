# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/macos.py
Installs a macOS LaunchAgent to proactively check for tasks every 5 minutes.
"""
from __future__ import annotations
import sys
import subprocess
from pathlib import Path

PLIST_NAME = "com.residue.notifier.plist"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / PLIST_NAME

PLIST_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.residue.notifier</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>-m</string>
        <string>residue</string>
        <string>notify</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""

def install(project_dir: Path = Path(".")) -> list[str]:
    """Install the residue notifier daemon for macOS."""
    actions = []
    
    # Write the plist file
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(PLIST_CONTENT, encoding="utf-8")
    actions.append(f"Wrote LaunchAgent plist → {PLIST_PATH}")
    
    # Load into launchctl
    try:
        # Unload if it already exists to refresh it
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
        subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=True, capture_output=True)
        actions.append("Loaded daemon into launchctl (runs every 5m)")
    except Exception as e:
        actions.append(f"Failed to load via launchctl: {e}")

    return actions

def uninstall(project_dir: Path = Path(".")) -> list[str]:
    """Remove the macOS LaunchAgent."""
    actions = []
    if PLIST_PATH.exists():
        try:
            subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
            actions.append("Unloaded daemon from launchctl")
        except Exception:
            pass
        PLIST_PATH.unlink()
        actions.append(f"Deleted LaunchAgent plist → {PLIST_PATH}")
    
    return actions
