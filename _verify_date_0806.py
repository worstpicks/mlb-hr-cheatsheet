from pathlib import Path
import re

checks = {
    "preview/index.html": ("2026-08-06", "Thursday, August 6, 2026"),
    "index.html": ("2026-08-06", "Thursday, August 6, 2026"),
    "preview/archive/2026-08-05.html": ("2026-08-05", "Wednesday, August 5, 2026"),
}
for path, (expect_date, expect_hero) in checks.items():
    t = Path(path).read_text(encoding="utf-8")
    meta = re.search(r'name="sheet-date" content="([^"]+)"', t)
    hero = re.search(
        r"(Wednesday|Tuesday|Monday|Thursday|Friday|Saturday|Sunday), August \d+, 2026",
        t,
    )
    print(path, "meta", meta.group(1) if meta else None, "hero", hero.group(0) if hero else None)
    assert meta and meta.group(1) == expect_date, path
    assert hero and hero.group(0) == expect_hero, path

t = Path("preview/index.html").read_text(encoding="utf-8")
for s in [
    "Homerun Form",
    "straights-history",
    "Damage Window",
    "Goblin's Insight",
    "Derek Hill",
    "Wilyer Abreu",
    "J.T. Realmuto",
    "Gunnar Henderson",
    "Eugenio Suarez",
    "MLB Research",
    "Pikkit",
    "bet tracker",
    "propfinder.app/weather",
]:
    assert s in t, f"missing {s}"
    print("OK", s)

titles = re.findall(r'title:\s*"([^"]+)"', t)
metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', t)
assert len(titles) == 11 and len(metas) == 11
for title, meta in zip(titles, metas):
    s = meta.encode().decode("unicode_escape")
    assert "Park" in s, title
    assert s.count("pitcher-meta") == 2, title
    assert "LHB" in s and "RHB" in s, title
print("OK 11 games park+pitcher splits")
for bum in ("Kohl Drake", "Miles Mikolas", "Ryan Johnson"):
    assert f"{bum} 🧤" in t, bum
    print("OK bum", bum)
print("ALL GOOD")
