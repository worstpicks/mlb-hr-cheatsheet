#!/usr/bin/env python3
"""Inject Batters Won recap at top-left of cheat sheet HTML files."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

CSS_BLOCK = """
        .batters-won-section {
            padding: 14px;
            margin: 0;
            background: linear-gradient(135deg, rgba(6, 48, 32, 0.94) 0%, rgba(10, 17, 28, 0.96) 55%, rgba(14, 10, 20, 0.95) 100%);
            border-top: 1px solid rgba(34, 197, 94, 0.28);
            border-bottom: 1px solid rgba(251, 146, 60, 0.14);
            min-width: 0;
        }
        .batters-won-section[hidden] {
            display: none !important;
        }
        .batters-won-panel {
            border-color: rgba(34, 197, 94, 0.45);
            background: rgba(15, 23, 42, 0.5);
            padding: 14px;
        }
        .batters-won-panel h2 {
            color: #86efac;
            font-size: inherit;
            margin: 0 0 0.5rem;
            letter-spacing: 0.7px;
            text-transform: uppercase;
        }
        .batters-won-lede {
            margin: 0 0 12px;
            color: var(--wpz-color-paragraph);
            font-size: 0.92rem;
            line-height: 1.45;
            max-width: 72ch;
        }
        .batters-won-list {
            list-style: none;
            margin: 0;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
            gap: 10px;
        }
        .batters-won-item {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 2px 12px;
            align-items: center;
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(34, 197, 94, 0.28);
            min-width: 0;
        }
        .batters-won-item--fav {
            border-color: rgba(244, 63, 94, 0.5);
            box-shadow: inset 3px 0 0 rgba(244, 63, 94, 0.85);
        }
        .batters-won-name {
            font-weight: 800;
            color: #ecfdf5;
            font-size: 0.95rem;
        }
        .batters-won-meta {
            grid-column: 1;
            font-size: 0.76rem;
            color: rgba(226, 232, 240, 0.78);
        }
        .batters-won-meta small {
            opacity: 0.9;
        }
        .batters-won-score {
            grid-row: 1 / span 2;
            grid-column: 2;
            font-size: 1.1rem;
            color: #86efac;
        }
        html.theme-light .batters-won-section {
            background: linear-gradient(135deg, #ecfdf5 0%, #f1f5f9 50%, #e8eef7 100%);
            border-top-color: rgba(22, 163, 74, 0.35);
        }
        html.theme-light .batters-won-panel {
            border-color: rgba(22, 163, 74, 0.45);
            background: rgba(255, 255, 255, 0.72);
        }
        html.theme-light .batters-won-panel h2 { color: #15803d; }
        html.theme-light .batters-won-item {
            background: rgba(255, 255, 255, 0.9);
            border-color: rgba(22, 163, 74, 0.35);
        }
        html.theme-light .batters-won-name { color: #14532d; }
        html.theme-light .batters-won-meta { color: #334155; }
        html.theme-light .batters-won-score { color: #15803d; }
"""

HTML_BLOCK = """
        <section class="batters-won-section" id="battersWonSection" aria-labelledby="battersWonHeading">
            <div class="panel batters-won-panel">
                <h2 id="battersWonHeading">Batters Won</h2>
                <p class="batters-won-lede" id="battersWonLede" aria-live="polite">Checking homers from MLB box scores…</p>
                <ol class="batters-won-list" id="battersWonList"></ol>
            </div>
        </section>
"""

JS_BLOCK = """
            function listedOddsLabel(oddsStr) {
                const n = parseListedNumber(oddsStr);
                if (n == null) return String(oddsStr || "").replace(/^Listed\\s*/i, "").trim();
                return n > 0 ? "+" + n : String(n);
            }
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
                    const pill = rowEl.querySelector(".hr-row-result__pill");
                    if (!pill) return;
                    if (pill.classList.contains("hr-row-result__pill--pending")) pending++;
                    else if (
                        pill.classList.contains("hr-row-result__pill--win") ||
                        pill.classList.contains("hr-row-result__pill--loss") ||
                        pill.classList.contains("hr-row-result__pill--void")
                    ) {
                        settled++;
                    }
                    if (!pill.classList.contains("hr-row-result__pill--win")) return;
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
                const totalProps = games.reduce((n, g) => n + (g.rows ? g.rows.length : 0), 0);
                wins.sort((a, b) => b.score - a.score);
                if (wins.length) {
                    ledeEl.textContent =
                        wins.length +
                        " of " +
                        totalProps +
                        " listed batters homered (Over 0.5 HR cashed per MLB box score).";
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
                        "No homers recorded yet for listed props — " +
                        pending +
                        " still waiting on final box scores (" +
                        settled +
                        " settled).";
                } else {
                    ledeEl.textContent =
                        "None of the " + totalProps + " listed batters hit Over 0.5 HR on this slate.";
                }
            }
"""

ARCHIVE_ONLY_GATE = """                if (!isArchiveSheetPage()) {
                    section.hidden = true;
                    return;
                }
"""

OLD_HTML_BLOCK_RE = re.compile(
    r'\n\s*<section class="batters-won-section"[^>]*id="battersWonSection"[^>]*>.*?</section>\n',
    re.DOTALL,
)


def inject_css(text: str) -> str:
    if ".batters-won-section {" in text:
        if ".batters-won-section--top" in text:
            text = text.replace(
                "        .batters-won-section--top {\n            order: -1;\n        }\n",
                "",
                1,
            )
            text = re.sub(
                r"(\.batters-won-section \{[^}]*margin:\s*)0 0 14px",
                r"\114px 0 0",
                text,
                count=1,
            )
        else:
            return text
    if ".batters-won-section {" in text:
        old = re.search(
            r"        \.batters-won-section \{.*?html\.theme-light \.batters-won-score \{ color: #[^;]+; \}\n",
            text,
            re.DOTALL,
        )
        if old:
            text = text.replace(old.group(0), "", 1)
    marker = "        .hr-row-result__pill--na .hr-row-result__pill-value {\n"
    if marker not in text:
        return text
    return text.replace(
        marker,
        CSS_BLOCK + "\n" + marker,
        1,
    )


def inject_html(text: str) -> str:
    if 'id="battersWonSection"' in text:
        return text
    m = re.search(
        r'(<section class="games-section" id="gamesSection">\s*'
        r'<div class="games-grid" id="gamesGrid"></div>\s*'
        r'<div id="tableView" hidden></div>\s*)'
        r'(<footer class="site-footer-cta" role="contentinfo">.*?</footer>\s*)'
        r"</section>",
        text,
        re.DOTALL,
    )
    if not m:
        return text
    return (
        text[: m.start()]
        + m.group(1)
        + "</section>\n"
        + HTML_BLOCK
        + "        "
        + m.group(2)
        + text[m.end() :]
    )


def inject_js(text: str) -> str:
    if ARCHIVE_ONLY_GATE in text:
        text = text.replace(ARCHIVE_ONLY_GATE, "")
    text = re.sub(
        r"            function isArchiveSheetPage\(\) \{\s*return /\\/archive\\//i\.test\(window\.location\.pathname \|\| \"\"\);\s*\}\s*function listedOddsLabel",
        "            function listedOddsLabel",
        text,
        count=1,
    )
    if "function updateBattersWonRecap" not in text:
        marker = "            let hrResultsHydrateToken = 0;"
        if marker in text:
            text = text.replace(marker, JS_BLOCK + "\n" + marker, 1)
    else:
        # ensure section is shown (no early archive-only return)
        text = text.replace(
            "                section.hidden = false;\n                const wins = [];",
            "                section.hidden = false;\n                const wins = [];",
        )
    if "updateBattersWonRecap();" not in text:
        old = (
            "                        else setPill(host, \"na\", \"—\");\n"
            "                    } catch (err) {\n"
            "                        if (token !== hrResultsHydrateToken) return;\n"
            "                        setPill(host, \"na\", \"—\");\n"
            "                    }\n"
            "                }\n"
            "            }"
        )
        new = old[:-1] + "\n                updateBattersWonRecap();\n            }"
        if old in text:
            text = text.replace(old, new, 1)
    if "renderGames();\n            enhanceRows();\n            void hydratePickRowHrResultsFromMlb();" in text:
        if "updateBattersWonRecap();\n            renderGames();" not in text:
            text = text.replace(
                "            renderGames();\n            enhanceRows();\n            void hydratePickRowHrResultsFromMlb();",
                "            renderGames();\n            enhanceRows();\n            updateBattersWonRecap();\n            void hydratePickRowHrResultsFromMlb();",
                1,
            )
    return text


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    o = text
    text = inject_css(text)
    text = inject_html(text)
    text = inject_js(text)
    if text != o:
        path.write_text(text, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


def main() -> None:
    targets = [
        ROOT / "preview" / "index.html",
        ROOT / "index.html",
        ROOT / "preview" / "archive" / "2026-05-14.html",
        ROOT / "preview" / "archive" / "2026-05-15.html",
        ROOT / "preview" / "archive" / "2026-05-16.html",
    ]
    for t in targets:
        if t.is_file():
            patch(t)


if __name__ == "__main__":
    main()
