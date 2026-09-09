#!/usr/bin/env python3
"""Use clean system font for Pikkit wordmark; drop Syne."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

FONT_LINES = re.compile(
    r"    <link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">\n"
    r"    <link rel=\"preconnect\" href=\"https://fonts\.gstatic\.com\" crossorigin>\n"
    r"    <link href=\"https://fonts\.googleapis\.com/css2\?family=Syne[^\"]+\" rel=\"stylesheet\">\n",
)

SYNE_LINK = re.compile(
    r'    <link href="https://fonts\.googleapis\.com/css2\?family=Syne[^"]+" rel="stylesheet">\n'
)

WORDMARK_OLD = re.compile(
    r"        \.pikkit-link__wordmark \{[^}]+\}\n",
    re.DOTALL,
)

WORDMARK_NEW = """        .pikkit-link__wordmark {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            font-size: 0.88rem;
            letter-spacing: 0.03em;
            line-height: 1;
            color: #fff7ed;
            pointer-events: none;
            user-select: none;
        }
"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    t = FONT_LINES.sub("", t)
    t = SYNE_LINK.sub("", t)
    if WORDMARK_OLD.search(t):
        t = WORDMARK_OLD.sub(WORDMARK_NEW, t, count=1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file() and "pikkit-link__wordmark" in p.read_text(encoding="utf-8"):
            patch(p)
