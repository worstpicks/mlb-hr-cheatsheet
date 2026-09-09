#!/usr/bin/env python3
"""Pikkit icon: white clover only, no blue rounded tile."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

HEART = (
    'd="M0-9.5c-3.8-5.8-11.2-4.2-8.2 2.2-.8 1.6 0 4.2 0 4.2'
    's.8-2.6 0-4.2c3-6.4 10.4-8 8.2-2.2z"'
)

PETAL = (
    "d=\"M0-9C-5.5-9-9.5-4.5-8.5 0.5C-7 4 0 7 0 7"
    "C0 7 7 4 8.5 0.5C9.5-4.5 5.5-9 0-9Z\""
)
SVG_NO_TILE = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <g fill="#FFFFFF" transform="translate(24 24) scale(0.88)">
    <path {PETAL}/>
    <path {PETAL} transform="rotate(90)"/>
    <path {PETAL} transform="rotate(180)"/>
    <path {PETAL} transform="rotate(270)"/>
  </g>
</svg>
"""

ICON_CSS_OLD = re.compile(
    r"        \.pikkit-link__icon \{[^}]+\}\n",
    re.DOTALL,
)
ICON_CSS_NEW = """        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            pointer-events: none;
            flex-shrink: 0;
        }
"""

LIGHT_PIKKIT = """        html.theme-light .pikkit-link__icon {
            filter: brightness(0) saturate(100%) invert(32%) sepia(93%) saturate(4200%) hue-rotate(211deg) brightness(101%) contrast(107%);
        }
"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if "pikkit-link" not in t:
        print("skip", path.relative_to(ROOT))
        return
    o = t
    if ICON_CSS_OLD.search(t):
        t = ICON_CSS_OLD.sub(ICON_CSS_NEW, t, count=1)
    if "html.theme-light .pikkit-link__icon" not in t and "html.theme-light .pikkit-link:hover" in t:
        t = t.replace(
            "        html.theme-light .pikkit-link:hover {\n            filter: brightness(1.06);\n        }\n",
            "        html.theme-light .pikkit-link:hover {\n            filter: brightness(1.06);\n        }\n"
            + LIGHT_PIKKIT,
            1,
        )
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched css", path.relative_to(ROOT))


if __name__ == "__main__":
    (ROOT / "preview" / "assets" / "pikkit-icon.svg").write_text(
        SVG_NO_TILE.strip() + "\n", encoding="utf-8"
    )
    print("wrote preview/assets/pikkit-icon.svg (clover only)")
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
