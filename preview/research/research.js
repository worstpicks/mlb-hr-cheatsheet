(function () {
    "use strict";

    function isFileProtocol() {
        return window.location.protocol === "file:";
    }

    function showFileProtocolError() {
        setStatus(
            "Opened as file:// — use python serve-research.py then http://localhost:8080/research/index.html?date=2026-06-23",
            true
        );
    }

    const SAVANT_ONLY = true;

    const MLB_API = "https://statsapi.mlb.com/api/v1";

    const PITCH_LABELS = {
        FF: "4-seam",
        SI: "sinker",
        FC: "cutter",
        SL: "slider",
        CH: "changeup",
        CU: "curve",
        KC: "knuckle-curve",
        ST: "sweeper",
        FS: "splitter",
        SV: "slurve",
    };

    function hitterStats(row) {
        return row?.stats || {};
    }

    const GROUPS = [
        { id: "identity", label: "Lineup", className: "rs-group--identity" },
        { id: "matchup", label: "Pitch mix", className: "rs-group--matchup" },
        { id: "power", label: "Power", className: "rs-group--power" },
        { id: "contact", label: "Contact quality", className: "rs-group--contact" },
        { id: "batted", label: "Batted-ball profile", className: "rs-group--batted" },
        { id: "plate", label: "Plate", className: "rs-group--plate" },
    ];

    const COLS = [
        { key: "order", label: "#", group: "identity", fmt: (r) => r.order ?? "—", tip: "Batting order spot in today's lineup." },
        { key: "name", label: "Hitter", group: "identity", fmt: (r) => r.name, text: true, tip: "Player name and defensive position." },
        { key: "hand", label: "B", group: "identity", fmt: (r) => r.hand || "—", text: true, tip: "Batting hand — L (left), R (right), or S (switch)." },
        { key: "mixPlus", label: "Mix%", group: "matchup", stat: "mixPlus", fmt: (r) => fmtFormPct(hitterStats(r).mixPlus), tip: "Pitch-mix fit — weighted xwOBA vs this starter's pitch usage compared to league average on those pitches. Positive % = favorable matchup." },
        { key: "mixEdge", label: "Edge%", group: "matchup", stat: "mixEdge", fmt: (r) => fmtFormPct(hitterStats(r).mixEdge), tip: "Personal edge — how the hitter performs vs this pitch mix compared to their own season xwOBA. Positive % = better than their baseline." },
        { key: "hr", label: "HR", group: "power", stat: "hr", fmt: (r) => fmtNum(hitterStats(r).hr), tip: "Home runs — balls hit over the fence. Core measure of raw power." },
        { key: "nearHr", label: "Near HR", group: "power", stat: "nearHr", fmt: (r) => fmtNum(hitterStats(r).nearHr), tip: "Near home runs — batted balls with homer distance and trajectory from PropFinder matchup CSVs." },
        { key: "avg", label: "AVG", group: "plate", stat: "avg", fmt: (r) => fmtRate(hitterStats(r).avg), tip: "Batting average — hits divided by at-bats. Overall hitting for average." },
        { key: "iso", label: "ISO", group: "plate", stat: "iso", fmt: (r) => fmtRate(hitterStats(r).iso), tip: "Isolated power — slugging minus average. Extra-base hit power per at-bat." },
        { key: "slg", label: "SLG", group: "plate", stat: "slg", fmt: (r) => fmtRate(hitterStats(r).slg), tip: "Slugging percentage — total bases per at-bat. Measures overall power production." },
        { key: "xwoba", label: "xwOBA", group: "plate", stat: "xwoba", fmt: (r) => fmtRate(hitterStats(r).xwoba), tip: "Expected weighted on-base average — overall offensive value from contact quality, independent of luck." },
        { key: "barrelPct", label: "Barrel%", group: "plate", stat: "barrelPct", fmt: (r) => fmtPct(hitterStats(r).barrelPct), tip: "Barrel rate — batted balls with ideal launch angle and exit velocity to produce homers and extra-base hits." },
        { key: "hardHitPct", label: "Hard Hit%", group: "plate", stat: "hardHitPct", fmt: (r) => fmtPct(hitterStats(r).hardHitPct), tip: "Hard hit rate — share of batted balls at 95+ mph. Measures how often a hitter squares the ball up." },
        { key: "avgEV", label: "EV", group: "plate", stat: "avgEV", fmt: (r) => fmtEv(hitterStats(r).avgEV), tip: "Average exit velocity — how hard the ball is hit on average. Higher EV usually means more power potential." },
        { key: "fbPct", label: "FB%", group: "plate", stat: "fbPct", fmt: (r) => fmtPct(hitterStats(r).fbPct), tip: "Fly ball rate — share of batted balls in the air. Fly-ball hitters tend to have more home run upside." },
        { key: "hrFbPct", label: "HR/FB%", group: "plate", stat: "hrFbPct", fmt: (r) => fmtPct(hitterStats(r).hrFbPct), tip: "Home runs per fly ball — how often fly balls leave the yard. Power efficiency on balls in the air." },
        { key: "recentForm", label: "Form%", group: "plate", stat: "recentForm", fmt: (r) => fmtFormPct(hitterStats(r).recentForm), tip: "Recent form — wOBA vs expected wOBA gap. Positive means outperforming expected contact quality; negative means underperforming." },
        { key: "whiffPct", label: "Whiff%", group: "plate", stat: "whiffPct", fmt: (r) => fmtPct(hitterStats(r).whiffPct), tip: "Whiff rate — swings and misses as a share of swings. Lower is better for contact hitters." },
        { key: "kPct", label: "K%", group: "plate", stat: "kPct", fmt: (r) => fmtPct(hitterStats(r).kPct), tip: "Strikeout rate — strikeouts as a share of plate appearances. Lower is better for contact." },
        { key: "gbPct", label: "GB%", group: "batted", stat: "gbPct", fmt: (r) => fmtPct(hitterStats(r).gbPct), tip: "Ground ball rate — share of batted balls on the ground. Lower rates often correlate with more power and fly balls." },
        { key: "ldPct", label: "LD%", group: "batted", stat: "ldPct", fmt: (r) => fmtPct(hitterStats(r).ldPct), tip: "Line drive rate — share of batted balls hit on a line. A sign of solid, hard contact." },
        { key: "pullPct", label: "Pull%", group: "batted", stat: "pullPct", fmt: (r) => fmtPct(hitterStats(r).pullPct), tip: "Pull rate — share of batted balls hit to the pull side. Higher pull rates often mean more power, especially for same-side matchups." },
    ];

    let slate = null;
    let savantLookup = null;
    let pitchMixCache = null;
    let activeGameIdx = 0;
    let activeSide = "away";
    let sortKey = "order";
    let sortDir = 1;

    const els = {
        status: document.getElementById("rsStatus"),
        games: document.getElementById("rsGames"),
        matchupTitle: document.getElementById("rsMatchupTitle"),
        matchupSp: document.getElementById("rsMatchupSp"),
        tableHead: document.getElementById("rsTableHead"),
        tableBody: document.getElementById("rsTableBody"),
        dateInput: document.getElementById("rsDate"),
        refreshBtn: document.getElementById("rsRefresh"),
        sideAway: document.getElementById("rsSideAway"),
        sideHome: document.getElementById("rsSideHome"),
        sourceBadge: document.getElementById("rsSourceBadge"),
        backLink: document.getElementById("rsBackLink"),
        themeToggle: document.getElementById("rsThemeToggle"),
        mobileSort: document.getElementById("rsMobileSort"),
        cardList: document.getElementById("rsCardList"),
    };

    function isMobileView() {
        return window.matchMedia("(max-width: 640px)").matches;
    }

    function syncThemeToggle() {
        const light = document.documentElement.classList.contains("theme-light");
        if (!els.themeToggle) return;
        els.themeToggle.textContent = light ? "🌙" : "☀️";
        els.themeToggle.setAttribute("aria-pressed", light ? "true" : "false");
        els.themeToggle.title = light ? "Switch to dark mode" : "Switch to light mode";
        els.themeToggle.setAttribute("aria-label", els.themeToggle.title);
    }

    function toggleTheme() {
        const root = document.documentElement;
        const light = root.classList.toggle("theme-light");
        try {
            localStorage.setItem("worstpickz-theme", light ? "light" : "dark");
        } catch (e) {}
        syncThemeToggle();
    }

    function qs(name) {
        return new URLSearchParams(window.location.search).get(name);
    }

    function sheetDateFromQuery() {
        const d = qs("date");
        if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) return d;
        const meta = document.querySelector('meta[name="research-date"]');
        return meta?.content || new Date().toISOString().slice(0, 10);
    }

    function seasonFromDate(date) {
        return parseInt(String(date).slice(0, 4), 10);
    }

    function fmtNum(v) {
        return v == null || v === "" ? "—" : String(v);
    }

    function fmtRate(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        return Number(v).toFixed(3);
    }

    function fmtPct(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        return `${Number(v).toFixed(1)}%`;
    }

    function fmtFormPct(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        const n = Number(v);
        return (n > 0 ? "+" : "") + n.toFixed(1) + "%";
    }

    function fmtPitchCode(code) {
        if (!code) return "—";
        return String(code);
    }

    function mixTipForRow(row) {
        const game = activeGame();
        const pitcher = activeSide === "away" ? game?.homePitcher : game?.awayPitcher;
        const s = hitterStats(row);
        if (s.mixPlus == null || !pitcher?.arsenal) return null;
        const lines = [
            `vs ${pitcher.name || "SP"}: ${pitcher.arsenalLabel || formatArsenal(pitcher.arsenal)}`,
            `Mix% ${fmtFormPct(s.mixPlus)} · Edge% ${fmtFormPct(s.mixEdge)} · mix xwOBA ${s.mixXwoba != null ? Number(s.mixXwoba).toFixed(3) : "—"}`,
        ];
        return lines.join("\n");
    }

    function formatArsenal(arsenal) {
        if (!arsenal) return "";
        return Object.entries(arsenal)
            .sort((a, b) => Number(b[1]) - Number(a[1]))
            .slice(0, 4)
            .map(([pt, usage]) => `${pt} ${Number(usage).toFixed(0)}%`)
            .join(" · ");
    }

    function fmtEv(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        return Number(v).toFixed(1);
    }

    function escAttr(s) {
        return String(s)
            .replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/</g, "&lt;");
    }

    function tipAttr(tip) {
        return tip ? ` class="rs-has-tip" title="${escAttr(tip)}"` : "";
    }

    function sortIndicator(key) {
        if (key !== sortKey) return "";
        const arrow = sortDir > 0 ? "↑" : "↓";
        const dir = sortDir > 0 ? "ascending" : "descending";
        return `<span class="rs-sort-indicator" aria-hidden="true" title="Sorted ${dir}">${arrow}</span>`;
    }

    function fmtTime(iso) {
        if (!iso) return "";
        try {
            const d = new Date(iso);
            const h = d.getHours() % 12 || 12;
            const m = String(d.getMinutes()).padStart(2, "0");
            const ap = d.getHours() < 12 ? "AM" : "PM";
            return `${h}:${m} ${ap} ET`;
        } catch {
            return "";
        }
    }

    function setStatus(msg, isError) {
        if (!els.status) return;
        const text = msg || "";
        els.status.textContent = text;
        els.status.classList.toggle("is-error", !!isError);
        // Only surface the status bar for errors — keep the UI clean when data loads OK.
        els.status.hidden = !(isError && text);
    }

    function clearStatus() {
        setStatus("", false);
    }

    function num(val) {
        if (val == null || val === "" || val === "-") return null;
        const n = parseFloat(String(val).replace("%", ""));
        return Number.isFinite(n) ? n : null;
    }

    async function mlbGet(path) {
        const res = await fetch(`${MLB_API}${path}`);
        if (!res.ok) throw new Error(`MLB API ${res.status}`);
        return res.json();
    }

    function lookupFromSavantPayload(payload) {
        const lookup = {};
        for (const [pid, stats] of Object.entries(payload?.lookup || {})) {
            const id = parseInt(pid, 10);
            if (id) lookup[id] = stats;
        }
        return lookup;
    }

    async function fetchSavantFromProxy(season) {
        const urls = [
            `/.netlify/functions/savant-batter?season=${season}`,
            `/api/savant-batter?season=${season}`,
            `../api/savant-batter?season=${season}`,
        ];
        for (const url of urls) {
            try {
                const res = await fetch(url, { cache: "no-store" });
                if (!res.ok) continue;
                const payload = await res.json();
                const lookup = lookupFromSavantPayload(payload);
                if (Object.keys(lookup).length) return lookup;
            } catch (_) {}
        }
        return null;
    }

    function hasSavantStats(stats) {
        return stats?.avgEV != null || stats?.xwoba != null || stats?.barrelPct != null;
    }

    function lineupsHaveSavant(games) {
        for (const g of games || []) {
            for (const h of [...(g.awayLineup || []), ...(g.homeLineup || [])]) {
                if (hasSavantStats(h.stats)) return true;
            }
        }
        return false;
    }

    function dataFileUrls(filename) {
        const path = window.location.pathname.replace(/\\/g, "/");
        const urls = [];
        const add = (u) => {
            if (u && !urls.includes(u)) urls.push(u);
        };
        add(`/data/${filename}`);
        add(`../data/${filename}`);
        if (path.includes("/research/")) {
            const base = path.slice(0, path.indexOf("/research/"));
            add(`${base}/data/${filename}`);
        }
        add(`/preview/data/${filename}`);
        return urls;
    }

    async function fetchDataJson(filename) {
        if (isFileProtocol()) {
            return { data: null, url: null, lastStatus: "file:// protocol — need http://localhost server" };
        }
        let lastStatus = "no paths tried";
        for (const url of dataFileUrls(filename)) {
            try {
                const res = await fetch(url, { cache: "no-store" });
                lastStatus = `${url} → HTTP ${res.status}`;
                if (!res.ok) continue;
                return { data: await res.json(), url, lastStatus };
            } catch (err) {
                lastStatus = `${url} → ${err.message || err}`;
            }
        }
        return { data: null, url: null, lastStatus };
    }

    function lineupsHavePitchMix(games) {
        for (const g of games || []) {
            for (const h of [...(g.awayLineup || []), ...(g.homeLineup || [])]) {
                if (h.stats?.mixPlus != null) return true;
            }
        }
        return false;
    }

    function normalizeArsenal(raw, minUsage = 5) {
        if (!raw) return {};
        const out = {};
        for (const [pt, usage] of Object.entries(raw)) {
            const u = Number(usage);
            if (!Number.isNaN(u) && u >= minUsage) out[pt] = u;
        }
        return out;
    }

    function scoreBatterVsArsenal(batterId, arsenal, batterPitch, batterOverallXwoba, leagueAvgs) {
        const mix = normalizeArsenal(arsenal);
        if (!mix || !Object.keys(mix).length || !batterId) return null;

        batterPitch = batterPitch || {};
        const baseline = batterOverallXwoba != null ? batterOverallXwoba : 0.32;
        let totalW = 0;
        let weightedXwoba = 0;
        let weightedLeague = 0;
        const edges = [];

        for (const [pt, usagePct] of Object.entries(mix)) {
            const w = usagePct / 100;
            const bStats = batterPitch[pt] || {};
            const pitchesSeen = bStats.pitches || 0;
            let xw = bStats.xwoba;
            if (xw == null || pitchesSeen < 15) xw = baseline;
            const lgXw = leagueAvgs?.[pt]?.xwoba ?? baseline;

            weightedXwoba += w * xw;
            weightedLeague += w * lgXw;
            totalW += w;
            edges.push([pt, xw - lgXw, usagePct]);
        }
        if (totalW <= 0) return null;

        weightedXwoba /= totalW;
        weightedLeague /= totalW;
        const mixPlus = Math.round((weightedXwoba - weightedLeague) * 1000) / 10;
        const mixEdge = Math.round((weightedXwoba - baseline) * 1000) / 10;
        edges.sort((a, b) => b[1] * b[2] - a[1] * a[2]);
        const bestPt = edges[0]?.[0] || null;
        const worstPt = edges.length
            ? edges.reduce((min, cur) => (cur[1] * cur[2] < min[1] * min[2] ? cur : min))[0]
            : null;

        return {
            mixPlus,
            mixEdge,
            mixXwoba: Math.round(weightedXwoba * 1000) / 1000,
            mixBest: bestPt,
            mixWorst: worstPt,
            mixPitches: Object.keys(mix).length,
        };
    }

    function attachPitcherArsenal(pitcher, pitcherArsenalLookup) {
        if (!pitcher) return pitcher;
        const out = { ...pitcher };
        const pid = out.id;
        const arsenal = normalizeArsenal(pitcherArsenalLookup?.[pid] || pitcherArsenalLookup?.[String(pid)]);
        if (Object.keys(arsenal).length) {
            out.arsenal = arsenal;
            out.arsenalLabel = formatArsenal(arsenal);
        }
        return out;
    }

    function enrichHitterPitchMix(row, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap) {
        const enriched = { ...row };
        const stats = { ...(enriched.stats || {}) };
        if (stats.mixPlus != null) {
            enriched.stats = stats;
            return enriched;
        }
        const pid = enriched.id;
        const pitcher = opposingPitcher || {};
        const batterPitch = batterPitchLookup?.[pid] || batterPitchLookup?.[String(pid)] || null;
        const overallXwoba = stats.xwoba ?? savantLookupMap?.[pid]?.xwoba ?? savantLookupMap?.[String(pid)]?.xwoba;
        const mix = scoreBatterVsArsenal(pid, pitcher.arsenal, batterPitch, overallXwoba, leagueAvgs);
        if (mix) Object.assign(stats, mix);
        enriched.stats = stats;
        return enriched;
    }

    function enrichLineupPitchMix(lineup, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap) {
        return (lineup || []).map((row) =>
            enrichHitterPitchMix(row, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap)
        );
    }

    async function ensurePitchMixCaches(season) {
        if (pitchMixCache) return pitchMixCache;
        if (slate?.pitcher_arsenal_lookup && Object.keys(slate.pitcher_arsenal_lookup).length) {
            pitchMixCache = {
                pitcherArsenal: slate.pitcher_arsenal_lookup,
                batterPitch: slate.batter_pitch_lookup || {},
                leagueAvgs: slate.league_pitch_avgs || {},
            };
            return pitchMixCache;
        }
        const [arsenalRes, batterRes] = await Promise.all([
            fetchDataJson(`savant-pitcher-arsenal-${season}.json`),
            fetchDataJson(`savant-batter-pitch-type-${season}.json`),
        ]);
        pitchMixCache = {
            pitcherArsenal: arsenalRes.data?.lookup || {},
            batterPitch: batterRes.data?.lookup || {},
            leagueAvgs: batterRes.data?.leagueAvgs || {},
            lastStatus: `${arsenalRes.lastStatus}; ${batterRes.lastStatus}`,
        };
        return pitchMixCache;
    }

    function savantLookupMapFromSlate() {
        const map = {};
        const src = slate?.savant_lookup || savantLookup || {};
        for (const [k, v] of Object.entries(src)) map[k] = v;
        return map;
    }

    async function applyPitchMixEnrichment(season) {
        if (lineupsHavePitchMix(slate?.games)) return { n: 0, source: "preserve" };
        const caches = await ensurePitchMixCaches(season);
        if (!Object.keys(caches.pitcherArsenal || {}).length) {
            return { n: 0, source: null, lastStatus: caches.lastStatus };
        }
        const savMap = savantLookupMapFromSlate();
        let n = 0;
        for (const game of slate.games || []) {
            game.awayPitcher = attachPitcherArsenal(game.awayPitcher, caches.pitcherArsenal);
            game.homePitcher = attachPitcherArsenal(game.homePitcher, caches.pitcherArsenal);
            game.awayLineup = enrichLineupPitchMix(
                game.awayLineup,
                game.homePitcher,
                caches.batterPitch,
                caches.leagueAvgs,
                savMap
            );
            game.homeLineup = enrichLineupPitchMix(
                game.homeLineup,
                game.awayPitcher,
                caches.batterPitch,
                caches.leagueAvgs,
                savMap
            );
            for (const h of [...(game.awayLineup || []), ...(game.homeLineup || [])]) {
                if (h.stats?.mixPlus != null) n += 1;
            }
        }
        return { n, source: "pitch-mix-cache" };
    }

    function mergePitcher(live, cached) {
        if (!cached) return live || null;
        if (!live) return { ...cached };
        return {
            ...cached,
            ...live,
            arsenal: cached.arsenal || live.arsenal,
            arsenalLabel: cached.arsenalLabel || live.arsenalLabel,
        };
    }

    function applyCachedEnrichment(live, cached) {
        if (!live || !cached) return;
        for (const key of [
            "savant_lookup",
            "propfinder_lookup",
            "pitcher_arsenal_lookup",
            "batter_pitch_lookup",
            "league_pitch_avgs",
            "season",
            "fetched_at",
            "stat_windows",
            "savant_only",
            "source",
        ]) {
            if (cached[key] != null && live[key] == null) live[key] = cached[key];
        }
        const cachedByPk = new Map(
            (cached.games || []).filter((g) => g.gamePk).map((g) => [g.gamePk, g])
        );
        for (const game of live.games || []) {
            const cg = cachedByPk.get(game.gamePk);
            if (!cg) continue;
            game.awayPitcher = mergePitcher(game.awayPitcher, cg.awayPitcher);
            game.homePitcher = mergePitcher(game.homePitcher, cg.homePitcher);
            if (!(game.awayLineup || []).length && (cg.awayLineup || []).length) {
                game.awayLineup = (cg.awayLineup || []).map((r) => ({ ...r, stats: { ...(r.stats || {}) } }));
            }
            if (!(game.homeLineup || []).length && (cg.homeLineup || []).length) {
                game.homeLineup = (cg.homeLineup || []).map((r) => ({ ...r, stats: { ...(r.stats || {}) } }));
            }
            for (const side of ["awayLineup", "homeLineup"]) {
                const cachedById = new Map((cg[side] || []).filter((r) => r.id).map((r) => [r.id, r]));
                game[side] = (game[side] || []).map((row) => {
                    const prev = cachedById.get(row.id);
                    if (!prev?.stats) return row;
                    return {
                        ...prev,
                        ...row,
                        stats: { ...(prev.stats || {}), ...(row.stats || {}) },
                        hand: row.hand || prev.hand,
                    };
                });
            }
        }
    }

    async function ensureBatterHands() {
        const needIds = [];
        for (const g of slate?.games || []) {
            for (const r of [...(g.awayLineup || []), ...(g.homeLineup || [])]) {
                if (r?.id && !r.hand) needIds.push(r.id);
            }
        }
        const unique = [...new Set(needIds)];
        if (!unique.length) return;
        const lookup = {};
        for (let i = 0; i < unique.length; i += 50) {
            const chunk = unique.slice(i, i + 50);
            try {
                const data = await mlbGet(`/people?personIds=${chunk.join(",")}`);
                for (const person of data.people || []) {
                    const hand = person.batSide?.code;
                    if (person.id && hand) lookup[person.id] = hand;
                }
            } catch (err) {
                console.warn("batter hands", err);
            }
        }
        for (const g of slate.games || []) {
            for (const key of ["awayLineup", "homeLineup"]) {
                g[key] = (g[key] || []).map((row) => {
                    if (row.hand || !row.id) return row;
                    const hand = lookup[row.id];
                    return hand ? { ...row, hand } : row;
                });
            }
        }
    }

    async function mergeSavantIntoAllLineups(season) {
        const cached = await fetchDataJson(`savant-batter-${season}.json`);
        if (cached.data?.lookup) {
            slate.savant_lookup = { ...(slate?.savant_lookup || {}), ...cached.data.lookup };
            savantLookup = lookupFromSavantPayload({ lookup: slate.savant_lookup });
        } else if (slate?.savant_lookup && Object.keys(slate.savant_lookup).length) {
            savantLookup = lookupFromSavantPayload({ lookup: slate.savant_lookup });
        }

        if (slate?.savant_lookup && Object.keys(slate.savant_lookup).length) {
            const patched = applySavantFromSlate();
            if (lineupsHavePitchMix(slate?.games)) {
                return { n: patched, source: patched ? "patch-savant-gaps" : "preserve-enriched" };
            }
            if (patched > 0) return { n: patched, source: cached.url || "embedded" };
        }

        savantLookup = null;
        const lookup = await loadSavantLookup(season);
        if (!Object.keys(lookup).length) {
            return { n: 0, source: null, lastStatus: cached.lastStatus };
        }
        let n = 0;
        for (const game of slate.games || []) {
            for (const key of ["awayLineup", "homeLineup"]) {
                game[key] = (game[key] || []).map((row) => {
                    const sav = lookup[row.id] || lookup[String(row.id)];
                    if (!sav) return row;
                    n += 1;
                    return {
                        ...row,
                        stats: mergeStats(
                            SAVANT_ONLY ? {} : row.stats || {},
                            sav,
                            propfinderLookupFromSlate()[nameLookupKey(row.name)] || null,
                            row.stats
                        ),
                    };
                });
            }
        }
        return { n, source: "proxy/cache" };
    }

    async function loadSavantLookup(season) {
        if (savantLookup) return savantLookup;

        if (slate?.savant_lookup && Object.keys(slate.savant_lookup).length) {
            savantLookup = lookupFromSavantPayload({ lookup: slate.savant_lookup });
            if (Object.keys(savantLookup).length) return savantLookup;
        }

        const cached = await fetchDataJson(`savant-batter-${season}.json`);
        if (cached.data?.lookup) {
            savantLookup = lookupFromSavantPayload(cached);
            return savantLookup;
        }

        const proxied = await fetchSavantFromProxy(season);
        if (proxied) {
            savantLookup = proxied;
            return savantLookup;
        }

        console.warn("Savant unavailable — run fetch-research-slate.py or serve-research.py");
        savantLookup = {};
        return savantLookup;
    }

    function mergeStats(windowStats, savant, propfinder, existing) {
        const out = { ...(existing || {}) };
        const sav = savant || {};
        const savantKeys = [
            "avg",
            "slg",
            "iso",
            "xwoba",
            "barrelPct",
            "hardHitPct",
            "avgEV",
            "fbPct",
            "gbPct",
            "ldPct",
            "hrFbPct",
            "whiffPct",
            "kPct",
            "hr",
            "recentForm",
            "pullPct",
            "pullAirPct",
            "pullBarrelPct",
        ];
        for (const k of savantKeys) {
            if (sav[k] != null) out[k] = sav[k];
        }
        if (SAVANT_ONLY) {
            const pf = propfinder || {};
            if (pf.nearHr != null) out.nearHr = pf.nearHr;
            if (out.kPct == null && pf.kPct != null) out.kPct = pf.kPct;
            const sources = [out.source || sav.source || "savant"];
            if (pf.nearHr != null || pf.kPct != null) sources.push("propfinder");
            out.source = [...new Set(sources.filter(Boolean))].join("+");
            return out;
        }
        const win = windowStats || {};
        const pf = propfinder || {};
        for (const k of ["hr", "hits", "ab"]) {
            if (win[k] != null) out[k] = win[k];
        }
        if (out.hr == null && sav.hr != null) out.hr = sav.hr;
        if (pf.nearHr != null) out.nearHr = pf.nearHr;
        for (const k of ["obp", "slg", "kPct", "bbPct"]) {
            if (win[k] != null) out[k] = win[k];
        }
        const sources = ["savant"];
        if (Object.keys(win).length) sources.push("mlb-window");
        if (Object.keys(pf).length) sources.push("propfinder");
        out.source = sources.join("+");
        return out;
    }

    function windowBounds(sheetDate, days = 30) {
        const end = new Date(sheetDate + "T12:00:00");
        const start = new Date(end);
        start.setDate(start.getDate() - days);
        return { start: start.toISOString().slice(0, 10), end: sheetDate };
    }

    async function mlbWindowStats(playerId, season, start, end) {
        for (const yr of [season, season - 1]) {
            try {
                const hydrate = encodeURIComponent(
                    `stats(group=[hitting],type=[byDateRange],startDate=${start},endDate=${end},season=${yr})`
                );
                const data = await mlbGet(`/people/${playerId}?hydrate=${hydrate}`);
                const groups = data.people?.[0]?.stats || [];
                for (const g of groups) {
                    const stat = g.splits?.[0]?.stat;
                    if (!stat) continue;
                    const avg = num(stat.avg);
                    const slg = num(stat.slg);
                    const pa = num(stat.plateAppearances);
                    const k = num(stat.strikeOuts);
                    const bb = num(stat.baseOnBalls);
                    return {
                        hr: num(stat.homeRuns),
                        hits: num(stat.hits),
                        ab: num(stat.atBats),
                        pa,
                        avg,
                        obp: num(stat.obp),
                        slg,
                        iso: avg != null && slg != null ? +(slg - avg).toFixed(3) : null,
                        kPct: pa && k != null ? +((100 * k) / pa).toFixed(1) : null,
                        bbPct: pa && bb != null ? +((100 * bb) / pa).toFixed(1) : null,
                        source: "mlb-window",
                    };
                }
            } catch (_) {}
        }
        return {};
    }

    async function loadCachedJson(date) {
        const result = await fetchDataJson(`research-${date}.json`);
        return result.data;
    }

    async function fetchTeamHitters(teamId, rosterSeason) {
        for (const yr of [rosterSeason, rosterSeason - 1, null]) {
            let path = `/teams/${teamId}/roster?rosterType=active`;
            if (yr != null) path += `&season=${yr}`;
            try {
                const data = await mlbGet(path);
                const entries = data.roster || data.rosters || [];
                const list = entries
                    .filter((e) => (e.position?.abbreviation || "") !== "P")
                    .map((e) => ({
                        id: e.person?.id,
                        name: e.person?.fullName || "",
                        hand: e.person?.batSide?.code || "",
                        position: e.position?.abbreviation || "",
                        projected: true,
                    }));
                if (list.length) return list;
            } catch (_) {}
        }
        return [];
    }

    function propfinderLookupFromSlate() {
        return slate?.propfinder_lookup && typeof slate.propfinder_lookup === "object"
            ? slate.propfinder_lookup
            : {};
    }

    function applyPropfinderToAllLineups(lookup) {
        if (!lookup || !Object.keys(lookup).length) return 0;
        let n = 0;
        for (const game of slate.games || []) {
            for (const key of ["awayLineup", "homeLineup"]) {
                game[key] = (game[key] || []).map((row) => {
                    const pf = lookup[nameLookupKey(row.name)];
                    if (pf?.nearHr == null) return row;
                    n += 1;
                    return {
                        ...row,
                        stats: mergeStats({}, null, pf, row.stats),
                    };
                });
            }
        }
        return n;
    }

    async function ensurePropfinderLookup(date) {
        const existing = propfinderLookupFromSlate();
        if (Object.keys(existing).length) return existing;
        try {
            const res = await fetch(`/api/propfinder?date=${encodeURIComponent(date)}`);
            if (!res.ok) return {};
            const data = await res.json();
            if (data.lookup && Object.keys(data.lookup).length) {
                slate.propfinder_lookup = data.lookup;
                return data.lookup;
            }
        } catch (err) {
            console.warn("propfinder", err);
        }
        return {};
    }

    async function enrichLineup(lineup, season, lookup, windowRange, propfinderLookup) {
        const out = [];
        const pfLookup = propfinderLookup || propfinderLookupFromSlate();
        for (const row of lineup) {
            const pid = row.id;
            const sav = lookup?.[pid] || lookup?.[String(pid)] || null;
            if (SAVANT_ONLY) {
                const pf = pfLookup?.[nameLookupKey(row.name)] || null;
                out.push({ ...row, stats: mergeStats({}, sav, pf, row.stats) });
                continue;
            }
            let win = row.stats || {};
            if (win.hits == null && pid) {
                win = await mlbWindowStats(pid, season, windowRange.start, windowRange.end);
            }
            const pf = propfinderLookup?.[nameLookupKey(row.name)] || null;
            const near = win.nearHr != null ? { nearHr: win.nearHr } : pf;
            out.push({ ...row, stats: mergeStats(win, sav, near) });
        }
        return out;
    }

    function applySavantFromSlate() {
        if (!slate?.savant_lookup) return 0;
        let n = 0;
        for (const game of slate.games || []) {
            for (const key of ["awayLineup", "homeLineup"]) {
                game[key] = (game[key] || []).map((row) => {
                    const sav = slate.savant_lookup[String(row.id)] || slate.savant_lookup[row.id];
                    if (!sav) return row;
                    n += 1;
                    const win = row.stats || {};
                    const pf = propfinderLookupFromSlate()[nameLookupKey(row.name)] || null;
                    return {
                        ...row,
                        stats: mergeStats(SAVANT_ONLY ? {} : win, sav, pf, row.stats),
                    };
                });
            }
        }
        return n;
    }

    async function finalizeSlateStats(season, sheetDate) {
        const embedded = applySavantFromSlate();
        if (embedded > 0) {
            savantLookup = lookupFromSavantPayload({ lookup: slate.savant_lookup });
            return embedded;
        }

        const windowRange = slate?.window_start && slate?.window_end
            ? { start: slate.window_start, end: slate.window_end }
            : windowBounds(sheetDate);
        const lookup = await loadSavantLookup(season);
        const propfinderLookup = propfinderLookupFromSlate();
        for (const game of slate.games || []) {
            game.awayLineup = await enrichLineup(game.awayLineup || [], season, lookup, windowRange, propfinderLookup);
            game.homeLineup = await enrichLineup(game.homeLineup || [], season, lookup, windowRange, propfinderLookup);
        }
        return Object.keys(lookup).length;
    }

    function nameLookupKey(name) {
        return String(name || "")
            .replace(/\s+(LHB|RHB|SHB)\s*$/i, "")
            .replace(/^\d+\s+/, "")
            .toLowerCase()
            .replace(/\./g, "")
            .replace(/\s+/g, " ")
            .trim();
    }

    async function buildProjectedLineup(teamId, season, lookup, windowRange, propfinderLookup, limit = 13) {
        const rosterSeason = season;
        let hitters = await fetchTeamHitters(teamId, rosterSeason);
        hitters.sort((a, b) => {
            const sa = lookup?.[a.id] || {};
            const sb = lookup?.[b.id] || {};
            return (sb.pa || 0) - (sa.pa || 0) || (sb.hr || 0) - (sa.hr || 0);
        });
        const lineup = hitters.slice(0, limit).map((h, i) => ({ ...h, order: i + 1 }));
        return enrichLineup(lineup, season, lookup, windowRange, propfinderLookup);
    }

    async function hydrateGameSide(game, side, season, lookup, windowRange, propfinderLookup) {
        const key = side === "away" ? "awayLineup" : "homeLineup";
        const teamId = side === "away" ? game.awayTeamId : game.homeTeamId;
        let lineup = game[key] || [];
        const fullyEnriched =
            lineup.length > 0 &&
            lineup.every((h) => h.stats?.mixPlus != null && hasSavantStats(h.stats));
        if (fullyEnriched) return;
        if (!lineup.length && teamId) {
            game[key] = await buildProjectedLineup(teamId, season, lookup, windowRange, propfinderLookup);
        } else {
            game[key] = await enrichLineup(lineup, season, lookup, windowRange, propfinderLookup);
        }
    }

    async function hydrateAllGames(season, sheetDate) {
        const lookup = await loadSavantLookup(season);
        const windowRange = slate?.window_start && slate?.window_end
            ? { start: slate.window_start, end: slate.window_end }
            : windowBounds(sheetDate);
        const propfinderLookup = propfinderLookupFromSlate();
        for (const game of slate.games || []) {
            if (game.gamePk) {
                try {
                    const box = await mlbGet(`/game/${game.gamePk}/boxscore`);
                    for (const side of ["away", "home"]) {
                        const team = box.teams?.[side] || {};
                        const order = team.battingOrder || [];
                        if (!order.length) continue;
                        const players = team.players || {};
                        const key = side === "away" ? "awayLineup" : "homeLineup";
                        const prev = game[key] || [];
                        const byId = new Map(prev.map((h) => [h.id, h]));
                        game[key] = order.map((pid, i) => {
                            const pl = players[`ID${pid}`] || {};
                            const id = pl.person?.id;
                            const old = byId.get(id);
                            return {
                                id,
                                name: pl.person?.fullName || old?.name || "",
                                order: i + 1,
                                position: pl.position?.abbreviation || old?.position || "",
                                hand: pl.batSide?.code || old?.hand || "",
                                projected: false,
                                stats: old?.stats || {},
                            };
                        });
                    }
                } catch (err) {
                    console.warn("boxscore", game.gamePk, err);
                }
            }
            await hydrateGameSide(game, "away", season, lookup, windowRange, propfinderLookup);
            await hydrateGameSide(game, "home", season, lookup, windowRange, propfinderLookup);
            const awayP = (game.awayLineup || []).some((h) => !h.projected);
            const homeP = (game.homeLineup || []).some((h) => !h.projected);
            game.lineupStatus =
                awayP && homeP ? "confirmed" : awayP || homeP ? "partial" : game.awayLineup?.length || game.homeLineup?.length ? "projected" : "empty";
        }
    }

    async function fetchLiveSlate(date) {
        const data = await mlbGet(
            `/schedule?sportId=1&date=${encodeURIComponent(date)}&hydrate=probablePitcher,team,venue`
        );
        const games = [];
        for (const day of data.dates || []) {
            for (const g of day.games || []) {
                const awayT = g.teams?.away?.team || {};
                const homeT = g.teams?.home?.team || {};
                const awayP = g.teams?.away?.probablePitcher;
                const homeP = g.teams?.home?.probablePitcher;
                games.push({
                    gamePk: g.gamePk,
                    matchup: `${awayT.abbreviation} @ ${homeT.abbreviation}`,
                    away: awayT.abbreviation,
                    home: homeT.abbreviation,
                    awayTeamId: awayT.id,
                    homeTeamId: homeT.id,
                    startTime: g.gameDate,
                    venue: g.venue?.name || "",
                    status: g.status?.detailedState || "",
                    awayPitcher: awayP ? { id: awayP.id, name: awayP.fullName, throws: awayP.pitchHand?.code } : null,
                    homePitcher: homeP ? { id: homeP.id, name: homeP.fullName, throws: homeP.pitchHand?.code } : null,
                    awayLineup: [],
                    homeLineup: [],
                    lineupStatus: "projected",
                });
            }
        }
        games.sort((a, b) => (a.startTime || "").localeCompare(b.startTime || ""));
        return { sheet_date: date, source: "mlb+savant", enriched: false, games };
    }

    function pickDefaultSide() {
        const game = slate?.games?.[activeGameIdx];
        if (!game) return;
        const awayN = (game.awayLineup || []).length;
        const homeN = (game.homeLineup || []).length;
        if (activeSide === "away" && !awayN && homeN) activeSide = "home";
        else if (activeSide === "home" && !homeN && awayN) activeSide = "away";
        else if (!awayN && !homeN) activeSide = "away";
    }

    function activeGame() {
        return slate?.games?.[activeGameIdx] || null;
    }

    function activeRows() {
        const game = activeGame();
        if (!game) return [];
        return activeSide === "away" ? game.awayLineup || [] : game.homeLineup || [];
    }

    function heatClass(values, val, higherBetter) {
        const nums = values.filter((v) => v != null && !Number.isNaN(v));
        if (!nums.length || val == null || Number.isNaN(val)) return "";
        const min = Math.min(...nums);
        const max = Math.max(...nums);
        if (min === max) return "rs-cell-heat rs-cell-heat--mid";
        const t = (val - min) / (max - min);
        const score = higherBetter ? t : 1 - t;
        if (score >= 0.66) return "rs-cell-heat rs-cell-heat--good";
        if (score >= 0.33) return "rs-cell-heat rs-cell-heat--mid";
        return "rs-cell-heat rs-cell-heat--bad";
    }

    function renderGames() {
        if (!els.games || !slate?.games) return;
        els.games.innerHTML = slate.games
            .map((g, i) => {
                const time = fmtTime(g.startTime);
                const sp = `${g.awayPitcher?.name || "?"} vs ${g.homePitcher?.name || "?"}`;
                const nAway = (g.awayLineup || []).length;
                const nHome = (g.homeLineup || []).length;
                return `<button type="button" class="rs-game-pill${i === activeGameIdx ? " is-active" : ""}" data-idx="${i}">
                    <span class="rs-game-pill__matchup">${g.matchup}</span>
                    <span class="rs-game-pill__meta">${time}${time ? " · " : ""}${g.lineupStatus || ""} · ${nAway}/${nHome} hitters</span>
                    <span class="rs-game-pill__meta">${sp}</span>
                </button>`;
            })
            .join("");
        els.games.querySelectorAll(".rs-game-pill").forEach((btn) => {
            btn.addEventListener("click", () => {
                activeGameIdx = parseInt(btn.getAttribute("data-idx"), 10);
                pickDefaultSide();
                renderAll();
            });
        });
    }

    function renderMatchupBar() {
        const game = activeGame();
        if (!game || !els.matchupTitle) return;
        const offense = activeSide === "away" ? game.away : game.home;
        const pitcher = activeSide === "away" ? game.homePitcher : game.awayPitcher;
        const rows = activeRows();
        const projected = rows.length && rows.every((r) => r.projected);
        els.matchupTitle.textContent = `${offense} hitters${projected ? " (proj)" : ""}`;
        if (els.matchupSp) {
            const mix = pitcher?.arsenalLabel || formatArsenal(pitcher?.arsenal);
            els.matchupSp.textContent = pitcher?.name
                ? `vs ${pitcher.name}${mix ? ` · ${mix}` : ""}`
                : "vs TBD";
        }
        if (els.sideAway) {
            els.sideAway.textContent = game.away;
            els.sideAway.classList.toggle("is-active", activeSide === "away");
        }
        if (els.sideHome) {
            els.sideHome.textContent = game.home;
            els.sideHome.classList.toggle("is-active", activeSide === "home");
        }
    }

    function sortedActiveRows() {
        let rows = activeRows();
        const col = COLS.find((c) => c.key === sortKey);
        if (!col) return rows;
        return [...rows].sort((a, b) => {
            if (col.text) return sortDir * String(col.fmt(a)).localeCompare(String(col.fmt(b)));
            const av = col.stat ? hitterStats(a)[col.stat] : a[sortKey];
            const bv = col.stat ? hitterStats(b)[col.stat] : b[sortKey];
            return sortDir * ((av == null ? -Infinity : Number(av)) - (bv == null ? -Infinity : Number(bv)));
        });
    }

    function statHeatMap(rows) {
        const statCols = COLS.filter((c) => c.stat);
        const higherBetter = {
            mixPlus: true,
            mixEdge: true,
            hr: true,
            nearHr: true,
            avg: true,
            iso: true,
            slg: true,
            xwoba: true,
            barrelPct: true,
            hardHitPct: true,
            avgEV: true,
            fbPct: true,
            hrFbPct: true,
            recentForm: true,
            gbPct: false,
            ldPct: true,
            pullPct: true,
            whiffPct: false,
            kPct: false,
        };
        return {
            colValues: Object.fromEntries(
                statCols.map((c) => [
                    c.key,
                    rows.map((r) => Number(hitterStats(r)[c.stat])).filter((n) => !Number.isNaN(n)),
                ])
            ),
            higherBetter,
        };
    }

    function syncMobileSortSelect() {
        if (!els.mobileSort) return;
        const options = COLS.filter((c) => c.key !== "order").map((c) => {
            const selected = c.key === sortKey ? " selected" : "";
            return `<option value="${c.key}"${selected}>${c.label}</option>`;
        });
        els.mobileSort.innerHTML = options.join("");
    }

    function renderMobileCards() {
        if (!els.cardList) return;
        const rows = sortedActiveRows();
        if (!rows.length) {
            els.cardList.innerHTML = `<p class="rs-empty">Loading hitters… try Refresh API or pick the other team.</p>`;
            return;
        }
        const { colValues, higherBetter } = statHeatMap(rows);
        const cardGroups = GROUPS.filter((g) => g.id !== "identity");
        els.cardList.innerHTML = rows
            .map((row) => {
                const projected = row.projected ? '<span class="rs-hand rs-hand--proj">proj</span>' : "";
                const sections = cardGroups
                    .map((group) => {
                        const cols = COLS.filter((c) => c.group === group.id && c.stat);
                        if (!cols.length) return "";
                        const stats = cols
                            .map((c) => {
                                const val = hitterStats(row)[c.stat];
                                const heat =
                                    val != null
                                        ? heatClass(colValues[c.key], Number(val), higherBetter[c.key] !== false)
                                        : "";
                                return `<div class="rs-card-stat"><dt>${c.label}</dt><dd><span class="${heat}">${c.fmt(row)}</span></dd></div>`;
                            })
                            .join("");
                        return `<section class="rs-card__section rs-card__section--${group.id}"><h3 class="rs-card__section-title">${group.label}</h3><dl class="rs-card__stats">${stats}</dl></section>`;
                    })
                    .join("");
                return `<article class="rs-card">
                    <header class="rs-card__head">
                        <span class="rs-card__order">${row.order ?? "—"}</span>
                        <div class="rs-card__identity">
                            <div class="rs-card__name">${row.name || "—"} <span class="rs-hand">${row.position || ""}</span>${projected}</div>
                            <div class="rs-card__meta">Bats ${row.hand || "—"}</div>
                        </div>
                    </header>
                    ${sections}
                </article>`;
            })
            .join("");
        els.cardList.querySelectorAll(".rs-cell-heat--good").forEach((el) => {
            el.style.background = "var(--rs-good-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(134, 239, 172, 0.35)";
        });
        els.cardList.querySelectorAll(".rs-cell-heat--mid").forEach((el) => {
            el.style.background = "var(--rs-mid-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(253, 224, 71, 0.25)";
        });
        els.cardList.querySelectorAll(".rs-cell-heat--bad").forEach((el) => {
            el.style.background = "var(--rs-bad-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(252, 165, 165, 0.25)";
        });
    }

    function renderTable() {
        if (!els.tableHead || !els.tableBody) return;
        const rows = sortedActiveRows();

        els.tableHead.innerHTML = buildTableHeadHtml();

        els.tableHead.querySelectorAll("tr.rs-col-row th").forEach((th) => {
            th.addEventListener("click", () => {
                const key = th.getAttribute("data-key");
                if (sortKey === key) sortDir *= -1;
                else {
                    sortKey = key;
                    sortDir = key === "name" ? 1 : -1;
                }
                renderTable();
                renderMobileCards();
                syncMobileSortSelect();
            });
        });

        if (!rows.length) {
            els.tableBody.innerHTML = `<tr><td colspan="${COLS.length}" class="rs-empty">Loading hitters… try Refresh API or pick the other team.</td></tr>`;
            return;
        }

        const { colValues, higherBetter } = statHeatMap(rows);

        els.tableBody.innerHTML = rows
            .map((r) => {
                const cells = COLS.map((c) => {
                    if (c.key === "name") {
                        const tag = r.projected ? ' <span class="rs-hand">proj</span>' : "";
                        const tip = c.tip ? tipAttr(c.tip) : "";
                        return `<td${tip}><span class="rs-hitter">${r.name || "—"}</span> <span class="rs-hand">${r.position || ""}</span>${tag}</td>`;
                    }
                    const val = c.stat ? hitterStats(r)[c.stat] : r[c.key];
                    const heat =
                        c.stat && val != null ? heatClass(colValues[c.key], Number(val), higherBetter[c.key] !== false) : "";
                    const mixTip = c.key.startsWith("mix") ? mixTipForRow(r) : null;
                    const tip = mixTip ? tipAttr(mixTip) : c.tip ? tipAttr(c.tip) : "";
                    return `<td${tip}><span class="${heat}">${c.fmt(r)}</span></td>`;
                }).join("");
                return `<tr>${cells}</tr>`;
            })
            .join("");

        document.querySelectorAll(".rs-cell-heat--good").forEach((el) => {
            el.style.background = "var(--rs-good-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(134, 239, 172, 0.35)";
        });
        document.querySelectorAll(".rs-cell-heat--mid").forEach((el) => {
            el.style.background = "var(--rs-mid-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(253, 224, 71, 0.25)";
        });
        document.querySelectorAll(".rs-cell-heat--bad").forEach((el) => {
            el.style.background = "var(--rs-bad-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(252, 165, 165, 0.25)";
        });
    }

    function buildTableHeadHtml() {
        const groupCells = [];
        let i = 0;
        while (i < COLS.length) {
            const gid = COLS[i].group;
            let span = 1;
            while (i + span < COLS.length && COLS[i + span].group === gid) span += 1;
            const meta = GROUPS.find((g) => g.id === gid) || { label: gid, className: "" };
            groupCells.push(
                `<th colspan="${span}" class="${meta.className}">${meta.label}</th>`
            );
            i += span;
        }
        const colCells = COLS.map((c) => {
            const colClass =
                c.group === "batted"
                    ? " rs-col--batted"
                    : c.group === "contact"
                      ? " rs-col--contact"
                      : c.group === "matchup"
                        ? " rs-col--matchup"
                        : "";
            const sort =
                c.key === sortKey ? (sortDir > 0 ? "ascending" : "descending") : "none";
            const tip = c.tip ? ` title="${escAttr(c.tip)}"` : "";
            const tipClass = c.tip ? " rs-has-tip" : "";
            const sortedClass = c.key === sortKey ? " rs-col--sorted" : "";
            return `<th class="${colClass.trim()}${tipClass}${sortedClass}" data-key="${c.key}" aria-sort="${sort}"${tip}>${c.label}${sortIndicator(c.key)}</th>`;
        }).join("");
        return `<tr class="rs-group-row">${groupCells.join("")}</tr><tr class="rs-col-row">${colCells}</tr>`;
    }

    function renderSourceBadge() {
        if (!els.sourceBadge) return;
        els.sourceBadge.style.display = "none";
    }

    function renderAll() {
        pickDefaultSide();
        renderGames();
        renderMatchupBar();
        renderTable();
        renderMobileCards();
        syncMobileSortSelect();
        renderSourceBadge();
        clearStatus();
    }

    async function loadSlate(date, forceLive) {
        if (isFileProtocol()) {
            showFileProtocolError();
            return;
        }
        savantLookup = null;
        pitchMixCache = null;
        if (els.dateInput) els.dateInput.value = date;
        if (els.backLink) els.backLink.href = `../index.html`;

        clearStatus();
        const cacheResult = await fetchDataJson(`research-${date}.json`);

        if (forceLive) {
            const cached = cacheResult.data;
            slate = await fetchLiveSlate(date);
            if (cached) applyCachedEnrichment(slate, cached);
        } else {
            slate = cacheResult.data;
        }
        if (!slate) slate = await fetchLiveSlate(date);
        if (!slate?.games?.length) {
            setStatus(`No MLB games found for ${date}.`, true);
            return;
        }

        const season = seasonFromDate(date);
        const needsHydrate = forceLive || !lineupsHaveSavant(slate.games);

        if (needsHydrate) {
            if (slate?.fetched_at && slate?.savant_lookup && !lineupsHaveSavant(slate.games)) {
                applySavantFromSlate();
            }
            await hydrateAllGames(season, date);
        }

        const savantMerge = await mergeSavantIntoAllLineups(season);
        const pitchMixMerge = await applyPitchMixEnrichment(season);
        const pfLookup = await ensurePropfinderLookup(date);
        applyPropfinderToAllLineups(pfLookup);
        await ensureBatterHands();

        activeGameIdx = Math.min(activeGameIdx, slate.games.length - 1);
        pickDefaultSide();
        renderAll();

        if (!lineupsHaveSavant(slate.games)) {
            const hint = cacheResult.lastStatus || savantMerge.lastStatus || "unknown";
            setStatus(
                `Savant stats missing for ${date}. Data file: ${hint}. From repo folder run: python fetch-research-slate.py --date ${date} then python serve-research.py — open http://localhost:8080/research/index.html?date=${date}`,
                true
            );
            return;
        }

        if (!lineupsHavePitchMix(slate.games)) {
            setStatus(
                `Pitch mix unavailable for ${date} — starter arsenal or batter pitch-type cache missing. Run: python fetch-research-slate.py --date ${date}`,
                true
            );
            return;
        }

        clearStatus();
    }

    function wireUi() {
        els.refreshBtn?.addEventListener("click", () => {
            const date = els.dateInput?.value || sheetDateFromQuery();
            loadSlate(date, true).catch((e) => setStatus(String(e.message || e), true));
        });
        els.dateInput?.addEventListener("change", () => {
            const date = els.dateInput.value;
            if (!date) return;
            const url = new URL(window.location.href);
            url.searchParams.set("date", date);
            window.history.replaceState({}, "", url);
            loadSlate(date, false).catch((e) => setStatus(String(e.message || e), true));
        });
        els.sideAway?.addEventListener("click", () => {
            activeSide = "away";
            renderAll();
        });
        els.sideHome?.addEventListener("click", () => {
            activeSide = "home";
            renderAll();
        });
        els.mobileSort?.addEventListener("change", () => {
            sortKey = els.mobileSort.value || "order";
            sortDir = sortKey === "name" ? 1 : -1;
            renderTable();
            renderMobileCards();
        });
        window.matchMedia("(max-width: 640px)").addEventListener("change", () => {
            syncMobileSortSelect();
        });
        els.themeToggle?.addEventListener("click", toggleTheme);
        syncThemeToggle();
    }

    wireUi();
    loadSlate(sheetDateFromQuery(), false).catch((e) => setStatus(String(e.message || e), true));
})();
