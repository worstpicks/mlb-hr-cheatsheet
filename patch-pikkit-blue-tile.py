#!/usr/bin/env python3
"""Pikkit header: white four-heart clover on blue tile (app logo)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

OLD_LINK = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: #000000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
            position: relative;
            z-index: 12;
            isolation: isolate;
        }
        .pikkit-link:hover {
            filter: brightness(1.1);
            border-color: rgba(79, 95, 255, 0.55);
        }"""

NEW_LINK = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(0, 122, 255, 0.35);
            background: transparent;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
            position: relative;
            z-index: 12;
            isolation: isolate;
        }
        .pikkit-link:hover {
            filter: brightness(1.06);
            border-color: rgba(0, 122, 255, 0.75);
        }"""

OLD_LIGHT = """        html.theme-light .pikkit-link {
            background: transparent;
            border-color: rgba(15, 23, 42, 0.2);
        }"""

NEW_LIGHT = """        html.theme-light .pikkit-link {
            background: transparent;
            border-color: rgba(0, 122, 255, 0.28);
        }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_LINK in t:
        t = t.replace(OLD_LINK, NEW_LINK, 1)
    if OLD_LIGHT in t:
        t = t.replace(OLD_LIGHT, NEW_LIGHT, 1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
