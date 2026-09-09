#!/usr/bin/env python3
"""Fix FAB stack CSS after legend-above-top patch."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

BROKEN_MEDIA = re.compile(
    r"        @media \(max-width: 640px\) \{\n"
    r"            :root \{ --fab-edge: 10px; --fab-gap: 6px; \}\n"
    r"            \.fab-stack \{ right: var\(--fab-edge\); bottom: var\(--fab-edge\); \}\n"
    r"            \.scroll-jump-fab__btn \{ padding: 7px 12px; font-size: 0\.74rem; \}\n"
    r"                    :root \{\n"
    r"            --fab-edge: 12px;\n"
    r"            --fab-gap: 6px;\n"
    r"        \}\n"
    r"        \.fab-stack \{\n"
    r"            position: fixed;\n"
    r"            right: var\(--fab-edge\);\n"
    r"            bottom: var\(--fab-edge\);\n"
    r"            z-index: 60;\n"
    r"            display: flex;\n"
    r"            flex-direction: column-reverse;\n"
    r"            align-items: flex-end;\n"
    r"            gap: var\(--fab-gap\);\n"
    r"        \}\n"
    r"        \.my-slip-fab \{ right: var\(--fab-edge\); bottom: var\(--fab-edge\); \}\n"
    r"        \}",
)

FAB_ROOT_STACK = """        :root {
            --fab-edge: 12px;
            --fab-gap: 6px;
        }
        .fab-stack {
            position: fixed;
            right: var(--fab-edge);
            bottom: var(--fab-edge);
            z-index: 60;
            display: flex;
            flex-direction: column-reverse;
            align-items: flex-end;
            gap: var(--fab-gap);
        }
        @media (max-width: 640px) {
            :root { --fab-edge: 10px; --fab-gap: 6px; }
            .fab-stack { right: var(--fab-edge); bottom: var(--fab-edge); }
            .scroll-jump-fab__btn { padding: 7px 12px; font-size: 0.74rem; }
        }"""

MY_SLIP_OLD = re.compile(
    r"        \.my-slip-fab \{\n"
    r"            position: fixed; right: var\(--fab-edge\); bottom: var\(--fab-edge\); z-index: 80;\n",
)

MY_SLIP_NEW = """        .my-slip-fab {
            position: static;
            z-index: 1;
"""

LEGEND_900_OLD = (
    "        @media (max-width: 900px) {\n"
    "            .quick-legend { right: var(--fab-edge); bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap) + var(--fab-scroll-h) + var(--fab-gap)); max-width: min(200px, 46vw); }\n"
    "        }"
)

LEGEND_900_NEW = """        @media (max-width: 900px) {
            .fab-stack .quick-legend { max-width: min(200px, 46vw); }
        }"""

SCROLL_INDENT = ".scroll-jump-fab {"
SCROLL_INDENT_FIX = "        .scroll-jump-fab {"
QUICK_INDENT = ".quick-legend {"
QUICK_INDENT_FIX = "        .quick-legend {"


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if BROKEN_MEDIA.search(t):
        t = BROKEN_MEDIA.sub(FAB_ROOT_STACK, t, count=1)
    elif ".fab-stack {" not in t:
        t = t.replace(SCROLL_INDENT_FIX, FAB_ROOT_STACK + "\n" + SCROLL_INDENT_FIX, 1)

    if MY_SLIP_OLD.search(t):
        t = MY_SLIP_OLD.sub(MY_SLIP_NEW, t, count=1)

    if LEGEND_900_OLD in t:
        t = t.replace(LEGEND_900_OLD, LEGEND_900_NEW, 1)

    t = t.replace(SCROLL_INDENT, SCROLL_INDENT_FIX, 1)
    t = t.replace(QUICK_INDENT, QUICK_INDENT_FIX, 1)

    t = re.sub(
        r"\n            \.quick-legend \{ right: var\(--fab-edge\); bottom: calc\([^)]+\); max-width: min\(200px, 46vw\); \}",
        "",
        t,
    )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
