#!/usr/bin/env python3
"""Fix My Slip: slide-out panel on FAB click (CSS was missing)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

CSS_ANCHOR = "        .toolbar-parlay {"
MY_SLIP_CSS = """        .my-slip-fab {
            position: fixed; right: 14px; bottom: 14px; z-index: 80;
            padding: 12px 16px; border-radius: 999px;
            border: 1px solid rgba(251, 146, 60, 0.5);
            background: linear-gradient(135deg, rgba(180, 83, 9, 0.98) 0%, rgba(127, 29, 29, 0.95) 100%);
            color: #fff7ed; font-weight: 800; font-size: 0.85rem; cursor: pointer;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.45);
        }
        .my-slip-fab:hover { filter: brightness(1.08); }
        .my-slip-fab:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .my-slip-fab-count {
            display: inline-block; min-width: 1.25rem; margin-left: 6px;
            padding: 2px 6px; border-radius: 999px; background: rgba(15, 23, 42, 0.65);
            font-variant-numeric: tabular-nums;
        }
        .my-slip-backdrop {
            position: fixed; inset: 0; z-index: 85;
            background: rgba(0, 0, 0, 0.55);
            opacity: 0; pointer-events: none; transition: opacity 0.2s ease;
        }
        .my-slip-backdrop.is-open { opacity: 1; pointer-events: auto; }
        .my-slip-panel {
            position: fixed; top: 0; right: 0; z-index: 90;
            width: min(100%, 360px); height: 100%; max-height: 100dvh;
            display: flex; flex-direction: column;
            background: linear-gradient(180deg, #0f172a 0%, #1e0a0a 100%);
            border-left: 2px solid rgba(251, 146, 60, 0.45);
            box-shadow: -12px 0 40px rgba(0, 0, 0, 0.5);
            transform: translateX(100%);
            transition: transform 0.22s ease;
            visibility: hidden;
            pointer-events: none;
        }
        .my-slip-panel.is-open {
            transform: translateX(0);
            visibility: visible;
            pointer-events: auto;
        }
        .my-slip-panel__head {
            display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
            padding: 14px 14px 12px; border-bottom: 1px solid rgba(251, 146, 60, 0.25);
            flex-shrink: 0;
        }
        .my-slip-panel__head h2 { font-size: 1.1rem; color: #fed7aa; margin: 0; }
        .my-slip-panel__head p { font-size: 0.72rem; color: #94a3b8; margin: 4px 0 0; line-height: 1.35; }
        .my-slip-panel__body {
            flex: 1; overflow: auto; padding: 12px 14px;
            -webkit-overflow-scrolling: touch;
        }
        .my-slip-panel__body .parlay-legs { margin: 0; }
        .my-slip-panel__body .parlay-combined { margin-top: 10px; }
        .my-slip-panel__actions {
            display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 14px max(16px, env(safe-area-inset-bottom));
            border-top: 1px solid rgba(251, 146, 60, 0.25);
            flex-shrink: 0;
        }
        .my-slip-panel__actions .btn-gambly,
        .my-slip-panel__actions .btn-secondary { flex: 1; min-width: 7rem; }
        .parlay-leg--empty {
            cursor: default; opacity: 0.85; font-size: 0.82rem; color: #94a3b8;
            border-style: dashed;
        }
        .toolbar-parlay-stack { display: none !important; }
        body.my-slip-open { overflow: hidden; }
        .to-top-fab { bottom: 64px; }
        html.theme-light .my-slip-panel {
            background: linear-gradient(180deg, #fff7ed 0%, #ffedd5 100%);
            border-left-color: rgba(234, 88, 12, 0.35);
        }
        html.theme-light .my-slip-panel__head h2 { color: #9a3412; }
        html.theme-light .my-slip-panel__head p { color: #64748b; }
        html.theme-light .my-slip-fab {
            color: #fff7ed;
            border-color: rgba(234, 88, 12, 0.45);
        }
        @media (prefers-reduced-motion: reduce) {
            .my-slip-panel, .my-slip-backdrop { transition: none; }
        }
        """

OPEN_OLD = """            function openMySlip() {
                document.getElementById("mySlipPanel")?.classList.add("is-open");
                const b = document.getElementById("mySlipBackdrop");
                if (b) { b.hidden = false; b.classList.add("is-open"); }
                document.getElementById("mySlipFab")?.setAttribute("aria-expanded", "true");
                rebuildParlayPanel();
            }
            function closeMySlip() {
                document.getElementById("mySlipPanel")?.classList.remove("is-open");
                const b = document.getElementById("mySlipBackdrop");
                if (b) { b.hidden = true; b.classList.remove("is-open"); }
                document.getElementById("mySlipFab")?.setAttribute("aria-expanded", "false");
            }"""

OPEN_NEW = """            function openMySlip() {
                const panel = document.getElementById("mySlipPanel");
                const b = document.getElementById("mySlipBackdrop");
                const fab = document.getElementById("mySlipFab");
                rebuildParlayPanel();
                if (panel) {
                    panel.classList.add("is-open");
                    panel.setAttribute("aria-hidden", "false");
                }
                if (b) {
                    b.hidden = false;
                    b.classList.add("is-open");
                }
                if (fab) fab.setAttribute("aria-expanded", "true");
                document.body.classList.add("my-slip-open");
            }
            function closeMySlip() {
                const panel = document.getElementById("mySlipPanel");
                const b = document.getElementById("mySlipBackdrop");
                const fab = document.getElementById("mySlipFab");
                if (panel) {
                    panel.classList.remove("is-open");
                    panel.setAttribute("aria-hidden", "true");
                }
                if (b) {
                    b.hidden = true;
                    b.classList.remove("is-open");
                }
                if (fab) fab.setAttribute("aria-expanded", "false");
                document.body.classList.remove("my-slip-open");
            }"""

REBUILD_OLD_START = """            function rebuildParlayPanel() {
                const panel = document.getElementById("parlayPanel");
                const ul = document.getElementById("parlayLegs");
                if (!panel || !ul) return;"""

REBUILD_NEW_START = """            function rebuildParlayPanel() {
                const ul = document.getElementById("parlayLegs");
                const sumEl = document.getElementById("parlayCombined");
                if (!ul) return;"""

REBUILD_EMPTY_OLD = """                if (!rows.length) {
                    panel.hidden = true;
                    ul.innerHTML = "";
                    recalcParlayFromUl();
                    return;
                }
                panel.hidden = false;"""

REBUILD_EMPTY_NEW = """                if (!rows.length) {
                    ul.innerHTML = '<li class="parlay-leg parlay-leg--empty">No picks yet — use <strong>Add to Gambly</strong> on any row, then open My Slip here.</li>';
                    if (sumEl) sumEl.textContent = "";
                    recalcParlayFromUl();
                    return;
                }"""

ESCAPE_LISTENER = """                document.getElementById("clearPicksSlip")?.addEventListener("click", () => document.getElementById("clearPicks")?.click());
                document.addEventListener("keydown", (e) => {
                    if (e.key === "Escape" && document.getElementById("mySlipPanel")?.classList.contains("is-open")) closeMySlip();
                });"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if ".my-slip-panel {" not in t and CSS_ANCHOR in t:
        t = t.replace(CSS_ANCHOR, MY_SLIP_CSS + CSS_ANCHOR, 1)

    if OPEN_OLD in t:
        t = t.replace(OPEN_OLD, OPEN_NEW, 1)

    if REBUILD_OLD_START in t:
        t = t.replace(REBUILD_OLD_START, REBUILD_NEW_START, 1)

    if REBUILD_EMPTY_OLD in t:
        t = t.replace(REBUILD_EMPTY_OLD, REBUILD_EMPTY_NEW, 1)

    if 'e.key === "Escape" && document.getElementById("mySlipPanel")' not in t and 'document.getElementById("clearPicksSlip")' in t:
        t = t.replace(
            'document.getElementById("clearPicksSlip")?.addEventListener("click", () => document.getElementById("clearPicks")?.click());',
            ESCAPE_LISTENER,
            1,
        )

  # Keep toolbar export buttons in DOM but hidden via CSS
    if 'id="exportGambly"' not in t.split("mySlipPanel")[0]:
        pass  # export still in hidden toolbar row

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
