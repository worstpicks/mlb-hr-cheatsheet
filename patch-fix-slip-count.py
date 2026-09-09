#!/usr/bin/env python3
"""My Slip FAB count: dedupe card+table checkboxes per row."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

OLD = """                    const n = document.querySelectorAll(".pick-cb.pick-cb--gambly:checked").length;
                    const c = document.getElementById("mySlipFabCount");"""

NEW = """                    const gamblyFabKeys = new Set();
                    document.querySelectorAll(".pick-cb.pick-cb--gambly:checked").forEach((cb) => {
                        const r = cb.closest(".pick-row[data-gi][data-ri]");
                        if (r) gamblyFabKeys.add(`${r.getAttribute("data-gi")}|${r.getAttribute("data-ri")}`);
                    });
                    const n = gamblyFabKeys.size;
                    const c = document.getElementById("mySlipFabCount");"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if OLD in t:
        path.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
