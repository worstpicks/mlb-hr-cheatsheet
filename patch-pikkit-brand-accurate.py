#!/usr/bin/env python3
"""Pikkit header icon: blue four-heart clover on black (matches app logo)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_BLUE = "#4F5FFF"
PIKKIT_BG = "#000000"
# Thin black cross in center (hearts meet at tips, do not overlap).
HEART_SCALE = "0.91"
HEART = (
    'd="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"'
)

INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    f'<rect class="pikkit-link__bg" width="48" height="48" rx="11" fill="{PIKKIT_BG}"/>'
    f'<g class="pikkit-link__mark" fill="{PIKKIT_BLUE}" '
    f'transform="translate(24 24) scale({HEART_SCALE})">'
    f'<path {HEART} transform="rotate(0)"/>'
    f'<path {HEART} transform="rotate(90)"/>'
    f'<path {HEART} transform="rotate(180)"/>'
    f'<path {HEART} transform="rotate(270)"/>'
    "</g></svg>"
)

STANDALONE_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="{PIKKIT_BG}"/>
  <g fill="{PIKKIT_BLUE}" transform="translate(24 24) scale({HEART_SCALE})">
    <path {HEART} transform="rotate(0)"/>
    <path {HEART} transform="rotate(90)"/>
    <path {HEART} transform="rotate(180)"/>
    <path {HEART} transform="rotate(270)"/>
  </g>
</svg>
"""

SVG_RE = re.compile(r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>', re.DOTALL)

LINK_CSS_BLOCK = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover[^\n]*\{[^}]+\}\n"
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
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: transparent;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
        }}
        .pikkit-link:hover .pikkit-link__mark {{ fill: #6370ff; }}
        .pikkit-link:focus-visible {{
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }}
        .pikkit-link__icon {{
            display: block;
            width: 42px;
            height: 42px;
            pointer-events: none;
            flex-shrink: 0;
        }}
        .pikkit-link__mark {{
            pointer-events: none;
        }}
"""

THEME_PIKKIT_RE = re.compile(
    r"        html\.theme-light \.pikkit-link \{[^}]+\}\n"
    r"(?:        html\.theme-light \.pikkit-link:hover[^\n]*\{[^}]+\}\n)?",
    re.DOTALL,
)

THEME_PIKKIT_NEW = """        html.theme-light .pikkit-link {
            background: transparent;
            border-color: rgba(15, 23, 42, 0.2);
        }
        html.theme-light .pikkit-link:hover .pikkit-link__mark { fill: #6370ff; }
"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if LINK_CSS_BLOCK.search(t):
        t = LINK_CSS_BLOCK.sub(LINK_CSS_NEW, t, count=1)

    t = re.sub(
        r"        html\.theme-light \.pikkit-link:hover \.pikkit-link__bg \{ fill: #5a6aff; \}\n?",
        "",
        t,
    )
    if THEME_PIKKIT_RE.search(t):
        t = THEME_PIKKIT_RE.sub(THEME_PIKKIT_NEW, t, count=1)
    elif "html.theme-light .pikkit-link" not in t:
        t = t.replace(
            "        html.theme-light .header-actions .theme-toggle,",
            THEME_PIKKIT_NEW + "        html.theme-light .header-actions .theme-toggle,",
            1,
        )

    sm = SVG_RE.search(t)
    if sm:
        t = t[: sm.start()] + INLINE_SVG + t[sm.end() :]

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    (ROOT / "preview" / "assets" / "pikkit-icon.svg").write_text(
        STANDALONE_SVG.strip() + "\n", encoding="utf-8"
    )
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
