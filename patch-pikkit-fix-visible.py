#!/usr/bin/env python3
"""Pikkit icon: blue tile + white hearts (readable at 42px; no black center void)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    '<rect width="48" height="48" rx="11" fill="#4F5FFF"/>'
    '<g fill="#FFFFFF" transform="translate(24 24) scale(1.06)">'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(0)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(90)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(180)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(270)"/>'
    "</g></svg>"
)

SVG_RE = re.compile(
    r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>',
    re.DOTALL,
)

LINK_CSS_OLD = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: none;
            background: transparent;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
        }
        .pikkit-link:hover {
            filter: brightness(1.1);
        }"""

LINK_CSS_NEW = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(96, 112, 255, 0.55);
            background: transparent;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
        }
        .pikkit-link:hover {
            filter: brightness(1.08);
            border-color: rgba(120, 136, 255, 0.85);
        }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if LINK_CSS_OLD in t:
        t = t.replace(LINK_CSS_OLD, LINK_CSS_NEW, 1)
    sm = SVG_RE.search(t)
    if sm:
        t = t[: sm.start()] + INLINE_SVG + t[sm.end() :]
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
