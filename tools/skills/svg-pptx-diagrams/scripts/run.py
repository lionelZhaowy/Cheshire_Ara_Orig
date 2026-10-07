#!/usr/bin/env python3
"""Use the skill's isolated environment when installed; otherwise current Python."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.is_file():
    python = Path(sys.executable)
# Windows execv starts a new process then exits the current one; a caller may
# proceed before the export finishes and cannot reliably observe its exit code.
# Keep a waiting parent on all platforms so PowerShell and batch callers agree.
raise SystemExit(subprocess.call([str(python), str(root / "scripts/svg_to_pptx.py"), *sys.argv[1:]]))
