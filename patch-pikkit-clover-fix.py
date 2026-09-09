#!/usr/bin/env python3
"""Pikkit clover: no center circle, no clipped hearts, no overflow crop."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PETAL = (
    "d=\"M0-9C-5.5-9-9.5-4.5-8.5 0.5C-7 4 0 7 0 7"
    "C0 7 7 4 8.5 0.5C9.5-4.5 5.5-9 0-9Z\""
)

SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Pikkit">
  <g fill="#FFFFFF" transform="translate(24 24) scale(0.88)">
    <path {PETAL}/>
    <path {PETAL} transform="rotate(90)"/>
    <path {PETAL} transform="rotate(180)"/>
    <path {PETAL} transform="rotate(270)"/>
  </g>
</svg>
"""

LINK_CSS_RE = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover \{[^}]+\}\n"
    r"        \.pikkit-link:focus-visible \{[^}]+\}\n",
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
            background: transparent;
            text-decoration: none;
            overflow: visible;
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
"""


def patch(path: Path) -> None:
    if "pikkit-link" not in path.read_text(encoding="utf-8"):
        print("skip", path.relative_to(ROOT))
        return
    t = path.read_text(encoding="utf-8")
    o = t
    if LINK_CSS_RE.search(t):
        t = LINK_CSS_RE.sub(LINK_CSS_NEW, t, count=1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched css", path.relative_to(ROOT))


if __name__ == "__main__":
    (ROOT / "preview" / "assets" / "pikkit-icon.svg").write_text(SVG.strip() + "\n", encoding="utf-8")
    print("wrote preview/assets/pikkit-icon.svg")
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
