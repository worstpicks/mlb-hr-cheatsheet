#!/usr/bin/env python3
"""Pikkit wordmark — neutral header styling (no blue brand color)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_BLOCK_RE = re.compile(
    r"        \.pikkit-link \{[^}]+\}\n"
    r"        \.pikkit-link:hover \{[^}]+\}\n"
    r"        \.pikkit-link:focus-visible \{[^}]+\}\n"
    r"        \.pikkit-link__wordmark \{[^}]+\}\n"
    r"(?:        \.pikkit-link:hover \.pikkit-link__wordmark \{[^}]+\}\n)?",
    re.DOTALL,
)

PIKKIT_CSS_NEW = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            padding: 0 12px;
            border-radius: 12px;
            border: 1px solid rgba(254, 215, 170, 0.4);
            background: rgba(15, 23, 42, 0.55);
            text-decoration: none;
            flex-shrink: 0;
            line-height: 1;
            position: relative;
            z-index: 12;
        }
        .pikkit-link:hover {
            background: rgba(15, 23, 42, 0.88);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__wordmark {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            font-size: 0.88rem;
            letter-spacing: 0.03em;
            line-height: 1;
            color: #fff7ed;
            pointer-events: none;
            user-select: none;
        }
        .pikkit-link:hover .pikkit-link__wordmark {
            color: #fff;
        }
"""

THEME_PIKKIT_RE = re.compile(
    r"        html\.theme-light \.pikkit-link \{[^}]+\}\n"
    r"        html\.theme-light \.pikkit-link:hover \{[^}]+\}\n"
    r"        html\.theme-light \.pikkit-link__wordmark \{[^}]+\}\n",
    re.DOTALL,
)

THEME_HEADER_GROUP_OLD = """        html.theme-light .header-actions .theme-toggle,
        html.theme-light .header-actions .social-x,
        html.theme-light .header-actions .header-install-btn {"""

THEME_HEADER_GROUP_NEW = """        html.theme-light .header-actions .theme-toggle,
        html.theme-light .header-actions .social-x,
        html.theme-light .header-actions .pikkit-link,
        html.theme-light .header-actions .header-install-btn {"""

THEME_HEADER_HOVER_OLD = """        html.theme-light .header-actions .theme-toggle:hover,
        html.theme-light .header-actions .social-x:hover,
        html.theme-light .header-actions .header-install-btn:hover {"""

THEME_HEADER_HOVER_NEW = """        html.theme-light .header-actions .theme-toggle:hover,
        html.theme-light .header-actions .social-x:hover,
        html.theme-light .header-actions .pikkit-link:hover,
        html.theme-light .header-actions .header-install-btn:hover {"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    if "pikkit-link" not in t:
        print("skip", path.relative_to(ROOT))
        return
    o = t

    if PIKKIT_BLOCK_RE.search(t):
        t = PIKKIT_BLOCK_RE.sub(PIKKIT_CSS_NEW, t, count=1)

    if THEME_PIKKIT_RE.search(t):
        t = THEME_PIKKIT_RE.sub(
            "        html.theme-light .pikkit-link__wordmark { color: #0f172a; }\n",
            t,
            count=1,
        )

    if THEME_HEADER_GROUP_OLD in t and ".pikkit-link," not in THEME_HEADER_GROUP_OLD:
        t = t.replace(THEME_HEADER_GROUP_OLD, THEME_HEADER_GROUP_NEW, 1)
    if THEME_HEADER_HOVER_OLD in t and ".pikkit-link:hover" not in THEME_HEADER_HOVER_OLD:
        t = t.replace(THEME_HEADER_HOVER_OLD, THEME_HEADER_HOVER_NEW, 1)

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("skip (no changes)", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in SHEET_HTML:
        if p.is_file():
            patch(p)
