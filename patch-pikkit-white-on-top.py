#!/usr/bin/env python3
"""Pikkit icon: crisp white mark on blue — no fill overlap / link background layer."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

# Blue rect first, then white hearts (smaller so fills do not stack in the center).
HEART = (
    'd="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"'
)
INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    '<rect class="pikkit-link__bg" width="48" height="48" rx="11" fill="#4F5FFF"/>'
    '<g class="pikkit-link__mark" fill="#FFFFFF" transform="translate(24 24) scale(0.72)">'
    f'<path {HEART} transform="rotate(0)"/>'
    f'<path {HEART} transform="rotate(90)"/>'
    f'<path {HEART} transform="rotate(180)"/>'
    f'<path {HEART} transform="rotate(270)"/>'
    "</g></svg>"
)

STANDALONE_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="#4F5FFF"/>
  <g fill="#FFFFFF" transform="translate(24 24) scale(0.72)">
    <path {HEART} transform="rotate(0)"/>
    <path {HEART} transform="rotate(90)"/>
    <path {HEART} transform="rotate(180)"/>
    <path {HEART} transform="rotate(270)"/>
  </g>
</svg>
"""

SVG_RE = re.compile(r'<svg class="pikkit-link__icon"[^>]*>.*?</svg>', re.DOTALL)

LINK_CSS_OLD = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: none;
            background: #4F5FFF;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
            line-height: 0;
        }
        .pikkit-link:hover {
            background: #5a6aff;
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 100%;
            height: 100%;
        }"""

LINK_CSS_NEW = """        .pikkit-link {
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
            overflow: visible;
            flex-shrink: 0;
            line-height: 0;
            position: relative;
            isolation: isolate;
        }
        .pikkit-link:hover .pikkit-link__bg { fill: #5a6aff; }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            position: relative;
            z-index: 1;
            pointer-events: none;
            flex-shrink: 0;
        }
        .pikkit-link__mark {
            pointer-events: none;
        }"""

THEME_PIKKIT_OLD = """        html.theme-light .pikkit-link {
            background: #4F5FFF;
            border: none;
        }
        html.theme-light .header-actions .theme-toggle:hover,
        html.theme-light .header-actions .social-x:hover,
        html.theme-light .header-actions .header-install-btn:hover {
            background: #fff;
            color: #0f172a;
        }
        html.theme-light .pikkit-link:hover {
            background: #5a6aff;
            color: #0f172a;
        }"""

THEME_PIKKIT_NEW = """        html.theme-light .pikkit-link {
            background: transparent;
            border: none;
        }
        html.theme-light .header-actions .theme-toggle:hover,
        html.theme-light .header-actions .social-x:hover,
        html.theme-light .header-actions .header-install-btn:hover {
            background: #fff;
            color: #0f172a;
        }
        html.theme-light .pikkit-link:hover .pikkit-link__bg { fill: #5a6aff; }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if LINK_CSS_OLD in t:
        t = t.replace(LINK_CSS_OLD, LINK_CSS_NEW, 1)
    elif ".pikkit-link__icon {" in t and "pointer-events: none" not in t:
        t = t.replace(
            "            background: #4F5FFF;\n            text-decoration: none;\n            overflow: hidden;",
            "            background: transparent;\n            text-decoration: none;\n            overflow: visible;\n            position: relative;\n            isolation: isolate;",
            1,
        )
        t = t.replace(
            "        .pikkit-link:hover {\n            background: #5a6aff;\n        }",
            "        .pikkit-link:hover .pikkit-link__bg { fill: #5a6aff; }",
            1,
        )
        t = t.replace(
            "        .pikkit-link__icon {\n            display: block;\n            width: 100%;\n            height: 100%;\n        }",
            "        .pikkit-link__icon {\n            display: block;\n            width: 42px;\n            height: 42px;\n            position: relative;\n            z-index: 1;\n            pointer-events: none;\n            flex-shrink: 0;\n        }\n        .pikkit-link__mark { pointer-events: none; }",
            1,
        )

    if THEME_PIKKIT_OLD in t:
        t = t.replace(THEME_PIKKIT_OLD, THEME_PIKKIT_NEW, 1)

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
