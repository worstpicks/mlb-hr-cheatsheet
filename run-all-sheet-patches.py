#!/usr/bin/env python3
"""Apply UX / archive patches to current index and all archive sheets."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_PATCHES = [
    "patch-ux-improvements.py",
    "patch-fix-score-grade-filters.py",
    "patch-fix-gambly-init.py",
    "patch-remove-duplicate-filters.py",
    "patch-fix-my-slip.py",
    "patch-fix-my-slip-dom.py",
    "patch-pikkit-top-only.py",
    "patch-fab-compact.py",
    "patch-fix-slip-count.py",
]

ARCHIVE_PATCHES = [
    "patch-batters-won.py",
    "move-batters-won-bottom.py",
    "patch-archived-title.py",
    "fix-archive-picker.py",
    "patch-current-slate-btn.py",
]


def run_script(py: str, name: str) -> None:
    path = ROOT / name
    if not path.is_file():
        print("skip missing", name)
        return
    print("---", name)
    r = subprocess.run([py, str(path)], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"{name} failed with code {r.returncode}")


def main() -> None:
    py = sys.executable
    for name in INDEX_PATCHES:
        run_script(py, name)
    run_script(py, "sync-archives-from-index.py")
    for name in ARCHIVE_PATCHES:
        run_script(py, name)
    print("done")


if __name__ == "__main__":
    main()
