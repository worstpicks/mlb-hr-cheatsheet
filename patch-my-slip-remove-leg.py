#!/usr/bin/env python3
"""Add per-leg remove (×) buttons to My Slip parlay list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

CSS_BLOCK = """        .parlay-leg .parlay-leg-label { flex: 1; min-width: 0; }
        .parlay-leg-remove {
            flex-shrink: 0;
            width: 26px;
            height: 26px;
            border: none;
            border-radius: 6px;
            background: rgba(248, 113, 113, 0.15);
            color: #fca5a5;
            font-size: 1.05rem;
            line-height: 1;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0;
        }
        .parlay-leg-remove:hover { background: rgba(248, 113, 113, 0.32); color: #fff; }
        .parlay-leg-remove:focus-visible { outline: 2px solid #fb923c; outline-offset: 1px; }
        html.theme-light .parlay-leg-remove { background: rgba(220, 38, 38, 0.12); color: #b91c1c; }
        html.theme-light .parlay-leg-remove:hover { background: rgba(220, 38, 38, 0.22); color: #7f1d1d; }
"""

HELPER = """            function removeParlayLeg(gi, ri) {
                document.querySelectorAll(`.pick-row[data-gi="${gi}"][data-ri="${ri}"] .pick-cb.pick-cb--gambly`).forEach((cb) => {
                    cb.checked = false;
                });
                updatePickCount();
            }
            function wireMySlipLegRemove() {
                const ul = mySlipParlayLegsEl();
                if (!ul || ul.dataset.removeWired === "1") return;
                ul.dataset.removeWired = "1";
                ul.addEventListener("click", (e) => {
                    const btn = e.target.closest(".parlay-leg-remove");
                    if (!btn) return;
                    e.preventDefault();
                    e.stopPropagation();
                    const li = btn.closest("li.parlay-leg");
                    if (!li || li.classList.contains("parlay-leg--empty")) return;
                    const gi = li.getAttribute("data-gi");
                    const ri = li.getAttribute("data-ri");
                    if (gi == null || ri == null) return;
                    removeParlayLeg(gi, ri);
                });
            }
"""

OLD_LEG_HTML = (
    'return `<li class="parlay-leg" draggable="true" data-gi="${gi}" data-ri="${ri}" data-american="${amAttr}">'
    '<span class="parlay-drag-hint" aria-hidden="true">↕</span><span>${escapeHtml(nm)}</span>'
    '<span class="parlay-leg-odds">${escapeHtml(amTxt)}</span></li>`;'
)

NEW_LEG_HTML = (
    'return `<li class="parlay-leg" draggable="true" data-gi="${gi}" data-ri="${ri}" data-american="${amAttr}">'
    '<span class="parlay-drag-hint" aria-hidden="true">↕</span>'
    '<span class="parlay-leg-label">${escapeHtml(nm)}</span>'
    '<span class="parlay-leg-odds">${escapeHtml(amTxt)}</span>'
    '<button type="button" class="parlay-leg-remove" aria-label="Remove ${escapeHtml(nm)} from slip">×</button></li>`;'
)

DRAG_WIRE_OLD = """                    li.addEventListener("dragstart", (e) => {
                        dragEl = li;"""

DRAG_WIRE_NEW = """                    li.addEventListener("dragstart", (e) => {
                        if (e.target.closest(".parlay-leg-remove")) {
                            e.preventDefault();
                            return;
                        }
                        dragEl = li;"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if ".parlay-leg-remove" not in t:
        t = t.replace(
            "        .parlay-leg .parlay-leg-odds { margin-left: auto; font-weight: 900; color: #a7f3d0; font-variant-numeric: tabular-nums; }",
            "        .parlay-leg .parlay-leg-odds { margin-left: auto; font-weight: 900; color: #a7f3d0; font-variant-numeric: tabular-nums; }\n"
            + CSS_BLOCK,
            1,
        )

    if "function removeParlayLeg(" not in t:
        t = t.replace(
            "            function rebuildParlayPanel() {",
            HELPER + "            function rebuildParlayPanel() {",
            1,
        )

    if OLD_LEG_HTML in t:
        t = t.replace(OLD_LEG_HTML, NEW_LEG_HTML, 1)

    if DRAG_WIRE_OLD in t and "parlay-leg-remove" not in t.split("dragstart", 1)[1][:120]:
        t = t.replace(DRAG_WIRE_OLD, DRAG_WIRE_NEW, 1)

    if "wireMySlipLegRemove();" not in t:
        t = t.replace(
            "            wireMySlipControls();",
            "            wireMySlipControls();\n                wireMySlipLegRemove();",
            1,
        )
        if "wireMySlipLegRemove();" not in t:
            t = t.replace(
                "            wireUxEnhancements();\n            wireMySlipControls();",
                "            wireUxEnhancements();\n            wireMySlipControls();\n            wireMySlipLegRemove();",
                1,
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
