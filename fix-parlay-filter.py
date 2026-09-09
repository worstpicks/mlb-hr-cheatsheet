#!/usr/bin/env python3
"""Parlay/export: respect advanced-filter-hidden; My Slip without toolbar panel."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [ROOT / "preview" / "index.html", ROOT / "index.html"]

OLD_REBUILD_GUARD = """            function rebuildParlayPanel() {
                const panel = document.getElementById("parlayPanel");
                const ul = document.getElementById("parlayLegs");
                if (!panel || !ul) return;"""

NEW_REBUILD_GUARD = """            function rebuildParlayPanel() {
                const panel = document.getElementById("parlayPanel");
                const ul = document.getElementById("parlayLegs");
                if (!ul) return;"""

OLD_FILTER = """.filter((r) => r && !r.classList.contains("pick-hidden") && !r.classList.contains("quick-filter-hidden") && !r.classList.contains("emoji-filter-hidden"))"""

NEW_FILTER = """.filter((r) => r && !r.classList.contains("pick-hidden") && !r.classList.contains("quick-filter-hidden") && !r.classList.contains("emoji-filter-hidden") && !r.classList.contains("advanced-filter-hidden"))"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_REBUILD_GUARD in t:
        t = t.replace(OLD_REBUILD_GUARD, NEW_REBUILD_GUARD, 1)
    if OLD_FILTER in t:
        t = t.replace(OLD_FILTER, NEW_FILTER)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.name)
    else:
        print("ok", path.name)


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
