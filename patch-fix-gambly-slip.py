#!/usr/bin/env python3
"""Fix Gambly Add + My Slip: unique parlay DOM ids and reliable click handling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

HELPER = """            function mySlipParlayLegsEl() {
                return document.getElementById("mySlipLegs");
            }
            function mySlipParlayCombinedEl() {
                return document.getElementById("mySlipCombined");
            }
            function handleGamblyPickButtonClick(e) {
                const gamblyBtn = e.target.closest(".gambly-pick-btn");
                if (!gamblyBtn) return;
                const zone = gamblyBtn.closest("#gamesSection");
                if (!zone) return;
                e.preventDefault();
                const wrap = gamblyBtn.closest(".gambly-pick-wrap");
                const cb = wrap && wrap.querySelector(".pick-cb.pick-cb--gambly");
                if (!cb) return;
                cb.checked = !cb.checked;
                syncGamblyPickRowCheckboxesFrom(cb);
                updatePickCount();
            }
"""

OLD_CLICK_BLOCK = """            if (gamesSection) {
                gamesSection.addEventListener("click", (e) => {
                    const gamblyBtn = e.target.closest(".gambly-pick-btn");
                    if (gamblyBtn && gamesSection.contains(gamblyBtn)) {
                        e.preventDefault();
                        const wrap = gamblyBtn.closest(".gambly-pick-wrap");
                        const cb = wrap && wrap.querySelector(".pick-cb.pick-cb--gambly");
                        if (cb) {
                            cb.checked = !cb.checked;
                            syncGamblyPickRowCheckboxesFrom(cb);
                            updatePickCount();
                        }
                        return;
                    }
                    const betSave = e.target.closest(".bet-tracker-save-btn");"""

NEW_CLICK_BLOCK = """            document.addEventListener("click", handleGamblyPickButtonClick);
            if (gamesSection) {
                gamesSection.addEventListener("click", (e) => {
                    const betSave = e.target.closest(".bet-tracker-save-btn");"""

ROW_FILTER_OLD = (
    '!r.classList.contains("pick-hidden") && !r.classList.contains("quick-filter-hidden") '
    '&& !r.classList.contains("emoji-filter-hidden")'
)
ROW_FILTER_NEW = (
    '!r.classList.contains("pick-hidden") && !r.classList.contains("quick-filter-hidden") '
    '&& !r.classList.contains("emoji-filter-hidden") && !r.classList.contains("advanced-filter-hidden")'
)


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if 'id="mySlipLegs"' not in t:
        t = t.replace(
            '<div class="my-slip-panel__body">\n            <ul class="parlay-legs" id="parlayLegs"></ul>\n            <div class="parlay-combined" id="parlayCombined"></div>',
            '<div class="my-slip-panel__body">\n            <ul class="parlay-legs" id="mySlipLegs"></ul>\n            <div class="parlay-combined" id="mySlipCombined"></div>',
            1,
        )

    if 'id="parlayLegsToolbar"' not in t:
        t = t.replace(
            '<ul class="parlay-legs" id="parlayLegs" aria-label="Parlay legs, drag to reorder"></ul>',
            '<ul class="parlay-legs" id="parlayLegsToolbar" aria-label="Parlay legs, drag to reorder"></ul>',
            1,
        )
        t = t.replace(
            '<div class="parlay-combined" id="parlayCombined" aria-live="polite"></div>',
            '<div class="parlay-combined" id="parlayCombinedToolbar" aria-live="polite"></div>',
            1,
        )

    if "function mySlipParlayLegsEl()" not in t:
        anchor = "            function recalcParlayFromUl() {"
        if anchor not in t:
            raise SystemExit(f"missing anchor in {path}")
        t = t.replace(anchor, HELPER + anchor, 1)

    t = t.replace(
        'const ul = document.getElementById("parlayLegs");\n                const sumEl = document.getElementById("parlayCombined");',
        'const ul = mySlipParlayLegsEl();\n                const sumEl = mySlipParlayCombinedEl();',
    )
    t = t.replace(
        'const ul = document.getElementById("parlayLegs");\n                const sumEl = document.getElementById("parlayCombined");',
        'const ul = mySlipParlayLegsEl();\n                const sumEl = mySlipParlayCombinedEl();',
        1,
    )
    t = t.replace(
        'const ul = document.getElementById("parlayLegs");\n                if (!ul) return;',
        'const ul = mySlipParlayLegsEl();\n                const sumEl = mySlipParlayCombinedEl();\n                if (!ul) return;',
        1,
    )

    if OLD_CLICK_BLOCK in t:
        t = t.replace(OLD_CLICK_BLOCK, NEW_CLICK_BLOCK, 1)
    elif "handleGamblyPickButtonClick" not in t:
        print("warn: gambly click block not found in", path.name)

    if ROW_FILTER_NEW not in t:
        t = t.replace(ROW_FILTER_OLD, ROW_FILTER_NEW)

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
