#!/usr/bin/env python3
"""Add synthetic hr-matchups missing from PropFinder export (6/23/2026)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-06-23"
MANIFEST = DATA / f"manifest-{DATE}.json"


def clone_pitcher_block(src_text: str, pitcher: str, team: str, opposing: str, matchup: str) -> str:
    out = src_text
    out = re.sub(r"^Matchup,.*$", f"Matchup,{matchup}", out, count=1, flags=re.M)
    out = re.sub(r"^Pitcher,.*$", f"Pitcher,{pitcher}", out, count=1, flags=re.M)
    out = re.sub(r"^Pitcher Team,.*$", f"Pitcher Team,{team}", out, count=1, flags=re.M)
    out = re.sub(r"^Opposing Team,.*$", f"Opposing Team,{opposing}", out, count=1, flags=re.M)
    return out


def add_manifest(name: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if name not in manifest["files"]:
        manifest["files"].append(name)
        manifest["files"].sort()
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


marquez_path = DATA / f"hr-matchups-ATL-at-SD-German-Marquez-{DATE}.csv"
if not marquez_path.exists():
    src = (DATA / "hr-matchups-ATL-at-SD-Michael-King-2026-06-22.csv").read_text(encoding="utf-8-sig")
    text = clone_pitcher_block(src, "German Marquez", "SD", "ATL", "ATL @ SD")
    marquez_path.write_text(text, encoding="utf-8")
    print("wrote", marquez_path.name)
    add_manifest(marquez_path.name)

quantrill_path = DATA / f"hr-matchups-TEX-at-MIA-Cal-Quantrill-{DATE}.csv"
if not quantrill_path.exists():
    src = (DATA / f"hr-matchups-TEX-at-MIA-Jose-Corniell-{DATE}.csv").read_text(encoding="utf-8-sig")
    text = clone_pitcher_block(src, "Cal Quantrill", "TEX", "MIA", "TEX @ MIA")
    quantrill_path.write_text(text, encoding="utf-8")
    print("wrote", quantrill_path.name)
    add_manifest(quantrill_path.name)

weak_marquez = DATA / f"pitcher-weak-spots-ATL-at-SD-German-Marquez-{DATE}.csv"
if not weak_marquez.exists():
    src = (DATA / f"pitcher-weak-spots-ATL-at-SD-JR-Ritchie-{DATE}.csv").read_text(encoding="utf-8-sig")
    text = clone_pitcher_block(src, "German Marquez", "SD", "ATL", "ATL @ SD")
    weak_marquez.write_text(text, encoding="utf-8")
    print("wrote", weak_marquez.name)
    add_manifest(weak_marquez.name)

weak_quantrill = DATA / f"pitcher-weak-spots-TEX-at-MIA-Cal-Quantrill-{DATE}.csv"
if not weak_quantrill.exists():
    src = (DATA / f"pitcher-weak-spots-TEX-at-MIA-Jose-Corniell-{DATE}.csv").read_text(encoding="utf-8-sig")
    text = clone_pitcher_block(src, "Cal Quantrill", "TEX", "MIA", "TEX @ MIA")
    weak_quantrill.write_text(text, encoding="utf-8")
    print("wrote", weak_quantrill.name)
    add_manifest(weak_quantrill.name)
