#!/usr/bin/env python3
"""Apply missing UX HTML fixes (idempotent)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIKKIT = "https://links.pikkit.com/invite/worst"
TARGETS = [ROOT / "preview" / "index.html", ROOT / "index.html"]

GLOBAL_ROW = """            <div class="toolbar-row toolbar-row--global-filters" aria-label="Search and filters">
                <span class="toolbar-title">Find</span>
                <label class="filter-label" for="playerFilter">Player <input type="search" id="playerFilter" placeholder="Search name…" autocomplete="off" enterkeyhint="search"></label>
                <label class="filter-label" for="scoreMinFilter">Min score <input type="number" id="scoreMinFilter" min="0" max="100" placeholder="Any"></label>
                <label class="filter-label" for="gradeFilter">Grade
                    <select id="gradeFilter"><option value="">All</option><option>S+</option><option>S</option><option>A</option><option>B+</option><option>B</option><option>C+</option><option>C</option><option>D</option><option>F</option></select>
                </label>
                <button type="button" class="filter-chip" id="clearAllFiltersBtn">Clear filters</button>
            </div>
"""

OLD_PLAYER_ROW = """            <motion.div class="toolbar-row">
                <label class="filter-label" for="playerFilter">Player <input type="search" id="playerFilter" placeholder="Search name…" autocomplete="off" enterkeyhint="search"></label>
            </div>
""".replace("<motion.div", "<div")

PARLAY_TOOLBAR_OLD = """                    <ul class="parlay-legs" id="parlayLegs" aria-label="Parlay legs, drag to reorder"></ul>
                    <div class="parlay-combined" id="parlayCombined" aria-live="polite"></div>"""

PARLAY_TOOLBAR_NEW = """                    <p class="parlay-disclaimer">Open <strong>My Slip</strong> (bottom-right) to combine odds and export.</p>"""

QUICK_FILTER_PATCH = """                    if (activeQuickFilter === "park" && (parkN == null || parkN < 5)) hide = true;
                    if (activeQuickFilter === "favorites" && !row.classList.contains("pick-row--worst-pickz-fav")) hide = true;
                    if (activeQuickFilter === "moonshot") {
                        let tags = row.getAttribute("data-emoji-tags") || "";
                        try { tags = decodeURIComponent(tags); } catch (e) {}
                        if (!tags.includes("🌕")) hide = true;
                    }
                    row.classList.toggle("quick-filter-hidden", hide);"""

QUICK_FILTER_OLD = """                    if (activeQuickFilter === "park" && (parkN == null || parkN < 5)) hide = true;
                    row.classList.toggle("quick-filter-hidden", hide);"""

TABLE_QUICK_PATCH = """                    if (activeQuickFilter === "park" && (parkN == null || parkN < 5)) hide = true;
                    if (activeQuickFilter === "favorites" && !tr.classList.contains("pick-row--worst-pickz-fav")) hide = true;
                    if (activeQuickFilter === "moonshot") {
                        let tags = tr.getAttribute("data-emoji-tags") || "";
                        try { tags = decodeURIComponent(tags); } catch (e) {}
                        if (!tags.includes("🌕")) hide = true;
                    }
                    tr.classList.toggle("quick-filter-hidden", hide);"""

TABLE_QUICK_OLD = """                    if (activeQuickFilter === "park" && (parkN == null || parkN < 5)) hide = true;
                    tr.classList.toggle("quick-filter-hidden", hide);"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    header = t.split("</header>", 1)[0]
    if PIKKIT not in header:
        t = t.replace(
            '<a class="social-x" href="https://x.com/WorstPickz"',
            f'<a class="pikkit-link" href="{PIKKIT}" target="_blank" rel="noopener noreferrer" title="Track on Pikkit — code WORST">Pikkit</a>\n                <a class="social-x" href="https://x.com/WorstPickz"',
            1,
        )

    if 'id="quickFavBtn"' not in t and OLD_PLAYER_ROW in t:
        t = t.replace(OLD_PLAYER_ROW, GLOBAL_ROW + "\n", 1)

    if PARLAY_TOOLBAR_OLD in t:
        t = t.replace(PARLAY_TOOLBAR_OLD, PARLAY_TOOLBAR_NEW, 1)

    if QUICK_FILTER_OLD in t:
        t = t.replace(QUICK_FILTER_OLD, QUICK_FILTER_PATCH, 1)

    if TABLE_QUICK_OLD in t:
        t = t.replace(TABLE_QUICK_OLD, TABLE_QUICK_PATCH, 1)

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.name)
    else:
        print("ok", path.name)


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
