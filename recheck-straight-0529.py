#!/usr/bin/env python3
"""Recheck straight picks for 2026-05-29 (wrapper — prefer recheck-straight.py --date 2026-05-29)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
raise SystemExit(
    subprocess.call(
        [sys.executable, str(ROOT / "recheck-straight.py"), "--date", "2026-05-29", "--import"],
        cwd=ROOT,
    )
)
