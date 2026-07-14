/* Worst Pickz — NFL Matchup Research (BETA)
 * Offense (left) vs what the defense allows (right), Doink-style.
 * Data: pre-built JSON from fetch-nfl-research-slate.py (nflverse + ESPN, free).
 */
(function () {
    "use strict";

    const DEFAULT_SEASON = 2026;
    const SEASONS = [2026, 2025];
    const MAX_WEEK = 18;
    const POSITIONS = ["QB", "RB", "WR", "TE"];

    // columns shown per position (offense + defense share the same set)
    const POS_COLUMNS = {
        QB: [
            { key: "pass_att", label: "Att" },
            { key: "pass_cmp", label: "Cmp" },
            { key: "pass_yds", label: "Yds" },
            { key: "pass_td", label: "TD" },
            { key: "pass_int", label: "INT", lowerBetter: true },
            { key: "rush_yds", label: "Yds" },
        ],
        RB: [
            { key: "rush_att", label: "Att" },
            { key: "rush_yds", label: "Yds" },
            { key: "rush_td", label: "TD" },
            { key: "tgt", label: "Tgt" },
            { key: "rec", label: "Rec" },
            { key: "rec_yds", label: "Yds" },
        ],
        WR: [
            { key: "tgt", label: "Tgt" },
            { key: "rec", label: "Rec" },
            { key: "rec_yds", label: "Yds" },
            { key: "rec_td", label: "TD" },
        ],
        TE: [
            { key: "tgt", label: "Tgt" },
            { key: "rec", label: "Rec" },
            { key: "rec_yds", label: "Yds" },
            { key: "rec_td", label: "TD" },
        ],
    };

    // group bands over the stat columns (counts must match POS_COLUMNS order)
    const POS_GROUPS = {
        QB: [
            { label: "Passing", span: 5 },
            { label: "Rushing", span: 1 },
        ],
        RB: [
            { label: "Rushing", span: 3 },
            { label: "Receiving", span: 3 },
        ],
        WR: [{ label: "Receiving", span: 4 }],
        TE: [{ label: "Receiving", span: 4 }],
    };

    // Doink-style line label per market (full words for the lines box)
    const LINE_LABELS = {
        pass_att: "Pass Att", pass_cmp: "Cmp", pass_yds: "Pass Yds", pass_td: "Pass TD", pass_int: "INT",
        rush_att: "Rush Att", rush_yds: "Rush Yds", rush_td: "Rush TD",
        tgt: "Targets", rec: "Receptions", rec_yds: "Rec Yds", rec_td: "Rec TD",
    };

    const TEAM_LOGO = (abbr) =>
        abbr ? `https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/${abbr.toLowerCase()}.png` : "";

    // near-even band per stat so tiny gaps stay neutral instead of flashing color
    const THRESHOLDS = {
        pass_att: 1.5, pass_cmp: 1.0, pass_yds: 12, pass_td: 0.15, pass_int: 0.1,
        rush_att: 1.0, rush_yds: 5, rush_td: 0.1,
        tgt: 0.75, rec: 0.5, rec_yds: 5, rec_td: 0.1,
    };

    const state = {
        season: DEFAULT_SEASON,
        week: 1,
        slate: null,
        gameId: null,
        side: "away", // which team's offense is shown on the left
        leagueAvg: null, // per-position league average allowed (from slate defenses)
        cardFilters: {}, // per-player-card log filter: l5 | l10 | l15 | all | opp | home | away
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
            state.week = Number(weekSel.value);
            loadSlate();
        });

        el("nrsRefresh").addEventListener("click", () => loadSlate(true));

        // per-card log filters (delegated: cards re-render on every matchup draw)
        el("nrsPosSections").addEventListener("click", (e) => {
            const btn = e.target.closest(".nrs-log-filter button[data-filter]");
            if (!btn) return;
            const key = btn.closest(".nrs-log-filter").dataset.key;
            state.cardFilters[key] = btn.dataset.filter;
            renderMatchup();
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
        badge.textContent = `Stats: ${state.slate.stats_season} season (nflverse)`;
        el("nrsLastUpdated").textContent = state.slate.fetched_at ? `Updated ${state.slate.fetched_at.replace("T", " ")}` : "";
        el("nrsSeasonNote").textContent =
            `Player averages from the ${state.slate.stats_season} season vs what each defense allowed per game — ` +
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
        state.leagueAvg = computeLeagueAverages(games);
        renderGames();
        renderMatchup();
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
            for (const sideKey of ["away_def_vs_pos", "home_def_vs_pos"]) {
                const defense = game[sideKey] || {};
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
        if (val == null || ref == null) return "";
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

    function fmtStat(val) {
        if (val == null) return "—";
        return Number.isInteger(val) ? String(val) : val.toFixed(1);
    }

    // "W12" for the current year, "W12 '25" when viewing an older season
    function weekLabel(week) {
        if (state.season === new Date().getFullYear()) return `W${week}`;
        return `W${week} '${String(state.season).slice(-2)}`;
    }

    // ── matchup panels: all positions stacked, offense left | defense right ──
    function renderMatchup() {
        const game = currentGame();
        const section = el("nrsMatchupSection");
        if (!game) {
            section.hidden = true;
            return;
        }
        section.hidden = false;

        const offenseIsAway = state.side === "away";
        const offName = offenseIsAway ? game.away_name : game.home_name;
        const offLogo = offenseIsAway ? game.away_logo : game.home_logo;
        const defName = offenseIsAway ? game.home_name : game.away_name;
        const defLogo = offenseIsAway ? game.home_logo : game.away_logo;
        const offense = (offenseIsAway ? game.away_offense : game.home_offense) || {};
        const defense = (offenseIsAway ? game.home_def_vs_pos : game.away_def_vs_pos) || {};

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

        const meta = { offName, offLogo, defName, defLogo, offAbbr, defAbbr };
        const cards = POSITIONS
            .flatMap((pos) => {
                const cols = POS_COLUMNS[pos];
                const defBlock = defense[pos] || { overall: null, ranks: {} };
                return (offense[pos] || []).map((player) => playerCardHtml(pos, cols, player, defBlock, meta));
            })
            .join("");
        el("nrsPosSections").innerHTML =
            defenseOverviewHtml(defense, meta) +
            `<div class="nrs-player-grid">${cards || `<p class="nrs-empty">No player data for ${offName}.</p>`}</div>`;
    }

    // top section: what this defense allows per game vs each position overall
    function defenseOverviewHtml(defense, meta) {
        const logo = meta.defLogo ? `<img class="nrs-def-overview__logo" src="${meta.defLogo}" alt="" loading="lazy">` : "";
        const cards = POSITIONS
            .map((pos) => {
                const overall = (defense[pos] || {}).overall;
                const league = (state.leagueAvg && state.leagueAvg[pos] && state.leagueAvg[pos].overall) || null;
                if (!overall) return "";
                const rows = POS_COLUMNS[pos]
                    .map((col) => {
                        const allowed = overall[col.key];
                        const leagueVal = league ? league[col.key] : null;
                        return `<tr><td class="nrs-stat-label">${LINE_LABELS[col.key] || col.label}</td><td class="nrs-cell"${heatAttr(allowed, leagueVal, col)}>${fmtStat(allowed)}</td></tr>`;
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

    function filterBarHtml(cardKey, active, defAbbr) {
        const options = [
            ["l5", "L5"], ["l10", "L10"], ["l15", "L15"], ["all", "All"],
            ["opp", `vs ${defAbbr}`], ["home", "Home"], ["away", "Away"],
        ];
        const buttons = options
            .map(([f, label]) => `<button type="button" data-filter="${f}"${f === active ? ' class="is-active"' : ""}>${label}</button>`)
            .join("");
        return `<div class="nrs-card-filterbar"><div class="nrs-log-filter nrs-log-filter--card" role="group" aria-label="Game log filter" data-key="${cardKey}">${buttons}</div></div>`;
    }

    function playerCardHtml(pos, cols, player, defBlock, meta) {
        const rank = player.rank;
        const defRow = defForRank(defBlock, rank);
        const league = (state.leagueAvg && state.leagueAvg[pos]) || null;
        const leagueRow = league ? league.ranks[String(rank)] || league.overall : null;
        const lines = player.lines || {};

        const cardKey = `${pos}${rank}-${(player.name || "").replace(/[^a-zA-Z0-9]/g, "")}`;
        const filter = state.cardFilters[cardKey] || DEFAULT_FILTER;

        // "vs OPP": player log vs this defense, defense log vs the player's team
        const playerLog = filterLog(player.log || [], meta.defAbbr, filter);
        const defLog = filterLog((defBlock.rank_logs || {})[String(rank)] || [], meta.offAbbr, filter);

        const groupRow =
            `<tr class="nrs-group-row"><th colspan="3"></th>` +
            POS_GROUPS[pos].map((g) => `<th colspan="${g.span}" class="nrs-group-th">${g.label}</th>`).join("") +
            `</tr>`;
        const statHead = cols.map((c) => `<th>${c.label}</th>`).join("");
        const logHead = `${groupRow}<tr><th>Wk</th><th class="nrs-th-opp">Opp</th><th>W/L</th>${statHead}</tr>`;

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
                        const val = g.stats[col.key];
                        const avg = player.stats ? player.stats[col.key] : null;
                        return `<td class="nrs-cell"${heatAttr(val, avg, col)}>${fmtStat(val)}</td>`;
                    })
                    .join("");
                return `<tr><td class="nrs-log-week">${weekLabel(g.week)}</td><td class="nrs-log-opp">${oppCell(g)}</td>${wlCell(g)}${cells}</tr>`;
            })
            .join("") || `<tr><td colspan="${cols.length + 3}" class="nrs-log-none">No games match this filter.</td></tr>`;

        // avg row: season average colored vs what this defense allows (the matchup)
        const playerAvgCells = cols
            .map((col) => {
                const val = player.stats ? player.stats[col.key] : null;
                const defVal = defRow ? defRow[col.key] : null;
                return `<td class="nrs-cell"${heatAttr(val, defVal, col)}>${fmtStat(val)}</td>`;
            })
            .join("");

        // ── right: defense game log vs this position rank, colored vs league average ──
        const defRows = defLog
            .map((g) => {
                const cells = cols
                    .map((col) => {
                        const val = g.stats[col.key];
                        const leagueVal = leagueRow ? leagueRow[col.key] : null;
                        return `<td class="nrs-cell"${heatAttr(val, leagueVal, col)}>${fmtStat(val)}</td>`;
                    })
                    .join("");
                return `<tr><td class="nrs-log-week">${weekLabel(g.week)}</td><td class="nrs-log-opp" title="${g.player || ""}">${oppCell(g)}</td>${wlCell(g)}${cells}</tr>`;
            })
            .join("") || `<tr><td colspan="${cols.length + 3}" class="nrs-log-none">No games match this filter.</td></tr>`;

        const defAvgCells = cols
            .map((col) => {
                const val = defRow ? defRow[col.key] : null;
                const leagueVal = leagueRow ? leagueRow[col.key] : null;
                return `<td class="nrs-cell"${heatAttr(val, leagueVal, col)}>${fmtStat(val)}</td>`;
            })
            .join("");

        const photo = player.headshot
            ? `<img class="nrs-card__photo" src="${player.headshot}" alt="" loading="lazy" onerror="this.remove()">`
            : "";
        const defLogoImg = meta.defLogo
            ? `<img class="nrs-card__photo nrs-card__photo--logo" src="${meta.defLogo}" alt="" loading="lazy">`
            : "";

        const lineChips = cols
            .filter((col) => lines[col.key] != null)
            .map((col) => `<span class="nrs-line-chip">${LINE_LABELS[col.key] || col.label} <b>${lines[col.key]}</b></span>`);
        if (lines.atd) lineChips.push(`<span class="nrs-line-chip nrs-line-chip--td">Anytime TD <b>${lines.atd}</b></span>`);
        const linesBox = lineChips.length
            ? `<div class="nrs-lines-box"><span class="nrs-lines-box__title">Best lines</span>${lineChips.join("")}</div>`
            : `<div class="nrs-lines-box nrs-lines-box--empty"><span class="nrs-lines-box__title">Best lines</span><span class="nrs-lines-box__none">Not posted yet</span></div>`;

        return (
            `<article class="nrs-matchup-card">` +
            filterBarHtml(cardKey, filter, meta.defAbbr) +
            `<div class="nrs-mc-duo">` +
            `<div class="nrs-mc-panel nrs-mc-panel--player">` +
            `<header class="nrs-mc-panel__head">${photo}<div>` +
            `<span class="nrs-player-card__name">${player.name}</span>` +
            `<span class="nrs-player-card__meta">${pos}${rank} · ${player.gp} games</span>` +
            `</div></header>` +
            `<div class="nrs-table-wrap"><table class="nrs-table nrs-table--log">` +
            `<thead>${logHead}</thead><tbody>${playerRows}</tbody>` +
            `<tfoot><tr><td class="nrs-log-week nrs-log-avg" colspan="3">Avg</td>${playerAvgCells}</tr></tfoot>` +
            `</table></div>` +
            `</div>` +
            `<div class="nrs-mc-panel nrs-mc-panel--def">` +
            `<header class="nrs-mc-panel__head">${defLogoImg}<div>` +
            `<span class="nrs-player-card__name">${meta.defName} Defense</span>` +
            `<span class="nrs-player-card__meta">allows vs ${pos}${rank} each game</span>` +
            `</div></header>` +
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

    // ── boot ──
    document.addEventListener("DOMContentLoaded", () => {
        if (location.protocol === "file:") return;
        initTheme();
        initControls();
        const params = new URLSearchParams(location.search);
        const season = Number(params.get("season"));
        const week = Number(params.get("week"));
        if (SEASONS.includes(season)) {
            state.season = season;
            el("nrsSeason").value = String(season);
        }
        if (week >= 1 && week <= MAX_WEEK) {
            state.week = week;
            el("nrsWeek").value = String(week);
        }
        loadSlate();
    });
})();
