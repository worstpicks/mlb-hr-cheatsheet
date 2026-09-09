#!/usr/bin/env python3
"""Remove redundant sheetLiveDate line under h1 (date already in intro <p>)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

SPAN = '                    <span class="sheet-live-date" id="sheetLiveDate"></span>\n'

JS_SUB_BLOCK = re.compile(
    r"\n                const sub = document\.getElementById\(\"sheetLiveDate\"\);",
    re.MULTILINE,
)
JS_FMT_LINE = re.compile(
    r"\n                const fmt = d\.toLocaleDateString\(undefined, \{ weekday: \"long\", month: \"long\", day: \"numeric\", year: \"numeric\" \}\);",
    re.MULTILINE,
)
JS_SUB_SET = re.compile(
    r"\n                if \(sub\) sub\.textContent = fmt \+ \(archived \? \" — archived sheet\" : isToday \? \" — today's sheet\" : \"\"\);",
    re.MULTILINE,
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    t = t.replace(SPAN, "")
    t = JS_SUB_BLOCK.sub("", t, count=1)
    t = JS_FMT_LINE.sub("", t, count=1)
    t = JS_SUB_SET.sub("", t, count=1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("removed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
