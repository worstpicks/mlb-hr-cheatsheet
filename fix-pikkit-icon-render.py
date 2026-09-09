#!/usr/bin/env python3
"""Fix Pikkit icon: clearer SVG + CSS so it scales cleanly in the header."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

OLD_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(79, 95, 255, 0.55);
            background: #000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: #0a0a0a;
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
            object-fit: cover;
        }"""

NEW_CSS = """        .pikkit-link {
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

OLD_MEDIA = """            .header-actions .pikkit-link,
            .header-actions .pikkit-link__icon { width: 38px; height: 38px; }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_CSS in t:
        t = t.replace(OLD_CSS, NEW_CSS, 1)
    if 'object-fit: cover' in t and '.pikkit-link__icon' in t:
        t = t.replace(
            ".pikkit-link__icon {\n            display: block;\n            width: 42px;\n            height: 42px;\n            border-radius: 11px;\n            object-fit: cover;\n        }",
            ".pikkit-link__icon {\n            display: block;\n            width: 100%;\n            height: 100%;\n            border-radius: 11px;\n            object-fit: contain;\n        }",
            1,
        )
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("css", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
