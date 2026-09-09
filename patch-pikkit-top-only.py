#!/usr/bin/env python3
"""Remove Pikkit link from My Slip; keep header link only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

BOTTOM = (
    '            <button type="button" class="btn-gambly" id="exportGamblySlip" disabled>Export Gambly</button>\n'
    '            <a class="pikkit-link" href="https://links.pikkit.com/invite/worst" target="_blank" rel="noopener noreferrer">Pikkit</a>\n'
)
BOTTOM_NEW = (
    '            <button type="button" class="btn-gambly" id="exportGamblySlip" disabled>Export Gambly</button>\n'
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if BOTTOM in t:
        t = t.replace(BOTTOM, BOTTOM_NEW, 1)
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
