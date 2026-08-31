"""Game-day weather for the NFL Research tab.

Forecasts come from Open-Meteo (https://open-meteo.com) -- free, no API key,
and already the source the MLB side of this site uses.

Roof handling matters more in the NFL than the ballpark equivalent: a dome or a
closed retractable makes the forecast irrelevant, and the sheet should say so
rather than print a wind speed nobody can act on.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# home team -> (venue, lat, lon, roof)
#   roof: "outdoor" | "dome" | "retractable"
STADIUMS: dict[str, tuple[str, float, float, str]] = {
    "ARI": ("State Farm Stadium", 33.5277, -112.2626, "retractable"),
    "ATL": ("Mercedes-Benz Stadium", 33.7554, -84.4009, "retractable"),
    "BAL": ("M&T Bank Stadium", 39.2780, -76.6227, "outdoor"),
    "BUF": ("Highmark Stadium", 42.7738, -78.7870, "outdoor"),
    "CAR": ("Bank of America Stadium", 35.2258, -80.8528, "outdoor"),
    "CHI": ("Soldier Field", 41.8623, -87.6167, "outdoor"),
    "CIN": ("Paycor Stadium", 39.0955, -84.5161, "outdoor"),
    "CLE": ("Huntington Bank Field", 41.5061, -81.6995, "outdoor"),
    "DAL": ("AT&T Stadium", 32.7473, -97.0945, "retractable"),
    "DEN": ("Empower Field at Mile High", 39.7439, -105.0201, "outdoor"),
    "DET": ("Ford Field", 42.3400, -83.0456, "dome"),
    "GB": ("Lambeau Field", 44.5013, -88.0622, "outdoor"),
    "HOU": ("NRG Stadium", 29.6847, -95.4107, "retractable"),
    "IND": ("Lucas Oil Stadium", 39.7601, -86.1639, "retractable"),
    "JAX": ("EverBank Stadium", 30.3239, -81.6373, "outdoor"),
    "KC": ("GEHA Field at Arrowhead", 39.0489, -94.4839, "outdoor"),
    "LAC": ("SoFi Stadium", 33.9535, -118.3392, "dome"),
    "LAR": ("SoFi Stadium", 33.9535, -118.3392, "dome"),
    "LV": ("Allegiant Stadium", 36.0909, -115.1833, "dome"),
    "MIA": ("Hard Rock Stadium", 25.9580, -80.2389, "outdoor"),
    "MIN": ("U.S. Bank Stadium", 44.9738, -93.2578, "dome"),
    "NE": ("Gillette Stadium", 42.0909, -71.2643, "outdoor"),
    "NO": ("Caesars Superdome", 29.9511, -90.0812, "dome"),
    "NYG": ("MetLife Stadium", 40.8135, -74.0745, "outdoor"),
    "NYJ": ("MetLife Stadium", 40.8135, -74.0745, "outdoor"),
    "PHI": ("Lincoln Financial Field", 39.9008, -75.1675, "outdoor"),
    "PIT": ("Acrisure Stadium", 40.4468, -80.0158, "outdoor"),
    "SEA": ("Lumen Field", 47.5952, -122.3316, "outdoor"),
    "SF": ("Levi's Stadium", 37.4030, -121.9698, "outdoor"),
    "TB": ("Raymond James Stadium", 27.9759, -82.5033, "outdoor"),
    "TEN": ("Nissan Stadium", 36.1665, -86.7713, "outdoor"),
    # ESPN sends WSH, not WAS -- keyed the other way this venue never matched.
    "WSH": ("Northwest Stadium", 38.9077, -76.8645, "outdoor"),
}


def _get_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "worstpickz-nfl-research"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _kickoff_dt(kickoff: str) -> datetime | None:
    if not kickoff:
        return None
    try:
        return datetime.fromisoformat(kickoff.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_game_weather(games: list[dict]) -> dict[str, dict]:
    """game id -> forecast at kickoff. Indoor venues short-circuit."""
    out: dict[str, dict] = {}
    # One request per venue, not per game: two clubs share SoFi and MetLife.
    wanted: dict[tuple[float, float], list[dict]] = {}

    for game in games:
        home = game.get("home")
        venue = STADIUMS.get(home)
        if not venue:
            continue
        name, lat, lon, roof = venue
        base = {"venue": name, "roof": roof, "home": home}
        if roof == "dome":
            out[game["id"]] = {**base, "indoor": True,
                               "note": "Dome — conditions are controlled."}
            continue
        wanted.setdefault((lat, lon), []).append({**base, "game": game})

    for (lat, lon), entries in wanted.items():
        params = urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,apparent_temperature,precipitation_probability,"
                          "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "forecast_days": 16,
                "timezone": "UTC",
            }
        )
        try:
            data = _get_json(f"{FORECAST_URL}?{params}")
        except Exception:
            continue
        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        if not times:
            continue
        stamps = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in times]

        for entry in entries:
            game = entry["game"]
            kick = _kickoff_dt(game.get("kickoff", ""))
            base = {k: v for k, v in entry.items() if k != "game"}
            if kick is None:
                out[game["id"]] = {**base, "indoor": False,
                                   "note": "Kickoff time unavailable."}
                continue
            # Forecasts run 16 days out; a week-15 slate in September has none.
            idx = min(range(len(stamps)), key=lambda i: abs((stamps[i] - kick).total_seconds()))
            if abs((stamps[idx] - kick).total_seconds()) > 6 * 3600:
                out[game["id"]] = {
                    **base,
                    "indoor": False,
                    "note": "Too far out for a forecast — check back closer to kickoff.",
                }
                continue

            def val(key):
                series = hourly.get(key) or []
                return series[idx] if idx < len(series) else None

            out[game["id"]] = {
                **base,
                "indoor": False,
                "temp_f": val("temperature_2m"),
                "feels_f": val("apparent_temperature"),
                "precip_pct": val("precipitation_probability"),
                "wind_mph": val("wind_speed_10m"),
                "gust_mph": val("wind_gusts_10m"),
                "wind_dir": val("wind_direction_10m"),
                "forecast_for": stamps[idx].isoformat(),
            }

    return out
