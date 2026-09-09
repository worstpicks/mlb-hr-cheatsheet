#!/usr/bin/env python3
"""Fix slate-patch HTML damage and re-apply UX patches without touching games data."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FAV_BLOCK = (
    "/** Sheet-curated Worst Pickz Favorites — edit this list when the board changes; not read from or written to localStorage. */\n"
    """            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "Kyle Schwarber (L)",
                "JJ Bleday (L)",
                "Will Benson (L)",
                "James Wood (L)",
                "Juan Soto (L)",
                "Byron Buxton (R)",
                "Yordan Alvarez (L)",
                "Bobby Witt Jr. (R)",
                "Ian Happ (S)",
                "Seiya Suzuki (R)",
                "Michael Busch (L)",
                "Michael Conforto (L)",
                "Hunter Goodman (R)",
                "Miguel Vargas (R)",
                "Gavin Sheets (L)",
                "Jackson Merrill (L)",
                "Julio Rodriguez (R)",
                "Will Smith (R)",
                "Shohei Ohtani (L)"
            ]);
            function isWorstPickzFavoriteRow(row) {
                return WORST_PICKZ_FAVORITE_NAMES.has(row.name);
            }"""
)


def repair_html(text: str) -> str:
    text = text.replace(
        "                    </div>\n</div>\n                <div class=\"summary-card\">",
        "                    </div>\n                </div>\n                <div class=\"summary-card\">",
        1,
    )
    text = re.sub(
        r"/\*\* Sheet-curated Worst Pickz Favorites[\s\S]*?function isWorstPickzFavoriteRow\(row\) \{\s*return WORST_PICKZ_FAVORITE_NAMES\.has\(row\.name\);\s*\}",
        FAV_BLOCK,
        text,
        count=1,
    )
    if text.count("wireUxEnhancements();") > 1:
        text = re.sub(
            r"\n            wireUxEnhancements\(\);\n            updatePickCount\(\);\n",
            "\n            updatePickCount();\n",
            text,
            count=1,
        )
    return text


def main() -> None:
    for rel in ["preview/index.html", "index.html"]:
        path = ROOT / rel
        if not path.is_file():
            continue
        t = path.read_text(encoding="utf-8")
        fixed = repair_html(t)
        if fixed != t:
            path.write_text(fixed, encoding="utf-8")
            print("repaired", rel)

    patches = [
        "patch-fix-fab-stack.py",
        "patch-fab-compact.py",
        "patch-fix-score-grade-filters.py",
        "patch-fix-gambly-init.py",
        "patch-remove-duplicate-filters.py",
        "patch-fix-my-slip.py",
        "patch-fix-my-slip-dom.py",
        "patch-pikkit-top-only.py",
        "patch-fix-slip-count.py",
        "fix-archive-picker.py",
        "patch-current-slate-btn.py",
    ]
    py = sys.executable
    for name in patches:
        p = ROOT / name
        if p.is_file():
            print("---", name)
            subprocess.run([py, str(p)], cwd=ROOT, check=True)
    print("done")


if __name__ == "__main__":
    main()
