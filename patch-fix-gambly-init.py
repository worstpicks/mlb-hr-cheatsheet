#!/usr/bin/env python3
"""Fix Gambly: declare pickCountEl before wireUxEnhancements calls updatePickCount."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    ROOT / "preview" / "archive" / "2026-05-14.html",
    ROOT / "preview" / "archive" / "2026-05-15.html",
    ROOT / "preview" / "archive" / "2026-05-16.html",
]

EARLY = """            const pickCountEl = document.getElementById("pickCount");
            const clearPicksBtn = document.getElementById("clearPicks");
            const exportGamblyBtn = document.getElementById("exportGambly");
"""

ANCHOR = """            applyQuickFilterAll();
            if (gamesSection) {
                gamesSection.addEventListener("click", (e) => {
                    const gamblyBtn = e.target.closest(".gambly-pick-btn");"""

LATE = """            const pickCountEl = document.getElementById("pickCount");
            const clearPicksBtn = document.getElementById("clearPicks");
            const exportGamblyBtn = document.getElementById("exportGambly");
            function getAmericanFromGiRi"""


def patch(path: Path) -> None:
    if "function wireUxEnhancements" not in path.read_text(encoding="utf-8"):
        print("skip (no UX)", path.relative_to(ROOT))
        return
    t = path.read_text(encoding="utf-8")
    o = t
    if EARLY not in t and ANCHOR in t:
        t = t.replace(
            ANCHOR,
            ANCHOR.replace(
                "            if (gamesSection) {",
                EARLY + "\n            if (gamesSection) {",
                1,
            ),
            1,
        )
    if LATE in t:
        t = t.replace(LATE, "            function getAmericanFromGiRi", 1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
