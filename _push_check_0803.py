#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
assert re.search(r'sheet-date" content="2026-08-03"', html)
assert "Monday, August 3, 2026" in html
assert "Sunday, August 2, 2026 — Worst" not in html
assert "Aaron Nola 🧤" in html
assert "Park +26%" in html  # WSH @ PHI
print("hero/date/bum/park OK")

for script in [
    "validate-index-matchups.py",
    "goblin_parlay_rules.py",
    "verify-summary-0803.py",
    "_audit_0803_final.py",
    "_deep_audit_0803.py",
    "verify-deploy.py",
]:
    print(">>>", script)
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
print("ALL CHECKS PASSED")
