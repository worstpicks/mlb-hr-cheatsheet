#!/usr/bin/env python3
"""Refresh MLB Research tab JSON + park factors for a slate date."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from research.mlb_api import build_slate
from research.park_factors import write_park_factors_json
from sheet_data import normalize_sheet_date

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "preview" / "data"
RESEARCH_INDEX = ROOT / "preview" / "research" / "index.html"


def update_research_date_meta(_sheet_date: str = "") -> bool:
    """Clear preview/research/index.html meta research-date (UI defaults to today)."""
    if not RESEARCH_INDEX.is_file():
        return False
    text = RESEARCH_INDEX.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(<meta name="research-date" content=")[^"]*(")',
        r'\g<1>\2',
        text,
        count=1,
    )
    if new_text == text:
        return False
    RESEARCH_INDEX.write_text(new_text, encoding="utf-8")
    return True


def refresh_research_tab(
    sheet_date: str,
    *,
    with_stats: bool = True,
    update_meta: bool = True,
) -> dict[str, Path | str | None]:
    """Build and write research + park-factors JSON for a slate date."""
    sheet_date = normalize_sheet_date(sheet_date)
    payload = build_slate(sheet_date, with_stats=with_stats)
    payload["fetched_at"] = datetime.now().isoformat(timespec="seconds")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    research_path = OUT_DIR / f"research-{sheet_date}.json"
    research_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    pf_path = write_park_factors_json(OUT_DIR, sheet_date)

    if update_meta:
        update_research_date_meta(sheet_date)

    return {
        "sheet_date": sheet_date,
        "research": research_path,
        "park_factors": pf_path,
    }


def _slate_health_report(data: dict) -> list[str]:
    """Coverage counts for the signals the research tab depends on."""
    games = data.get("games") or []
    savant_lookup = data.get("savant_lookup") or {}
    hitters = [
        row
        for g in games
        for side in ("awayLineup", "homeLineup")
        for row in g.get(side) or []
    ]
    pitchers = [g.get(k) for g in games for k in ("awayPitcher", "homePitcher") if g.get(k)]
    n_h = len(hitters)
    n_p = len(pitchers)

    def hit_cov(key: str) -> int:
        # The UI backfills row stats from the embedded savant_lookup at runtime,
        # so count a hitter as covered if either source has the field.
        n = 0
        for r in hitters:
            if (r.get("stats") or {}).get(key) is not None:
                n += 1
                continue
            sav = savant_lookup.get(str(r.get("id"))) or {}
            if sav.get(key) is not None:
                n += 1
        return n

    lines = [
        f"  health: SP throws {sum(1 for p in pitchers if (p.get('throws') or '').strip())}/{n_p}"
        f" · SP arsenal {sum(1 for p in pitchers if p.get('arsenal'))}/{n_p}",
        f"  health: savant xwOBA {hit_cov('xwoba')}/{n_h}"
        f" · mix% {hit_cov('mixPlus')}/{n_h}"
        f" · platoon splits {max(hit_cov('xwobaVsLhp'), hit_cov('xwobaVsRhp'))}/{n_h}",
        f"  health: Due+ {hit_cov('hrLuckDiff')}/{n_h}"
        f" · nearHR {hit_cov('nearHr')}/{n_h}"
        f" · park factors {sum(1 for g in games if g.get('parkHrPct') is not None)}/{len(games)} games",
    ]
    warn = []
    if n_p and sum(1 for p in pitchers if (p.get("throws") or "").strip()) < n_p:
        warn.append("some SPs missing throwing hand (platoon edge degraded)")
    if n_h and hit_cov("mixPlus") < n_h * 0.5:
        warn.append("under 50% mix coverage — check pitch-mix caches")
    if n_h and hit_cov("xwoba") < n_h * 0.5:
        warn.append("under 50% Savant coverage — check Savant CSV fetch")
    for w in warn:
        lines.append(f"  WARN {w}")
    return lines


def print_refresh_summary(result: dict[str, Path | str | None]) -> None:
    sheet_date = result.get("sheet_date")
    research = result.get("research")
    pf = result.get("park_factors")
    print(f"Research tab refreshed for {sheet_date}")
    if isinstance(research, Path):
        n_games = 0
        n_hitters = 0
        health_lines: list[str] = []
        try:
            data = json.loads(research.read_text(encoding="utf-8"))
            n_games = len(data.get("games") or [])
            n_hitters = sum(
                len(g.get("awayLineup") or []) + len(g.get("homeLineup") or [])
                for g in data.get("games") or []
            )
            health_lines = _slate_health_report(data)
        except (json.JSONDecodeError, OSError):
            pass
        print(f"  {research.relative_to(ROOT)} — {n_games} games, {n_hitters} lineup slots")
        for line in health_lines:
            print(line)
    if isinstance(pf, Path):
        print(f"  {pf.relative_to(ROOT)}")
    elif pf is None:
        print("  park-factors: stadium fallback or unavailable (import Ballpark Pal CSV)")
