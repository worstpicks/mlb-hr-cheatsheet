#!/usr/bin/env python3
"""Exclude void/DNP batters from Batters Won and Batters with Hits counts."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

HELPERS = """
            function pickRowHrResultState(rowEl) {
                const pill = rowEl.querySelector(".hr-row-result__pill");
                if (!pill) return "none";
                if (pill.classList.contains("hr-row-result__pill--win")) return "win";
                if (pill.classList.contains("hr-row-result__pill--loss")) return "loss";
                if (pill.classList.contains("hr-row-result__pill--void")) return "void";
                if (pill.classList.contains("hr-row-result__pill--pending")) return "pending";
                if (pill.classList.contains("hr-row-result__pill--na")) return "na";
                return "other";
            }
            function isListedHr05PickRow(rowEl) {
                const gi = parseInt(rowEl.getAttribute("data-gi") || "", 10);
                const ri = parseInt(rowEl.getAttribute("data-ri") || "", 10);
                const row = games[gi] && games[gi].rows[ri];
                return !!(row && /Over\\s*0\\.5\\s*HR/i.test(row.odds || ""));
            }
            function countActiveSheetBatters() {
                let active = 0;
                document.querySelectorAll(".game-card .pick-row").forEach((rowEl) => {
                    if (!isListedHr05PickRow(rowEl)) return;
                    const st = pickRowHrResultState(rowEl);
                    if (st === "win" || st === "loss" || st === "pending") active++;
                });
                return active;
            }
            function filterHitNamesToActivePlayers(names) {
                const allowed = new Set();
                document.querySelectorAll(".game-card .pick-row").forEach((rowEl) => {
                    if (!isListedHr05PickRow(rowEl)) return;
                    const st = pickRowHrResultState(rowEl);
                    if (st !== "win" && st !== "loss") return;
                    const gi = parseInt(rowEl.getAttribute("data-gi") || "", 10);
                    const ri = parseInt(rowEl.getAttribute("data-ri") || "", 10);
                    const row = games[gi] && games[gi].rows[ri];
                    if (row) allowed.add(cleanBatterDisplayName(row.name));
                });
                return (names || []).map(cleanBatterDisplayName).filter((n) => allowed.has(n));
            }
"""

UPDATE_START = "            function updateBattersWonRecap() {"
UPDATE_END = "\n            let hrResultsHydrateToken"

NEW_UPDATE = (
    HELPERS
    + """
            function updateBattersWonRecap() {
                const section = document.getElementById("battersWonSection");
                const listEl = document.getElementById("battersWonList");
                const ledeEl = document.getElementById("battersWonLede");
                if (!section || !listEl || !ledeEl) return;
                section.hidden = false;
                const wins = [];
                let pending = 0;
                let settled = 0;
                document.querySelectorAll(".game-card .pick-row").forEach((rowEl) => {
                    if (!isListedHr05PickRow(rowEl)) return;
                    const st = pickRowHrResultState(rowEl);
                    if (st === "pending") pending++;
                    else if (st === "win" || st === "loss" || st === "void") settled++;
                    if (st !== "win") return;
                    const gi = parseInt(rowEl.getAttribute("data-gi") || "", 10);
                    const ri = parseInt(rowEl.getAttribute("data-ri") || "", 10);
                    const game = games[gi];
                    const row = game && game.rows[ri];
                    if (!row || !game) return;
                    wins.push({
                        name: row.name,
                        odds: row.odds,
                        score: row.score,
                        matchup: matchupShort(game.title),
                        fav: isWorstPickzFavoriteRow(row),
                    });
                });
                const activeBatters = countActiveSheetBatters();
                wins.sort((a, b) => b.score - a.score);
                if (wins.length) {
                    ledeEl.textContent =
                        wins.length +
                        " of " +
                        activeBatters +
                        " active batters homered (Over 0.5 HR cashed — void/DNP excluded).";
                    listEl.innerHTML = wins
                        .map((w) => {
                            const favCls = w.fav ? " batters-won-item--fav" : "";
                            const favTag = w.fav ? " ⭐" : "";
                            return (
                                '<li class="batters-won-item' +
                                favCls +
                                '"><span class="batters-won-name">' +
                                escapeHtml(w.name) +
                                favTag +
                                '</span><span class="batters-won-meta"><small>' +
                                escapeHtml(w.matchup) +
                                "</small> · Listed " +
                                escapeHtml(listedOddsLabel(w.odds)) +
                                '</span><strong class="batters-won-score">' +
                                w.score +
                                "</strong></li>"
                            );
                        })
                        .join("");
                    return;
                }
                listEl.innerHTML = "";
                if (pending > 0) {
                    ledeEl.textContent =
                        "No homers recorded yet for active props — " +
                        pending +
                        " still waiting on final box scores (" +
                        settled +
                        " settled, void/DNP excluded from totals).";
                } else if (activeBatters > 0) {
                    ledeEl.textContent =
                        "None of the " + activeBatters + " active batters hit Over 0.5 HR on this slate.";
                } else {
                    ledeEl.textContent = "No active batters to score yet (all void/DNP or still loading).";
                }
            }
