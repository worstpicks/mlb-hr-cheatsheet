#!/usr/bin/env python3
"""Regenerate games block and sync preview + root index."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b", ROOT / "build-sheet-2026-05-28.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

block = m.emit_games_js(m.games)
(ROOT / "_games-0528.txt").write_text(block, encoding="utf-8")

fav_set = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f'                "{name}"' for name in sorted(m.FAVS))
    + "\n            ]);"
)

for path in (ROOT / "preview/index.html", ROOT / "index.html"):
    text = path.read_text(encoding="utf-8")
    start = text.find("const games = [")
    end = text.find("];\n\n            const grid", start)
    if start < 0 or end < 0:
        raise SystemExit(f"markers not found in {path}")
    text = text[:start] + block + "\n\n            const grid" + text[end + len("];\n\n            const grid") :]
    text = re.sub(
        r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);",
        fav_set,
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")
    print("synced", path.relative_to(ROOT))
