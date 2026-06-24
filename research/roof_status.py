#!/usr/bin/env python3
"""Retractable roof resolution: MLB API strings, climate rules, safe PASS state."""
from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

from research.stadium_db import lookup_stadium_spec

MLB_API = "https://statsapi.mlb.com/api/v1"

# Venue keys (normalized) with team-specific climate boundaries.
CLIMATE_RULES: dict[str, dict[str, Any]] = {
    "loandepot park": {
        "close_temp_f": 92,
        "open_temp_min": 58,
        "open_temp_max": 88,
        "close_precip_pct": 45,
        "high_variance": False,
    },
    "minute maid park": {
        "close_temp_f": 92,
        "open_temp_min": 55,
        "open_temp_max": 90,
        "close_precip_pct": 45,
        "high_variance": False,
    },
    "globe life field": {
        "close_temp_f": 92,
        "open_temp_min": 55,
        "open_temp_max": 90,
        "close_precip_pct": 40,
        "high_variance": False,
    },
    "chase field": {
        "close_temp_f": 95,
        "close_temp_f_low": 58,
        "open_temp_min": 62,
        "open_temp_max": 92,
        "close_precip_pct": 35,
        "high_variance": False,
    },
    "american family field": {
        "close_temp_f_low": 50,
        "open_temp_min": 58,
        "open_temp_max": 78,
        "close_precip_pct": 40,
        "high_variance": True,
    },
    "rogers centre": {
        "close_temp_f_low": 45,
        "open_temp_min": 55,
        "open_temp_max": 82,
        "close_precip_pct": 35,
        "high_variance": True,
    },
    "t mobile park": {
        "close_temp_f_low": 50,
        "open_temp_min": 55,
        "open_temp_max": 80,
        "close_precip_pct": 40,
        "high_variance": True,
    },
}

# Outdoor parks where wind uncertainty alone can trigger PASS (no roof step).
OUTDOOR_WIND_VARIANCE = {"wrigley field", "fenway park"}

ROOF_CLOSED_RE = re.compile(
    r"(roof\s*closed|closed\s*roof|retract(?:ed|able)\s*roof\s*closed|"
    r"\bdome\b|\bindoor|\binside\b|retracted)",
    re.I,
)
ROOF_OPEN_RE = re.compile(r"(roof\s*open|open\s*air|\boutdoor\b|retract(?:ed|able)\s*roof\s*open)", re.I)
RAIN_RE = re.compile(r"\b(rain|shower|storm|drizzle|thunder|precip)\b", re.I)


def _norm_venue(name: str) -> str:
    return " ".join((name or "").lower().split())


def _venue_key(venue_name: str) -> str | None:
    spec = lookup_stadium_spec(venue_name)
    if not spec:
        return _norm_venue(venue_name)
    for key in CLIMATE_RULES:
        if key in _norm_venue(venue_name) or _norm_venue(venue_name) in key:
            return key
    name = _norm_venue(spec.get("mlbName") or venue_name)
    return name if name in CLIMATE_RULES else _norm_venue(venue_name)


def needs_roof_check(venue_name: str) -> bool:
    spec = lookup_stadium_spec(venue_name)
    if not spec:
        return False
    roof = (spec.get("roof") or "open").lower()
    return roof in {"retractable", "dome", "ret"}


def is_outdoor_only(venue_name: str) -> bool:
    spec = lookup_stadium_spec(venue_name)
    if not spec:
        return True
    return (spec.get("roof") or "open").lower() == "open"


def parse_mlb_weather_roof(*texts: str | None) -> str | None:
    """Return 'closed', 'open', or None from MLB weather/condition strings."""
    blob = " ".join(t for t in texts if t).strip()
    if not blob:
        return None
    if ROOF_CLOSED_RE.search(blob):
        return "closed"
    if ROOF_OPEN_RE.search(blob):
        return "open"
    return None


