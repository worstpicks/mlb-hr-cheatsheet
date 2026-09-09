#!/usr/bin/env python3
"""Add Overdue filter chip, legend, and JS hook to index HTML files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [ROOT / "preview" / "index.html", ROOT / "index.html"]
BUM_LEGEND = "Bum onna Mound / HR-leaky SP in game title"

CHIP = (
    '                    <button type="button" class="filter-chip filter-chip--emoji" data-emoji="\U0001f4a4" '
    'aria-pressed="false" title="Overdue">\U0001f4a4</button>\n'
)

QUICK_LEGEND = '                <span class="quick-legend-item" title="Leaky starter called out in game line">\U0001f9e4 HR-leaky SP</span>'
QUICK_LEGEND_NEW = (
    QUICK_LEGEND
    + '\n                <span class="quick-legend-item" title="Overdue">'
    + "\U0001f4a4 Overdue</span>"
)

EMOJI_FN_OLD = """                if (vsKey && bumKeys.includes(vsKey) && !emojiBase.includes(BUM_ON_MOUND)) {
                    emojiBase = `${emojiBase} ${BUM_ON_MOUND}`.trim();
                }
                return emojiBase;"""

EMOJI_FN_NEW = """                if (vsKey && bumKeys.includes(vsKey) && !emojiBase.includes(BUM_ON_MOUND)) {
                    emojiBase = `${emojiBase} ${BUM_ON_MOUND}`.trim();
                }
                const OVERDUE_SLEEP = "\\u{1F4A4}";
                if (row.overdue && !emojiBase.includes(OVERDUE_SLEEP)) {
                    emojiBase = `${emojiBase} ${OVERDUE_SLEEP}`.trim();
                }
                return emojiBase;"""


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    orig = text

    if 'data-emoji="\U0001f4a4"' not in text and "data-emoji=\"\U0001f4a4\"" not in text:
        needle = '                    <button type="button" class="filter-chip filter-chip--emoji" data-emoji="\U0001f9e4"'
        if needle in text:
            text = text.replace(needle, CHIP + needle, 1)

    if "Overdue</span>" not in text or "\U0001f4a4 Overdue" not in text:
        if QUICK_LEGEND in text:
            text = text.replace(QUICK_LEGEND, QUICK_LEGEND_NEW, 1)

    if "\U0001f4a4</strong> Overdue" not in text:
        text = re.sub(
            rf'(\s*<div class="emoji-key-item"><strong>\U0001f9e4</strong> {re.escape(BUM_LEGEND)}</div>)',
            r'\1\n                        <div class="emoji-key-item"><strong>\U0001f4a4</strong> Overdue</div>',
            text,
            count=1,
        )

    if "row.overdue" not in text:
        text = text.replace(EMOJI_FN_OLD, EMOJI_FN_NEW, 1)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"Patched {path.name}")
    else:
        print(f"No changes needed for {path.name}")


def main() -> None:
    for p in TARGETS:
        if p.is_file():
            patch_file(p)


if __name__ == "__main__":
    main()
