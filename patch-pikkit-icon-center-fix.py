#!/usr/bin/env python3
"""Fix Pikkit icon: remove center 'layer' (transparent hole + double blue rect)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

# Blue tile on the link only; white hearts scaled so center stays clean blue.
INLINE_SVG = (
    '<svg class="pikkit-link__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'width="42" height="42" aria-hidden="true" focusable="false">'
    '<g fill="#FFFFFF" transform="translate(24 24) scale(0.84)">'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(90)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(180)"/>'
    '<path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(270)"/>'
    "</g></svg>"
)

STANDALONE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <rect width="48" height="48" rx="11" fill="#4F5FFF"/>
  <g fill="#FFFFFF" transform="translate(24 24) scale(0.84)">
    <path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"/>
    <path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(90)"/>
    <path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(180)"/>
    <path d="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2s.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z" transform="rotate(270)"/>
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

LINK_CSS_NEW = """        .pikkit-link {
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
        }"""

ICON_CSS_OLD = """        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 11px;
        }"""

ICON_CSS_NEW = """        .pikkit-link__icon {
            display: block;
            width: 100%;
            height: 100%;
        }"""

THEME_GROUP_OLD = """        html.theme-light .header-actions .theme-toggle,
        html.theme-light .pikkit-link,
        html.theme-light .header-actions .social-x,
        html.theme-light .header-actions .header-install-btn {
            background: rgba(255, 255, 255, 0.82);
            border-color: rgba(100, 116, 139, 0.4);
            color: #0f172a;
        }
        html.theme-light .header-actions .theme-toggle:hover,
        html.theme-light .pikkit-link:hover,
        html.theme-light .header-actions .social-x:hover,
        html.theme-light .header-actions .header-install-btn:hover {
            background: #fff;
            color: #0f172a;
        }"""

THEME_GROUP_NEW = """        html.theme-light .header-actions .theme-toggle,
        html.theme-light .header-actions .social-x,
        html.theme-light .header-actions .header-install-btn {
            background: rgba(255, 255, 255, 0.82);
            border-color: rgba(100, 116, 139, 0.4);
            color: #0f172a;
        }
        html.theme-light .pikkit-link {
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


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if LINK_CSS_OLD in t:
        t = t.replace(LINK_CSS_OLD, LINK_CSS_NEW, 1)
    elif "background: transparent" in t and ".pikkit-link {" in t:
        t = t.replace(
            "            border: 1px solid rgba(96, 112, 255, 0.55);\n            background: transparent;",
            "            border: none;\n            background: #4F5FFF;",
            1,
        )
        t = t.replace(
            "        .pikkit-link:hover {\n            filter: brightness(1.08);\n            border-color: rgba(120, 136, 255, 0.85);\n        }",
            "        .pikkit-link:hover {\n            background: #5a6aff;\n        }",
            1,
        )

    if ICON_CSS_OLD in t:
        t = t.replace(ICON_CSS_OLD, ICON_CSS_NEW, 1)

    if THEME_GROUP_OLD in t:
        t = t.replace(THEME_GROUP_OLD, THEME_GROUP_NEW, 1)

    sm = SVG_RE.search(t)
    if sm:
        t = t[: sm.start()] + INLINE_SVG + t[sm.end() :]

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    asset = ROOT / "preview" / "assets" / "pikkit-icon.svg"
    asset.write_text(STANDALONE_SVG.strip() + "\n", encoding="utf-8")
    print("wrote", asset.relative_to(ROOT))
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
