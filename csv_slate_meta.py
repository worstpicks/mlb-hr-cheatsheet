#!/usr/bin/env python3
"""Derive slate game SP pairs and batter rows from hr-matchups CSV exports."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sheet_data import DATA_DIR, load_pitcher_risk, hr_targets_csv

MATCHUP_RE = re.compile(
    r"hr-matchups-([A-Z]{2,3})-at-([A-Z]{2,3})-(.+)-(\d{4}-\d{2}-\d{2})\.csv$",
    re.I,
)
LINEUP_PREFIX_RE = re.compile(r"^\d+\s+")


def normalize_batter_name(raw: str) -> str:
    """Strip PropFinder lineup slot prefixes and handedness suffixes from batter labels."""
    name = raw.strip()
    name = re.sub(r"\s+(LHB|RHB|SHB)\s*$", "", name, flags=re.I).strip()
    name = LINEUP_PREFIX_RE.sub("", name).strip()
    return name


def name_lookup_key(name: str) -> str:
    """Canonical lookup key for prop-list ↔ CSV batter matching."""
    key = normalize_batter_name(name).lower()
    key = key.replace(".", "")
    key = re.sub(r"\s+", " ", key).strip()
    return key


def manifest_matchup_files(sheet_date: str, data_dir: Path | None = None) -> list[Path]:
    data = data_dir or DATA_DIR
    manifest_path = data / f"manifest-{sheet_date}.json"
    if not manifest_path.exists():
        return sorted(data.glob(f"hr-matchups-*-{sheet_date}.csv"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names = {n for n in manifest.get("files", []) if n.startswith("hr-matchups-")}
    return sorted(data / n for n in names if (data / n).exists())


def parse_matchup_filename(path: Path) -> dict | None:
    m = MATCHUP_RE.match(path.name)
    if not m:
        return None
    away, home, slug, date = m.group(1).upper(), m.group(2).upper(), m.group(3), m.group(4)
    pitcher = slug.replace("-", " ")
    pitcher = re.sub(r"\bJ T\b", "J.T.", pitcher, flags=re.I)
    pitcher = " ".join(p.title() if p.lower() not in ("de", "la", "di") else p.lower() for p in pitcher.split())
    if pitcher.lower() == "j.t. ginn":
        pitcher = "J.T. Ginn"
    return {"away": away, "home": home, "pitcher": pitcher, "path": path, "date": date}


def read_matchup_header(path: Path) -> dict:
    out = {"matchup": "", "pitcher": "", "pitcher_team": "", "opposing_team": ""}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0] == "Matchup":
                out["matchup"] = row[1].strip()
            elif len(row) >= 2 and row[0] == "Pitcher":
                out["pitcher"] = row[1].strip()
            elif len(row) >= 2 and row[0] == "Pitcher Team":
                out["pitcher_team"] = row[1].strip().upper()
            elif len(row) >= 2 and row[0] == "Opposing Team":
                out["opposing_team"] = row[1].strip().upper()
            if out["pitcher"] and out["pitcher_team"]:
                break
    return out


def read_batter_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if row and row[0] == "BATTER":
                header = [c.strip() for c in row]
                continue
            if not header or not row or not row[0]:
                continue
            if row[0].startswith("SPLIT") or row[0] == "BATTER":
                continue
            data = dict(zip(header, row))
            name_raw = row[0].strip()
            hand_m = re.search(r"\b(LHB|RHB|SHB)\b", name_raw)
            hand = {"LHB": "L", "RHB": "R", "SHB": "S"}.get(hand_m.group(1) if hand_m else "", "?")
            name = normalize_batter_name(name_raw)
            odds_raw = data.get("ODDS", "").strip()
            odds = odds_raw if odds_raw and odds_raw.upper() != "N/A" else "N/A"
            if odds_raw.startswith("+") or odds_raw.startswith("-"):
                odds = odds_raw
            def num(key):
                v = data.get(key, "").strip()
                try:
                    return float(v)
                except ValueError:
                    return None
            rows.append(
                {
                    "name": name,
                    "hand": hand,
                    "odds": odds,
                    "hr": int(num("HR") or 0),
                    "near": int(num("NEAR HR") or 0),
                    "ev": num("EV"),
                    "barrel": num("BARREL%"),
                }
            )
    return rows


def derive_games_from_csv(sheet_date: str, data_dir: Path | None = None) -> list[dict]:
    files = manifest_matchup_files(sheet_date, data_dir)
    by_game: dict[str, dict] = {}
    for path in files:
        meta = parse_matchup_filename(path)
        if not meta or meta["date"] != sheet_date:
            continue
        hdr = read_matchup_header(path)
        key = f"{meta['away']} @ {meta['home']}"
        gm = by_game.setdefault(
            key,
            {
                "key": key,
                "away": meta["away"],
                "home": meta["home"],
                "away_sp": None,
                "home_sp": None,
                "away_sp_full": None,
                "home_sp_full": None,
                "batters": {},
            },
        )
        sp_last = hdr["pitcher"].split()[-1]
        team = hdr["pitcher_team"]
        if team == meta["away"]:
            gm["away_sp"] = sp_last
            gm["away_sp_full"] = hdr["pitcher"]
        elif team == meta["home"]:
            gm["home_sp"] = sp_last
            gm["home_sp_full"] = hdr["pitcher"]
        for b in read_batter_rows(path):
            gm["batters"][name_lookup_key(b["name"])] = {
                **b,
                "vs": sp_last,
                "vs_full": hdr["pitcher"],
                "file": path.name,
            }

    # When two SPs share a last name (e.g. Grayson/Eduardo Rodriguez), chips must
    # use the full name so resolve_pitcher() can score splits/risk correctly.
    last_counts: dict[str, int] = {}
    for gm in by_game.values():
        for full in (gm.get("away_sp_full"), gm.get("home_sp_full")):
            if not full or full == "TBD":
                continue
            last = full.split()[-1]
            last_counts[last] = last_counts.get(last, 0) + 1
    for gm in by_game.values():
        for batter in gm["batters"].values():
            last = (batter.get("vs") or "").strip()
            full = (batter.get("vs_full") or last).strip()
            if last and last_counts.get(last, 0) > 1 and full:
                batter["vs"] = full

    risk = load_pitcher_risk(hr_targets_csv(sheet_date) or Path("__missing__"))
    games = []
    for key in sorted(by_game):
        gm = by_game[key]
        if not gm["away_sp"] and gm["home_sp"]:
            gm["away_sp"] = "TBD"
            gm["away_sp_full"] = "TBD"
        elif gm["away_sp"] and not gm["home_sp"]:
            gm["home_sp"] = "TBD"
            gm["home_sp_full"] = "TBD"
        elif not gm["away_sp"] or not gm["home_sp"]:
            raise SystemExit(f"Incomplete SP pair for {key}: {gm}")
        away_r = risk.get(gm["away_sp_full"].lower()) or risk.get(gm["away_sp"].lower())
        home_r = risk.get(gm["home_sp_full"].lower()) or risk.get(gm["home_sp"].lower())
        bum_away = away_r and away_r["overall"] >= 1.0
        bum_home = home_r and home_r["overall"] >= 1.0
        away_tag = f"{gm['away_sp_full']} 🧤" if bum_away else gm["away_sp_full"]
        home_tag = f"{gm['home_sp_full']} 🧤" if bum_home else gm["home_sp_full"]
        gm["title"] = f"{key} - {away_tag} (R, {gm['away']}) vs {home_tag} (R, {gm['home']})"
        gm["away_risk"] = away_r["overall"] if away_r else None
        gm["home_risk"] = home_r["overall"] if home_r else None
        games.append(gm)
    return games


def opposing_sp_for_team(gm: dict, team: str) -> str:
    team = team.upper()
    if team == gm["away"]:
        return gm["home_sp"]
    if team == gm["home"]:
        return gm["away_sp"]
    raise KeyError(f"{team} not in {gm['key']}")


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else "2026-05-30"
    for g in derive_games_from_csv(date):
        print(f"{g['key']:12} {g['away_sp']:12} vs {g['home_sp']}")
