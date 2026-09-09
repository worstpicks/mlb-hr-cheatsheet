#!/usr/bin/env python3
"""Batters Won: full-width section under slate (not narrow scroll box)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

OLD_BLOCK = """        .batters-won-section {
            margin: 14px 0 0;
            max-width: min(520px, 100%);
        }
        .batters-won-section[hidden] {
            display: none !important;
        }
        .batters-won-panel {
            border-color: rgba(34, 197, 94, 0.45);
            background: linear-gradient(145deg, rgba(6, 78, 59, 0.35) 0%, rgba(12, 28, 18, 0.97) 52%, rgba(22, 10, 14, 0.96) 100%);
            padding: 12px 14px;
        }
        .batters-won-panel h2 {
            color: #86efac;
            font-size: 1.05rem;
            margin: 0 0 0.35rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .batters-won-lede {
            margin: 0 0 0.65rem;
            color: var(--wpz-color-paragraph);
            font-size: 0.88rem;
            line-height: 1.35;
        }
        .batters-won-list {
            list-style: none;
            margin: 0;
            padding: 0;
            display: grid;
            gap: 6px;
            max-height: min(42vh, 320px);
            overflow: auto;
        }
        .batters-won-item {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 2px 10px;
            align-items: center;
            padding: 8px 10px;
            border-radius: 10px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(34, 197, 94, 0.25);
        }
        .batters-won-item--fav {
            border-color: rgba(244, 63, 94, 0.5);
            box-shadow: inset 3px 0 0 rgba(244, 63, 94, 0.85);
        }
        .batters-won-name {
            font-weight: 800;
            color: #ecfdf5;
            font-size: 0.92rem;
        }
        .batters-won-meta {
            grid-column: 1;
            font-size: 0.72rem;
            color: rgba(226, 232, 240, 0.75);
        }
        .batters-won-meta small {
            opacity: 0.9;
        }
        .batters-won-score {
            grid-row: 1 / span 2;
            grid-column: 2;
            font-size: 1rem;
            color: #86efac;
        }
        html.theme-light .batters-won-panel {
            border-color: rgba(22, 163, 74, 0.45);
            background: linear-gradient(145deg, rgba(220, 252, 231, 0.9) 0%, #fff 48%, #fef3c7 100%);
        }
        html.theme-light .batters-won-panel h2 { color: #15803d; }
        html.theme-light .batters-won-item {
            background: rgba(255, 255, 255, 0.85);
            border-color: rgba(22, 163, 74, 0.35);
        }
        html.theme-light .batters-won-name { color: #14532d; }
        html.theme-light .batters-won-meta { color: #334155; }
        html.theme-light .batters-won-score { color: #15803d; }
        @media (max-width: 640px) {
            .batters-won-section { max-width: 100%; }
        }"""

NEW_BLOCK = """        .batters-won-section {
            padding: 14px;
            margin: 0;
            background: linear-gradient(135deg, rgba(6, 48, 32, 0.94) 0%, rgba(10, 17, 28, 0.96) 55%, rgba(14, 10, 20, 0.95) 100%);
            border-top: 1px solid rgba(34, 197, 94, 0.28);
            border-bottom: 1px solid rgba(251, 146, 60, 0.14);
            min-width: 0;
        }
        .batters-won-section[hidden] {
            display: none !important;
        }
        .batters-won-panel {
            border-color: rgba(34, 197, 94, 0.45);
            background: rgba(15, 23, 42, 0.5);
            padding: 14px;
        }
        .batters-won-panel h2 {
            color: #86efac;
            font-size: inherit;
            margin: 0 0 0.5rem;
            letter-spacing: 0.7px;
            text-transform: uppercase;
        }
        .batters-won-lede {
            margin: 0 0 12px;
            color: var(--wpz-color-paragraph);
            font-size: 0.92rem;
            line-height: 1.45;
            max-width: 72ch;
        }
        .batters-won-list {
            list-style: none;
            margin: 0;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
            gap: 10px;
        }
        .batters-won-item {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 2px 12px;
            align-items: center;
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(34, 197, 94, 0.28);
            min-width: 0;
        }
        .batters-won-item--fav {
            border-color: rgba(244, 63, 94, 0.5);
            box-shadow: inset 3px 0 0 rgba(244, 63, 94, 0.85);
        }
        .batters-won-name {
            font-weight: 800;
            color: #ecfdf5;
            font-size: 0.95rem;
        }
        .batters-won-meta {
            grid-column: 1;
            font-size: 0.76rem;
            color: rgba(226, 232, 240, 0.78);
        }
        .batters-won-meta small {
            opacity: 0.9;
        }
        .batters-won-score {
            grid-row: 1 / span 2;
            grid-column: 2;
            font-size: 1.1rem;
            color: #86efac;
        }
        html.theme-light .batters-won-section {
            background: linear-gradient(135deg, #ecfdf5 0%, #f1f5f9 50%, #e8eef7 100%);
            border-top-color: rgba(22, 163, 74, 0.35);
        }
        html.theme-light .batters-won-panel {
            border-color: rgba(22, 163, 74, 0.45);
            background: rgba(255, 255, 255, 0.72);
        }
        html.theme-light .batters-won-panel h2 { color: #15803d; }
        html.theme-light .batters-won-item {
            background: rgba(255, 255, 255, 0.9);
            border-color: rgba(22, 163, 74, 0.35);
        }
        html.theme-light .batters-won-name { color: #14532d; }
        html.theme-light .batters-won-meta { color: #334155; }
        html.theme-light .batters-won-score { color: #15803d; }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_BLOCK in t:
        t = t.replace(OLD_BLOCK, NEW_BLOCK, 1)
    if ".intro, .summary-section, .games-section { padding: 10px; }" in t:
        t = t.replace(
            ".intro, .summary-section, .games-section { padding: 10px; }",
            ".intro, .summary-section, .games-section, .batters-won-section { padding: 10px; }",
            1,
        )
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("expanded", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
