#!/usr/bin/env python3
"""Sync build-sheet-2026-05-18.py chips arrays from fix_games()."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec_fix = importlib.util.spec_from_file_location(
    "fix_batter_vs_pitcher", ROOT / "fix-batter-vs-pitcher.py"
)
fix = importlib.util.module_from_spec(spec_fix)
spec_fix.loader.exec_module(fix)

spec_build = importlib.util.spec_from_file_location(
    "build0518", ROOT / "build-sheet-2026-05-18.py"
)
build = importlib.util.module_from_spec(spec_build)
spec_build.loader.exec_module(build)

fixed, _ = fix.fix_games([dict(g) for g in build.games])
lookup = {r["name"]: r["chips"] for g in fixed for r in g["rows"]}

path = ROOT / "build-sheet-2026-05-18.py"
text = path.read_text(encoding="utf-8")
updated = 0
for name, chips in lookup.items():
    chips_py = ", ".join(repr(c) for c in chips)
    pat = re.compile(
        rf'(row\({re.escape(name)},.*?,)\s*\[(?:[^\[\]]|"(?:[^"\\]|\\.)*")*\]'
    )
    m = pat.search(text)
    if not m:
        print("skip:", name)
        continue
    repl = f"{m.group(1)} [{chips_py}]"
    if repl != m.group(0):
        text = text[: m.start()] + repl + text[m.end() :]
        updated += 1

path.write_text(text, encoding="utf-8")
print(f"Updated chips on {updated} rows")
