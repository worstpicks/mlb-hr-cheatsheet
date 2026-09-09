from pathlib import Path
import re

checks = {
    "preview/index.html": "2026-08-05",
    "index.html": "2026-08-05",
    "preview/archive/2026-08-04.html": "2026-08-04",
}
for path, expect in checks.items():
    t = Path(path).read_text(encoding="utf-8")
    meta = re.search(r'name="sheet-date" content="([^"]+)"', t)
    hero = re.search(r"(Wednesday|Tuesday|Monday|Thursday|Friday|Saturday|Sunday), August \d+, 2026", t)
    print(path, "meta", meta.group(1) if meta else None, "hero", hero.group(0) if hero else None)
    assert meta and meta.group(1) == expect, path
features = [
    "Homerun Form",
    "straights-history",
    "Damage Window",
    "Goblin's Insight",
    "Daylen Lile",
    "Coby Mayo",
    "MLB Research",
    "Pikkit",
    "bet tracker",
]
t = Path("preview/index.html").read_text(encoding="utf-8")
for s in features:
    assert s in t, f"missing {s}"
    print("OK", s)
# park lines present on game cards
assert t.count("parkPct:") >= 15 or t.count("park_pct") or "net +" in t
print("park/split summary snippets", t.count("net +") + t.count("net -"))
print("ALL GOOD")
