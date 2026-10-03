/* Worst Pickz — player card popup on the NHL cheat sheet.
 * The NHL twin of the football sheet's atd-card.js: tapping a name opens a card
 * with his rating, goal chance, the five components that built the rating, the
 * lane he is attacking and the goalie in it, and his last ten games -- without
 * leaving the sheet. Everything it shows rides in the page (atgs_sheet.py writes
 * it onto each play), so nothing is fetched.
 *
 * The name stays a real link to him in the Research tab, so a new tab, a middle
 * click, or a sheet built before the cards existed still gets somewhere useful.
 * The dialog itself is atd-card.css, shared with the football sheet, so the two
 * cards cannot drift apart.
 */
(function () {
    "use strict";

    var SHEET = window.ATGS_SHEET;
    if (!SHEET || !SHEET.by_id) return;
    var ROOT = SHEET.root || "";
    var BY_ID = SHEET.by_id;
    var WEIGHTS = SHEET.weights || { volume: 20, quality: 20, defense: 20, goalie: 15, form: 15 };
    var BAND_LABEL = { elite: "Elite Target", strong: "Strong Target", playable: "Playable", thin: "Thin", dart: "Dart" };

    var esc = function (s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    };
    var LOGO = function (t) { return t ? "https://assets.nhle.com/logos/nhl/svg/" + t + "_light.svg" : ""; };
    var logoImg = function (t) {
        return t ? '<img src="' + LOGO(t) + '" alt="" loading="lazy" onerror="this.remove()">' : "";
    };
    // .893, not 0.893 -- how hockey writes a save percentage
    var pct3 = function (v) { return v ? v.toFixed(3).replace(/^0/, "") : "—"; };
    var num = function (v, d) { return v == null ? "—" : Number(v).toFixed(d == null ? 1 : d); };

    function seasonSpan(seasons) {
        var s = (seasons || []).filter(Boolean);
        var yy = function (id) { return "'" + String(id).slice(2, 4) + "–'" + String(id).slice(-2); };
        return !s.length ? "" : s.length > 1 ? yy(s[0]) + " → " + yy(s[s.length - 1]) : yy(s[0]);
    }
    function shortDate(iso) {
        if (!iso) return "—";
        var p = iso.split("-").map(Number);
        return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][p[1] - 1] + " " + p[2];
    }
    function puckDrop(iso) {
        var d = new Date(iso);
        return !iso || isNaN(d) ? "" : d.toLocaleString([], { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
    }
    function bandClass(band) {
        return { elite: "is-great", strong: "is-good", thin: "is-poor", dart: "is-bad" }[band] || "";
    }
    function laneClass(mult) {
        if (mult == null) return "";
        if (mult >= 1.12) return "is-soft";
        if (mult >= 1.04) return "is-soft-lite";
        if (mult <= 0.88) return "is-tough";
        if (mult <= 0.96) return "is-tough-lite";
        return "";
    }
    function signedPct(mult) {
        var p = Math.round((mult - 1) * 100);
        return p === 0 ? "even" : (p > 0 ? "+" : "−") + Math.abs(p) + "%";
    }

    // ── links into the Research tab: the game, or the game focused on him ──
    function researchLink(r, focus) {
        return ROOT + "index.html?date=" + encodeURIComponent(SHEET.date) +
               "&game=" + encodeURIComponent(r.game_id || "") +
               "&side=" + encodeURIComponent(r.side || "") +
               (focus ? "&player=" + encodeURIComponent(r.player_id || "") : "");
    }

    // ── the card's blocks ──
    function heroHtml(r) {
        var tile = function (label, value, sub, cls) {
            return '<div class="nrs-pf-tile' + (cls ? " " + cls : "") + '"><span class="nrs-pf-label">' + label + "</span>" +
                   '<span class="nrs-pf-value">' + value + "</span>" + (sub ? '<span class="nrs-pf-sub">' + sub + "</span>" : "") + "</div>";
        };
        var hit = r.hit || {};
        return '<div class="nrs-pf-hero">' +
            tile("Rating", Math.floor(r.score), esc(BAND_LABEL[r.band] || r.band_label || ""), "atgs-pf-ovr " + bandClass(r.band)) +
            tile(r.need ? r.need + "+ goal chance" : "Goal chance", r.small ? "—" : num(r.chance, 0) + "%",
                 r.small ? "too few games to rate" : (r.need ? "this bet needs " + r.need + " goals · " : "") +
                 "scored in " + (hit.g_1 == null ? "—" : hit.g_1 + "%") + " of his last " + r.games) +
            tile("Shots", num(r.sog, 1), "a game · 2+ in " + (hit.sog_2 == null ? "—" : hit.sog_2 + "%")) +
            (r.mult != null ? tile(esc(r.opp) + " vs " + esc(r.role) + "s", signedPct(r.mult),
                 "goals allowed vs an average club", laneClass(r.mult)) : "") +
            "</div>";
    }

    function readHtml(r) {
        var parts = r.parts || {};
        var rows = (r.reasons || []).map(function (x) {
            var got = parts[x.part], max = WEIGHTS[x.part] || 1;
            var share = got == null ? null : got / max;
            var cls = share == null ? "nrs-br-dim" : share >= 0.75 ? "nrs-up" : share <= 0.45 ? "nrs-down" : "";
            return '<li><span class="nrs-why-part">' + esc(x.label) + "</span>" +
                   '<span class="' + cls + '" title="' + (got == null ? "" : got + " of " + max + " points") + '">' +
                   (got == null ? "—" : Math.round(got) + "/" + max) + "</span>" +
                   '<span class="nrs-why-text">' + esc(x.text) + "</span></li>";
        }).join("");
        var hit = r.hit || {};
        var lines = [
            "Scored in <b>" + (hit.g_1 == null ? "—" : hit.g_1 + "%") + "</b> of his last " + r.games +
                " · a point in <b>" + (hit.pts_1 == null ? "—" : hit.pts_1 + "%") + "</b>",
            "<b>" + (hit.sog_2 == null ? "—" : hit.sog_2 + "%") + "</b> of games with 2+ shots · <b>" +
                (hit.sog_3 == null ? "—" : hit.sog_3 + "%") + "</b> with 3+ · <b>" +
                (hit.sog_4 == null ? "—" : hit.sog_4 + "%") + "</b> with 4+",
            "<b>" + num(r.g, 2) + "</b> goals · <b>" + num(r.a, 2) + "</b> assists · <b>" + num(r.pp_p, 2) +
                "</b> power-play points a game over his last " + r.games
        ];
        return '<h4 class="nrs-pf-h">Why a ' + Math.floor(r.score) + "</h4>" +
            '<ul class="nrs-why">' + (rows || "<li>No components available.</li>") + "</ul>" +
            '<ul class="nrs-bd-lines">' + lines.map(function (l) { return "<li>" + l + "</li>"; }).join("") + "</ul>" +
            (r.why ? '<p class="nrs-bd-proj">' + esc(r.why) + "</p>" : "");
    }

    function matchupHtml(r) {
        var slot = r.slot || {}, lg = r.lg_slot || {};
        var ROWS = [["g", "Goals", 2], ["sog", "Shots on goal", 1], ["iscf", "Scoring chances", 1], ["ihdcf", "High-danger chances", 1]];
        var body = ROWS.map(function (row) {
            var a = slot[row[0]], l = lg[row[0]];
            var edge = a != null && l ? (a - l) / l : null;
            var cls = edge == null ? "" : edge >= 0.08 ? "nrs-up" : edge <= -0.08 ? "nrs-down" : "";
            return "<tr><td>" + row[1] + '</td><td class="' + cls + '">' + num(a, row[2]) + "</td><td>" + num(l, row[2]) + "</td>" +
                   '<td class="' + cls + '">' + (edge == null ? "—" : (edge >= 0 ? "+" : "−") + Math.abs(Math.round(edge * 100)) + "%") + "</td></tr>";
        }).join("");
        var lane = r.mult == null ? ["No read", ""] : r.mult >= 1.08 ? ["Soft lane", "is-soft"] : r.mult <= 0.92 ? ["Tough lane", "is-tough"] : ["Even lane", ""];
        var goalie = r.g_name && !r.g_sv_pct
            ? '<h4 class="nrs-pf-h">In net: ' + esc(r.g_name) + "</h4>" +
              '<p class="atgs-pf-note">No NHL games in his sample, so the goalie component is scored as neutral.' +
              (r.g_note ? " Tonight\u2019s projected starter (" + esc(r.g_note) + ")." : "") + "</p>"
            : r.g_name
            ? '<h4 class="nrs-pf-h">In net: ' + esc(r.g_name) + "</h4>" +
              '<div class="nrs-mx-chips nrs-pf-chips">' +
                '<span class="nrs-mx-chip"><b>' + pct3(r.g_sv_raw || r.g_sv_pct) + "</b> save rate</span>" +
                '<span class="nrs-mx-chip"><b>' + pct3(r.g_hd_raw || r.g_hd_sv_pct) + "</b> on high-danger shots</span>" +
                '<span class="nrs-mx-chip"><b>' + num(r.g_ga_raw != null ? r.g_ga_raw : r.g_ga, 2) + "</b> goals against a game</span>" +
                '<span class="nrs-mx-chip"><b>' + num(r.g_sa, 1) + "</b> shots faced a game</span>" +
              "</div>" +
              (r.g_gp && r.g_gp < 10 ? '<p class="atgs-pf-note">Only ' + r.g_gp + " games in his sample, so the model reads him closer to league average (" +
                pct3(r.g_sv_pct) + ").</p>" : "") +
              (r.g_src === "lineup"
                ? '<p class="atgs-pf-note">Tonight\u2019s projected starter' + (r.g_note ? " (" + esc(r.g_note) + ")" : "") +
                  ", from the morning lineup reports. Teams confirm about an hour before puck drop.</p>"
                : '<p class="atgs-pf-note">The busiest goalie on the club by ice time. Starters are named about an hour before puck drop.</p>')
            : '<p class="atgs-pf-note">No goalie to read yet &mdash; the goalie component is scored as neutral.</p>';
        return '<div class="nrs-pf-verdict"><span class="nrs-mx-verdict ' + lane[1] + '">' + lane[0] + "</span>" +
            "<span>for " + esc(r.team) + " " + esc(r.role) + "s against " + esc(r.opp) + "</span></div>" +
            '<h4 class="nrs-pf-h">What ' + esc(r.opp) + " allows to " + esc(r.role) + "s, per game</h4>" +
            '<table class="nrs-bd-table nrs-pf-table"><thead><tr><th></th><th>' + esc(r.opp) + "</th><th>League</th><th>Diff</th></tr></thead>" +
            "<tbody>" + body + "</tbody></table>" + goalie;
    }

    function logHtml(r) {
        var log = (r.log10 || []).slice().reverse();          // newest first, like the NFL card
        if (!log.length) return '<p class="nrs-empty">No games in his log yet.</p>';
        var rows = log.map(function (g) {
            return "<tr><td>" + shortDate(g.d) + (g.pre ? ' <span class="atgs-pre">PRE</span>' : "") + "</td>" +
                '<td><span class="nrs-opp">' + (g.ha === "@" ? "@ " : "vs ") + logoImg(g.opp) + esc(g.opp) + "</span></td>" +
                // some preseason box scores never clocked ice time: "—", not "0:00"
                "<td>" + esc(/^0?0:00$/.test(g.toi || "") ? "—" : (g.toi || "—")) + "</td>" +
                '<td class="' + (g.g ? "nrs-up atgs-goal" : "") + '">' + g.g + "</td>" +
                "<td>" + g.a + "</td><td>" + g.sog + "</td><td>" + g.iscf + "</td></tr>";
        }).join("");
        var n = log.length;
        var sum = function (k) { return log.reduce(function (a, g) { return a + (g[k] || 0); }, 0); };
        var goals = log.filter(function (g) { return g.g; }).length;
        return '<h4 class="nrs-pf-h">Last ' + n + " games &middot; a goal in " + goals + "</h4>" +
            '<table class="nrs-bd-table nrs-pf-table"><thead><tr><th>Date</th><th>Opp</th><th>TOI</th><th>G</th><th>A</th><th>SOG</th><th>iSCF</th></tr></thead>' +
            "<tbody>" + rows + "</tbody>" +
            '<tfoot><tr><td colspan="3">Avg, last ' + n + "</td>" +
              "<td><b>" + (sum("g") / n).toFixed(2) + "</b></td><td><b>" + (sum("a") / n).toFixed(2) + "</b></td>" +
              "<td><b>" + (sum("sog") / n).toFixed(1) + "</b></td><td><b>" + (sum("iscf") / n).toFixed(1) + "</b></td></tr></tfoot></table>" +
            '<p class="atgs-pf-note">The rating reads his last ' + r.games + " games; this is the most recent stretch of them.</p>";
    }

    // ── the dialog, built once ──
    var dlg = document.createElement("dialog");
    dlg.className = "nrs-profile atgs-card";
    dlg.id = "atgsCard";
    dlg.setAttribute("aria-labelledby", "atgsCardName");
    dlg.innerHTML =
        '<div class="nrs-profile__inner">' +
          '<header class="nrs-profile__head">' +
            '<div class="nrs-profile__head-main">' +
              '<img class="nrs-profile__photo" id="atgsCardPhoto" alt="" hidden>' +
              '<div><h2 class="nrs-profile__name" id="atgsCardName"></h2><p class="nrs-profile__sub" id="atgsCardSub"></p></div>' +
            "</div>" +
            '<div class="nrs-profile__head-right">' +
              '<button type="button" class="nrs-profile__close" id="atgsCardClose" aria-label="Close">&times;</button>' +
              '<p class="nrs-profile__game" id="atgsCardGame"></p>' +
            "</div>" +
          "</header>" +
          '<div class="nrs-profile__body" id="atgsCardBody"></div>' +
          '<footer class="nrs-profile__foot">' +
            // a new tab, so the sheet stays right where the reader left it
            '<a class="nrs-profile__board nrs-profile__board--quiet" id="atgsCardGameLink" href="#" target="_blank" rel="noopener">Game in Research &#8599;</a>' +
            '<a class="nrs-profile__board" id="atgsCardLogs" href="#" target="_blank" rel="noopener">Full log in Research &#8599;</a>' +
          "</footer>" +
        "</div>";
    document.body.appendChild(dlg);
    var $ = function (id) { return document.getElementById(id); };

    function open(r) {
        var photo = $("atgsCardPhoto");
        if (r.headshot) {
            photo.src = r.headshot;
            photo.hidden = false;
            photo.onerror = function () { photo.hidden = true; };
        } else {
            photo.hidden = true;
        }
        $("atgsCardName").innerHTML = esc(r.name) +
            '<span class="nrs-depth-badge atgs-pos atgs-pos--' + esc(String(r.pos || "").slice(0, 1)) + '">' + esc(r.role) + "</span>" +
            '<span class="sheet-ovr sheet-ovr--' + esc(r.band) + ' sheet-ovr--sm atgs-card-ovr"><b>' + Math.floor(r.score) + "</b></span>" +
            (r.small ? '<span class="nrs-bb nrs-bb--low">Small sample</span>' : "");
        $("atgsCardSub").textContent = r.team + " · " + r.games + (r.games === 1 ? " game" : " games") +
            " in the sample" + (r.seasons && r.seasons.length ? " · " + seasonSpan(r.seasons) : "") +
            (r.market ? " · " + r.market : "");
        var game = (SHEET.games || []).filter(function (g) { return g.away + "@" + g.home === r.game; })[0];
        $("atgsCardGame").textContent = game ? game.away + " @ " + game.home + "\n" + puckDrop(game.kick) : "";

        var tabs = [["read", "The Read"], ["matchup", "Matchup"], ["log", "Last games"]];
        $("atgsCardBody").innerHTML =
            (r.doubt_note ? '<p class="atd-card-inj">' + esc(r.doubt_note) + "</p>" : "") +
            (r.small ? '<p class="atd-card-inj">Only ' + r.games + " game" + (r.games === 1 ? "" : "s") +
                " of data &mdash; read these numbers as a placeholder, not a rating.</p>" : "") +
            heroHtml(r) +
            '<nav class="nrs-pf-tabs" role="tablist" aria-label="Player detail">' +
            tabs.map(function (t, i) {
                return '<button type="button" role="tab" data-pftab="' + t[0] + '" aria-selected="' + (i === 0) + '"' +
                       (i === 0 ? ' class="is-active"' : "") + ">" + t[1] + "</button>";
            }).join("") + "</nav>" +
            '<section class="nrs-pf-panel is-active" data-pfpanel="read">' + readHtml(r) + "</section>" +
            '<section class="nrs-pf-panel" data-pfpanel="matchup">' + matchupHtml(r) + "</section>" +
            '<section class="nrs-pf-panel" data-pfpanel="log">' + logHtml(r) + "</section>";
        $("atgsCardLogs").href = researchLink(r, true);
        $("atgsCardGameLink").href = researchLink(r, false);
        if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
    }

    function close() {
        if (typeof dlg.close === "function") dlg.close(); else dlg.removeAttribute("open");
    }

    $("atgsCardClose").addEventListener("click", close);
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

    // Names on the board, the top five and the scorers open the card.
    document.addEventListener("click", function (ev) {
        var name = ev.target.closest("[data-pid]");
        if (!name || dlg.contains(name)) return;
        var r = BY_ID[name.getAttribute("data-pid")];
        if (r) open(r);
    });
})();
