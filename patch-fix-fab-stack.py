#!/usr/bin/env python3
"""Even spacing for My Slip, Top, and Legend FABs (right-aligned stack)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

FAB_STACK = """        :root {
            --fab-edge: 14px;
            --fab-gap: 12px;
            --fab-slip-h: 50px;
            --fab-top-h: 42px;
        }
"""

TO_TOP_OLD = """        .to-top-fab {
            position: fixed;
            right: 16px;
            bottom: 22px;
            z-index: 60;"""

TO_TOP_NEW = """        .to-top-fab {
            position: fixed;
            right: var(--fab-edge);
            bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap));
            z-index: 60;"""

LEGEND_OLD = """        .quick-legend {
            position: fixed;
            right: 12px;
            bottom: 132px;
            z-index: 55;"""

LEGEND_NEW = """        .quick-legend {
            position: fixed;
            right: var(--fab-edge);
            bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap) + var(--fab-top-h) + var(--fab-gap));
            z-index: 55;"""

SLIP_OLD = "            position: fixed; right: 14px; bottom: 14px; z-index: 80;"
SLIP_NEW = "            position: fixed; right: var(--fab-edge); bottom: var(--fab-edge); z-index: 80;"

REMOVE = "        .to-top-fab { bottom: 58px; }\n"

MEDIA640_OLD = """            .to-top-fab { right: 12px; bottom: 16px; padding: 9px 14px; font-size: 0.78rem; }"""
MEDIA640_NEW = """            :root { --fab-edge: 12px; --fab-gap: 10px; --fab-slip-h: 46px; --fab-top-h: 38px; }
            .to-top-fab { right: var(--fab-edge); bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap)); padding: 9px 14px; font-size: 0.78rem; }
            .my-slip-fab { right: var(--fab-edge); bottom: var(--fab-edge); }"""

MEDIA900_OLD = ".quick-legend { right: 8px; bottom: 128px;"
MEDIA900_NEW = ".quick-legend { right: var(--fab-edge); bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap) + var(--fab-top-h) + var(--fab-gap));"


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if ":root {\n            --fab-edge:" not in t and ".my-slip-fab {" in t:
        t = t.replace("        .my-slip-fab {", FAB_STACK + "        .my-slip-fab {", 1)
    if TO_TOP_OLD in t:
        t = t.replace(TO_TOP_OLD, TO_TOP_NEW, 1)
    if LEGEND_OLD in t:
        t = t.replace(LEGEND_OLD, LEGEND_NEW, 1)
    if SLIP_OLD in t:
        t = t.replace(SLIP_OLD, SLIP_NEW, 1)
    if REMOVE in t:
        t = t.replace(REMOVE, "", 1)
    if MEDIA640_OLD in t:
        t = t.replace(MEDIA640_OLD, MEDIA640_NEW, 1)
    if MEDIA900_OLD in t:
        t = t.replace(MEDIA900_OLD, MEDIA900_NEW, 1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
