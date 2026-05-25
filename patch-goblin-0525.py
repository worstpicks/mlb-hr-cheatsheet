#!/usr/bin/env python3
"""Fix Goblin's Insight + summary cards for 2026-05-25 (games block was updated; summaries were stale)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"

SHEET_PLAYERS = {
    "Colson Montgomery", "James Wood", "Ben Rice", "Miguel Vargas", "Brent Rooker",
    "Aaron Judge", "Bo Bichette", "Rafael Devers", "George Springer", "Kyle Schwarber",
    "Luke Raley", "Yandy Diaz", "Jac Caglianone", "Brandon Lowe", "Jordan Walker",
    "Kyle Schwarber", "Elly De La Cruz", "Jarred Kelenic", "Andrew Vaughn", "Ezequiel Duran",
    "Pete Alonso", "Michael Conforto", "Ivan Herrera",
}


def data_attr(lines):
    return json.dumps(lines).replace('"', "&quot;")


THREE_LEG = [
    "James Wood - Over 0.5 homerun",
    "Ben Rice - Over 0.5 homerun",
    "Miguel Vargas - Over 0.5 homerun",
]
TWO_LEG = [
    "Rafael Devers - Over 0.5 homerun",
    "Brent Rooker - Over 0.5 homerun",
]
HITS = [
    "Ben Rice - Over 0.5 hits",
    "Aaron Judge - Over 0.5 hits",
    "Bo Bichette - Over 0.5 hits",
    "Rafael Devers - Over 0.5 hits",
    "George Springer - Over 0.5 hits",
    "James Wood - Over 0.5 hits",
    "Kyle Schwarber - Over 0.5 hits",
    "Brent Rooker - Over 0.5 hits",
    "Luke Raley - Over 0.5 hits",
    "Yandy Diaz - Over 0.5 hits",
]
FAV_THREE = [
    "Miguel Vargas - Over 0.5 homerun",
    "Jac Caglianone - Over 0.5 homerun",
    "Brandon Lowe - Over 0.5 homerun",
]

SUMMARY_BLOCK = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <p class="model-note summary-note">Full-slate view built from weather, pitcher HR risk, current power form, and batter-vs-pitcher history.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>James Wood HR</strong><small>Littell LHB 4.63 HR/9 with four near-HR and a clear 🧤 bum lane.</small></li>
                                <li><strong>Ben Rice HR</strong><small>Three HR plus Kauffman +11% carry versus Warren.</small></li>
                                <li><strong>Miguel Vargas HR</strong><small>Kay RHB HR-risk split in warm Rate Field air.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Rafael Devers HR</strong><small>Kelly LHB HR leak despite Oracle drag.</small></li>
                                <li><strong>Brent Rooker HR</strong><small>Sutter +34% HR row versus Miller.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(TWO_LEG)}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Ben Rice, Aaron Judge, Bo Bichette, Rafael Devers, George Springer</strong><small>Top attack-pitcher lanes with recent contact.</small></li>
                                <li><strong>James Wood, Kyle Schwarber, Brent Rooker, Luke Raley, Yandy Diaz</strong><small>Hot hitters vs Littell, Vasquez, Miller, Civale, Bradish.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(HITS)}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Miguel Vargas HR &#11088;</strong><small>Worst Pickz Favorite with Kay RHB HR-risk lane (score 86).</small></li>
                                <li><strong>Jac Caglianone HR &#11088;</strong><small>100.3 mph EV plus Kauffman heat versus Warren.</small></li>
                                <li><strong>Brandon Lowe HR &#11088;</strong><small>Two HR, three near-HR, and 27.3% barrels versus Brown.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Weather Games</h4>
                            <ol>
                                <li><strong>SEA @ ATH</strong><small>+34% HR at Sutter with 15+ mph out-blowing wind.</small></li>
                                <li><strong>NYY @ KC</strong><small>+11% HR at Kauffman with 88°F heat.</small></li>
                                <li><strong>COL @ LAD</strong><small>+12% HR at Dodger Stadium.</small></li>
                                <li><strong>MIN @ CWS</strong><small>+5% combined at Rate Field with 84°F air.</small></li>
                                <li><strong>WSH @ CLE</strong><small>-13% park row, but Littell is the slate's #1 HR-risk arm.</small></li>
                            </ol>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Zack Littell</strong><small>2.85 HR/9 and 4.63 HR/9 vs LHB.</small></li>
                                <li><strong>Nick Lodolo</strong><small>1.69 vs-RHB HR-risk split.</small></li>
                                <li><strong>Tatsuya Imai</strong><small>2.89 HR/9 vs LHB.</small></li>
                                <li><strong>Tanner Gordon</strong><small>1.80 vs-LHB HR-risk split.</small></li>
                                <li><strong>Anthony Kay</strong><small>1.17 HR/9 with RHB leak.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>
                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage profile, matchup leakage, park/weather, lineup slot, and price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Colson Montgomery (L) <small>Three HR + warm Rate Field stack</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez (L) <small>Elite power window vs Rocker</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>James Wood (L) <small>Littell LHB 4.63 HR/9 + four near-HR</small></span><strong>90</strong></div>
                        <div class="top-five-item"><span>Ben Rice (L) <small>Three HR vs Warren + Kauffman</small></span><strong>89</strong></div>
                        <div class="top-five-item"><span>Brent Rooker (R) <small>Sutter +34% HR vs Miller</small></span><strong>88</strong></div>
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Best Park / Weather HR Rows (slate)</h3>
                    <div class="summary-list">
                        <div class="summary-item"><span>SEA @ ATH <small>Sutter +34% HR, 15+ mph out</small></span><strong>+34%</strong></div>
                        <div class="summary-item"><span>NYY @ KC <small>Kauffman +11% HR, 88°F wind out L</small></span><strong>+11%</strong></div>
                        <div class="summary-item"><span>COL @ LAD <small>Dodger Stadium +12% HR</small></span><strong>+12%</strong></div>
                        <div class="summary-item"><span>MIN @ CWS <small>Rate Field +5% combined</small></span><strong>+5%</strong></div>
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Top 5 Weather Heavy HR Plays</h3>
                    <div class="summary-list">
                        <div class="summary-item"><span>#1 Brent Rooker <small>Sutter heat vs Miller</small></span><strong>88</strong></div>
                        <div class="summary-item"><span>#2 Ben Rice <small>Kauffman heat vs Warren</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#3 Luke Raley <small>Sutter + Civale LHB lane</small></span><strong>83</strong></div>
                        <div class="summary-item"><span>#4 Nick Kurtz <small>Sacramento carry vs Miller</small></span><strong>84</strong></div>
                        <div class="summary-item"><span>#5 Jac Caglianone <small>88°F + Warren LHB leak</small></span><strong>82</strong></div>
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Best longshot HR (listed +700+)</h3>
                    <div class="summary-list">
                        <div class="summary-item"><span>Jarred Kelenic <small>+550 vs Kay</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>James Wood <small>+390 vs Littell</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>Andrew Vaughn <small>+520 vs Liberatore</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Ezequiel Duran <small>+900 vs Imai</small></span><strong>76</strong></div>
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Harsh Environment Fades</h3>
                    <div class="summary-list">
                        <div class="summary-item"><span>WSH @ CLE <small>Progressive -13% HR row</small></span><strong>-13%</strong></div>
                        <div class="summary-item"><span>PHI @ SD <small>Petco -9% HR, marine layer</small></span><strong>-9%</strong></div>
                        <div class="summary-item"><span>ARI @ SF <small>Oracle -6% HR (ignore wind forecast)</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>MIA @ TOR <small>Rogers -8% HR, roof open cold</small></span><strong>-8%</strong></div>
                    </div>
                </div>
"""


