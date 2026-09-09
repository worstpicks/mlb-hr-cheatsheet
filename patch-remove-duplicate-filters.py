#!/usr/bin/env python3
"""Remove duplicate quick filters (Favorites/Parks/Moonshots) from Find row."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

HTML_BTNS = (
    '                <button type="button" class="filter-chip" id="quickFavBtn">⭐ Favorites</button>\n'
    '                <button type="button" class="filter-chip" id="quickParkBtn">🏟️ Parks</button>\n'
    '                <button type="button" class="filter-chip" id="quickMoonBtn">🌕 Moonshots</button>\n'
)

JS_OLD = """                function toggleQuick(mode, btn) {
                    activeQuickFilter = activeQuickFilter === mode ? "all" : mode;
                    document.querySelectorAll("#quickFilterRow .filter-chip, #quickFavBtn, #quickParkBtn, #quickMoonBtn").forEach((c) => c.classList.remove("is-active"));
                    if (activeQuickFilter !== "all" && btn) btn.classList.add("is-active");
                    if (activeQuickFilter === "all") document.querySelector('#quickFilterRow [data-filter="all"]')?.classList.add("is-active");
                    applyQuickFilterAll(); run();
                }
                document.getElementById("quickFavBtn")?.addEventListener("click", function () { toggleQuick("favorites", this); });
                document.getElementById("quickParkBtn")?.addEventListener("click", function () { toggleQuick("park", this); });
                document.getElementById("quickMoonBtn")?.addEventListener("click", function () { toggleQuick("moonshot", this); });
"""

QUICK_ROW_RUN = """                quickFilterRow.addEventListener("click", (e) => {
                    const chip = e.target.closest(".filter-chip");
                    if (!chip) return;
                    activeQuickFilter = chip.getAttribute("data-filter") || "all";
                    quickFilterRow.querySelectorAll(".filter-chip").forEach((c) => c.classList.toggle("is-active", c === chip));
                    applyQuickFilterAll();
                });"""

QUICK_ROW_RUN_NEW = """                quickFilterRow.addEventListener("click", (e) => {
                    const chip = e.target.closest(".filter-chip");
                    if (!chip) return;
                    activeQuickFilter = chip.getAttribute("data-filter") || "all";
                    quickFilterRow.querySelectorAll(".filter-chip").forEach((c) => c.classList.toggle("is-active", c === chip));
                    applyQuickFilterAll();
                    if (typeof applyRowVisibilityFilters === "function") applyRowVisibilityFilters();
                });"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if HTML_BTNS in t:
        t = t.replace(HTML_BTNS, "", 1)
    if JS_OLD in t:
        t = t.replace(JS_OLD, "", 1)
    if QUICK_ROW_RUN in t and QUICK_ROW_RUN_NEW not in t:
        t = t.replace(QUICK_ROW_RUN, QUICK_ROW_RUN_NEW, 1)
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
