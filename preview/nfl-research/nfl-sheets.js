/* Worst Pickz — NFL Research cheat sheets.
 *
 * The Doink matchup view (nfl-research.js) is the front door and is untouched
 * by this file. This adds the left rail of sheets alongside it, reusing the same
 * table / heat / segmented-control vocabulary so they read as one product.
 *
 * Every sheet here is backed by free data. Three of PropFinder's sheets are
 * deliberately missing — coverage scheme, route alignment and line play — because
 * all three need paid charting. A thin imitation would be worse than their absence.
 */
(function () {
    "use strict";

    const SHEETS = [
        { key: "matchup", label: "Matchup", group: "Board" },
        { key: "rushing", label: "Rushing Gaps", group: "Matchups" },
        { key: "redzone", label: "Red Zone", group: "Matchups" },
        { key: "explosive", label: "Explosive Plays", group: "Matchups" },
        { key: "hitrate", label: "Hit Rate Matrix", group: "Players" },
        { key: "share", label: "Team Share %", group: "Players" },
        { key: "receiving", label: "Receiving Value", group: "Players" },
        { key: "coverage", label: "Coverage Players", group: "Players" },
        { key: "compare", label: "Compare", group: "Players" },
        { key: "teamdef", label: "Team Stats", group: "Teams" },
        { key: "tendencies", label: "Team Tendencies", group: "Teams" },
        { key: "power", label: "Power Ratings", group: "Teams" },
        { key: "hfa", label: "Home Field Edge", group: "League" },
        { key: "weather", label: "Weather", group: "League" },
        { key: "injuries", label: "Injuries & Snaps", group: "League" },
    ];

    const GAP_LABEL = {
        "left-end": "L End", "left-tackle": "L Tkl", "left-guard": "L Grd",
        middle: "Mid",
        "right-guard": "R Grd", "right-tackle": "R Tkl", "right-end": "R End",
    };

    const state = { slate: null, view: "matchup", opts: {} };

    const el = (id) => document.getElementById(id);
    const esc = (s) =>
        String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
            ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const num = (v, nd) => (v == null || v === "" || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(nd == null ? 1 : nd));
    const logo = (t) => (t ? `https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/${String(t).toLowerCase()}.png` : "");

    /* Colour a cell against the column's own league spread. Deeper = further out.
       `invert` flips it for columns where low is good (rating allowed, EPA given up). */
    function heat(value, values, invert) {
        if (value == null || !values.length) return "";
        const nums = values.filter((v) => v != null).sort((a, b) => a - b);
        if (nums.length < 4) return "";
        const lo = nums[Math.floor(nums.length * 0.25)];
        const hi = nums[Math.floor(nums.length * 0.75)];
        if (lo === hi) return "";
        let good = value >= hi;
        let bad = value <= lo;
        if (invert) { const t = good; good = bad; bad = t; }
        if (good) return " nrs-cell-heat--good";
        if (bad) return " nrs-cell-heat--bad";
        return "";
    }

    const ROW_CAP = 60;

    function table(cols, rows, opts) {
        opts = opts || {};
        // Some sheets carry 400+ rows. Painting them all stalls the first render
        // for no benefit -- nobody reads past the top of a sorted board without
        // filtering first. Cap, and let the reader ask for the rest.
        const total = rows.length;
        let capped = false;
        if (!opts.noCap && !state.opts.showAll && total > ROW_CAP) {
            rows = rows.slice(0, ROW_CAP);
            capped = true;
        }
        const colValues = cols.map((c) =>
            c.numeric ? rows.map((r) => (typeof c.value === "function" ? c.value(r) : r[c.key])) : []);
        const exp = !!opts.expandable;
        const head = (exp ? `<th class="nrs-exp-th"></th>` : "")
            + cols.map((c) => `<th${c.numeric ? ' class="nrs-num"' : ""}>${esc(c.label)}</th>`).join("");
        const body = rows.map((r, ri) => {
            const tds = cols.map((c, ci) => {
                const raw = typeof c.value === "function" ? c.value(r) : r[c.key];
                const shown = c.render ? c.render(r, raw) : (c.numeric ? num(raw, c.nd) : esc(raw == null ? "—" : raw));
                const cls = (c.numeric && !c.noHeat ? heat(raw, colValues[ci], c.invert) : "");
                return `<td class="${c.numeric ? "nrs-num" : ""}${cls}">${shown}</td>`;
            }).join("");
            const lead = exp
                ? `<td class="nrs-exp-td"><button type="button" class="nrs-exp-btn" data-player="${esc(r.name)}" data-team="${esc(r.team)}" aria-label="More on ${esc(r.name)}">\u25b8</button></td>`
                : "";
            return `<tr data-row="${ri}">${lead}${tds}</tr>`;
        }).join("");
        const more = capped
            ? `<button type="button" class="nrs-btn nrs-more" data-opt="showAll" data-val="true">Show all ${total} rows</button>`
            : "";
        return `<div class="nrs-table-wrap"><table class="nrs-table nrs-sheet-table">
            <thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${cols.length + (exp ? 1 : 0)}">No rows.</td></tr>`}</tbody>
        </table></div>${more}`;
    }

    const teamCell = (r) =>
        `<span class="nrs-sheet-team"><img src="${logo(r.team)}" alt="" width="18" height="18" loading="lazy">${esc(r.team || "—")}</span>`;
    const nameCell = (r) => `<span class="nrs-sheet-name">${esc(r.name)}</span>`;

    /* segmented control, same shape as the Doink game-log filter */
    function segmented(name, options, current) {
        return `<div class="nrs-log-filter nrs-sheet-seg" role="group">${options
            .map((o) => `<button type="button" data-opt="${name}" data-val="${esc(o.value)}"${String(o.value) === String(current) ? ' class="is-active"' : ""}>${esc(o.label)}</button>`)
            .join("")}</div>`;
    }

    function opt(key, fallback) {
        return state.opts[key] == null ? fallback : state.opts[key];
    }

    function intro(text) {
        return `<p class="nrs-sheet-intro">${text}</p>`;
    }

    function teamsOnSlate() {
        const s = state.slate;
        if (!s) return [];
        const set = new Set();
        (s.games || []).forEach((g) => { set.add(g.away); set.add(g.home); });
        return Array.from(set).sort();
    }

    function slateFilter(rows) {
        if (!opt("slateOnly", true)) return rows;
        const teams = new Set(teamsOnSlate());
        return rows.filter((r) => !r.team || teams.has(r.team));
    }

    function slateToggle() {
        return segmented("slateOnly", [
            { value: true, label: "This slate" },
            { value: false, label: "All teams" },
        ], opt("slateOnly", true));
    }


    /* The one real UX change PropFinder flags this season is the arrow next to the
       player. Ours pulls that player's row out of every other sheet at once, so
       "what else do we know about him" costs one click instead of five. */
    function roleChip(name, team) {
        const share = (((state.slate.sheets || {}).team_share || {}).players || [])
            .find((p) => p.name === name && p.team === team);
        if (!share) return "";
        if ((share.car_share || 0) >= 55) return `<span class="nrs-chip nrs-chip--hot">Workhorse back</span>`;
        if ((share.car_share || 0) >= 35) return `<span class="nrs-chip">Committee back</span>`;
        if ((share.tgt_share || 0) >= 24) return `<span class="nrs-chip nrs-chip--hot">Alpha target</span>`;
        if ((share.tgt_share || 0) >= 15) return `<span class="nrs-chip">Secondary target</span>`;
        return `<span class="nrs-chip nrs-chip--cool">Rotational</span>`;
    }

    function drawerHtml(name, team) {
        const sheets = state.slate.sheets || {};
        const find = (key) => (((sheets[key] || {}).players) || [])
            .find((p) => p.name === name && (!p.team || p.team === team));
        const share = find("team_share"), rz = find("red_zone"), expl = find("explosive");
        const rush = find("rushing_gaps"), rec = find("receiving_value"), cov = find("coverage_players");
        const block = (title, pairs) => {
            const live = pairs.filter((x) => x[1] != null && x[1] !== "");
            if (!live.length) return "";
            return `<div class="nrs-drawer-block"><h4>${esc(title)}</h4>${live
                .map(([k, v]) => `<div><span>${esc(k)}</span><strong>${typeof v === "number" ? num(v, 1) : esc(v)}</strong></div>`)
                .join("")}</div>`;
        };
        const gapBits = rush && rush.gaps
            ? Object.entries(rush.gaps)
                .filter((e) => e[1].att >= 5)
                .sort((a, b) => b[1].share - a[1].share)
                .slice(0, 3)
                .map((e) => [GAP_LABEL[e[0]] || e[0], `${num(e[1].share, 0)}% - ${num(e[1].ypc, 1)} ypc`])
            : [];
        const body = [
            block("Usage", [
                ["Touches", share && share.touches], ["Tgt share", share && share.tgt_share],
                ["Car share", share && share.car_share], ["Rec mix", share && share.rec_mix],
            ]),
            block("Red zone", [
                ["RZ touches", rz && rz.rz_touches], ["RZ share", rz && rz.rz_share],
                ["Inside 10", rz && rz.in10_touches], ["RZ TD", rz && rz.rz_td],
            ]),
            block("Explosive", [
                ["20+ rec %", expl && expl.rec20_rate], ["10+ run %", expl && expl.rush10_rate],
                ["Long rec", expl && expl.long_rec], ["Long run", expl && expl.long_rush],
            ]),
            block("Top gaps", gapBits),
            block("Receiving", [
                ["aDOT", rec && rec.adot], ["YBC/r", rec && rec.ybc_r],
                ["YAC/r", rec && rec.yac_r], ["Drop%", rec && rec.drop_pct],
            ]),
            block("Coverage", [
                ["Targeted", cov && cov.tgt], ["Cmp% allowed", cov && cov.cmp_pct],
                ["Rating allowed", cov && cov.rating_allowed], ["Miss tkl%", cov && cov.missed_tkl_pct],
            ]),
        ].filter(Boolean).join("");
        return `<div class="nrs-drawer-inner">
            <div class="nrs-drawer-head"><strong>${esc(name)}</strong> <span class="nrs-drawer-team">${esc(team || "")}</span> ${roleChip(name, team)}</div>
            ${body ? `<div class="nrs-drawer-body">${body}</div>` : `<p class="nrs-empty">No other sheet carries this player.</p>`}</div>`;
    }

    // ── sheets ───────────────────────────────────────────────────────────────

    function sheetRushing() {
        const d = (state.slate.sheets || {}).rushing_gaps;
        if (!d) return `<p class="nrs-empty">No rushing data in this slate file.</p>`;
        const view = opt("rushView", "players");
        const gaps = d.gap_keys || [];
        let body;
        if (view === "players") {
            const rows = slateFilter(d.players || []);
            const cols = [
                { label: "Team", key: "team", render: teamCell },
                { label: "Player", key: "name", render: nameCell },
                { label: "Att", key: "att", numeric: true, nd: 0, noHeat: true },
                { label: "YPC", key: "ypc", numeric: true },
                { label: "Succ%", key: "success_pct", numeric: true },
                { label: "EPA/att", key: "epa_play", numeric: true, nd: 3 },
                { label: "TD", key: "td", numeric: true, nd: 0, noHeat: true },
            ].concat(gaps.map((g) => ({
                label: GAP_LABEL[g] || g,
                numeric: true,
                nd: 0,
                value: (r) => (r.gaps && r.gaps[g] ? r.gaps[g].share : null),
                render: (r) => {
                    const b = r.gaps && r.gaps[g];
                    if (!b || !b.att) return "—";
                    return `${num(b.share, 0)}%<span class="nrs-sub">${num(b.ypc, 1)}</span>`;
                },
            })));
            body = table(cols, rows, { expandable: true });
        } else {
            const rows = slateFilter(Object.entries(d.defense || {}).map(([team, v]) => ({ team, ...v })));
            const cols = [
                { label: "Defense", key: "team", render: teamCell },
                { label: "Att faced", key: "att", numeric: true, nd: 0, noHeat: true },
                { label: "YPC allowed", key: "ypc", numeric: true },
                { label: "Succ% allowed", key: "success_pct", numeric: true },
            ].concat(gaps.map((g) => ({
                label: GAP_LABEL[g] || g,
                numeric: true,
                value: (r) => (r.gaps && r.gaps[g] ? r.gaps[g].ypc : null),
                render: (r) => {
                    const b = r.gaps && r.gaps[g];
                    if (!b || !b.att) return "—";
                    return `${num(b.ypc, 1)}<span class="nrs-sub">${b.att} att</span>`;
                },
            })));
            body = table(cols, rows);
        }
        return intro(`Where backs actually run, and where defences give it up. Player cells show <strong>carry share</strong> of that gap with yards per carry beneath; defence cells show <strong>YPC allowed</strong> through the gap. League YPC ${num(d.league_ypc, 2)}.`)
            + `<div class="nrs-sheet-controls">${segmented("rushView", [{ value: "players", label: "Rushers" }, { value: "defense", label: "Defences" }], view)}${slateToggle()}</div>`
            + body;
    }

    function sheetRedZone() {
        const d = (state.slate.sheets || {}).red_zone;
        if (!d) return `<p class="nrs-empty">No red zone data in this slate file.</p>`;
        const view = opt("rzView", "players");
        if (view === "players") {
            const rows = slateFilter(d.players || []);
            return intro(`Inside-the-20 usage. <strong>RZ share</strong> is the player's cut of his own team's red-zone touches — the number that travels best to anytime-touchdown pricing.`)
                + `<div class="nrs-sheet-controls">${segmented("rzView", [{ value: "players", label: "Players" }, { value: "defense", label: "Defences" }], view)}${slateToggle()}</div>`
                + table([
                    { label: "Team", key: "team", render: teamCell },
                    { label: "Player", key: "name", render: nameCell },
                    { label: "RZ touches", key: "rz_touches", numeric: true, nd: 0 },
                    { label: "RZ share", key: "rz_share", numeric: true },
                    { label: "Carries", key: "rz_car", numeric: true, nd: 0 },
                    { label: "Targets", key: "rz_tgt", numeric: true, nd: 0 },
                    { label: "Inside 10", key: "in10_touches", numeric: true, nd: 0 },
                    { label: "TD", key: "rz_td", numeric: true, nd: 0 },
                ], rows, { expandable: true });
        }
        const rows = slateFilter(Object.entries(d.defense || {}).map(([team, v]) => ({ team, ...v })));
        return intro(`What each defence concedes inside the 20. League red-zone TD rate ${num(d.league_rz_td_pct, 1)}%.`)
            + `<div class="nrs-sheet-controls">${segmented("rzView", [{ value: "players", label: "Players" }, { value: "defense", label: "Defences" }], view)}${slateToggle()}</div>`
            + table([
                { label: "Defense", key: "team", render: teamCell },
                { label: "RZ plays", key: "rz_plays", numeric: true, nd: 0, noHeat: true },
                { label: "TD allowed", key: "rz_td", numeric: true, nd: 0 },
                { label: "TD rate", key: "rz_td_pct", numeric: true },
                { label: "EPA/play", key: "rz_epa_play", numeric: true, nd: 3 },
                { label: "Run rate faced", key: "rush_pct", numeric: true },
            ], rows);
    }

    function sheetExplosive() {
        const d = (state.slate.sheets || {}).explosive;
        if (!d) return `<p class="nrs-empty">No explosive-play data in this slate file.</p>`;
        const view = opt("expView", "players");
        if (view === "players") {
            const rows = slateFilter(d.players || []);
            return intro(`Explosive = a catch of <strong>20+</strong> yards or a carry of <strong>10+</strong> / <strong>20+</strong>. The rate columns matter more than the counts — they survive a change in volume.`)
                + `<div class="nrs-sheet-controls">${segmented("expView", [{ value: "players", label: "Players" }, { value: "defense", label: "Defences" }], view)}${slateToggle()}</div>`
                + table([
                    { label: "Team", key: "team", render: teamCell },
                    { label: "Player", key: "name", render: nameCell },
                    { label: "Rec", key: "rec", numeric: true, nd: 0, noHeat: true },
                    { label: "20+ rec", key: "rec20", numeric: true, nd: 0 },
                    { label: "20+ rec %", key: "rec20_rate", numeric: true },
                    { label: "Long rec", key: "long_rec", numeric: true, nd: 0 },
                    { label: "Car", key: "car", numeric: true, nd: 0, noHeat: true },
                    { label: "10+ run %", key: "rush10_rate", numeric: true },
                    { label: "20+ run %", key: "rush20_rate", numeric: true },
                    { label: "Long run", key: "long_rush", numeric: true, nd: 0 },
                ], rows, { expandable: true });
        }
        const rows = slateFilter(Object.entries(d.defense || {}).map(([team, v]) => ({ team, ...v })));
        return intro(`Explosives allowed. Green here means the defence gives up big plays — a target, not a warning.`)
            + `<div class="nrs-sheet-controls">${segmented("expView", [{ value: "players", label: "Players" }, { value: "defense", label: "Defences" }], view)}${slateToggle()}</div>`
            + table([
                { label: "Defense", key: "team", render: teamCell },
                { label: "20+ rec allowed", key: "rec20", numeric: true, nd: 0 },
                { label: "20+ rec %", key: "rec20_rate", numeric: true },
                { label: "10+ run allowed", key: "rush10", numeric: true, nd: 0 },
                { label: "10+ run %", key: "rush10_rate", numeric: true },
                { label: "20+ run allowed", key: "rush20", numeric: true, nd: 0 },
                { label: "20+ run %", key: "rush20_rate", numeric: true },
            ], rows);
    }

    const HIT_PROPS = [
        { value: "rec_yds", label: "Rec yds", lines: [39.5, 49.5, 59.5, 69.5, 79.5, 99.5] },
        { value: "rush_yds", label: "Rush yds", lines: [29.5, 39.5, 49.5, 59.5, 69.5, 89.5] },
        { value: "rec", label: "Receptions", lines: [2.5, 3.5, 4.5, 5.5, 6.5] },
        { value: "tgt", label: "Targets", lines: [3.5, 4.5, 5.5, 6.5, 7.5] },
        { value: "car", label: "Carries", lines: [8.5, 11.5, 14.5, 17.5] },
        { value: "td", label: "TD", lines: [0.5] },
    ];

    function sheetHitRate() {
        const d = (state.slate.sheets || {}).hit_rates;
        if (!d) return `<p class="nrs-empty">No game logs in this slate file.</p>`;
        const propKey = opt("hitProp", "rec_yds");
        const prop = HIT_PROPS.find((p) => p.value === propKey) || HIT_PROPS[0];
        const span = Number(opt("hitSpan", 5));
        const rows = slateFilter(d.players || [])
            .map((p) => {
                const games = p.games.slice(-span);
                const rec = { team: p.team, name: p.name, played: games.length };
                prop.lines.forEach((line) => {
                    const hits = games.filter((g) => (g[prop.value] || 0) > line).length;
                    rec["l" + String(line).replace(".", "_")] = games.length ? (100 * hits) / games.length : null;
                    rec["n" + String(line).replace(".", "_")] = hits;
                });
                return rec;
            })
            .filter((r) => r.played >= Math.min(3, span));
        const cols = [
            { label: "Team", key: "team", render: teamCell },
            { label: "Player", key: "name", render: nameCell },
            { label: "GP", key: "played", numeric: true, nd: 0, noHeat: true },
        ].concat(prop.lines.map((line) => {
            const k = "l" + String(line).replace(".", "_");
            const n = "n" + String(line).replace(".", "_");
            return {
                label: `${line}+`, key: k, numeric: true, nd: 0,
                render: (r) => (r[k] == null ? "—" : `${num(r[k], 0)}%<span class="nrs-sub">${r[n]}/${r.played}</span>`),
            };
        }));
        rows.sort((a, b) => (b[Object.keys(b).find((k) => k.startsWith("l")) || ""] || 0) - 0);
        return intro(`How often each player has cleared a line over his last ${span} games. Cells show hit rate with the raw count beneath. Book lines are not attached — set <code>ODDS_API_KEY</code> to price these against the market.`)
            + `<div class="nrs-sheet-controls">${segmented("hitProp", HIT_PROPS.map((p) => ({ value: p.value, label: p.label })), propKey)}
               ${segmented("hitSpan", [{ value: 3, label: "L3" }, { value: 5, label: "L5" }, { value: 10, label: "L10" }, { value: 99, label: "All" }], String(span))}
               ${slateToggle()}</div>`
            + table(cols, rows, { expandable: true });
    }

    function sheetShare() {
        const d = (state.slate.sheets || {}).team_share;
        if (!d) return `<p class="nrs-empty">No usage data in this slate file.</p>`;
        const rows = slateFilter(d.players || []);
        return intro(`Each player's cut of his own team's volume. <strong>Rec mix</strong> is what share of his touches arrive through the air — the split that decides which market his workload actually feeds.`)
            + `<div class="nrs-sheet-controls">${slateToggle()}</div>`
            + table([
                { label: "Team", key: "team", render: teamCell },
                { label: "Player", key: "name", render: nameCell },
                { label: "Touches", key: "touches", numeric: true, nd: 0, noHeat: true },
                { label: "Tgt share", key: "tgt_share", numeric: true },
                { label: "Car share", key: "car_share", numeric: true },
                { label: "Rec mix", key: "rec_mix", numeric: true },
                { label: "Rec yds", key: "rec_yds", numeric: true, nd: 0 },
                { label: "Rush yds", key: "rush_yds", numeric: true, nd: 0 },
            ], rows, { expandable: true });
    }

    function sheetReceiving() {
        const d = (state.slate.sheets || {}).receiving_value;
        if (!d || !(d.players || []).length) return `<p class="nrs-empty">No PFR receiving data for this season yet.</p>`;
        const pos = opt("recPos", "ALL");
        let rows = slateFilter(d.players);
        if (pos !== "ALL") rows = rows.filter((r) => r.pos === pos);
        return intro(`Receiver efficiency from Pro-Football-Reference. <strong>aDOT</strong> is average depth of target; <strong>YBC/r</strong> and <strong>YAC/r</strong> split each catch into what the route won and what the runner won.`)
            + `<div class="nrs-sheet-controls">${segmented("recPos", [{ value: "ALL", label: "All" }, { value: "WR", label: "WR" }, { value: "TE", label: "TE" }, { value: "RB", label: "RB" }], pos)}${slateToggle()}</div>`
            + table([
                { label: "Team", key: "team", render: teamCell },
                { label: "Player", key: "name", render: nameCell },
                { label: "Pos", key: "pos" },
                { label: "Tgt", key: "tgt", numeric: true, nd: 0, noHeat: true },
                { label: "Rec", key: "rec", numeric: true, nd: 0, noHeat: true },
                { label: "Yds", key: "yds", numeric: true, nd: 0 },
                { label: "aDOT", key: "adot", numeric: true },
                { label: "YBC/r", key: "ybc_r", numeric: true },
                { label: "YAC/r", key: "yac_r", numeric: true },
                { label: "Brk tkl", key: "brk_tkl", numeric: true, nd: 0 },
                { label: "Drop%", key: "drop_pct", numeric: true, invert: true },
                { label: "Rating", key: "rating_when_targeted", numeric: true, nd: 0 },
            ], rows, { expandable: true });
    }

    function sheetCoverage() {
        const d = (state.slate.sheets || {}).coverage_players;
        if (!d || !(d.players || []).length) return `<p class="nrs-empty">No PFR coverage data for this season yet.</p>`;
        const pos = opt("covPos", "ALL");
        let rows = slateFilter(d.players);
        if (pos !== "ALL") rows = rows.filter((r) => r.pos === pos);
        return intro(`What happened when the man was thrown at — completion rate, yards per target and passer rating allowed. This is coverage <em>results</em>, not coverage scheme: man/zone shell data has no free source since nflverse participation stopped after 2023, so it is not on this site.`)
            + `<div class="nrs-sheet-controls">${segmented("covPos", [{ value: "ALL", label: "All" }, { value: "CB", label: "CB" }, { value: "S", label: "S" }, { value: "LB", label: "LB" }], pos)}${slateToggle()}</div>`
            + table([
                { label: "Team", key: "team", render: teamCell },
                { label: "Defender", key: "name", render: nameCell },
                { label: "Pos", key: "pos" },
                { label: "Tgt", key: "tgt", numeric: true, nd: 0, noHeat: true },
                { label: "Cmp%", key: "cmp_pct", numeric: true, invert: true },
                { label: "Yds/tgt", key: "yds_tgt", numeric: true, invert: true },
                { label: "TD", key: "td", numeric: true, nd: 0, invert: true },
                { label: "INT", key: "int", numeric: true, nd: 0 },
                { label: "Rating allowed", key: "rating_allowed", numeric: true, nd: 0, invert: true },
                { label: "aDOT", key: "dadot", numeric: true },
                { label: "Miss tkl%", key: "missed_tkl_pct", numeric: true, invert: true },
            ], rows, { expandable: true });
    }

    function sheetTeamDef() {
        const d = (state.slate.sheets || {}).team_stats;
        if (!d) return `<p class="nrs-empty">No team data in this slate file.</p>`;
        const side = opt("tdSide", "def");
        const rows = slateFilter(Object.entries(d)
            .filter(([, v]) => v && v[side])
            .map(([team, v]) => ({ team, ...v[side] })));
        const invert = side === "def";
        return intro(side === "def"
            ? `Defensive results per play. Green means the defence <strong>gives up more</strong> — these are matchups to attack, not compliments.`
            : `Offensive results per play. Green is a better offence.`)
            + `<div class="nrs-sheet-controls">${segmented("tdSide", [{ value: "def", label: "Defense" }, { value: "off", label: "Offense" }], side)}${slateToggle()}</div>`
            + table([
                { label: "Team", key: "team", render: teamCell },
                { label: "Plays", key: "plays", numeric: true, nd: 0, noHeat: true },
                { label: "Yds/play", key: "ypp", numeric: true },
                { label: "EPA/play", key: "epa_play", numeric: true, nd: 3 },
                { label: "Success%", key: "success_pct", numeric: true },
                { label: "Pass EPA", key: "pass_epa_play", numeric: true, nd: 3 },
                { label: "Rush EPA", key: "rush_epa_play", numeric: true, nd: 3 },
                { label: "Sacks", key: "sacks", numeric: true, nd: 0, invert: invert },
                { label: "INT", key: "int", numeric: true, nd: 0, invert: invert },
                { label: "Pass rate", key: "pass_rate", numeric: true, noHeat: true },
            ], rows);
    }

    function sheetTendencies() {
        const d = (state.slate.sheets || {}).tendencies;
        if (!d || !Object.keys(d).length) return `<p class="nrs-empty">No FTN charting for this season yet.</p>`;
        const side = opt("tendSide", "offense");
        const rows = slateFilter(Object.entries(d)
            .filter(([, v]) => v && v[side])
            .map(([team, v]) => ({ team, ...v[side] })));
        const cols = side === "offense"
            ? [
                { label: "Team", key: "team", render: teamCell },
                { label: "Plays", key: "plays", numeric: true, nd: 0, noHeat: true },
                { label: "Motion%", key: "motion_pct", numeric: true },
                { label: "Play action%", key: "play_action_pct", numeric: true },
                { label: "RPO%", key: "rpo_pct", numeric: true },
                { label: "Screen%", key: "screen_pct", numeric: true },
                { label: "No huddle%", key: "no_huddle_pct", numeric: true },
                { label: "Backfield", key: "avg_backfield", numeric: true, nd: 2 },
            ]
            : [
                { label: "Team", key: "team", render: teamCell },
                { label: "Plays", key: "plays", numeric: true, nd: 0, noHeat: true },
                { label: "Blitz%", key: "blitz_pct", numeric: true },
                { label: "Pass rushers", key: "avg_pass_rushers", numeric: true, nd: 2 },
                { label: "Box count", key: "avg_box", numeric: true, nd: 2 },
            ];
        return intro(`Play-calling tendencies from FTN charting. Coverage shells are <em>not</em> here — that data has no free source after 2023, so the sheet stops at what can be verified.`)
            + `<div class="nrs-sheet-controls">${segmented("tendSide", [{ value: "offense", label: "Offense" }, { value: "defense", label: "Defense" }], side)}${slateToggle()}</div>`
            + table(cols, rows);
    }

    function sheetPower() {
        const d = (state.slate.sheets || {}).power_ratings;
        if (!d) return `<p class="nrs-empty">No power ratings in this slate file.</p>`;
        const rows = slateFilter(d.teams || []);
        return intro(`Net EPA per play scaled to points per game, so the rating reads like a spread. <strong>SOS</strong> columns average the rating of the opponents played and still to come — a positive number means a harder schedule.`)
            + `<div class="nrs-sheet-controls">${slateToggle()}</div>`
            + table([
                { label: "#", key: "rank", numeric: true, nd: 0, noHeat: true },
                { label: "Team", key: "team", render: teamCell },
                { label: "Rating", key: "rating", numeric: true, nd: 2 },
                { label: "Off EPA", key: "off_epa", numeric: true, nd: 3 },
                { label: "Def EPA", key: "def_epa", numeric: true, nd: 3, invert: true },
                { label: "SOS played", key: "sos_played", numeric: true, nd: 2 },
                { label: "SOS left", key: "sos_left", numeric: true, nd: 2 },
                { label: "SOS full", key: "sos_full", numeric: true, nd: 2 },
            ], rows);
    }

    function sheetHfa() {
        const d = (state.slate.sheets || {}).hfa;
        if (!d || !(d.seasons || []).length) return `<p class="nrs-empty">No schedule history in this slate file.</p>`;
        const rows = d.seasons;
        const w = 900, h = 260, padL = 44, padB = 28, padT = 16;
        const max = Math.max(...rows.map((r) => r.avg_margin), 3.5);
        const min = Math.min(...rows.map((r) => r.avg_margin), 0);
        const x = (i) => padL + (i * (w - padL - 12)) / Math.max(1, rows.length - 1);
        const y = (v) => padT + (h - padT - padB) * (1 - (v - min) / (max - min || 1));
        const line = rows.map((r, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(r.avg_margin).toFixed(1)}`).join(" ");
        const dots = rows.map((r, i) =>
            `<circle cx="${x(i).toFixed(1)}" cy="${y(r.avg_margin).toFixed(1)}" r="2.6"><title>${r.season}: ${r.avg_margin} pts, ${r.home_win_pct}% home wins</title></circle>`).join("");
        const ticks = [0, 1, 2, 3, 4].filter((v) => v >= min && v <= max).map((v) =>
            `<g><line x1="${padL}" x2="${w - 12}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" class="nrs-chart-grid"/>
              <text x="${padL - 8}" y="${(y(v) + 4).toFixed(1)}" class="nrs-chart-axis" text-anchor="end">${v}</text></g>`).join("");
        const labels = rows.map((r, i) => (r.season % 5 === 0
            ? `<text x="${x(i).toFixed(1)}" y="${h - 8}" class="nrs-chart-axis" text-anchor="middle">${r.season}</text>` : "")).join("");
        return intro(`Average home margin by season since ${rows[0].season}. All-time average <strong>${num(d.all_time_avg_margin, 2)} points</strong>. The dip is real — home edge collapsed in the crowdless season and has never fully returned.`)
            + `<div class="nrs-chart-wrap"><svg viewBox="0 0 ${w} ${h}" class="nrs-chart" role="img" aria-label="Home field advantage by season">
                ${ticks}<path d="${line}" class="nrs-chart-line" fill="none"/>${dots}${labels}</svg></div>`
            + table([
                { label: "Season", key: "season", numeric: true, nd: 0, noHeat: true },
                { label: "Games", key: "games", numeric: true, nd: 0, noHeat: true },
                { label: "Avg home margin", key: "avg_margin", numeric: true, nd: 2 },
                { label: "Home win%", key: "home_win_pct", numeric: true },
            ], rows.slice().reverse());
    }

    function sheetWeather() {
        const games = (state.slate.games || []).filter((g) => g.weather);
        if (!games.length) return `<p class="nrs-empty">No forecasts in this slate file.</p>`;
        const cards = games.map((g) => {
            const w = g.weather;
            const head = `<div class="nrs-wx-head"><img src="${logo(g.away)}" alt="" width="20" height="20"><strong>${esc(g.away)}</strong>
                <span class="nrs-wx-at">@</span><img src="${logo(g.home)}" alt="" width="20" height="20"><strong>${esc(g.home)}</strong></div>`;
            const venue = `<div class="nrs-wx-venue">${esc(w.venue || "")} · <span class="nrs-wx-roof">${esc(w.roof || "")}</span></div>`;
            if (w.indoor || w.note) {
                return `<div class="nrs-wx-card">${head}${venue}<div class="nrs-wx-note">${esc(w.note || "Indoor.")}</div></div>`;
            }
            const heavy = (w.precip_pct || 0) >= 40 || (w.wind_mph || 0) >= 15;
            return `<div class="nrs-wx-card${heavy ? " is-flagged" : ""}">${head}${venue}
                <div class="nrs-wx-grid">
                    <div><span>Temp</span><strong>${num(w.temp_f, 0)}°</strong></div>
                    <div><span>Feels</span><strong>${num(w.feels_f, 0)}°</strong></div>
                    <div><span>Precip</span><strong>${num(w.precip_pct, 0)}%</strong></div>
                    <div><span>Wind</span><strong>${num(w.wind_mph, 0)} mph</strong></div>
                    <div><span>Gusts</span><strong>${num(w.gust_mph, 0)} mph</strong></div>
                </div>${heavy ? `<div class="nrs-wx-flag">Wind or rain enough to lean unders on passing</div>` : ""}</div>`;
        }).join("");
        return intro(`Kickoff forecasts from Open-Meteo. Domes short-circuit — no point printing a wind speed nobody can act on. Games more than 16 days out have no forecast yet.`)
            + `<div class="nrs-wx-grid-wrap">${cards}</div>`;
    }

    function sheetInjuries() {
        const roster = (state.slate.sheets || {}).roster || {};
        const teams = teamsOnSlate().filter((t) => roster[t]);
        if (!teams.length) return `<p class="nrs-empty">No roster data in this slate file.</p>`;
        const team = opt("injTeam", teams[0]);
        const rec = roster[team] || {};
        const inj = (rec.injuries || []);
        const snaps = (rec.snaps || []);
        return intro(`Latest injury report and season snap share. Snap % is the strongest single tell for whether last season's production is still the right base rate.`)
            + `<div class="nrs-sheet-controls">${segmented("injTeam", teams.map((t) => ({ value: t, label: t })), team)}</div>`
            + `<div class="nrs-duo">
                <div><h3 class="nrs-sheet-h3">Injury report</h3>${inj.length
                    ? table([
                        { label: "Player", key: "name", render: nameCell },
                        { label: "Pos", key: "pos" },
                        { label: "Status", key: "status" },
                        { label: "Injury", key: "injury" },
                    ], inj)
                    : `<p class="nrs-empty">Nothing reported.</p>`}</div>
                <div><h3 class="nrs-sheet-h3">Snap share</h3>${table([
                    { label: "Player", key: "name", render: nameCell },
                    { label: "Pos", key: "pos" },
                    { label: "Off snap%", key: "off_pct", numeric: true },
                    { label: "G", key: "games", numeric: true, nd: 0, noHeat: true },
                ], snaps)}</div>
            </div>`;
    }

    // ── compare (radar) ──────────────────────────────────────────────────────

    const COMPARE_METRICS = [
        { key: "touches", label: "Touches", src: "team_share" },
        { key: "tgt_share", label: "Tgt share", src: "team_share" },
        { key: "car_share", label: "Car share", src: "team_share" },
        { key: "rz_share", label: "RZ share", src: "red_zone" },
        { key: "rec20_rate", label: "20+ rec %", src: "explosive" },
        { key: "rush10_rate", label: "10+ run %", src: "explosive" },
        { key: "yac_r", label: "YAC/rec", src: "receiving_value" },
        { key: "adot", label: "aDOT", src: "receiving_value" },
    ];

    function comparePool() {
        const share = ((state.slate.sheets || {}).team_share || {}).players || [];
        return slateFilter(share).slice(0, 400);
    }

    function metricsFor(name) {
        const sheets = state.slate.sheets || {};
        const out = {};
        COMPARE_METRICS.forEach((m) => {
            const src = sheets[m.src];
            const list = (src && src.players) || [];
            const hit = list.find((p) => p.name === name);
            out[m.key] = hit ? hit[m.key] : null;
        });
        return out;
    }

    function sheetCompare() {
        const pool = comparePool();
        if (!pool.length) return `<p class="nrs-empty">No players in this slate file.</p>`;
        const aName = opt("cmpA", pool[0].name);
        const bName = opt("cmpB", (pool[1] || pool[0]).name);
        const options = (sel) => pool.map((p) => `<option value="${esc(p.name)}"${p.name === sel ? " selected" : ""}>${esc(p.name)} (${esc(p.team)})</option>`).join("");
        const A = metricsFor(aName), B = metricsFor(bName);

        // scale each axis against the pool so the shapes are comparable
        const sheets = state.slate.sheets || {};
        const maxes = {};
        COMPARE_METRICS.forEach((m) => {
            const list = ((sheets[m.src] || {}).players) || [];
            const vals = list.map((p) => p[m.key]).filter((v) => v != null);
            maxes[m.key] = vals.length ? Math.max.apply(null, vals) : 1;
        });

        const size = 380, cx = size / 2, cy = size / 2, R = 140;
        const n = COMPARE_METRICS.length;
        const pt = (i, frac) => {
            const ang = (Math.PI * 2 * i) / n - Math.PI / 2;
            return [cx + R * frac * Math.cos(ang), cy + R * frac * Math.sin(ang)];
        };
        const poly = (vals) => COMPARE_METRICS.map((m, i) => {
            const v = vals[m.key];
            const frac = v == null || !maxes[m.key] ? 0 : Math.max(0, Math.min(1, v / maxes[m.key]));
            const [px, py] = pt(i, frac);
            return `${px.toFixed(1)},${py.toFixed(1)}`;
        }).join(" ");
        const rings = [0.25, 0.5, 0.75, 1].map((f) =>
            `<polygon points="${COMPARE_METRICS.map((_, i) => pt(i, f).map((v) => v.toFixed(1)).join(",")).join(" ")}" class="nrs-radar-ring"/>`).join("");
        const axisLabels = COMPARE_METRICS.map((m, i) => {
            const [px, py] = pt(i, 1.16);
            return `<text x="${px.toFixed(1)}" y="${py.toFixed(1)}" class="nrs-radar-label" text-anchor="middle">${esc(m.label)}</text>`;
        }).join("");

        let aWins = 0, bWins = 0;
        COMPARE_METRICS.forEach((m) => {
            const av = A[m.key], bv = B[m.key];
            if (av == null || bv == null) return;
            if (av > bv) aWins++; else if (bv > av) bWins++;
        });

        return intro(`Head to head on the metrics this site can actually source. Each axis is scaled against the league, so a bigger shape is a bigger role — not a better player.`)
            + `<div class="nrs-sheet-controls nrs-cmp-controls">
                <label>Player A <select class="nrs-select" data-cmp="cmpA">${options(aName)}</select></label>
                <label>Player B <select class="nrs-select" data-cmp="cmpB">${options(bName)}</select></label>
               </div>
               <div class="nrs-cmp-head"><span class="nrs-cmp-a">${esc(aName)}</span> leads <strong>${aWins}–${bWins}</strong> <span class="nrs-cmp-b">${esc(bName)}</span></div>
               <div class="nrs-cmp-wrap">
                 <svg viewBox="0 0 ${size} ${size}" class="nrs-radar" role="img" aria-label="Player comparison radar">
                   ${rings}${axisLabels}
                   <polygon points="${poly(A)}" class="nrs-radar-a"/>
                   <polygon points="${poly(B)}" class="nrs-radar-b"/>
                 </svg>
                 ${table([
                    { label: "Metric", key: "label" },
                    { label: aName, key: "a", numeric: true, nd: 1, noHeat: true },
                    { label: bName, key: "b", numeric: true, nd: 1, noHeat: true },
                 ], COMPARE_METRICS.map((m) => ({ label: m.label, a: A[m.key], b: B[m.key] })))}
               </div>`;
    }

    const RENDERERS = {
        rushing: sheetRushing, redzone: sheetRedZone, explosive: sheetExplosive,
        hitrate: sheetHitRate, share: sheetShare, receiving: sheetReceiving,
        coverage: sheetCoverage, teamdef: sheetTeamDef, tendencies: sheetTendencies,
        power: sheetPower, hfa: sheetHfa, weather: sheetWeather,
        injuries: sheetInjuries, compare: sheetCompare,
    };

    // ── shell ────────────────────────────────────────────────────────────────

    function renderRail() {
        const rail = el("nrsRail");
        if (!rail) return;
        const groups = [];
        SHEETS.forEach((s) => {
            let g = groups.find((x) => x.name === s.group);
            if (!g) groups.push((g = { name: s.group, items: [] }));
            g.items.push(s);
        });
        rail.innerHTML = groups.map((g) =>
            `<div class="nrs-rail-group"><span class="nrs-rail-group__title">${esc(g.name)}</span>
              ${g.items.map((s) => `<button type="button" class="nrs-rail-btn${s.key === state.view ? " is-active" : ""}" data-view="${s.key}">${esc(s.label)}</button>`).join("")}
            </div>`).join("");
    }

    function render() {
        renderRail();
        const matchup = el("nrsMatchupHost");
        const sheet = el("nrsSheet");
        if (!sheet) return;
        if (state.view === "matchup") {
            if (matchup) matchup.hidden = false;
            sheet.hidden = true;
            return;
        }
        if (matchup) matchup.hidden = true;
        sheet.hidden = false;
        const def = SHEETS.find((s) => s.key === state.view);
        let html;
        try {
            html = (RENDERERS[state.view] || (() => `<p class="nrs-empty">Nothing here yet.</p>`))();
        } catch (err) {
            html = `<p class="nrs-empty">Could not render this sheet: ${esc(err && err.message)}</p>`;
        }
        sheet.innerHTML = `<h2 class="nrs-section-title">${esc(def ? def.label : "")}</h2>${html}`;
    }

    function initEvents() {
        document.addEventListener("click", (ev) => {
            const railBtn = ev.target.closest(".nrs-rail-btn");
            if (railBtn) {
                state.view = railBtn.dataset.view;
                state.opts.showAll = false;
                render();
                window.scrollTo({ top: 0, behavior: "smooth" });
                return;
            }
            const expBtn = ev.target.closest(".nrs-exp-btn");
            if (expBtn) {
                const tr = expBtn.closest("tr");
                const next = tr.nextElementSibling;
                if (next && next.classList.contains("nrs-drawer")) {
                    next.remove();
                    expBtn.textContent = "\u25b8";
                    return;
                }
                const row = document.createElement("tr");
                row.className = "nrs-drawer";
                row.innerHTML = `<td colspan="${tr.cells.length}">${drawerHtml(expBtn.dataset.player, expBtn.dataset.team)}</td>`;
                tr.after(row);
                expBtn.textContent = "\u25be";
                return;
            }
            const segBtn = ev.target.closest("[data-opt]");
            if (segBtn && segBtn.closest("#nrsSheet")) {
                const raw = segBtn.dataset.val;
                state.opts[segBtn.dataset.opt] = raw === "true" ? true : raw === "false" ? false : raw;
                render();
            }
        });
        document.addEventListener("change", (ev) => {
            const sel = ev.target.closest("[data-cmp]");
            if (sel) {
                state.opts[sel.dataset.cmp] = sel.value;
                render();
            }
        });
    }

    window.NRSSheets = {
        onSlate(slate) {
            state.slate = slate;
            render();
        },
        init() {
            initEvents();
            renderRail();
        },
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => window.NRSSheets.init());
    } else {
        window.NRSSheets.init();
    }
})();
