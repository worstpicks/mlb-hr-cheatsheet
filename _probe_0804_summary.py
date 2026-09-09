#!/usr/bin/env python3
"""Probe 8/4 pitcher summaries and estimate HR RISK proxy from L10 stats."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def parse_summary(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    header = None
    rows: list[dict] = []
    for line in text.splitlines():
        if line.startswith("TIME,") and "PITCHER" in line:
            header = next(csv.reader([line]))
            continue
        if header is None:
            continue
        row = next(csv.reader([line]))
        if len(row) < 3 or not row[1]:
            continue
        if row[0] in ("Range", "Dates", "Games", "Split", "") or row[1] in (
            "PITCHER",
            "STATS",
        ):
            continue
        d = dict(zip(header, row + [""] * max(0, len(header) - len(row))))
        rows.append(d)
    return rows


def fnum(x: str | None) -> float | None:
    x = (x or "").replace("%", "").strip()
    if not x or x == "-":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def proxy_risk(row: dict) -> float:
    """Rough z-ish proxy from L10 contact/HR markers (not PropFinder official)."""
    hr9 = fnum(row.get("HR/9")) or 1.2
    barrel = fnum(row.get("BARREL%")) or 8.0
    hrfb = fnum(row.get("HR/FB%")) or 12.0
    hh = fnum(row.get("HH%")) or 38.0
    fb = fnum(row.get("FB%")) or 25.0
    meat = fnum(row.get("MEATBALL%")) or 7.0
    # League-ish baselines
    score = (
        (hr9 - 1.2) * 0.9
        + (barrel - 8.0) * 0.08
        + (hrfb - 12.0) * 0.04
        + (hh - 38.0) * 0.03
        + (fb - 25.0) * 0.02
        + (meat - 7.0) * 0.05
    )
    return round(score, 2)


def main() -> None:
    overall = parse_summary(DATA / "pitcher-summary-season-l10-2026-08-04.csv")
    lhb = {r["PITCHER"]: r for r in parse_summary(DATA / "pitcher-summary-vslhb-l10-2026-08-04.csv")}
    rhb = {r["PITCHER"]: r for r in parse_summary(DATA / "pitcher-summary-vsrhb-l10-2026-08-04.csv")}
    print("counts", len(overall), len(lhb), len(rhb))
    ranked = sorted(overall, key=lambda r: proxy_risk(r), reverse=True)
    for r in ranked:
        name = r["PITCHER"]
        o = proxy_risk(r)
        vl = proxy_risk(lhb[name]) if name in lhb else o
        vr = proxy_risk(rhb[name]) if name in rhb else o
        print(
            f"{name:22} risk~{o:+.2f} LHB~{vl:+.2f} RHB~{vr:+.2f} "
            f"HR9={r.get('HR/9')} BAR={r.get('BARREL%')} BF={r.get('BF')} t={r.get('TIME')}"
        )


if __name__ == "__main__":
    main()
