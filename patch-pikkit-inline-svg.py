#!/usr/bin/env python3
"""Pikkit header: inline SVG for crisp rendering (no scaled img)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    '<rect width="48" height="48" rx="11" fill="#000"/>'
    '<g fill="#4F5FFF" transform="translate(24 24)">'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(0)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(90)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(180)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(270)"/>'
    "</g></svg>"
)

OLD_LINK_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(79, 95, 255, 0.5);
            background: #000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            filter: brightness(1.12);
            border-color: rgba(79, 95, 255, 0.75);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 100%;
            height: 100%;
            border-radius: 11px;
            object-fit: contain;
        }"""

NEW_LINK_CSS = """        .pikkit-link {
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
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 11px;
        }"""

IMG_RE = re.compile(
    r'<img class="pikkit-link__icon" src="(?:\.\./)?assets/pikkit-(?:icon|logo)\.svg"[^>]*>',
)
SVG_RE = re.compile(
    r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>',
    re.DOTALL,
)


def patch_file(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if OLD_LINK_CSS in t:
        t = t.replace(OLD_LINK_CSS, NEW_LINK_CSS, 1)

    m = IMG_RE.search(t)
    if m:
        t = t[: m.start()] + INLINE_SVG + t[m.end() :]
    else:
        sm = SVG_RE.search(t)
        if sm:
            t = t[: sm.start()] + INLINE_SVG + t[sm.end() :]

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch_file(p)
