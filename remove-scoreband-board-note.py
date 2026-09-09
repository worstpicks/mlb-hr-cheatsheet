#!/usr/bin/env python3
"""Remove 'This board covers…' bet-tracker note from Score Bands panel."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

BOARD_NOTE_PAT = re.compile(
    r"\n\s*<p class=\"model-note\">This board covers[\s\S]*?</p>",
    re.DOTALL,
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    t = BOARD_NOTE_PAT.sub("", t, count=1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("removed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
