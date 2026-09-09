"""Shared patch targets: current index + all archive sheets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE_HTML = sorted((ROOT / "preview" / "archive").glob("2026-*.html"))
SHEET_HTML = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    *ARCHIVE_HTML,
]
