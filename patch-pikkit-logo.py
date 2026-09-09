#!/usr/bin/env python3
"""Use Pikkit wordmark logo (heart clover + text) in header instead of square icon."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

OLD_LINK_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(254, 215, 170, 0.4);
            background: rgba(15, 23, 42, 0.55);
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: rgba(15, 23, 42, 0.88);
            filter: brightness(1.06);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 11px;
        }"""

NEW_LINK_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: auto;
            min-width: 42px;
            height: 42px;
            padding: 0 11px 0 9px;
            border-radius: 12px;
            border: 1px solid rgba(140, 146, 146, 0.45);
            background: #000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: #0a0a0a;
            filter: brightness(1.08);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            height: 24px;
            width: auto;
            max-width: 112px;
            object-fit: contain;
        }"""

OLD_MEDIA = """            .header-actions .pikkit-link,
            .header-actions .pikkit-link__icon { width: 38px; height: 38px; }"""

NEW_MEDIA = """            .header-actions .pikkit-link {
                height: 38px;
                padding: 0 9px 0 7px;
            }
            .header-actions .pikkit-link__icon {
                height: 20px;
                max-width: 96px;
            }"""

IMG_RE = re.compile(
    r'(<img class="pikkit-link__icon" src=")(?:\.\./)?assets/pikkit-(?:icon|logo)\.svg(" width=")\d+(" height=")\d+(" alt="" decoding="async">)',
)


def patch_file(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    asset = "../assets/pikkit-logo.svg" if "/archive/" in str(path).replace("\\", "/") else "assets/pikkit-logo.svg"

    if OLD_LINK_CSS in t:
        t = t.replace(OLD_LINK_CSS, NEW_LINK_CSS, 1)

    if OLD_MEDIA in t:
        t = t.replace(OLD_MEDIA, NEW_MEDIA, 1)

    t = IMG_RE.sub(lambda m: f'{m.group(1)}{asset}" width="108" height="24{m.group(4)}', t)
    t = re.sub(
        r'(pikkit-logo\.svg)[^"]*(" alt="" decoding="async">)',
        r'\1" width="108" height="24"\2',
        t,
    )
    if "pikkit-logo.svg" not in t and "pikkit-icon.svg" in t:
        t = t.replace("pikkit-icon.svg", "pikkit-logo.svg")

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


def main() -> None:
    logo = ROOT / "preview" / "assets" / "pikkit-logo.svg"
    if not logo.is_file():
        raise SystemExit(f"missing {logo}")
    for p in SHEET_HTML:
        if p.is_file():
            patch_file(p)


if __name__ == "__main__":
    main()
