#!/usr/bin/env python3
"""One-shot: write clean patch-0518-index.py from patch-0516 template."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
src = (ROOT / "patch-0516-index.py").read_text(encoding="utf-8")

src = src.replace("2026-05-16", "2026-05-18", 1)
src = src.replace("_games-0516.txt", "_games-0518.txt")
src = src.replace("local only.", "local only, do not deploy.")

src = src.replace(
    """FAV_SET = \"\"\"            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "Angel Martinez (S)",
                "Sal Stewart (R)",
                "Colson Montgomery (L)",
                "Jarred Kelenic (L)",
                "Ian Happ (S)",
                "Alex Bregman (R)",
                "Paul Goldschmidt (R)",
                "Matt Olson (L)",
                "Jo Adell (R)"
            ]);\"\"\"""",
    """FAV_SET = \"\"\"            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "JJ Bleday (L)",
                "Will Benson (L)",
                "James Wood (L)",
                "Juan Soto (L)",
                "Byron Buxton (R)",
                "Yordan Alvarez (L)",
                "Bobby Witt Jr. (R)",
                "Ian Happ (S)",
                "Michael Busch (L)",
                "Michael Conforto (L)",
                "Hunter Goodman (R)",
                "Miguel Vargas (R)",
                "Gavin Sheets (L)",
                "Jackson Merrill (L)",
                "Julio Rodriguez (R)",
                "Will Smith (R)",
                "Shohei Ohtani (L)"
            ]);\"\"\"""",
)

src = src.replace(
    '{"date":"2026-05-18","label":"May 18, 2026 \\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"},'
    '{"date":"2026-05-14","label":"May 14, 2026","href":"/archive/2026-05-14.html"}]}',
    '{"date":"2026-05-18","label":"May 18, 2026 \\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-16","label":"May 16, 2026","href":"/archive/2026-05-16.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"}]}',
)

src = src.replace(
    """TOP5 = \"\"\"                    <div class="top-five-list">
                        <motion.div class="top-five-item"><span>Colson Montgomery <small>Rate Field + Taillon RHB leak</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Shea Langeliers <small>Sutter +18% vs McDonald LHB</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Jo Adell <small>Wrobleski LHB lane at Angel Stadium</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Sal Stewart <small>100.4 EV vs Cantillo</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Drake Baldwin <small>Four HR in window vs Tolle</small></span><strong>92</strong></div>
                    </div>\"\"\"""",
    """TOP5 = \"\"\"                    <div class="top-five-list">
                        <div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></motion.div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </div>\"\"\"""",
)

# Fix accidental motion.div in TOP5 above
src = src.replace(
    """TOP5 = \"\"\"                    <div class="top-five-list">
                        <div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></motion.div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </motion.div>\"\"\"""",
    """TOP5 = \"\"\"                    <div class="top-five-list">
                        <div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </div>\"\"\"""",
)

src = src.replace(
    """WEATHER5_INNER = \"\"\"
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Sutter carry vs McDonald</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Colson Montgomery <small>Rate Field + Taillon leak</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#3 Lawrence Butler <small>Sacramento wind receptivity</small></span><strong>83</strong></div>
                        <div class="summary-item"><span>#4 Nick Kurtz <small>Sutter + McDonald LHB</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#5 Kyle Manzardo <small>Progressive +16% row</small></span><strong>84</strong></div>
                    \"\"\"""",
    """WEATHER5_INNER = \"\"\"
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Angel Stadium carry vs Urena</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Seiya Suzuki <small>Wrigley +42% HR row</small></span><strong>90</strong></div>
                        <motion.div class="summary-item"><span>#3 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></motion.div>
                        <motion.div class="summary-item"><span>#4 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#5 Bobby Witt Jr. <small>Kauffman +35% wind out</small></span><strong>87</strong></div>
                    \"\"\"""",
)

# fix motion in weather
src = src.replace(
    """WEATHER5_INNER = \"\"\"
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Angel Stadium carry vs Urena</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Seiya Suzuki <small>Wrigley +42% HR row</small></span><strong>90</strong></div>
                        <motion.div class="summary-item"><span>#3 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></motion.div>
                        <motion.div class="summary-item"><span>#4 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#5 Bobby Witt Jr. <small>Kauffman +35% wind out</small></span><strong>87</strong></div>
                    \"\"\"""",
    """WEATHER5_INNER = \"\"\"
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Angel Stadium carry vs Urena</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Seiya Suzuki <small>Wrigley +42% HR row</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#3 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#4 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#5 Bobby Witt Jr. <small>Kauffman +35% wind out</small></span><strong>87</strong></div>
                    \"\"\"""",
)

