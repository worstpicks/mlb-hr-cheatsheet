#!/usr/bin/env python3
"""Synthesize 7/16 NYM@PHI hr-matchups from 7/15 same-pitcher exports + today's zones."""
from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATE = "2026-07-16"
SRC_DATE = "2026-07-15"
MANIFEST = DATA / f"manifest-{DATE}.json"

SPECS = [
    {
        "src": f"hr-matchups-NYM-at-PHI-Aaron-Nola-{SRC_DATE}.csv",
        "dst": f"hr-matchups-NYM-at-PHI-Aaron-Nola-{DATE}.csv",
        "pitcher": "Aaron Nola",
    },
    {
        "src": f"hr-matchups-NYM-at-PHI-Christian-Scott-{SRC_DATE}.csv",
        "dst": f"hr-matchups-NYM-at-PHI-Christian-Scott-{DATE}.csv",
        "pitcher": "Christian Scott",
    },
]


def zone_by_batter_pitcher() -> dict[tuple[str, str], str]:
    path = DATA / f"zone-matchups-{DATE}.csv"
    out: dict[tuple[str, str], str] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            score = (row.get("ZoneScore") or "").strip()
            if score:
                out[(row["Batter"].strip(), row["Pitcher"].strip())] = score
    return out


def rewrite_lines(text: str, pitcher: str, zones: dict[tuple[str, str], str]) -> str:
    lines = text.splitlines()
    out: list[str] = []
    header_seen = False
    for line in lines:
        if line.startswith("BATTER,"):
            header_seen = True
            out.append(line)
            continue
        if not header_seen or not line.strip() or line.startswith(",STATS"):
            out.append(line)
            continue
        # batter stat row
        parts = next(csv.reader([line]))
        if not parts:
            out.append(line)
            continue
        batter = parts[0].strip()
        # strip hand suffix like "Juan Soto LHB"
        name = batter
        for suf in (" LHB", " RHB", " SHB"):
            if name.endswith(suf):
                name = name[: -len(suf)].strip()
                break
        # strip leading lineup number
        import re

        name = re.sub(r"^\d+\s+", "", name)
        z = zones.get((name, pitcher))
        if z is not None and len(parts) > 3:
            parts[3] = z
        buf = io.StringIO()
        csv.writer(buf, lineterminator="").writerow(parts)
        out.append(buf.getvalue())
    return "\n".join(out) + "\n"


def main() -> None:
    zones = zone_by_batter_pitcher()
    for spec in SPECS:
        src = DATA / spec["src"]
        if not src.exists():
            raise SystemExit(f"missing source {src}")
        dst = DATA / spec["dst"]
        text = src.read_text(encoding="utf-8-sig")
        dst.write_text(rewrite_lines(text, spec["pitcher"], zones), encoding="utf-8")
        print("wrote", dst.name)

    # Normalize park factors filename already copied; ensure Game key present
    park = DATA / f"ParkFactors_{DATE}.csv"
    if park.exists():
        rows = list(csv.DictReader(park.open(encoding="utf-8-sig")))
        if rows and not (rows[0].get("Game") or "").strip():
            rows[0]["Game"] = "NYM @ PHI"
        # fix date cell if stamped
        if rows and "00:00:00" in (rows[0].get("Date") or ""):
            rows[0]["Date"] = DATE
        with park.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print("park", rows[0].get("Game"), rows[0].get("HR %"))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = set(manifest.get("files", []))
    for spec in SPECS:
        files.add(spec["dst"])
    files.add(f"ParkFactors_{DATE}.csv")
    manifest["files"] = sorted(files)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("manifest updated", len(manifest["files"]), "files")


if __name__ == "__main__":
    main()
