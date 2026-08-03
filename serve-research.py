#!/usr/bin/env python3
"""Serve preview/ + /api/savant-batter proxy (Savant CSV without browser CORS)."""
from __future__ import annotations

import datetime
import json
import os
import re
import socket
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview"
sys.path.insert(0, str(ROOT))

SERVER_STARTED_AT = datetime.datetime.now().isoformat(timespec="seconds")
CODE_MTIME = datetime.datetime.fromtimestamp(
    Path(__file__).stat().st_mtime
).isoformat(timespec="seconds")

from research.savant_api import fetch_batter_statcast_lookup, fetch_pitcher_game_trends, fetch_player_game_trends  # noqa: E402


class ResearchHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PREVIEW), **kwargs)

    def do_OPTIONS(self) -> None:
        if (
            self._is_savant_api()
            or self._is_trends_api()
            or self._is_pitcher_trends_api()
            or self._is_propfinder_api()
            or self._is_savant_matchup_api()
            or self._is_rotowire_api()
            or self._is_projected_pitchers_api()
            or self._is_zone_api()
            or self._is_park_api()
            or self._is_player_detail_api()
        ):
            self._send_json(204, {})
            return
        super().do_OPTIONS()

    def do_GET(self) -> None:
        if urlparse(self.path).path.rstrip("/") == "/api/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "pid": os.getpid(),
                    "startedAt": SERVER_STARTED_AT,
                    "codeMtime": CODE_MTIME,
                },
            )
            return
        if self._is_savant_api():
            self._handle_savant_api()
            return
        if self._is_trends_api():
            self._handle_trends_api()
            return
        if self._is_pitcher_trends_api():
            self._handle_pitcher_trends_api()
            return
        if self._is_propfinder_api():
            self._handle_propfinder_api()
            return
        if self._is_savant_matchup_api():
            self._handle_savant_matchup_api()
            return
        if self._is_rotowire_api():
            self._handle_rotowire_api()
            return
        if self._is_projected_pitchers_api():
            self._handle_projected_pitchers_api()
            return
        if self._is_zone_api():
            self._handle_zone_api()
            return
        if self._is_park_api():
            self._handle_park_api()
            return
        if self._is_player_detail_api():
            self._handle_player_detail_api()
            return
        super().do_GET()

    def _is_player_detail_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/savant-player-detail"

    def _handle_player_detail_api(self) -> None:
        """Run the deployed Netlify handler so local matches production."""
        qs = parse_qs(urlparse(self.path).query)
        player_id = qs.get("playerId", [""])[0]
        if not player_id.isdigit():
            self._send_json(400, {"error": "playerId required"})
            return
        query = {"playerId": player_id}
        role = qs.get("role", [""])[0]
        if role in ("batter", "pitcher"):
            query["role"] = role
        season = qs.get("season", [""])[0]
        if re.fullmatch(r"\d{4}(?:[,|]\d{4})*", season or ""):
            query["season"] = season
        fn = ROOT / "tools" / "invoke-netlify-function.js"
        try:
            proc = subprocess.run(
                ["node", str(fn), "savant-player-detail", json.dumps(query)],
                capture_output=True,
                timeout=120,
            )
        except FileNotFoundError:
            self._send_json(501, {"error": "node not on PATH — needed for /api/savant-player-detail"})
            return
        except subprocess.TimeoutExpired:
            self._send_json(504, {"error": "savant-player-detail timed out"})
            return
        body = proc.stdout.decode("utf-8", "replace")
        if not body.strip():
            err = proc.stderr.decode("utf-8", "replace").strip() or "empty response"
            self._send_json(502, {"error": err})
            return
        self._send_raw_json(200 if proc.returncode == 0 else 502, body)

    def _is_rotowire_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/rotowire-lineups"

    def _handle_rotowire_api(self) -> None:
        from research.rotowire_lineups import build_rotowire_payload

        qs = parse_qs(urlparse(self.path).query)
        sheet_date = qs.get("date", [""])[0]
        if not sheet_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
            self._send_json(400, {"error": "invalid date"})
            return
        try:
            payload = build_rotowire_payload(sheet_date)
            self._send_json(200, payload)
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_projected_pitchers_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/projected-pitchers"

    def _handle_projected_pitchers_api(self) -> None:
        from research.projected_pitchers import build_projected_pitchers_payload

        qs = parse_qs(urlparse(self.path).query)
        sheet_date = qs.get("date", [""])[0]
        if not sheet_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
            self._send_json(400, {"error": "invalid date"})
            return
        try:
            payload = build_projected_pitchers_payload(sheet_date)
            self._send_json(200, payload)
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_propfinder_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/propfinder"

    def _handle_propfinder_api(self) -> None:
        from research.propfinder_stats import load_propfinder_lookup

        qs = parse_qs(urlparse(self.path).query)
        sheet_date = qs.get("date", [""])[0]
        if not sheet_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
            self._send_json(400, {"error": "invalid date"})
            return
        try:
            lookup = load_propfinder_lookup(sheet_date)
            self._send_json(
                200,
                {
                    "date": sheet_date,
                    "source": "propfinder-csv",
                    "batters": len(lookup),
                    "lookup": lookup,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_savant_matchup_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/savant-matchup"

    def _handle_savant_matchup_api(self) -> None:
        from research.matchup_edge import fetch_savant_matchup, matchup_pair_key

        qs = parse_qs(urlparse(self.path).query)
        batter_id = qs.get("batterId", [""])[0]
        pitcher_id = qs.get("pitcherId", [""])[0]
        if not batter_id.isdigit() or not pitcher_id.isdigit():
            self._send_json(400, {"error": "batterId and pitcherId required"})
            return
        try:
            entry = fetch_savant_matchup(int(batter_id), int(pitcher_id))
            if not entry:
                self._send_json(200, {"key": matchup_pair_key(batter_id, pitcher_id), "matchup": None})
                return
            self._send_json(
                200,
                {
                    "key": matchup_pair_key(batter_id, pitcher_id),
                    "source": "savant-matchup",
                    "matchup": entry,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_park_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/park-factors"

    def _handle_park_api(self) -> None:
        from research.park_factors import load_park_lookup

        qs = parse_qs(urlparse(self.path).query)
        sheet_date = qs.get("date", [""])[0]
        if not sheet_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
            self._send_json(400, {"error": "invalid date"})
            return
        try:
            lookup = load_park_lookup(sheet_date)
            self._send_json(
                200,
                {
                    "date": sheet_date,
                    "venues": len(lookup.get("by_venue") or {}),
                    "games": len(lookup.get("by_game") or {}),
                    **lookup,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_zone_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/zone-matchups"

    def _handle_zone_api(self) -> None:
        from zone_matchups import load_zone_lookup

        from research.mlb_api import _serialize_zone_lookup

        qs = parse_qs(urlparse(self.path).query)
        sheet_date = qs.get("date", [""])[0]
        if not sheet_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
            self._send_json(400, {"error": "invalid date"})
            return
        try:
            lookup = _serialize_zone_lookup(load_zone_lookup(sheet_date))
            self._send_json(
                200,
                {
                    "date": sheet_date,
                    "source": "zone-matchups-csv",
                    "matchups": len(lookup),
                    "lookup": lookup,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_savant_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/savant-batter"

    def _is_trends_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/player-trends"

    def _handle_trends_api(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        try:
            player_id = int(qs.get("playerId", [""])[0])
            season = int(qs.get("season", ["2026"])[0])
            limit = int(qs.get("limit", ["30"])[0])
        except ValueError:
            self._send_json(400, {"error": "invalid playerId, season, or limit"})
            return
        if player_id <= 0 or limit <= 0 or limit > 60:
            self._send_json(400, {"error": "invalid playerId or limit"})
            return
        try:
            games = fetch_player_game_trends(player_id, season, limit=min(limit, 60))
            self._send_json(
                200,
                {
                    "playerId": player_id,
                    "season": season,
                    "source": "mlb-game-log",
                    "games": games,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _is_pitcher_trends_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/pitcher-trends"

    def _handle_pitcher_trends_api(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        try:
            player_id = int(qs.get("playerId", [""])[0])
            season = int(qs.get("season", ["2026"])[0])
            limit = int(qs.get("limit", ["30"])[0])
        except ValueError:
            self._send_json(400, {"error": "invalid playerId, season, or limit"})
            return
        if player_id <= 0 or limit <= 0 or limit > 60:
            self._send_json(400, {"error": "invalid playerId or limit"})
            return
        try:
            games = fetch_pitcher_game_trends(player_id, season, limit=min(limit, 60))
            self._send_json(
                200,
                {
                    "playerId": player_id,
                    "season": season,
                    "source": "mlb-pitching-game-log",
                    "games": games,
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _handle_savant_api(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        try:
            season = int(qs.get("season", ["2026"])[0])
        except ValueError:
            self._send_json(400, {"error": "invalid season"})
            return
        try:
            lookup = fetch_batter_statcast_lookup(season)
            self._send_json(
                200,
                {
                    "season": season,
                    "source": "savant-csv-proxy",
                    "batters": len(lookup),
                    "lookup": {str(k): v for k, v in lookup.items()},
                },
            )
        except Exception as exc:
            self._send_json(502, {"error": str(exc)})

    def _send_json(self, code: int, payload: dict) -> None:
        self._send_raw_json(code, json.dumps(payload))

    def _send_raw_json(self, code: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        if (
            self._is_savant_api()
            or self._is_trends_api()
            or self._is_pitcher_trends_api()
            or self._is_propfinder_api()
            or self._is_savant_matchup_api()
            or self._is_rotowire_api()
            or self._is_projected_pitchers_api()
            or self._is_zone_api()
            or self._is_park_api()
            or str(args[0]).startswith("2")
        ):
            super().log_message(fmt, *args)


class ExclusiveHTTPServer(ThreadingHTTPServer):
    # On Windows, SO_REUSEADDR lets a second server bind the same port and
    # silently serve stale code. Disable it so a double start fails loudly.
    allow_reuse_address = False


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((host, port)) == 0


def main() -> None:
    port = 8080
    host = "127.0.0.1"
    if _port_in_use(host, port):
        print(f"ERROR: something is already listening on {host}:{port}.")
        print("A stale serve-research.py may be running with old code. Kill it first:")
        print("  Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*serve-research*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
        sys.exit(1)
    server = ExclusiveHTTPServer((host, port), ResearchHandler)
    print(f"serve-research.py pid={os.getpid()} started={SERVER_STARTED_AT} code-mtime={CODE_MTIME}")
    print(f"Serving preview at http://{host}:{port}/")
    print(f"Health check  http://{host}:{port}/api/health")
    print(f"Savant proxy  http://{host}:{port}/api/savant-batter?season=2026")
    print(f"Player trends http://{host}:{port}/api/player-trends?playerId=592450&season=2026")
    print(f"Pitcher trends http://{host}:{port}/api/pitcher-trends?playerId=605483&season=2026")
    print(f"Research      http://{host}:{port}/research/index.html?date=2026-06-22")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
