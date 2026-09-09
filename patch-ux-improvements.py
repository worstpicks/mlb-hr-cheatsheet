#!/usr/bin/env python3
"""UX quick wins + Pikkit + My Slip sidebar."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIKKIT = "https://links.pikkit.com/invite/worst"
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

CSS = """
        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(254, 215, 170, 0.4);
            background: rgba(15, 23, 42, 0.55);
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: rgba(15, 23, 42, 0.88);
            filter: brightness(1.06);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 11px;
        }
        .toolbar-row--global-filters { width: 100%; gap: 8px 12px; align-items: flex-end; }
        #scoreMinFilter, #gradeFilter {
            padding: 7px 8px; border-radius: 10px; border: 1px solid rgba(251, 146, 60, 0.35);
            background: rgba(15, 23, 42, 0.95); color: #f8fafc; font-size: 0.88rem;
            font-weight: 600; min-height: 38px;
        }
        #scoreMinFilter { width: 5.5rem; }
        #gradeFilter { width: 7.5rem; }
        details.game-card { border-radius: 14px; overflow: hidden; scroll-margin-top: 6.5rem; }
        details.game-card > summary.game-header { cursor: pointer; list-style: none; }
        details.game-card > summary.game-header::-webkit-details-marker { display: none; }
        details.game-card > summary.game-header::after {
            content: "▾"; float: right; font-size: 1.1rem; color: #fed7aa;
        }
        details.game-card:not([open]) > summary.game-header::after { content: "▸"; }
        .pick-row.advanced-filter-hidden, .pick-table-row.advanced-filter-hidden { display: none !important; }
        .my-slip-fab {
            position: fixed; right: 14px; bottom: 14px; z-index: 80;
            padding: 12px 16px; border-radius: 999px;
            border: 1px solid rgba(251, 146, 60, 0.5);
            background: linear-gradient(135deg, rgba(180, 83, 9, 0.98) 0%, rgba(127, 29, 29, 0.95) 100%);
            color: #fff7ed; font-weight: 800; font-size: 0.85rem; cursor: pointer;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.45);
        }
        .my-slip-fab:hover { filter: brightness(1.08); }
        .my-slip-fab-count {
            display: inline-block; min-width: 1.25rem; margin-left: 6px;
            padding: 2px 6px; border-radius: 999px; background: rgba(15, 23, 42, 0.65);
            font-variant-numeric: tabular-nums;
        }
        .my-slip-backdrop {
            position: fixed; inset: 0; z-index: 85; background: rgba(0, 0, 0, 0.55);
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
            transform: translateX(100%); transition: transform 0.22s ease;
            visibility: hidden; pointer-events: none;
        }
        .my-slip-panel.is-open { transform: translateX(0); visibility: visible; pointer-events: auto; }
        .my-slip-panel__head {
            display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
            padding: 14px 14px 12px; border-bottom: 1px solid rgba(251, 146, 60, 0.25);
            flex-shrink: 0;
        }
        .my-slip-panel__head h2 { font-size: 1.1rem; color: #fed7aa; margin: 0; }
        .my-slip-panel__head p { font-size: 0.72rem; color: #94a3b8; margin: 4px 0 0; }
        .my-slip-panel__body { flex: 1; overflow: auto; padding: 12px 14px; }
        .my-slip-panel__actions {
            display: flex; flex-wrap: wrap; gap: 8px;
            padding: 12px 14px max(16px, env(safe-area-inset-bottom));
            border-top: 1px solid rgba(251, 146, 60, 0.25); flex-shrink: 0;
        }
        .parlay-leg--empty { cursor: default; opacity: 0.85; font-size: 0.82rem; color: #94a3b8; border-style: dashed; }
        .toolbar-parlay-stack { display: none !important; }
        body.my-slip-open { overflow: hidden; }
        .to-top-fab { bottom: 64px; }
        @media (max-width: 640px) {
            details.game-card:not(.user-opened) { }
            .pikkit-link { font-size: 0.65rem; padding: 0 8px; }
        }
"""

GLOBAL_ROW = '''            <div class="toolbar-row toolbar-row--global-filters" aria-label="Search and filters">
                <span class="toolbar-title">Find</span>
                <label class="filter-label" for="playerFilter">Player <input type="search" id="playerFilter" placeholder="Search name…" autocomplete="off"></label>
                <label class="filter-label" for="scoreMinFilter">Min score <input type="number" id="scoreMinFilter" min="0" max="100" placeholder="Any"></label>
                <label class="filter-label" for="gradeFilter">Grade
                    <select id="gradeFilter"><option value="">All</option><option>S+</option><option>S</option><option>A</option><option>B+</option><option>B</option><option>C+</option><option>C</option><option>D</option><option>F</option></select>
                </label>
                <button type="button" class="filter-chip" id="clearAllFiltersBtn">Clear filters</button>
            </div>'''

MY_SLIP = f'''
    <div class="my-slip-backdrop" id="mySlipBackdrop" hidden></div>
    <aside class="my-slip-panel" id="mySlipPanel" aria-hidden="true">
        <div class="my-slip-panel__head">
            <div><h2>My Slip</h2><p>Saved HR props + combined odds (uncorrelated). Export or track on Pikkit.</p></div>
            <button type="button" class="btn-secondary" id="mySlipClose">Close</button>
        </div>
        <div class="my-slip-panel__body">
            <ul class="parlay-legs" id="parlayLegs"></ul>
            <div class="parlay-combined" id="parlayCombined"></div>
        </div>
        <div class="my-slip-panel__actions">
            <button type="button" class="btn-secondary" id="clearPicksSlip">Clear</button>
            <button type="button" class="btn-gambly" id="exportGamblySlip" disabled>Export Gambly</button>
        </div>
    </aside>
    <button type="button" class="my-slip-fab" id="mySlipFab">My Slip<span class="my-slip-fab-count" id="mySlipFabCount">0</span></button>
'''

JS = r'''
            function syncSheetLiveHeader() {
                const h1 = document.getElementById("sheetLiveTitle");
                const sd = (getSheetDateMeta() || "").trim();
                if (!sd || sd.length < 10) return;
                const p = sd.split("-");
                const d = new Date(+p[0], +p[1] - 1, +p[2]);
                const t = new Date();
                const isToday = t.getFullYear() === d.getFullYear() && t.getMonth() === d.getMonth() && t.getDate() === d.getDate();
                if (h1) h1.textContent = isToday ? "Today's MLB HR Cheat Sheet" : "MLB HR Cheat Sheet";
            }
            function rowPassesAdvancedFilters(el) {
                const score = parseInt(el.getAttribute("data-score") || "0", 10);
                const parkN = el.getAttribute("data-park") === "" ? null : parseInt(el.getAttribute("data-park"), 10);
                const sm = document.getElementById("scoreMinFilter");
                const gf = document.getElementById("gradeFilter");
                if (sm && sm.value !== "" && score < parseInt(sm.value, 10)) return false;
                if (gf && gf.value) {
                    const g = el.querySelector(".letter-box strong");
                    if (!g || g.textContent.trim() !== gf.value) return false;
                }
                if (activeQuickFilter === "elite" && score < 90) return false;
                if (activeQuickFilter === "longshot" && el.getAttribute("data-longshot") !== "1") return false;
                if (activeQuickFilter === "park" && (parkN == null || parkN < 5)) return false;
                if (activeQuickFilter === "favorites" && !el.classList.contains("pick-row--worst-pickz-fav")) return false;
                if (activeQuickFilter === "moonshot") {
                    let tags = el.getAttribute("data-emoji-tags") || "";
                    try { tags = decodeURIComponent(tags); } catch (e) {}
                    if (!tags.includes("🌕")) return false;
                }
                if (activeEmojiFilters.size) {
                    let tags = el.getAttribute("data-emoji-tags") || "";
                    try { tags = decodeURIComponent(tags); } catch (e) {}
                    if ([...activeEmojiFilters].some((ch) => !tags.includes(ch))) return false;
                }
                return true;
            }
            function applyRowVisibilityFilters() {
                document.querySelectorAll(".game-card .pick-row, tr.pick-table-row").forEach((el) => {
                    const q = (document.getElementById("playerFilter")?.value || "").trim().toLowerCase();
                    let name = "";
                    if (el.matches("tr")) {
                        try { name = decodeURIComponent(el.getAttribute("data-player") || "").toLowerCase(); } catch (e) { name = ""; }
                    } else {
                        name = (el.querySelector(".pick-name-open, .pick-name")?.textContent || "").toLowerCase();
                    }
                    const nameOk = !q || name.includes(q);
                    const adv = rowPassesAdvancedFilters(el);
                    el.classList.toggle("pick-hidden", !nameOk);
                    el.classList.toggle("advanced-filter-hidden", nameOk && !adv);
                });
                document.querySelectorAll("details.game-card").forEach((card) => {
                    const vis = [...card.querySelectorAll(".pick-row")].some((r) =>
                        !r.classList.contains("pick-hidden") && !r.classList.contains("advanced-filter-hidden") &&
                        !r.classList.contains("quick-filter-hidden") && !r.classList.contains("emoji-filter-hidden"));
                    card.style.display = vis ? "" : "none";
                });
            }
            function syncMobileGameCards() {
                const mob = window.matchMedia("(max-width: 640px)").matches;
                document.querySelectorAll("details.game-card").forEach((d) => {
                    if (!d.classList.contains("user-opened")) d.open = !mob;
                });
            }
            function openMySlip() {
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
            }
            function wireUxEnhancements() {
                syncSheetLiveHeader();
                syncMobileGameCards();
                window.addEventListener("resize", syncMobileGameCards);
                document.querySelectorAll("details.game-card").forEach((d) => {
                    d.addEventListener("toggle", () => d.classList.add("user-opened"));
                });
                document.getElementById("mySlipFab")?.addEventListener("click", openMySlip);
                document.getElementById("mySlipClose")?.addEventListener("click", closeMySlip);
                document.getElementById("mySlipBackdrop")?.addEventListener("click", closeMySlip);
                document.getElementById("exportGamblySlip")?.addEventListener("click", () => document.getElementById("exportGambly")?.click());
                document.getElementById("clearPicksSlip")?.addEventListener("click", () => document.getElementById("clearPicks")?.click());
                const run = () => { applyRowVisibilityFilters(); updatePickCount(); };
                document.getElementById("scoreMinFilter")?.addEventListener("input", run);
                document.getElementById("gradeFilter")?.addEventListener("change", run);
                document.getElementById("playerFilter")?.addEventListener("input", run);
                document.getElementById("clearAllFiltersBtn")?.addEventListener("click", () => {
                    const pf = document.getElementById("playerFilter");
                    if (pf) pf.value = "";
                    const sm = document.getElementById("scoreMinFilter");
                    if (sm) sm.value = "";
                    const gf = document.getElementById("gradeFilter");
                    if (gf) gf.value = "";
                    activeQuickFilter = "all";
                    activeEmojiFilters.clear();
                    document.querySelectorAll("#emojiFilterRow .filter-chip[data-emoji]").forEach((b) => {
                        b.classList.remove("is-active"); b.setAttribute("aria-pressed", "false");
                    });
                    document.querySelectorAll("#quickFilterRow .filter-chip").forEach((c) => c.classList.toggle("is-active", c.getAttribute("data-filter") === "all"));
                    run();
                });
                const origQuick = applyQuickFilterAll;
                applyQuickFilterAll = function () { origQuick(); applyRowVisibilityFilters(); };
                const origEmoji = applyEmojiFiltersToAll;
                applyEmojiFiltersToAll = function () { origEmoji(); applyRowVisibilityFilters(); };
                const origApplyPlayer = applyPlayerFilter;
                applyPlayerFilter = function () { applyRowVisibilityFilters(); };
                const origUpdate = updatePickCount;
                updatePickCount = function () {
                    origUpdate();
                    const gamblyFabKeys = new Set();
                    document.querySelectorAll(".pick-cb.pick-cb--gambly:checked").forEach((cb) => {
                        const r = cb.closest(".pick-row[data-gi][data-ri]");
                        if (r) gamblyFabKeys.add(`${r.getAttribute("data-gi")}|${r.getAttribute("data-ri")}`);
                    });
                    const n = gamblyFabKeys.size;
                    const c = document.getElementById("mySlipFabCount");
                    if (c) c.textContent = String(n);
                    const se = document.getElementById("exportGamblySlip");
                    const eg = document.getElementById("exportGambly");
                    if (se && eg) se.disabled = eg.disabled;
                };
                document.querySelectorAll(".emoji-key-item strong, .quick-legend-item").forEach((el) => {
                    const tip = el.closest("[title]")?.title || el.parentElement?.title;
                    if (!el.parentElement?.title && el.textContent) el.parentElement.title = el.textContent.trim();
                });
                run();
            }
'''


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if ".pikkit-link" not in t:
        t = t.replace("@media print {", CSS + "\n        @media print {", 1)

    header = t.split("</header>", 1)[0]
    if PIKKIT not in header:
        t = t.replace(
            '<a class="social-x" href="https://x.com/WorstPickz"',
            '                <a class="pikkit-link" href="' + PIKKIT + '" target="_blank" rel="noopener noreferrer" aria-label="Track on Pikkit — code WORST" title="Track on Pikkit — code WORST">'
            '<img class="pikkit-link__icon" src="assets/pikkit-icon.svg" width="42" height="42" alt="" decoding="async"></a>\n'
            '                <a class="social-x" href="https://x.com/WorstPickz"',
            1,
        )

    if "sheetLiveTitle" not in t:
        t = t.replace(
            "<h1>Worst Pickz Cheat Daily MLB Sheet</h1>",
            '<h1 id="sheetLiveTitle">Worst Pickz Cheat Daily MLB Sheet</h1>',
            1,
        )

    old = '            <div class="toolbar-row">\n                <label class="filter-label" for="playerFilter">Player <input type="search" id="playerFilter"'
    if old in t and 'id="quickFavBtn"' not in t:
        t = t.replace(
            '            <div class="toolbar-row">\n                <label class="filter-label" for="playerFilter">Player <input type="search" id="playerFilter" placeholder="Search name…" autocomplete="off" enterkeyhint="search"></label>\n            </div>\n',
            GLOBAL_ROW + "\n",
            1,
        )

    if 'data-filter="favorites"' not in t:
        t = t.replace(
            '<button type="button" class="filter-chip" data-filter="park">Park boost +5%</button>',
            '<button type="button" class="filter-chip" data-filter="park">Park boost +5%</button>\n                    <button type="button" class="filter-chip" data-filter="favorites">⭐ Favorites</button>\n                    <button type="button" class="filter-chip" data-filter="moonshot">🌕 Moonshots</button>',
            1,
        )

    if "quick-filter-hidden" in t and "favorites" not in t.split("activeQuickFilter")[1][:500] if "activeQuickFilter" in t else "":
        pass

    if 'id="mySlipFab"' not in t:
        t = t.replace("</body>", MY_SLIP + "\n</body>", 1)

    if '<article class="game-card"' in t:
        t = t.replace('<article class="game-card"', '<details class="game-card" open')
        t = t.replace('<motion.div class="game-header">', '<summary class="game-header">')
        t = t.replace('<div class="game-header">', '<summary class="game-header">')
        t = t.replace('</p></div><div class="pick-list">', '</p></summary><div class="pick-list">')
        t = t.replace("</article>`", "</details>`")

    if "function wireUxEnhancements" not in t:
        t = t.replace(
            "            if (filterInput) {",
            JS + "\n            wireUxEnhancements();\n            if (filterInput) {",
            1,
        )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.name)
    else:
        print("unchanged", path.name)


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
