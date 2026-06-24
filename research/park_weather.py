#!/usr/bin/env python3
"""Open-Meteo park weather + density altitude for MLB Research (free, no API key)."""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
STADIUM_JSON = ROOT / "preview" / "data" / "stadium-coords.json"

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
RHO_ZERO = 1.225
DA_EXPONENT = 1 / ((9.80665 / (287.053 * 0.0065)) - 1)
BASELINE_DA_FT = None  # computed lazily from standard atmosphere
DISTANCE_BOOST_PER_1000FT = 2.75  # ft on ~400 ft fly ball per 1000 ft DA above baseline


def _norm_venue(name: str) -> str:
    return " ".join((name or "").lower().split())


def _load_stadiums() -> dict[str, dict]:
    if not STADIUM_JSON.is_file():
        return {}
    payload = json.loads(STADIUM_JSON.read_text(encoding="utf-8"))
    return payload.get("venues") or {}


def lookup_stadium(venue_name: str) -> dict | None:
    try:
        from research.stadium_db import lookup_stadium_spec

        spec = lookup_stadium_spec(venue_name)
        if spec:
            return spec
    except Exception:
        pass
    key = _norm_venue(venue_name)
    venues = _load_stadiums()
    if key in venues:
        return venues[key]
    for alias, data in venues.items():
        ak = _norm_venue(alias)
        if ak in key or key in ak:
            return data
    return None


def _compass(deg: float | None) -> str:
    if deg is None:
        return "—"
    idx = int((deg + 11.25) / 22.5) % 16
    return COMPASS[idx]


def _normalize_roof(roof: str | None) -> str:
    value = (roof or "open").strip().lower()
    if value in {"dome", "closed"}:
        return "dome"
    if value in {"retractable", "ret"}:
        return "retractable"
    return "open"


def calculate_density_altitude(
    temp_f: float | None,
    relative_humidity: float | None,
    station_pressure_hpa: float | None,
) -> int | None:
    """Density altitude (ft) via 1976 US Standard Atmosphere + Tetens vapor pressure."""
    if temp_f is None or relative_humidity is None or station_pressure_hpa is None:
        return None

    temp_c = (temp_f - 32) * 5 / 9
    temp_k = temp_c + 273.15
    es = 6.11 * math.pow(10, (7.5 * temp_c) / (237.3 + temp_c))
    e = (relative_humidity / 100.0) * es

    r_dry = 287.058
    r_vapor = 461.495
    p_pa = station_pressure_hpa * 100
    p_vapor_pa = e * 100
    p_dry_pa = p_pa - p_vapor_pa

    rho = (p_dry_pa / (r_dry * temp_k)) + (p_vapor_pa / (r_vapor * temp_k))
    alt_meters = (288.15 / 0.0065) * (1.0 - math.pow((rho / RHO_ZERO), DA_EXPONENT))
    return round(alt_meters * 3.28084)


def _baseline_da_ft() -> int:
    global BASELINE_DA_FT
    if BASELINE_DA_FT is None:
        BASELINE_DA_FT = calculate_density_altitude(75, 55, 1013.25) or 0
    return BASELINE_DA_FT


def wind_component_toward_cf(
    wind_from_deg: float | None,
    wind_mph: float | None,
    cf_bearing_deg: float | None,
) -> float | None:
    """Positive = wind blowing out toward center field."""
    if wind_from_deg is None or wind_mph is None or cf_bearing_deg is None:
        return None
    wind_to = (wind_from_deg + 180) % 360
    angle_rad = math.radians(wind_to - cf_bearing_deg)
    return round(float(wind_mph) * math.cos(angle_rad), 1)


def distance_boost_ft(density_alt_ft: int | None, *, baseline_ft: int | None = None) -> float | None:
    if density_alt_ft is None:
        return None
    baseline = _baseline_da_ft() if baseline_ft is None else baseline_ft
    delta = density_alt_ft - baseline
    return round(delta / 1000 * DISTANCE_BOOST_PER_1000FT, 1)


def hr_carry_score(
    *,
    density_alt_ft: int | None = None,
    wind_component_mph: float | None = None,
    roof: str = "open",
) -> tuple[int, str]:
    if _normalize_roof(roof) == "dome":
        return 0, "Dome — weather neutral"

    score = 0
    baseline = _baseline_da_ft()
    if density_alt_ft is not None:
        da_delta = density_alt_ft - baseline
        if da_delta >= 1500:
            score += 3
        elif da_delta >= 800:
            score += 2
        elif da_delta >= 300:
            score += 1
        elif da_delta <= -800:
            score -= 2
        elif da_delta <= -300:
            score -= 1

    if wind_component_mph is not None:
        if wind_component_mph >= 10:
            score += 2
        elif wind_component_mph >= 5:
            score += 1
        elif wind_component_mph <= -10:
            score -= 2
        elif wind_component_mph <= -5:
            score -= 1

    if score >= 2:
        return score, "Helps HR carry"
    if score <= -2:
        return score, "Suppresses carry"
    return score, "Neutral carry"


