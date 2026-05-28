#!/usr/bin/env python3
import importlib.util
import re
from pathlib import Path

idx = Path("preview/index.html").read_text(encoding="utf-8")
rows = re.findall(
    r'name: "([^"]+)".*?score: (\d+).*?emojis: "([^"]+)".*?chips: \[(.*?)\]',
    idx,
    re.DOTALL,
)

print("=== 100+ mph EV rocket (🚀) rows ===")
for name, score, em, _chips in rows:
    if "🚀" in em:
        print(f"  {name}  score={score}  {em}")

spec = importlib.util.spec_from_file_location("b", Path("build-sheet-2026-05-28.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print("\n=== Bum mound emoji coverage ===")
missing = []
for game in m.games:
    for row in game["rows"]:
        chip = row["chips"][0].replace("vs ", "")
        if chip in m.BUM_PITCHERS:
            em = row["emojis"]
            if not all(x in em for x in ("⚾", "🕊️", "🧤")):
                missing.append((row["name"], chip, em))

if missing:
    for item in missing:
        print(" MISSING:", item)
else:
    print("  All vs-bum rows have ⚾ 🕊️ 🧤")

print("\n=== Top 5 holistic vs row scores ===")
top5 = [
    ("Brandon Lowe", 96),
    ("Yohendrick Pinango", 93),
    ("Yordan Alvarez", 92),
    ("Byron Buxton", 90),
    ("Brandon Nimmo", 88),
]
scores = {name: int(score) for name, score, *_ in rows}
for name, expected in top5:
    key = next(k for k in scores if k.startswith(name))
    ok = "OK" if scores[key] == expected else f"MISMATCH got {scores[key]}"
    print(f"  {ok}  {name} -> {expected}")
