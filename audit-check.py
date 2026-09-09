#!/usr/bin/env python3
"""Quick audit of sheet HTML files."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    ROOT / "preview" / "archive" / "2026-05-14.html",
    ROOT / "preview" / "archive" / "2026-05-15.html",
    ROOT / "preview" / "archive" / "2026-05-16.html",
]


def audit(path: Path) -> list[str]:
    t = path.read_text(encoding="utf-8")
    issues: list[str] = []
    ids = re.findall(r'\bid="([^"]+)"', t)
    dups = [k for k, v in Counter(ids).items() if v > 1]
    if dups:
        issues.append("duplicate ids: " + ", ".join(dups))
    if "motion." in t or "</motion" in t:
        issues.append("motion.div typo in HTML")
    n_parlay = len(re.findall(r'\bid="parlayLegs"', t))
    if n_parlay > 1:
        issues.append(f"parlayLegs appears {n_parlay}x")
    if n_parlay == 0 and "rebuildParlayPanel" in t:
        issues.append("missing parlayLegs but parlay JS present")
    if "<article class=\"game-card\"" in t:
        issues.append("uses article.game-card instead of details")
    if "getSheetSiteRoot" not in t:
        issues.append("missing getSheetSiteRoot (archive nav fix)")
    if "opt.value = resolveManifestHref" in t:
        issues.append("archive select still uses resolveManifestHref for opt.value")
    if "wireUxEnhancements" in t and "my-slip-fab" not in t:
        issues.append("wireUxEnhancements without My Slip FAB")
    if "my-slip-fab" in t and n_parlay > 1:
        issues.append("My Slip + toolbar both have parlayLegs")
    meta = re.search(r'<meta name="sheet-date" content="([^"]+)"', t)
    if meta:
        issues.append(f"sheet-date={meta.group(1)}")
    return issues


def main() -> None:
    manifest = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
    print("manifest:", [s["date"] for s in manifest["sheets"]])
    print()
    for p in FILES:
        if not p.exists():
            print(p.name, "MISSING")
            continue
        iss = audit(p)
        print(p.relative_to(ROOT))
        for i in iss:
            print(" ", i)
        print()


if __name__ == "__main__":
    main()
