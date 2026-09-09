#!/usr/bin/env python3
"""Replace Top-only FAB with Top + Bottom scroll jump buttons."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

OLD_CSS = """        .to-top-fab {
            position: fixed;
            right: var(--fab-edge);
            bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap));
            z-index: 60;
            border: 1px solid rgba(254,215,170,0.5);
            background: rgba(127,29,29,0.92);
            color: #fff7ed;
            padding: 8px 14px;
            border-radius: 999px;
            font-weight: 800;
            cursor: pointer;
            font-size: 0.78rem;
            box-shadow: 0 6px 22px rgba(0,0,0,0.4);
        }
        .to-top-fab:hover { background: rgba(153,27,27,0.96); }"""

NEW_CSS = """        .scroll-jump-fab {
            position: fixed;
            right: var(--fab-edge);
            bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap));
            z-index: 60;
            display: flex;
            flex-direction: column; /* Top above Bottom */
            align-items: stretch;
            gap: 4px;
        }
        .scroll-jump-fab__btn {
            border: 1px solid rgba(254,215,170,0.5);
            background: rgba(127,29,29,0.92);
            color: #fff7ed;
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: 800;
            cursor: pointer;
            font-size: 0.72rem;
            line-height: 1.2;
            box-shadow: 0 6px 22px rgba(0,0,0,0.4);
            font-family: inherit;
        }
        .scroll-jump-fab__btn:hover { background: rgba(153,27,27,0.96); }
        .scroll-jump-fab__btn:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }"""

OLD_HTML = """    <button type="button" class="to-top-fab" id="toTop" aria-label="Back to top of page">↑ Top</button>"""

NEW_HTML = """    <div class="scroll-jump-fab" role="group" aria-label="Scroll page">
        <button type="button" class="scroll-jump-fab__btn" id="scrollToTop" aria-label="Back to top of page">↑ Top</button>
        <button type="button" class="scroll-jump-fab__btn" id="scrollToBottom" aria-label="Go to bottom of page">↓ Bottom</button>
    </div>"""

OLD_JS = """            const toTop = document.getElementById("toTop");
            if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }));"""

NEW_JS = """            function pageScrollBehavior() {
                return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
            }
            const scrollToTopBtn = document.getElementById("scrollToTop");
            const scrollToBottomBtn = document.getElementById("scrollToBottom");
            if (scrollToTopBtn) {
                scrollToTopBtn.addEventListener("click", () => {
                    window.scrollTo({ top: 0, behavior: pageScrollBehavior() });
                });
            }
            if (scrollToBottomBtn) {
                scrollToBottomBtn.addEventListener("click", () => {
                    const maxY = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
                    window.scrollTo({ top: maxY, behavior: pageScrollBehavior() });
                });
            }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_CSS in t:
        t = t.replace(OLD_CSS, NEW_CSS, 1)
    if OLD_HTML in t:
        t = t.replace(OLD_HTML, NEW_HTML, 1)
    if OLD_JS in t:
        t = t.replace(OLD_JS, NEW_JS, 1)
    t = t.replace("--fab-top-h:", "--fab-scroll-h:")
    t = t.replace("var(--fab-top-h)", "var(--fab-scroll-h)")
    t = t.replace("--fab-scroll-h: 32px;", "--fab-scroll-h: 60px;")
    t = t.replace(
        ":root { --fab-edge: 10px; --fab-gap: 6px; --fab-slip-h: 40px; --fab-scroll-h: 34px; }",
        ":root { --fab-edge: 10px; --fab-gap: 6px; --fab-slip-h: 40px; --fab-scroll-h: 62px; }",
    )
    t = t.replace(
        ".scroll-jump-fab { right: var(--fab-edge); bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap)); padding: 9px 14px; font-size: 0.78rem; }",
        ".scroll-jump-fab { right: var(--fab-edge); bottom: calc(var(--fab-edge) + var(--fab-slip-h) + var(--fab-gap)); }\n            .scroll-jump-fab__btn { padding: 7px 12px; font-size: 0.74rem; }",
    )
    t = t.replace(
        ".sheet-toolbar, .to-top-fab, .header-actions",
        ".sheet-toolbar, .scroll-jump-fab, .header-actions",
    )
    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("skip", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
