#!/usr/bin/env python3
"""Move Batters Won below games slate, above Follow Worst Pickz footer."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

BATTERS_BLOCK = """        <section class="batters-won-section" id="battersWonSection" aria-labelledby="battersWonHeading">
            <div class="panel batters-won-panel">
                <h2 id="battersWonHeading">Batters Won</h2>
                <p class="batters-won-lede" id="battersWonLede" aria-live="polite">Checking homers from MLB box scores…</p>
                <ol class="batters-won-list" id="battersWonList"></ol>
            </div>
        </section>
"""

BATTERS_PAT = re.compile(
    r"\n\s*<section class=\"batters-won-section(?: batters-won-section--top)?\""
    r'[^>]*id="battersWonSection"[^>]*>.*?</section>\n',
    re.DOTALL,
)

GAMES_FOOTER_PAT = re.compile(
    r'(<section class="games-section" id="gamesSection">\s*'
    r'<div class="games-grid" id="gamesGrid"></div>\s*'
    r'<motion.div id="tableView" hidden></motion.div>\s*)'
    r'(<footer class="site-footer-cta" role="contentinfo">.*?</footer>\s*)'
    r"</section>",
    re.DOTALL,
)

GAMES_FOOTER_PAT = re.compile(
    r'(<section class="games-section" id="gamesSection">\s*'
    r'<div class="games-grid" id="gamesGrid"></div>\s*'
    r'<div id="tableView" hidden></div>\s*)'
    r'(<footer class="site-footer-cta" role="contentinfo">.*?</footer>\s*)'
    r"</section>",
    re.DOTALL,
)

CSS_OLD = """        .batters-won-section {
            margin: 0 0 14px;
            max-width: min(520px, 100%);
        }
        .batters-won-section--top {
            order: -1;
        }"""

CSS_NEW = """        .batters-won-section {
            margin: 14px 0 0;
            max-width: min(520px, 100%);
        }"""


def already_bottom(t: str) -> bool:
    bw = t.find('id="battersWonSection"')
    footer = t.find('class="site-footer-cta"')
    games = t.find('id="gamesSection"')
    if bw < 0 or footer < 0 or games < 0:
        return False
    games_close = t.find("</section>", t.find('id="tableView"'))
    return games_close < bw < footer


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if already_bottom(t):
        if CSS_OLD in t:
            t = t.replace(CSS_OLD, CSS_NEW, 1)
        t = t.replace("batters-won-section batters-won-section--top", "batters-won-section")
        if t != o:
            path.write_text(t, encoding="utf-8")
            print("css", path.relative_to(ROOT))
        else:
            print("ok", path.relative_to(ROOT))
        return

    # Remove block at top (or any stray copy before re-insert)
    while True:
        m = BATTERS_PAT.search(t)
        if not m:
            break
        t = t[: m.start()] + "\n" + t[m.end() :]

    m = GAMES_FOOTER_PAT.search(t)
    if not m:
        print("skip", path.relative_to(ROOT))
        return

    t = (
        t[: m.start()]
        + m.group(1)
        + "</section>\n"
        + BATTERS_BLOCK
        + "        "
        + m.group(2)
        + t[m.end() :]
    )

    if CSS_OLD in t:
        t = t.replace(CSS_OLD, CSS_NEW, 1)
    elif ".batters-won-section--top" in t:
        t = t.replace(
            "        .batters-won-section--top {\n            order: -1;\n        }\n",
            "",
            1,
        )

    t = t.replace("batters-won-section batters-won-section--top", "batters-won-section")
    t = t.replace('id="battersWonSection" hidden', 'id="battersWonSection"')

    path.write_text(t, encoding="utf-8")
    print("moved", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
