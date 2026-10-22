#!/usr/bin/env python3
"""
BLACK ROYAL — Master "sports" Autonomous Pipeline
Delegates to pronostico_diario.py to execute the full daily cycle with real ESPN/DraftKings data:
1. Audits & Settles previous pending scenarios (Football & Hybrid).
2. Analyzes real-time fixtures and lines for today.
3. Generates Opción 1 (100% Football) & Opción 2 (Hybrid Multi-Sport).
4. Rebuilds and synchronizes index.html.
5. Archives snapshots into scenarios_archive.json.
"""

import os
import subprocess
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PRONOSTICO_SCRIPT = os.path.join(CURRENT_DIR, "pronostico_diario.py")


def main():
    cmd = [sys.executable, PRONOSTICO_SCRIPT] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=CURRENT_DIR)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
