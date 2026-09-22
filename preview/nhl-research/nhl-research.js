/* Worst Pickz — NHL Matchup Research (BETA)
 * Skaters (left) vs what the opponent allows to that line slot (right).
 * Data: pre-built JSON from fetch-nhl-research-slate.py (NHL public API, free).
 *
 * Deliberately the NFL tab's twin: same `nrs-` DOM, same stylesheet, same
 * left/right log-vs-log read. Hockey differs in three ways and only three --
 * the slate is a DATE rather than a week, depth is decided by ICE TIME rather
 * than a published chart, and goalies get their own card shape.
 */
(function () {
    "use strict";

    const POSITIONS = ["C", "L", "R", "D", "G"];
    const POS_LABEL = { C: "Centers", L: "Left Wing", R: "Right Wing", D: "Defense", G: "Goalies" };

    /* Columns per position, in table order. Mirrors the NFL tab's model exactly:
       every column has a short header (`abbr`) and a full name for the settings
       panel; `on` is what a first visit shows.

       All of it is free data from NHL.com's own API: the summary report (goals,
       assists, points, shots, ice time, power play) and the realtime report
       (hits, blocks, takeaways, giveaways, missed shots, first goal).

       fmt: "pct" percent · "toi" mm:ss · "flag" 1/0 per game, a rate on average
       heat: false leaves a column uncoloured, for context that is not better or worse
       div: [a, b] is a / b (x100 for pct); worked out from stored totals, so an
            average is total over total rather than a mean of per-game ratios. */
    const col = (key, abbr, name, group, extra) =>
        Object.assign({ key, abbr, name, group, on: false }, extra);
    const G = {
        game: "Game", score: "Scoring", shot: "Shots", phys: "Physical",
        rate: "Hit rates", goal: "Goaltending",
    };

    const TOI = col("toi", "TOI", "Time on ice", G.game, { fmt: "toi", on: true });
    const PM = col("pm", "+/-", "Plus / minus", G.game, { heat: false });
    const PIM = col("pim", "PIM", "Penalty minutes", G.phys, { lowerBetter: true });

    const SCORING = [
        col("g", "G", "Goals", G.score, { on: true }),
        col("a", "A", "Assists", G.score, { on: true }),
        col("p", "P", "Points", G.score, { on: true }),
        col("pp_p", "PPP", "Power play points", G.score, { on: true }),
        col("pp_g", "PPG", "Power play goals", G.score),
        col("sh_p", "SHP", "Shorthanded points", G.score),
        col("ev_p", "EVP", "Even strength points", G.score),
        col("gwg", "GWG", "Game winning goals", G.score),
        col("en_g", "EN", "Empty net goals", G.score),
        col("first_g", "1ST G", "First goal of the game", G.score, { fmt: "flag" }),
    ];
    const SHOTS = [
        col("sog", "SOG", "Shots on goal", G.shot, { on: true }),
        col("satt", "ATT", "Total shot attempts", G.shot),
        col("msog", "MISS", "Missed shots", G.shot, { lowerBetter: true }),
        col("sh_pct", "SH%", "Shooting %", G.shot, { fmt: "pct", div: ["g", "sog"] }),
    ];
    const PHYSICAL = [
        col("blk", "BLK", "Blocked shots", G.phys),
        col("hits", "HIT", "Hits", G.phys),
        col("tk", "TK", "Takeaways", G.phys),
        col("gv", "GV", "Giveaways", G.phys, { lowerBetter: true }),
        PIM,
    ];
    const RATES = [
        col("sog_1", "1+SOG", "Games with 1+ shot", G.rate, { fmt: "flag" }),
        col("sog_2", "2+SOG", "Games with 2+ shots", G.rate, { fmt: "flag" }),
        col("sog_3", "3+SOG", "Games with 3+ shots", G.rate, { fmt: "flag" }),
        col("sog_4", "4+SOG", "Games with 4+ shots", G.rate, { fmt: "flag" }),
        col("pts_1", "1+P", "Games with a point", G.rate, { fmt: "flag" }),
        col("pts_2", "2+P", "Games with 2+ points", G.rate, { fmt: "flag" }),
        col("g_1", "1+G", "Games with a goal", G.rate, { fmt: "flag" }),
        col("a_1", "1+A", "Games with an assist", G.rate, { fmt: "flag" }),
        col("blk_1", "1+BLK", "Games with a block", G.rate, { fmt: "flag" }),
        col("blk_2", "2+BLK", "Games with 2+ blocks", G.rate, { fmt: "flag" }),
        col("hits_1", "1+HIT", "Games with a hit", G.rate, { fmt: "flag" }),
        col("hits_3", "3+HIT", "Games with 3+ hits", G.rate, { fmt: "flag" }),
    ];

    const FORWARD_COLS = [TOI, PM].concat(SCORING, SHOTS, PHYSICAL, RATES);
    // A defenseman is bet on blocks and shots far more than goals, so his card
    // opens on those instead of on a goal total he clears twice a month.
    const DEFENSE_COLS = [
        Object.assign({}, TOI, { on: true }), PM,
        col("g", "G", "Goals", G.score),
        col("a", "A", "Assists", G.score, { on: true }),
        col("p", "P", "Points", G.score, { on: true }),
        col("pp_p", "PPP", "Power play points", G.score),
        col("pp_g", "PPG", "Power play goals", G.score),
        col("sh_p", "SHP", "Shorthanded points", G.score),
        col("ev_p", "EVP", "Even strength points", G.score),
        col("gwg", "GWG", "Game winning goals", G.score),
        col("en_g", "EN", "Empty net goals", G.score),
        col("first_g", "1ST G", "First goal of the game", G.score, { fmt: "flag" }),
        col("sog", "SOG", "Shots on goal", G.shot, { on: true }),
        col("satt", "ATT", "Total shot attempts", G.shot),
        col("msog", "MISS", "Missed shots", G.shot, { lowerBetter: true }),
        col("sh_pct", "SH%", "Shooting %", G.shot, { fmt: "pct", div: ["g", "sog"] }),
        col("blk", "BLK", "Blocked shots", G.phys, { on: true }),
        col("hits", "HIT", "Hits", G.phys, { on: true }),
        col("tk", "TK", "Takeaways", G.phys),
        col("gv", "GV", "Giveaways", G.phys, { lowerBetter: true }),
        PIM,
    ].concat(RATES);

    const GOALIE_COLS = [
        col("sv", "SV", "Saves", G.goal, { on: true }),
        col("sa", "SA", "Shots against", G.goal, { on: true }),
        col("ga", "GA", "Goals against", G.goal, { on: true, lowerBetter: true }),
        // total saves over total shots against -- averaging each night's own
        // percentage overweights a 4-shot relief appearance against a 40-shot start
        col("sv_pct", "SV%", "Save percentage", G.goal, { on: true, fmt: "pct3", div: ["sv", "sa"] }),
        col("win", "W", "Wins", G.goal, { on: true, fmt: "flag" }),
        col("so", "SO", "Shutouts", G.goal, { fmt: "flag" }),
        col("start", "GS", "Games started", G.goal, { fmt: "flag" }),
        Object.assign({}, TOI, { on: false }),
        col("sv_25", "25+SV", "Games with 25+ saves", G.rate, { fmt: "flag" }),
        col("sv_30", "30+SV", "Games with 30+ saves", G.rate, { fmt: "flag", on: true }),
        col("sv_35", "35+SV", "Games with 35+ saves", G.rate, { fmt: "flag" }),
    ];

    const POS_COLUMNS = {
        C: FORWARD_COLS, L: FORWARD_COLS, R: FORWARD_COLS,
        D: DEFENSE_COLS, G: GOALIE_COLS,
    };
    const GROUP_ORDER = {
        C: [G.game, G.score, G.shot, G.phys, G.rate],
        L: [G.game, G.score, G.shot, G.phys, G.rate],
        R: [G.game, G.score, G.shot, G.phys, G.rate],
        D: [G.game, G.score, G.shot, G.phys, G.rate],
        G: [G.goal, G.rate],
    };

    // Markets a book actually posts. Rates and context columns are not tracked:
    // nobody offers "games with 2+ blocks" as a line, they offer the block itself.
    const MARKETS = new Set(["g", "a", "p", "sog", "blk", "hits", "pp_p", "sv", "ga"]);
    const LINE_LABELS = {
        g: "Goals", a: "Assists", p: "Points", sog: "Shots on goal",
        blk: "Blocked shots", hits: "Hits", pp_p: "Power play points",
        sv: "Saves", ga: "Goals against", atgs: "Anytime goal",
    };

    /* How big an edge has to be before a cell colours, per stat -- roughly one
       game's worth of normal variation in that stat.

       These are deliberately wider than the NFL tab's. Football stats are large
       and continuous (68 rushing yards against an average of 54); hockey's are
       small integers, and a single goal against an average of 0.3 is already
       six times a football-sized threshold. Tuned tight, every cell in the log
       pinned to full green or full red and the colour stopped carrying any
       information. At this scale a quiet night stays neutral and only a real
       outlier saturates. */
    const THRESHOLDS = {
        g: 0.45, a: 0.55, p: 0.8, sog: 1.3, satt: 2.0, msog: 1.0,
        blk: 1.1, hits: 1.4, tk: 0.8, gv: 0.9, pim: 1.5,
        pp_p: 0.45, pp_g: 0.3, sh_p: 0.2, ev_p: 0.7, gwg: 0.2, en_g: 0.2,
        toi: 180, sv: 6.0, sa: 6.5, ga: 1.1, sv_pct: 0.035,
        sh_pct: 9.0, pm: 1.2,
    };

    const COLS_STORAGE_KEY = "worstpickz-nhl-cols.v1";
    const TRACK_KEY = "nhlTrackedProps.v1";
    const DEFAULT_FILTER = "l10";
    const GAME_LENGTH_MS = 3.25 * 3600 * 1000;  // puck drop to final, generously
    const KEEP_AFTER_MS = 12 * 3600 * 1000;     // the owner's 12-hour window

    const state = {
        date: "",
        slate: null,
        gameId: "",
        side: "away",
        leagueAvg: null,
        logFilter: { off: DEFAULT_FILTER, def: DEFAULT_FILTER },
        colSetPos: "C",
        cols: {},
    };

    const el = (id) => document.getElementById(id);
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g,
        (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    /* ── theme ─────────────────────────────────────────────────────────────── */
    function initTheme() {
        const toggle = el("nrsThemeToggle");
        if (!toggle) return;
        const apply = (light) => {
            document.documentElement.classList.toggle("theme-light", light);
            toggle.textContent = light ? "🌙" : "☀️";
            toggle.setAttribute("aria-pressed", String(light));
        };
        let light = false;
        try { light = localStorage.getItem("worstpickz-theme") === "light"; } catch (e) {}
        apply(light);
        toggle.addEventListener("click", () => {
            light = !document.documentElement.classList.contains("theme-light");
            apply(light);
            try { localStorage.setItem("worstpickz-theme", light ? "light" : "dark"); } catch (e) {}
        });
    }

    /* ── column preferences ────────────────────────────────────────────────── */
    function loadColPrefs() {
        let saved = {};
        try { saved = JSON.parse(localStorage.getItem(COLS_STORAGE_KEY) || "{}") || {}; } catch (e) {}
        POSITIONS.forEach((pos) => {
            state.cols[pos] = Array.isArray(saved[pos]) && saved[pos].length
                ? saved[pos]
                : defaultCols(pos);
        });
    }
    function saveColPrefs() {
        try { localStorage.setItem(COLS_STORAGE_KEY, JSON.stringify(state.cols)); } catch (e) {}
    }
    function defaultCols(pos) {
        return (POS_COLUMNS[pos] || []).filter((c) => c.on).map((c) => c.key);
    }
    function visibleCols(pos) {
        const want = new Set(state.cols[pos] || defaultCols(pos));
        return (POS_COLUMNS[pos] || []).filter((c) => want.has(c.key));
    }

    /* ── stat plumbing ─────────────────────────────────────────────────────── */
    /* Threshold columns ("2+ shots") are a 1/0 in a single game and a hit rate
       as an average. The average is stored; the per-game flag is not, because
       a dozen of them on every log row was more than half the slate's bytes.
       Each one is recomputed here from the count sitting next to it. */
    const FLAG_FROM = {
        sog_1: ["sog", 1], sog_2: ["sog", 2], sog_3: ["sog", 3], sog_4: ["sog", 4],
        pts_1: ["p", 1], pts_2: ["p", 2], g_1: ["g", 1], a_1: ["a", 1],
        blk_1: ["blk", 1], blk_2: ["blk", 2], hits_1: ["hits", 1], hits_3: ["hits", 3],
        sv_25: ["sv", 25], sv_30: ["sv", 30], sv_35: ["sv", 35],
    };

    // `perGame` is true for a single game's row, where a derived rate has to be
    // worked out from that game's own counts rather than off season totals.
    function colVal(stats, c, perGame) {
        if (!stats || !c) return null;
        if (perGame && FLAG_FROM[c.key] !== undefined && stats[c.key] == null) {
            const [from, cut] = FLAG_FROM[c.key];
            return Number(stats[from] || 0) >= cut ? 1 : 0;
        }
        if (c.div) {
            const a = Number(stats[c.div[0]] || 0);
            const b = Number(stats[c.div[1]] || 0);
            if (!b) return null;
            return c.fmt === "pct" ? (a / b) * 100 : a / b;
        }
        const raw = stats[c.key];
        return raw == null ? (perGame ? 0 : null) : Number(raw);
    }

    function fmtStat(val, c, avg) {
        if (val == null) return "—";
        const fmt = c && c.fmt;
        if (fmt === "toi") {
            const s = Math.round(val);
            return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
        }
        if (fmt === "pct") return `${Math.round(val)}%`;
        if (fmt === "pct3") return val ? val.toFixed(3).replace(/^0/, "") : "—";
        if (fmt === "flag") {
            if (avg) return `${Math.round(val * 100)}%`;
            return val >= 1 ? "✓" : "–";
        }
        if (c && c.key === "pm" && val > 0) return `+${Math.round(val * 10) / 10}`;
        return Number.isInteger(val) ? String(val) : val.toFixed(1);
    }

    function heatAttr(val, ref, c) {
        if (val == null || ref == null || (c && c.heat === false)) return "";
        const threshold = THRESHOLDS[c.key] != null ? THRESHOLDS[c.key] : 0.5;
        let edge = val - ref;
        if (c.lowerBetter) edge = -edge;
        if (Math.abs(edge) <= threshold * 0.5) return "";
        // full saturation at 6x threshold; sqrt ramp keeps mid edges visible
        const mag = Math.min(Math.abs(edge) / (threshold * 6), 1);
        const alpha = (0.14 + 0.56 * Math.sqrt(mag)).toFixed(2);
        const rgb = edge > 0 ? "34, 197, 94" : "239, 68, 68";
        return ` style="background:rgba(${rgb},${alpha})"`;
    }

    const TEAM_LOGO = (abbr) =>
        abbr ? `https://assets.nhle.com/logos/nhl/svg/${abbr}_light.svg` : "";

    /* ── dates ─────────────────────────────────────────────────────────────── */
    function todayISO() {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    }
    function shiftDate(iso, days) {
        const [y, m, d] = iso.split("-").map(Number);
        const dt = new Date(Date.UTC(y, m - 1, d));
        dt.setUTCDate(dt.getUTCDate() + days);
        return dt.toISOString().slice(0, 10);
    }
    // "Oct 7" for a game in the season being viewed, "Oct 7 '25" when the log
    // reaches back past it. A hockey log spans two seasons for most of the year.
    function dateLabel(g) {
        const iso = g && g.date;
        if (!iso) return "—";
        const [y, m, d] = iso.split("-").map(Number);
        const mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1];
        const seasonStartYear = state.slate ? Math.floor(state.slate.stats_season / 10000) : y;
        const sameSeason = y === seasonStartYear || y === seasonStartYear + 1;
        return `${mon} ${d}${sameSeason ? "" : ` '${String(y).slice(-2)}`}`;
    }
    function seasonSpan(seasons) {
        const s = (seasons || []).filter(Boolean);
        if (!s.length) return "";
        const yy = (id) => `'${String(id).slice(2, 4)}–'${String(id).slice(-2)}`;
        return s.length > 1 ? `${yy(s[0])} → ${yy(s[s.length - 1])}` : yy(s[0]);
    }
    function formatPuckDrop(iso) {
        if (!iso) return "";
        const d = new Date(iso);
        if (isNaN(d)) return "";
        return d.toLocaleString(undefined, {
            weekday: "short", month: "short", day: "numeric",
            hour: "numeric", minute: "2-digit",
        });
    }

    /* ── loading ───────────────────────────────────────────────────────────── */
    function setStatus(message, kind) {
        const node = el("nrsStatus");
        if (!node) return;
        node.hidden = !message;
        node.textContent = message || "";
        node.className = "nrs-status" + (kind ? ` nrs-status--${kind}` : "");
    }

    async function loadSlate(bustCache) {
        const date = state.date;
        setStatus(`Loading ${date}…`);
        const url = `../data/nhl-research-${date}.json${bustCache ? `?t=${Date.now()}` : ""}`;
        let payload;
        try {
            const resp = await fetch(url, { cache: bustCache ? "reload" : "default" });
            if (!resp.ok) throw new Error(String(resp.status));
            payload = await resp.json();
        } catch (err) {
            state.slate = null;
            el("nrsGames").innerHTML = "";
            el("nrsMatchupSection").hidden = true;
            setStatus(
                `No slate built for ${date}. Run:  python fetch-nhl-research-slate.py --date ${date}`,
                "warn",
            );
            return;
        }
        state.slate = payload;
        state.leagueAvg = payload.league || null;

        const games = payload.games || [];
        // keep the selected game across a refresh when it is still on the slate
        if (!games.some((g) => g.id === state.gameId)) {
            state.gameId = games.length ? games[0].id : "";
        }

        const stamp = payload.fetched_at
            ? new Date(payload.fetched_at).toLocaleString(undefined,
                { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })
            : "";
        el("nrsLastUpdated").textContent = stamp ? `Built ${stamp}` : "";

        const badge = el("nrsSourceBadge");
        if (badge) {
            const statsSeason = payload.stats_season;
            const schedSeason = payload.season;
            const label = (id) => `${String(id).slice(2, 4)}–${String(id).slice(-2)}`;
            badge.hidden = false;
            badge.textContent = statsSeason === schedSeason
                ? `${label(statsSeason)} season`
                : `${label(statsSeason)} stats · ${label(schedSeason)} rosters`;
            badge.title = statsSeason === schedSeason
                ? "Averages and allowed tables read this season."
                : "This season has no games played yet, so the numbers are last "
                  + "season's production on this season's rosters.";
        }

        const note = el("nrsSeasonNote");
        if (note && !games.length) {
            note.textContent = "No NHL games scheduled on this date.";
        } else if (note) {
            note.textContent = "Skater vs what the opponent allows to that line slot — "
                + "green means the player beats what that defense gives up.";
        }

        setStatus(games.length ? "" : `No NHL games on ${date}.`);
        renderGames();
        renderMatchup();
    }

    /* ── slate strip ───────────────────────────────────────────────────────── */
    function currentGame() {
        const games = (state.slate && state.slate.games) || [];
        return games.find((g) => g.id === state.gameId) || games[0] || null;
    }

    function renderGames() {
        const host = el("nrsGames");
        const games = (state.slate && state.slate.games) || [];
        if (!games.length) { host.innerHTML = ""; return; }
        host.innerHTML = games.map((g) => {
            const on = g.id === state.gameId;
            const logo = (abbr) => {
                const src = TEAM_LOGO(abbr);
                return src ? `<img src="${src}" alt="" loading="lazy" onerror="this.remove()">` : "";
            };
            const time = g.kickoff
                ? new Date(g.kickoff).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })
                : "";
            return (
                `<button type="button" class="nrs-game-pill${on ? " is-active" : ""}" data-game="${esc(g.id)}">` +
                `<span class="nrs-game-pill__teams">${logo(g.away)}${esc(g.away)} @ ` +
                `${logo(g.home)}${esc(g.home)}</span>` +
                `<span class="nrs-game-pill__meta">${esc(time)}${g.game_type_label === "PRE" ? " · PRE" : ""}</span>` +
                `</button>`
            );
        }).join("");
    }

    /* ── log filtering ─────────────────────────────────────────────────────── */
    function filterLog(log, oppAbbr, mode) {
        const rows = (log || []).slice().sort((a, b) => (a.date < b.date ? 1 : -1));
        if (mode === "vs") return rows.filter((r) => r.opp === oppAbbr);
        if (mode === "l5") return rows.slice(0, 5);
        if (mode === "l10") return rows.slice(0, 10);
        if (mode === "l20") return rows.slice(0, 20);
        return rows;
    }

    function filterBarHtml(sideKey, active, oppAbbr, cardKey) {
        const opts = [
            ["l5", "L5"], ["l10", "L10"], ["l20", "L20"],
            ["all", "All"], ["vs", `vs ${oppAbbr}`],
        ];
        const buttons = opts.map(([key, label]) =>
            `<button type="button" data-filter="${key}"` +
            `${key === active ? ' class="is-active"' : ""}>${esc(label)}</button>`).join("");
        return `<div class="nrs-card-filterbar">` +
            `<div class="nrs-log-filter nrs-log-filter--card" role="group" aria-label="Game log filter" ` +
            `data-filter-side="${sideKey}" data-card="${esc(cardKey)}">${buttons}</div></div>`;
    }

    /* ── the matchup: every player stacked, player left | opponent right ────── */
    function skaterBlock(game, side) {
        return (side === "away" ? game.away_skaters : game.home_skaters) || {};
    }
    function allowedBlock(game, side) {
        return (side === "away" ? game.away_allowed : game.home_allowed) || {};
    }

    function renderMatchup() {
        const game = currentGame();
        const section = el("nrsMatchupSection");
        if (!game) { section.hidden = true; return; }
        section.hidden = false;

        const isAway = state.side === "away";
        const offName = isAway ? game.away_name : game.home_name;
        const offAbbr = isAway ? game.away : game.home;
        const defAbbr = isAway ? game.home : game.away;
        const defShort = (isAway ? game.home_short : game.away_short) || defAbbr;
        const offLogo = TEAM_LOGO(offAbbr);
        const defLogo = TEAM_LOGO(defAbbr);
        const skaters = skaterBlock(game, isAway ? "away" : "home");
        const allowed = allowedBlock(game, isAway ? "home" : "away");

        el("nrsMatchupTitle").textContent = `${game.away_name} @ ${game.home_name}`;
        const bits = [formatPuckDrop(game.kickoff)];
        if (game.venue) bits.push(game.venue);
        if (game.away_record && game.home_record) {
            bits.push(`${game.away} ${game.away_record} · ${game.home} ${game.home_record}`);
        }
        if (game.game_type_label === "PRE") bits.push("Preseason");
        el("nrsMatchupSub").textContent = bits.filter(Boolean).join(" · ");

        el("nrsSideAway").classList.toggle("is-active", isAway);
        el("nrsSideHome").classList.toggle("is-active", !isAway);
        el("nrsSideAway").textContent = `${game.away} SKATERS`;
        el("nrsSideHome").textContent = `${game.home} SKATERS`;

        const meta = {
            offName, offLogo, defShort, defLogo, offAbbr, defAbbr,
            gameId: game.id,
            kickoff: game.kickoff,
            gameLabel: `${game.away} @ ${game.home}`,
        };
        const trackedIds = trackedIdSet();

        const cards = POSITIONS.flatMap((pos) => {
            const cols = visibleCols(pos);
            const block = allowed[pos] || { overall: null, ranks: {} };
            return (skaters[pos] || []).map((p) => playerCardHtml(pos, cols, p, block, meta, trackedIds));
        }).join("");

        const count = POSITIONS.reduce((n, pos) => n + ((skaters[pos] || []).length), 0);
        const head =
            `<header class="nrs-lineup-head">` +
            (offLogo ? `<img src="${offLogo}" alt="" loading="lazy" onerror="this.remove()">` : "") +
            `<div><h3>${esc(offAbbr)} Lineup</h3>` +
            `<span>${count} players ranked by ice time · C1–4 · LW1–4 · RW1–4 · D1–6 · G1–2</span></div>` +
            `</header>`;

        el("nrsPosSections").innerHTML =
            allowedOverviewHtml(allowed, meta) + head +
            `<div class="nrs-player-grid">${cards ||
                `<p class="nrs-empty">No player data for ${esc(offName)}.</p>`}</div>`;
    }

    // top strip: what this opponent allows per game to each position group
    function allowedOverviewHtml(allowed, meta) {
        const logo = meta.defLogo
            ? `<img class="nrs-def-overview__logo" src="${esc(meta.defLogo)}" alt="" loading="lazy" onerror="this.remove()">`
            : "";
        const cards = POSITIONS.map((pos) => {
            const node = allowed[pos] || {};
            const overall = node.overall;
            if (!overall) return "";
            const league = leagueRow(pos, null);
            const rows = visibleCols(pos).map((c) => {
                const val = colVal(overall.stats, c);
                return `<tr><td class="nrs-stat-label">${esc(c.name)}</td>` +
                    `<td class="nrs-cell"${heatAttr(val, colVal(league, c), c)}>${fmtStat(val, c, true)}</td></tr>`;
            }).join("");
            return `<article class="nrs-def-card">` +
                `<header class="nrs-def-card__head">vs all ${esc(pos === "G" ? "goalies" : pos + "s")}</header>` +
                `<table class="nrs-table nrs-table--down"><tbody>${rows}</tbody></table>` +
                `</article>`;
        }).join("");
        if (!cards) return "";
        return `<section class="nrs-def-overview">` +
            `<header class="nrs-def-overview__head">${logo}<div>` +
            `<span class="nrs-def-overview__title">${esc(meta.defShort)} — allows per game</span>` +
            `<span class="nrs-def-overview__sub">Combined production allowed to each position group · ` +
            `green = gives up more than an average club</span>` +
            `</div></header>` +
            `<div class="nrs-def-grid">${cards}</div></section>`;
    }

    /* The league line for a position, at a line slot when one is asked for.
       Shaped like the per-team tables -- { overall, ranks } -- so a slot that no
       club has faced often enough falls back to the position's overall line
       rather than to nothing. */
    function leagueRow(pos, rank) {
        const node = (state.leagueAvg || {})[pos];
        if (!node) return null;
        if (rank != null) {
            const at = (node.ranks || {})[String(rank)];
            if (at) return at;
        }
        return node.overall || null;
    }

    // the allowed row for this player's line slot, falling back to the overall
    // table when a team has not faced that deep a slot enough times
    function allowedForRank(block, rank) {
        const ranks = block.ranks || {};
        const exact = ranks[String(rank)];
        if (exact && exact.gp) return exact.stats;
        const overall = block.overall;
        return overall ? overall.stats : null;
    }

    function playerCardHtml(pos, cols, player, block, meta, trackedIds) {
        const rank = player.rank;
        const allowedRow = allowedForRank(block, rank);
        const league = leagueRow(pos, rank);
        const lines = player.lines || {};
        const isGoalie = pos === "G";

        const cardKey = `${pos}${rank}-${String(player.name || "").replace(/[^a-zA-Z0-9]/g, "")}`;
        const offFilter = state.logFilter.off || DEFAULT_FILTER;
        const defFilter = state.logFilter.def || DEFAULT_FILTER;

        const playerLog = filterLog(player.log || [], meta.defAbbr, offFilter);
        const rankNode = (block.ranks || {})[String(rank)] || {};
        const defLog = filterLog(rankNode.log || [], meta.offAbbr, defFilter);

        const statHead = cols.map((c) => `<th title="${esc(c.name)}">${esc(c.abbr)}</th>`).join("");
        const logHead = `<tr><th>Date</th><th class="nrs-th-opp">Opp</th>${statHead}</tr>`;

        const oppCell = (g) => {
            const src = TEAM_LOGO(g.opp);
            const img = src ? `<img src="${src}" alt="" loading="lazy" onerror="this.remove()">` : "";
            return `<span class="nrs-opp">${g.ha === "@" ? "@" : "vs"} ${img}${esc(g.opp)}</span>`;
        };

        // ── left: the player's game log, each game vs his own average ──
        const playerRows = playerLog.map((g) => {
            const cells = cols.map((c) => {
                const val = colVal(g.stats, c, true);
                const avg = colVal(player.stats, c);
                return `<td class="nrs-cell${c.fmt === "toi" ? " nrs-cell--toi" : ""}"${heatAttr(val, avg, c)}>${fmtStat(val, c)}</td>`;
            }).join("");
            return `<tr><td class="nrs-log-week">${esc(dateLabel(g))}</td>` +
                `<td class="nrs-log-opp">${oppCell(g)}</td>${cells}</tr>`;
        }).join("") ||
            `<tr><td colspan="${cols.length + 2}" class="nrs-log-none">No games match this filter.</td></tr>`;

        // avg row: his average coloured vs what this opponent allows (the matchup)
        const playerAvgCells = cols.map((c) => {
            const val = colVal(player.stats, c);
            return `<td class="nrs-cell"${heatAttr(val, colVal(allowedRow, c), c)}>${fmtStat(val, c, true)}</td>`;
        }).join("");

        // ── right: what the opponent allowed to this slot, vs the league ──
        const defRows = defLog.map((g) => {
            const cells = cols.map((c) => {
                const val = colVal(g.stats, c, true);
                return `<td class="nrs-cell${c.fmt === "toi" ? " nrs-cell--toi" : ""}"${heatAttr(val, colVal(league, c), c)}>${fmtStat(val, c)}</td>`;
            }).join("");
            return `<tr><td class="nrs-log-week">${esc(dateLabel(g))}</td>` +
                `<td class="nrs-log-opp" title="${esc(g.who || "")}">${oppCell(g)}</td>${cells}</tr>`;
        }).join("") ||
            `<tr><td colspan="${cols.length + 2}" class="nrs-log-none">No games match this filter.</td></tr>`;

        const defAvgCells = cols.map((c) => {
            const val = colVal(allowedRow, c);
            return `<td class="nrs-cell"${heatAttr(val, colVal(league, c), c)}>${fmtStat(val, c, true)}</td>`;
        }).join("");

        // ── the track row: each control sits under the column it refers to ──
        const baseId = `${state.date}-${meta.gameId || ""}-${cardKey}`;
        const trackExpires = trackExpiry(meta.kickoff);
        const trackAttrs =
            ` data-track-name="${esc(player.name)}"` +
            ` data-track-meta="${esc(`${pos}${rank} · ${meta.offAbbr} vs ${meta.defAbbr}`)}"` +
            ` data-track-game="${esc(meta.gameLabel)}"` +
            ` data-track-expires="${trackExpires}"`;

        const trackCells = cols.map((c) => {
            if (!MARKETS.has(c.key)) return `<td class="nrs-tc nrs-tc--none" aria-hidden="true"></td>`;
            const label = LINE_LABELS[c.key] || c.name;
            const book = lines[c.key];
            const suggested = book != null ? book : halfStep(colVal(player.stats, c));
            const id = `${baseId}|${c.key}`;
            const on = [...trackedIds].some((t) => t.startsWith(`${id}|`));
            return `<td class="nrs-tc${on ? " is-on" : ""}" data-tc-key="${esc(c.key)}" data-tc-label="${esc(label)}">` +
                `<div class="nrs-tc__wrap">` +
                `<button type="button" class="nrs-tc__side" data-tc-side="over" title="Over / Under">O</button>` +
                `<select class="nrs-tc__line" aria-label="${esc(label)} line for ${esc(player.name)}"` +
                `${book != null ? ' data-book="1"' : ""}>` +
                lineLadder(c.key, suggested).map((v) =>
                    `<option value="${v}"${v === Number(suggested) ? " selected" : ""}>${v}</option>`).join("") +
                `</select>` +
                `<button type="button" class="nrs-tc__add" data-tc-id="${esc(id)}"${trackAttrs} ` +
                `aria-label="Track ${esc(label)} for ${esc(player.name)}" title="Track this prop">` +
                `${on ? "✓" : "+"}</button></div></td>`;
        }).join("");
        const trackRow = `<tr class="nrs-track-row-cells">` +
            `<td class="nrs-log-week nrs-tc__label" colspan="2">Track</td>${trackCells}</tr>`;

        const photo = player.headshot
            ? `<img class="nrs-card__photo" src="${esc(player.headshot)}" alt="" loading="lazy" onerror="this.remove()">`
            : "";
        const defLogoImg = meta.defLogo
            ? `<img class="nrs-card__photo nrs-card__photo--logo" src="${esc(meta.defLogo)}" alt="" loading="lazy" onerror="this.remove()">`
            : "";

        const lineChips = cols.filter((c) => lines[c.key] != null)
            .map((c) => `<span class="nrs-line-chip">${esc(LINE_LABELS[c.key] || c.name)} <b>${esc(lines[c.key])}</b></span>`);
        if (lines.atgs) {
            lineChips.push(`<span class="nrs-line-chip nrs-line-chip--td">Anytime Goal <b>${esc(lines.atgs)}</b></span>`);
        }
        const linesBox = lineChips.length
            ? `<div class="nrs-lines-box"><span class="nrs-lines-box__title">Best lines</span>${lineChips.join("")}</div>`
            : `<div class="nrs-lines-box nrs-lines-box--empty"><span class="nrs-lines-box__title">Best lines</span>` +
              `<span class="nrs-lines-box__none">Not posted yet</span></div>`;

        const noHistory = !(player.log || []).length;
        const span = seasonSpan(player.seasons);
        const gamesLabel = noHistory
            ? "No NHL games yet"
            : `Avg of last ${player.gp} game${player.gp === 1 ? "" : "s"}${span ? ` · ${span}` : ""}`;

        const slotName = isGoalie
            ? `Goalies vs ${meta.defShort}`
            : `${pos}${rank}s vs ${meta.defShort}`;
        const slotNote = isGoalie
            ? "what shooters did to them each game"
            : `what they allowed to ${pos}${rank}s each game`;

        const playerBody = noHistory
            ? `<div class="nrs-no-history"><strong>No NHL games yet.</strong> ` +
              `He is ${pos}${rank} by ice time, so he is on the board. ` +
              `What this opponent allows to ${pos}${rank}s is on the right.</div>`
            : filterBarHtml("off", offFilter, meta.defAbbr, cardKey) +
              `<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log">` +
              `<thead>${logHead}</thead><tbody>${playerRows}</tbody>` +
              `<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="2">Avg</td>${playerAvgCells}</tr>` +
              `${trackRow}</tfoot></table></div>`;

        return (
            `<article class="nrs-matchup-card${noHistory ? " nrs-matchup-card--new" : ""}` +
            `${isGoalie ? " nrs-matchup-card--goalie" : ""}" data-card="${esc(cardKey)}">` +
            `<div class="nrs-mc-duo">` +
            `<div class="nrs-mc-panel nrs-mc-panel--player">` +
            `<header class="nrs-mc-panel__head">${photo}<div>` +
            `<span class="nrs-player-card__name">${esc(player.name)}` +
            `<span class="nrs-depth-badge" data-pos="${esc(pos)}">${esc(pos)}${rank}</span></span>` +
            `<span class="nrs-player-card__meta">${esc(gamesLabel)}</span>` +
            `</div></header>` + playerBody + `</div>` +
            `<div class="nrs-mc-panel nrs-mc-panel--def">` +
            `<header class="nrs-mc-panel__head">${defLogoImg}<div>` +
            `<span class="nrs-player-card__name">${esc(slotName)}</span>` +
            `<span class="nrs-player-card__meta">${esc(slotNote)}</span>` +
            `</div></header>` +
            filterBarHtml("def", defFilter, meta.offAbbr, cardKey) +
            `<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log">` +
            `<thead>${logHead}</thead><tbody>${defRows}</tbody>` +
            `<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="2">Avg</td>${defAvgCells}</tr></tfoot>` +
            `</table></div></div></div>` + linesBox + `</article>`
        );
    }

    /* ── prop tracker ──────────────────────────────────────────────────────────
       Saved props live in this browser only. Each entry carries its own expiry so
       the list empties itself twelve hours after the game ends -- pruning by "is
       this game still on the board" would drop entries the moment the slate
       rolled to tomorrow, and a hockey slate rolls every single day. */
    const LINE_STEP = {
        g: 1, a: 1, p: 1, sog: 1, blk: 1, hits: 1, pp_p: 1, sv: 1, ga: 1,
    };
    function halfStep(val) {
        const n = Number(val || 0);
        return Math.max(0.5, Math.round(n * 2) / 2 || 0.5);
    }
    function lineLadder(key, centre) {
        const step = LINE_STEP[key] || 1;
        const base = halfStep(centre);
        const out = [];
        for (let i = -3; i <= 4; i += 1) {
            const v = base + i * step;
            if (v > 0) out.push(Math.round(v * 2) / 2);
        }
        return [...new Set(out)].sort((a, b) => a - b);
    }
    function trackExpiry(kickoff) {
        const t = kickoff ? Date.parse(kickoff) : NaN;
        const base = isNaN(t) ? Date.now() : t;
        return base + GAME_LENGTH_MS + KEEP_AFTER_MS;
    }
    function trackLoad() {
        let raw = [];
        try { raw = JSON.parse(localStorage.getItem(TRACK_KEY) || "[]"); } catch (e) { raw = []; }
        if (!Array.isArray(raw)) raw = [];
        const now = Date.now();
        const live = raw.filter((e) => e && typeof e.expires === "number" && e.expires > now);
        if (live.length !== raw.length) trackSave(live);
        return live;
    }
    function trackSave(list) {
        try { localStorage.setItem(TRACK_KEY, JSON.stringify(list)); } catch (e) {
            /* private window or storage disabled: the tracker just will not persist */
        }
    }
    function trackedIdSet() {
        return new Set(trackLoad().map((e) => e.id));
    }
    function renderTracker() {
        const list = trackLoad();
        el("nrsTrackCount").textContent = String(list.length);
        const body = el("nrsTrackBody");
        if (!body) return;
        if (!list.length) {
            body.innerHTML = `<p class="nrs-track-empty">Nothing tracked yet. ` +
                `Hit <b>+</b> under any column to save a prop.</p>`;
            return;
        }
        const byGame = {};
        list.forEach((e) => { (byGame[e.game] = byGame[e.game] || []).push(e); });
        body.innerHTML = Object.entries(byGame).map(([game, entries]) =>
            `<div class="nrs-track-game"><h4>${esc(game)}</h4>` +
            entries.map((e) =>
                `<div class="nrs-track-row">` +
                `<span class="nrs-track-row__name">${esc(e.name)}</span>` +
                `<span class="nrs-track-row__meta">${esc(e.meta)}</span>` +
                `<span class="nrs-track-row__pick">${esc(e.side)} ${esc(e.line)} ${esc(e.label)}</span>` +
                `<button type="button" class="nrs-track-row__del" data-track-del="${esc(e.id)}" ` +
                `aria-label="Remove">&times;</button></div>`).join("") +
            `</div>`).join("");
    }

    /* ── column picker ─────────────────────────────────────────────────────
       Same panel the NFL tab ships: a tab per position, a search box, and a
       switch per column. The DOM is the stylesheet's `nrs-colset` contract, so
       it inherits every bit of the existing styling. */
    function colSetListHtml(pos) {
        const on = new Set(visibleCols(pos).map((c) => c.key));
        const all = POS_COLUMNS[pos] || [];
        return (GROUP_ORDER[pos] || []).map((group) => {
            const cols = all.filter((c) => c.group === group);
            if (!cols.length) return "";
            const allOn = cols.every((c) => on.has(c.key));
            const rows = cols.map((c) =>
                `<li class="nrs-colset__row" data-colsearch="${esc((c.name + " " + c.abbr + " " + group).toLowerCase())}">` +
                `<span class="nrs-colset__name">${esc(c.name)} <abbr>(${esc(c.abbr)})</abbr></span>` +
                `<label class="nrs-switch">` +
                `<input type="checkbox" role="switch" data-colkey="${esc(c.key)}"${on.has(c.key) ? " checked" : ""} ` +
                `aria-label="${esc(c.name)}">` +
                `<span class="nrs-switch__track" aria-hidden="true"></span>` +
                `</label></li>`).join("");
            return `<li class="nrs-colset__group" data-colgroup-head="${esc(group)}">` +
                `<span>${esc(group)}</span>` +
                `<button type="button" data-colgroup="${esc(group)}">${allOn ? "None" : "All"}</button></li>` + rows;
        }).join("");
    }

    function renderColPanel() {
        const host = el("nrsColPanel");
        if (!host) return;
        const tabs = POSITIONS.map((p) =>
            `<button type="button" data-colpos="${esc(p)}"` +
            `${p === state.colSetPos ? ' class="is-active"' : ""}>${esc(p)}</button>`).join("");
        const pos = state.colSetPos;
        const count = visibleCols(pos).length;
        host.innerHTML =
            `<header class="nrs-colset__head"><h3>Column Settings</h3>` +
            `<button type="button" class="nrs-colset__close" data-colclose aria-label="Close">&times;</button></header>` +
            `<div class="nrs-colset__pos" role="tablist" aria-label="Position">${tabs}</div>` +
            `<div class="nrs-colset__searchwrap"><input type="search" class="nrs-colset__search" id="nrsColSearch" ` +
            `placeholder="Search columns — shots, blocks, power play…" aria-label="Search columns" autocomplete="off"></div>` +
            `<div class="nrs-colset__actions">` +
            `<button type="button" data-colall>Select All</button>` +
            `<button type="button" data-colreset>&#8634; Reset</button></div>` +
            `<p class="nrs-colset__note">${count} column${count === 1 ? "" : "s"} shown · ` +
            `applies to every ${esc(POS_LABEL[pos])} log and opponent table · saved on this device</p>` +
            `<ul class="nrs-colset__list" id="nrsColSetList">${colSetListHtml(pos)}</ul>`;
    }

    function setColKeys(pos, keys) {
        // keep the stored order matching the table's order
        const want = new Set(keys);
        state.cols[pos] = (POS_COLUMNS[pos] || []).filter((c) => want.has(c.key)).map((c) => c.key);
        saveColPrefs();
        renderColPanel();
        renderMatchup();
    }

    function initColPicker() {
        const panel = el("nrsColPanel");
        const gear = el("nrsColGear");
        gear.addEventListener("click", () => {
            panel.hidden = !panel.hidden;
            gear.setAttribute("aria-expanded", String(!panel.hidden));
        });
        panel.addEventListener("change", (ev) => {
            const box = ev.target.closest("[data-colkey]");
            if (!box) return;
            const pos = state.colSetPos;
            const keys = new Set(visibleCols(pos).map((c) => c.key));
            if (box.checked) keys.add(box.dataset.colkey); else keys.delete(box.dataset.colkey);
            setColKeys(pos, keys);
        });
        panel.addEventListener("input", (ev) => {
            if (ev.target.id !== "nrsColSearch") return;
            const q = ev.target.value.trim().toLowerCase();
            panel.querySelectorAll(".nrs-colset__row").forEach((row) => {
                row.hidden = !!q && !row.dataset.colsearch.includes(q);
            });
            // a group header with nothing left under it is noise while searching
            panel.querySelectorAll(".nrs-colset__group").forEach((head) => {
                let node = head.nextElementSibling, any = false;
                while (node && node.classList.contains("nrs-colset__row")) {
                    if (!node.hidden) { any = true; break; }
                    node = node.nextElementSibling;
                }
                head.hidden = !!q && !any;
            });
        });
        panel.addEventListener("click", (ev) => {
            const pos = state.colSetPos;
            const all = POS_COLUMNS[pos] || [];
            if (ev.target.closest("[data-colclose]")) {
                panel.hidden = true;
                gear.setAttribute("aria-expanded", "false");
                return;
            }
            const tab = ev.target.closest("[data-colpos]");
            if (tab) { state.colSetPos = tab.dataset.colpos; renderColPanel(); return; }
            if (ev.target.closest("[data-colall]")) { setColKeys(pos, all.map((c) => c.key)); return; }
            if (ev.target.closest("[data-colreset]")) { setColKeys(pos, defaultCols(pos)); return; }
            const group = ev.target.closest("[data-colgroup]");
            if (group) {
                const name = group.dataset.colgroup;
                const inGroup = all.filter((c) => c.group === name).map((c) => c.key);
                const on = new Set(visibleCols(pos).map((c) => c.key));
                const allOn = inGroup.every((k) => on.has(k));
                inGroup.forEach((k) => (allOn ? on.delete(k) : on.add(k)));
                setColKeys(pos, on);
            }
        });
    }

    /* ── controls ──────────────────────────────────────────────────────────── */
    function initControls() {
        const input = el("nrsDate");
        const goto = (date) => {
            state.date = date;
            input.value = date;
            // the address bar carries the slate, so a reload or a shared link lands here
            const url = new URL(location.href);
            url.searchParams.set("date", date);
            history.replaceState(null, "", url);
            loadSlate();
        };
        input.value = state.date;
        input.addEventListener("change", () => { if (input.value) goto(input.value); });
        el("nrsPrevDay").addEventListener("click", () => goto(shiftDate(state.date, -1)));
        el("nrsNextDay").addEventListener("click", () => goto(shiftDate(state.date, 1)));
        el("nrsToday").addEventListener("click", () => goto(todayISO()));
        el("nrsRefresh").addEventListener("click", () => loadSlate(true));

        el("nrsGames").addEventListener("click", (ev) => {
            const btn = ev.target.closest("[data-game]");
            if (!btn) return;
            state.gameId = btn.dataset.game;
            renderGames();
            renderMatchup();
        });

        el("nrsSideAway").addEventListener("click", () => { state.side = "away"; renderMatchup(); });
        el("nrsSideHome").addEventListener("click", () => { state.side = "home"; renderMatchup(); });

        // log filters are shared across cards: pick L5 on one and every card follows
        el("nrsPosSections").addEventListener("click", (ev) => {
            const btn = ev.target.closest(".nrs-log-filter [data-filter]");
            if (btn) {
                const side = btn.closest(".nrs-log-filter").dataset.filterSide;
                state.logFilter[side] = btn.dataset.filter;
                renderMatchup();
                return;
            }
            const side = ev.target.closest("[data-tc-side]");
            if (side) {
                const next = side.dataset.tcSide === "over" ? "under" : "over";
                side.dataset.tcSide = next;
                side.textContent = next === "over" ? "O" : "U";
                return;
            }
            const add = ev.target.closest("[data-tc-id]");
            if (!add) return;
            const cell = add.closest(".nrs-tc");
            const sideBtn = cell.querySelector("[data-tc-side]");
            const select = cell.querySelector(".nrs-tc__line");
            const pick = sideBtn.dataset.tcSide === "over" ? "Over" : "Under";
            const id = `${add.dataset.tcId}|${pick}|${select.value}`;
            const list = trackLoad();
            const at = list.findIndex((e) => e.id === id);
            if (at >= 0) {
                list.splice(at, 1);
            } else {
                list.push({
                    id,
                    name: add.dataset.trackName,
                    meta: add.dataset.trackMeta,
                    game: add.dataset.trackGame,
                    label: cell.dataset.tcLabel,
                    side: pick,
                    line: select.value,
                    expires: Number(add.dataset.trackExpires) || Date.now() + 864e5,
                });
            }
            trackSave(list);
            renderTracker();
            renderMatchup();
        });

        const trackOpen = el("nrsTrackOpen");
        trackOpen.addEventListener("click", () => {
            const panel = el("nrsTrackPanel");
            panel.hidden = !panel.hidden;
            trackOpen.setAttribute("aria-expanded", String(!panel.hidden));
        });
        el("nrsTrackBody").addEventListener("click", (ev) => {
            const del = ev.target.closest("[data-track-del]");
            if (!del) return;
            trackSave(trackLoad().filter((e) => e.id !== del.dataset.trackDel));
            renderTracker();
            renderMatchup();
        });
        el("nrsTrackClear").addEventListener("click", () => {
            trackSave([]);
            renderTracker();
            renderMatchup();
        });
    }

    /* ── boot ──────────────────────────────────────────────────────────────── */
    function init() {
        initTheme();
        loadColPrefs();
        // a ?date= in the URL wins, so a saved link opens on its own slate
        const params = new URLSearchParams(location.search);
        state.date = params.get("date") || todayISO();
        initControls();
        initColPicker();
        renderColPanel();
        renderTracker();
        loadSlate();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
