#!/usr/bin/env python3
"""Remove How to read rows / Grade prose from Legend fold (emoji grid stays)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

LEGEND_GUIDE_PAT = re.compile(
    r"\n\s*<p class=\"model-note\"><strong>How to read rows:</strong>[\s\S]*?"
    r"<p class=\"model-note\"><strong>Grade:</strong>[\s\S]*?</p>",
    re.DOTALL,
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    t = LEGEND_GUIDE_PAT.sub("", t, count=1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("removed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
