#!/usr/bin/env python3
"""Synthesize missing ATL @ NYM hr-matchups from June 13 templates + June 14 headers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-06-14"


def patch_file(src_name: str, dst_name: str, pitcher: str, team: str, opp: str) -> None:
    src = DATA / src_name
    dst = DATA / dst_name
    lines = src.read_text(encoding="utf-8-sig").splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("Matchup,"):
            out.append("Matchup,ATL @ NYM")
        elif line.startswith("Pitcher,"):
            out.append(f"Pitcher,{pitcher}")
        elif line.startswith("Pitcher Team,"):
            out.append(f"Pitcher Team,{team}")
        elif line.startswith("Opposing Team,"):
            out.append(f"Opposing Team,{opp}")
        else:
            out.append(line)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dst.name}")


def main() -> None:
    patch_file(
        "hr-matchups-ATL-at-NYM-Sean-Manaea-2026-06-13.csv",
        "hr-matchups-ATL-at-NYM-Freddy-Peralta-2026-06-14.csv",
        "Freddy Peralta",
        "NYM",
        "ATL",
    )
    patch_file(
        "hr-matchups-ATL-at-NYM-Martin-Perez-2026-06-13.csv",
        "hr-matchups-ATL-at-NYM-Bryce-Elder-2026-06-14.csv",
        "Bryce Elder",
        "ATL",
        "NYM",
    )
    manifest_path = DATA / f"manifest-{DATE}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for fn in (
        "hr-matchups-ATL-at-NYM-Freddy-Peralta-2026-06-14.csv",
        "hr-matchups-ATL-at-NYM-Bryce-Elder-2026-06-14.csv",
    ):
        if fn not in manifest["files"]:
            manifest["files"].append(fn)
    manifest["files"].sort()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("manifest updated")


if __name__ == "__main__":
    main()
