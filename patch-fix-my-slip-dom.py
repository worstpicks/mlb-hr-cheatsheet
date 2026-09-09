#!/usr/bin/env python3
"""Move My Slip DOM before script; wire FAB click; raise legend above Top."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

TARGETS = SHEET_HTML

SLIP_RE = re.compile(
    r'\n    <div class="my-slip-backdrop" id="mySlipBackdrop" hidden></motion.div>'
    r'.*?'
    r'id="mySlipFab"[^>]*>.*?</button>\n',
    re.DOTALL,
)

SLIP_RE = re.compile(
    r'\n    <div class="my-slip-backdrop" id="mySlipBackdrop" hidden></div>'
    r'.*?'
    r'id="mySlipFab"[^>]*>.*?</button>\n',
    re.DOTALL,
)

WIRE_FN = """            function wireMySlipControls() {
                const fab = document.getElementById("mySlipFab");
                if (!fab || fab.dataset.mySlipWired === "1") return;
                fab.dataset.mySlipWired = "1";
                fab.addEventListener("click", (e) => { e.preventDefault(); openMySlip(); });
                document.getElementById("mySlipClose")?.addEventListener("click", closeMySlip);
                document.getElementById("mySlipBackdrop")?.addEventListener("click", closeMySlip);
            }
"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    m = SLIP_RE.search(t)
    if m:
        slip = m.group(0)
        t = SLIP_RE.sub("\n", t, count=1)
    else:
        slip = ""

    before_script = t.split("<script>", 1)[0]
    if 'id="mySlipFab"' not in before_script and slip:
        anchor = '    <button type="button" class="to-top-fab" id="toTop"'
        if anchor in t:
            t = t.replace(anchor, slip.rstrip() + "\n\n" + anchor, 1)

    t = t.replace(
        "bottom: 72px;\n            z-index: 55",
        "bottom: 132px;\n            z-index: 55",
    )
    t = t.replace(
        ".quick-legend { right: 8px; bottom: 68px;",
        ".quick-legend { right: 8px; bottom: 128px;",
    )
    t = t.replace(".to-top-fab { bottom: 64px; }", ".to-top-fab { bottom: 58px; }")

    if "function wireMySlipControls" not in t:
        t = t.replace(
            "            function wireUxEnhancements() {",
            WIRE_FN + "            function wireUxEnhancements() {",
            1,
        )

    t = t.replace(
        'document.getElementById("mySlipFab")?.addEventListener("click", openMySlip);',
        "wireMySlipControls();",
    )

    if "wireUxEnhancements();\n            wireMySlipControls();" not in t:
        t = t.replace(
            "            wireUxEnhancements();",
            "            wireUxEnhancements();\n            wireMySlipControls();",
            1,
        )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
