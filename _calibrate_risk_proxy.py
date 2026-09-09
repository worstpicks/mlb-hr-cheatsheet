#!/usr/bin/env python3
"""Compare 8/3 PropFinder HR RISK vs L10 proxy to calibrate."""
from __future__ import annotations

import csv
from pathlib import Path

from _probe_0804_summary import fnum, parse_summary, proxy_risk
from sheet_data import load_pitcher_risk

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def main() -> None:
    risk = load_pitcher_risk(DATA / "hr-targets-overall-2026-08-03.csv")
    overall = parse_summary(DATA / "pitcher-summary-season-l10-2026-08-03.csv")
    if not overall:
        print("no 8/3 summary")
        return
    pairs = []
    for r in overall:
        name = r["PITCHER"]
        actual = risk.get(name.lower())
        if not actual:
            continue
        pred = proxy_risk(r)
        pairs.append((name, actual["overall"], pred, actual["overall"] - pred))
    pairs.sort(key=lambda x: abs(x[3]), reverse=True)
    print(f"n={len(pairs)}")
    mae = sum(abs(d) for *_, d in pairs) / max(1, len(pairs))
    print(f"mae={mae:.3f}")
    for name, a, p, d in pairs[:15]:
        print(f"{name:22} actual={a:+.2f} proxy={p:+.2f} delta={d:+.2f}")


if __name__ == "__main__":
    main()
