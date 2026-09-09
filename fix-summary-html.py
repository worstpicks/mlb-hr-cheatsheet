#!/usr/bin/env python3
from pathlib import Path

SUMMARY_BLOCK = (
    "        <section class=\"summary-section\">\n"
    "            <div class=\"summary-grid\">\n"
    "                <motion.div class=\"summary-card full-width top-five-card\">\n"
)
# Fix accidental motion tags
SUMMARY_BLOCK = SUMMARY_BLOCK.replace("motion.", "div")

SUMMARY_BLOCK = (
    "        <section class=\"summary-section\">\n"
    "            <div class=\"summary-grid\">\n"
    "                <div class=\"summary-card full-width top-five-card\">\n"
    "                    <h3>Top 5 HR Tickets (Holistic)</h3>\n"
    "                    <p class=\"model-note summary-note\">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>\n"
    "                    <div class=\"top-five-list\">\n"
    "                        <div class=\"top-five-item\"><span>Colson Montgomery <small>Rate Field + Taillon RHB leak</small></span><strong>94</strong></div>\n"
    "                        <div class=\"top-five-item\"><span>Shea Langeliers <small>Sutter +18% vs McDonald LHB</small></span><strong>94</strong></div>\n"
    "                        <div class=\"top-five-item\"><span>Jo Adell <small>Wrobleski LHB lane at Angel Stadium</small></span><strong>93</strong></div>\n"
    "                        <div class=\"top-five-item\"><span>Sal Stewart <small>100.4 EV vs Cantillo</small></span><strong>93</strong></div>\n"
    "                        <div class=\"top-five-item\"><span>Drake Baldwin <small>Four HR in window vs Tolle</small></span><strong>92</strong></div>\n"
    "                    </div>\n"
    "                </div>\n"
    "                <div class=\"summary-card\">\n"
    "                    <h3>Best Park / Weather HR Rows (slate)</h3>\n"
    "                    <div class=\"summary-list\">\n"
    "                        <div class=\"summary-item\"><span>SF @ ATH <small>Sutter Health +18% HR, very high receptivity</small></span><strong>+18%</strong></div>\n"
    "                        <div class=\"summary-item\"><span>CIN @ CLE <small>Progressive +16% HR, 74°F</small></span><strong>+16%</strong></div>\n"
    "                        <div class=\"summary-item\"><span>BAL @ WAS <small>Nationals Park +11% HR</small></span><strong>+11%</strong></div>\n"
    "                        <div class=\"summary-item\"><span>TEX @ HOU <small>Daikin roof closed, +5% HR</small></span><strong>+5%</strong></div>\n"
    "                    </div>\n"
    "                </div>\n"
    "                <div class=\"summary-card\">\n"
    "                    <h3>Top 5 Weather Heavy HR Plays</h3>\n"
    "                    <div class=\"summary-list\">\n"
    "                        <motion.div class=\"summary-item\"><span>#1 Shea Langeliers <small>Sutter carry vs McDonald</small></span><strong>94</strong></div>\n"
    "                        <div class=\"summary-item\"><span>#2 Colson Montgomery <small>Rate Field + Taillon leak</small></span><strong>94</strong></div>\n"
    "                        <div class=\"summary-item\"><span>#3 Lawrence Butler <small>Sacramento wind receptivity</small></span><strong>83</strong></div>\n"
    "                        <div class=\"summary-item\"><span>#4 Nick Kurtz <small>Sutter + McDonald LHB</small></span><strong>86</strong></div>\n"
    "                        <div class=\"summary-item\"><span>#5 Kyle Manzardo <small>Progressive +16% row</small></span><strong>84</strong></div>\n"
    "                    </div>\n"
    "                </div>\n"
    "                <div class=\"summary-card\">\n"
    "                    <h3>Best longshot HR (listed +700+)</h3>\n"
    "                    <div class=\"summary-list\">\n"
    "                        <div class=\"summary-item\"><span>J.P. Crawford <small>+980 vs Buehler</small></span><strong>79</strong></div>\n"
    "                        <div class=\"summary-item\"><span>Ezequiel Duran <small>+820 vs deGrom</small></span><strong>78</strong></div>\n"
    "                        <div class=\"summary-item\"><span>Spencer Steer <small>+750 vs Cantillo</small></span><strong>79</strong></div>\n"
    "                        <div class=\"summary-item\"><span>Teoscar Hernandez <small>+790 vs Soriano</small></span><strong>82</strong></div>\n"
    "                    </div>\n"
    "                </div>\n"
    "                <div class=\"summary-card\">\n"
    "                    <h3>Harsh Environment Fades</h3>\n"
    "                    <div class=\"summary-list\">\n"
    "                        <div class=\"summary-item\"><span>SD @ SEA <small>T-Mobile -11% HR, 55°F, 57% rain</small></span><strong>-11%</strong></div>\n"
    "                        <div class=\"summary-item\"><span>MIL @ MIN <small>Target Field -7% HR</small></span><strong>-7%</strong></motion.div>\n"
    "                        <div class=\"summary-item\"><span>BOS @ ATL <small>Truist -8% HR row</small></span><strong>-8%</strong></div>\n"
    "                        <div class=\"summary-item\"><span>PHI @ PIT <small>PNC -8% HR row</small></span><strong>-8%</strong></div>\n"
    "                    </div>\n"
    "                </div>\n"
)
SUMMARY_BLOCK = SUMMARY_BLOCK.replace("motion.", "div")

ROOT = Path(__file__).resolve().parent
for rel in ("index.html", "preview/index.html"):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    start = text.index('        <section class="summary-section">')
    end = text.index('                <div class="summary-card emoji-key-card">')
    text = text[:start] + SUMMARY_BLOCK + text[end:]
    path.write_text(text, encoding="utf-8")
    print("fixed", path)
