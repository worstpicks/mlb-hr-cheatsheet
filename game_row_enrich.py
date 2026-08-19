#!/usr/bin/env python3
"""Enrich game rows with form/air/contact fields and emit JS for the cheat sheet."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from csv_slate_meta import derive_games_from_csv, name_lookup_key, read_batter_rows
from note_compact import compact_note
from csv_slate_meta import manifest_matchup_files, parse_matchup_filename
from sheet_data import format_pitcher_risk_pct, load_pitcher_risk, resolve_pitcher
from zone_matchups import load_zone_lookup, lookup_zone_row

ROOT = Path(__file__).resolve().parent

# Sheet title keys that differ from ParkFactors CSV Game column.
# Reserved slot in the weather lookup holding ParkFactors rows that shipped without
# a Game label, indexed by first pitch. Never a real game key.
_UNKEYED_BY_TIME = "__by_time__"

TITLE_WEATHER_KEY_ALIASES = {
    "MIA @ WSH": "MIA @ WAS",
    "KC @ WSH": "KC @ WAS",
    "PHI @ WSH": "PHI @ WAS",
    "WSH @ BAL": "WAS @ BAL",
    "WSH @ BOS": "WAS @ BOS",
    "WSH @ ATH": "WAS @ ATH",
    "WSH @ COL": "WAS @ COL",
    "CWS @ BAL": "CHW @ BAL",
    "CWS @ TOR": "CHW @ TOR",
    "CWS @ TEX": "CHW @ TEX",
    "CWS @ TB": "CHW @ TB",
    "TB @ CWS": "TB @ CHW",

    "KC @ CWS": "KC @ CHW",
    "CLE @ CWS": "CLE @ CHW",
    "CWS @ MIN": "CHW @ MIN",
    "CWS @ NYY": "CHW @ NYY",
    "CWS @ CLE": "CHW @ CLE",
    "BOS @ CWS": "BOS @ CHW",
    "CWS @ BOS": "CHW @ BOS",
    "PIT @ WSH": "PIT @ WAS",
    "HOU @ WSH": "HOU @ WAS",
    "ARI @ WSH": "ARI @ WAS",
    "CIN @ WSH": "CIN @ WAS",
    "CIN @ WAS": "CIN @ WAS",
    "CHC @ WSH": "CHC @ WAS",
    "CHC @ WAS": "CHC @ WAS",
    "CIN @ CWS": "CIN @ CHW",
    "CIN @ CHW": "CIN @ CHW",
    "HOU @ CWS": "HOU @ CHW",
    "ATH @ CWS": "ATH @ CHW",
    "DET @ CWS": "DET @ CHW",
    "NYY @ CWS": "NYY @ CHW",
    "SEA @ CWS": "SEA @ CHW",
    "TEX @ CWS": "TEX @ CHW",
    "MIN @ CWS": "MIN @ CHW",
    "LAA @ CWS": "LAA @ CHW",
    "WSH @ ATL": "WAS @ ATL",
    "WAS @ ATL": "WAS @ ATL",
    "WSH @ PHI": "WAS @ PHI",
    "WAS @ PHI": "WAS @ PHI",
}

# Only two codes actually differ between the sheet and Ballpark Pal. The map above
# enumerates opponent pairs, so every matchup combination that had not been seen
# before missed and the game silently lost its park row. Normalize each side of the
# key instead, and keep the explicit map ahead of it for genuine exceptions.
WEATHER_TEAM_CODE_ALIASES = {"CWS": "CHW", "WSH": "WAS"}


def alias_weather_game_key(key: str) -> str:
    explicit = TITLE_WEATHER_KEY_ALIASES.get(key)
    if explicit:
        return explicit
    m = re.match(r"^([A-Z]{2,3})\s*@\s*([A-Z]{2,3})\s*(.*)$", (key or "").strip())
    if not m:
        return key
    away = WEATHER_TEAM_CODE_ALIASES.get(m.group(1), m.group(1))
    home = WEATHER_TEAM_CODE_ALIASES.get(m.group(2), m.group(2))
    suffix = f" {m.group(3)}" if m.group(3) else ""
    return f"{away} @ {home}{suffix}"

# PropFinder / sheet venue labels -> Ballpark Pal BALLPARK column.
VENUE_BALLPARK_ALIASES = {
    "american family fld": "american family field",
    "great american bp": "great american ball park",
    "oriole park": "oriole park at camden yards",
}


def _num(val: str | None) -> float | None:
    if val is None:
        return None
    v = str(val).strip().replace("%", "")
    if not v or v in ("-", "N/A"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def load_batter_stat_lookup(sheet_date: str) -> dict[str, dict]:
    """name_lookup_key -> stat dict from hr-matchups CSVs."""
    lookup: dict[str, dict] = {}
    for path in manifest_matchup_files(sheet_date, ROOT / "data"):
        meta = parse_matchup_filename(path)
        if not meta or meta["date"] != sheet_date:
            continue
        for b in read_batter_rows(path):
            key = name_lookup_key(b["name"])
            prev = lookup.get(key)
            if prev and (prev.get("hr") or 0) >= (b.get("hr") or 0):
                continue
            lookup[key] = {
                "hr": b.get("hr") or 0,
                "near": b.get("near") or 0,
                "ev": b.get("ev") or 0.0,
                "barrel": b.get("barrel"),
            }
            lookup[key].update(_read_extra_statcast(path, b["name"]))
            if lookup[key].get("barrel") is None and b.get("barrel") is not None:
                lookup[key]["barrel"] = b.get("barrel")
    return lookup


HIGH_GB_PCT = 52.0
LOW_GB_PCT = 29.0
HIGH_HH_PCT = 50.0
LOW_HH_PCT = 30.0


def gb_signal(gb_pct: float | None) -> str | None:
    if gb_pct is None:
        return None
    if gb_pct >= HIGH_GB_PCT:
        return "high"
    if gb_pct <= LOW_GB_PCT:
        return "low"
    return None


def hh_signal(hh_pct: float | None) -> str | None:
    if hh_pct is None:
        return None
    if hh_pct >= HIGH_HH_PCT:
        return "high"
    if hh_pct <= LOW_HH_PCT:
        return "low"
    return None


def _read_extra_statcast(path: Path, batter_name: str) -> dict:
    out: dict = {
        "fb_pct": None,
        "pull_air": None,
        "whiff_pct": None,
        "k_pct": None,
        "hh_pct": None,
        "gb_pct": None,
    }
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if row and row[0] == "BATTER":
                header = [c.strip() for c in row]
                continue
            if not header or not row or not row[0]:
                continue
            raw = row[0].strip()
            if name_lookup_key(raw) != name_lookup_key(batter_name):
                continue
            data = dict(zip(header, row))
            out["fb_pct"] = _num(data.get("FB%"))
            out["pull_air"] = _num(data.get("PULLAIR%"))
            out["whiff_pct"] = _num(data.get("WHIFF%"))
            out["k_pct"] = _num(data.get("K%"))
            out["hh_pct"] = _num(data.get("HH%"))
            out["gb_pct"] = _num(data.get("GB%"))
            out["barrel_pct"] = _num(data.get("BARREL%"))
            break
    return out


def pitcher_summary_path(split: str, sheet_date: str) -> Path | None:
    """Locate a pitcher-summary export regardless of its window suffix.

    PropFinder names these by the window it was exported with (`-l10-`, `-season-`),
    so pinning one suffix silently drops HR/9 from every game header when the export
    window changes.
    """
    data = ROOT / "data"
    exact = data / f"pitcher-summary-{split}-l10-{sheet_date}.csv"
    if exact.is_file():
        return exact
    matches = sorted(data.glob(f"pitcher-summary-{split}-*-{sheet_date}.csv"))
    return matches[0] if matches else None


def load_pitcher_hr9_lookup(sheet_date: str) -> dict[str, float]:
    path = pitcher_summary_path("season", sheet_date)
    if path is None:
        print(f"WARN: no pitcher-summary-season-*-{sheet_date}.csv — HR/9 will be blank")
        return {}
    lookup: dict[str, float] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 14 or row[0] in ("", "Split", "Range", "Dates", "Games", ",STATS"):
                continue
            if row[1] == "PITCHER":
                continue
            pitcher = (row[1] or "").strip()
            hr9 = _num(row[12] if len(row) > 12 else None)
            if pitcher and hr9 is not None:
                lookup[pitcher.lower()] = hr9
                lookup[pitcher.split()[-1].lower()] = hr9
    return lookup


def load_pitcher_rates_from_matchups(sheet_date: str) -> dict[str, dict]:
    """Measured Season / vsLHB / vsRHB rates from each hr-matchups pitcher block.

    PropFinder omits late-added starters from hr-targets-overall and pitcher-summary
    but still ships their own matchup export, which carries the same stat block. This
    is the fallback so a game header never loses a starter entirely.
    """
    out: dict[str, dict] = {}
    for path in sorted((ROOT / "data").glob(f"hr-matchups-*-{sheet_date}.csv")):
        pitcher = ""
        header: list[str] | None = None
        splits: dict[str, dict] = {}
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("Pitcher,"):
                pitcher = line.split(",", 1)[1].strip()
                continue
            if line.startswith("SPLIT,"):
                header = next(csv.reader([line]))
                continue
            if header and line.split(",", 1)[0].strip() in ("Season", "vsLHB", "vsRHB"):
                row = next(csv.reader([line]))
                splits[row[0].strip()] = dict(zip(header, row))
                continue
            if line.startswith("BATTER,"):
                break
        if not pitcher or "Season" not in splits:
            continue

        def rate(split: str, col: str) -> float | None:
            return _num((splits.get(split) or {}).get(col))

        entry = {
            "pitcher": pitcher,
            "hr9": rate("Season", "HR/9"),
            "hr9_lhb": rate("vsLHB", "HR/9"),
            "hr9_rhb": rate("vsRHB", "HR/9"),
            "barrel_pct": rate("Season", "BARREL%"),
            "hh_pct": rate("Season", "HH%"),
        }
        if entry["hr9"] is None:
            continue
        out[pitcher.lower()] = entry
        out.setdefault(pitcher.split()[-1].lower(), entry)
    return out


def _pitcher_measured_segment(name: str, rates: dict) -> str:
    """Header segment for an arm PropFinder never scored, using its real rates.

    Deliberately not the risk index: the calibrated proxy carries ~0.4 MAE, and one
    risk point is 50 percentage points on this display, so a proxy would read as a
    measured figure while being off by up to ~40 points.
    """
    seg = f"{name} {rates['hr9']:.2f} HR/9"
    if rates.get("hr9_lhb") is not None:
        seg += f" · LHB {rates['hr9_lhb']:.2f}"
    if rates.get("hr9_rhb") is not None:
        seg += f" · RHB {rates['hr9_rhb']:.2f}"
    extra = []
    if rates.get("barrel_pct") is not None:
        extra.append(f"{rates['barrel_pct']:.1f}% barrel")
    if rates.get("hh_pct") is not None:
        extra.append(f"{rates['hh_pct']:.1f}% hard hit")
    if extra:
        seg += f" ({', '.join(extra)})"
    # No "no PropFinder HR risk" tail. The measured HR/9 and split ARE the useful
    # numbers; telling the reader which vendor lacked a score is noise on a betting
    # sheet, so the segment simply presents what is known.
    return f'<strong class="pitcher-meta">{seg}</strong>'


def form_trend(hr: int, near: int, ev: float) -> str:
    if hr >= 2 or (near >= 3 and ev >= 88) or (hr >= 1 and near >= 2 and ev >= 92):
        return "heating"
    if hr == 0 and near <= 1 and ev < 86:
        return "cooling"
    return "flat"


def form_power_score(stats: dict) -> float:
    hr = stats.get("hr") or 0
    near = stats.get("near") or 0
    ev = stats.get("ev") or 0.0
    barrel = stats.get("barrel") or stats.get("barrel_pct") or 0.0
    hh = stats.get("hh_pct") or 0.0
    return hr * 5.0 + near * 2.0 + max(ev - 90.0, 0.0) * 0.8 + barrel * 1.5 + hh * 0.25


def contact_risk(whiff: float | None, k_pct: float | None) -> bool:
    if whiff is not None and whiff >= 28.0:
        return True
    if k_pct is not None and k_pct >= 28.0:
        return True
    return False


def air_clause(fb: float | None, pull: float | None) -> str:
    parts: list[str] = []
    if fb is not None:
        parts.append(f"FB {fb:.0f}%")
    if pull is not None:
        parts.append(f"pull-air {pull:.0f}%")
    if not parts:
        return ""
    return "Air: " + ", ".join(parts) + ". "


def inject_air_into_note(note: str, clause: str) -> str:
    if not clause or "Air:" in note:
        return note
    if "Matchup:" in note:
        return note.replace("Matchup:", f"{clause}Matchup:", 1)
    return f"{note} {clause}".strip()


def normalize_game_key(key: str) -> str:
    return " ".join((key or "").upper().split())


def normalize_venue_key(name: str) -> str:
    key = " ".join((name or "").lower().split())
    return VENUE_BALLPARK_ALIASES.get(key, key)


def _hr_mult_to_stadium_pct(mult: str | float | None) -> int | None:
    if mult is None:
        return None
    try:
        return int(round((float(str(mult).strip()) - 1.0) * 100))
    except ValueError:
        return None


def _parse_ballpark_pal_hand_file(path: Path) -> dict[str, int]:
    """Ballpark Pal park-factors-L/R export -> venue_key -> HR stadium %."""
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header_idx = next(
        (i for i, ln in enumerate(lines) if "BALLPARK" in ln and "HR" in ln),
        None,
    )
    if header_idx is None:
        return {}
    reader = csv.reader(lines[header_idx:])
    header = next(reader, None)
    if not header:
        return {}
    try:
        ballpark_idx = header.index("BALLPARK")
        hr_idx = header.index("HR")
    except ValueError:
        return {}
    out: dict[str, int] = {}
    for row in reader:
        if len(row) <= max(ballpark_idx, hr_idx):
            continue
        venue = normalize_venue_key(row[ballpark_idx])
        pct = _hr_mult_to_stadium_pct(row[hr_idx])
        if venue and pct is not None:
            out[venue] = pct
    return out


def _park_hand_paths(data_dir: Path, sheet_date: str, hand: str) -> list[Path]:
    """Ballpark Pal L/R exports: prefer *-all-*, fall back to *-night-* for night slates."""
    patterns = (
        f"park-factors-{hand}-all-{sheet_date}*.csv",
        f"park-factors-{hand}-night-{sheet_date}*.csv",
    )
    for pattern in patterns:
        matches = sorted(data_dir.glob(pattern))
        if matches:
            return matches
    return []


def load_venue_hand_stadium_pcts(sheet_date: str) -> tuple[dict[str, int], dict[str, int]]:
    """LHB/RHB stadium HR % from park-factors-L/R Ballpark Pal CSVs (all or night)."""
    data_dir = ROOT / "data"
    lhb_paths = _park_hand_paths(data_dir, sheet_date, "L")
    rhb_paths = _park_hand_paths(data_dir, sheet_date, "R")
    lhb = _parse_ballpark_pal_hand_file(lhb_paths[-1]) if lhb_paths else {}
    rhb = _parse_ballpark_pal_hand_file(rhb_paths[-1]) if rhb_paths else {}
    return lhb, rhb


def game_key_from_title(title: str) -> str:
    return normalize_game_key(title.split(" - ")[0].strip())


def _pct_from_field(val: str | None) -> int | None:
    if not val:
        return None
    m = re.search(r"([+-]?\d+)", str(val).replace("%", ""))
    return int(m.group(1)) if m else None


def _park_time_sort_key(time_str: str) -> tuple[int, str]:
    """Sort PropFinder Time values like 12:35 / 7:20 for DH ordering.

    PropFinder exports 12-hour clock without AM/PM. Day games use 12:xx and
    1–11 for afternoon; evening slots are also 1–11. Treat 1–11 as PM so
    7:20 sorts after 12:35 on doubleheaders.
    """
    raw = (time_str or "").strip()
    m = re.match(r"^(\d{1,2}):(\d{2})", raw)
    if not m:
        return (99_999, raw)
    hour = int(m.group(1))
    minute = int(m.group(2))
    if 1 <= hour <= 11:
        hour += 12
    return (hour * 60 + minute, raw)


def load_weather_lookup(sheet_date: str) -> dict[str, dict]:
    data_dir = ROOT / "data"
    path = data_dir / f"ParkFactors_{sheet_date}.csv"
    if not path.is_file():
        matches = sorted(data_dir.glob(f"ParkFactors_{sheet_date}*.csv"))
        if matches:
            path = matches[0]
    lhb_stadium, rhb_stadium = load_venue_hand_stadium_pcts(sheet_date)
    lookup: dict[str, dict] = {}
    if not path.is_file():
        return lookup
    by_game: dict[str, list[tuple[str, dict]]] = {}
    by_time: dict[str, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            game = normalize_game_key(row.get("Game", ""))
            try:
                hr_pct = int(str(row["HR %"]).replace("%", "").strip())
            except (ValueError, KeyError):
                continue
            venue = (row.get("Venue") or "").strip()
            venue_key = normalize_venue_key(venue)
            wx_pct = _pct_from_field(row.get("HR % Weather"))
            lhb_st = lhb_stadium.get(venue_key)
            rhb_st = rhb_stadium.get(venue_key)
            entry = {
                "game": game,
                "venue": venue,
                "hr_pct": hr_pct,
                "hr_pct_text": row.get("HR %", ""),
                "hr_stadium": row.get("HR % Stadium", ""),
                "hr_weather": row.get("HR % Weather", ""),
                "stadium_pct": _pct_from_field(row.get("HR % Stadium")),
                "weather_pct": wx_pct,
                "time": (row.get("Time") or "").strip(),
            }
            if lhb_st is not None:
                entry["lhb_stadium_pct"] = lhb_st
                entry["park_lhb_pct"] = lhb_st + (wx_pct or 0)
            if rhb_st is not None:
                entry["rhb_stadium_pct"] = rhb_st
                entry["park_rhb_pct"] = rhb_st + (wx_pct or 0)
            if not game:
                # Special-event sites (e.g. Field of Dreams) ship a blank Game
                # column. Keep them keyed by first pitch so the slate can still
                # resolve park factors by start time.
                if entry["time"]:
                    by_time[entry["time"]] = entry
                continue
            by_game.setdefault(game, []).append((entry["time"], entry))
    for game, entries in by_game.items():
        entries.sort(key=lambda item: _park_time_sort_key(item[0]))
        if len(entries) == 1:
            lookup[game] = entries[0][1]
            continue
        for i, (_, entry) in enumerate(entries, 1):
            keyed = {**entry, "game": f"{game} (G{i})"}
            lookup[f"{game} (G{i})"] = keyed
        # Bare matchup falls back to earliest first-pitch row (G1).
        lookup[game] = lookup[f"{game} (G1)"]
    if by_time:
        lookup[_UNKEYED_BY_TIME] = by_time
    return lookup


def _et_clock_from_iso(start_time: str | None) -> str | None:
    """ISO UTC start -> 'H:MM' Eastern, matching the ParkFactors Time column."""
    if not start_time:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", start_time)
    if not m:
        return None
    y, mo, d, hh, mm = (int(g) for g in m.groups())
    stamp = datetime(y, mo, d, hh, mm) - timedelta(hours=_et_utc_offset(y, mo, d))
    return f"{(stamp.hour % 12) or 12}:{stamp.minute:02d}"


def _et_utc_offset(year: int, month: int, day: int) -> int:
    """4 during EDT, 5 during EST — MLB slates only ever need the coarse rule."""
    return 4 if 3 < month < 11 else 5


def lookup_weather_for_game(
    title: str,
    weather_lookup: dict[str, dict],
    start_time: str | None = None,
) -> dict | None:
    key = game_key_from_title(title)
    aliased = alias_weather_game_key(key)
    if aliased in weather_lookup:
        return weather_lookup[aliased]
    if key in weather_lookup:
        return weather_lookup[key]
    base = re.sub(r"\s*\(G\d+\)$", "", key)
    base_aliased = alias_weather_game_key(base)
    # Prefer DH-specific key when title has (Gn) and CSV was keyed that way.
    gn = re.search(r"\(G(\d+)\)$", key)
    if gn:
        for candidate in (f"{base_aliased} (G{gn.group(1)})", f"{base} (G{gn.group(1)})"):
            if candidate in weather_lookup:
                return weather_lookup[candidate]
    hit = weather_lookup.get(base_aliased) or weather_lookup.get(base)
    if hit is not None:
        return hit
    clock = _et_clock_from_iso(start_time)
    if clock:
        by_time = weather_lookup.get(_UNKEYED_BY_TIME) or {}
        entry = by_time.get(clock)
        if entry is not None:
            print(
                f"park: matched {key} to {entry.get('venue') or '?'} by first pitch {clock}"
            )
            return entry
    return None


def parse_game_description(desc: str) -> dict:
    park_m = re.search(r"Park boost\s*([+-]?\d+)%", desc or "")
    if not park_m:
        park_m = re.search(r"HR environment\s*([+-]?\d+)%", desc or "")
    st_m = re.search(r"stadium\s*([+-]?\d+)%", desc or "", re.I)
    wx_m = re.search(r"weather\s*([+-]?\d+)%", desc or "", re.I)
    risks = re.findall(
        r"([^(]+?)\s*\(HR risk\s*([+-]?\d+\.?\d*)",
        desc or "",
    )
    away_risk = home_risk = None
    if len(risks) >= 2:
        away_risk = float(risks[0][1])
        home_risk = float(risks[1][1])
    elif len(risks) == 1:
        away_risk = float(risks[0][1])
    return {
        "park_pct": int(park_m.group(1)) if park_m else None,
        "stadium_pct": int(st_m.group(1)) if st_m else None,
        "weather_pct": int(wx_m.group(1)) if wx_m else None,
        "away_risk": away_risk,
        "home_risk": home_risk,
    }


def resolve_park_context(game: dict, weather: dict | None) -> dict:
    """Net park % plus stadium/weather and per-hand HR park from PropFinder + Ballpark Pal.

    Prefer the fresh ParkFactors CSV (weather) over stale build descriptions so
    mid-day park refreshes actually update gameMeta / parkPct.
    """
    desc_meta = parse_game_description(game.get("description", ""))
    if weather:
        park_pct = weather.get("hr_pct")
        stadium_pct = weather.get("stadium_pct")
        weather_pct = weather.get("weather_pct")
    else:
        park_pct = desc_meta["park_pct"]
        stadium_pct = desc_meta["stadium_pct"]
        weather_pct = desc_meta["weather_pct"]
    if park_pct is None:
        park_pct = desc_meta["park_pct"]
    if stadium_pct is None:
        stadium_pct = desc_meta["stadium_pct"]
    if weather_pct is None:
        weather_pct = desc_meta["weather_pct"]
    park_lhb_stadium = weather.get("lhb_stadium_pct") if weather else None
    park_rhb_stadium = weather.get("rhb_stadium_pct") if weather else None
    park_lhb_pct = weather.get("park_lhb_pct") if weather else None
    park_rhb_pct = weather.get("park_rhb_pct") if weather else None
    return {
        "park_pct": park_pct,
        "stadium_pct": stadium_pct,
        "weather_pct": weather_pct,
        "park_lhb_stadium_pct": park_lhb_stadium,
        "park_rhb_stadium_pct": park_rhb_stadium,
        "park_lhb_pct": park_lhb_pct,
        "park_rhb_pct": park_rhb_pct,
    }


def pitcher_name_from_title_segment(seg: str) -> str:
    seg = seg.strip()
    seg = re.sub(r"\s*🧤\s*", " ", seg)
    m = re.match(r"^(.+?)\s*\([LR],\s*[A-Z]{2,4}\)", seg)
    return m.group(1).strip() if m else seg.strip()


def pitcher_last_from_title_segment(seg: str) -> str:
    return pitcher_name_from_title_segment(seg).split()[-1]


def parse_pitcher_blocks_from_description(desc: str) -> dict[str, dict]:
    """Last-name key -> overall / vs_lhb / vs_rhb from Tail key data lines."""
    out: dict[str, dict] = {}
    for m in re.finditer(
        r"([A-Za-z][A-Za-z\s.'-]+?)\s*"
        r"\(HR risk\s*([+-]?\d+\.?\d*),\s*vs LHB\s*([+-]?\d+\.?\d*),\s*vs RHB\s*([+-]?\d+\.?\d*)\)",
        desc or "",
    ):
        name = re.sub(r"\s*🧤\s*", " ", m.group(1)).strip()
        key = name.split()[-1].lower()
        out[key] = {
            "pitcher": name,
            "overall": float(m.group(2)),
            "vs_lhb": float(m.group(3)),
            "vs_rhb": float(m.group(4)),
        }
    return out


def resolve_pitcher_risk_row(
    label: str,
    pitcher_risk: dict | None,
    desc_blocks: dict[str, dict],
) -> dict | None:
    if pitcher_risk:
        row = resolve_pitcher(pitcher_risk, label)
        if row:
            return row
    return desc_blocks.get(label.split()[-1].lower())


def _pitcher_meta_segment(name: str, row: dict, hr9_lookup: dict[str, float]) -> str:
    last = name.split()[-1]
    hr9 = hr9_lookup.get(name.lower()) or hr9_lookup.get(last.lower())
    if row.get("no_data"):
        # Nothing measured anywhere for this arm. Omit the segment entirely -- a
        # "no data yet" placeholder tells the reader nothing actionable and just
        # eats space in the header.
        return ""
    seg = (
        f"{name} {format_pitcher_risk_pct(row['overall'])} overall · "
        f"LHB {format_pitcher_risk_pct(row['vs_lhb'])} · "
        f"RHB {format_pitcher_risk_pct(row['vs_rhb'])}"
    )
    if hr9 is not None:
        seg += f" ({hr9:.2f} HR/9)"
    return f'<strong class="pitcher-meta">{seg}</strong>'


def hand_park_pcts(park_ctx: dict) -> tuple[int | None, int | None]:
    """LHB/RHB net HR park boost (Ballpark Pal stadium hand + PropFinder weather)."""
    park_pct = park_ctx.get("park_pct")
    lhb = park_ctx.get("park_lhb_pct")
    rhb = park_ctx.get("park_rhb_pct")
    if lhb is None and park_pct is not None:
        lhb = park_pct
    if rhb is None and park_pct is not None:
        rhb = park_pct
    if lhb is None and rhb is None:
        return None, None
    return (int(lhb) if lhb is not None else None, int(rhb) if rhb is not None else None)


def row_hand_park_fields(hand: str, park_ctx: dict) -> dict:
    """Per-batter hand park fields for Goblin / straight ranking rows."""
    overall = park_ctx.get("park_pct")
    lhb = park_ctx.get("park_lhb_pct")
    rhb = park_ctx.get("park_rhb_pct")
    hand_key = (hand or "").strip().upper()
    if hand_key == "L" and lhb is not None:
        hand_pct = lhb
    elif hand_key == "R" and rhb is not None:
        hand_pct = rhb
    elif hand_key == "S" and lhb is not None and rhb is not None:
        # Switch: use the stronger hand-park lane (mirrors batter_split).
        hand_pct = max(lhb, rhb)
    elif hand_key == "S" and rhb is not None:
        hand_pct = rhb
    else:
        hand_pct = overall
    out: dict = {}
    if lhb is not None:
        out["park_lhb_pct"] = lhb
    if rhb is not None:
        out["park_rhb_pct"] = rhb
    if hand_pct is not None:
        out["hand_park_pct"] = hand_pct
    return out


def format_park_segment(park_ctx: dict) -> str | None:
    park_pct = park_ctx.get("park_pct")
    if park_pct is None:
        return None
    lhb_pct, rhb_pct = hand_park_pcts(park_ctx)
    stadium_pct = park_ctx.get("stadium_pct")
    weather_pct = park_ctx.get("weather_pct")
    lhb_stadium = park_ctx.get("park_lhb_stadium_pct")
    rhb_stadium = park_ctx.get("park_rhb_stadium_pct")
    if lhb_pct is None or rhb_pct is None:
        return None
    hand_seg = f"LHB {lhb_pct:+d}% · RHB {rhb_pct:+d}%"
    if (
        lhb_stadium is not None
        and rhb_stadium is not None
        and weather_pct is not None
    ):
        return (
            f"Park {park_pct:+d}% · {hand_seg} "
            f"(stadium LHB {lhb_stadium:+d}%, RHB {rhb_stadium:+d}%, wx {weather_pct:+d}%)"
        )
    if stadium_pct is not None and weather_pct is not None:
        return (
            f"Park {park_pct:+d}% · {hand_seg} "
            f"(stadium {stadium_pct:+d}%, wx {weather_pct:+d}%)"
        )
    return f"Park {park_pct:+d}% · {hand_seg}"


def build_game_meta_line(
    game: dict,
    hr9_lookup: dict[str, float],
    weather: dict | None = None,
    pitcher_risk: dict | None = None,
    rate_lookup: dict[str, dict] | None = None,
) -> str:
    parts: list[str] = []
    if game.get("startTime"):
        try:
            from datetime import datetime
            from zoneinfo import ZoneInfo

            dt = datetime.fromisoformat(game["startTime"].replace("Z", "+00:00")).astimezone(
                ZoneInfo("America/New_York")
            )
            h = dt.hour % 12 or 12
            parts.append(f"{h}:{dt.minute:02d} {'AM' if dt.hour < 12 else 'PM'} ET")
        except (ValueError, OSError):
            pass
    park_seg = format_park_segment(resolve_park_context(game, weather))
    if park_seg:
        parts.append(park_seg)
    desc = game.get("description", "")
    desc_blocks = parse_pitcher_blocks_from_description(desc)
    title = game.get("title", "")
    if " - " in title and " vs " in title:
        _, matchup = title.split(" - ", 1)
        away_seg, home_seg = matchup.split(" vs ", 1)
        away_label = pitcher_name_from_title_segment(away_seg)
        home_label = pitcher_name_from_title_segment(home_seg)
        for label in (away_label, home_label):
            row = resolve_pitcher_risk_row(label, pitcher_risk, desc_blocks)
            if row:
                parts.append(_pitcher_meta_segment(label, row, hr9_lookup))
                continue
            rates = (rate_lookup or {}).get(label.lower()) or (rate_lookup or {}).get(
                label.split()[-1].lower()
            )
            if rates:
                print(f"note: {label} absent from HR risk export — using measured rates")
                parts.append(_pitcher_measured_segment(label, rates))
            else:
                print(f"note: no risk or rate data for {label} — header omits this SP")
    return " · ".join(p for p in parts if p)


def plain_name(entry: dict) -> str:
    return entry["name"].rsplit(" (", 1)[0]


def chip_label(entry: dict) -> str:
    chips = entry.get("chips") or []
    if not chips:
        return ""
    return chips[0].replace("vs ", "").strip()


def listed_odds_short(odds: str) -> str:
    m = re.search(r"Listed ([+-]\d+)", odds or "")
    return m.group(1) if m else ""


def top3_why(row: dict, rank: int) -> str:
    bits = [f"#{rank} model score in this game"]
    hr = int(row.get("hr") or 0)
    near = int(row.get("near") or 0)
    ev = float(row.get("ev") or 0)
    bits.append(f"{hr} HR, {near} near-HR, {ev:.0f} mph EV")
    chip = chip_label(row)
    if chip:
        bits.append(f"vs {chip}")
    if row.get("formTrend") == "heating":
        bits.append("heating L5")
    if row.get("blast") == "high":
        bits.append("high blast rate")
    em = row.get("emojis", "")
    if "🚀" in em:
        bits.append("elite EV")
    if "⭐" in em:
        bits.append("WPZ Favorite")
    return " · ".join(bits)


def sleeper_why(sleeper: dict, top3_rows: list[dict]) -> str:
    bits = [f"Score {sleeper['score']} — outside top 3 on the sheet"]
    third = top3_rows[2] if len(top3_rows) >= 3 else None
    sfs = sleeper.get("_formScore") or form_power_score(sleeper)
    if third:
        tfs = third.get("_formScore") or form_power_score(third)
        tname = plain_name(third)
        if sfs >= tfs + 0.5:
            bits.append(f"hotter L5 power than #{3} {tname}")
        elif sfs > tfs:
            bits.append(f"edging {tname} on recent power")
    hr = int(sleeper.get("hr") or 0)
    near = int(sleeper.get("near") or 0)
    ev = float(sleeper.get("ev") or 0)
    bits.append(f"{hr} HR, {near} near-HR, {ev:.0f} mph EV")
    chip = chip_label(sleeper)
    if chip:
        bits.append(f"vs {chip}")
    if sleeper.get("formTrend") == "heating":
        bits.append("form heating up")
    return " · ".join(bits[:5])


def pick_card(entry: dict, rank: int | None, why: str) -> dict:
    return {
        "name": plain_name(entry),
        "score": entry["score"],
        "why": why,
        "chip": chip_label(entry),
        "rank": rank,
        "oddsShort": listed_odds_short(entry.get("odds", "")),
    }


def pick_top3_and_sleeper(rows: list[dict]) -> tuple[list[dict], dict | None]:
    indexed = list(enumerate(rows))
    by_score = sorted(indexed, key=lambda x: x[1]["score"], reverse=True)
    top3_idx = {i for i, _ in by_score[:3]}
    top3 = [rows[i] for i, _ in by_score[:3]]
    if len(by_score) < 4:
        return top3, None
    third_form = form_power_score(by_score[2][1])
    by_form = sorted(indexed, key=lambda x: form_power_score(x[1]), reverse=True)
    best_outside = None
    best_fs = -1.0
    for i, row in by_form:
        if i in top3_idx:
            continue
        fs = form_power_score(row)
        score_rank = next(r for r, (idx, _) in enumerate(by_score) if idx == i)
        form_rank = next(r for r, (idx, _) in enumerate(by_form) if idx == i)
        if score_rank < 3:
            continue
        if fs >= third_form + 0.5 or (score_rank >= 3 and form_rank == 0):
            if fs > best_fs:
                best_fs = fs
                best_outside = row
        elif score_rank >= 4 and form_rank <= 1 and fs > best_fs:
            best_fs = fs
            best_outside = row
    return top3, best_outside


def enrich_row(entry: dict, stats: dict | None, zone: dict | None = None) -> dict:
    out = dict(entry)
    st = stats or {}
    hr = st.get("hr")
    if hr is None:
        m = re.search(r"(\d+)\s+HR", entry.get("note", ""))
        hr = int(m.group(1)) if m else 0
    near = st.get("near")
    if near is None:
        m = re.search(r"(\d+)\s+near-HR", entry.get("note", ""))
        near = int(m.group(1)) if m else 0
    ev = st.get("ev")
    if ev is None:
        m = re.search(r"(\d+(?:\.\d+)?)\s+mph EV", entry.get("note", ""))
        ev = float(m.group(1)) if m else 0.0
    fb = st.get("fb_pct")
    pull = st.get("pull_air")
    whiff = st.get("whiff_pct")
    k_pct = st.get("k_pct")
    gb = st.get("gb_pct")
    hh = st.get("hh_pct")
    out["hr"] = hr
    out["near"] = near
    out["ev"] = ev
    if st.get("barrel") is not None:
        out["barrel"] = st["barrel"]
    if fb is not None:
        out["fbPct"] = round(fb, 1)
    if pull is not None:
        out["pullAir"] = round(pull, 1)
    if whiff is not None:
        out["whiffPct"] = round(whiff, 1)
    if k_pct is not None:
        out["kPct"] = round(k_pct, 1)
    if gb is not None:
        out["gbPct"] = round(gb, 1)
        sig = gb_signal(gb)
        if sig:
            out["gbSignal"] = sig
    if hh is not None:
        out["hhPct"] = round(hh, 1)
        sig = hh_signal(hh)
        if sig:
            out["hhSignal"] = sig
    trend = form_trend(int(hr), int(near), float(ev))
    out["formTrend"] = trend
    if contact_risk(whiff, k_pct):
        out["contactRisk"] = True
    clause = air_clause(fb, pull)
    if clause:
        out["note"] = inject_air_into_note(out.get("note", ""), clause)
    out["note"] = compact_note(out.get("note", ""))
    out["_formScore"] = form_power_score({**st, "hr": hr, "near": near, "ev": ev})
    if zone and zone.get("zone_score") is not None:
        out["zoneScore"] = round(zone["zone_score"], 1)
        if zone.get("contact") is not None:
            out["zoneContact"] = round(zone["contact"], 1)
        if zone.get("barrel") is not None:
            out["zoneBarrel"] = round(zone["barrel"], 1)
        if zone.get("hr") is not None:
            out["zoneHr"] = round(zone["hr"], 1)
        if zone.get("hard_hit") is not None:
            out["zoneHardHit"] = round(zone["hard_hit"], 1)
    return out


def enrich_games_list(games: list[dict], sheet_date: str) -> list[dict]:
    batter_lookup = load_batter_stat_lookup(sheet_date)
    zone_lookup = load_zone_lookup(sheet_date)
    hr9_lookup = load_pitcher_hr9_lookup(sheet_date)
    weather_lookup = load_weather_lookup(sheet_date)
    risk_path = ROOT / "data" / f"hr-targets-overall-{sheet_date}.csv"
    pitcher_risk = load_pitcher_risk(risk_path) if risk_path.is_file() else {}
    rate_lookup = load_pitcher_rates_from_matchups(sheet_date)
    enriched: list[dict] = []
    for game in games:
        g = dict(game)
        weather = lookup_weather_for_game(
            g.get("title", ""), weather_lookup, g.get("startTime")
        )
        rows = []
        for entry in game.get("rows", []):
            plain = entry["name"].rsplit(" (", 1)[0]
            key = name_lookup_key(plain)
            chip = (entry.get("chips") or [""])[0]
            zone = lookup_zone_row(plain, chip, zone_lookup)
            rows.append(enrich_row(entry, batter_lookup.get(key), zone))
        top3, sleeper = pick_top3_and_sleeper(rows)
        g["rows"] = rows
        g["top3"] = [plain_name(r) for r in top3]
        g["top3Detail"] = [
            pick_card(r, i + 1, top3_why(r, i + 1)) for i, r in enumerate(top3)
        ]
        if sleeper:
            g["sleeper"] = plain_name(sleeper)
            g["sleeperDetail"] = pick_card(sleeper, None, sleeper_why(sleeper, top3))
        park_ctx = resolve_park_context(g, weather)
        g["gameMeta"] = build_game_meta_line(
            g, hr9_lookup, weather, pitcher_risk, rate_lookup
        )
        if park_ctx["park_pct"] is not None:
            g["parkPct"] = park_ctx["park_pct"]
            lhb_pct, rhb_pct = hand_park_pcts(park_ctx)
            g["parkLhbPct"] = lhb_pct
            g["parkRhbPct"] = rhb_pct
        # Full description duplicates gameMeta — keep data for park stars only.
        g["description"] = ""
        enriched.append(g)
    return enriched


def emit_games_js(games_data: list[dict]) -> str:
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    out = ["const games = ["]
    for game in games_data:
        out.append("    {")
        out.append(f"        title: {js_string(game['title'])},")
        if game.get("description"):
            out.append(f"        description: {js_string(game['description'])},")
        if game.get("startTime"):
            out.append(f"        startTime: {js_string(game['startTime'])},")
        if game.get("gameMeta"):
            out.append(f"        gameMeta: {js_string(game['gameMeta'])},")
        if game.get("parkPct") is not None:
            out.append(f"        parkPct: {game['parkPct']},")
        if game.get("parkLhbPct") is not None:
            out.append(f"        parkLhbPct: {game['parkLhbPct']},")
        if game.get("parkRhbPct") is not None:
            out.append(f"        parkRhbPct: {game['parkRhbPct']},")
        if game.get("top3"):
            out.append(f"        top3: {js_string(game['top3'])},")
        if game.get("top3Detail"):
            out.append(f"        top3Detail: {json.dumps(game['top3Detail'], ensure_ascii=False)},")
        if game.get("sleeper"):
            out.append(f"        sleeper: {js_string(game['sleeper'])},")
        if game.get("sleeperDetail"):
            out.append(f"        sleeperDetail: {json.dumps(game['sleeperDetail'], ensure_ascii=False)},")
        out.append("        rows: [")
        for entry in game["rows"]:
            parts = [
                f"name: {js_string(entry['name'])}",
                f"odds: {js_string(entry['odds'])}",
                f"score: {entry['score']}",
                f"emojis: {js_string(entry['emojis'])}",
                f"note: {js_string(entry['note'])}",
                f"chips: {js_string(entry['chips'])}",
            ]
            if entry.get("blast"):
                parts.append(f"blast: {js_string(entry['blast'])}")
            if entry.get("formTrend"):
                parts.append(f"formTrend: {js_string(entry['formTrend'])}")
            if entry.get("contactRisk"):
                parts.append("contactRisk: true")
            if entry.get("gbPct") is not None:
                parts.append(f"gbPct: {entry['gbPct']}")
            if entry.get("gbSignal"):
                parts.append(f"gbSignal: {js_string(entry['gbSignal'])}")
            if entry.get("hhPct") is not None:
                parts.append(f"hhPct: {entry['hhPct']}")
            if entry.get("hhSignal"):
                parts.append(f"hhSignal: {js_string(entry['hhSignal'])}")
            if entry.get("fbPct") is not None:
                parts.append(f"fbPct: {entry['fbPct']}")
            if entry.get("pullAir") is not None:
                parts.append(f"pullAir: {entry['pullAir']}")
            if entry.get("zoneScore") is not None:
                parts.append(f"zoneScore: {entry['zoneScore']}")
            if entry.get("zoneContact") is not None:
                parts.append(f"zoneContact: {entry['zoneContact']}")
            if entry.get("zoneBarrel") is not None:
                parts.append(f"zoneBarrel: {entry['zoneBarrel']}")
            if entry.get("zoneHr") is not None:
                parts.append(f"zoneHr: {entry['zoneHr']}")
            if entry.get("zoneHardHit") is not None:
                parts.append(f"zoneHardHit: {entry['zoneHardHit']}")
            out.append("            { " + ", ".join(parts) + " },")
        out.append("        ],")
        out.append("    },")
    out.append("];")
    return "\n".join(out)
