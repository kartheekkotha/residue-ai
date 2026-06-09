# Copyright (c) 2026 Kartheek Kotha.
# Licensed under the MIT License.

"""
residue/installer/platforms/windows.py
Installs a Windows Scheduled Task to proactively check for tasks every 5 minutes.
"""
from __future__ import annotations
import sys
import subprocess
from pathlib import Path

TASK_NAME = "ResidueNotifier"

def install(project_dir: Path = Path(".")) -> list[str]:
    """Install the residue notifier daemon for Windows using schtasks."""
    actions = []
    
    # We use pythonw.exe instead of python.exe so it runs completely hidden without a console window
    python_exe = sys.executable
    if python_exe.lower().endswith("python.exe"):
        python_exe = python_exe[:-10] + "pythonw.exe"
        
    command = f'"{python_exe}" -m residue notify'
    
    # Command to create the scheduled task
    # /tn "ResidueNotifier"
    # /tr "pythonw.exe -m residue notify"
    # /sc minute /mo 5 (every 5 minutes)
    # /f (force overwrite if exists)
    cmd = [
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", command,
        "/sc", "minute",
        "/mo", "5",
        "/f"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        actions.append("Loaded daemon into Task Scheduler (runs every 5m)")
    except subprocess.CalledProcessError as e:
        actions.append(f"Failed to load via schtasks: {e.stderr}")
    except Exception as e:
        actions.append(f"Failed to load via schtasks: {e}")

    return actions

def uninstall(project_dir: Path = Path(".")) -> list[str]:
    """Remove the Windows Scheduled Task."""
    actions = []
    cmd = ["schtasks", "/delete", "/tn", TASK_NAME, "/f"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        actions.append("Deleted daemon from Task Scheduler")
    except Exception:
        pass
    
    return actions
