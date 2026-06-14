#!/usr/bin/env python3
"""Add GB% and Hard Hit signal pills (High/Low) to index HTML files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [ROOT / "preview" / "index.html", ROOT / "index.html"]

CSS_AFTER_FLAT = """        .signal-pill--flat .signal-pill__dot {
            background: #94a3b8;
            color: #94a3b8;
        }
        .signal-pill--high-gb {
            color: #fde68a;
            background: linear-gradient(135deg, rgba(120, 53, 15, 0.52) 0%, rgba(245, 158, 11, 0.14) 100%);
            border-color: rgba(251, 191, 36, 0.42);
        }
        .signal-pill--high-gb .signal-pill__dot {
            background: #fbbf24;
            color: #fbbf24;
        }
        .signal-pill--low-gb {
            color: #a5f3fc;
            background: linear-gradient(135deg, rgba(14, 116, 144, 0.48) 0%, rgba(34, 211, 238, 0.12) 100%);
            border-color: rgba(34, 211, 238, 0.38);
        }
        .signal-pill--low-gb .signal-pill__dot {
            background: #22d3ee;
            color: #22d3ee;
        }
        .signal-pill--high-hh {
            color: #bbf7d0;
            background: linear-gradient(135deg, rgba(21, 94, 52, 0.5) 0%, rgba(52, 211, 153, 0.14) 100%);
            border-color: rgba(52, 211, 153, 0.42);
        }
        .signal-pill--high-hh .signal-pill__dot {
            background: #34d399;
            color: #34d399;
        }
        .signal-pill--low-hh {
            color: #fecdd3;
            background: linear-gradient(135deg, rgba(136, 19, 55, 0.48) 0%, rgba(244, 63, 94, 0.12) 100%);
            border-color: rgba(251, 113, 133, 0.38);
        }
        .signal-pill--low-hh .signal-pill__dot {
            background: #f43f5e;
            color: #f43f5e;
        }"""

CSS_BEFORE = """        .signal-pill--flat .signal-pill__dot {
            background: #94a3b8;
            color: #94a3b8;
        }
        .emoji-key-item--signal {"""

LIGHT_AFTER_FLAT = """        html.theme-light .signal-pill--flat .signal-pill__dot { background: #64748b; color: #64748b; }
        html.theme-light .signal-pill--high-gb {
            color: #78350f;
            background: linear-gradient(135deg, rgba(254, 243, 199, 0.95) 0%, rgba(251, 191, 36, 0.28) 100%);
            border-color: rgba(245, 158, 11, 0.45);
        }
        html.theme-light .signal-pill--high-gb .signal-pill__dot { background: #d97706; color: #d97706; }
        html.theme-light .signal-pill--low-gb {
            color: #155e75;
            background: linear-gradient(135deg, rgba(207, 250, 254, 0.95) 0%, rgba(34, 211, 238, 0.25) 100%);
            border-color: rgba(6, 182, 212, 0.4);
        }
        html.theme-light .signal-pill--low-gb .signal-pill__dot { background: #0891b2; color: #0891b2; }
        html.theme-light .signal-pill--high-hh {
            color: #14532d;
            background: linear-gradient(135deg, rgba(209, 250, 229, 0.95) 0%, rgba(52, 211, 153, 0.28) 100%);
            border-color: rgba(16, 185, 129, 0.42);
        }
        html.theme-light .signal-pill--high-hh .signal-pill__dot { background: #059669; color: #059669; }
        html.theme-light .signal-pill--low-hh {
            color: #9f1239;
            background: linear-gradient(135deg, rgba(254, 205, 211, 0.95) 0%, rgba(244, 63, 94, 0.22) 100%);
            border-color: rgba(244, 63, 94, 0.35);
        }
        html.theme-light .signal-pill--low-hh .signal-pill__dot { background: #e11d48; color: #e11d48; }"""

LIGHT_BEFORE = """        html.theme-light .signal-pill--flat .signal-pill__dot { background: #64748b; color: #64748b; }
        html.theme-light .pick-odds { color: #047857; }"""

EMOJI_KEY_AFTER = """                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--whiff legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">Whiff</span></span> High whiff / K% — swing-and-miss risk</div>
                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--high-gb legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">High GB</span></span> Groundball-heavy profile (≥52% GB)</div>
                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--low-gb legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">Low GB</span></span> Low groundball rate (≤29% GB)</div>
                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--high-hh legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">High HH</span></span> High hard-hit rate (≥50% HH)</div>
                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--low-hh legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">Low HH</span></span> Low hard-hit rate (≤30% HH)</div>"""

EMOJI_KEY_BEFORE = """                        <div class="emoji-key-item emoji-key-item--signal"><span class="signal-pill signal-pill--whiff legend-sample" aria-hidden="true"><span class="signal-pill__dot"></span><span class="signal-pill__text">Whiff</span></span> High whiff / K% — swing-and-miss risk</div>"""

QUICK_AFTER = """                <span class="quick-legend-item" title="High whiff or K%">Whiff — K/whiff risk</span>
                <span class="quick-legend-item" title="Groundball-heavy profile">High GB — ≥52%</span>
                <span class="quick-legend-item" title="Low groundball rate">Low GB — ≤29%</span>
                <span class="quick-legend-item" title="High hard-hit rate">High HH — ≥50%</span>
                <span class="quick-legend-item" title="Low hard-hit rate">Low HH — ≤30%</span>"""

QUICK_BEFORE = """                <span class="quick-legend-item" title="High whiff or K%">Whiff — K/whiff risk</span>"""

PICK_SIGNALS_OLD = """            function pickSignalsHtml(row) {
                const pills = [];
                if (row.formTrend === "heating") {
                    pills.push(
                        '<span class="signal-pill signal-pill--hot" title="L5 power trending up">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Hot</span></span>'
                    );
                } else if (row.formTrend === "cooling") {
                    pills.push(
                        '<span class="signal-pill signal-pill--cold" title="L5 power cooling off">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Cool</span></span>'
                    );
                }
                if (row.contactRisk) {
                    pills.push(
                        '<span class="signal-pill signal-pill--whiff" title="High whiff or K% — swing-and-miss risk">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Whiff</span></span>'
                    );
                }
                if (!pills.length) return "";
                return `<div class="pick-signals">${pills.join("")}</div>`;
            }"""

PICK_SIGNALS_NEW = """            function pickSignalsHtml(row) {
                const pills = [];
                if (row.formTrend === "heating") {
                    pills.push(
                        '<span class="signal-pill signal-pill--hot" title="L5 power trending up">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Hot</span></span>'
                    );
                } else if (row.formTrend === "cooling") {
                    pills.push(
                        '<span class="signal-pill signal-pill--cold" title="L5 power cooling off">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Cool</span></span>'
                    );
                }
                if (row.contactRisk) {
                    pills.push(
                        '<span class="signal-pill signal-pill--whiff" title="High whiff or K% — swing-and-miss risk">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Whiff</span></span>'
                    );
                }
                if (row.gbSignal === "high") {
                    const gb = row.gbPct != null ? ` (${row.gbPct}%)` : "";
                    pills.push(
                        '<span class="signal-pill signal-pill--high-gb" title="Groundball-heavy profile' + gb + '">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">High GB</span></span>'
                    );
                } else if (row.gbSignal === "low") {
                    const gb = row.gbPct != null ? ` (${row.gbPct}%)` : "";
                    pills.push(
                        '<span class="signal-pill signal-pill--low-gb" title="Low groundball rate' + gb + '">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Low GB</span></span>'
                    );
                }
                if (row.hhSignal === "high") {
                    const hh = row.hhPct != null ? ` (${row.hhPct}%)` : "";
                    pills.push(
                        '<span class="signal-pill signal-pill--high-hh" title="High hard-hit rate' + hh + '">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">High HH</span></span>'
                    );
                } else if (row.hhSignal === "low") {
                    const hh = row.hhPct != null ? ` (${row.hhPct}%)` : "";
                    pills.push(
                        '<span class="signal-pill signal-pill--low-hh" title="Low hard-hit rate' + hh + '">' +
                            '<span class="signal-pill__dot" aria-hidden="true"></span><span class="signal-pill__text">Low HH</span></span>'
                    );
                }
                if (!pills.length) return "";
                return `<div class="pick-signals">${pills.join("")}</div>`;
            }"""


def patch_file(path: Path) -> bool:
    if not path.is_file():
        print(f"skip missing {path}")
        return False
    text = path.read_text(encoding="utf-8")
    orig = text
    if "signal-pill--high-gb" not in text:
        text = text.replace(CSS_BEFORE, CSS_AFTER_FLAT + "\n        .emoji-key-item--signal {", 1)
    if "html.theme-light .signal-pill--high-gb" not in text:
        text = text.replace(LIGHT_BEFORE, LIGHT_AFTER_FLAT + "\n        html.theme-light .pick-odds { color: #047857; }", 1)
    if "High GB — ≥52%" not in text:
        text = text.replace(QUICK_BEFORE, QUICK_AFTER, 1)
    if "signal-pill--high-gb legend-sample" not in text:
        text = text.replace(EMOJI_KEY_BEFORE, EMOJI_KEY_AFTER, 1)
    if 'row.gbSignal === "high"' not in text:
        text = text.replace(PICK_SIGNALS_OLD, PICK_SIGNALS_NEW, 1)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"patched {path.name}")
        return True
    print(f"already patched {path.name}")
    return False


def main() -> None:
    for path in TARGETS:
        patch_file(path)


if __name__ == "__main__":
    main()
