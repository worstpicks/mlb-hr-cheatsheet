#!/usr/bin/env python3
"""Apply the 8/16 straight and Goblin judgment locks to patch-0816-preview.py."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "patch-0816-preview.py"

STRAIGHT_LOCK = '''# 8/16 judgment: Lindor has the most complete O0.5 lane — a +1.43 platoon split into
# Jake Irvin (+1.28 HR risk, one of four bums on the slate), a 92.0 zone fit and real
# form at 1 HR / 2 near-HR. Josh Bell grades higher on raw zone (104.3) but his split
# and risk are both under half of Lindor's.
# Murakami takes O1.5 on the loudest multi-HR profile of the slate — 3 HR and 3
# near-HR with a +18% park — in a different game.
_o05_lock = next((r for r in straight_rows if r["name_plain"] == "Francisco Lindor"), None)
_o15_lock = next((r for r in straight_rows if r["name_plain"] == "Munetaka Murakami"), None)
if _o05_lock is not None:
    straight_o05 = _o05_lock
if _o15_lock is not None and _o15_lock["game_key"] != straight_o05["game_key"]:
    straight_o15 = _o15_lock
straight_names = {straight_o05["name"], straight_o15["name"]}
'''

GOBLIN_LOCK = '''
# 8/16 Goblin judgment: three separate games per ticket, every leg carrying a positive
# split AND positive opposing HR risk.
#   3 Leg  — Josh Bell (104.3 zone, best on the board, +0.41/+0.40, +5% park),
#            Carter Jensen (+1.87 split into Ryan Johnson, the slate's worst arm at
#            +1.63), Feduccia (+0.99/+0.89).
#   2 Leg  — Duran into bum Bachar with a +13% park, and Baty on 2 HR with a +1.43
#            split; neither reuses a straight.
#   Fav 3  — only three favorites were listed, so all three carry the card.
_top3_lock_names = ["Josh Bell", "Carter Jensen", "Hunter Feduccia"]
_two_lock_names = ["Jarren Duran", "Brett Baty"]
_fav3_lock_names = ["Wilyer Abreu", "Pete Alonso", "Brandon Lowe"]
_top3_lock = [rows_by_plain[n] for n in _top3_lock_names if n in rows_by_plain]
_two_lock = [rows_by_plain[n] for n in _two_lock_names if n in rows_by_plain]
_fav3_lock = [rows_by_plain[n] for n in _fav3_lock_names if n in rows_by_plain]
if len(_top3_lock) == 3:
    top3 = _top3_lock
if len(_two_lock) == 2:
    two_leg = _two_lock
if len(_fav3_lock) == 3:
    fav3 = _fav3_lock
'''


def main() -> int:
    t = TARGET.read_text(encoding="utf-8")

    anchor = 'straight_names = {straight_o05["name"], straight_o15["name"]}\n'
    idx = t.rindex(anchor)
    t = t[:idx] + STRAIGHT_LOCK + t[idx + len(anchor) :]

    anchor2 = 'rows_by_plain = {r["name_plain"]: r for r in rows}\n'
    idx2 = t.index(anchor2)
    end = idx2 + len(anchor2)
    t = t[:end] + GOBLIN_LOCK + t[end:]

    TARGET.write_text(t, encoding="utf-8")
    assert '"Francisco Lindor"' in t and '"Josh Bell", "Carter Jensen"' in t
    print("locked straights (Lindor / Murakami) and Goblin legs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