def fetch_boxscore_weather(game_pk: int, *, timeout: int = 15) -> dict[str, str]:
    """Pull Weather/Wind lines from live boxscore info feed."""
    out: dict[str, str] = {}
    if not game_pk:
        return out
    try:
        url = f"{MLB_API}/game/{game_pk}/boxscore"
        req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Roof/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        for item in data.get("info") or []:
            label = (item.get("label") or "").strip().lower()
            value = (item.get("value") or "").strip()
            if label == "weather":
                out["weather"] = value
            elif label == "wind":
                out["wind"] = value
    except Exception:
        return out
    return out


def fetch_live_feed_weather(game_pk: int, *, timeout: int = 15) -> dict[str, str]:
    if not game_pk:
        return {}
    try:
        url = f"{MLB_API}/1.1/game/{game_pk}/feed/live"
        req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Roof/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        wx = (data.get("gameData") or {}).get("weather") or {}
        return {
            "condition": wx.get("condition") or "",
            "temp": wx.get("temp") or "",
            "wind": wx.get("wind") or "",
        }
    except Exception:
        return {}


def predict_roof_by_climate(
    venue_name: str,
    *,
    temp_f: float | None,
    precip_pct: float | None,
    condition: str | None = None,
) -> tuple[str | None, str]:
    """Return ('open'|'closed'|'unknown', reason). None means skip (outdoor)."""
    if is_outdoor_only(venue_name):
        return None, "outdoor_skip"

    key = _venue_key(venue_name)
    rules = CLIMATE_RULES.get(key)
    if not rules:
        if (lookup_stadium_spec(venue_name) or {}).get("roof") == "dome":
            return "closed", "permanent_dome"
        return "unknown", "no_climate_rules"

    if temp_f is None:
        return "unknown", "missing_temp"

    close_hot = rules.get("close_temp_f")
    close_cold = rules.get("close_temp_f_low")
    open_min = rules.get("open_temp_min", 55)
    open_max = rules.get("open_temp_max", 85)
    close_precip = rules.get("close_precip_pct", 40)

    if close_hot is not None and temp_f >= close_hot:
        return "closed", f"climate_hot_{temp_f:.0f}F>={close_hot}F"
    if close_cold is not None and temp_f <= close_cold:
        return "closed", f"climate_cold_{temp_f:.0f}F<={close_cold}F"
    if precip_pct is not None and precip_pct >= close_precip:
        return "closed", f"climate_rain_{precip_pct:.0f}%>={close_precip}%"
    if condition and RAIN_RE.search(condition) and (precip_pct is None or precip_pct >= 25):
        return "closed", "climate_rain_condition"

    if open_min <= temp_f <= open_max and (precip_pct is None or precip_pct < 25):
        if rules.get("high_variance") and (precip_pct is None or precip_pct >= 15):
            return "unknown", f"borderline_{temp_f:.0f}F_precip_{precip_pct or 0:.0f}%"
        return "open", f"climate_comfort_{temp_f:.0f}F_precip_{precip_pct or 0:.0f}%"

    if rules.get("high_variance"):
        return "unknown", f"borderline_{temp_f:.0f}F_precip_{precip_pct or 0:.0f}%"

    # Non high-variance: lean open in mild gap zones
    if temp_f > open_max and temp_f < (close_hot or 999):
        return "unknown", f"warm_borderline_{temp_f:.0f}F"
    return "open", f"climate_default_{temp_f:.0f}F"


def outdoor_wind_pass(
    venue_name: str,
    *,
    wind_component_mph: float | None,
    wind_mph: float | None,
) -> bool:
    """PASS outdoor props when wind is borderline at variance parks."""
    key = _norm_venue(venue_name)
    if key not in OUTDOOR_WIND_VARIANCE:
        return False
    if wind_mph is not None and wind_mph >= 18:
        return False
    if wind_component_mph is None:
        return True
    return abs(wind_component_mph) <= 4


