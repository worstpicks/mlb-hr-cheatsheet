#!/usr/bin/env python3
"""Rules for Goblin 3-leg HR vs Worst Pickz Favorite 3-leg — no duplicate batters."""
import html
import json
import re
from pathlib import Path

THREE_LEG_LABEL = "Add 3 Leg HR to Gambly"
TWO_LEG_LABEL = "Add 2 Leg HR to Gambly"
FAV_THREE_LABEL = "Add Favorite 3 Leg to Gambly"
STRAIGHT_O05_LABEL = "Add O0.5 Straight to Gambly"
STRAIGHT_O15_LABEL = "Add O1.5 Straight to Gambly"

FAV_THREE_REQUIRED_EMOJIS = ("⭐",)  # Favorite 3 Leg: ⭐ only (no moonshot required on label)


def extract_goblin_gambly_lines(html_text: str, button_label: str) -> list[str]:
    pat = (
        r"data-goblin-gambly-lines='([^']+)'[^>]*>"
        + re.escape(button_label)
    )
    m = re.search(pat, html_text)
    if not m:
        raise ValueError(f"missing Goblin button: {button_label}")
    raw = html.unescape(m.group(1))
    return json.loads(raw)


def gambly_batter(line: str) -> str:
    return line.split(" - ", 1)[0].strip()


def validate_three_leg_parlays(html_text: str, fav_names: set[str] | None = None) -> list[str]:
    """Return list of error strings; empty means OK."""
    errors: list[str] = []
    try:
        three = extract_goblin_gambly_lines(html_text, THREE_LEG_LABEL)
        fav = extract_goblin_gambly_lines(html_text, FAV_THREE_LABEL)
    except (ValueError, json.JSONDecodeError) as e:
        return [str(e)]

    if len(three) != 3:
        errors.append(f"3 Leg HR must have 3 legs, found {len(three)}")
    if len(fav) != 3:
        errors.append(f"Favorite 3 Leg must have 3 legs, found {len(fav)}")

    three_b = [gambly_batter(x) for x in three]
    fav_b = [gambly_batter(x) for x in fav]
    overlap = set(three_b) & set(fav_b)
    if overlap:
        errors.append(f"3 Leg HR and Favorite 3 Leg share batters: {sorted(overlap)}")

    if fav_names:
        fav_on_card = [name for name in fav_b if name in fav_names]
        # Thin boards with fewer than 3 designated favorites may fill remaining
        # Favorite 3 Leg seats with loud non-⭐ attack names, but every sheet
        # favorite must still appear on the card.
        if len(fav_names) >= 3:
            for name in fav_b:
                if name not in fav_names:
                    errors.append(f"Favorite 3 Leg batter not on ⭐ list: {name}")
        else:
            missing_favs = sorted(set(fav_names) - set(fav_b))
            if missing_favs:
                errors.append(
                    f"Favorite 3 Leg missing sheet ⭐ on thin board: {missing_favs}"
                )

    row_pat = re.compile(
        r'name: "([^"]+)"[^}]*emojis: "([^"]*)"[^}]*note: "([^"]*)"'
    )
    rows = {m.group(1): (m.group(2), m.group(3)) for m in row_pat.finditer(html_text)}
    for name in fav_b:
        sheet_name = next((k for k in rows if k.startswith(name + " (")), None)
        if not sheet_name:
            errors.append(f"Favorite 3 Leg batter missing from sheet rows: {name}")
            continue
        emojis, note = rows[sheet_name]
        # On thin boards (<3 favorites), only require ⭐ on designated favorites.
        if fav_names is not None and len(fav_names) < 3:
            if name in fav_names and "⭐" not in emojis:
                errors.append(f"Favorite 3 Leg batter missing ⭐ on sheet: {name}")
        elif "⭐" not in emojis:
            errors.append(f"Favorite 3 Leg batter missing ⭐ on sheet: {name}")

    return errors


def straight_batters(html_text: str) -> set[str]:
    names: set[str] = set()
    for label in (STRAIGHT_O05_LABEL, STRAIGHT_O15_LABEL):
        try:
            lines = extract_goblin_gambly_lines(html_text, label)
        except (ValueError, json.JSONDecodeError):
            continue
        names.update(gambly_batter(x) for x in lines)
    return names


def validate_two_leg_parlay(html_text: str) -> list[str]:
    """Return list of error strings; empty means OK."""
    errors: list[str] = []
    try:
        three = extract_goblin_gambly_lines(html_text, THREE_LEG_LABEL)
        two = extract_goblin_gambly_lines(html_text, TWO_LEG_LABEL)
    except (ValueError, json.JSONDecodeError) as e:
        return [str(e)]

    if len(two) != 2:
        errors.append(f"2 Leg HR must have 2 legs, found {len(two)}")
    if len(three) != 3:
        return errors

    two_b = [gambly_batter(x) for x in two]
    three_b = [gambly_batter(x) for x in three]
    overlap = set(two_b) & set(three_b)
    if overlap:
        errors.append(f"2 Leg HR and 3 Leg HR share batters: {sorted(overlap)}")

    straight_overlap = set(two_b) & straight_batters(html_text)
    if straight_overlap:
        errors.append(f"2 Leg HR and Straights of the Day share batters: {sorted(straight_overlap)}")

    return errors


def validate_gambly_data_attrs(html_text: str) -> list[str]:
    """Every Goblin Gambly button must have parseable JSON in its data attribute."""
    errors: list[str] = []
    for m in re.finditer(r"data-goblin-gambly-lines='([^']+)'", html_text):
        raw = html.unescape(m.group(1))
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid data-goblin-gambly-lines JSON: {exc}")
            continue
        if not isinstance(parsed, list) or not parsed:
            errors.append("data-goblin-gambly-lines must be a non-empty JSON array")
    if not errors and "data-goblin-gambly-lines=" not in html_text:
        errors.append("missing any data-goblin-gambly-lines buttons")
    return errors


def validate_goblin_parlays(html_text: str, fav_names: set[str] | None = None) -> list[str]:
    errors = validate_three_leg_parlays(html_text, fav_names)
    errors.extend(validate_two_leg_parlay(html_text))
    errors.extend(validate_gambly_data_attrs(html_text))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent
    html_text = (root / "preview" / "index.html").read_text(encoding="utf-8")
    fav_names = None
    date_m = re.search(r'<meta name="sheet-date" content="([^"]+)">', html_text)
    sheet_date = date_m.group(1) if date_m else None
    build = root / f"build-sheet-{sheet_date}.py" if sheet_date else None
    if build and build.is_file():
        import importlib.util

        spec = importlib.util.spec_from_file_location("build_sheet", build)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fav_names = {x.split(" (")[0] for x in mod.FAVS}

    errors = validate_goblin_parlays(html_text, fav_names)
    for e in errors:
        print("FAIL", e)
    if errors:
        return 1
    print("OK   3 Leg HR and Favorite 3 Leg are distinct ⭐ favorites")
    print("OK   2 Leg HR is distinct from 3 Leg HR and Straights of the Day")
    print("OK   All Goblin Gambly data attributes parse as JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
