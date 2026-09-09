#!/usr/bin/env python3
"""Pikkit: blue hearts visible on top — img icon + z-index + larger clover."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_BLUE = "#4F5FFF"
PIKKIT_BG = "#000000"
HEART_SCALE = "0.96"
HEART = (
    'd="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"'
)

ICON_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="{PIKKIT_BG}"/>
  <g fill="{PIKKIT_BLUE}" transform="translate(24 22.5) scale({HEART_SCALE})">
    <path {HEART}/>
    <path {HEART} transform="rotate(90)"/>
    <path {HEART} transform="rotate(180)"/>
    <path {HEART} transform="rotate(270)"/>
  </g>
</svg>
"""

INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    f'<rect width="48" height="48" rx="11" fill="{PIKKIT_BG}"/>'
    f'<g class="pikkit-link__mark" fill="{PIKKIT_BLUE}" '
    f'transform="translate(24 24) scale({HEART_SCALE})">'
    f'<path {HEART}/>'
    f'<path {HEART} transform="rotate(90)"/>'
    f'<path {HEART} transform="rotate(180)"/>'
    f'<path {HEART} transform="rotate(270)"/>'
    "</g></svg>"
)

IMG_TAG = (
    '<img class="pikkit-link__icon" src="{src}" width="42" height="42" alt="" '
    'decoding="async" loading="eager">'
)

SVG_RE = re.compile(r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>', re.DOTALL)
IMG_RE = re.compile(r'<img class="pikkit-link__icon"[^>]*>', re.DOTALL)

LINK_CSS_BLOCK = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover[^\n]*\{[^}]+\}\n"
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
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            position: relative;
            z-index: 2;
            pointer-events: none;
            flex-shrink: 0;
        }
"""

HEADER_ACTIONS_OLD = """        .header-actions {
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 6;"""

HEADER_ACTIONS_NEW = """        .header-actions {
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 20;"""

THEME_HOVER_RE = re.compile(
    r"        html\.theme-light \.pikkit-link:hover \.pikkit-link__mark \{ fill: #6370ff; \}\n?",
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    asset = "../assets/pikkit-icon.svg" if "/archive/" in str(path).replace("\\", "/") else "assets/pikkit-icon.svg"
    img = IMG_TAG.format(src=asset)

    if HEADER_ACTIONS_OLD in t:
        t = t.replace(HEADER_ACTIONS_OLD, HEADER_ACTIONS_NEW, 1)

    if LINK_CSS_BLOCK.search(t):
        t = LINK_CSS_BLOCK.sub(LINK_CSS_NEW, t, count=1)

    t = THEME_HOVER_RE.sub("", t)
    t = re.sub(
        r"        html\.theme-light \.pikkit-link:hover \.pikkit-link__bg \{[^}]+\}\n?",
        "",
        t,
    )
    t = re.sub(
        r"        \.pikkit-link:hover \.pikkit-link__mark \{ fill: #6370ff; \}\n?",
        "",
        t,
    )
    t = re.sub(
        r"        \.pikkit-link:hover \.pikkit-link__bg \{ fill: #[^;]+; \}\n?",
        "",
        t,
    )

    sm = SVG_RE.search(t)
    if sm:
        t = t[: sm.start()] + img + t[sm.end() :]
    elif IMG_RE.search(t):
        t = IMG_RE.sub(img, t, count=1)

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    (ROOT / "preview" / "assets" / "pikkit-icon.svg").write_text(
        ICON_SVG.strip() + "\n", encoding="utf-8"
    )
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