def resolve_roof_status(
    venue_name: str,
    *,
    game_pk: int | None = None,
    mlb_weather: dict | None = None,
    temp_f: float | None = None,
    precip_pct: float | None = None,
    wind_component_mph: float | None = None,
    wind_mph: float | None = None,
) -> dict[str, Any]:
    """
    Tiered roof evaluation.
    Returns state: open | closed | dome | unknown | skip
    propPass True when UNKNOWN on high-variance retractable or outdoor wind borderline.
    """
    spec = lookup_stadium_spec(venue_name) or {}
    roof_type = (spec.get("roof") or "open").lower()

    if roof_type == "open":
        prop_pass = outdoor_wind_pass(
            venue_name,
            wind_component_mph=wind_component_mph,
            wind_mph=wind_mph,
        )
        return {
            "state": "skip",
            "effective": "open",
            "source": "outdoor",
            "confidence": "high",
            "propPass": prop_pass,
            "reason": "outdoor_grass_skip_roof" if not prop_pass else "outdoor_wind_borderline_pass",
            "highVariance": prop_pass,
        }

    if roof_type == "dome":
        return {
            "state": "dome",
            "effective": "closed",
            "source": "permanent_dome",
            "confidence": "high",
            "propPass": False,
            "reason": "permanent_dome",
            "highVariance": False,
        }

    # --- Retractable ---
    mlb = mlb_weather or {}
    condition = mlb.get("condition") or ""
    parsed = None
    source = None
    reason = None

    # Tier 1: live boxscore strings (game underway / late pregame)
    if game_pk:
        box = fetch_boxscore_weather(game_pk)
        live = fetch_live_feed_weather(game_pk)
        blob_parts = [box.get("weather"), box.get("wind"), live.get("condition"), live.get("wind")]
        parsed = parse_mlb_weather_roof(*blob_parts)
        if parsed:
            source = "mlb_boxscore"
            reason = "mlb_boxscore_weather_string"

    # Tier 2: schedule hydrate weather
    if not parsed:
        parsed = parse_mlb_weather_roof(condition, mlb.get("wind"), mlb.get("temp"))
        if parsed:
            source = "mlb_schedule"
            reason = "mlb_schedule_weather_string"

    # Tier 3: climate engine (Open-Meteo inputs)
    climate_state = None
    if not parsed:
        climate_state, climate_reason = predict_roof_by_climate(
            venue_name,
            temp_f=temp_f,
            precip_pct=precip_pct,
            condition=condition,
        )
        if climate_state in {"open", "closed"}:
            parsed = climate_state
            source = "climate"
            reason = climate_reason
        elif climate_state == "unknown":
            source = "climate"
            reason = climate_reason

    key = _venue_key(venue_name)
    high_variance = bool((CLIMATE_RULES.get(key) or {}).get("high_variance"))

    if parsed in {"open", "closed"}:
        return {
            "state": parsed,
            "effective": parsed,
            "source": source or "inferred",
            "confidence": "high" if source in {"mlb_boxscore", "mlb_schedule"} else "medium",
            "propPass": False,
            "reason": reason or parsed,
            "highVariance": high_variance,
        }

    # UNKNOWN safe-state
    return {
        "state": "unknown",
        "effective": "open",
        "source": source or "unknown",
        "confidence": "low",
        "propPass": high_variance,
        "reason": reason or "roof_decision_unknown",
        "highVariance": high_variance,
    }


def effective_roof_for_weather(roof_status: dict | None) -> str:
    """Map roof status to park_weather roof arg: open | dome (closed)."""
    if not roof_status:
        return "open"
    state = roof_status.get("effective") or roof_status.get("state")
    if state in {"closed", "dome"}:
        return "dome"
    return "open"


def try_scrape_roof_hint(venue_name: str, home_team: str | None = None) -> str | None:
    """
    Optional Tier-4 hint from public web text (no API key).
    Returns 'open' | 'closed' | None. Extend with team-specific URLs as needed.
    """
    _ = (venue_name, home_team)
    return None
