#!/usr/bin/env python3
"""FAB stack: My Slip (bottom), Top/Bottom, Legend on top."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

FAB_STACK_CSS = """        :root {
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
"""

SCROLL_JUMP_NEW = """        .scroll-jump-fab {
            display: flex;
            flex-direction: column;
            align-items: stretch;
            gap: 4px;
        }"""

QUICK_LEGEND_NEW = """        .quick-legend {
            position: static;
            z-index: 1;
            max-width: 220px;
        }"""

LEGEND_RE = re.compile(
    r"\n        <aside class=\"quick-legend\" id=\"quickLegend\"[\s\S]*?</aside>",
)
FAB_STACK_RE = re.compile(r"\n    <motion.div class=\"fab-stack\"[\s\S]*?</div>", re.MULTILINE)
FAB_STACK_RE2 = re.compile(r"\n    <div class=\"fab-stack\"[\s\S]*?</motion.div>", re.MULTILINE)
FAB_STACK_RE3 = re.compile(r"\n    <div class=\"fab-stack\"[\s\S]*?</motion.div>", re.MULTILINE)
FAB_STACK_RE = re.compile(r"\n    <div class=\"fab-stack\"[\s\S]*?</div>", re.MULTILINE)
SLIP_RE = re.compile(r"\n    <button type=\"button\" class=\"my-slip-fab\"[\s\S]*?</button>")
SCROLL_RE = re.compile(r"\n    <div class=\"scroll-jump-fab\"[\s\S]*?</div>")
ROOT_OLD = re.compile(
    r"        :root \{\n            --fab-edge: 12px;\n            --fab-gap: 6px;\n            --fab-slip-h: 40px;\n            --fab-scroll-h: 60px;\n        \}\n",
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    leg_m = LEGEND_RE.search(t)
    legend = (leg_m.group(0) + "\n") if leg_m else ""
    if leg_m:
        t = t[: leg_m.start()] + t[leg_m.end() :]

    fab_m = FAB_STACK_RE.search(t)
    if fab_m:
        t = t[: fab_m.start()] + t[fab_m.end() :]

    slip_m = SLIP_RE.search(t)
    scroll_m = SCROLL_RE.search(t)
    if not slip_m or not scroll_m:
        print("skip (missing fab parts)", path.relative_to(ROOT))
        return

    slip, scroll = slip_m.group(0), scroll_m.group(0)
    t = t[: slip_m.start()] + t[slip_m.end() :]
    scroll_m = SCROLL_RE.search(t)
    if not scroll_m:
        print("skip (scroll missing after slip)", path.relative_to(ROOT))
        return
    scroll = scroll_m.group(0)
    t = t[: scroll_m.start()] + t[scroll_m.end() :]

    stack = (
        '\n    <div class="fab-stack" aria-label="Sheet shortcuts">'
        + slip
        + scroll
        + legend
        + "    </div>\n"
    )
    marker = '\n    <div class="my-slip-backdrop"'
    if marker not in t:
        print("skip (no backdrop marker)", path.relative_to(ROOT))
        return
    t = t.replace(marker, stack + marker, 1)

    if ROOT_OLD.search(t):
        t = ROOT_OLD.sub("", t, count=1)
    if ".fab-stack {" not in t:
        t = t.replace(".my-slip-fab {", FAB_STACK_CSS + "        .my-slip-fab {", 1)

    t = re.sub(r"        \.scroll-jump-fab \{[^}]+\}", SCROLL_JUMP_NEW.strip(), t, count=1)
    t = re.sub(r"        \.quick-legend \{[^}]+\}", QUICK_LEGEND_NEW.strip(), t, count=1)

    if "fab-stack .quick-legend.is-open" not in t:
        t = t.replace(
            "        .quick-legend.is-open .quick-legend-panel { display: block; }",
            "        .quick-legend.is-open .quick-legend-panel { display: block; }\n"
            "        .fab-stack .quick-legend.is-open { z-index: 62; }",
            1,
        )

    t = t.replace(
        ".sheet-toolbar, .scroll-jump-fab, .header-actions",
        ".sheet-toolbar, .fab-stack, .header-actions",
    )

    t = re.sub(
        r"            :root \{ --fab-edge: 10px; --fab-gap: 6px; --fab-slip-h: 40px; --fab-scroll-h: 62px; \}\n"
        r"            \.scroll-jump-fab \{[^}]+\}\n"
        r"            \.scroll-jump-fab__btn",
        "            :root { --fab-edge: 10px; --fab-gap: 6px; }\n"
        "            .fab-stack { right: var(--fab-edge); bottom: var(--fab-edge); }\n"
        "            .scroll-jump-fab__btn",
        t,
        count=1,
    )
    t = re.sub(
        r"\n            \.quick-legend \{ right: var\(--fab-edge\); bottom: calc\([^)]+\); max-width: min\(200px, 46vw\); \}",
        "",
        t,
    )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
