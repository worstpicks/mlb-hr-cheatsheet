#!/usr/bin/env python3
"""Pre-deploy verification for sheet HTML."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHEETS = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    *(ROOT / "preview" / "archive").glob("2026-*.html"),
]
REQUIRED_IDS = [
    "mySlipLegs",
    "mySlipCombined",
    "mySlipFab",
    "parlayLegsToolbar",
    "parlayCombinedToolbar",
    "mySlipCombined",
    "scrollToTop",
    "scrollToBottom",
    "quickLegend",
    "quickLegendToggle",
    "battersWonSection",
    "exportGambly",
    "exportGamblySlip",
]
REQUIRED_FUNCS = [
    "getSheetSiteRoot",
    "rebuildParlayPanel",
    "initSheetArchiveNav",
    "wireUxEnhancements",
]


def verify_file(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"missing file: {path}"]
    t = path.read_text(encoding="utf-8")
    is_archive = "archive" in path.parts
    if "motion.div" in t or "</motion" in t:
        issues.append("motion.div typo in HTML")
    ids = re.findall(r'\bid="([^"]+)"', t)
    for dup in [k for k, v in Counter(ids).items() if v > 1]:
        if "${" in dup:
            continue
        issues.append(f"duplicate id: {dup}")
    if not is_archive:
        for rid in REQUIRED_IDS:
            if f'id="{rid}"' not in t:
                issues.append(f"missing id: {rid}")
        if 'id="parlayLegs"' in t and 'id="mySlipLegs"' in t:
            issues.append("duplicate parlayLegs id (toolbar + slip conflict)")
        for fn in REQUIRED_FUNCS:
            if fn not in t:
                issues.append(f"missing function: {fn}")
        if "fab-stack" not in t:
            issues.append("missing fab-stack")
        if "pikkit-link__wordmark" not in t and "pikkit-link" not in t:
            issues.append("missing pikkit wordmark link")
    if path.name == "index.html" and path.parent.name == "preview":
        if "../assets/" in t:
            issues.append("preview index should not use ../assets/")
    if is_archive:
        if 'src="assets/pikkit' in t and 'src="../assets/pikkit' not in t:
            issues.append("archive should use ../assets/ for pikkit")
    return issues


def main() -> int:
    manifest_path = ROOT / "preview" / "sheets-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print("manifest dates:", [s["date"] for s in manifest["sheets"]])
    failed = False
    import subprocess

    r = subprocess.run(
        [sys.executable, str(ROOT / "validate-index-matchups.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        failed = True
        print("FAIL pitcher matchup validation")
        print(r.stdout or r.stderr)
    else:
        print("OK   pitcher matchups (validate-index-matchups.py)")
    for p in SHEETS:
        rel = p.relative_to(ROOT)
        issues = verify_file(p)
        if issues:
            failed = True
            print(f"FAIL {rel}")
            for i in issues:
                print(f"  - {i}")
        else:
            print(f"OK   {rel}")
    if (ROOT / "preview" / "index.html").read_text(encoding="utf-8").find("pikkit-link__wordmark") >= 0:
        print("OK   Pikkit wordmark in sheet")
    else:
        print("FAIL missing Pikkit wordmark on current sheet")
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
