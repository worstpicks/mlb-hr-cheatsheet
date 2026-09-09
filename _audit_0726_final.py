#!/usr/bin/env python3
"""Full pre-push audit for 2026-07-26 sheet."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
root_html = (ROOT / "index.html").read_text(encoding="utf-8")
arch = (ROOT / "preview" / "archive" / "2026-07-25.html").read_text(encoding="utf-8")
errors: list[str] = []
warns: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


# --- DATE (critical — failed last time) ---
for label, doc in [("preview", html), ("root", root_html)]:
    m = re.search(r'name="sheet-date" content="([^"]+)"', doc)
    if not m or m.group(1) != "2026-07-26":
        err(f"{label}: sheet-date={m.group(1) if m else None}")
    if "Sunday, July 26, 2026 — Worst Pickz HR cheat sheet" not in doc:
        err(f"{label}: hero missing Sunday, July 26, 2026")
    if "July 25, 2026 — Worst Pickz" in doc or "July 24, 2026 — Worst Pickz" in doc:
        err(f"{label}: stale prior-day hero date still present")
    if "Saturday, July 25" in doc or "Friday, July 24" in doc:
        err(f"{label}: wrong weekday/date in body")

manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
top = manifest["sheets"][0]
if top["date"] != "2026-07-26" or "July 26" not in top["label"]:
    err(f"manifest current wrong: {top}")
arch_entry = next(s for s in manifest["sheets"] if s["date"] == "2026-07-25")
if arch_entry["label"] != "July 25, 2026":
    err(f"archive 7/25 label wrong: {arch_entry['label']}")

# --- props / emojis ---
fav = len(re.findall(r'emojis: "[^"]*⭐', html))
gem = len(re.findall(r'emojis: "[^"]*💎', html))
print(f"fav={fav} gem={gem}")
if fav != 17:
    err(f"expected 17 favorites, got {fav}")
if gem != 1:
    err(f"expected 1 gem, got {gem}")

# --- bums from targets ---
targets = ROOT / "data" / "hr-targets-overall-2026-07-26.csv"
bums = []
with targets.open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        # skip header-ish rows
        pitcher = (row.get("PITCHER") or "").strip()
        risk_s = (row.get("HR RISK") or "").strip()
        if not pitcher or not risk_s:
            continue
        try:
            risk = float(risk_s)
        except ValueError:
            continue
        if risk >= 0.95:
            bums.append((pitcher, risk))
bums.sort(key=lambda x: -x[1])
print("BUMS >= 0.95:")
for name, risk in bums:
    print(f"  {name} {risk:+.2f}")
    if not re.search(rf"{re.escape(name)}[^\n\"]{{0,40}}🧤", html):
        err(f"bum {name} ({risk:+.2f}) missing 🧤 in game title")

# --- gameMeta park + splits ---
metas = re.findall(
    r'title:\s*"([^"]+)"\s*,\s*startTime:[^,]*,\s*gameMeta:\s*"([^"]*)"',
    html,
)
print(f"gameMeta blocks: {len(metas)}")
if len(metas) != 15:
    err(f"expected 15 gameMeta blocks, got {len(metas)}")
for title, meta in metas:
    print(f"  {title[:70]}")
    print(f"    {meta[:180]}")
    if "Park" not in meta:
        err(f"{title}: missing Park %")
    if "LHB" not in meta or "RHB" not in meta:
        err(f"{title}: missing LHB/RHB park")
    # pitcher overall / hand splits in meta
    if "overall" not in meta.lower():
        warn(f"{title}: no 'overall' pitcher split text (may still have LHB/RHB %)")

park_lhb = html.count("parkLhbPct")
park_rhb = html.count("parkRhbPct")
if park_lhb < 15 or park_rhb < 15:
    err(f"parkLhbPct={park_lhb} parkRhbPct={park_rhb} (need >=15)")

# --- LHP hands ---
for sp, hand in [
    ("Parker Messick", "L"),
    ("Kohl Drake", "L"),
    ("Jeffrey Springs", "L"),
    ("Kyle Freeland", "L"),
    ("Andrew Abbott", "L"),
    ("Ranger Suarez", "L"),
    ("Framber Valdez", "L"),
    ("Carson Whisenhunt", "L"),
    ("Cristopher Sanchez", "L"),
]:
    if f"{sp} ({hand}" not in html and f"{sp} ({hand}," not in html:
        # titles use "Parker Messick (L, CLE)"
        if not re.search(rf"{re.escape(sp)} \({hand}", html):
            err(f"{sp} not marked ({hand}) in sheet")

# --- features vs 7/25 archive ---
features = [
    "Homerun Form",
    "Damage Window",
    "Straights of the Day",
    "Goblin",
    "Favorite 3",
    "Top 5 HR Tickets",
    "Weather Heavy",
    "Longshot",
    "Hits",
    "research",
    "gambly",
    "Pikkit",
    "bet tracker",
]
print("\nFeature parity:")
for feat in features:
    now = feat.lower() in html.lower()
    then = feat.lower() in arch.lower()
    status = "OK" if now else "MISSING"
    print(f"  [{status}] {feat} (7/25={then})")
    if then and not now:
        err(f"feature missing vs 7/25: {feat}")

# --- research / park JSON ---
for p in [
    ROOT / "preview/data/research-2026-07-26.json",
    ROOT / "preview/data/park-factors-2026-07-26.json",
]:
    if not p.is_file():
        err(f"missing {p.name}")

# --- stale SPs ---
for stale in ["Travis Adams", "Tim Mayza", "Mike Paredes"]:
    if stale in html:
        err(f"stale SP present: {stale}")

# --- zone ---
if len(re.findall(r"zoneScore", html)) < 40:
    err("low zoneScore presence")

print("\nWARNINGS:")
for w in warns:
    print(" WARN:", w)
print("\nERRORS:" if errors else "\nPASS")
for e in errors:
    print(" ERR:", e)
raise SystemExit(1 if errors else 0)
