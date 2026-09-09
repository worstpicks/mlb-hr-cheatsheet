#!/usr/bin/env python3
"""Fix min score + grade filters (CSS + data-grade)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    ROOT / "preview" / "archive" / "2026-05-14.html",
    ROOT / "preview" / "archive" / "2026-05-15.html",
    ROOT / "preview" / "archive" / "2026-05-16.html",
]

CSS_OLD = """        .pick-row.emoji-filter-hidden,
        .pick-table-row.emoji-filter-hidden { display: none !important; }"""

CSS_NEW = """        .pick-row.emoji-filter-hidden,
        .pick-table-row.emoji-filter-hidden { display: none !important; }
        .pick-row.advanced-filter-hidden,
        .pick-table-row.advanced-filter-hidden { display: none !important; }"""

GRADE_FN = """
            function gradeForGiRi(gi, ri) {
                const game = games[gi];
                const row = game && game.rows[ri];
                if (!row) return "";
                const emojiRow = effectiveEmojiTagsForRow(row, game);
                const blastBonus = blastBonusMap[(row.blast || "").toLowerCase()] || 0;
                const card = document.getElementById("game-" + gi);
                const power = powerStars(row.score, emojiRow, row.note || "");
                const park = parkStars(card);
                const attack = attackStars(row.score, emojiRow, row.note || "");
                return letterGrade(row.score, power, park, attack, blastBonus);
            }
            function gradeForPickEl(el) {
                const dg = el.getAttribute("data-grade");
                if (dg) return dg.trim();
                const strong = el.querySelector(".letter-box strong");
                if (strong) return strong.textContent.trim();
                const gi = parseInt(el.getAttribute("data-gi") || "", 10);
                const ri = parseInt(el.getAttribute("data-ri") || "", 10);
                if (!Number.isNaN(gi) && !Number.isNaN(ri)) return gradeForGiRi(gi, ri);
                return "";
            }
"""

OLD_ROW_PASS = """                if (gf && gf.value) {
                    const g = el.querySelector(".letter-box strong");
                    if (!g || g.textContent.trim() !== gf.value) return false;
                }"""

NEW_ROW_PASS = """                if (gf && gf.value) {
                    if (gradeForPickEl(el) !== gf.value) return false;
                }"""

ENHANCE_GRADE_LINE = "                    const grade = letterGrade(score, power, park, attack, blastBonus);\n                    row.setAttribute(\"data-grade\", grade);"

APPLY_AFTER_TABLE = """                applyQuickFilterToTable();
                applyEmojiFiltersToAll();
            }"""

APPLY_AFTER_TABLE_NEW = """                applyQuickFilterToTable();
                applyEmojiFiltersToAll();
                if (typeof applyRowVisibilityFilters === "function") applyRowVisibilityFilters();
            }"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if CSS_NEW not in t and CSS_OLD in t:
        t = t.replace(CSS_OLD, CSS_NEW, 1)

    if "function gradeForPickEl" not in t and "function letterGrade(score" in t:
        t = t.replace(
            "            function letterGrade(score",
            GRADE_FN + "            function letterGrade(score",
            1,
        )

    if OLD_ROW_PASS in t:
        t = t.replace(OLD_ROW_PASS, NEW_ROW_PASS, 1)

    if 'row.setAttribute("data-grade", grade)' not in t and "function enhanceRows()" in t:
        t = t.replace(
            "                    const grade = letterGrade(score, power, park, attack, blastBonus);\n                    row.insertAdjacentHTML(\"beforeend\",",
            ENHANCE_GRADE_LINE + '\n                    row.insertAdjacentHTML("beforeend",',
            1,
        )

    if 'data-grade="${grade}"' not in t and "function buildPropsTable()" in t:
        t = t.replace(
            """                    const emojiCell = emojiRowDisplay.trim()
                        ? `<span class="table-emoji-tags">${escapeHtml(emojiRowDisplay)}</span>`
                        : '<span class="table-emoji-tags table-emoji-tags--empty">—</span>';
                    return `<tr class="pick-table-row""",
            """                    const emojiCell = emojiRowDisplay.trim()
                        ? `<span class="table-emoji-tags">${escapeHtml(emojiRowDisplay)}</span>`
                        : '<span class="table-emoji-tags table-emoji-tags--empty">—</span>';
                    const grade = gradeForGiRi(gi, ri);
                    return `<tr class="pick-table-row""",
            1,
        )
        if 'data-grade="${gradeForGiRi(gi, ri)}"' not in t:
            t = t.replace(
                'data-longshot="${dataLongshot}" data-gambly-batter=',
                'data-longshot="${dataLongshot}" data-grade="${grade}" data-gambly-batter=',
                1,
            )

    if (
        "if (typeof applyRowVisibilityFilters === \"function\") applyRowVisibilityFilters();"
        not in t
        and APPLY_AFTER_TABLE in t
    ):
        t = t.replace(APPLY_AFTER_TABLE, APPLY_AFTER_TABLE_NEW, 1)

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
