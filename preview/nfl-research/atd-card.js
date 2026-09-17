/* Worst Pickz — player card popup on the NFL cheat sheet.
 * Tapping a name opens the same card Player Logs opens in the Research tab -- grade,
 * TD chance, projection, matchup, then The Read / Matchup / Last games -- without
 * leaving the sheet. The data rides in the page: nfl_research/atd_sheet.py writes each
 * listed player's Game Board entry into SHEET.cards, so nothing is fetched.
 *
 * The name stays a real link to the player in Player Logs, so a new tab, a middle
 * click, or a page built before the cards existed still gets somewhere useful; the
 * card's own buttons go to Player Logs and the Game Board.
 */
(function () {
    "use strict";

    var SHEET = window.ATD_SHEET;
    if (!SHEET || !SHEET.cards) return;
    var ROOT = SHEET.root || "";

    // ── helpers, matching nfl-research.js ──
    var STAT_NAME = {
        pass_yds: "pass yds", pass_td: "pass TD", rush_yds: "rush yds",
        rec_yds: "rec yds", rec: "rec", tgt: "tgt"
    };
    var PART_LABEL = { matchup: "Matchup", script: "Game script", coverage: "Coverage", usage: "Usage", volume: "Volume" };
    // a reason's edge as a percent from normal, grade points in the tooltip (as nfl-research.js)
    function reasonPct(r) {
        var n = r.points == null ? "" : Math.abs(r.points).toFixed(0);
        var pts = r.points == null ? "" : (r.points >= 0 ? "+" : "−") + n + " grade point" + (n === "1" ? "" : "s");
        if (r.pct != null) {
            var cls = r.pct > 0 ? "nrs-up" : r.pct < 0 ? "nrs-down" : "nrs-br-dim";
            var txt = r.pct === 0 ? "0%" : (r.pct > 0 ? "+" : "−") + Math.abs(r.pct) + "%";
            return '<span class="' + cls + '"' + (pts ? ' title="' + pts + '"' : "") + ">" + txt + "</span>";
        }
        if (r.points == null) return '<span class="nrs-br-dim">—</span>';
        return '<span class="' + (r.points >= 0 ? "nrs-up" : "nrs-down") + '">' + (r.points >= 0 ? "+" : "") + r.points.toFixed(0) + "</span>";
    }
    var TEAM_LOGO = function (abbr) {
        return abbr ? "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/" + abbr.toLowerCase() + ".png" : "";
    };
    var esc = function (s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    };
    var ord = function (n) {
        var s = ["th", "st", "nd", "rd"], v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    };
    var softness = function (rank, of) {
        var soft = of + 1 - rank;
        return soft <= of / 2 ? ord(soft) + " softest" : ord(rank) + " toughest";
    };
    var signedPct = function (index) {
        var p = Math.round((index - 1) * 100);
        return p === 0 ? "even" : (p > 0 ? "+" : "−") + Math.abs(p) + "%";
    };
    function thumb(url) {
        return String(url || "").replace("/image/upload/f_auto,q_auto/", "/image/upload/f_auto,q_auto,w_96/");
    }
    function fmtProj(v, stat) {
        if (v == null) return "—";
        return stat === "pass_td" || stat === "rec" || stat === "tgt" ? v.toFixed(1) : String(Math.round(v));
    }
    function gradeClass(g) {
        if (g == null) return "is-none";
        if (g >= 70) return "is-great";
        if (g >= 58) return "is-good";
        if (g >= 43) return "is-even";
        if (g >= 31) return "is-poor";
        return "is-bad";
    }
    function leakClass(index) {
        if (index == null) return "";
        if (index >= 1.12) return "is-soft";
        if (index >= 1.04) return "is-soft-lite";
        if (index <= 0.88) return "is-tough";
        if (index <= 0.96) return "is-tough-lite";
        return "";
    }
    function weekLabel(g) {
        if (!g.season || g.season === SHEET.season) return "W" + g.week;
        return "W" + g.week + " '" + String(g.season).slice(-2);
    }
    function seasonSpan(seasons) {
        var s = (seasons || []).filter(Boolean);
        if (!s.length) return "";
        var yy = function (y) { return "'" + String(y).slice(-2); };
        return s.length > 1 ? yy(s[0]) + "–" + yy(s[s.length - 1]) : yy(s[0]);
    }
    function matchupVerdict(leaks) {
        var idx = function (r) { return leaks[r] && leaks[r].index != null ? leaks[r].index : null; };
        var pass = ["QB1", "WR1", "WR2", "TE1"].map(idx).filter(function (v) { return v != null; });
        var passIdx = pass.length ? pass.reduce(function (a, b) { return a + b; }, 0) / pass.length : 1;
        var runIdx = idx("RB1") != null ? idx("RB1") : 1;
        if (passIdx >= 1.05 && runIdx >= 1.05) return ["Soft all over", "is-soft"];
        if (passIdx >= 1.06 && passIdx >= runIdx + 0.04) return ["Attack through the air", "is-soft"];
        if (runIdx >= 1.06 && runIdx >= passIdx + 0.04) return ["Attack on the ground", "is-soft"];
        if (passIdx <= 0.94 && runIdx <= 0.97) return ["Tough all over", "is-tough"];
        if (passIdx <= 0.94) return ["Pass game stifled", "is-tough"];
        if (runIdx <= 0.94) return ["Run game stifled", "is-tough"];
        return ["No clear edge", "is-even"];
    }
    function fmtKick(iso) {
        var d = new Date(iso);
        if (!iso || isNaN(d)) return "";
        return d.toLocaleString([], { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
    }

    // the sheet's own row for each player: injury status, market, line, his game
    var PLAY = {};
    (SHEET.games || []).forEach(function (g) {
        Object.keys(g.sides).forEach(function (team) {
            g.sides[team].forEach(function (pl) { if (pl.id) PLAY[pl.id] = { pl: pl, game: g }; });
        });
    });

    function linkFor(p, view) {
        return ROOT + "index.html?season=" + SHEET.season + "&week=" + SHEET.week +
               "&view=" + view + "&player=" + encodeURIComponent(p.player_id || "");
    }

    // ── the card: the same four blocks as the Research tab's popup ──
    function heroHtml(p, play) {
        var tile = function (label, value, sub, cls) {
            return '<div class="nrs-pf-tile' + (cls ? " " + cls : "") + '"><span class="nrs-pf-label">' + label + "</span>" +
                   '<span class="nrs-pf-value">' + value + "</span>" + (sub ? '<span class="nrs-pf-sub">' + sub + "</span>" : "") + "</div>";
        };
        var stats = Object.keys(p.proj || {});
        var head = stats[0];
        var m = p.matchup || {};
        var pl = play && play.pl;
        var rushOnly = pl && pl.mk === "rush_td";
        // the sheet lists a player with under four games without a TD number; so does his card
        var small = pl && pl.m && pl.m.small;
        var tdSub = small ? "too few games to rate"
            : pl && pl.line >= 1.5 && pl.m && pl.m.td2 != null
            ? Math.ceil(pl.line) + "+ TD: " + pl.m.td2 + "%"
            : (rushOnly ? "at least one rushing TD" : "at least one touchdown");
        return '<div class="nrs-pf-hero">' +
            tile("Grade", p.grade == null ? "—" : p.grade, p.low_volume ? "discounted: low volume" : "50 is neutral for him",
                 "nrs-pf-grade " + gradeClass(p.grade)) +
            tile(rushOnly ? "Rush TD chance" : "TD chance", p.td_chance == null || small ? "—" : p.td_chance + "%", tdSub) +
            (head ? tile("Projection", fmtProj(p.proj[head], head), STAT_NAME[head]) : "") +
            (m.index != null ? tile(esc(p.opp) + " vs " + esc(p.role) + "s", signedPct(m.index), softness(m.rank, m.of) + " of " + m.of, leakClass(m.index)) : "") +
            "</div>";
    }

    function readHtml(p) {
        var reasons = (p.reasons || []).map(function (r) {
            var pts = reasonPct(r);
            return '<li><span class="nrs-why-part">' + (PART_LABEL[r.part] || esc(r.part)) + "</span>" + pts +
                   '<span class="nrs-why-text">' + esc(r.text) + "</span></li>";
        }).join("");
        var e = (SHEET.env || {})[p.team] || {};
        var d = (SHEET.env || {})[p.opp] || {};
        var facts = [];
        if (p.share != null) {
            facts.push("<b>" + Math.round(p.share) + "%</b> " + esc(p.share_kind) + " over " + p.games + (p.games === 1 ? " game" : " games") + " · <b>" +
                       Math.round(p.share_l3) + "%</b> over the last 3");
        }
        if (p.pos !== "QB" && p.rz_share != null) {
            facts.push("Handles <b>" + Math.round(p.rz_share) + "%</b> of " + esc(p.team) + "'s red-zone work · " + esc(p.team) +
                       " reaches the 20 <b>" + (e.rz_trips != null ? e.rz_trips.toFixed(1) : "—") + "</b> times a game · " + esc(p.opp) +
                       " lets <b>" + (d.def_rz_td != null ? Math.round(d.def_rz_td) : "—") + "%</b> of those trips score");
        }
        if (p.cov && (p.cov.man_t || p.cov.zone_t)) {
            var ypt = function (v) { return v == null ? "—" : v.toFixed(1); };
            facts.push("<b>" + ypt(p.cov.man_ypt) + "</b> yds/target vs man (" + p.cov.man_t + ") · <b>" + ypt(p.cov.zone_ypt) +
                       "</b> vs zone (" + p.cov.zone_t + ")" + (d.def_man != null ? " · " + esc(p.opp) + " plays man " + Math.round(d.def_man) + "%" : ""));
        }
        var stats = Object.keys(p.proj || {});
        return '<h4 class="nrs-pf-h">Why ' + (p.grade == null ? "no grade" : "a " + p.grade) + "</h4>" +
            '<ul class="nrs-why">' + (reasons || "<li>No components available.</li>") + "</ul>" +
            (facts.length ? '<ul class="nrs-bd-lines">' + facts.map(function (f) { return "<li>" + f + "</li>"; }).join("") + "</ul>" : "") +
            (stats.length ? '<p class="nrs-bd-proj">Projection: ' + stats.map(function (s) {
                return "<b>" + fmtProj(p.proj[s], s) + "</b> " + STAT_NAME[s];
            }).join(" · ") + "</p>" : "");
    }

    function matchupHtml(p) {
        var m = p.matchup || {};
        var stats = Object.keys(p.proj || {});
        var rows = stats.map(function (s) {
            var a = (m.allowed || {})[s], l = (m.league || {})[s];
            var edge = a != null && l ? (a - l) / (l || 1) : null;
            var cls = edge == null ? "" : edge >= 0.08 ? "nrs-up" : edge <= -0.08 ? "nrs-down" : "";
            return "<tr><td>" + STAT_NAME[s] + '</td><td class="' + cls + '">' + (a != null ? fmtProj(a, s) : "—") + "</td>" +
                   "<td>" + (l != null ? fmtProj(l, s) : "—") + "</td>" +
                   '<td class="' + cls + '">' + (edge == null ? "—" : (edge >= 0 ? "+" : "−") + Math.abs(Math.round(edge * 100)) + "%") + "</td></tr>";
        }).join("");
        var v = matchupVerdict((SHEET.leaks || {})[p.opp] || {});
        var d = (SHEET.env || {})[p.opp] || {};
        return '<div class="nrs-pf-verdict"><span class="nrs-mx-verdict ' + v[1] + '">' + v[0] + "</span>" +
            "<span>for the " + esc(p.team) + " offense against " + esc(p.opp) + "</span></div>" +
            '<h4 class="nrs-pf-h">What ' + esc(p.opp) + " allows to " + esc(p.role) + "s, per game</h4>" +
            '<table class="nrs-bd-table nrs-pf-table"><thead><tr><th></th><th>' + esc(p.opp) + "</th><th>League</th><th>Diff</th></tr></thead>" +
            "<tbody>" + rows + "</tbody></table>" +
            '<div class="nrs-mx-chips nrs-pf-chips">' +
            (d.def_rz_td != null ? '<span class="nrs-mx-chip">' + esc(p.opp) + " lets <b>" + Math.round(d.def_rz_td) + "%</b> of red-zone trips score</span>" : "") +
            (d.def_man != null ? '<span class="nrs-mx-chip">' + esc(p.opp) + " man coverage <b>" + Math.round(d.def_man) + "%</b></span>" : "") +
            (d.def_pressure != null ? '<span class="nrs-mx-chip">' + esc(p.opp) + " pressure <b>" + Math.round(d.def_pressure) + "%</b></span>" : "") +
            "</div>";
    }

    function logHtml(p) {
        var stats = Object.keys(p.proj || {});
        var rows = (p.log || []).slice().reverse().map(function (g) {
            return "<tr><td>" + weekLabel(g) + "</td>" +
                '<td><span class="nrs-opp"><img src="' + TEAM_LOGO(g.opp) + '" alt="" loading="lazy" onerror="this.remove()">' + esc(g.opp) + "</span></td>" +
                "<td>" + esc(g.role || "—") + "</td>" +
                stats.map(function (s) { return "<td>" + (g[s] == null ? "—" : Math.round(g[s])) + "</td>"; }).join("") + "</tr>";
        }).join("");
        var avg = stats.map(function (s) { return "<td><b>" + fmtProj((p.window || {})[s], s) + "</b></td>"; }).join("");
        return '<h4 class="nrs-pf-h">Last ' + (p.log || []).length + " games</h4>" +
            '<table class="nrs-bd-table nrs-pf-table"><thead><tr><th>Wk</th><th>Opp</th><th>Role</th>' +
            stats.map(function (s) { return "<th>" + STAT_NAME[s] + "</th>"; }).join("") + "</tr></thead><tbody>" + rows + "</tbody>" +
            '<tfoot><tr><td colspan="3">Avg, last ' + p.games + "</td>" + avg + "</tr></tfoot></table>";
    }

    // ── the dialog, built once ──
    var dlg = document.createElement("dialog");
    dlg.className = "nrs-profile";
    dlg.id = "atdCard";
    dlg.setAttribute("aria-labelledby", "atdCardName");
    dlg.innerHTML =
        '<div class="nrs-profile__inner">' +
          '<header class="nrs-profile__head">' +
            '<div class="nrs-profile__head-main">' +
              '<img class="nrs-profile__photo" id="atdCardPhoto" alt="" hidden>' +
              '<div><h2 class="nrs-profile__name" id="atdCardName"></h2><p class="nrs-profile__sub" id="atdCardSub"></p></div>' +
            "</div>" +
            '<div class="nrs-profile__head-right">' +
              '<button type="button" class="nrs-profile__close" id="atdCardClose" aria-label="Close">&times;</button>' +
              '<p class="nrs-profile__game" id="atdCardGame"></p>' +
            "</div>" +
          "</header>" +
          '<div class="nrs-profile__body" id="atdCardBody"></div>' +
          '<footer class="nrs-profile__foot">' +
            '<a class="nrs-profile__board nrs-profile__board--quiet" id="atdCardBoard" href="#">Game Board</a>' +
            '<a class="nrs-profile__board" id="atdCardLogs" href="#">Full player logs &rarr;</a>' +
          "</footer>" +
        "</div>";
    document.body.appendChild(dlg);
    var $ = function (id) { return document.getElementById(id); };

    function open(p) {
        var play = PLAY[p.player_id];
        var pl = play && play.pl, g = play && play.game;
        var photo = $("atdCardPhoto");
        if (p.headshot) { photo.src = thumb(p.headshot); photo.hidden = false; } else { photo.hidden = true; }

        var status = { q: "Q", d: "D", out: "Out" }[pl && pl.st];
        $("atdCardName").innerHTML = esc(p.name) + '<span class="nrs-depth-badge">' + esc(p.role) + "</span>" +
            (status ? '<span class="nrs-bb nrs-bb--inj" title="' + esc((pl.stl || "") + (pl.inj ? " — " + pl.inj : "")) + '">' + status + "</span>" : "") +
            (p.low_volume ? '<span class="nrs-bb nrs-bb--low">Low vol</span>' : "") +
            (p.new_team ? '<span class="nrs-bb nrs-bb--new">New team</span>' : "");
        $("atdCardSub").textContent = p.no_history
            ? p.team + " · on the depth chart, no games yet"
            : p.team + " · " + p.games + (p.games === 1 ? " game" : " games") + " in the sample" +
              (p.seasons && p.seasons.length > 1 ? " · " + seasonSpan(p.seasons) : "");
        $("atdCardGame").textContent = g ? g.away + " @ " + g.home + "\n" + fmtKick(g.kick) : "";

        var body = $("atdCardBody");
        if (p.no_history || !(p.log || []).length) {
            body.innerHTML = '<p class="nrs-empty">No games to build a read from yet — he is ' + esc(p.role) + " on the current depth chart.</p>";
        } else {
            var tabs = [["read", "The Read"], ["matchup", "Matchup"], ["log", "Last games"]];
            body.innerHTML = heroHtml(p, play) +
                '<nav class="nrs-pf-tabs" role="tablist" aria-label="Player detail">' +
                tabs.map(function (t, i) {
                    return '<button type="button" role="tab" data-pftab="' + t[0] + '" aria-selected="' + (i === 0) + '"' +
                           (i === 0 ? ' class="is-active"' : "") + ">" + t[1] + "</button>";
                }).join("") + "</nav>" +
                '<section class="nrs-pf-panel is-active" data-pfpanel="read">' + readHtml(p) + "</section>" +
                '<section class="nrs-pf-panel" data-pfpanel="matchup">' + matchupHtml(p) + "</section>" +
                '<section class="nrs-pf-panel" data-pfpanel="log">' + logHtml(p) + "</section>";
        }
        if (pl && pl.st && pl.inj) body.insertAdjacentHTML("afterbegin", '<p class="atd-card-inj">' + esc(pl.inj) + "</p>");
        if (pl && pl.m && pl.m.small && !p.no_history) {
            body.insertAdjacentHTML("afterbegin", '<p class="atd-card-inj">Only ' + p.games + " NFL game" + (p.games === 1 ? "" : "s") +
                " of data — read these numbers as a placeholder, not a rating.</p>");
        }
        $("atdCardLogs").href = linkFor(p, "logs");
        $("atdCardBoard").href = linkFor(p, "board");
        if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
    }

    function close() {
        if (typeof dlg.close === "function") dlg.close(); else dlg.removeAttribute("open");
    }

    $("atdCardClose").addEventListener("click", close);
    dlg.addEventListener("click", function (ev) {
        if (ev.target === dlg) { close(); return; }   // the dimmed backdrop
        var tab = ev.target.closest("[data-pftab]");
        if (!tab) return;
        Array.prototype.forEach.call(dlg.querySelectorAll("[data-pftab]"), function (b) {
            var on = b === tab;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-selected", String(on));
        });
        Array.prototype.forEach.call(dlg.querySelectorAll("[data-pfpanel]"), function (s) {
            s.classList.toggle("is-active", s.dataset.pfpanel === tab.dataset.pftab);
        });
    });
    document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape" && dlg.open) { ev.preventDefault(); close(); }
    });

    // names on the board and in the top five open the card; a modified click keeps the link
    document.addEventListener("click", function (ev) {
        var a = ev.target.closest("a[data-pid]");
        if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
        var p = SHEET.cards[a.getAttribute("data-pid")];
        if (!p) return;
        ev.preventDefault();
        open(p);
    });
})();
