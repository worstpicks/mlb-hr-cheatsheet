#!/usr/bin/env python3
"""Tighter FAB stack spacing and padding."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

REPLACEMENTS = [
    (
        """        :root {
            --fab-edge: 14px;
            --fab-gap: 12px;
            --fab-slip-h: 50px;
            --fab-top-h: 42px;
        }""",
        """        :root {
            --fab-edge: 12px;
            --fab-gap: 6px;
            --fab-slip-h: 40px;
            --fab-top-h: 32px;
        }""",
    ),
    (
        ":root { --fab-edge: 12px; --fab-gap: 10px; --fab-slip-h: 46px; --fab-top-h: 38px; }",
        ":root { --fab-edge: 10px; --fab-gap: 6px; --fab-slip-h: 40px; --fab-top-h: 34px; }",
    ),
    ("padding: 12px 16px; border-radius: 999px;\n            border: 1px solid rgba(251, 146, 60, 0.5);\n            background: linear-gradient(135deg, rgba(180, 83, 9, 0.98)",
     "padding: 10px 14px; border-radius: 999px;\n            border: 1px solid rgba(251, 146, 60, 0.5);\n            background: linear-gradient(135deg, rgba(180, 83, 9, 0.98)"),
    ("font-size: 0.85rem; cursor: pointer;\n            box-shadow: 0 8px 28px", "font-size: 0.8rem; cursor: pointer;\n            box-shadow: 0 8px 28px"),
    ("padding: 10px 18px;\n            border-radius: 999px;\n            font-weight: 800;\n            cursor: pointer;\n            font-size: 0.82rem;",
     "padding: 8px 14px;\n            border-radius: 999px;\n            font-weight: 800;\n            cursor: pointer;\n            font-size: 0.78rem;"),
    ("padding: 8px 12px;\n            font-weight: 800;\n            font-size: 0.72rem;\n            text-transform: uppercase;\n            letter-spacing: 0.05em;\n            cursor: pointer;\n            border: 1px solid rgba(251, 146, 60, 0.45);\n            background: rgba(8, 6, 5, 0.94);\n            color: #fed7aa;\n        }\n        .quick-legend-panel {\n            display: none;\n            margin-top: 8px;",
     "padding: 6px 10px;\n            font-weight: 800;\n            font-size: 0.68rem;\n            text-transform: uppercase;\n            letter-spacing: 0.05em;\n            cursor: pointer;\n            border: 1px solid rgba(251, 146, 60, 0.45);\n            background: rgba(8, 6, 5, 0.94);\n            color: #fed7aa;\n        }\n        .quick-legend-panel {\n            display: none;\n            margin-top: 6px;"),
]


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if "--fab-edge:" not in t:
        print("skip (no fab stack)", path.relative_to(ROOT))
        return
    o = t
    for old, new in REPLACEMENTS:
        if old in t:
            t = t.replace(old, new, 1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
