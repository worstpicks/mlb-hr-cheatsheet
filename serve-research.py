#!/usr/bin/env python3
"""Serve preview/ + /api/savant-batter proxy (Savant CSV without browser CORS)."""
from __future__ import annotations

import json
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview"
sys.path.insert(0, str(ROOT))

from research.savant_api import fetch_batter_statcast_lookup  # noqa: E402


class ResearchHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PREVIEW), **kwargs)

    def do_OPTIONS(self) -> None:
        if self._is_savant_api() or self._is_propfinder_api():
            self._send_json(204, {})
            return
        super().do_OPTIONS()

    def do_GET(self) -> None:
        if self._is_savant_api():
            self._handle_savant_api()
            return
        if self._is_propfinder_api():
            self._handle_propfinder_api()
            return
        super().do_GET()

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

    def _is_savant_api(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path == "/api/savant-batter"

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
        body = json.dumps(payload).encode("utf-8")
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
        if self._is_savant_api() or self._is_propfinder_api() or str(args[0]).startswith("2"):
            super().log_message(fmt, *args)


def main() -> None:
    port = 8080
    host = "127.0.0.1"
    server = ThreadingHTTPServer((host, port), ResearchHandler)
    print(f"Serving preview at http://{host}:{port}/")
    print(f"Savant proxy  http://{host}:{port}/api/savant-batter?season=2026")
    print(f"Research      http://{host}:{port}/research/index.html?date=2026-06-22")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
