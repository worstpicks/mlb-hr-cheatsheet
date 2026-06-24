#!/usr/bin/env python3
"""Canonical MLB stadium geolocation, dimensions, and roof parameters."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STADIUM_JSON = ROOT / "preview" / "data" / "stadium-coords.json"

# wall distances (ft), wall heights (ft), CF compass bearing (deg from home plate)
# Pull alleys default from lcf (RHB) / rcf (LHB) unless overridden.
_STADIUM_SPECS: dict[str, dict] = {
    "truist park": {"lat": 33.8907, "lon": -84.4678, "bearing": 23, "roof": "open", "tz": "America/New_York", "walls": {"lf": 335, "lcf": 380, "cf": 400, "rcf": 375, "rf": 325}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "loandepot park": {"lat": 25.7781, "lon": -80.2197, "bearing": 56, "roof": "retractable", "tz": "America/New_York", "walls": {"lf": 315, "lcf": 362, "cf": 409, "rcf": 373, "rf": 326}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "citi field": {"lat": 40.7571, "lon": -73.8458, "bearing": 45, "roof": "open", "tz": "America/New_York", "walls": {"lf": 335, "lcf": 370, "cf": 408, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "citizens bank park": {"lat": 39.9061, "lon": -75.1665, "bearing": 45, "roof": "open", "tz": "America/New_York", "walls": {"lf": 329, "lcf": 374, "cf": 401, "rcf": 369, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "nationals park": {"lat": 38.873, "lon": -77.0074, "bearing": 34, "roof": "open", "tz": "America/New_York", "walls": {"lf": 336, "lcf": 377, "cf": 402, "rcf": 370, "rf": 335}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "wrigley field": {"lat": 41.9484, "lon": -87.6553, "bearing": 45, "roof": "open", "tz": "America/Chicago", "walls": {"lf": 355, "lcf": 368, "cf": 400, "rcf": 368, "rf": 353}, "heights": {"lf": 11, "cf": 11, "rf": 11}},
    "great american ball park": {"lat": 39.0979, "lon": -84.5082, "bearing": 135, "roof": "open", "tz": "America/New_York", "walls": {"lf": 328, "lcf": 370, "cf": 404, "rcf": 370, "rf": 325}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "american family field": {"lat": 43.028, "lon": -87.9712, "bearing": 68, "roof": "retractable", "tz": "America/Chicago", "walls": {"lf": 344, "lcf": 370, "cf": 400, "rcf": 374, "rf": 345}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "pnc park": {"lat": 40.4469, "lon": -80.0057, "bearing": 68, "roof": "open", "tz": "America/New_York", "walls": {"lf": 325, "lcf": 375, "cf": 399, "rcf": 365, "rf": 320}, "heights": {"lf": 6, "cf": 10, "rf": 21}},
    "busch stadium": {"lat": 38.6226, "lon": -90.1928, "bearing": 124, "roof": "open", "tz": "America/Chicago", "walls": {"lf": 336, "lcf": 375, "cf": 400, "rcf": 375, "rf": 335}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "chase field": {"lat": 33.4453, "lon": -112.0667, "bearing": 0, "roof": "retractable", "tz": "America/Phoenix", "walls": {"lf": 330, "lcf": 376, "cf": 407, "rcf": 376, "rf": 334}, "heights": {"lf": 7, "cf": 25, "rf": 7}},
    "coors field": {"lat": 39.7559, "lon": -104.9942, "bearing": 15, "roof": "open", "tz": "America/Denver", "walls": {"lf": 347, "lcf": 390, "cf": 415, "rcf": 375, "rf": 350}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "dodger stadium": {"lat": 34.0739, "lon": -118.24, "bearing": 23, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 330, "lcf": 375, "cf": 395, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "petco park": {"lat": 32.7073, "lon": -117.1567, "bearing": 23, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 334, "lcf": 387, "cf": 396, "rcf": 382, "rf": 322}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "oracle park": {"lat": 37.7786, "lon": -122.3893, "bearing": 23, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 339, "lcf": 399, "cf": 399, "rcf": 415, "rf": 309}, "heights": {"lf": 25, "cf": 8, "rf": 25}, "pullL": {"dist": 309, "bearing": 45}, "pullR": {"dist": 399, "bearing": 0}},
    "oriole park at camden yards": {"lat": 39.284, "lon": -76.6202, "bearing": 45, "roof": "open", "tz": "America/New_York", "walls": {"lf": 333, "lcf": 364, "cf": 400, "rcf": 373, "rf": 318}, "heights": {"lf": 7, "cf": 7, "rf": 7}},
    "fenway park": {"lat": 42.3467, "lon": -71.0972, "bearing": 45, "roof": "open", "tz": "America/New_York", "walls": {"lf": 310, "lcf": 379, "cf": 420, "rcf": 380, "rf": 302}, "heights": {"lf": 37, "cf": 17, "rf": 3}, "pullL": {"dist": 302, "bearing": 90}, "pullR": {"dist": 310, "bearing": 0}},
    "yankee stadium": {"lat": 40.8296, "lon": -73.9262, "bearing": 56, "roof": "open", "tz": "America/New_York", "walls": {"lf": 318, "lcf": 399, "cf": 408, "rcf": 385, "rf": 314}, "heights": {"lf": 8, "cf": 8, "rf": 8}, "pullL": {"dist": 314, "bearing": 101}, "pullR": {"dist": 318, "bearing": 11}},
    "tropicana field": {"lat": 27.7682, "lon": -82.6534, "bearing": 0, "roof": "dome", "tz": "America/New_York", "walls": {"lf": 315, "lcf": 370, "cf": 404, "rcf": 370, "rf": 322}, "heights": {"lf": 9, "cf": 9, "rf": 9}},
    "rogers centre": {"lat": 43.6414, "lon": -79.3894, "bearing": 0, "roof": "retractable", "tz": "America/Toronto", "walls": {"lf": 328, "lcf": 375, "cf": 400, "rcf": 375, "rf": 328}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "guaranteed rate field": {"lat": 41.8299, "lon": -87.6337, "bearing": 45, "roof": "open", "tz": "America/Chicago", "walls": {"lf": 330, "lcf": 375, "cf": 400, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "progressive field": {"lat": 41.4962, "lon": -81.6852, "bearing": 45, "roof": "open", "tz": "America/New_York", "walls": {"lf": 325, "lcf": 370, "cf": 400, "rcf": 375, "rf": 325}, "heights": {"lf": 19, "cf": 8, "rf": 19}},
    "comerica park": {"lat": 42.339, "lon": -83.0485, "bearing": 45, "roof": "open", "tz": "America/Detroit", "walls": {"lf": 345, "lcf": 370, "cf": 420, "rcf": 365, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "kauffman stadium": {"lat": 39.0517, "lon": -94.4803, "bearing": 45, "roof": "open", "tz": "America/Chicago", "walls": {"lf": 330, "lcf": 375, "cf": 410, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "target field": {"lat": 44.9817, "lon": -93.2778, "bearing": 45, "roof": "open", "tz": "America/Chicago", "walls": {"lf": 339, "lcf": 377, "cf": 404, "rcf": 367, "rf": 328}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "minute maid park": {"lat": 29.7573, "lon": -95.3555, "bearing": 34, "roof": "retractable", "tz": "America/Chicago", "walls": {"lf": 315, "lcf": 362, "cf": 409, "rcf": 373, "rf": 326}, "heights": {"lf": 19, "cf": 8, "rf": 7}},
    "angel stadium": {"lat": 33.8003, "lon": -117.8827, "bearing": 45, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 330, "lcf": 370, "cf": 396, "rcf": 370, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "oakland coliseum": {"lat": 37.7516, "lon": -122.2005, "bearing": 23, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 330, "lcf": 375, "cf": 400, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "t mobile park": {"lat": 47.5914, "lon": -122.3325, "bearing": 45, "roof": "retractable", "tz": "America/Los_Angeles", "walls": {"lf": 331, "lcf": 378, "cf": 401, "rcf": 378, "rf": 326}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "globe life field": {"lat": 32.7473, "lon": -97.0842, "bearing": 0, "roof": "retractable", "tz": "America/Chicago", "walls": {"lf": 329, "lcf": 372, "cf": 407, "rcf": 374, "rf": 326}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
    "sutter health park": {"lat": 38.5805, "lon": -121.4997, "bearing": 45, "roof": "open", "tz": "America/Los_Angeles", "walls": {"lf": 330, "lcf": 375, "cf": 400, "rcf": 375, "rf": 330}, "heights": {"lf": 8, "cf": 8, "rf": 8}},
}

_ALIASES: dict[str, str] = {
    "rate field": "guaranteed rate field",
    "daikin park": "minute maid park",
    "t-mobile park": "t mobile park",
    "tampa bay times forum": "tropicana field",
}


def _norm(name: str) -> str:
    return " ".join((name or "").lower().split())


def lookup_stadium_spec(venue_name: str) -> dict | None:
    key = _norm(venue_name)
    key = _ALIASES.get(key, key)
    if key in _STADIUM_SPECS:
        spec = dict(_STADIUM_SPECS[key])
        spec["mlbName"] = venue_name
        return spec
    for alias, target in _ALIASES.items():
        if alias in key or key in alias:
            spec = dict(_STADIUM_SPECS[target])
            spec["mlbName"] = venue_name
            return spec
    for name, spec in _STADIUM_SPECS.items():
        if name in key or key in name:
            out = dict(spec)
            out["mlbName"] = venue_name
            return out
    return None


def export_stadium_json(path: Path | None = None) -> None:
    venues: dict[str, dict] = {}
    for key, spec in _STADIUM_SPECS.items():
        entry = dict(spec)
        entry["mlbName"] = key.title() if key != "loandepot park" else "loanDepot park"
        venues[key] = entry
    for alias, target in _ALIASES.items():
        if alias not in venues and target in _STADIUM_SPECS:
            venues[alias] = dict(_STADIUM_SPECS[target])
            venues[alias]["mlbName"] = venues[target]["mlbName"] if target in venues else target
    out_path = path or STADIUM_JSON
    out_path.write_text(json.dumps({"venues": venues}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_stadium_json()
    print(f"Wrote {STADIUM_JSON}")