def build_weather_metrics(
    *,
    temp_f: float | None,
    humidity_pct: float | None,
    pressure_hpa: float | None,
    wind_mph: float | None,
    wind_from_deg: float | None,
    stadium: dict,
    roof: str | None = None,
    precip_pct: float | None = None,
    game_hour_local: str | None = None,
    venue: str | None = None,
) -> dict[str, Any]:
    roof_type = _normalize_roof(roof or stadium.get("roof"))
    bearing = stadium.get("bearing")

    if roof_type == "dome":
        score, label = hr_carry_score(roof=roof_type)
        return {
            "source": "dome-neutral",
            "venue": venue,
            "gameHourLocal": game_hour_local,
            "tempF": 72,
            "humidityPct": 40,
            "windMph": 0,
            "windDirDeg": None,
            "windDir": "—",
            "windComponentMph": 0,
            "pressureHpa": 1013.3,
            "precipPct": precip_pct,
            "roof": roof_type,
            "cfBearing": bearing,
            "densityAltFt": 0,
            "baselineDaFt": _baseline_da_ft(),
            "distanceBoostFt": 0,
            "hrCarryScore": score,
            "hrCarryLabel": label,
        }

    density_alt = calculate_density_altitude(temp_f, humidity_pct, pressure_hpa)
    wind_comp = wind_component_toward_cf(wind_from_deg, wind_mph, bearing)
    dist_boost = distance_boost_ft(density_alt)
    score, label = hr_carry_score(
        density_alt_ft=density_alt,
        wind_component_mph=wind_comp,
        roof=roof_type,
    )

    return {
        "source": "open-meteo",
        "venue": venue,
        "gameHourLocal": game_hour_local,
        "tempF": temp_f,
        "humidityPct": humidity_pct,
        "windMph": None if wind_mph is None else round(float(wind_mph), 1),
        "windDirDeg": None if wind_from_deg is None else round(float(wind_from_deg)),
        "windDir": _compass(wind_from_deg),
        "windComponentMph": wind_comp,
        "pressureHpa": None if pressure_hpa is None else round(float(pressure_hpa), 1),
        "precipPct": precip_pct,
        "roof": roof_type,
        "cfBearing": bearing,
        "densityAltFt": density_alt,
        "baselineDaFt": _baseline_da_ft(),
        "distanceBoostFt": dist_boost,
        "hrCarryScore": score,
        "hrCarryLabel": label,
    }


def fetch_game_hour_weather(
    venue_name: str,
    start_time_iso: str,
    *,
    game_pk: int | None = None,
    mlb_weather: dict | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    stadium = lookup_stadium(venue_name)
    if not stadium:
        return {"error": "unknown_venue", "venue": venue_name}
    if not start_time_iso:
        return {"error": "no_start_time", "venue": venue_name}

    roof_type = _normalize_roof(stadium.get("roof"))
    if roof_type == "dome":
        wx = build_weather_metrics(
            temp_f=None,
            humidity_pct=None,
            pressure_hpa=None,
            wind_mph=None,
            wind_from_deg=None,
            stadium=stadium,
            roof=roof_type,
            venue=venue_name,
        )
        wx["roofStatus"] = {
            "state": "dome",
            "effective": "closed",
            "source": "permanent_dome",
            "confidence": "high",
            "propPass": False,
            "reason": "permanent_dome",
        }
        wx["propPass"] = False
        return wx

    start = datetime.fromisoformat(start_time_iso.replace("Z", "+00:00"))
    tz = ZoneInfo(stadium.get("tz") or "America/New_York")
    local = start.astimezone(tz)
    target_date = local.date().isoformat()
    target_hour = local.hour

    params = urllib.parse.urlencode(
        {
            "latitude": stadium["lat"],
            "longitude": stadium["lon"],
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,precipitation_probability",
            "timezone": stadium.get("tz") or "America/New_York",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "forecast_days": 3,
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    idx = None
    for i, t in enumerate(times):
        if not t.startswith(target_date):
            continue
        hour = int(t[11:13])
        if hour == target_hour:
            idx = i
            break
    if idx is None:
        best_diff = 999
        for i, t in enumerate(times):
            if not t.startswith(target_date):
                continue
            diff = abs(int(t[11:13]) - target_hour)
            if diff < best_diff:
                best_diff = diff
                idx = i

    if idx is None:
        return {"error": "no_forecast_hour", "venue": venue_name}

    temp_f = hourly.get("temperature_2m", [None])[idx]
    humidity_pct = hourly.get("relative_humidity_2m", [None])[idx]
    pressure_hpa = hourly.get("surface_pressure", [None])[idx]
    wind_mph = hourly.get("wind_speed_10m", [None])[idx]
    wind_from_deg = hourly.get("wind_direction_10m", [None])[idx]
    precip_pct = hourly.get("precipitation_probability", [None])[idx]
    wind_comp = wind_component_toward_cf(wind_from_deg, wind_mph, stadium.get("bearing"))

    roof_status: dict[str, Any] | None = None
    effective_roof = "open"
    if roof_type == "retractable":
        from research.roof_status import effective_roof_for_weather, resolve_roof_status

        roof_status = resolve_roof_status(
            venue_name,
            game_pk=game_pk,
            mlb_weather=mlb_weather,
            temp_f=temp_f,
            precip_pct=precip_pct,
            wind_component_mph=wind_comp,
            wind_mph=wind_mph,
        )
        effective_roof = effective_roof_for_weather(roof_status)
    elif roof_type == "open":
        from research.roof_status import resolve_roof_status

        roof_status = resolve_roof_status(
            venue_name,
            wind_component_mph=wind_comp,
            wind_mph=wind_mph,
        )

    wx = build_weather_metrics(
        temp_f=temp_f,
        humidity_pct=humidity_pct,
        pressure_hpa=pressure_hpa,
        wind_mph=wind_mph,
        wind_from_deg=wind_from_deg,
        precip_pct=precip_pct,
        stadium=stadium,
        game_hour_local=times[idx],
        venue=venue_name,
        roof="dome" if effective_roof == "dome" else roof_type,
    )
    if roof_status:
        wx["roofStatus"] = roof_status
        wx["propPass"] = bool(roof_status.get("propPass"))
        if roof_status.get("state") == "closed":
            wx["roof"] = "closed"
    else:
        wx["propPass"] = False
    return wx