src = src.replace(
    """PARK_INNER = \"\"\"
                        <div class="summary-item"><span>SF @ ATH <small>Sutter Health +18% HR, very high receptivity</small></span><strong>+18%</strong></div>
                        <div class="summary-item"><span>CIN @ CLE <small>Progressive +16% HR, 74°F</small></span><strong>+16%</strong></div>
                        <div class="summary-item"><span>BAL @ WAS <small>Nationals Park +11% HR</small></span><strong>+11%</strong></div>
                        <div class="summary-item"><span>TEX @ HOU <small>Daikin roof closed, +5% HR</small></span><strong>+5%</strong></div>
                    \"\"\"""",
    """PARK_INNER = \"\"\"
                        <div class="summary-item"><span>MIL @ CHC <small>Wrigley +42% HR, 17 mph out</small></span><strong>+42%</strong></div>
                        <div class="summary-item"><span>BOS @ KC <small>Kauffman +35% HR, 18 mph out</small></span><strong>+35%</strong></div>
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +31% HR, 88°F</small></span><strong>+31%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park +9% HR, 92°F</small></span><strong>+9%</strong></div>
                    \"\"\"""",
)

src = src.replace(
    """LONGSHOT_INNER = \"\"\"
                        <motion.div class="summary-item"><span>J.P. Crawford <small>+980 vs Buehler</small></span><strong>79</strong></div>
                        <motion.div class="summary-item"><span>Ezequiel Duran <small>+820 vs deGrom</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Spencer Steer <small>+750 vs Cantillo</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>Teoscar Hernandez <small>+790 vs Soriano</small></span><strong>82</strong></div>
                    \"\"\"""",
    """LONGSHOT_INNER = \"\"\"
                        <div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Kyle Karros <small>+1050 vs Quintana at Coors</small></span><strong>76</strong></div>
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></div>
                    \"\"\"""",
)

# longshot - 0516 doesn't have motion.div, fix replace
src = src.replace(
    """LONGSHOT_INNER = \"\"\"
                        <div class="summary-item"><span>J.P. Crawford <small>+980 vs Buehler</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>Ezequiel Duran <small>+820 vs deGrom</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Spencer Steer <small>+750 vs Cantillo</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>Teoscar Hernandez <small>+790 vs Soriano</small></span><strong>82</strong></div>
                    \"\"\"""",
    """LONGSHOT_INNER = \"\"\"
                        <motion.div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Kyle Karros <small>+1050 vs Quintana at Coors</small></span><strong>76</strong></div>
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></motion.div>
                    \"\"\"""",
)

src = src.replace(
    """LONGSHOT_INNER = \"\"\"
                        <motion.div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></motion.div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Kyle Karros <small>+1050 vs Quintana at Coors</small></span><strong>76</strong></div>
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></motion.div>
                    \"\"\"""",
    """LONGSHOT_INNER = \"\"\"
                        <motion.div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Kyle Karros <small>+1050 vs Quintana at Coors</small></span><strong>76</strong></div>
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></div>
                    \"\"\"""",
)

# again fix longshot - no motion
src = src.replace('<motion.div class="summary-item"><span>Luis Arraez', '<motion.div class="summary-item"><span>Luis Arraez')
src = src.replace(
    '<motion.div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>',
    '<div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>',
)

src = src.replace(
    """FADES_INNER = \"\"\"
                        <div class="summary-item"><span>SD @ SEA <small>T-Mobile -11% HR, 55°F, 57% rain</small></span><strong>-11%</strong></div>
                        <div class="summary-item"><span>MIL @ MIN <small>Target Field -7% HR</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BOS @ ATL <small>Truist -8% HR row</small></span><strong>-8%</strong></div>
                        <div class="summary-item"><span>PHI @ PIT <small>PNC -8% HR row</small></span><strong>-8%</strong></div>
                    \"\"\"""",
    """FADES_INNER = \"\"\"
                        <div class="summary-item"><span>CHW @ SEA <small>T-Mobile -21% runs row, dome</small></span><strong>-21%</strong></div>
                        <div class="summary-item"><span>LAD @ SD <small>Petco -7% HR row</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></motion.div>
                        <div class="summary-item"><span>TEX @ COL <small>Coors cold 36°F suppresses carry</small></span><strong>~flat</strong></div>
                    \"\"\"""",
)

src = src.replace('</strong></motion.div>\n                        <div class="summary-item"><span>TEX @ COL', '</strong></motion.div>\n                        <div class="summary-item"><span>TEX @ COL')
src = src.replace(
    '<div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></motion.div>',
    '<div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></div>',
)

src = src.replace(
    'text = text.replace(\'content="2026-05-15"\', \'content="2026-05-18"\')',
    'text = re.sub(r\'content="2026-05-\\d+"\', \'content="2026-05-18"\', text, count=1)',
)
src = src.replace(
    'text = text.replace(\'content="2026-05-16"\', \'content="2026-05-18"\')\n    text = re.sub',
    'text = re.sub',
)
src = src.replace(
    "<p>Saturday, May 16, 2026 — Worst Pickz HR cheat sheet",
    "<p>Monday, May 18, 2026 — Worst Pickz HR cheat sheet",
)
src = src.replace(
    "This board covers <strong>41 listed HR props</strong> across <strong>9 games</strong>, with <strong>9 Worst Pickz Favorite</strong>",
    "This board covers <strong>88 listed HR props</strong> across <strong>14 games</strong>, with <strong>17 Worst Pickz Favorite</strong>",
)

# Remove any motion.div typos
src = src.replace("<motion.div ", "<div ")
src = src.replace("</motion.div>", "</div>")

(ROOT / "patch-0518-index.py").write_text(src, encoding="utf-8")
print("wrote clean patch-0518-index.py")
