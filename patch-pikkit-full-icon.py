#!/usr/bin/env python3
"""Pikkit header: full blue-tile + white clover SVG as img (matches brand asset)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_BLUE = "#007AFF"
HEART = (
    'd="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2'
    's.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"'
)

STANDALONE_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="{PIKKIT_BLUE}"/>
  <g fill="#FFFFFF" transform="translate(24 24) scale(0.92)">
    <path {HEART}/>
    <path {HEART} transform="rotate(90)"/>
    <path {HEART} transform="rotate(180)"/>
    <path {HEART} transform="rotate(270)"/>
  </g>
</svg>
"""

IMG_TAG = (
    '<img class="pikkit-link__icon" src="assets/pikkit-icon.svg" width="42" height="42" alt="" '
    'decoding="async" loading="eager">'
)
ARCHIVE_IMG = IMG_TAG.replace('src="assets/', 'src="../assets/')

SVG_RE = re.compile(
    r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>',
    re.DOTALL,
)
IMG_RE = re.compile(
    r'<img class="pikkit-link__icon"[^>]*>',
)

LINK_CSS_RE = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover \{[^}]+\}\n"
    r"        \.pikkit-link:focus-visible \{[^}]+\}\n"
    r"        \.pikkit-link__icon \{[^}]+\}\n"
    r"(?:        \.pikkit-link__mark \{[^}]+\}\n)?",
    re.DOTALL,
)

LINK_CSS_NEW = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border: none;
            border-radius: 12px;
            background: transparent;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
            position: relative;
            z-index: 12;
        }
        .pikkit-link:hover {
            filter: brightness(1.06);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 12px;
            pointer-events: none;
            flex-shrink: 0;
        }
"""

THEME_PIKKIT_RE = re.compile(
    r"        html\.theme-light \.pikkit-link \{[^}]+\}\n"
    r"        html\.theme-light \.pikkit-link:hover \{[^}]+\}\n",
    re.DOTALL,
)
THEME_PIKKIT_NEW = """        html.theme-light .pikkit-link {
            background: transparent;
            border: none;
        }
        html.theme-light .pikkit-link:hover {
            filter: brightness(1.06);
        }
"""


def patch(path: Path) -> None:
    if "pikkit-link" not in path.read_text(encoding="utf-8"):
        print("skip (no pikkit)", path.relative_to(ROOT))
        return
    t = path.read_text(encoding="utf-8")
    o = t

    if LINK_CSS_RE.search(t):
        t = LINK_CSS_RE.sub(LINK_CSS_NEW, t, count=1)

    if THEME_PIKKIT_RE.search(t):
        t = THEME_PIKKIT_RE.sub(THEME_PIKKIT_NEW, t, count=1)

    img = ARCHIVE_IMG if "archive" in str(path) else IMG_TAG
    m = SVG_RE.search(t) or IMG_RE.search(t)
    if m:
        t = t[: m.start()] + img + t[m.end() :]

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
