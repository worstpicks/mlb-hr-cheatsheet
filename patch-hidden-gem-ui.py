#!/usr/bin/env python3
"""Add Worst Pickz Hidden Gemz blue border/badge (local preview only)."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ROOT_INDEX = ROOT / "index.html"


def load_build_module(sheet_date: str):
    path = ROOT / f"build-sheet-{sheet_date}.py"
    if not path.exists():
        raise SystemExit(f"build sheet not found: {path.name}")
    spec = importlib.util.spec_from_file_location(f"build_{sheet_date}", path)
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    return build


def gems_for_date(sheet_date: str) -> list[str]:
    build = load_build_module(sheet_date)
    return sorted(build.GEMS)


def gem_set_block(gems: list[str]) -> str:
    return (
        "            const WORST_PICKZ_HIDDEN_GEM_NAMES = new Set([\n"
        + ",\n".join(f"                {json.dumps(name)}" for name in gems)
        + "\n            ]);"
    )


GEM_CSS = """
        .hidden-gem-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            position: absolute;
            top: -11px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 6;
            padding: 4px 10px;
            border-radius: 999px;
            background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
            color: #eff6ff;
            border: 1px solid rgba(186, 230, 253, 0.45);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.55px;
            text-transform: uppercase;
            white-space: nowrap;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.35);
        }
        .game-card .pick-row > .hidden-gem-badge {
            position: relative;
            top: auto;
            left: auto;
            transform: none;
            grid-column: 1 / -1;
            justify-self: center;
            margin: 0 auto 10px;
        }
        .hidden-gem-badge.hidden-gem-badge--pop {
            position: relative;
            top: auto;
            left: auto;
            transform: none;
        }
        .game-card .pick-row.pick-row--worst-pickz-gem,
        .game-card .pick-row.pick-row--worst-pickz-gem.elite,
        .game-card .pick-row.pick-row--worst-pickz-gem.strong,
        .game-card .pick-row.pick-row--worst-pickz-gem.playable,
        .game-card .pick-row.pick-row--worst-pickz-gem.thin {
            position: relative;
            padding-top: 14px;
            border: 2px solid rgba(56, 189, 248, 0.82) !important;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(12, 44, 82, 0.96) 0%, rgba(30, 64, 175, 0.9) 55%, rgba(30, 41, 59, 0.9) 100%) !important;
            box-shadow: 0 0 0 1px rgba(125, 211, 252, 0.28), 0 10px 22px rgba(37, 99, 235, 0.28) !important;
        }
        .game-card .pick-row.pick-row--worst-pickz-gem.is-saved,
        .game-card .pick-row.pick-row--worst-pickz-gem.elite.is-saved,
        .game-card .pick-row.pick-row--worst-pickz-gem.strong.is-saved,
        .game-card .pick-row.pick-row--worst-pickz-gem.playable.is-saved,
        .game-card .pick-row.pick-row--worst-pickz-gem.thin.is-saved {
            box-shadow:
                0 0 0 1px rgba(125, 211, 252, 0.28),
                0 10px 22px rgba(37, 99, 235, 0.28),
                inset 3px 0 0 rgba(45, 212, 191, 0.88);
        }
        .game-card .pick-row.pick-row--worst-pickz-gem.is-saved.bet-win,
        .game-card .pick-row.pick-row--worst-pickz-gem.elite.is-saved.bet-win,
        .game-card .pick-row.pick-row--worst-pickz-gem.strong.is-saved.bet-win,
        .game-card .pick-row.pick-row--worst-pickz-gem.playable.is-saved.bet-win,
        .game-card .pick-row.pick-row--worst-pickz-gem.thin.is-saved.bet-win {
            box-shadow:
                0 0 0 1px rgba(125, 211, 252, 0.28),
                0 10px 22px rgba(37, 99, 235, 0.28),
                inset 3px 0 0 rgba(34, 197, 94, 0.95);
        }
        .game-card .pick-row.pick-row--worst-pickz-gem.is-saved.bet-loss,
        .game-card .pick-row.pick-row--worst-pickz-gem.elite.is-saved.bet-loss,
        .game-card .pick-row.pick-row--worst-pickz-gem.strong.is-saved.bet-loss,
        .game-card .pick-row.pick-row--worst-pickz-gem.playable.is-saved.bet-loss,
        .game-card .pick-row.pick-row--worst-pickz-gem.thin.is-saved.bet-loss {
            box-shadow:
                0 0 0 1px rgba(125, 211, 252, 0.28),
                0 10px 22px rgba(37, 99, 235, 0.28),
                inset 3px 0 0 rgba(244, 63, 94, 0.92);
        }
        .game-card .pick-row.pick-row--worst-pickz-gem.is-saved.bet-void,
        .game-card .pick-row.pick-row--worst-pickz-gem.elite.is-saved.bet-void,
        .game-card .pick-row.pick-row--worst-pickz-gem.strong.is-saved.bet-void,
        .game-card .pick-row.pick-row--worst-pickz-gem.playable.is-saved.bet-void,
        .game-card .pick-row.pick-row--worst-pickz-gem.thin.is-saved.bet-void {
            box-shadow:
                0 0 0 1px rgba(125, 211, 252, 0.28),
                0 10px 22px rgba(37, 99, 235, 0.28),
                inset 3px 0 0 rgba(148, 163, 184, 0.88);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem {
            box-shadow: inset 0 0 0 2px rgba(56, 189, 248, 0.82);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem td {
            background: rgba(30, 64, 175, 0.12);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved,
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-win,
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-loss,
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-void {
            box-shadow:
                inset 0 0 0 2px rgba(56, 189, 248, 0.78),
                inset 5px 0 0 rgba(45, 212, 191, 0.75);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-win {
            box-shadow:
                inset 0 0 0 2px rgba(56, 189, 248, 0.78),
                inset 5px 0 0 rgba(34, 197, 94, 0.95);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-loss {
            box-shadow:
                inset 0 0 0 2px rgba(56, 189, 248, 0.78),
                inset 5px 0 0 rgba(244, 63, 94, 0.92);
        }
        .props-table tbody tr.pick-row--worst-pickz-gem.is-saved.bet-void {
            box-shadow:
                inset 0 0 0 2px rgba(56, 189, 248, 0.78),
                inset 5px 0 0 rgba(148, 163, 184, 0.88);
        }
        html.theme-light .game-card .pick-row.pick-row--worst-pickz-gem,
        html.theme-light .game-card .pick-row.pick-row--worst-pickz-gem.elite,
        html.theme-light .game-card .pick-row.pick-row--worst-pickz-gem.strong,
        html.theme-light .game-card .pick-row.pick-row--worst-pickz-gem.playable,
        html.theme-light .game-card .pick-row.pick-row--worst-pickz-gem.thin {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 48%, #f8fafc 100%) !important;
            border-color: rgba(37, 99, 235, 0.82) !important;
            box-shadow: 0 0 0 1px rgba(125, 211, 252, 0.45), 0 12px 28px rgba(37, 99, 235, 0.12) !important;
        }
        html.theme-light .props-table tbody tr.pick-row--worst-pickz-gem td {
            background: rgba(219, 234, 254, 0.55);
        }
"""

GEM_JS_HELPERS = """
            function isWorstPickzHiddenGemRow(row) {
                return WORST_PICKZ_HIDDEN_GEM_NAMES.has(row.name);
            }
            function worstPickzDesignationBadgeHtml(row) {
                const fav = isWorstPickzFavoriteRow(row);
                const gem = isWorstPickzHiddenGemRow(row);
                let html = "";
                if (fav) {
                    html += '<span class="favorite-badge" aria-label="Worst Pickz Favorite">★ Worst Pickz Favorite</span>';
                }
                if (gem) {
                    html += '<span class="hidden-gem-badge" aria-label="Worst Pickz Hidden Gemz">💎 Worst Pickz Hidden Gemz</span>';
                }
                return html;
            }
            function worstPickzDesignationClass(row) {
                let cls = "";
                if (isWorstPickzFavoriteRow(row)) cls += " pick-row--worst-pickz-fav";
                if (isWorstPickzHiddenGemRow(row)) cls += " pick-row--worst-pickz-gem";
                return cls;
            }
"""


def patch(text: str, sheet_date: str | None = None) -> str:
    if sheet_date is None:
        m = re.search(r'<meta name="sheet-date" content="([^"]+)">', text)
        sheet_date = m.group(1) if m else "2026-06-10"

    build = load_build_module(sheet_date)
    gems = sorted(build.GEMS)
    fav_count = len(build.FAVS)
    gem_count = len(gems)
    gem_set = gem_set_block(gems)

    if "pick-row--worst-pickz-gem" not in text:
        anchor = "        .favorite-badge.favorite-badge--pop {"
        if anchor not in text:
            raise SystemExit("Could not locate favorite-badge CSS anchor")
        end = text.index("        }", text.index(anchor)) + len("        }")
        text = text[:end] + GEM_CSS + text[end:]

    if "WORST_PICKZ_HIDDEN_GEM_NAMES" not in text:
        text = text.replace(
            "            function isWorstPickzFavoriteRow(row) {\n"
            "                return WORST_PICKZ_FAVORITE_NAMES.has(row.name);\n"
            "            }",
            gem_set
            + "\n"
            + GEM_JS_HELPERS.strip()
            + "\n            function isWorstPickzFavoriteRow(row) {\n"
            "                return WORST_PICKZ_FAVORITE_NAMES.has(row.name);\n"
            "            }",
            1,
        )
    else:
        text = re.sub(
            r"const WORST_PICKZ_HIDDEN_GEM_NAMES = new Set\(\[[\s\S]*?\]\);",
            gem_set.strip(),
            text,
            count=1,
        )

    text = text.replace(
        "                const fav = isWorstPickzFavoriteRow(row);\n"
        "                const favClass = fav ? \" pick-row--worst-pickz-fav\" : \"\";",
        "                const designationClass = worstPickzDesignationClass(row);\n"
        "                const designationBadge = worstPickzDesignationBadgeHtml(row);",
        1,
    )
    text = text.replace(
        '${betOutcomeClass}${favClass}"',
        '${betOutcomeClass}${designationClass}"',
        1,
    )
    text = text.replace(
        '${fav ? \'<span class="favorite-badge" aria-label="Worst Pickz Favorite">★ Worst Pickz Favorite</span>\' : ""}',
        "${designationBadge}",
        1,
    )

    text = text.replace(
        "                    const fav = isWorstPickzFavoriteRow(row);\n"
        "                    const favClass = fav ? \" pick-row--worst-pickz-fav\" : \"\";",
        "                    const designationClass = worstPickzDesignationClass(row);\n"
        "                    const designationBadge = worstPickzDesignationBadgeHtml(row);",
        1,
    )
    text = text.replace(
        '${betOutcomeClass}${favClass}" data-emoji-tags="${emojiTagsEnc}"',
        '${betOutcomeClass}${designationClass}" data-emoji-tags="${emojiTagsEnc}"',
        1,
    )

    text = text.replace(
        "                const favHtml = isWorstPickzFavoriteRow(row)\n"
        "                    ? `<div class=\"player-pop__fav\"><span class=\"favorite-badge favorite-badge--pop\" aria-label=\"Worst Pickz Favorite\">★ Worst Pickz Favorite</span></div>`\n"
        "                    : \"\";",
        "                let favHtml = \"\";\n"
        "                if (isWorstPickzFavoriteRow(row)) {\n"
        "                    favHtml += `<div class=\"player-pop__fav\"><span class=\"favorite-badge favorite-badge--pop\" aria-label=\"Worst Pickz Favorite\">★ Worst Pickz Favorite</span></div>`;\n"
        "                }\n"
        "                if (isWorstPickzHiddenGemRow(row)) {\n"
        "                    favHtml += `<div class=\"player-pop__fav\"><span class=\"hidden-gem-badge hidden-gem-badge--pop\" aria-label=\"Worst Pickz Hidden Gemz\">💎 Worst Pickz Hidden Gemz</span></div>`;\n"
        "                }",
        1,
    )

    text = text.replace(
        "                        fav: isWorstPickzFavoriteRow(row),",
        "                        fav: isWorstPickzFavoriteRow(row),\n                        gem: isWorstPickzHiddenGemRow(row),",
        1,
    )

    if 'data-filter="hidden-gems"' not in text:
        text = text.replace(
            '                    <button type="button" class="filter-chip" data-filter="favorites">⭐ Favorites</button>',
            '                    <button type="button" class="filter-chip" data-filter="favorites">⭐ Favorites</button>\n'
            '                    <button type="button" class="filter-chip" data-filter="hidden-gems">💎 Hidden Gemz</button>',
            1,
        )

    text = text.replace(
        "                if (activeQuickFilter === \"favorites\" && !el.classList.contains(\"pick-row--worst-pickz-fav\")) return false;",
        "                if (activeQuickFilter === \"favorites\" && !el.classList.contains(\"pick-row--worst-pickz-fav\")) return false;\n"
        "                if (activeQuickFilter === \"hidden-gems\" && !el.classList.contains(\"pick-row--worst-pickz-gem\")) return false;",
        1,
    )

    text = re.sub(
        r"<strong>\d+ Worst Pickz Favorite</strong> rows \(.*?Designated <strong>Worst Pickz Favorites</strong> get the rose border(?:; designated <strong>Hidden Gemz</strong> get the blue border)?",
        f"<strong>{fav_count} Worst Pickz Favorite</strong> rows (&#11088;) and <strong>{gem_count} Worst Pickz Hidden Gemz</strong> (&#128142;). Designated <strong>Worst Pickz Favorites</strong> get the rose border; designated <strong>Hidden Gemz</strong> get the blue border",
        text,
        count=1,
    )

    if '<div class="emoji-key-item"><strong>💎</strong>' not in text:
        text = text.replace(
            '<div class="emoji-key-item"><strong>⭐</strong> Worst Pickz Favorite (sheet-designated; rose border)</div>',
            '<div class="emoji-key-item"><strong>⭐</strong> Worst Pickz Favorite (sheet-designated; rose border)</div>\n'
            '                        <div class="emoji-key-item"><strong>💎</strong> Worst Pickz Hidden Gemz (sheet-designated; blue border)</div>',
            1,
        )

    if 'title="Designated Worst Pickz Hidden Gemz' not in text:
        text = text.replace(
            '<span class="quick-legend-item" title="Designated Worst Pickz Favorite on this sheet">⭐ Favorite</span>',
            '<span class="quick-legend-item" title="Designated Worst Pickz Favorite on this sheet">⭐ Favorite</span>\n'
            '                <span class="quick-legend-item" title="Designated Worst Pickz Hidden Gemz on this sheet">💎 Hidden Gemz</span>',
            1,
        )

    return text


def main() -> None:
    text = PREVIEW.read_text(encoding="utf-8")
    m = re.search(r'<meta name="sheet-date" content="([^"]+)">', text)
    sheet_date = m.group(1) if m else "2026-06-10"
    gems = gems_for_date(sheet_date)
    patched = patch(text, sheet_date=sheet_date)
    PREVIEW.write_text(patched, encoding="utf-8")
    shutil.copy2(PREVIEW, ROOT_INDEX)
    print(f"Patched {PREVIEW.relative_to(ROOT)} ({len(gems)} hidden gems for {sheet_date})")
    print("Synced index.html (not pushed live)")


if __name__ == "__main__":
    main()
