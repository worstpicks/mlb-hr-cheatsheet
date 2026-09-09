#!/usr/bin/env python3
import csv
from pathlib import Path

rows = list(csv.DictReader(Path("data/zone-matchups-2026-07-31.csv").open(encoding="utf-8-sig")))
pitchers = sorted({(r.get("Pitcher") or "").strip() for r in rows})
print("zone pitchers", len(pitchers))
for name in [
    "Michael Wacha",
    "Foster Griffin",
    "Ranger Suarez",
    "Yoshinobu Yamamoto",
    "Jeffrey Springs",
    "Carson Whisenhunt",
    "German Marquez",
    "Brian Keller",
]:
    zs = [r for r in rows if (r.get("Pitcher") or "").strip() == name]
    print(name, "zone", len(zs), [r.get("Batter") for r in zs[:10]])

print("Neill search:")
for r in rows:
    b = r.get("Batter") or ""
    if "Neill" in b or "ONeil" in b:
        print(" ", b, "vs", r.get("Pitcher"))