"""
)

OLD_HIT_STATUS = re.compile(
    r"            function battersHitStatusText\(names\) \{\n"
    r"                return names\.length \? `\$\{names\.length\} cheat-sheet batter\$\{names\.length === 1 \? \"\" : \"s\"\} recorded a hit\.` : \"No cheat-sheet batters with hits yet\.\";\n"
    r"            \}",
)

NEW_HIT_STATUS = """
            function battersHitStatusText(names, activeCount) {
                const hits = (names || []).length;
                const active = typeof activeCount === "number" && activeCount > 0 ? activeCount : 0;
                if (!hits) {
                    return active
                        ? "No cheat-sheet batters with hits yet (" + active + " active on slate)."
                        : "No cheat-sheet batters with hits yet.";
                }
                if (active) {
                    return hits + " of " + active + " active cheat-sheet batter" + (active === 1 ? "" : "s") + " recorded a hit.";
                }
                return hits + " cheat-sheet batter" + (hits === 1 ? "" : "s") + " recorded a hit.";
            }"""

OLD_HITS_PUSH = (
    "                        if (typeof r.hits === \"number\" && r.hits >= 1) {\n"
    "                            hitNames.push(row.name);\n"
    "                        }"
)

NEW_HITS_PUSH = (
    "                        if ((r.code === \"win\" || r.code === \"loss\") && typeof r.hits === \"number\" && r.hits >= 1) {\n"
    "                            hitNames.push(row.name);\n"
    "                        }"
)

OLD_FINAL_HITS = re.compile(
    r"                updateBattersWonRecap\(\);\n"
    r"                if \(token !== hrResultsHydrateToken\) return;\n"
    r"                const finalHitNames = hitNames\.length \? hitNames : staticHitNames;\n"
    r"                renderBattersHitSummary\(finalHitNames, battersHitStatusText\(finalHitNames\)\);",
)

NEW_FINAL_HITS = (
    "                updateBattersWonRecap();\n"
    "                if (token !== hrResultsHydrateToken) return;\n"
    "                const activeBatters = countActiveSheetBatters();\n"
    "                const finalHitNames = hitNames.length\n"
    "                    ? hitNames\n"
    "                    : filterHitNamesToActivePlayers(staticHitNames);\n"
    "                renderBattersHitSummary(finalHitNames, battersHitStatusText(finalHitNames, activeBatters));"
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "function updateBattersWonRecap" not in text:
        return False
    orig = text
    if "function countActiveSheetBatters" not in text:
        s = text.find(UPDATE_START)
        e = text.find(UPDATE_END, s)
        if s == -1 or e == -1:
            return False
        text = text[:s] + NEW_UPDATE + text[e:]
    text = OLD_HIT_STATUS.sub(NEW_HIT_STATUS, text, count=1)
    if OLD_HITS_PUSH in text:
        text = text.replace(OLD_HITS_PUSH, NEW_HITS_PUSH, 1)
    text = OLD_FINAL_HITS.sub(NEW_FINAL_HITS, text, count=1)
    # early static render passes active count when helpers exist
    text = text.replace(
        'renderBattersHitSummary(staticHitNames, staticHitNames.length ? battersHitStatusText(staticHitNames) :',
        'renderBattersHitSummary(staticHitNames, staticHitNames.length ? battersHitStatusText(staticHitNames, countActiveSheetBatters()) :',
        1,
    )
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    targets = [ROOT / "preview" / "index.html", ROOT / "index.html"]
    targets.extend(sorted((ROOT / "preview" / "archive").glob("*.html")))
    n = 0
    for path in targets:
        if path.is_file() and patch_file(path):
            print("patched", path.relative_to(ROOT))
            n += 1
    if not n:
        print("no files changed")
    else:
        print(f"done — {n} file(s)")


if __name__ == "__main__":
    main()
