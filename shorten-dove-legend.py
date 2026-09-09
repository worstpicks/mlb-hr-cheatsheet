#!/usr/bin/env python3
"""Shorten 🕊️ legend — drop PropFinder handedness / lane detail."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

REPLACEMENTS = [
    (
        "<strong>🕊️</strong> Clear pitcher HR-risk advantage (PropFinder HR-risk split favors this batter's handedness / lane)",
        "<strong>🕊️</strong> Pitcher HR-risk advantage",
    ),
    (
        'title="PropFinder HR-risk split favors this batter lane">🕊️ HR-risk edge',
        'title="Pitcher HR-risk advantage">🕊️ HR-risk edge',
    ),
]


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    for old, new in REPLACEMENTS:
        t = t.replace(old, new)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("updated", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
