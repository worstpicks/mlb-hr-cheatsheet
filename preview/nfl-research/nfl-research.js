/* Worst Pickz — NFL Matchup Research (BETA)
 * Offense (left) vs what the defense allows (right), Doink-style.
 * Data: pre-built JSON from fetch-nfl-research-slate.py (nflverse + ESPN, free).
 */
(function () {
    "use strict";

    const DEFAULT_SEASON = 2026;
    // The Tuesday before each season's Week 1 kickoff. NFL weeks turn over on Tuesdays,
    // so the page opens on the week being played rather than on Week 1 all season.
    const WEEK1_TUESDAY = { 2026: Date.UTC(2026, 8, 8, 12) };
    function currentWeek(season) {
        const start = WEEK1_TUESDAY[season];
        if (!start) return 1;
        return Math.min(18, Math.max(1, Math.floor((Date.now() - start) / (7 * 86400000)) + 1));
    }
    const SEASONS = [2026, 2025];
    const MAX_WEEK = 18;
    const POSITIONS = ["QB", "RB", "WR", "TE"];

    /* Columns per position, in table order. The settings panel lists them by group.
       Every column has a short header (`abbr`) and a full name for the settings panel;
       `on` is what a first visit shows -- the lean default Doink ships for receivers:
       TD, share, targets, receptions, yards, longest reception. Everything else is one
       switch away.

       All of it is free data: nflverse weekly stats, play-by-play (red zone, goal line,
       big plays, longest plays), and Pro Football Reference snap counts. Drops, yards
       after contact and routes come from paid charting and are left out, not faked.

       fmt: "pct" percent · "spread" signed line · "flag" 1/0 per game, a rate on average
       heat: false leaves a column uncoloured, for context that is not better or worse
       div: [a, b] is a / b (x100 for pct) and sum: [...] adds keys. Both are worked out
            from the stored counts, so an average is total over total, not a mean of
            game-by-game ratios. */
    const col = (key, abbr, name, group, extra) => Object.assign({ key, abbr, name, group, on: false }, extra);
    const G = {
        game: "Game", score: "Scoring", pass: "Passing", rush: "Rushing", recv: "Receiving",
        rz: "Red zone & goal line", combo: "Combos & fantasy",
    };
    const SPREAD = col("spread", "SPREAD", "Team spread", G.game, { fmt: "spread", heat: false });
    const SNAP_PCT = col("snap_pct", "SNAP%", "Snap share", G.game, { fmt: "pct" });
    const SNAPS = col("snaps", "SNAPS", "Offensive snaps", G.game);
    const TD = col("td", "TD", "Touchdowns scored", G.score, { on: true });
    const FIRST_TD = col("first_td", "1ST TD", "First touchdown of the game", G.score, { fmt: "flag" });
    const LAST_TD = col("last_td", "LAST TD", "Last touchdown of the game", G.score, { fmt: "flag" });
    const FUM = col("fum_lost", "FUM", "Fumbles lost", G.combo, { lowerBetter: true });
    const FPTS_HALF = col("fpts_half", "FPTS ½", "Fantasy points (half PPR)", G.combo);
    const FPTS_PPR = col("fpts_ppr", "FPTS PPR", "Fantasy points (PPR)", G.combo);
    const RZ_TD = col("rz_td", "RZ TD", "Red zone touchdowns", G.rz);

    const POS_COLUMNS = {
        QB: [
            SPREAD, SNAP_PCT,
            col("pass_yds", "PASS YDS", "Passing yards", G.pass, { on: true }),
            col("pass_td", "PASS TD", "Passing touchdowns", G.pass, { on: true }),
            col("pass_att", "ATT", "Pass attempts", G.pass, { on: true }),
            col("pass_cmp", "CMP", "Completions", G.pass, { on: true }),
            col("cmp_pct", "CMP%", "Completion %", G.pass, { fmt: "pct", div: ["pass_cmp", "pass_att"] }),
            col("ypa", "YPA", "Yards per attempt", G.pass, { div: ["pass_yds", "pass_att"] }),
            col("pass_int", "INT", "Interceptions", G.pass, { on: true, lowerBetter: true }),
            col("sacks", "SACKS", "Sacks taken", G.pass, { lowerBetter: true }),
            col("long_pass", "LNG CMP", "Longest completion", G.pass),
            col("pass_20", "20+ CMP", "Completions of 20+ yards", G.pass),
            col("deep_att", "DEEP ATT", "Deep attempts (20+ air yards)", G.pass),
            col("qb_adot", "ADOT", "Average depth of throw", G.pass, { div: ["pass_air", "pass_att"] }),
            col("pass_1d", "PASS 1D", "Passing first downs", G.pass),
            col("rush_yds", "RUSH YDS", "Rushing yards", G.rush, { on: true }),
            // a QB's own score is its own market (and his anytime TD), so it shows by default
            col("rush_td", "RUSH TD", "Rushing touchdowns", G.rush, { on: true }),
            col("rush_att", "CAR", "Carries", G.rush),
            col("ypc", "YPC", "Yards per carry", G.rush, { div: ["rush_yds", "rush_att"] }),
            col("long_rush", "LNG RUSH", "Longest rush", G.rush),
            col("scrambles", "SCRAM", "Scrambles", G.rush),
            col("rush_1d", "RUSH 1D", "Rushing first downs", G.rush),
            col("rz_pass_att", "RZ ATT", "Red zone pass attempts", G.rz),
            col("rz_pass_td", "RZ PTD", "Red zone passing touchdowns", G.rz),
            col("rz_car", "RZ CAR", "Red zone carries", G.rz),
            col("i5_car", "GL CAR", "Goal-line carries (inside the 5)", G.rz),
            RZ_TD,
            FIRST_TD, LAST_TD,
            col("pass_rush_yds", "P+R YDS", "Pass + rush yards", G.combo, { sum: ["pass_yds", "rush_yds"] }),
            FPTS_HALF, FPTS_PPR, FUM,
        ],
        RB: [
            SPREAD, SNAP_PCT, SNAPS, TD, FIRST_TD, LAST_TD,
            col("rush_att", "CAR", "Carries", G.rush, { on: true }),
            col("rush_share", "CAR%", "Carry share", G.rush, { fmt: "pct" }),
            col("rush_yds", "RUSH YDS", "Rushing yards", G.rush, { on: true }),
            col("rush_td", "RUSH TD", "Rushing touchdowns", G.rush),
            col("ypc", "YPC", "Yards per carry", G.rush, { div: ["rush_yds", "rush_att"] }),
            col("long_rush", "LNG RUSH", "Longest rush", G.rush),
            col("rush_10", "10+ RUSH", "Runs of 10+ yards", G.rush),
            col("rush_1d", "RUSH 1D", "Rushing first downs", G.rush),
            col("tgt_share", "SHARE", "Target share", G.recv, { fmt: "pct" }),
            col("tgt", "TGT", "Targets", G.recv, { on: true }),
            col("rec", "REC", "Receptions", G.recv, { on: true }),
            col("rec_yds", "REC YDS", "Receiving yards", G.recv, { on: true }),
            col("long", "LONG", "Longest reception", G.recv),
            col("rec_td", "REC TD", "Receiving touchdowns", G.recv),
            col("catch_pct", "CATCH%", "Catch rate", G.recv, { fmt: "pct", div: ["rec", "tgt"] }),
            col("yac", "YAC", "Yards after catch", G.recv),
            col("rec_1d", "REC 1D", "Receiving first downs", G.recv),
            col("rz_car", "RZ CAR", "Red zone carries", G.rz),
            col("rz_car_share", "RZ CAR%", "Red zone carry share", G.rz, { fmt: "pct" }),
            col("i10_car", "I10 CAR", "Carries inside the 10", G.rz),
            col("i5_car", "GL CAR", "Goal-line carries (inside the 5)", G.rz),
            col("rz_tgt", "RZ TGT", "Red zone targets", G.rz),
            col("rz_share", "RZ TGT%", "Red zone target share", G.rz, { fmt: "pct" }),
            col("rz_rec", "RZ REC", "Red zone catches", G.rz),
            RZ_TD,
            col("rush_rec_yds", "R+R YDS", "Rush + receiving yards", G.combo, { sum: ["rush_yds", "rec_yds"] }),
            col("touches", "TOUCH", "Touches (carries + catches)", G.combo, { sum: ["rush_att", "rec"] }),
            FPTS_HALF, FPTS_PPR, FUM,
        ],
    };
    // Receivers and tight ends share one list, in Doink's order.
    POS_COLUMNS.WR = [
        SPREAD, SNAP_PCT, SNAPS, TD, FIRST_TD, LAST_TD,
        col("tgt_share", "SHARE", "Target share", G.recv, { on: true, fmt: "pct" }),
        col("tgt", "TGT", "Targets", G.recv, { on: true }),
        col("rec", "REC", "Receptions", G.recv, { on: true }),
        col("rec_yds", "YDS", "Receiving yards", G.recv, { on: true }),
        col("long", "LONG", "Longest reception", G.recv, { on: true }),
        col("rec_td", "REC TD", "Receiving touchdowns", G.recv),
        col("lng_td", "LNG TD", "Longest receiving touchdown", G.recv),
        col("catch_pct", "CATCH%", "Catch rate", G.recv, { fmt: "pct", div: ["rec", "tgt"] }),
        col("ypr", "YPR", "Yards per reception", G.recv, { div: ["rec_yds", "rec"] }),
        col("ypt", "YPT", "Yards per target", G.recv, { div: ["rec_yds", "tgt"] }),
        col("air_yds", "AIR YDS", "Air yards", G.recv),
        col("air_share", "AIR%", "Air yards share", G.recv, { fmt: "pct" }),
        col("adot", "ADOT", "Average depth of target", G.recv, { div: ["air_yds", "tgt"] }),
        col("yac", "YAC", "Yards after catch", G.recv),
        col("rec_1d", "REC 1D", "Receiving first downs", G.recv),
        col("rec_20", "20+ REC", "Catches of 20+ yards", G.recv),
        col("deep_tgt", "DEEP TGT", "Deep targets (20+ air yards)", G.recv),
        col("rz_tgt", "RZ TGT", "Red zone targets", G.rz),
        col("rz_share", "RZ TGT%", "Red zone target share", G.rz, { fmt: "pct" }),
        col("rz_rec", "RZ REC", "Red zone catches", G.rz),
        col("i10_tgt", "I10 TGT", "Targets inside the 10", G.rz),
        RZ_TD,
        col("rush_att", "CAR", "Carries", G.rush),
        col("rush_yds", "RUSH YDS", "Rushing yards", G.rush),
        col("rush_rec_yds", "R+R YDS", "Rush + receiving yards", G.combo, { sum: ["rush_yds", "rec_yds"] }),
        FPTS_HALF, FPTS_PPR, FUM,
    ];
    POS_COLUMNS.TE = POS_COLUMNS.WR;

    // the order groups are listed in the settings panel, per position
    const GROUP_ORDER = {
        QB: [G.pass, G.rush, G.rz, G.score, G.combo, G.game],
        RB: [G.score, G.rush, G.recv, G.rz, G.combo, G.game],
        WR: [G.score, G.recv, G.rz, G.rush, G.combo, G.game],
        TE: [G.score, G.recv, G.rz, G.rush, G.combo, G.game],
    };

    // columns a sportsbook posts a line for, and so get a track control under them
    const MARKETS = new Set([
        "pass_yds", "pass_td", "pass_att", "pass_cmp", "pass_int", "long_pass", "sacks",
        "rush_att", "rush_yds", "rush_td", "long_rush",
        "tgt", "rec", "rec_yds", "rec_td", "long",
        "td", "first_td", "last_td", "pass_rush_yds", "rush_rec_yds", "fpts_half", "fpts_ppr",
    ]);

    /* One stat for one column out of a stats object: a game's log row (`log` true) or
       an average. Game logs are stored without their zeros, so a missing key there is
       a 0; in an average a missing key means the slate predates the column, and shows
       as a dash rather than a made-up zero. */
    function colVal(stats, c, log) {
        if (!stats) return null;
        const get = (k) => {
            const v = stats[k];
            if (v === undefined) return log && state.compactLogs ? 0 : null;
            return v;
        };
        if (c.sum) {
            let total = 0;
            for (const k of c.sum) {
                const v = get(k);
                if (v == null) return null;
                total += v;
            }
            return total;
        }
        if (c.div) {
            const top = get(c.div[0]), bottom = get(c.div[1]);
            if (top == null || !bottom) return null;
            return (top / bottom) * (c.fmt === "pct" ? 100 : 1);
        }
        return get(c.key);
    }

    // v2: the column set changed, and a v1 choice made from the old four columns
    // would otherwise hide every new default on a returning visitor's first load.
    const COLS_STORAGE_KEY = "worstpickz-nfl-cols.v2";

    /* Which columns the reader has switched on, per position. */
    function loadColPrefs() {
        let raw = {};
        try {
            const parsed = JSON.parse(localStorage.getItem(COLS_STORAGE_KEY) || "{}");
            if (parsed && typeof parsed === "object") raw = parsed;
        } catch (e) {}
        return adoptNewDefaults(raw);
    }

    /* A saved choice is a list of switched-on keys, so a column that ships later
       switched on would stay hidden for anyone who ever touched the settings. `_known`
       records every key that existed when the choice was saved: a default-on column
       missing from it is new, and joins the saved list once. Turning it off again
       sticks, because by then it is known. Choices saved before `_known` existed
       knew every current column except the QB rushing TD default. */
    const LEGACY_UNKNOWN = { QB: ["rush_td"] };
    function adoptNewDefaults(prefs) {
        const known = prefs._known || {};
        let changed = !prefs._known;
        POSITIONS.forEach((pos) => {
            const all = (POS_COLUMNS[pos] || []).map((c) => c.key);
            const seen = known[pos] || all.filter((k) => !(LEGACY_UNKNOWN[pos] || []).includes(k));
            if (Array.isArray(prefs[pos])) {
                const add = (POS_COLUMNS[pos] || []).filter((c) => c.on && !seen.includes(c.key) && !prefs[pos].includes(c.key));
                if (add.length) {
                    const keep = new Set([...prefs[pos], ...add.map((c) => c.key)]);
                    prefs[pos] = all.filter((k) => keep.has(k));
                    changed = true;
                }
            }
            if (!known[pos] || known[pos].length !== all.length) changed = true;
            known[pos] = all;
        });
        prefs._known = known;
        if (changed) saveColPrefs(prefs);
        return prefs;
    }

    function saveColPrefs(prefs) {
        try { localStorage.setItem(COLS_STORAGE_KEY, JSON.stringify(prefs)); } catch (e) {}
    }

    function defaultCols(pos) {
        return (POS_COLUMNS[pos] || []).filter((c) => c.on);
    }

    function visibleCols(pos) {
        const all = POS_COLUMNS[pos] || [];
        const pref = state.colPrefs[pos];
        if (!pref) return defaultCols(pos);
        const on = all.filter((c) => pref.indexOf(c.key) !== -1);
        // never let the picker empty a table out entirely
        return on.length ? on : defaultCols(pos);
    }

    // Doink-style line label per market (full words for the lines box)
    const LINE_LABELS = {
        pass_att: "Pass Att", pass_cmp: "Cmp", pass_yds: "Pass Yds", pass_td: "Pass TD", pass_int: "INT",
        // a QB's own rushing touchdown is a different market from a thrown one
        rush_att: "Rush Att", rush_yds: "Rush Yds", rush_td: "Rush TD",
        tgt: "Targets", rec: "Receptions", rec_yds: "Rec Yds", rec_td: "Rec TD",
        long_pass: "Longest Cmp", long_rush: "Longest Rush", long: "Longest Rec", sacks: "Sacks Taken",
        td: "Anytime TD", first_td: "First TD", last_td: "Last TD",
        pass_rush_yds: "Pass+Rush Yds", rush_rec_yds: "Rush+Rec Yds",
        fpts_half: "Fantasy (Half)", fpts_ppr: "Fantasy (PPR)",
    };

    const TEAM_LOGO = (abbr) =>
        abbr ? `https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/${abbr.toLowerCase()}.png` : "";

    // near-even band per stat so tiny gaps stay neutral instead of flashing color
    const THRESHOLDS = {
        pass_att: 1.5, pass_cmp: 1.0, pass_yds: 12, pass_td: 0.15, pass_int: 0.1,
        rush_att: 1.0, rush_yds: 5, rush_td: 0.1,
        rec_td: 0.1,
        tgt: 0.75, rec: 0.5, rec_yds: 5, rec_td: 0.1,
        td: 0.15, tgt_share: 3, air_yds: 10, yac: 5, long: 4, lng_td: 5,
        rz_tgt: 0.3, rz_share: 5, first_td: 0.1, last_td: 0.1,
        snap_pct: 5, snaps: 4, spread: 1, fum_lost: 0.1, fpts_half: 2, fpts_ppr: 2.2,
        cmp_pct: 4, ypa: 0.6, sacks: 0.5, long_pass: 5, pass_20: 0.6, deep_att: 0.8, qb_adot: 0.8, pass_1d: 1.5,
        ypc: 0.4, long_rush: 4, rush_10: 0.4, rush_1d: 0.6, scrambles: 0.5, rush_share: 5,
        catch_pct: 6, ypr: 1.2, ypt: 1, air_share: 4, adot: 1.2, rec_1d: 0.6, rec_20: 0.3, deep_tgt: 0.4,
        rz_car: 0.6, rz_car_share: 8, i10_car: 0.4, i5_car: 0.3, rz_rec: 0.3, i10_tgt: 0.25, rz_td: 0.15,
        rz_pass_att: 1, rz_pass_td: 0.2, pass_rush_yds: 12, rush_rec_yds: 7, touches: 1.2,
    };

    const state = {
        hostView: "logs",
        boardFilter: { pos: "All", team: "both", sort: "grade" },
        boardOpen: new Set(),
        colSetPos: "WR",
        season: DEFAULT_SEASON,
        week: currentWeek(DEFAULT_SEASON),
        autoWeek: true, // the week was picked by date, so a missing file may step back one
        slate: null,
        gameId: null,
        side: "away", // which team's offense is shown on the left
        leagueAvg: null, // per-position league average allowed (from slate defenses)
        // One log filter for every player panel and one for every defense panel on the
        // page: L5 on one card is L5 on all of them, so the lineup reads as one sample.
        // l5 | l10 | l15 | all | opp | home | away
        logFilter: { off: "l10", def: "l10" },
        compactLogs: false, // slate logs stored without zeros (built with the full column set)
        colPrefs: {}, // per-position visible stat columns (column picker)
        source: "reg", // "reg" = last full season, "pre" = this preseason
    };
    const DEFAULT_FILTER = "l10";

    const el = (id) => document.getElementById(id);

    // ── theme toggle (shared worstpickz-theme key) ──
    function initTheme() {
        const btn = el("nrsThemeToggle");
        const sync = () => {
            const light = document.documentElement.classList.contains("theme-light");
            btn.textContent = light ? "🌙" : "☀️";
            btn.setAttribute("aria-pressed", String(light));
        };
        btn.addEventListener("click", () => {
            const light = document.documentElement.classList.toggle("theme-light");
            try { localStorage.setItem("worstpickz-theme", light ? "light" : "dark"); } catch (e) {}
            sync();
        });
        sync();
    }



    /* Which stat block a game exposes. Preseason lives on parallel *_pre keys so
       switching source never rewrites the slate -- and falls back silently when
       a slate file predates the preseason build. */
    function usingPre() {
        return state.source === "pre" && state.slate && state.slate.has_preseason;
    }

    function offenseBlock(game, side) {
        const key = side === "away" ? "away_offense" : "home_offense";
        if (usingPre() && game[key + "_pre"]) return game[key + "_pre"];
        return game[key];
    }

    function defenseBlock(game, side) {
        const key = side === "away" ? "away_def_vs_pos" : "home_def_vs_pos";
        if (usingPre() && game[key + "_pre"]) return game[key + "_pre"];
        return game[key];
    }

    // ── stat source: last full season vs this preseason ──
    function initSourceToggle() {
        const wrap = el("nrsSrcToggle");
        if (!wrap) return;
        wrap.addEventListener("click", (ev) => {
            const btn = ev.target.closest("[data-src]");
            if (!btn) return;
            state.source = btn.dataset.src;
            syncSourceToggle();
            state.leagueAvg = computeLeagueAverages(state.slate ? state.slate.games : []);
            renderMatchup();
        });
    }

    function syncSourceToggle() {
        const wrap = el("nrsSrcToggle");
        const warn = el("nrsSrcWarn");
        if (!wrap) return;
        const available = !!(state.slate && state.slate.has_preseason);
        wrap.hidden = !available;
        if (!available && state.source === "pre") state.source = "reg";
        wrap.querySelectorAll("[data-src]").forEach((b) => {
            b.classList.toggle("is-active", b.dataset.src === state.source);
            // was hardcoded "2025 REG", which stayed wrong once 2026 games were in
            if (b.dataset.src === "reg" && state.slate) b.textContent = `${state.slate.stats_season} REG`;
            if (b.dataset.src === "pre" && state.slate) b.textContent = `${state.slate.season} PRE`;
        });
        if (warn) {
            const on = usingPre();
            warn.hidden = !on;
            if (on) {
                warn.innerHTML =
                    "<strong>Preseason sample.</strong> These are August snaps, and most of them belong "
                    + "to roster hopefuls rather than the players you are betting — a camp arm throwing "
                    + "22 passes is not evidence about the week-one starter. Recent, but thin. Switch back "
                    + `to ${state.slate ? state.slate.stats_season : ""} REG for a sample worth leaning on.`;
            }
        }
    }

    // ── Column Settings (cogwheel) ──
    // Laid out like Doink's panel: a position tab, a search, Select All / Reset, then
    // every column under its group, by full name with the header abbreviation beside
    // it and a switch. It opens from the cogwheel beside each log's Away filter (and
    // the one in the matchup bar), on the position of the card it was opened from.
    // One delegated listener on a panel built once: the old picker rebuilt its markup
    // on Reset and re-bound handlers onto the fresh copy, so a second Reset fired twice.
    function colSetListHtml(pos) {
        const on = new Set(visibleCols(pos).map((c) => c.key));
        const all = POS_COLUMNS[pos] || [];
        return (GROUP_ORDER[pos] || [])
            .map((group) => {
                const cols = all.filter((c) => c.group === group);
                if (!cols.length) return "";
                const allOn = cols.every((c) => on.has(c.key));
                const rows = cols
                    .map((c) => {
                        const checked = on.has(c.key);
                        return (
                            `<li class="nrs-colset__row" data-colsearch="${(c.name + " " + c.abbr + " " + group).toLowerCase()}">` +
                            `<span class="nrs-colset__name">${c.name} <abbr>(${c.abbr})</abbr></span>` +
                            `<label class="nrs-switch">` +
                            `<input type="checkbox" role="switch" data-colkey="${c.key}"${checked ? " checked" : ""} ` +
                            `aria-label="${c.name}">` +
                            `<span class="nrs-switch__track" aria-hidden="true"></span>` +
                            `</label></li>`
                        );
                    })
                    .join("");
                return (
                    `<li class="nrs-colset__group" data-colgroup-head="${group}">` +
                    `<span>${group}</span>` +
                    `<button type="button" data-colgroup="${group}">${allOn ? "None" : "All"}</button></li>` +
                    rows
                );
            })
            .join("");
    }

    function colSetHtml() {
        const tabs = POSITIONS
            .map((p) => `<button type="button" data-colpos="${p}"${p === state.colSetPos ? ' class="is-active"' : ""}>${p}</button>`)
            .join("");
        return (
            `<div class="nrs-colset" id="nrsColPick" role="dialog" aria-label="Column settings" hidden>` +
            `<header class="nrs-colset__head"><h3>Column Settings</h3>` +
            `<button type="button" class="nrs-colset__close" data-colclose aria-label="Close">&times;</button></header>` +
            `<div class="nrs-colset__pos" role="tablist" aria-label="Position">${tabs}</div>` +
            `<div class="nrs-colset__searchwrap"><input type="search" class="nrs-colset__search" id="nrsColSearch" ` +
            `placeholder="Search columns — red zone, snaps, yards…" aria-label="Search columns" autocomplete="off"></div>` +
            `<div class="nrs-colset__actions">` +
            `<button type="button" data-colall>Select All</button>` +
            `<button type="button" data-colreset>&#8634; Reset</button>` +
            `</div>` +
            `<p class="nrs-colset__note"><span id="nrsColCount"></span> · applies to every ${"<span id=\"nrsColPosName\"></span>"} log and defense table · saved on this device</p>` +
            `<ul class="nrs-colset__list" id="nrsColSetList"></ul>` +
            `</div>`
        );
    }

    // repositions the open panel against its cogwheel; set once the panel exists
    let placeColPanel = () => {};

    function setColPrefs(pos, keys) {
        state.colPrefs[pos] = (POS_COLUMNS[pos] || []).filter((c) => keys.has(c.key)).map((c) => c.key);
        saveColPrefs(state.colPrefs);
        renderKeeping(".nrs-colset-anchor");
    }

    /* Re-render without the page jumping. Toggling a column changes the height of
       the defense summary above the cards, and a filter changes every card's height,
       so the element the reader was working with is held where it sat on screen. */
    function renderKeeping(selector) {
        const before = selector ? document.querySelector(selector) : null;
        const top = before ? before.getBoundingClientRect().top : null;
        const id = before && (before.dataset.card || before.dataset.gearId);
        renderMatchup();
        if (top == null || !id) return;
        const after = document.querySelector(`[data-card="${id}"], [data-gear-id="${id}"]`);
        if (after) window.scrollBy(0, after.getBoundingClientRect().top - top);
    }

    function initColPicker() {
        document.body.insertAdjacentHTML("beforeend", colSetHtml());
        const panel = el("nrsColPick");
        const search = el("nrsColSearch");
        let anchor = null;      // the cogwheel it opened from
        let anchorId = null;    // how to find that cogwheel again after a re-render

        const applySearch = () => {
            const q = search.value.trim().toLowerCase();
            const list = el("nrsColSetList");
            list.querySelectorAll(".nrs-colset__row").forEach((row) => {
                row.hidden = !!q && !q.split(/\s+/).every((w) => row.dataset.colsearch.includes(w));
            });
            list.querySelectorAll(".nrs-colset__group").forEach((head) => {
                let n = head.nextElementSibling, any = false;
                while (n && n.classList.contains("nrs-colset__row")) { if (!n.hidden) any = true; n = n.nextElementSibling; }
                head.hidden = !any;
            });
        };
        const refreshList = () => {
            const pos = state.colSetPos;
            el("nrsColSetList").innerHTML = colSetListHtml(pos);
            el("nrsColCount").textContent = `${visibleCols(pos).length} of ${(POS_COLUMNS[pos] || []).length} on`;
            el("nrsColPosName").textContent = pos === "WR" || pos === "TE" ? "WR & TE" : pos;
            panel.querySelectorAll("[data-colpos]").forEach((b) => b.classList.toggle("is-active", b.dataset.colpos === pos));
            applySearch();
        };

        placeColPanel = () => {
            if (panel.hidden) return;
            if ((!anchor || !document.body.contains(anchor)) && anchorId) {
                anchor = document.querySelector(`[data-gear-id="${anchorId}"]`) || el("nrsColGear");
            }
            document.querySelectorAll(".nrs-colset-anchor").forEach((g) => g.classList.remove("nrs-colset-anchor"));
            if (anchor) {
                anchor.classList.add("nrs-colset-anchor");
                anchor.setAttribute("aria-expanded", "true");
            }
            const vw = document.documentElement.clientWidth, vh = window.innerHeight;
            const w = Math.min(360, vw - 24);
            panel.style.width = `${w}px`;
            const h = panel.offsetHeight;
            const r = anchor && anchor.getBoundingClientRect();
            // off screen (scrolled away, or a card that is gone): sit it top right
            if (!r || r.bottom < 0 || r.top > vh) {
                panel.style.left = `${Math.max(12, vw - w - 12)}px`;
                panel.style.top = "12px";
                return;
            }
            const left = Math.min(Math.max(12, r.right - w), vw - w - 12);
            let top = r.bottom + 8;
            if (top + h > vh - 12) top = r.top - h - 8 >= 12 ? r.top - h - 8 : Math.max(12, vh - h - 12);
            panel.style.left = `${left}px`;
            panel.style.top = `${top}px`;
        };

        const open = (gear) => {
            anchor = gear;
            anchorId = gear.dataset.gearId || null;
            if (gear.dataset.colgear) state.colSetPos = gear.dataset.colgear;
            search.value = "";
            refreshList();
            panel.hidden = false;
            placeColPanel();
        };
        const close = () => {
            panel.hidden = true;
            document.querySelectorAll(".nrs-colset-anchor").forEach((g) => {
                g.classList.remove("nrs-colset-anchor");
                g.setAttribute("aria-expanded", "false");
            });
            const back = anchor && document.body.contains(anchor) ? anchor : null;
            anchor = anchorId = null;
            return back;
        };

        document.addEventListener("click", (ev) => {
            const gear = ev.target.closest("[data-colgear], #nrsColGear");
            if (gear) {
                const same = !panel.hidden && (gear === anchor || (anchorId && gear.dataset.gearId === anchorId));
                if (same) close(); else open(gear);
                return;
            }
            // the path as dispatched: a group button the list just redrew is no longer
            // inside the panel by the time this runs, but the click still came from it
            if (!panel.hidden && !ev.composedPath().includes(panel)) close();
        });
        document.addEventListener("keydown", (ev) => {
            if (ev.key === "Escape" && !panel.hidden) {
                const back = close();
                if (back) back.focus();
            }
        });
        window.addEventListener("scroll", placeColPanel, { passive: true });
        window.addEventListener("resize", placeColPanel);
        search.addEventListener("input", applySearch);

        panel.addEventListener("click", (ev) => {
            const t = ev.target;
            if (t.closest("[data-colclose]")) { const back = close(); if (back) back.focus(); return; }
            const tab = t.closest("[data-colpos]");
            if (tab) {
                state.colSetPos = tab.dataset.colpos;
                refreshList();
                placeColPanel();
                return;
            }
            const pos = state.colSetPos;
            const all = POS_COLUMNS[pos] || [];
            const groupBtn = t.closest("[data-colgroup]");
            if (groupBtn) {
                const group = groupBtn.dataset.colgroup;
                const current = new Set(visibleCols(pos).map((c) => c.key));
                const inGroup = all.filter((c) => c.group === group).map((c) => c.key);
                const allOn = inGroup.every((k) => current.has(k));
                inGroup.forEach((k) => (allOn ? current.delete(k) : current.add(k)));
                if (!current.size) return; // keep at least one
                setColPrefs(pos, current);
                refreshList();
                placeColPanel();
            } else if (t.closest("[data-colall]")) {
                setColPrefs(pos, new Set(all.map((c) => c.key)));
                refreshList();
                placeColPanel();
            } else if (t.closest("[data-colreset]")) {
                delete state.colPrefs[pos];
                saveColPrefs(state.colPrefs);
                renderKeeping(".nrs-colset-anchor");
                refreshList();
                placeColPanel();
            }
        });

        panel.addEventListener("change", (ev) => {
            const box = ev.target.closest("[data-colkey]");
            if (!box) return;
            const pos = state.colSetPos;
            const all = POS_COLUMNS[pos] || [];
            const current = new Set(visibleCols(pos).map((c) => c.key));
            if (box.checked) current.add(box.dataset.colkey);
            else current.delete(box.dataset.colkey);
            if (!current.size) { box.checked = true; return; } // keep at least one
            setColPrefs(pos, current);
            // keep the list (and the reader's scroll inside it) as is; only the counts move
            el("nrsColCount").textContent = `${current.size} of ${all.length} on`;
            const group = (all.find((c) => c.key === box.dataset.colkey) || {}).group;
            const gb = panel.querySelector(`[data-colgroup="${group}"]`);
            if (gb) gb.textContent = all.filter((c) => c.group === group).every((c) => current.has(c.key)) ? "None" : "All";
            placeColPanel();
        });
    }

    // ── toolbar ──
    function initControls() {
        const seasonSel = el("nrsSeason");
        seasonSel.innerHTML = SEASONS.map((s) => `<option value="${s}">${s}</option>`).join("");
        seasonSel.value = String(state.season);
        seasonSel.addEventListener("change", () => {
            state.season = Number(seasonSel.value);
            loadSlate();
        });

        const weekSel = el("nrsWeek");
        weekSel.innerHTML = Array.from({ length: MAX_WEEK }, (_, i) => `<option value="${i + 1}">Week ${i + 1}</option>`).join("");
        weekSel.value = String(state.week);
        weekSel.addEventListener("change", () => {
            state.autoWeek = false;
            state.week = Number(weekSel.value);
            loadSlate();
        });

        el("nrsRefresh").addEventListener("click", () => loadSlate(true));

        // log filters (delegated: cards re-render on every matchup draw). The choice
        // covers its whole side of every card, and the card clicked stays where it was.
        el("nrsPosSections").addEventListener("click", (e) => {
            const btn = e.target.closest(".nrs-log-filter button[data-filter]");
            if (!btn) return;
            const kind = btn.closest(".nrs-log-filter").dataset.kind;
            if (!kind) return;
            state.logFilter[kind] = btn.dataset.filter;
            const card = btn.closest("[data-card]");
            renderKeeping(card ? `[data-card="${card.dataset.card}"]` : null);
        });

        el("nrsSideAway").addEventListener("click", () => setSide("away"));
        el("nrsSideHome").addEventListener("click", () => setSide("home"));
    }

    function setStatus(message) {
        const status = el("nrsStatus");
        if (!message) {
            status.hidden = true;
            status.textContent = "";
            return;
        }
        status.hidden = false;
        status.textContent = message;
    }

    // ── data ──
    async function loadSlate(bustCache) {
        const url = `../data/nfl-research-${state.season}-W${state.week}.json` + (bustCache ? `?t=${Date.now()}` : "");
        setStatus(`Loading ${state.season} week ${state.week}…`);
        el("nrsMatchupSection").hidden = true;
        el("nrsGames").innerHTML = "";
        try {
            const resp = await fetch(url, { cache: bustCache ? "no-store" : "default" });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            state.slate = await resp.json();
        } catch (err) {
            state.slate = null;
            // this week's file is not built yet: show the last one that is
            if (state.autoWeek && state.week > 1) {
                state.week -= 1;
                el("nrsWeek").value = String(state.week);
                return loadSlate(bustCache);
            }
            setStatus(
                `No slate data for ${state.season} week ${state.week}. ` +
                `Build it with: python fetch-nfl-research-slate.py --season ${state.season} --week ${state.week}`
            );
            el("nrsLastUpdated").textContent = "";
            el("nrsSourceBadge").hidden = true;
            return;
        }
        setStatus("");
        const badge = el("nrsSourceBadge");
        badge.hidden = false;
        const logSeasons = seasonSpan(state.slate.log_seasons || [state.slate.stats_season]);
        badge.textContent = `Stats: last 17 games · ${logSeasons} (nflverse)`;
        el("nrsLastUpdated").textContent = state.slate.fetched_at ? `Updated ${state.slate.fetched_at.replace("T", " ")}` : "";
        el("nrsSeasonNote").textContent =
            `Player averages over each player's last 17 games vs what each defense allowed per game — ` +
            `green means the player beats the defensive average.`;
        const propsHint = el("nrsPropsHint");
        if (state.slate.has_props) {
            propsHint.hidden = true;
        } else {
            propsHint.hidden = false;
            propsHint.textContent =
                "No player prop lines are posted for this week yet — books release them closer to kickoff. " +
                "Rebuild the slate then and the lines will appear under each stat automatically.";
        }

        const games = state.slate.games || [];
        if (!games.length) {
            setStatus("No games found for this week.");
            return;
        }
        if (!games.some((g) => g.id === state.gameId)) state.gameId = games[0].id;
        // slates built with the full column set carry fpts_ppr in every average and
        // store logs without zeros; older ones keep every key and lack the new columns
        state.compactLogs = games.some((g) => ["away_offense", "home_offense"].some((side) =>
            Object.values(g[side] || {}).some((list) => (list || []).some((p) => p.stats && "fpts_ppr" in p.stats))));
        state.leagueAvg = computeLeagueAverages(games);
        syncSourceToggle();
        if (window.NRSSheets) window.NRSSheets.onSlate(state.slate);
        const linked = applyDeepLink(games);
        renderGames();
        renderMatchup();
        if (linked) revealLinked(linked);
    }

    /* A link from the cheat sheet (?view=board&player=<gsis id>) lands on that
       player's game with the Game Board open and his row expanded. It applies once:
       picking another week or game afterwards behaves normally. */
    function applyDeepLink(games) {
        const link = state.deepLink;
        if (!link) return null;
        state.deepLink = null;
        if (link.view === "board" || link.view === "logs") state.hostView = link.view;
        if (!link.player) return null;
        const want = normName(link.player);
        for (const g of games) {
            const p = ((g.board && g.board.players) || []).find((b) =>
                b.player_id === link.player || normName(b.name) === want);
            if (!p) continue;
            state.gameId = g.id;
            state.side = p.team === g.away ? "away" : "home";
            state.boardFilter = { pos: "All", team: "both", sort: state.boardFilter.sort || "grade" };
            const key = `${p.team}|${p.role}|${p.player_id || normName(p.name)}`;
            if (state.hostView === "board") state.boardOpen.add(key);
            return key;
        }
        return null;
    }

    function revealLinked(key) {
        const toggle = document.querySelector(`[data-board-key="${key}"]`);
        const row = toggle && toggle.closest("tr");
        if (!row) return;
        row.classList.add("is-linked");
        // after layout settles, so the images above it do not push it off screen
        requestAnimationFrame(() => row.scrollIntoView({ block: "center" }));
    }

    // league average allowed per position/rank, from every defense on the slate
    function computeLeagueAverages(games) {
        const acc = {};
        const add = (bucket, stats) => {
            if (!stats) return;
            for (const [key, val] of Object.entries(stats)) {
                const slot = bucket[key] || (bucket[key] = { sum: 0, n: 0 });
                slot.sum += val;
                slot.n += 1;
            }
        };
        for (const game of games) {
            for (const side of ["away", "home"]) {
                const defense = defenseBlock(game, side) || {};
                for (const pos of POSITIONS) {
                    const block = defense[pos];
                    if (!block) continue;
                    const posAcc = acc[pos] || (acc[pos] = { overall: {}, ranks: {} });
                    add(posAcc.overall, block.overall);
                    for (const [rank, stats] of Object.entries(block.ranks || {})) {
                        add(posAcc.ranks[rank] || (posAcc.ranks[rank] = {}), stats);
                    }
                }
            }
        }
        const finalize = (bucket) => {
            const out = {};
            for (const [key, slot] of Object.entries(bucket)) {
                if (slot.n > 0) out[key] = slot.sum / slot.n;
            }
            return out;
        };
        const league = {};
        for (const [pos, posAcc] of Object.entries(acc)) {
            league[pos] = { overall: finalize(posAcc.overall), ranks: {} };
            for (const [rank, bucket] of Object.entries(posAcc.ranks)) {
                league[pos].ranks[rank] = finalize(bucket);
            }
        }
        return league;
    }

    function currentGame() {
        if (!state.slate) return null;
        return (state.slate.games || []).find((g) => g.id === state.gameId) || null;
    }

    // ── week slate chips ──
    function renderGames() {
        const wrap = el("nrsGames");
        wrap.innerHTML = "";
        for (const game of state.slate.games) {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "nrs-game-pill" + (game.id === state.gameId ? " is-active" : "");
            const kickoff = formatKickoff(game.kickoff);
            btn.innerHTML =
                `<span class="nrs-game-pill__teams">` +
                (game.away_logo ? `<img src="${game.away_logo}" alt="" loading="lazy">` : "") +
                `${game.away} @ ` +
                (game.home_logo ? `<img src="${game.home_logo}" alt="" loading="lazy">` : "") +
                `${game.home}</span>` +
                `<span class="nrs-game-pill__meta">${kickoff}</span>`;
            btn.addEventListener("click", () => {
                state.gameId = game.id;
                renderGames();
                renderMatchup();
            });
            wrap.appendChild(btn);
        }
    }

    function formatKickoff(iso) {
        if (!iso) return "";
        const date = new Date(iso);
        if (Number.isNaN(date.getTime())) return iso;
        const opts = { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" };
        if (date.getFullYear() !== new Date().getFullYear()) opts.year = "numeric";
        return date.toLocaleString([], opts);
    }

    function setSide(side) {
        state.side = side;
        renderMatchup();
    }

    // ── comparison heat: continuous shading, deeper color = bigger edge ──
    // returns an inline style attr (or "" when the value is basically even)
    function heatAttr(val, ref, col) {
        if (val == null || ref == null || (col && col.heat === false)) return "";
        const threshold = THRESHOLDS[col.key] != null ? THRESHOLDS[col.key] : 0.5;
        let edge = val - ref;
        if (col.lowerBetter) edge = -edge;
        if (Math.abs(edge) <= threshold * 0.5) return "";
        // full saturation at 6x threshold; sqrt ramp keeps mid edges visible
        const mag = Math.min(Math.abs(edge) / (threshold * 6), 1);
        const alpha = (0.14 + 0.56 * Math.sqrt(mag)).toFixed(2);
        const rgb = edge > 0 ? "34, 197, 94" : "239, 68, 68";
        return ` style="background:rgba(${rgb},${alpha})"`;
    }

    // `avg` is true on the average rows, where a first-TD flag becomes a rate
    /* NFL.com headshots are served full size through Cloudinary -- a 3400px, 3.3MB
       original for a 36px circle, so a seven-card lineup pulled about 23MB and the
       faces faded in one by one. A width transform returns the same image at 3KB.
       ESPN headshots have no such parameter and are already small, so they pass. */
    function thumb(url) {
        return String(url || "").replace("/image/upload/f_auto,q_auto/", "/image/upload/f_auto,q_auto,w_96/");
    }

    function fmtStat(val, col, avg) {
        if (val == null) return "—";
        const fmt = col && col.fmt;
        if (fmt === "pct") return `${Math.round(val)}%`;
        if (fmt === "spread") {
            if (val === 0) return "PK";
            return val > 0 ? `+${val}` : String(val);
        }
        if (fmt === "flag") {
            if (avg) return `${Math.round(val * 100)}%`;
            return val >= 1 ? "✓" : "–";
        }
        return Number.isInteger(val) ? String(val) : val.toFixed(1);
    }

    // "W2" for a game in the season being viewed, "W18 '25" for one from before it.
    // Logs span two seasons once one is underway, so each row says which it is.
    function weekLabel(g) {
        const season = g && g.season;
        if (!season || season === state.season) return `W${g.week}`;
        return `W${g.week} '${String(season).slice(-2)}`;
    }

    // "'25–'26" when a sample crosses seasons, "'26" when it does not
    function seasonSpan(seasons) {
        const s = (seasons || []).filter(Boolean);
        if (!s.length) return "";
        const yy = (y) => `'${String(y).slice(-2)}`;
        return s.length > 1 ? `${yy(s[0])}–${yy(s[s.length - 1])}` : yy(s[0]);
    }

    // ── matchup panels: all positions stacked, offense left | defense right ──
    // ── Game Board ───────────────────────────────────────────────────────────
    // One view per game that joins what the separate sheets each answered a part
    // of: the script (implied points, pace, lean), where each defense leaks by
    // role, and every lineup player's usage, matchup, projection, TD chance and
    // grade -- with the reasons one click away. Built by nfl_research/game_board.py.
    const BOARD_ROLES = ["QB1", "RB1", "RB2", "WR1", "WR2", "WR3", "TE1", "TE2"];
    const STAT_NAME = {
        pass_yds: "pass yds", pass_td: "pass TD", rush_yds: "rush yds",
        rec_yds: "rec yds", rec: "rec", tgt: "tgt",
    };
    const PART_LABEL = { matchup: "Matchup", script: "Game script", coverage: "Coverage", usage: "Usage", volume: "Volume" };

    function normName(n) {
        return String(n || "").toLowerCase().replace(/[.'’]/g, "")
            .replace(/\b(jr|sr|ii|iii|iv|v)\b/g, "").replace(/[^a-z ]/g, " ").replace(/\s+/g, " ").trim();
    }

    // latest injury designation per player, from the roster report on the slate
    function injuryIndex() {
        const out = {};
        const roster = (state.slate && state.slate.sheets && state.slate.sheets.roster) || {};
        Object.entries(roster).forEach(([team, r]) => {
            // `_sources` sits alongside the clubs and holds season numbers, not lists
            if (team.startsWith("_") || !r || !Array.isArray(r.injuries)) return;
            r.injuries.forEach((i) => {
                const st = String(i.status || "");
                const short = /^out$/i.test(st) ? "OUT" : /doubtful/i.test(st) ? "D"
                    : /questionable/i.test(st) ? "Q" : null;
                if (short) out[`${team}|${normName(i.name)}`] = { short, status: st, injury: i.injury };
            });
        });
        return out;
    }

    function gradeClass(g) {
        if (g == null) return "is-none";
        if (g >= 70) return "is-great";
        if (g >= 58) return "is-good";
        if (g >= 43) return "is-even";
        if (g >= 31) return "is-poor";
        return "is-bad";
    }

    // leak colour reads from the offense's side: soft defense green, stingy red
    function leakClass(index) {
        if (index == null) return "";
        if (index >= 1.12) return "is-soft";
        if (index >= 1.04) return "is-soft-lite";
        if (index <= 0.88) return "is-tough";
        if (index <= 0.96) return "is-tough-lite";
        return "";
    }

    const ord = (n) => {
        const s = ["th", "st", "nd", "rd"], v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    };

    function boardScriptHtml(game, board) {
        const imp = board.implied || {};
        const games = (state.slate.games || []).filter((g) => g.odds && g.odds.over_under != null);
        const totals = games.map((g) => g.odds.over_under).sort((a, b) => b - a);
        const total = game.odds && game.odds.over_under;
        const totalRank = total != null ? totals.indexOf(total) + 1 : null;
        const fav = imp[game.away] != null && imp[game.home] != null
            ? (imp[game.away] >= imp[game.home] ? game.away : game.home) : null;
        const w = game.weather;
        const weather = !w ? "" : w.indoor ? "Indoors"
            : `${Math.round(w.temp_f)}°F · wind ${Math.round(w.wind_mph)} mph${w.precip_pct >= 30 ? ` · ${w.precip_pct}% rain` : ""}`;

        const side = (team, logo) =>
            `<div class="nrs-bs-team"><img src="${logo || TEAM_LOGO(team)}" alt="" loading="lazy">` +
            `<div><span class="nrs-bs-abbr">${team}</span>` +
            `<span class="nrs-bs-imp">${imp[team] != null ? imp[team].toFixed(1) : "—"}<small> pts implied</small></span></div></div>`;

        let read = "";
        if (fav && total != null) {
            const gap = Math.abs(imp[game.away] - imp[game.home]);
            read = `${fav} ${gap >= 0.5 ? `implied ${gap.toFixed(1)} points higher` : "and its opponent implied level"}` +
                (totalRank ? ` in the ${totalRank === 1 ? "highest" : totalRank === totals.length ? "lowest" : ord(totalRank) + "-highest"} total on the slate.` : ".");
        }
        return (
            `<div class="nrs-bs">` +
            side(game.away, game.away_logo) +
            `<div class="nrs-bs-mid"><span class="nrs-bs-line">${game.odds && game.odds.details ? game.odds.details : "No line yet"}` +
            `${total != null ? ` · O/U ${total}` : ""}</span>` +
            `<span class="nrs-bs-meta">${formatKickoff(game.kickoff)}${weather ? ` · ${weather}` : ""}</span>` +
            (read ? `<span class="nrs-bs-read">${read}</span>` : "") +
            `</div>` +
            side(game.home, game.home_logo).replace("nrs-bs-team", "nrs-bs-team nrs-bs-team--home") +
            `</div>`
        );
    }

    // One panel per side of the ball: an offense against the defense it faces.
    // It leads with the conclusion -- where to attack, and who that helps -- and
    // keeps the evidence underneath, so the reader never has to decode a rank to
    // work out whether it is good news.
    const LEAK_GROUPS = [["QB", ["QB1"]], ["RB", ["RB1", "RB2"]], ["WR", ["WR1", "WR2", "WR3"]], ["TE", ["TE1", "TE2"]]];

    function leakTone(index) {
        if (index == null) return "is-na";
        const pct = (index - 1) * 100;
        if (pct >= 12) return "is-soft";
        if (pct >= 4) return "is-soft-lite";
        if (pct <= -12) return "is-tough";
        if (pct <= -4) return "is-tough-lite";
        return "is-even";
    }

    // "3rd softest" in the soft half of the table, "5th toughest" in the tough half
    const softness = (rank, of) => {
        const soft = of + 1 - rank;
        return soft <= of / 2 ? `${ord(soft)} softest` : `${ord(rank)} toughest`;
    };
    const signedPct = (index) => {
        const p = Math.round((index - 1) * 100);
        return p === 0 ? "even" : `${p > 0 ? "+" : "−"}${Math.abs(p)}%`;
    };
    // everything after the first name, so "Amon-Ra St. Brown" reads "St. Brown", not "Brown"
    const lastName = (n) => {
        const parts = String(n || "").replace(/\s+(Jr\.?|Sr\.?|II|III|IV|V)$/i, "").split(" ");
        return parts.length > 1 ? parts.slice(1).join(" ") : parts[0];
    };

    // pass roles carry the passing game; RB1 carries the run game
    function matchupVerdict(leaks) {
        const idx = (r) => (leaks[r] && leaks[r].index != null ? leaks[r].index : null);
        const pass = ["QB1", "WR1", "WR2", "TE1"].map(idx).filter((v) => v != null);
        const passIdx = pass.length ? pass.reduce((a, b) => a + b, 0) / pass.length : 1;
        const runIdx = idx("RB1") ?? 1;
        if (passIdx >= 1.05 && runIdx >= 1.05) return ["Soft all over", "is-soft"];
        if (passIdx >= 1.06 && passIdx >= runIdx + 0.04) return ["Attack through the air", "is-soft"];
        if (runIdx >= 1.06 && runIdx >= passIdx + 0.04) return ["Attack on the ground", "is-soft"];
        if (passIdx <= 0.94 && runIdx <= 0.97) return ["Tough all over", "is-tough"];
        if (passIdx <= 0.94) return ["Pass game stifled", "is-tough"];
        if (runIdx <= 0.94) return ["Run game stifled", "is-tough"];
        return ["No clear edge", "is-even"];
    }

    // this offense's implied points, ranked among every team playing this week
    function impliedRank(team) {
        const all = [];
        (state.slate.games || []).forEach((g) => {
            const imp = g.board && g.board.implied;
            if (imp) Object.entries(imp).forEach(([t, v]) => all.push([t, v]));
        });
        all.sort((a, b) => b[1] - a[1]);
        const i = all.findIndex(([t]) => t === team);
        return i === -1 ? null : { rank: i + 1, of: all.length };
    }

    function boardTeamHtml(game, board, off, def) {
        const e = (board.env || {})[off] || {};
        const d = (board.env || {})[def] || {};
        const leaks = (board.leaks || {})[def] || {};
        const players = (board.players || []).filter((p) => p.team === off);
        const byRole = {};
        players.forEach((p) => { byRole[p.role] = p; });
        const imp = board.implied && board.implied[off];
        const impRank = impliedRank(off);
        const [verdict, verdictTone] = matchupVerdict(leaks);

        // ── the read: softest and toughest spots, named, then the script ──
        const named = (role) => {
            const L = leaks[role], p = byRole[role];
            if (!L || L.index == null) return null;
            return { role, index: L.index, who: p ? lastName(p.name) : null, low: p && p.low_volume };
        };
        const ranked = BOARD_ROLES.map(named).filter(Boolean);
        // A soft spot only counts if someone with real volume holds that role: telling
        // a bettor a defense leaks to RB2s is no help when the RB2 has a 1% share.
        const soft = ranked.filter((r) => r.index >= 1.04 && !r.low).sort((a, b) => b.index - a.index).slice(0, 2);
        const tough = ranked.filter((r) => r.index <= 0.96).sort((a, b) => a.index - b.index).slice(0, 2);
        const phrase = (r) => `${r.role}s${r.who ? ` (${r.who})` : ""}`;
        const more = (r) => signedPct(r.index).replace("+", "");
        let read = soft.length
            ? `${def} gives up ${more(soft[0])} more than league to ${phrase(soft[0])}` +
              (soft[1] ? ` and ${more(soft[1])} more to ${phrase(soft[1])}` : "")
            : `${def} has no soft spot a player with real volume can use`;
        if (tough.length) {
            read += `${soft.length ? " but is" : ", and is"} toughest on ${tough.map((r) => `${r.role}s`).join(" and ")}`;
        }
        read += ".";
        if (imp != null) {
            read += ` ${off} is implied for <b>${imp.toFixed(1)}</b>` +
                (impRank ? `, ${ord(impRank.rank)} of ${impRank.of} teams this week.` : ".");
        }

        // ── heat strip: one cell per role, grouped, with the player who holds it ──
        const strip = LEAK_GROUPS.map(([label, roles]) => {
            const cells = roles.map((role) => {
                const L = leaks[role] || {};
                const p = byRole[role];
                const tone = leakTone(L.index);
                const tip = L.index == null ? `${role}: no sample`
                    : `${def} allows ${L.fp != null ? L.fp.toFixed(1) : "—"} half-PPR pts/g to ${role}s — ` +
                      `${signedPct(L.index)} vs league, ${softness(L.rank, L.of)} of ${L.of}`;
                return (
                    `<div class="nrs-mx-cell ${tone}" title="${tip}">` +
                    `<span class="nrs-mx-role">${role}</span>` +
                    `<span class="nrs-mx-pct">${L.index == null ? "—" : signedPct(L.index)}</span>` +
                    `<span class="nrs-mx-who${p && p.low_volume ? " is-low" : ""}">${p ? lastName(p.name) : "—"}</span>` +
                    `</div>`
                );
            }).join("");
            return `<div class="nrs-mx-group"><span class="nrs-mx-glabel">${label}</span><div class="nrs-mx-cells" style="--n:${roles.length}">${cells}</div></div>`;
        }).join("");

        // ── script meters: a dot on a 1-to-32 track instead of a rank to decode ──
        const meter = (label, value, rank, of, caption) => {
            const pos = rank && of ? ((rank - 1) / Math.max(of - 1, 1)) * 100 : null;
            return (
                `<div class="nrs-mx-meter">` +
                `<div class="nrs-mx-mtop"><span>${label}</span><b>${value}</b></div>` +
                `<div class="nrs-mx-track">${pos == null ? "" : `<i style="left:${pos}%"></i>`}</div>` +
                `<div class="nrs-mx-mcap">${caption || ""}</div>` +
                `</div>`
            );
        };
        const lean = e.neutral_pass == null ? "" : e.neutral_pass >= 58 ? "pass-first" : e.neutral_pass <= 50 ? "run-first" : "balanced";
        const impliedMeterRank = impRank ? impRank.of - impRank.rank + 1 : null; // right end = most points
        const meters =
            meter("Implied points", imp != null ? imp.toFixed(1) : "—", impliedMeterRank, impRank && impRank.of,
                impRank ? `${ord(impRank.rank)} most this week` : "") +
            meter("Pace", e.pace != null ? `${Math.round(e.pace)} plays` : "—", e.pace_rank, 32,
                e.pace_rank ? `${ord(33 - e.pace_rank)} fastest` : "") +
            meter("Pass rate", e.neutral_pass != null ? `${Math.round(e.neutral_pass)}%` : "—", e.neutral_pass_rank, 32,
                lean ? `${lean} when the score is close` : "");

        // ── defense traits as chips, each one a single fact ──
        const chip = (text, tone) => `<span class="nrs-mx-chip${tone ? " " + tone : ""}">${text}</span>`;
        const chips = [
            e.rz_trips != null ? chip(`${off} red zone <b>${e.rz_trips.toFixed(1)}</b> trips/g · <b>${Math.round(e.rz_td)}%</b> TD`) : "",
            d.def_rz_td != null ? chip(`${def} lets <b>${Math.round(d.def_rz_td)}%</b> of red-zone trips score`,
                d.def_rz_td >= 62 ? "is-soft" : d.def_rz_td <= 52 ? "is-tough" : "") : "",
            d.def_man != null ? chip(`${def} man coverage <b>${Math.round(d.def_man)}%</b> · ${ord(33 - d.def_man_rank)} most`) : "",
            d.def_pressure != null ? chip(`${def} pressure <b>${Math.round(d.def_pressure)}%</b>` +
                (e.pressure_allowed != null ? ` · ${off} allows <b>${Math.round(e.pressure_allowed)}%</b>` : "")) : "",
        ].join("");

        return (
            `<article class="nrs-mx">` +
            `<header class="nrs-mx-head">` +
            `<div class="nrs-mx-teams"><img src="${TEAM_LOGO(off)}" alt="" loading="lazy"><b>${off}</b> offense` +
            `<span class="nrs-mx-vs">vs</span><img src="${TEAM_LOGO(def)}" alt="" loading="lazy"><b>${def}</b> defense</div>` +
            `<span class="nrs-mx-verdict ${verdictTone}">${verdict}</span>` +
            `</header>` +
            `<p class="nrs-mx-read">${read}</p>` +
            `<div class="nrs-mx-strip">${strip}</div>` +
            `<p class="nrs-mx-key"><span class="is-soft"></span>gives up more than league <span class="is-tough"></span>gives up less · names are this week's depth chart</p>` +
            `<div class="nrs-mx-meters">${meters}</div>` +
            `<div class="nrs-mx-chips">${chips}</div>` +
            `</article>`
        );
    }

    function boardRowHtml(p, inj, open) {
        const key = `${p.team}|${p.role}|${p.player_id || normName(p.name)}`;
        const injury = inj[`${p.team}|${normName(p.name)}`];
        const badges = [
            `<span class="nrs-depth-badge">${p.role}</span>`,
            injury ? `<span class="nrs-bb nrs-bb--inj" title="${injury.status}${injury.injury ? " · " + injury.injury : ""}">${injury.short}</span>` : "",
            p.low_volume ? `<span class="nrs-bb nrs-bb--low" title="Grade discounted: not enough of the work to use the matchup">Low vol</span>` : "",
            p.new_team ? `<span class="nrs-bb nrs-bb--new" title="His numbers were built with another team">New team</span>` : "",
        ].join("");
        const photo = p.headshot ? `<img class="nrs-br-photo" src="${thumb(p.headshot)}" alt="" loading="lazy" onerror="this.style.visibility='hidden'">` : `<span class="nrs-br-photo"></span>`;
        const player =
            `<td class="nrs-br-player"><button type="button" class="nrs-br-toggle" data-board-key="${key}" aria-expanded="${open}">` +
            `<span class="nrs-br-caret" aria-hidden="true">${open ? "▾" : "▸"}</span>${photo}` +
            `<span class="nrs-br-id"><span class="nrs-br-name">${p.name}${badges}</span>` +
            `<span class="nrs-br-sub"><img src="${TEAM_LOGO(p.team)}" alt="" loading="lazy">${p.team} vs ${p.opp}` +
            `${p.games ? ` · ${p.games} g` : ""}</span></span></button></td>`;

        if (p.no_history) {
            return `<tr class="nrs-br">${player}<td colspan="5" class="nrs-br-none">No games to build a read from yet — he is ${p.role} on the current depth chart.</td></tr>`;
        }

        let usage = `<td class="nrs-br-usage"><span class="nrs-br-dim">—</span></td>`;
        if (p.share != null) {
            const diff = p.share_l3 - p.share;
            const arrow = diff >= 3 ? `<span class="nrs-up">▲ ${Math.round(p.share_l3)}%</span>`
                : diff <= -3 ? `<span class="nrs-down">▼ ${Math.round(p.share_l3)}%</span>` : `<span class="nrs-br-dim">steady</span>`;
            usage = `<td class="nrs-br-usage"><b>${Math.round(p.share)}%</b><span class="nrs-br-sub2">${p.share_kind} · ${arrow} L3</span></td>`;
        }

        const m = p.matchup || {};
        const matchup = m.index == null ? `<td><span class="nrs-br-dim">—</span></td>`
            : `<td class="nrs-br-match"><span class="nrs-mpill ${leakClass(m.index)}">#${m.rank} · ×${m.index.toFixed(2)}</span>` +
              `<span class="nrs-br-sub2">${p.opp} vs ${p.role}s</span></td>`;

        const stats = Object.keys(p.proj || {});
        const head = stats[0];
        const projCell = head
            ? `<td class="nrs-br-proj"><b>${fmtProj(p.proj[head], head)}</b> <span class="nrs-br-unit">${STAT_NAME[head]}</span>` +
              `<span class="nrs-br-sub2">${stats.slice(1).map((s) => `${fmtProj(p.proj[s], s)} ${STAT_NAME[s]}`).join(" · ")}</span></td>`
            : `<td></td>`;

        const td = p.td_chance == null ? `<td></td>`
            : `<td class="nrs-br-td"><b>${p.td_chance}%</b><span class="nrs-tdbar"><span style="width:${Math.min(100, p.td_chance)}%"></span></span></td>`;

        const grade = `<td class="nrs-br-grade"><span class="nrs-grade ${gradeClass(p.grade)}">${p.grade == null ? "—" : p.grade}</span></td>`;
        // decisions first: grade and TD beside the name, the inputs behind them after
        return `<tr class="nrs-br${open ? " is-open" : ""}">${player}${grade}${td}${projCell}${matchup}${usage}</tr>`;
    }

    function fmtProj(v, stat) {
        if (v == null) return "—";
        return stat === "pass_td" || stat === "rec" || stat === "tgt" ? v.toFixed(1) : String(Math.round(v));
    }

    function boardDetailHtml(p, game, board) {
        const reasons = (p.reasons || []).map((r) => {
            // an empty cell still has to hold its grid column, or the text slides into it
            const pts = r.points == null ? `<span class="nrs-br-dim">—</span>` : `<span class="${r.points >= 0 ? "nrs-up" : "nrs-down"}">${r.points >= 0 ? "+" : ""}${r.points.toFixed(0)}</span>`;
            return `<li><span class="nrs-why-part">${PART_LABEL[r.part] || r.part}</span>${pts}<span class="nrs-why-text">${r.text}</span></li>`;
        }).join("");

        const stats = Object.keys(p.proj || {});
        const logRows = (p.log || []).slice().reverse().map((g) =>
            `<tr><td>${g.season === state.season ? "" : `'${String(g.season).slice(-2)} `}W${g.week}</td>` +
            `<td><span class="nrs-opp"><img src="${TEAM_LOGO(g.opp)}" alt="" loading="lazy" onerror="this.remove()">${g.opp}</span></td>` +
            `<td>${g.role || "—"}</td>` +
            stats.map((s) => `<td>${g[s] == null ? "—" : Math.round(g[s])}</td>`).join("") + `</tr>`
        ).join("");

        const m = p.matchup || {};
        const allowRows = stats.map((s) => {
            const a = (m.allowed || {})[s], l = (m.league || {})[s];
            const edge = a != null && l ? (a - l) / (l || 1) : null;
            const cls = edge == null ? "" : edge >= 0.08 ? "nrs-up" : edge <= -0.08 ? "nrs-down" : "";
            return `<tr><td>${STAT_NAME[s]}</td><td class="${cls}">${a != null ? fmtProj(a, s) : "—"}</td><td>${l != null ? fmtProj(l, s) : "—"}</td></tr>`;
        }).join("");

        const e = (board.env || {})[p.team] || {};
        const d = (board.env || {})[p.opp] || {};
        const lines = [];
        if (p.pos !== "QB" && p.rz_share != null) {
            lines.push(`Handles <b>${Math.round(p.rz_share)}%</b> of ${p.team}'s red-zone work · ${p.team} reaches the 20 <b>${e.rz_trips != null ? e.rz_trips.toFixed(1) : "—"}</b> times a game · ${p.opp} lets <b>${d.def_rz_td != null ? Math.round(d.def_rz_td) : "—"}%</b> of those trips score`);
        }
        if (p.cov && (p.cov.man_t || p.cov.zone_t)) {
            const ypt = (v) => (v == null ? "—" : v.toFixed(1));
            lines.push(`<b>${ypt(p.cov.man_ypt)}</b> yds/target vs man (${p.cov.man_t}) · <b>${ypt(p.cov.zone_ypt)}</b> vs zone (${p.cov.zone_t})` +
                (d.def_man != null ? ` · ${p.opp} plays man ${Math.round(d.def_man)}%` : ""));
        }

        return (
            `<tr class="nrs-bd"><td colspan="6"><div class="nrs-bd-grid">` +
            `<section><h4>Why ${p.grade == null ? "no grade" : `a ${p.grade}`}</h4><ul class="nrs-why">${reasons || "<li>No components available.</li>"}</ul>` +
            (lines.length ? `<ul class="nrs-bd-lines">${lines.map((l) => `<li>${l}</li>`).join("")}</ul>` : "") +
            `</section>` +
            `<section><h4>Last ${(p.log || []).length} games</h4><table class="nrs-bd-table"><thead><tr><th>Wk</th><th>Opp</th><th>Role</th>` +
            stats.map((s) => `<th>${STAT_NAME[s]}</th>`).join("") + `</tr></thead><tbody>${logRows}</tbody></table></section>` +
            `<section><h4>${p.opp} vs ${p.role}s, per game</h4><table class="nrs-bd-table"><thead><tr><th></th><th>${p.opp}</th><th>League</th></tr></thead>` +
            `<tbody>${allowRows}</tbody></table>` +
            `<p class="nrs-bd-proj">Projection: ${stats.map((s) => `<b>${fmtProj(p.proj[s], s)}</b> ${STAT_NAME[s]}`).join(" · ")}</p></section>` +
            `</div></td></tr>`
        );
    }

    function renderBoard() {
        const host = el("nrsBoardSection");
        const tabs = el("nrsViewTabs");
        const game = currentGame();
        if (!host) return;
        if (tabs) {
            tabs.hidden = !game;
            tabs.querySelectorAll("[data-hostview]").forEach((b) => b.classList.toggle("is-active", b.dataset.hostview === state.hostView));
        }
        if (!game || state.hostView !== "board") { host.hidden = true; return; }
        host.hidden = false;
        const board = game.board;
        if (!board) {
            host.innerHTML = `<p class="nrs-empty">The Game Board starts with Week 2 — pick a later week above, or use Player Logs for this one.</p>`;
            return;
        }

        const inj = injuryIndex();
        const f = state.boardFilter;
        if (f.team !== "both" && f.team !== game.away && f.team !== game.home) f.team = "both";
        let players = board.players.filter((p) =>
            (f.pos === "All" || p.pos === f.pos) && (f.team === "both" || p.team === f.team));
        const sorters = {
            grade: (p) => p.grade ?? -1,
            td: (p) => p.td_chance ?? -1,
            proj: (p) => { const k = Object.keys(p.proj || {})[0]; return k ? (p.proj[k] || 0) / ({ pass_yds: 3.5 }[k] || 1) : -1; },
        };
        players = players.slice().sort((a, b) => sorters[f.sort](b) - sorters[f.sort](a));

        const seg = (name, value, options) =>
            `<div class="nrs-seg" role="group" aria-label="${name}">` +
            options.map(([v, label]) => `<button type="button" data-bf="${name}" data-bv="${v}"${value === v ? ' class="is-active"' : ""}>${label}</button>`).join("") +
            `</div>`;

        const rows = players.map((p) => {
            const key = `${p.team}|${p.role}|${p.player_id || normName(p.name)}`;
            const open = state.boardOpen.has(key);
            return boardRowHtml(p, inj, open) + (open && !p.no_history ? boardDetailHtml(p, game, board) : "");
        }).join("");

        const seasons = [...new Set(board.players.flatMap((p) => p.seasons || []))].sort();
        host.innerHTML =
            boardScriptHtml(game, board) +
            `<p class="nrs-board-window">Each player's and each defense's last 17 games` +
            (seasons.length > 1 ? `, reaching back into ${seasons[0]} while ${seasons[seasons.length - 1]} is young. Rosters and roles have changed since — treat early reads as leans.` : ".") +
            `</p>` +
            `<div class="nrs-bt-grid">${boardTeamHtml(game, board, game.away, game.home)}${boardTeamHtml(game, board, game.home, game.away)}</div>` +
            `<div class="nrs-board-controls">` +
            seg("pos", f.pos, [["All", "All"], ["QB", "QB"], ["RB", "RB"], ["WR", "WR"], ["TE", "TE"]]) +
            seg("team", f.team, [["both", "Both"], [game.away, game.away], [game.home, game.home]]) +
            `<label class="nrs-board-sort">Sort <select data-bf="sort">` +
            [["grade", "Grade"], ["td", "TD chance"], ["proj", "Projection"]]
                .map(([v, l]) => `<option value="${v}"${f.sort === v ? " selected" : ""}>${l}</option>`).join("") +
            `</select></label>` +
            `</div>` +
            `<div class="nrs-table-wrap"><table class="nrs-board-table">` +
            `<thead><tr><th>Player</th><th title="Matchup grade, 0-100: 50 is neutral for this player">Grade</th><th>TD</th><th>Projection</th><th>Matchup</th><th>Usage</th></tr></thead>` +
            `<tbody>${rows || `<tr><td colspan="6" class="nrs-br-none">No players match these filters.</td></tr>`}</tbody></table></div>` +
            `<p class="nrs-legend"><strong>Grade</strong> is how much this game helps <em>this</em> player against his own normal output — 50 is neutral, so a star can sit at 40 in a hard spot and a WR3 at 75 in a soft one. ` +
            `It weighs what the defense allows to his role, his team's implied points, the defense's man/zone mix against his splits, and whether his share is rising, then discounts players without enough of the work to use the edge. ` +
            `<strong>Matchup</strong> is half-PPR points allowed to his role against league average (#32 is the softest). ` +
            `<strong>TD</strong> is the chance of at least one touchdown: red-zone work × trips × how often this defense lets a trip score, plus his scores from outside the 20. ` +
            `Open any row for the reasons, his last five games and what this defense has given up.</p>`;
    }

    function initBoard() {
        const tabs = el("nrsViewTabs");
        if (tabs) tabs.addEventListener("click", (ev) => {
            const b = ev.target.closest("[data-hostview]");
            if (!b) return;
            state.hostView = b.dataset.hostview;
            renderMatchup();
        });
        const host = el("nrsBoardSection");
        if (!host) return;
        host.addEventListener("click", (ev) => {
            const toggle = ev.target.closest("[data-board-key]");
            if (toggle) {
                const k = toggle.dataset.boardKey;
                state.boardOpen.has(k) ? state.boardOpen.delete(k) : state.boardOpen.add(k);
                renderBoard();
                return;
            }
            const seg = ev.target.closest("[data-bf][data-bv]");
            if (seg) {
                state.boardFilter[seg.dataset.bf] = seg.dataset.bv;
                renderBoard();
            }
        });
        host.addEventListener("change", (ev) => {
            const sel = ev.target.closest("select[data-bf]");
            if (sel) { state.boardFilter[sel.dataset.bf] = sel.value; renderBoard(); }
        });
    }

    // ── player popup ─────────────────────────────────────────────────────────
    // Clicking a name on a Player Logs card opens that player's Game Board read in
    // a dialog, laid out like the MLB research profile: header, a hero row of the
    // numbers that decide the bet, then tabs. Nobody has to leave the logs to see it.
    let profilePlayer = null;

    function boardPlayerFor(team, role, pid, name) {
        const game = currentGame();
        const players = (game && game.board && game.board.players) || [];
        return players.find((p) => pid && p.player_id === pid)
            || players.find((p) => p.team === team && p.role === role)
            || players.find((p) => p.team === team && normName(p.name) === normName(name))
            || null;
    }

    function profileHeroHtml(p) {
        const tile = (label, value, sub, cls) =>
            `<div class="nrs-pf-tile${cls ? " " + cls : ""}"><span class="nrs-pf-label">${label}</span>` +
            `<span class="nrs-pf-value">${value}</span>${sub ? `<span class="nrs-pf-sub">${sub}</span>` : ""}</div>`;
        const stats = Object.keys(p.proj || {});
        const head = stats[0];
        const m = p.matchup || {};
        return (
            `<div class="nrs-pf-hero">` +
            tile("Grade", p.grade == null ? "—" : p.grade, p.low_volume ? "discounted: low volume" : "50 is neutral for him", `nrs-pf-grade ${gradeClass(p.grade)}`) +
            tile("TD chance", p.td_chance == null ? "—" : `${p.td_chance}%`, "at least one touchdown") +
            (head ? tile("Projection", `${fmtProj(p.proj[head], head)}`, STAT_NAME[head]) : "") +
            (m.index != null
                ? tile(`${p.opp} vs ${p.role}s`, signedPct(m.index), `${softness(m.rank, m.of)} of ${m.of}`, leakClass(m.index))
                : "") +
            `</div>`
        );
    }

    function profileReadHtml(p, board) {
        const reasons = (p.reasons || []).map((r) => {
            const pts = r.points == null ? `<span class="nrs-br-dim">—</span>`
                : `<span class="${r.points >= 0 ? "nrs-up" : "nrs-down"}">${r.points >= 0 ? "+" : ""}${r.points.toFixed(0)}</span>`;
            return `<li><span class="nrs-why-part">${PART_LABEL[r.part] || r.part}</span>${pts}<span class="nrs-why-text">${r.text}</span></li>`;
        }).join("");
        const e = (board.env || {})[p.team] || {};
        const d = (board.env || {})[p.opp] || {};
        const facts = [];
        if (p.share != null) {
            facts.push(`<b>${Math.round(p.share)}%</b> ${p.share_kind} over ${p.games} games · <b>${Math.round(p.share_l3)}%</b> over the last 3`);
        }
        if (p.pos !== "QB" && p.rz_share != null) {
            facts.push(`Handles <b>${Math.round(p.rz_share)}%</b> of ${p.team}'s red-zone work · ${p.team} reaches the 20 <b>${e.rz_trips != null ? e.rz_trips.toFixed(1) : "—"}</b> times a game · ${p.opp} lets <b>${d.def_rz_td != null ? Math.round(d.def_rz_td) : "—"}%</b> of those trips score`);
        }
        if (p.cov && (p.cov.man_t || p.cov.zone_t)) {
            const ypt = (v) => (v == null ? "—" : v.toFixed(1));
            facts.push(`<b>${ypt(p.cov.man_ypt)}</b> yds/target vs man (${p.cov.man_t}) · <b>${ypt(p.cov.zone_ypt)}</b> vs zone (${p.cov.zone_t})` +
                (d.def_man != null ? ` · ${p.opp} plays man ${Math.round(d.def_man)}%` : ""));
        }
        const stats = Object.keys(p.proj || {});
        return (
            `<h4 class="nrs-pf-h">Why ${p.grade == null ? "no grade" : `a ${p.grade}`}</h4>` +
            `<ul class="nrs-why">${reasons || "<li>No components available.</li>"}</ul>` +
            (facts.length ? `<ul class="nrs-bd-lines">${facts.map((f) => `<li>${f}</li>`).join("")}</ul>` : "") +
            (stats.length ? `<p class="nrs-bd-proj">Projection: ${stats.map((s) => `<b>${fmtProj(p.proj[s], s)}</b> ${STAT_NAME[s]}`).join(" · ")}</p>` : "")
        );
    }

    function profileMatchupHtml(p, board) {
        const m = p.matchup || {};
        const stats = Object.keys(p.proj || {});
        const rows = stats.map((s) => {
            const a = (m.allowed || {})[s], l = (m.league || {})[s];
            const edge = a != null && l ? (a - l) / (l || 1) : null;
            const cls = edge == null ? "" : edge >= 0.08 ? "nrs-up" : edge <= -0.08 ? "nrs-down" : "";
            return `<tr><td>${STAT_NAME[s]}</td><td class="${cls}">${a != null ? fmtProj(a, s) : "—"}</td>` +
                `<td>${l != null ? fmtProj(l, s) : "—"}</td>` +
                `<td class="${cls}">${edge == null ? "—" : `${edge >= 0 ? "+" : "−"}${Math.abs(Math.round(edge * 100))}%`}</td></tr>`;
        }).join("");
        const [verdict, tone] = matchupVerdict((board.leaks || {})[p.opp] || {});
        const d = (board.env || {})[p.opp] || {};
        return (
            `<div class="nrs-pf-verdict"><span class="nrs-mx-verdict ${tone}">${verdict}</span>` +
            `<span>for the ${p.team} offense against ${p.opp}</span></div>` +
            `<h4 class="nrs-pf-h">What ${p.opp} allows to ${p.role}s, per game</h4>` +
            `<table class="nrs-bd-table nrs-pf-table"><thead><tr><th></th><th>${p.opp}</th><th>League</th><th>Diff</th></tr></thead><tbody>${rows}</tbody></table>` +
            `<div class="nrs-mx-chips nrs-pf-chips">` +
            (d.def_rz_td != null ? `<span class="nrs-mx-chip">${p.opp} lets <b>${Math.round(d.def_rz_td)}%</b> of red-zone trips score</span>` : "") +
            (d.def_man != null ? `<span class="nrs-mx-chip">${p.opp} man coverage <b>${Math.round(d.def_man)}%</b></span>` : "") +
            (d.def_pressure != null ? `<span class="nrs-mx-chip">${p.opp} pressure <b>${Math.round(d.def_pressure)}%</b></span>` : "") +
            `</div>`
        );
    }

    function profileLogHtml(p) {
        const stats = Object.keys(p.proj || {});
        const rows = (p.log || []).slice().reverse().map((g) =>
            `<tr><td>${weekLabel(g)}</td>` +
            `<td><span class="nrs-opp"><img src="${TEAM_LOGO(g.opp)}" alt="" loading="lazy" onerror="this.remove()">${g.opp}</span></td>` +
            `<td>${g.role || "—"}</td>` + stats.map((s) => `<td>${g[s] == null ? "—" : Math.round(g[s])}</td>`).join("") + `</tr>`
        ).join("");
        const avg = stats.map((s) => `<td><b>${fmtProj((p.window || {})[s], s)}</b></td>`).join("");
        return (
            `<h4 class="nrs-pf-h">Last ${(p.log || []).length} games</h4>` +
            `<table class="nrs-bd-table nrs-pf-table"><thead><tr><th>Wk</th><th>Opp</th><th>Role</th>` +
            stats.map((s) => `<th>${STAT_NAME[s]}</th>`).join("") + `</tr></thead><tbody>${rows}</tbody>` +
            `<tfoot><tr><td colspan="3">Avg, last ${p.games}</td>${avg}</tr></tfoot></table>`
        );
    }

    function openProfile(p) {
        const dlg = el("nrsProfile");
        const game = currentGame();
        if (!dlg || !p || !game) return;
        profilePlayer = p;
        const board = game.board || {};
        const inj = injuryIndex()[`${p.team}|${normName(p.name)}`];

        const photo = el("nrsProfilePhoto");
        if (p.headshot) { photo.src = thumb(p.headshot); photo.hidden = false; } else { photo.hidden = true; }
        el("nrsProfileName").innerHTML = `${p.name}<span class="nrs-depth-badge">${p.role}</span>` +
            (inj ? `<span class="nrs-bb nrs-bb--inj" title="${inj.status}">${inj.short}</span>` : "") +
            (p.low_volume ? `<span class="nrs-bb nrs-bb--low">Low vol</span>` : "") +
            (p.new_team ? `<span class="nrs-bb nrs-bb--new">New team</span>` : "");
        el("nrsProfileSub").textContent = p.no_history
            ? `${p.team} · on the depth chart, no games yet`
            : `${p.team} · ${p.games} games in the sample${p.seasons && p.seasons.length > 1 ? ` · ${seasonSpan(p.seasons)}` : ""}`;
        el("nrsProfileGame").textContent = `${game.away} @ ${game.home}\n${formatKickoff(game.kickoff)}`;

        const body = el("nrsProfileBody");
        if (p.no_history) {
            body.innerHTML = `<p class="nrs-empty">No games to build a read from yet — he is ${p.role} on the current depth chart.</p>`;
        } else {
            body.innerHTML =
                profileHeroHtml(p) +
                `<nav class="nrs-pf-tabs" role="tablist" aria-label="Player detail">` +
                [["read", "The Read"], ["matchup", "Matchup"], ["log", "Last games"]]
                    .map(([k, l], i) => `<button type="button" role="tab" data-pftab="${k}" aria-selected="${i === 0}"${i === 0 ? ' class="is-active"' : ""}>${l}</button>`).join("") +
                `</nav>` +
                `<section class="nrs-pf-panel is-active" data-pfpanel="read">${profileReadHtml(p, board)}</section>` +
                `<section class="nrs-pf-panel" data-pfpanel="matchup">${profileMatchupHtml(p, board)}</section>` +
                `<section class="nrs-pf-panel" data-pfpanel="log">${profileLogHtml(p)}</section>`;
        }
        el("nrsProfileBoard").hidden = !!p.no_history;
        if (typeof dlg.showModal === "function") dlg.showModal();
        else dlg.setAttribute("open", "");
    }

    function closeProfile() {
        const dlg = el("nrsProfile");
        profilePlayer = null;
        if (dlg && typeof dlg.close === "function") dlg.close();
        else if (dlg) dlg.removeAttribute("open");
    }

    function initProfile() {
        const dlg = el("nrsProfile");
        if (!dlg) return;
        el("nrsProfileClose").addEventListener("click", closeProfile);
        // a click on the dimmed backdrop lands on the dialog element itself
        dlg.addEventListener("click", (ev) => {
            if (ev.target === dlg) { closeProfile(); return; }
            const tab = ev.target.closest("[data-pftab]");
            if (!tab) return;
            dlg.querySelectorAll("[data-pftab]").forEach((b) => {
                const on = b === tab;
                b.classList.toggle("is-active", on);
                b.setAttribute("aria-selected", String(on));
            });
            dlg.querySelectorAll("[data-pfpanel]").forEach((s) => s.classList.toggle("is-active", s.dataset.pfpanel === tab.dataset.pftab));
        });
        dlg.addEventListener("cancel", () => { profilePlayer = null; });
        document.addEventListener("keydown", (ev) => {
            if (ev.key === "Escape" && dlg.open) { ev.preventDefault(); closeProfile(); }
        });

        // from the popup straight to his row on the Game Board, opened
        el("nrsProfileBoard").addEventListener("click", () => {
            const p = profilePlayer;
            if (!p) return;
            state.hostView = "board";
            state.boardFilter.team = "both";
            state.boardFilter.pos = "All";
            state.boardOpen.add(`${p.team}|${p.role}|${p.player_id || normName(p.name)}`);
            closeProfile();
            renderMatchup();
            const toggle = document.querySelector(`[data-board-key="${p.team}|${p.role}|${p.player_id || normName(p.name)}"]`);
            if (toggle) toggle.scrollIntoView({ block: "center", behavior: "smooth" });
        });

        // names on the Player Logs cards open the popup
        const host = el("nrsPosSections");
        if (host) host.addEventListener("click", (ev) => {
            const btn = ev.target.closest("[data-profile-role]");
            if (!btn) return;
            const p = boardPlayerFor(btn.dataset.profileTeam, btn.dataset.profileRole, btn.dataset.profilePid, btn.dataset.profileName);
            if (p) openProfile(p);
        });
    }

    function renderMatchup() {
        // every trigger that re-renders the logs re-renders the board first; the
        // heavy log cards are only built while their tab is the one open
        renderBoard();
        const game = currentGame();
        const section = el("nrsMatchupSection");
        if (!game || state.hostView !== "logs") {
            section.hidden = true;
            return;
        }
        section.hidden = false;

        const offenseIsAway = state.side === "away";
        const offName = offenseIsAway ? game.away_name : game.home_name;
        const offLogo = offenseIsAway ? game.away_logo : game.home_logo;
        const defName = offenseIsAway ? game.home_name : game.away_name;
        // "Chargers" rather than "Los Angeles Chargers": short enough to fit a card
        // header, and unlike the city it never collides with the other LA or NY side
        const defShort = (offenseIsAway ? game.home_short : game.away_short) || defName;
        const defLogo = offenseIsAway ? game.home_logo : game.away_logo;
        const offense = offenseBlock(game, offenseIsAway ? "away" : "home") || {};
        const defense = defenseBlock(game, offenseIsAway ? "home" : "away") || {};

        el("nrsMatchupTitle").textContent = `${game.away_name} @ ${game.home_name}`;
        let sub = formatKickoff(game.kickoff) + (game.status ? ` · ${game.status}` : "");
        if (game.odds && (game.odds.details || game.odds.over_under != null)) {
            const parts = [];
            if (game.odds.details) parts.push(game.odds.details);
            if (game.odds.over_under != null) parts.push(`O/U ${game.odds.over_under}`);
            sub += ` · ${game.odds.book || "Line"}: ${parts.join(" · ")}`;
        }
        el("nrsMatchupSub").textContent = sub;
        el("nrsSideAway").classList.toggle("is-active", offenseIsAway);
        el("nrsSideHome").classList.toggle("is-active", !offenseIsAway);
        el("nrsSideAway").textContent = `${game.away} OFF`;
        el("nrsSideHome").textContent = `${game.home} OFF`;

        const offAbbr = offenseIsAway ? game.away : game.home;
        const defAbbr = offenseIsAway ? game.home : game.away;

        // gameId/kickoff/gameLabel ride along so a tracked prop can carry its own
        // expiry and still name its game after the slate rolls to the next week
        const meta = {
            offName, offLogo, defName, defShort, defLogo, offAbbr, defAbbr,
            gameId: game.id,
            kickoff: game.kickoff,
            gameLabel: `${game.away} @ ${game.home}`,
        };
        // resolved once per render so every picker knows what is already saved
        const trackedIds = trackedIdSet();
        const cards = POSITIONS
            .flatMap((pos) => {
                const cols = visibleCols(pos);
                const defBlock = defense[pos] || { overall: null, ranks: {} };
                return (offense[pos] || []).map((player) => playerCardHtml(pos, cols, player, defBlock, meta, trackedIds));
            })
            .join("");
        const lineupCount = POSITIONS.reduce((n, pos) => n + (offense[pos] || []).length, 0);
        const lineupHead =
            `<header class="nrs-lineup-head">` +
            (offLogo ? `<img src="${offLogo}" alt="" loading="lazy">` : "") +
            `<div><h3>${offAbbr} Lineup</h3>` +
            `<span>${lineupCount} players from the current depth chart · QB1 · RB1–2 · WR1–3 · TE1–2</span></div>` +
            `</header>`;
        el("nrsPosSections").innerHTML =
            defenseOverviewHtml(defense, meta) +
            lineupHead +
            `<div class="nrs-player-grid">${cards || `<p class="nrs-empty">No player data for ${offName}.</p>`}</div>`;
        placeColPanel();
    }

    // top section: what this defense allows per game vs each position overall
    function defenseOverviewHtml(defense, meta) {
        const logo = meta.defLogo ? `<img class="nrs-def-overview__logo" src="${meta.defLogo}" alt="" loading="lazy">` : "";
        const cards = POSITIONS
            .map((pos) => {
                const overall = (defense[pos] || {}).overall;
                const league = (state.leagueAvg && state.leagueAvg[pos] && state.leagueAvg[pos].overall) || null;
                if (!overall) return "";
                const rows = visibleCols(pos)
                    .map((col) => {
                        const allowed = colVal(overall, col);
                        const leagueVal = colVal(league, col);
                        return `<tr><td class="nrs-stat-label">${col.name}</td><td class="nrs-cell"${heatAttr(allowed, leagueVal, col)}>${fmtStat(allowed, col, true)}</td></tr>`;
                    })
                    .join("");
                return (
                    `<article class="nrs-def-card">` +
                    `<header class="nrs-def-card__head">vs all ${pos}s</header>` +
                    `<table class="nrs-table nrs-table--down"><tbody>${rows}</tbody></table>` +
                    `</article>`
                );
            })
            .join("");
        return (
            `<section class="nrs-def-overview">` +
            `<header class="nrs-def-overview__head">${logo}<div>` +
            `<span class="nrs-def-overview__title">${meta.defName} — D allows per game</span>` +
            `<span class="nrs-def-overview__sub">Combined production allowed to each position · green = gives up more than league average</span>` +
            `</div></header>` +
            `<div class="nrs-def-grid">${cards}</div>` +
            `</section>`
        );
    }

    function defForRank(defBlock, rank) {
        if (!defBlock) return null;
        const ranks = defBlock.ranks || {};
        return ranks[String(rank)] || defBlock.overall || null;
    }

    // game-log filter: last N, vs this opponent, or home/away splits
    const FILTER_LAST = { l5: 5, l10: 10, l15: 15 };
    function filterLog(log, oppAbbr, f) {
        if (f === "opp") return log.filter((g) => g.opp === oppAbbr);
        if (f === "home") return log.filter((g) => g.ha !== "@");
        if (f === "away") return log.filter((g) => g.ha === "@");
        const n = FILTER_LAST[f] || 0;
        return n && log.length > n ? log.slice(-n) : log;
    }

    // One bar per panel. They used to share a single filter, so narrowing the
    // player to "vs SEA" also narrowed what the defense showed -- you could not ask
    // "his last five against that defense's whole season", which is usually the
    // comparison you actually want.
    function filterBarHtml(kind, active, abbr, pos, cardKey) {
        const options = [
            ["l5", "L5"], ["l10", "L10"], ["l15", "L15"], ["all", "All"],
            ["opp", `vs ${abbr}`], ["home", "Home"], ["away", "Away"],
        ];
        const buttons = options
            .map(([f, label]) => `<button type="button" data-filter="${f}"${f === active ? ' class="is-active"' : ""}>${label}</button>`)
            .join("");
        const gearId = `${cardKey}|${kind}`;
        return (
            `<div class="nrs-card-filterbar">` +
            `<div class="nrs-log-filter nrs-log-filter--card" role="group" aria-label="Game log filter" data-kind="${kind}">${buttons}</div>` +
            `<button type="button" class="nrs-card-gear" data-colgear="${pos}" data-gear-id="${gearId}" ` +
            `aria-haspopup="dialog" aria-expanded="false" title="Choose ${pos === "WR" || pos === "TE" ? "WR & TE" : pos} columns" ` +
            `aria-label="Column settings for ${pos}">&#9881;</button>` +
            `</div>`
        );
    }

    function playerCardHtml(pos, cols, player, defBlock, meta, trackedIds) {
        const rank = player.rank;
        const defRow = defForRank(defBlock, rank);
        const league = (state.leagueAvg && state.leagueAvg[pos]) || null;
        const leagueRow = league ? league.ranks[String(rank)] || league.overall : null;
        const lines = player.lines || {};

        const cardKey = `${pos}${rank}-${(player.name || "").replace(/[^a-zA-Z0-9]/g, "")}`;
        const offFilter = state.logFilter.off || DEFAULT_FILTER;
        const defFilter = state.logFilter.def || DEFAULT_FILTER;

        // "vs OPP": player log vs this defense, defense log vs the player's team
        const playerLog = filterLog(player.log || [], meta.defAbbr, offFilter);
        const defLog = filterLog((defBlock.rank_logs || {})[String(rank)] || [], meta.offAbbr, defFilter);

        const statHead = cols.map((c) => `<th title="${c.name}">${c.abbr}</th>`).join("");
        const logHead = `<tr><th>Wk</th><th class="nrs-th-opp">Opp</th><th>W/L</th>${statHead}</tr>`;

        const oppCell = (g) => {
            const logo = TEAM_LOGO(g.opp);
            const img = logo ? `<img src="${logo}" alt="" loading="lazy" onerror="this.remove()">` : "";
            return `<span class="nrs-opp">${g.ha === "@" ? "@" : "vs"} ${img}${g.opp}</span>`;
        };
        const wlCell = (g) => {
            const wl = (g.wl || "").toUpperCase();
            const cls = wl === "W" ? "nrs-wl--w" : wl === "L" ? "nrs-wl--l" : "nrs-wl--t";
            return `<td class="nrs-log-wl ${cls}">${wl || "—"}</td>`;
        };

        // ── left: player game log, each game colored vs the player's own season average ──
        const playerRows = playerLog
            .map((g) => {
                const cells = cols
                    .map((col) => {
                        const val = colVal(g.stats, col, true);
                        const avg = colVal(player.stats, col);
                        return `<td class="nrs-cell"${heatAttr(val, avg, col)}>${fmtStat(val, col)}</td>`;
                    })
                    .join("");
                return `<tr><td class="nrs-log-week">${weekLabel(g)}</td><td class="nrs-log-opp">${oppCell(g)}</td>${wlCell(g)}${cells}</tr>`;
            })
            .join("") || `<tr><td colspan="${cols.length + 3}" class="nrs-log-none">No games match this filter.</td></tr>`;

        // avg row: season average colored vs what this defense allows (the matchup)
        const playerAvgCells = cols
            .map((col) => {
                const val = colVal(player.stats, col);
                const defVal = colVal(defRow, col);
                return `<td class="nrs-cell"${heatAttr(val, defVal, col)}>${fmtStat(val, col, true)}</td>`;
            })
            .join("");

        // ── right: defense game log vs this position rank, colored vs league average ──
        const defRows = defLog
            .map((g) => {
                const cells = cols
                    .map((col) => {
                        const val = colVal(g.stats, col, true);
                        const leagueVal = colVal(leagueRow, col);
                        return `<td class="nrs-cell"${heatAttr(val, leagueVal, col)}>${fmtStat(val, col)}</td>`;
                    })
                    .join("");
                return `<tr><td class="nrs-log-week">${weekLabel(g)}</td><td class="nrs-log-opp" title="${g.player || ""}">${oppCell(g)}</td>${wlCell(g)}${cells}</tr>`;
            })
            .join("") || `<tr><td colspan="${cols.length + 3}" class="nrs-log-none">No games match this filter.</td></tr>`;

        const defAvgCells = cols
            .map((col) => {
                const val = colVal(defRow, col);
                const leagueVal = colVal(leagueRow, col);
                return `<td class="nrs-cell"${heatAttr(val, leagueVal, col)}>${fmtStat(val, col, true)}</td>`;
            })
            .join("");

        // The track control sits UNDER its own column. A separate picker meant
        // reading a market name off a list and hoping it matched the column you had
        // been looking at; here the button is directly beneath the numbers it refers
        // to, so there is nothing to match up. Book lines fill the box when a feed
        // is connected -- without one the player's own per-game average is the
        // honest starting point, and it is nudged onto a half so the line has the
        // shape a real one would.
        const baseId = `${state.season}-${state.week}-${meta.gameId || ""}-${cardKey}`;
        const trackExpires = trackExpiry(meta.kickoff);
        const trackMeta = `${pos}${rank} · ${meta.offAbbr} vs ${meta.defAbbr}`;
        const trackAttrs =
            ` data-track-name="${(player.name || "").replace(/"/g, "&quot;")}"` +
            ` data-track-meta="${trackMeta}"` +
            ` data-track-game="${meta.gameLabel || ""}"` +
            ` data-track-expires="${trackExpires}"`;

        const trackCells = cols
            .map((col) => {
                // rates, shares and red-zone counts are context, not something a book posts
                if (!MARKETS.has(col.key)) return `<td class="nrs-tc nrs-tc--none" aria-hidden="true"></td>`;
                const label = LINE_LABELS[col.key] || col.name;
                const book = lines[col.key];
                const suggested = book != null ? book : halfStep(colVal(player.stats, col));
                const id = `${baseId}|${col.key}`;
                // any side/line already saved for this market lights the cell up
                const on = [...trackedIds].some((t) => t.startsWith(`${id}|`));
                return (
                    `<td class="nrs-tc${on ? " is-on" : ""}" data-tc-key="${col.key}" data-tc-label="${label}">` +
                    `<div class="nrs-tc__wrap">` +
                    `<button type="button" class="nrs-tc__side" data-tc-side="over" title="Over / Under">O</button>` +
                    `<select class="nrs-tc__line" ` +
                    `aria-label="${label} line for ${player.name}"${book != null ? ' data-book="1"' : ""}>` +
                    lineLadder(col.key, suggested)
                        .map((v) => `<option value="${v}"${v === Number(suggested) ? " selected" : ""}>${v}</option>`)
                        .join("") +
                    `</select>` +
                    `<button type="button" class="nrs-tc__add" data-tc-id="${id}"${trackAttrs} ` +
                    `aria-label="Track ${label} for ${player.name}" title="Track this prop">` +
                    `${on ? "✓" : "+"}</button>` +
                    `</div></td>`
                );
            })
            .join("");
        const trackRow =
            `<tr class="nrs-track-row-cells">` +
            `<td class="nrs-log-week nrs-tc__label" colspan="3">Track</td>${trackCells}</tr>`;

        // with a Game Board on the slate, the name opens this player's read in a popup
        const game = currentGame();
        const hasBoard = !!(game && game.board && game.board.players);
        const attrName = (player.name || "").replace(/"/g, "&quot;");
        const photo = player.headshot
            ? `<img class="nrs-card__photo" src="${thumb(player.headshot)}" alt="" loading="lazy" onerror="this.remove()">`
            : "";
        const defLogoImg = meta.defLogo
            ? `<img class="nrs-card__photo nrs-card__photo--logo" src="${meta.defLogo}" alt="" loading="lazy">`
            : "";

        const lineChips = cols
            .filter((col) => lines[col.key] != null)
            .map((col) => `<span class="nrs-line-chip">${LINE_LABELS[col.key] || col.name} <b>${lines[col.key]}</b></span>`);
        if (lines.atd) lineChips.push(`<span class="nrs-line-chip nrs-line-chip--td">Anytime TD <b>${lines.atd}</b></span>`);
        const linesBox = lineChips.length
            ? `<div class="nrs-lines-box"><span class="nrs-lines-box__title">Best lines</span>${lineChips.join("")}</div>`
            : `<div class="nrs-lines-box nrs-lines-box--empty"><span class="nrs-lines-box__title">Best lines</span><span class="nrs-lines-box__none">Not posted yet</span></div>`;

        const noHistory = player.no_history || !(player.log || []).length;
        const span = seasonSpan(player.seasons);
        // averages cover his last `gp` games, which may reach into last season
        const gamesLabel = noHistory
            ? "No NFL games yet"
            : `Avg of last ${player.gp} game${player.gp === 1 ? "" : "s"}${span ? ` · ${span}` : ""}`;
        // A depth-chart starter with no games still belongs on the board -- the
        // defense side is exactly as useful for him as for a veteran.
        const playerBody = noHistory
            ? `<div class="nrs-no-history"><strong>No NFL games yet.</strong> ` +
              `He is ${pos}${rank} on the current depth chart, so he is on the board. ` +
              `What this defense has allowed to ${pos}${rank}s is on the right.</div>`
            : filterBarHtml("off", offFilter, meta.defAbbr, pos, cardKey) +
              `<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log">` +
              `<thead>${logHead}</thead><tbody>${playerRows}</tbody>` +
              `<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="3">Avg</td>${playerAvgCells}</tr>${trackRow}</tfoot>` +
              `</table></div>`;

        return (
            `<article class="nrs-matchup-card${noHistory ? " nrs-matchup-card--new" : ""}" data-card="${cardKey}">` +
            `<div class="nrs-mc-duo">` +
            `<div class="nrs-mc-panel nrs-mc-panel--player">` +
            `<header class="nrs-mc-panel__head">` +
            (hasBoard
                ? `<button type="button" class="nrs-profile-trigger" title="Open ${attrName}'s Game Board read"` +
                  ` data-profile-team="${meta.offAbbr}" data-profile-role="${pos}${rank}"` +
                  ` data-profile-pid="${player.player_id || ""}" data-profile-name="${attrName}">`
                : "") +
            `${photo}<div>` +
            `<span class="nrs-player-card__name">${player.name}<span class="nrs-depth-badge">${pos}${rank}</span></span>` +
            `<span class="nrs-player-card__meta">${gamesLabel}</span>` +
            `</div>${hasBoard ? "</button>" : ""}</header>` +
            playerBody +
            `</div>` +
            `<div class="nrs-mc-panel nrs-mc-panel--def">` +
            `<header class="nrs-mc-panel__head">${defLogoImg}<div>` +
            `<span class="nrs-player-card__name">${pos}s vs ${meta.defShort} Defense</span>` +
            `<span class="nrs-player-card__meta">what they allowed to ${pos}${rank}s each game</span>` +
            `</div></header>` +
            filterBarHtml("def", defFilter, meta.offAbbr, pos, cardKey) +
            `<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log">` +
            `<thead>${logHead}</thead><tbody>${defRows}</tbody>` +
            `<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="3">Avg</td>${defAvgCells}</tr></tfoot>` +
            `</table></div>` +
            `</div>` +
            `</div>` +
            linesBox +
            `</article>`
        );
    }

    // ── prop tracker ─────────────────────────────────────────────────────────
    // Saved props live in this browser only. Each entry carries its own expiry so
    // the list empties itself: a bet is no use once the game is long over, and an
    // NFL slate rolls over weekly, so pruning by "is this game still on the board"
    // would lose entries the moment the week advanced.
    const TRACK_KEY = "nrsTrackedProps.v1";
    const GAME_LENGTH_MS = 3.5 * 3600 * 1000;   // kickoff to final, generously
    const KEEP_AFTER_MS = 12 * 3600 * 1000;     // the owner's 12-hour window

    function trackLoad() {
        let raw = [];
        try {
            raw = JSON.parse(localStorage.getItem(TRACK_KEY) || "[]");
        } catch (err) {
            raw = [];
        }
        if (!Array.isArray(raw)) raw = [];
        const now = Date.now();
        const live = raw.filter((e) => e && typeof e.expires === "number" && e.expires > now);
        if (live.length !== raw.length) trackSave(live);
        return live;
    }

    function trackSave(list) {
        try {
            localStorage.setItem(TRACK_KEY, JSON.stringify(list));
        } catch (err) {
            /* private window or storage disabled: the tracker just will not persist */
        }
    }

    // Books post on a ladder, not on arbitrary decimals: yardage moves in fives,
    // counting stats in ones, touchdowns in halves. Offering the rungs a book
    // would actually have up beats a spinner you can type 37.3 into.
    // Every step is a whole number so each rung stays on a half. A 0.5 step off a
    // .5 base walks onto 1.0 and 2.0, and no book posts a whole-number line -- it
    // can push.
    const LINE_STEP = {
        pass_yds: 5, pass_att: 1, pass_cmp: 1, pass_td: 1, pass_int: 1,
        rush_yds: 5, rush_att: 1, rush_td: 1,
        tgt: 1, rec: 1, rec_yds: 5, rec_td: 1,
        long: 2, long_rush: 2, long_pass: 2, sacks: 1, td: 1, first_td: 1, last_td: 1,
        pass_rush_yds: 5, rush_rec_yds: 5, fpts_half: 1, fpts_ppr: 1,
    };
    const LINE_RUNGS = 4; // either side of the suggestion

    function lineLadder(key, suggested) {
        const step = LINE_STEP[key] || 0.5;
        const base = halfStep(suggested);
        const out = [];
        for (let i = -LINE_RUNGS; i <= LINE_RUNGS; i += 1) {
            const v = Number((base + i * step).toFixed(1));
            // belt and braces: a rung that is not on a half is not a real line
            if (v >= 0.5 && Math.abs(v % 1) === 0.5) out.push(v);
        }
        // A book line off a feed may not sit on our ladder; keep it selectable.
        if (suggested != null && !out.includes(Number(suggested))) out.push(Number(suggested));
        return [...new Set(out)].sort((a, b) => a - b);
    }

    function halfStep(value) {
        // Always land ON a half. Rounding to the nearest 0.5 let whole numbers
        // through -- a 1.8 average suggested "2", which no book offers because it
        // can push. floor + 0.5 keeps every suggestion a real line shape.
        const n = Number(value);
        if (value == null || Number.isNaN(n)) return 0.5;
        return Math.max(0.5, Math.floor(n) + 0.5);
    }

    function trackedIdSet() {
        return new Set(trackLoad().map((e) => e.id));
    }

    function trackExpiry(kickoff) {
        const t = kickoff ? Date.parse(kickoff) : NaN;
        // No parseable kickoff: keep it a day so it cannot linger forever.
        if (Number.isNaN(t)) return Date.now() + 24 * 3600 * 1000;
        return t + GAME_LENGTH_MS + KEEP_AFTER_MS;
    }

    function trackToggle(entry) {
        const list = trackLoad();
        const at = list.findIndex((e) => e.id === entry.id);
        if (at >= 0) list.splice(at, 1);
        else list.push(entry);
        trackSave(list);
        trackRender();
        return at < 0;
    }

    function trackRender() {
        const list = trackLoad();
        const count = el("nrsTrackCount");
        const openBtn = el("nrsTrackOpen");
        if (count) count.textContent = String(list.length);
        if (openBtn) openBtn.classList.toggle("is-empty", list.length === 0);
        const body = el("nrsTrackBody");
        if (!body) return;
        if (!list.length) {
            body.innerHTML =
                '<p class="nrs-track-empty">Nothing tracked yet. Hit <strong>Track</strong> on any player card.</p>';
        } else {
            const byGame = {};
            list.forEach((e) => (byGame[e.game] = byGame[e.game] || []).push(e));
            body.innerHTML = Object.keys(byGame)
                .map((game) => {
                    const rows = byGame[game]
                        .map((e) => {
                            const chips = (e.lines || [])
                                .map((l) => `<span class="nrs-track-chip">${l}</span>`)
                                .join("");
                            return (
                                `<div class="nrs-track-row">` +
                                `<span class="nrs-track-row__name">${e.name}</span>` +
                                `<span class="nrs-track-row__meta">${e.meta}</span>` +
                                `<span class="nrs-track-row__lines">${chips}</span>` +
                                `<button type="button" class="nrs-track-row__x" data-untrack="${e.id}" title="Remove">✕</button>` +
                                `</div>`
                            );
                        })
                        .join("");
                    return `<div class="nrs-track-game"><span class="nrs-track-game__title">${game}</span>${rows}</div>`;
                })
                .join("");
        }
        // keep the buttons on the cards in sync with the list
        // The market rows carry the line in their id, which the button cannot know
        // until it is clicked, so nothing to sync here -- the picker is rebuilt from
        // trackedIds on every matchup render.
    }

    function initTracker() {
        const openBtn = el("nrsTrackOpen");
        const panel = el("nrsTrackPanel");
        if (openBtn && panel) {
            openBtn.addEventListener("click", () => {
                const show = panel.hidden;
                panel.hidden = !show;
                openBtn.setAttribute("aria-expanded", show ? "true" : "false");
                // Re-render on open: trackLoad() is what drops expired entries, so
                // without this the sweep only ran on a page load and a tab left open
                // would keep showing bets whose games finished yesterday.
                if (show) trackRender();
            });
        }
        const clear = el("nrsTrackClear");
        if (clear) {
            clear.addEventListener("click", () => {
                trackSave([]);
                trackRender();
            });
        }
        if (panel) {
            panel.addEventListener("click", (e) => {
                const x = e.target.closest("[data-untrack]");
                if (!x) return;
                trackSave(trackLoad().filter((entry) => entry.id !== x.dataset.untrack));
                trackRender();
            });
        }
        el("nrsPosSections").addEventListener("click", (e) => {
            // O/U flips in place -- one button rather than a pair, because a stat
            // column is not wide enough for two and the state is obvious either way.
            const side = e.target.closest(".nrs-tc__side");
            if (side) {
                const over = side.dataset.tcSide === "over";
                side.dataset.tcSide = over ? "under" : "over";
                side.textContent = over ? "U" : "O";
                side.classList.toggle("is-under", over);
                return;
            }
            const add = e.target.closest(".nrs-tc__add");
            if (!add) return;
            const cell = add.closest(".nrs-tc");
            const input = cell.querySelector(".nrs-tc__line");
            const dir = cell.querySelector(".nrs-tc__side").dataset.tcSide;
            const line = input && input.value !== "" ? Number(input.value) : null;
            const market = cell.dataset.tcLabel;
            const now = trackToggle({
                // the line is part of the identity: O62.5 and O74.5 are two bets
                id: `${add.dataset.tcId}|${dir}|${line}`,
                name: add.dataset.trackName,
                meta: add.dataset.trackMeta,
                game: add.dataset.trackGame,
                market: market,
                side: dir,
                line: line,
                lines: [`${dir === "under" ? "U" : "O"}${line} ${market}`],
                expires: Number(add.dataset.trackExpires),
            });
            add.textContent = now ? "✓" : "+";
            cell.classList.toggle("is-on", now);
        });
        trackRender();
        // A tab can sit open for days. Sweep on a timer so entries disappear when
        // their 12 hours are up rather than waiting for the next reload, and again
        // whenever the tab is brought back to the front.
        setInterval(trackRender, 5 * 60 * 1000);
        document.addEventListener("visibilitychange", () => {
            if (!document.hidden) trackRender();
        });
    }

    // ── boot ──
    document.addEventListener("DOMContentLoaded", () => {
        if (location.protocol === "file:") return;
        initTheme();
        state.colPrefs = loadColPrefs();
        initColPicker();
        initBoard();
        initProfile();
        initSourceToggle();
        initControls();
        initTracker();
        const params = new URLSearchParams(location.search);
        const season = Number(params.get("season"));
        const week = Number(params.get("week"));
        if (params.get("view") || params.get("player")) {
            state.deepLink = { view: params.get("view"), player: params.get("player") };
        }
        if (SEASONS.includes(season)) {
            state.season = season;
            el("nrsSeason").value = String(season);
        }
        if (week >= 1 && week <= MAX_WEEK) {
            state.autoWeek = false;
            state.week = week;
            el("nrsWeek").value = String(week);
        }
        loadSlate();
    });
})();
