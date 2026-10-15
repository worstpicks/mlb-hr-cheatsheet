/*
 * Worst Pickz Lines -- the moneyline / puck line (spread) tab.
 *
 * Both teams' recent games side by side. Every game is graded against TONIGHT's
 * number -- the puck line or spread each team carries tonight, or tonight's
 * total -- so the hit rate under each team answers "how often would that line
 * have cashed?". Margin reads the way a spread does: -17 is a 17-point win.
 *
 * Results:  preview/data/results-<sport>.json  (final scores + DraftKings'
 *           closing lines from ESPN, a rolling log the daily run extends)
 * Tonight:  preview/data/lines-<sport>.json    (The Rundown, pulled once a day)
 * Both are written by research_lines.py. Pages call WPLines.render() inside
 * their own view tabs (NFL) or let WPLines.mount() add a tab row (NHL, NBA).
 */
(function () {
    "use strict";

    var cache = {};
    var LABELS = {
        nhl: { tab: "Moneyline & Puck Line", line: "Puck line" },
        nfl: { tab: "Moneyline & Spread", line: "Spread" },
        nba: { tab: "Moneyline & Spread", line: "Spread" }
    };
    // shared by both sides, and kept while you move between games
    var view = { market: "spread", ou: "over", span: "l10", venue: "all", alt: {} };

    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }
    function price(p) { return p == null ? "" : (p > 0 ? "+" + p : String(p)); }
    function signed(v) { return v == null ? "—" : (v > 0 ? "+" + v : v < 0 ? "−" + Math.abs(v) : "0"); }
    function round1(v) { return Math.round(v * 10) / 10; }

    function logo(sport, abbr) {
        if (!abbr) return "";
        if (sport === "nhl") return "https://assets.nhle.com/logos/nhl/svg/" + abbr + "_light.svg";
        return "https://a.espncdn.com/i/teamlogos/" + sport + "/500/" + abbr.toLowerCase() + ".png";
    }

    function load(name) {
        if (!cache[name]) {
            var bust = Math.floor(Date.now() / 3600000);   // the files change once a day
            cache[name] = fetch("../data/" + name + ".json?h=" + bust)
                .then(function (r) { return r.ok ? r.json() : null; })
                .catch(function () { return null; });
        }
        return cache[name];
    }

    /* One team's games from its own side, oldest first -- only those played
       before the game being looked at, so a past date reads as it did then. */
    function teamGames(results, abbr, before) {
        return ((results && results.games) || []).filter(function (g) {
            return (g.away === abbr || g.home === abbr) && (!before || g.date < before);
        }).map(function (g) {
            var home = g.home === abbr, c = g.close || {};
            var us = home ? g.hs : g.as, them = home ? g.as : g.hs;
            return { date: g.date, opp: home ? g.away : g.home, home: home, us: us, them: them, extra: g.extra,
                     pre: g.type === 1, post: g.type === 3 || g.type === 5, margin: us - them, total: g.as + g.hs, line: c.total };
        });
    }

    /* The number each side is graded against tonight. */
    function tonightLine(sport, tonight, side) {
        var b = (tonight && tonight.best) || {};
        if (view.market === "total") {
            var t = b.total;
            return t ? { value: t.line, price: view.ou === "over" ? t.over : t.under, book: view.ou === "over" ? t.over_book : t.under_book }
                     : { value: null, missing: true };
        }
        if (view.market === "ml") {
            var m = b["ml_" + side];
            return { value: 0, price: m && m.price, book: m && m.book };
        }
        var s = b["spread_" + side];
        var alt = view.alt[side];
        if (sport === "nhl" && alt != null && (!s || alt !== s.line)) return { value: alt };
        if (s) return { value: s.line, price: s.price, book: s.book };
        return { value: sport === "nhl" ? (alt != null ? alt : -1.5) : 0, missing: true };
    }

    // 1 cashed, -1 missed, 0 push, against tonight's number
    function grade(g, line) {
        var x;
        if (view.market === "total") {
            var t = line.value != null ? line.value : g.line;
            if (t == null) return null;
            x = view.ou === "over" ? g.total - t : t - g.total;
        } else {
            x = g.margin + (line.value || 0);
        }
        return x > 0 ? 1 : x < 0 ? -1 : 0;
    }

    function panel(sport, team, side, opp, results, tonight, before) {
        var all = teamGames(results, team.abbr, before);
        var games = all.filter(function (g) {
            if (view.venue === "home") return g.home;
            if (view.venue === "away") return !g.home;
            if (view.venue === "vs") return g.opp === opp;
            return true;
        });
        if (view.span !== "all") games = games.slice(-Number(view.span.slice(1)));
        var line = tonightLine(sport, tonight, side);
        var isTotal = view.market === "total";
        var grades = games.map(function (g) { return grade(g, line); });

        var rows = games.map(function (g, i) {
            var d = new Date(g.date + "T12:00:00");
            var yr = d.getFullYear() !== new Date().getFullYear() ? " '" + String(d.getFullYear()).slice(2) : "";
            var r = grades[i];
            var heat = r === 1 ? "nrs-cell-heat--good" : r === -1 ? "nrs-cell-heat--bad" : "nrs-cell";
            var last = isTotal ? String(g.total) : signed(-g.margin);
            return "<tr>" +
                '<td class="nrs-log-week">' + d.toLocaleDateString([], { month: "short", day: "numeric" }) + yr +
                  (g.pre ? " <small>PRE</small>" : g.post ? " <small>PO</small>" : "") + "</td>" +
                '<td class="nrs-log-opp"><span class="wpl-opp">' + (g.home ? "vs" : "at") +
                  ' <img src="' + esc(logo(sport, g.opp)) + '" alt="" loading="lazy" onerror="this.remove()">' + esc(g.opp) + "</span></td>" +
                '<td class="wpl-c nrs-cell">' + (g.line == null ? "—" : g.line) + "</td>" +
                '<td class="wpl-c nrs-cell"><b class="' + (g.margin > 0 ? "wpl-w" : g.margin < 0 ? "wpl-l" : "") + '">' +
                  (g.margin > 0 ? "W" : g.margin < 0 ? "L" : "T") + "</b> " + g.us + "–" + g.them + (g.extra ? " <small>" + esc(g.extra) + "</small>" : "") + "</td>" +
                '<td class="wpl-c ' + heat + '">' + last + "</td>" +
                "</tr>";
        }).join("");

        var hits = grades.filter(function (r) { return r === 1; }).length;
        var graded = grades.filter(function (r) { return r === 1 || r === -1; }).length;
        var pushes = grades.filter(function (r) { return r === 0; }).length;
        var rate = graded ? Math.round(100 * hits / graded) : null;
        var lines = games.filter(function (g) { return g.line != null; });
        var avgOu = lines.length ? round1(lines.reduce(function (a, g) { return a + g.line; }, 0) / lines.length) : null;
        var avgLast = games.length ? round1(games.reduce(function (a, g) { return a + (isTotal ? g.total : -g.margin); }, 0) / games.length) : null;
        var avgHit = avgLast == null ? null : isTotal
            ? (line.value == null ? null : (view.ou === "over" ? avgLast > line.value : avgLast < line.value))
            : (-avgLast + (line.value || 0) > 0);
        var avgCls = avgHit == null ? "nrs-cell" : avgHit ? "nrs-cell-heat--good" : "nrs-cell-heat--bad";
        var rateCls = rate == null ? "" : rate >= 50 ? "wpl-rate--good" : "wpl-rate--bad";

        return '<section class="wpl-team wpl-team--' + side + '">' +
            '<header class="wpl-team__head">' +
              '<img src="' + esc(team.logo || logo(sport, team.abbr)) + '" alt="" loading="lazy" onerror="this.remove()">' +
              "<div><b>" + esc(team.abbr) + "</b>" + (team.name ? "<span>" + esc(team.name) + "</span>" : "") + "</div>" +
              '<span class="wpl-side">' + (side === "away" ? "Away" : "Home") + "</span>" +
            "</header>" +
            (games.length
                ? '<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log wpl-log"><thead><tr>' +
                  '<th>Date</th><th class="nrs-th-opp">Opponent</th><th title="That game\'s closing total">O/U</th><th>W/L</th>' +
                  "<th>" + (isTotal ? "Total" : "Margin") + "</th></tr></thead><tbody>" + rows + "</tbody>" +
                  '<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="2">Avg</td><td class="wpl-c nrs-cell">' + (avgOu == null ? "—" : avgOu) +
                  '</td><td class="nrs-cell"></td><td class="wpl-c ' + avgCls + '">' + (avgLast == null ? "—" : isTotal ? avgLast : signed(avgLast)) + "</td></tr></tfoot>" +
                  "</table></div>" +
                  '<div class="wpl-rate"><span class="wpl-k">Hit rate</span><b class="' + rateCls + '">' + (rate == null ? "—" : rate + "%") + "</b>" +
                  "<small>" + hits + "/" + graded + (pushes ? " · " + pushes + " push" + (pushes > 1 ? "es" : "") : "") + "</small></div>"
                : '<p class="nrs-empty">' + (all.length ? "No games match this filter." : "No finished games logged yet.") + "</p>") +
            lineChip(sport, side, line, before) +
            "</section>";
    }

    /* Tonight's number for this side, and on the puck line a -1.5 / +1.5 switch. */
    function lineChip(sport, side, line, before) {
        var labels = LABELS[sport] || LABELS.nfl;
        var what = view.market === "total" ? (view.ou === "over" ? "Over " : "Under ") + (line.value == null ? "—" : line.value)
            : view.market === "ml" ? "Moneyline"
            : labels.line + " " + (line.missing && sport !== "nhl" ? "—" : signed(line.value));
        var alt = "";
        if (sport === "nhl" && view.market === "spread") {
            alt = '<span class="nrs-log-filter wpl-alt">' + [-1.5, 1.5].map(function (v) {
                return '<button type="button" data-wpl-alt="' + side + '" data-wpl-v="' + v + '" class="' + (line.value === v ? "is-active" : "") + '">' + signed(v) + "</button>";
            }).join("") + "</span>";
        }
        var past = before && before < todayET();
        var note = line.missing
            ? (view.market === "total" ? "graded against each game's closing total"
               : (past ? "no line saved for this game" : "no line posted yet") + (sport === "nhl" ? "" : " · graded straight up"))
            : (line.book ? esc(line.book) : view.market === "spread" && sport === "nhl" ? "alt line" : "");
        return '<footer class="wpl-chip"><span class="wpl-k">' + (past ? "Line" : "Tonight") + "</span><b>" + esc(what) + "</b>" +
            (line.price != null ? "<em>" + price(line.price) + "</em>" : "") + (note ? "<small>" + note + "</small>" : "") + alt + "</footer>";
    }

    function todayET() {
        return new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });
    }

    function seg(name, options) {
        return '<div class="nrs-log-filter" role="group">' + options.map(function (o) {
            return '<button type="button" data-wpl-f="' + name + '" data-wpl-v="' + o[0] + '" class="' + (view[name] === o[0] ? "is-active" : "") + '">' + o[1] + "</button>";
        }).join("") + "</div>";
    }

    /* Draw one game: teams = {away: {abbr, name, logo}, home: {...}}; before =
       the game's Eastern date (YYYY-MM-DD), so the logs stop short of it. */
    function render(host, sport, gameId, teams, before) {
        teams = teams || { away: {}, home: {} };
        var labels = LABELS[sport] || LABELS.nfl;
        if (host.dataset.wplGame !== String(gameId)) view.alt = {};   // a new game starts on its own lines
        host.dataset.wplGame = String(gameId);
        if (!host.querySelector(".wpl")) host.innerHTML = '<p class="nrs-empty">Loading…</p>';
        return Promise.all([load("results-" + sport), load("lines-" + sport)]).then(function (got) {
            var results = got[0], lines = got[1];
            var tonight = lines && lines.games && lines.games[String(gameId)];
            var since = (results && results.games && results.games.length)
                ? new Date(results.games[0].date + "T12:00:00").toLocaleDateString([], { month: "short", day: "numeric" }) : "";
            host.innerHTML = '<div class="wpl">' +
                '<div class="wpl-controls">' +
                  seg("market", [["spread", labels.line], ["ml", "Moneyline"], ["total", "Total"]]) +
                  (view.market === "total" ? seg("ou", [["over", "Over"], ["under", "Under"]]) : "") +
                  seg("span", [["l5", "L5"], ["l10", "L10"], ["all", "All"]]) +
                  seg("venue", [["all", "Both"], ["home", "Home"], ["away", "Away"], ["vs", "H2H"]]) +
                "</div>" +
                '<div class="nrs-bt-grid wpl-grid">' +
                  panel(sport, teams.away, "away", teams.home.abbr, results, tonight, before) +
                  panel(sport, teams.home, "home", teams.away.abbr, results, tonight, before) +
                "</div>" +
                '<p class="wpl-asof">Every game is graded against <b>tonight\'s</b> number, so the hit rate is how often that line would have cashed. ' +
                "Margin reads like a spread: −3 is a three-" + (sport === "nhl" ? "goal" : "point") + " win, +2 a two-" + (sport === "nhl" ? "goal" : "point") + " loss" +
                (sport === "nhl" ? " (shootout goals count, as books settle the puck line)" : "") + ". " +
                "O/U is that game's closing total. Scores and closing lines from ESPN" + (since ? ", logged since " + since : "") +
                "; tonight's lines from The Rundown. The log grows a day at a time.</p>" +
                "</div>";
            host.querySelectorAll("[data-wpl-f]").forEach(function (b) {
                b.addEventListener("click", function () {
                    view[b.dataset.wplF] = b.dataset.wplV;
                    render(host, sport, gameId, teams, before);
                });
            });
            host.querySelectorAll("[data-wpl-alt]").forEach(function (b) {
                b.addEventListener("click", function () {
                    view.alt[b.dataset.wplAlt] = Number(b.dataset.wplV);
                    render(host, sport, gameId, teams, before);
                });
            });
        });
    }

    /*
     * For pages without a view-tab row: add "Player research | Lines" above the
     * per-game research and swap between them for whichever game pill is active.
     * cfg: {sport, games: "#nrsGames", research: "#nrsMatchupSection", date: "#nrsDate", researchLabel}
     */
    function mount(cfg) {
        var games = document.querySelector(cfg.games);
        var research = document.querySelector(cfg.research);
        if (!games || !research) return;
        var labels = LABELS[cfg.sport] || LABELS.nfl;
        var tabs = document.createElement("div");
        tabs.className = "nrs-viewtabs wpl-tabs";
        tabs.setAttribute("role", "tablist");
        tabs.setAttribute("aria-label", "Game view");
        tabs.hidden = true;
        tabs.innerHTML = '<button type="button" data-wpl-view="research" class="is-active">' + esc(cfg.researchLabel || "Player Logs") + "</button>" +
            '<button type="button" data-wpl-view="lines">' + esc(labels.tab) + "</button>";
        var section = document.createElement("section");
        section.className = "nrs-section wpl-section";
        section.hidden = true;
        research.parentNode.insertBefore(tabs, research);
        research.parentNode.insertBefore(section, research);
        var mode = "research";
        var drawn = "";

        function active() { return games.querySelector("[data-game].is-active"); }
        function sync() {
            var pill = active();
            tabs.hidden = !pill;
            tabs.querySelectorAll("[data-wpl-view]").forEach(function (b) { b.classList.toggle("is-active", b.dataset.wplView === mode); });
            var showLines = !!pill && mode === "lines";
            research.classList.toggle("wpl-hide", showLines);
            section.hidden = !showLines;
            if (!showLines) { drawn = ""; return; }
            var dateEl = cfg.date && document.querySelector(cfg.date);
            var day = (dateEl && dateEl.value) || "";
            var id = pill.dataset.game;
            if (id + day === drawn) return;
            drawn = id + day;
            var logos = pill.querySelectorAll("img");
            var abbrs = (pill.textContent || "").match(/([A-Z]{2,4})\s*@\s*([A-Z]{2,4})/);
            render(section, cfg.sport, id, {
                away: { abbr: abbrs && abbrs[1], logo: logos[0] && logos[0].src },
                home: { abbr: abbrs && abbrs[2], logo: logos[1] && logos[1].src }
            }, day);
        }
        tabs.addEventListener("click", function (ev) {
            var b = ev.target.closest("[data-wpl-view]");
            if (!b) return;
            mode = b.dataset.wplView;
            drawn = "";
            sync();
        });
        // the page re-renders its pills on every date and game change
        new MutationObserver(function () { sync(); }).observe(games, { subtree: true, childList: true, attributes: true, attributeFilter: ["class"] });
        sync();
    }

    window.WPLines = { render: render, mount: mount, load: load };
})();
