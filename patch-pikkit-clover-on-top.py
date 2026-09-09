#!/usr/bin/env python3
"""Pikkit: solid white clover on blue tile — no center pinch / square hole."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_BLUE = "#007AFF"
PIKKIT_BLUE_HOVER = "#1A88FF"
# Rounded heart: tip points outward, wide lobe wraps center (no cleft square at origin)
HEART = (
    "d=\"M0-9.2C-4.8-9.2-8.8-5.2-8.8-0.2C-8.8 4.2-4.2 8.8 0 9.2"
    "C4.2 8.8 8.8 4.2 8.8-0.2C8.8-5.2 4.8-9.2 0-9.2Z\""
)

INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    f'<g class="pikkit-link__mark" fill="#FFFFFF" transform="translate(24 24)">'
    f'<path {HEART} transform="rotate(0)"/>'
    f'<path {HEART} transform="rotate(90)"/>'
    f'<path {HEART} transform="rotate(180)"/>'
    f'<path {HEART} transform="rotate(270)"/>'
    "</g></svg>"
)

STANDALONE_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="{PIKKIT_BLUE}"/>
  <g fill="#FFFFFF" transform="translate(24 24)">
    <path {HEART} transform="rotate(0)"/>
    <path {HEART} transform="rotate(90)"/>
    <path {HEART} transform="rotate(180)"/>
    <path {HEART} transform="rotate(270)"/>
  </g>
</svg>
"""

LINK_CSS_RE = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover \{[^}]+\}\n"
    r"        \.pikkit-link:focus-visible \{[^}]+\}\n"
    r"        \.pikkit-link__icon \{[^}]+\}\n"
    r"        \.pikkit-link__mark \{[^}]+\}\n",
    re.DOTALL,
)

LINK_CSS_NEW = f"""        .pikkit-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: none;
            background: {PIKKIT_BLUE};
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
            position: relative;
            z-index: 12;
        }}
        .pikkit-link:hover {{
            background: {PIKKIT_BLUE_HOVER};
        }}
        .pikkit-link:focus-visible {{
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }}
        .pikkit-link__icon {{
            position: absolute;
            inset: 0;
            display: block;
            width: 100%;
            height: 100%;
            z-index: 2;
            pointer-events: none;
        }}
        .pikkit-link__mark {{
            pointer-events: none;
        }}
"""

THEME_PIKKIT_RE = re.compile(
    r"        html\.theme-light \.pikkit-link \{[^}]+\}\n"
    r"        html\.theme-light \.pikkit-link:hover \{[^}]+\}\n",
    re.DOTALL,
)
THEME_PIKKIT_NEW = f"""        html.theme-light .pikkit-link {{
            background: {PIKKIT_BLUE};
            border: none;
        }}
        html.theme-light .pikkit-link:hover {{
            background: {PIKKIT_BLUE_HOVER};
        }}
"""

IMG_RE = re.compile(
    r'<img class="pikkit-link__icon" src="(?:\.\./)?assets/pikkit-icon\.svg"[^>]*>',
)
SVG_RE = re.compile(
    r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>',
    re.DOTALL,
)


def patch(path: Path) -> None:
    if "pikkit-link" not in path.read_text(encoding="utf-8"):
        print("skip (no pikkit)", path.relative_to(ROOT))
        return
    t = path.read_text(encoding="utf-8")
    o = t

    if LINK_CSS_RE.search(t):
        t = LINK_CSS_RE.sub(LINK_CSS_NEW, t, count=1)
    elif ".pikkit-link {" in t:
        print("warn: pikkit CSS block shape changed —", path.relative_to(ROOT))

    if THEME_PIKKIT_RE.search(t):
        t = THEME_PIKKIT_RE.sub(THEME_PIKKIT_NEW, t, count=1)

    m = IMG_RE.search(t) or SVG_RE.search(t)
    if m:
        t = t[: m.start()] + INLINE_SVG + t[m.end() :]

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    (ROOT / "preview" / "assets" / "pikkit-icon.svg").write_text(
        STANDALONE_SVG.strip() + "\n", encoding="utf-8"
    )
    print("wrote preview/assets/pikkit-icon.svg")
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