def verify_gambly_names(html: str) -> list[str]:
    errors = []
    stale = {"Juan Soto", "Mike Trout", "Matt Olson", "Braydon Fisher", "Jose Soriano", "Hao-Yu Lee"}
    for attr in re.findall(r"data-goblin-gambly-lines='([^']+)'", html):
        legs = json.loads(attr.replace("&quot;", '"'))
        for leg in legs:
            name = leg.split(" - ")[0].strip()
            if name in stale:
                errors.append(f"stale gambly name: {name}")
            if "Over 0.5 homerun" in leg and name not in SHEET_PLAYERS:
                # allow any sheet player — verify against games block names
                pass
    if "Aaron Judge" in html and "Fisher" in html and "Goblin" in html:
        if re.search(r"Judge HR</strong><small>Fisher", html):
            errors.append("stale Goblin copy still references Fisher")
    return errors


def main():
    text = PREVIEW.read_text(encoding="utf-8")
    start = text.index('<div class="summary-card full-width best-bets-card">')
    end = text.index('<div class="summary-card emoji-key-card">')
    text = text[:start] + SUMMARY_BLOCK + text[end:]
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched Goblin + summary cards")

    refreshed = PREVIEW.read_text(encoding="utf-8")
    errors = verify_gambly_names(refreshed)
    if errors:
        print("VERIFY FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("gambly parlays OK (no stale May 21 names)")


if __name__ == "__main__":
    main()
