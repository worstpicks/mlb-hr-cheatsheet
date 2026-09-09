#!/usr/bin/env python3
"""Move existing Batters Won block to top of container."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = """
        <section class="batters-won-section batters-won-section--top" id="battersWonSection" aria-labelledby="battersWonHeading">
            <div class="panel batters-won-panel">
                <h2 id="battersWonHeading">Batters Won</h2>
                <p class="batters-won-lede" id="battersWonLede" aria-live="polite">Checking homers from MLB box scores…</p>
                <ol class="batters-won-list" id="battersWonList"></ol>
            </div>
        </section>
"""
PAT = re.compile(
    r'\n\s*<section class="batters-won-section"[^>]*id="battersWonSection"[^>]*>.*?</section>\n',
    re.DOTALL,
)
NEEDLE = '    <div class="container">\n        <header>'
TOP = '    <div class="container">\n' + HTML + "\n        <header>"


def fix(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if "batters-won-section--top" in t and t.find("batters-won-section--top") < t.find("<header>"):
        print("ok", path.name)
        return
    t = PAT.sub("\n", t, count=1)
    if NEEDLE not in t:
        print("skip", path.name)
        return
    t = t.replace(NEEDLE, TOP, 1)
    t = t.replace('id="battersWonSection" hidden', 'id="battersWonSection"', 1)
    path.write_text(t, encoding="utf-8")
    print("moved", path.name)


if __name__ == "__main__":
    from patch_targets import ARCHIVE_HTML

    for p in ARCHIVE_HTML:
        fix(p)
