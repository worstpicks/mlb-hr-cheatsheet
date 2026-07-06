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
        const stats = row?.stats || {};
        if (stats.airPct == null && stats.fbPct != null && stats.ldPct != null) {
            return { ...stats, airPct: Math.round((Number(stats.fbPct) + Number(stats.ldPct)) * 10) / 10 };
        }
        return stats;
    }

    /**
     * Worst Pickz HR research scoring weights.
     */
    const HR_RESEARCH_CONFIG = {
        ticketVersion: 2,
        ticket: {
            pillars: {
                mix: 0.3,
                pitcher: 0.25,
                environment: 0.15,
                form: 0.2,
                power: 0.1,
            },
        },
        explore: {
            sort: "ticketRank",
            hand: "",
            minScore: "",
            minPark: "",
            topHitters: 25,
            topPitchers: 8,
            minPitcherRisk: 50,
        },
        pillars: [
            { id: "mix", label: "Pitch-mix fit", metrics: "Savant xwOBA vs starter arsenal + platoon split vs SP hand" },
            { id: "pitcher", label: "Pitcher leak", metrics: "Hand-specific dinger risk vs SP" },
            { id: "environment", label: "HR environment", metrics: "Park + weather + wind + dimensions" },
            { id: "form", label: "HR form", metrics: "Due+, near-HR, rolling HR rate, contact shape" },
            { id: "power", label: "Power contact", metrics: "Barrel%, hard-hit%, air rate" },
        ],
    };

    const ESSENTIAL_COL_KEYS = [
        "order",
        "name",
        "hand",
        "ticketScore",
        "mixPlus",
        "mixEdge",
        "matchWhiffPct",
        "hrEnv",
        "hrFormPct",
        "boomPct",
        "barrelPct",
        "nearHr",
    ];
    const TABLE_VIEW_STORAGE_KEY = "research-hitter-table-view-v2";

    const GROUPS = [
        { id: "identity", label: "Lineup", className: "rs-group--identity" },
        { id: "matchup", label: "Pitch mix", className: "rs-group--matchup" },
        { id: "power", label: "Power", className: "rs-group--power" },
        { id: "contact", label: "Contact quality", className: "rs-group--contact" },
        { id: "batted", label: "Batted-ball profile", className: "rs-group--batted" },
        { id: "plate", label: "Plate", className: "rs-group--plate" },
    ];

    const GROUP_TIPS = {
        identity: "Who's batting and where — order and handedness set platoon context for today's HR look.",
        matchup: "Starter matchup and HR environment — pitch-mix fit plus park, weather, wind, and pitcher leak combined.",
        power: "Season power output — homers, expected HR, luck, and near misses that signal HR upside.",
        contact: "Contact quality — how hard and true the hitter squares the ball; Boom% blends contact shape, pitch-mix fit vs today's starter, and HR Form%.",
        batted: "Batted-ball shape — launch angle, air rate, and pull profile tied to homer paths.",
        plate: "Overall plate profile — averages, whiff, and recent form that support or limit power.",
    };

    const EXPLORE_HITTER_LB_TIPS = {
        "#": "Rank on today's filtered HR ticket leaderboard.",
        Hitter: "Player name — click to open full profile with trends and HR environment breakdown.",
        Matchup: "Today's game pairing for this hitter.",
        "vs SP": "Opposing starting pitcher — split and risk columns score how leakable they are for this bat path.",
        ticketRank:
            "Composite HR ticket score on a 1–100 slate scale. 100 = best HR case on today's board; combines pitch-mix fit, form, pitcher split/risk, and park/weather.",
        splitPct:
            "Savant dinger-risk split for this hitter's handedness vs the starter. Higher % = pitcher is more vulnerable to this bat path; feeds ticket score.",
        riskPct:
            "Starting pitcher's overall dinger risk (Savant). Higher % = more HR-friendly arm; weighted into ticket score.",
        parkPct:
            "Handed park HR factor for this stadium today (Ballpark Pal + weather). Positive % = park boosts homers for this hitter's side.",
        mixPlus:
            "Pitch-mix fit — xwOBA vs starter's arsenal vs league average. Positive % = favorable matchup; largest single input to ticket score.",
        mixEdge:
            "Savant matchup edge — today's pitch-mix xwOBA vs season baseline, blended with career Statcast history vs this starter when available.",
        matchWhiffPct:
            "Savant swing & miss vs today's starter — whiff rate in career Statcast matchups with this pitcher. Lower = handles this arm better.",
        formPct:
            "HR form score (slate 0–100) — Due+, near-HR, last-7 HR rate vs season, pitch-mix fit vs today's starter, and contact shape. ↑↓← = HR trend (last 4 games vs prior 4).",
        barrelPct: "Season barrel rate — ideal EV/LA contact. Core power signal; high barrels mean more true HR upside.",
        airPct: "Fly ball + line drive share. More balls in the air = more chances to leave the yard.",
        nearHr: "Near misses — balls that almost cleared the fence; hints at latent HR luck turning.",
        avgEV: "Average exit velocity. Harder contact carries farther and raises HR probability on contact.",
    };

    const K_STUFF_WEIGHTS = {
        whiffPct: 38,
        kPct: 38,
        edgePct: 24,
    };

    const K_HAND_WEIGHTS = {
        whiffPct: 50,
        kPct: 50,
    };

    const K_SCORE_TIPS = {
        Overall:
            "K stuff — slate-relative score from Whiff%, K%, and Edge%. Higher % = more swing-and-miss and strikeout skill vs today's starters.",
        LHB: "K stuff vs left-handed hitters (Whiff% + K% on Savant hand splits).",
        RHB: "K stuff vs right-handed hitters (Whiff% + K% on Savant hand splits).",
        Matchup: "Opposing lineup's average hitter K% — higher = lineup strikes out more often (easier K matchup).",
        Pick: "K pick score — 70% pitcher K stuff + 30% opposing lineup K susceptibility. Higher = stronger lean for strikeout props.",
        ExpK: "Expected strikeouts — projected IP × effective K/9, adjusted for opposing lineup K% and pitcher K stuff.",
        CeilingK: "Ceiling K — realistic max if pitch count runs deep and recent form plays up.",
        Line: "Nearest half-K prop line with Over (O) or Under (U) lean from expected K.",
    };

    const EXPLORE_PITCHER_LB_TIPS = {
        Pitcher: "Starting pitcher — click for full HR vulnerability profile, splits, arsenal, and recent starts.",
        kPick:
            "K pick score (1–100 slate scale). Combines Whiff%, K%, Edge% vs today's SPs plus how often the opposing lineup strikes out.",
        Game: "Today's matchup for this arm.",
        risk: "Overall dinger risk % (Savant-weighted). Only SPs at ≥50% appear here. Click column to sort.",
        barrelPct: "Season barrel% allowed — ideal EV/LA contact surrendered. Top HR predictor for targeting.",
        hardHitPct: "Hard-hit% allowed at 95+ mph — balls driven with homer carry off this arm.",
        hr9: "Homers allowed per nine innings — direct HR rate this season.",
        lhb: "Dinger risk vs left-handed batters — pair with LHB targets on the hitter board.",
        rhb: "Dinger risk vs right-handed batters — pair with RHB targets on the hitter board.",
    };

    const PITCHER_OVERVIEW_KEYS = ["barrelPct", "hardHitPct", "hr9", "hrFbPct"];

    const COLS = [
        { key: "order", label: "#", group: "identity", fmt: (r) => r.order ?? "—", tip: "Batting order spot in today's lineup." },
        { key: "name", label: "Hitter", group: "identity", fmt: (r) => r.name, text: true, tip: "Player name and defensive position." },
        { key: "hand", label: "B", group: "identity", fmt: (r) => r.hand || "—", text: true, tip: "Batting hand — L (left), R (right), or S (switch)." },
        {
            key: "ticketScore",
            label: "Score",
            group: "matchup",
            ticket: true,
            fmt: (r) => fmtTicketBadgeForRow(r),
            tip: "HR ticket score (1–100 slate scale). Combines mix fit, pitcher leak, HR environment, form, and power contact.",
        },
        { key: "mixPlus", label: "Mix%", group: "matchup", stat: "mixPlus", fmt: (r) => fmtFormPct(hitterStats(r).mixPlus), tip: "Pitch-mix fit — weighted xwOBA vs this starter's pitch usage compared to league average on those pitches. Positive % = favorable matchup; heaviest input to HR ticket score." },
        { key: "mixEdge", label: "Edge%", group: "matchup", stat: "mixEdge", fmt: (r) => fmtFormPct(hitterStats(r).mixEdge), tip: "Savant matchup edge — blends today's pitch-mix xwOBA vs your season baseline with career Statcast history vs this starter. Positive % = favorable personal edge. History weights up as pitch sample grows." },
        { key: "matchWhiffPct", label: "SwM%", group: "matchup", stat: "matchWhiffPct", fmt: (r) => fmtPct(hitterStats(r).matchWhiffPct ?? hitterStats(r).bvpKPct), tip: "Savant swing & miss vs today's starter — whiff rate in career Statcast matchups with this pitcher. Lower % = better contact history vs this arm." },
        { key: "hrEnv", label: "HR env", group: "matchup", hrProp: true, fmt: (r) => fmtHrPropPct(r), tip: "HR environment — park, weather, wind, dimensions, and pitcher vulnerability combined. Positive = better homer conditions today; separate from ticket score but same slate context." },
        { key: "hr", label: "HR", group: "power", stat: "hr", fmt: (r) => fmtNum(hitterStats(r).hr), tip: "Home runs — balls hit over the fence. Core measure of raw power." },
        { key: "expectedHr", label: "xHR", group: "power", stat: "expectedHr", fmt: (r) => fmtXhr(hitterStats(r).expectedHr), tip: "Expected homers from contact quality — how many HRs Savant thinks this swing profile deserves (rounded)." },
        { key: "hrLuckDiff", label: "Due+", group: "power", stat: "hrLuckDiff", fmt: (r) => fmtLuck(hitterStats(r).hrLuckDiff), tip: "Homers owed (xHR minus actual HR). +1 or higher means the hitter is due for a jack." },
        { key: "nearHr", label: "Near HR", group: "power", stat: "nearHr", fmt: (r) => fmtNearHr(r), tip: "Near misses — balls that almost left the yard." },
        { key: "avg", label: "AVG", group: "plate", stat: "avg", fmt: (r) => fmtRate(hitterStats(r).avg), tip: "Batting average — hits divided by at-bats. Overall hitting for average." },
        { key: "iso", label: "ISO", group: "plate", stat: "iso", fmt: (r) => fmtRate(hitterStats(r).iso), tip: "Isolated power — slugging minus average. Extra-base hit power per at-bat." },
        { key: "slg", label: "SLG", group: "plate", stat: "slg", fmt: (r) => fmtRate(hitterStats(r).slg), tip: "Slugging percentage — total bases per at-bat. Measures overall power production." },
        { key: "xwoba", label: "xwOBA", group: "plate", stat: "xwoba", fmt: (r) => fmtRate(hitterStats(r).xwoba), tip: "Expected weighted on-base average — overall offensive value from contact quality, independent of luck." },
        { key: "barrelPct", label: "Barrel%", group: "plate", stat: "barrelPct", fmt: (r) => fmtPct(hitterStats(r).barrelPct), tip: "Barrel rate — batted balls with ideal launch angle and exit velocity to produce homers and extra-base hits." },
        { key: "hardHitPct", label: "Hard Hit%", group: "plate", stat: "hardHitPct", fmt: (r) => fmtPct(hitterStats(r).hardHitPct), tip: "Hard hit rate — share of batted balls at 95+ mph. Measures how often a hitter squares the ball up." },
        { key: "avgEV", label: "EV", group: "plate", stat: "avgEV", fmt: (r) => fmtEv(hitterStats(r).avgEV), tip: "Average exit velocity — how hard the ball is hit on average. Higher EV usually means more power potential." },
        { key: "solidContactPct", label: "Solid%", group: "batted", stat: "solidContactPct", fmt: (r) => fmtPct(hitterStats(r).solidContactPct), tip: "Solid contact rate — share of batted balls classified as solid contact (good EV/LA combo, below barrel threshold)." },
        { key: "blastPct", label: "Blast%", group: "batted", stat: "blastPct", fmt: (r) => fmtPct(hitterStats(r).blastPct), tip: "Blast rate — share of contact that is both squared up and on a fast swing. Elite bat-speed contact quality." },
        { key: "fbPct", label: "FB%", group: "plate", stat: "fbPct", fmt: (r) => fmtPct(hitterStats(r).fbPct), tip: "Fly ball rate — share of batted balls in the air. Fly-ball hitters tend to have more home run upside." },
        { key: "airPct", label: "Air%", group: "batted", stat: "airPct", fmt: (r) => fmtPct(hitterStats(r).airPct), tip: "Air rate (FB% + LD%) — share of batted balls in the air. Higher often means more HR upside." },
        { key: "hrFbPct", label: "HR/FB%", group: "plate", stat: "hrFbPct", fmt: (r) => fmtPct(hitterStats(r).hrFbPct), tip: "Home runs per fly ball — how often fly balls leave the yard. Power efficiency on balls in the air." },
        { key: "hrFormPct", label: "HR Form%", group: "plate", stat: "hrFormPct", fmt: (r) => fmtHrFormWithTrend(hitterStats(r).hrFormPct, formTrendForRow(r)), tip: "HR form — slate-relative score from Due+ (xHR luck), near-HR/mostly-gone, last-7 HR rate vs season, pitch-mix fit vs today's starter, and contact shape (air/pull). Higher = better HR momentum today. Arrow tracks HR in last 4 games vs prior 4." },
        { key: "boomPct", label: "Boom%", group: "contact", stat: "boomPct", fmt: (r) => fmtBoomWithTrend(hitterStats(r).boomPct, boomTrendForRow(r)), tip: "Boom% — slate-relative HR power score from contact quality (Barrel%, Blast%, Hard Hit%, Air%, FB%, Solid%), pitch-mix fit vs today's starter, and HR Form%. Higher = more homer upside today. Arrow tracks recent ISO + HR power vs prior 4 games." },
        { key: "whiffPct", label: "Whiff%", group: "plate", stat: "whiffPct", fmt: (r) => fmtPct(hitterStats(r).whiffPct), tip: "Whiff rate — swings and misses as a share of swings. Lower is better for contact hitters." },
        { key: "kPct", label: "K%", group: "plate", stat: "kPct", fmt: (r) => fmtPct(hitterStats(r).kPct), tip: "Strikeout rate — strikeouts as a share of plate appearances. Lower is better for contact." },
        { key: "gbPct", label: "GB%", group: "batted", stat: "gbPct", fmt: (r) => fmtPct(hitterStats(r).gbPct), tip: "Ground ball rate — share of batted balls on the ground. Lower rates often correlate with more power and fly balls." },
        { key: "ldPct", label: "LD%", group: "batted", stat: "ldPct", fmt: (r) => fmtPct(hitterStats(r).ldPct), tip: "Line drive rate — share of batted balls hit on a line. A sign of solid, hard contact." },
        { key: "pullPct", label: "Pull%", group: "batted", stat: "pullPct", fmt: (r) => fmtPct(hitterStats(r).pullPct), tip: "Pull rate — share of batted balls hit to the pull side. Higher pull rates often mean more power, especially for same-side matchups." },
        { key: "launchAngle", label: "LA", group: "batted", stat: "launchAngle", fmt: (r) => fmtAngle(hitterStats(r).launchAngle), tip: "Average launch angle — typical vertical angle of batted balls. Higher LA often means more fly balls and HR upside." },
        { key: "sweetSpotPct", label: "Sweet%", group: "batted", stat: "sweetSpotPct", fmt: (r) => fmtPct(hitterStats(r).sweetSpotPct), tip: "Sweet spot rate — share of batted balls with launch angle 8–32°. Optimal range for power and hard contact." },
        { key: "bipPct", label: "BIP%", group: "batted", stat: "bipPct", fmt: (r) => fmtPct(hitterStats(r).bipPct), tip: "Balls in play rate — batted balls as a share of plate appearances. Higher BIP% means more contact opportunities." },
        { key: "batSpeed", label: "BatSpd", group: "batted", stat: "batSpeed", fmt: (r) => fmtEv(hitterStats(r).batSpeed), tip: "Bat speed — average competitive swing speed (mph) measured at the sweet spot. Higher bat speed means more power potential." },
        { key: "swingStrength", label: "SqUp%", group: "batted", stat: "swingStrength", fmt: (r) => fmtPct(hitterStats(r).swingStrength), tip: "Swing strength (squared-up rate) — share of contact where exit velocity matched bat speed potential. Measures quality of contact transfer." },
    ];

    let slate = null;
    let savantLookup = null;
    let pitchMixCache = null;
    let parkFactorsLookup = null;
    let parkFactorsLookupDate = null;
    let stadiumCoords = null;
    let pitcherHandLookup = null;
    let hrTicketCache = new Map();
    let hrTicketScale = { min: null, max: null, ready: false };
    let activeGameIdx = 0;
    let activeSide = "away";
    let sortKey = "ticketScore";
    let sortDir = -1;
    let sortUserOverride = false;
    let tableViewMode = loadTableViewMode();
    let exploreSortKey = "ticketRank";
    let pitcherLbSortKey = "risk";
    let pitcherLbSortDir = -1;

    const IDENTITY_COL_KEYS = new Set(["order", "name", "hand"]);
    const COLUMN_ORDER_STORAGE_KEY = "research-hitter-column-order";

    function loadTableViewMode() {
        try {
            const v = localStorage.getItem(TABLE_VIEW_STORAGE_KEY);
            if (v === "essential") return "essential";
            return "full";
        } catch {
            return "full";
        }
    }

    const COL_SHORT_LABELS = {
        ticketScore: "Scr",
        mixPlus: "Mix",
        mixEdge: "Edge",
        matchWhiffPct: "SwM",
        hrEnv: "Env",
        expectedHr: "xHR",
        hrLuckDiff: "Due+",
        nearHr: "Near",
        hardHitPct: "Hard",
        solidContactPct: "Solid",
        blastPct: "Blast",
        hrFormPct: "Form",
        boomPct: "Boom",
        swingStrength: "SqUp",
        sweetSpotPct: "Sweet",
        launchAngle: "LA",
        batSpeed: "Bat",
        hrFbPct: "HR/FB",
    };

    function colDisplayLabel(col) {
        if (!col) return "";
        if (tableViewMode === "essential") return col.label;
        return COL_SHORT_LABELS[col.key] || col.label;
    }

    function saveTableViewMode(mode) {
        try {
            localStorage.setItem(TABLE_VIEW_STORAGE_KEY, mode);
        } catch (e) {}
    }

    function setTableViewMode(mode) {
        tableViewMode = mode === "full" ? "full" : "essential";
        saveTableViewMode(tableViewMode);
        if (els.tableViewEssential) els.tableViewEssential.classList.toggle("is-active", tableViewMode === "essential");
        if (els.tableViewFull) els.tableViewFull.classList.toggle("is-active", tableViewMode === "full");
        if (els.tableWrap) {
            els.tableWrap.classList.toggle("rs-table-wrap--essential", tableViewMode === "essential");
            els.tableWrap.classList.toggle("rs-table-wrap--full", tableViewMode === "full");
        }
        if (els.colReorderBtn) els.colReorderBtn.hidden = tableViewMode !== "full";
        if (tableViewMode === "essential" && columnReorderMode) setColumnReorderMode(false);
        renderTable();
        renderMobileCards();
        syncMobileSortSelect();
    }

    let columnReorderMode = false;
    let columnOrderKeys = loadColumnOrderKeys();
    let colDragKey = null;

    function loadColumnOrderKeys() {
        try {
            const raw = localStorage.getItem(COLUMN_ORDER_STORAGE_KEY);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed)) return null;
            const valid = new Set(COLS.map((c) => c.key));
            const keys = parsed
                .map((k) => (k === "recentForm" ? "hrFormPct" : k))
                .filter((k) => valid.has(k) && !IDENTITY_COL_KEYS.has(k));
            const deduped = [...new Set(keys)];
            return deduped.length ? deduped : null;
        } catch {
            return null;
        }
    }

    function saveColumnOrderKeys(keys) {
        localStorage.setItem(COLUMN_ORDER_STORAGE_KEY, JSON.stringify(keys));
    }

    function defaultReorderableKeys() {
        return COLS.filter((c) => !IDENTITY_COL_KEYS.has(c.key)).map((c) => c.key);
    }

    /** Saved order merged with any new columns (e.g. hrFormPct) so drag-drop always has valid indices. */
    function mergedReorderableColumnKeys() {
        const base = defaultReorderableKeys();
        const saved = columnOrderKeys;
        if (!saved?.length) return base;
        const keys = [];
        for (const k of saved) {
            if (base.includes(k) && !keys.includes(k)) keys.push(k);
        }
        for (const k of base) {
            if (!keys.includes(k)) keys.push(k);
        }
        return keys;
    }

    function reorderableColumnKeys() {
        return mergedReorderableColumnKeys();
    }

    function moveColumnKey(dragKey, targetKey) {
        if (IDENTITY_COL_KEYS.has(dragKey) || IDENTITY_COL_KEYS.has(targetKey)) return;
        const keys = mergedReorderableColumnKeys().slice();
        const from = keys.indexOf(dragKey);
        const to = keys.indexOf(targetKey);
        if (from < 0 || to < 0 || from === to) return;
        keys.splice(from, 1);
        keys.splice(to, 0, dragKey);
        columnOrderKeys = keys;
        saveColumnOrderKeys(keys);
    }

    function resetColumnOrder() {
        columnOrderKeys = null;
        localStorage.removeItem(COLUMN_ORDER_STORAGE_KEY);
    }

    function setColumnReorderMode(on) {
        columnReorderMode = Boolean(on);
        if (els.colReorderBtn) {
            els.colReorderBtn.textContent = columnReorderMode ? "Done" : "Sort columns";
            els.colReorderBtn.classList.toggle("is-on", columnReorderMode);
            els.colReorderBtn.setAttribute("aria-pressed", columnReorderMode ? "true" : "false");
        }
        if (els.colResetBtn) els.colResetBtn.hidden = !columnReorderMode;
        if (els.colReorderHint) els.colReorderHint.hidden = !columnReorderMode;
        if (els.tableWrap) els.tableWrap.classList.toggle("rs-table-wrap--reorder", columnReorderMode);
        renderTable();
    }

    function visibleCols() {
        const byKey = Object.fromEntries(COLS.map((c) => [c.key, c]));
        if (tableViewMode === "essential") {
            return ESSENTIAL_COL_KEYS.map((k) => byKey[k]).filter(Boolean);
        }
        const ordered = mergedReorderableColumnKeys()
            .map((k) => byKey[k])
            .filter(Boolean);
        return [...COLS.filter((c) => IDENTITY_COL_KEYS.has(c.key)), ...ordered];
    }

    const els = {
        status: document.getElementById("rsStatus"),
        games: document.getElementById("rsGames"),
        matchupTitle: document.getElementById("rsMatchupTitle"),
        matchupSp: document.getElementById("rsMatchupSp"),
        tableHead: document.getElementById("rsTableHead"),
        tableBody: document.getElementById("rsTableBody"),
        dateInput: document.getElementById("rsDate"),
        refreshBtn: document.getElementById("rsRefresh"),
        lastUpdated: document.getElementById("rsLastUpdated"),
        sideAway: document.getElementById("rsSideAway"),
        sideHome: document.getElementById("rsSideHome"),
        sourceBadge: document.getElementById("rsSourceBadge"),
        backLink: document.getElementById("rsBackLink"),
        themeToggle: document.getElementById("rsThemeToggle"),
        mobileSort: document.getElementById("rsMobileSort"),
        mobileSortDir: document.getElementById("rsMobileSortDir"),
        cardList: document.getElementById("rsCardList"),
        weatherPanel: document.getElementById("rsWeatherPanel"),
        weatherGrid: document.getElementById("rsWeatherGrid"),
        weatherMeta: document.getElementById("rsWeatherMeta"),
        windField: document.getElementById("rsWindField"),
        parkOutline: document.getElementById("rsParkOutline"),
        windArrow: document.getElementById("rsWindArrow"),
        windInfo: document.getElementById("rsWindInfo"),
        pitcherPanel: document.getElementById("rsPitcherPanel"),
        pitcherLead: document.getElementById("rsPitcherLead"),
        pitcherCards: document.getElementById("rsPitcherCards"),
        playerSearch: document.getElementById("rsPlayerSearch"),
        searchResults: document.getElementById("rsSearchResults"),
        exploreMeta: document.getElementById("rsExploreMeta"),
        exploreHand: document.getElementById("rsExploreHand"),
        exploreMinScore: document.getElementById("rsExploreMinScore"),
        exploreMinPark: document.getElementById("rsExploreMinPark"),
        exploreSort: document.getElementById("rsExploreSort"),
        exploreReset: document.getElementById("rsExploreReset"),
        exploreLede: document.getElementById("rsExploreLede"),
        hrLeaderboard: document.getElementById("rsHrLeaderboard"),
        hrLeaderboardBody: document.getElementById("rsHrLeaderboardBody"),
        pitcherLeaderboardBody: document.getElementById("rsPitcherLeaderboardBody"),
        pitcherLeaderboard: document.getElementById("rsPitcherLeaderboard"),
        playerProfile: document.getElementById("rsPlayerProfile"),
        profileName: document.getElementById("rsProfileName"),
        profileSub: document.getElementById("rsProfileSub"),
        profilePhoto: document.getElementById("rsProfilePhoto"),
        profileGame: document.getElementById("rsProfileGame"),
        profileHero: document.getElementById("rsProfileHero"),
        profileTrends: document.getElementById("rsProfileTrends"),
        profileGrid: document.getElementById("rsProfileGrid"),
        profileClose: document.getElementById("rsProfileClose"),
        profileJump: document.getElementById("rsProfileJump"),
        profileTracker: document.getElementById("rsProfileTracker"),
        profileSavant: document.getElementById("rsProfileSavant"),
        colReorderBtn: document.getElementById("rsColReorderBtn"),
        colResetBtn: document.getElementById("rsColResetBtn"),
        colReorderHint: document.getElementById("rsColReorderHint"),
        tableWrap: document.querySelector(".rs-table-wrap"),
        matchupSummary: document.getElementById("rsMatchupSummary"),
        tableViewEssential: document.getElementById("rsTableViewEssential"),
        tableViewFull: document.getElementById("rsTableViewFull"),
        header: document.querySelector(".rs-header"),
        exploreLbCards: document.getElementById("rsExploreLbCards"),
    };

    let profileEntry = null;
    let profilePitcherEntry = null;
    let profileTrendsGen = 0;
    let pitcherTrendsGen = 0;
    let profileToastTimer = null;
    const trendsCache = new Map();
    const pitcherTrendsCache = new Map();
    const formTrendCache = new Map();
    const boomTrendCache = new Map();
    const hrFormRollingCache = new Map();

    const HR_FORM_WEIGHTS = {
        hrLuckDiff: 30,
        hrProximity: 25,
        rollingHrBoost: 15,
        mixPlus: 20,
        hrContactShape: 10,
    };

    const BOOM_CONTACT_WEIGHTS = {
        barrelPct: 26,
        blastPct: 20,
        hardHitPct: 18,
        airPct: 16,
        fbPct: 14,
        solidContactPct: 6,
    };

    const BOOM_WEIGHTS = {
        boomContact: 55,
        mixPlus: 25,
        hrFormPct: 20,
    };
    const BET_TRACKER_LS = "worstpickz-bet-tracker-v1";
    let searchBlurTimer = null;

    function isMobileView() {
        return window.matchMedia("(max-width: 768px)").matches;
    }

    const MOBILE_CARD_OPEN_GROUPS = new Set(["matchup", "power"]);
    const MOBILE_HIGHLIGHT_KEYS = [
        "ticketScore",
        "hrEnv",
        "mixPlus",
        "hrFormPct",
        "boomPct",
        "barrelPct",
        "hardHitPct",
        "blastPct",
        "hrFbPct",
        "fbPct",
        "pullPct",
        "airPct",
        "avgEV",
        "gbPct",
        "whiffPct",
        "sweetSpotPct",
    ];

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

    function todayLocalIso() {
        const d = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        return `${y}-${m}-${day}`;
    }

    const RESEARCH_KEEP_DATE_KEY = "research-keep-date";
    const SORT_PREF_KEY = "research-hitter-sort";

    function defaultResearchDate() {
        return todayLocalIso();
    }

    function sheetDateFromQuery() {
        const d = qs("date");
        if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) return d;
        return defaultResearchDate();
    }

    function initResearchDate() {
        const today = todayLocalIso();
        const fromQuery = qs("date");
        let date =
            fromQuery && /^\d{4}-\d{2}-\d{2}$/.test(fromQuery) ? fromQuery : today;
        const keepDate = sessionStorage.getItem(RESEARCH_KEEP_DATE_KEY);
        if (date < today && date !== keepDate) {
            date = today;
        }
        const url = new URL(window.location.href);
        if (url.searchParams.get("date") !== date) {
            url.searchParams.set("date", date);
            window.history.replaceState({}, "", url);
        }
        return date;
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

    function fmtXhr(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        return String(Math.round(Number(v)));
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

    function formTrendForRow(row) {
        const id = row?.id;
        if (!id) return null;
        return formTrendCache.get(id) ?? formTrendCache.get(String(id)) ?? null;
    }

    function boomTrendForRow(row) {
        const id = row?.id;
        if (!id) return null;
        return boomTrendCache.get(id) ?? boomTrendCache.get(String(id)) ?? null;
    }

    function hrProximitySignal(stats) {
        const near = stats?.nearHr;
        const mostly = stats?.mostlyGone;
        if (near == null && mostly == null) return null;
        return (Number(near) || 0) + (Number(mostly) || 0) * 0.75;
    }

    function hrContactShapeSignal(stats) {
        const air = stats?.airPct ?? (stats?.fbPct != null && stats?.ldPct != null ? stats.fbPct + stats.ldPct : null);
        const pull = stats?.pullPct;
        if (air == null && pull == null) return null;
        const airPart = air != null ? Math.max(Number(air) - 38, 0) : 0;
        const pullPart = pull != null ? Math.max(Number(pull) - 38, 0) : 0;
        if (air == null) return pullPart;
        if (pull == null) return airPart;
        return airPart * 0.6 + pullPart * 0.4;
    }

    function rollingHrBoostFromGames(games, stats) {
        // 14-game window — a single quiet week is normal for a power hitter,
        // so a 7-game window was mostly noise.
        const slice = (games || []).slice(-14);
        let hr = 0;
        let pa = 0;
        for (const g of slice) {
            hr += Number(g.hr) || 0;
            pa += Number(g.pa) || 0;
        }
        if (pa < 8) return null;
        const recentRate = hr / pa;
        const seasonPa = stats?.pa;
        const seasonHr = stats?.hr;
        if (!seasonPa || seasonPa < 20 || seasonHr == null) return Math.round(recentRate * 1000) / 10;
        const seasonRate = seasonHr / seasonPa;
        const trust = Math.min(pa / 40, 1);
        const blended = trust * recentRate + (1 - trust) * seasonRate;
        return Math.round((blended - seasonRate) * 1000) / 10;
    }

    function computeHrFormTrendFromGames(games) {
        const hrs = (games || []).map((g) => Number(g.hr) || 0);
        if (hrs.length < 8) return "flat";
        const recent = hrs.slice(-4).reduce((a, b) => a + b, 0);
        const prior = hrs.slice(-8, -4).reduce((a, b) => a + b, 0);
        if (recent > prior) return "up";
        if (recent < prior) return "down";
        return "flat";
    }

    function scoreHrForm(stats, pools, rollingBoost, mixPlus) {
        let weighted = 0;
        let totalWeight = 0;
        const parts = [
            ["hrLuckDiff", stats.hrLuckDiff, HR_FORM_WEIGHTS.hrLuckDiff],
            ["hrProximity", hrProximitySignal(stats), HR_FORM_WEIGHTS.hrProximity],
            ["rollingHrBoost", rollingBoost, HR_FORM_WEIGHTS.rollingHrBoost],
            ["mixPlus", mixPlus, HR_FORM_WEIGHTS.mixPlus],
            ["hrContactShape", hrContactShapeSignal(stats), HR_FORM_WEIGHTS.hrContactShape],
        ];
        for (const [key, val, weight] of parts) {
            if (val == null || Number.isNaN(Number(val)) || !weight) continue;
            const pool = pools[key];
            if (!pool?.length) continue;
            const pct = percentileRank(pool, Number(val), true);
            weighted += pct * weight;
            totalWeight += weight;
        }
        if (totalWeight <= 0) return null;
        return Math.round((weighted / totalWeight) * 10) / 10;
    }

    function buildHrFormPools(entries) {
        const pools = {
            hrLuckDiff: [],
            hrProximity: [],
            rollingHrBoost: [],
            mixPlus: [],
            hrContactShape: [],
        };
        for (const entry of entries) {
            const stats = hitterStats(entry.row);
            if (stats.hrLuckDiff != null && !Number.isNaN(Number(stats.hrLuckDiff))) {
                pools.hrLuckDiff.push(Number(stats.hrLuckDiff));
            }
            const prox = hrProximitySignal(stats);
            if (prox != null) pools.hrProximity.push(prox);
            const shape = hrContactShapeSignal(stats);
            if (shape != null) pools.hrContactShape.push(shape);
            const mix = resolveMixPlusForEntry(entry, stats);
            if (mix != null && !Number.isNaN(Number(mix))) pools.mixPlus.push(Number(mix));
            const id = entry.row?.id;
            const rolling =
                hrFormRollingCache.get(id) ?? hrFormRollingCache.get(String(id)) ?? null;
            if (rolling != null && !Number.isNaN(Number(rolling))) {
                pools.rollingHrBoost.push(Number(rolling));
            }
        }
        return pools;
    }

    function resolveMixPlusForEntry(entry, stats) {
        if (stats?.mixPlus != null && !Number.isNaN(Number(stats.mixPlus))) return Number(stats.mixPlus);
        const row = entry?.row;
        const pitcher = entry?.pitcher;
        if (!row?.id || !pitcher?.arsenal) return null;
        const batterPitch = pitchMixCache?.batterPitch || slate?.batter_pitch_lookup || {};
        const leagueAvgs = pitchMixCache?.leagueAvgs || slate?.league_pitch_avgs || {};
        const mix = scoreBatterVsArsenal(
            row.id,
            pitcher.arsenal,
            batterPitch[row.id] || batterPitch[String(row.id)],
            stats?.xwoba,
            leagueAvgs
        );
        return mix?.mixPlus ?? null;
    }

    function computeHrFormForSlate() {
        const entries = collectSlateHitters();
        if (!entries.length) return;
        const pools = buildHrFormPools(entries);
        for (const entry of entries) {
            const row = entry.row;
            if (!row) continue;
            const stats = hitterStats(row);
            const id = row.id;
            const rolling =
                hrFormRollingCache.get(id) ?? hrFormRollingCache.get(String(id)) ?? null;
            const mixPlus = resolveMixPlusForEntry(entry, stats);
            const score = scoreHrForm(stats, pools, rolling, mixPlus);
            if (score == null) continue;
            row.stats = { ...stats, hrFormPct: Math.round(score), hrForm: score };
        }
        clearHrTicketCache();
    }

    function boomComponentValue(stats, key) {
        if (key === "airPct") {
            return stats?.airPct ?? (stats?.fbPct != null && stats?.ldPct != null ? Number(stats.fbPct) + Number(stats.ldPct) : null);
        }
        return stats?.[key] ?? null;
    }

    function boomContactSignal(stats) {
        let weighted = 0;
        let totalW = 0;
        for (const [key, weight] of Object.entries(BOOM_CONTACT_WEIGHTS)) {
            const val = boomComponentValue(stats, key);
            if (val == null || Number.isNaN(Number(val))) continue;
            weighted += Number(val) * weight;
            totalW += weight;
        }
        return totalW > 0 ? weighted / totalW : null;
    }

    function buildBoomPools(entries) {
        const pools = {
            boomContact: [],
            mixPlus: [],
            hrFormPct: [],
        };
        for (const entry of entries) {
            const stats = hitterStats(entry.row);
            const contact = boomContactSignal(stats);
            if (contact != null && !Number.isNaN(Number(contact))) pools.boomContact.push(Number(contact));
            const mix = resolveMixPlusForEntry(entry, stats);
            if (mix != null && !Number.isNaN(Number(mix))) pools.mixPlus.push(Number(mix));
            const form = stats.hrFormPct ?? stats.hrForm;
            if (form != null && !Number.isNaN(Number(form))) pools.hrFormPct.push(Number(form));
        }
        return pools;
    }

    function scoreBoom(stats, pools, entry) {
        let weighted = 0;
        let totalWeight = 0;
        const mixPlus = resolveMixPlusForEntry(entry, stats);
        const hrForm = stats.hrFormPct ?? stats.hrForm;
        const parts = [
            ["boomContact", boomContactSignal(stats), BOOM_WEIGHTS.boomContact],
            ["mixPlus", mixPlus, BOOM_WEIGHTS.mixPlus],
            ["hrFormPct", hrForm, BOOM_WEIGHTS.hrFormPct],
        ];
        for (const [key, val, weight] of parts) {
            if (val == null || Number.isNaN(Number(val)) || !weight) continue;
            const pool = pools[key];
            if (!pool?.length) continue;
            const pct = percentileRank(pool, Number(val), true);
            weighted += pct * weight;
            totalWeight += weight;
        }
        if (totalWeight <= 0) return null;
        return Math.round((weighted / totalWeight) * 10) / 10;
    }

    function computeBoomForSlate() {
        const entries = collectSlateHitters();
        if (!entries.length) return;
        const pools = buildBoomPools(entries);
        for (const entry of entries) {
            const row = entry.row;
            if (!row) continue;
            const stats = hitterStats(row);
            const score = scoreBoom(stats, pools, entry);
            if (score == null) continue;
            row.stats = { ...stats, boomPct: Math.round(score), boom: score };
        }
    }

    function gamePowerProxy(g) {
        const pa = Number(g.pa) || 0;
        if (pa <= 0) return null;
        const hrRate = (Number(g.hr) || 0) / pa;
        const iso = g.iso != null ? Number(g.iso) : null;
        if (iso != null) return iso * 0.65 + hrRate * 0.35;
        if (g.slg != null) {
            const estIso = Math.max(Number(g.slg) - 0.22, 0);
            return estIso * 0.65 + hrRate * 0.35;
        }
        return hrRate;
    }

    function computeBoomTrendFromGames(games) {
        const proxies = (games || []).map(gamePowerProxy).filter((v) => v != null && !Number.isNaN(Number(v)));
        if (proxies.length < 8) return "flat";
        const recent = proxies.slice(-4);
        const prior = proxies.slice(-8, -4);
        const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
        const priorAvg = prior.reduce((a, b) => a + b, 0) / prior.length;
        const thresh = 0.008;
        if (recentAvg > priorAvg + thresh) return "up";
        if (recentAvg < priorAvg - thresh) return "down";
        return "flat";
    }

    function formTrendArrow(trend) {
        if (trend === "up") return "↑";
        if (trend === "down") return "↓";
        if (trend === "flat") return "←";
        return "";
    }

    function formTrendLabel(trend) {
        if (trend === "up") return "HR form trending up";
        if (trend === "down") return "HR form trending down";
        if (trend === "flat") return "HR form flat";
        return "";
    }

    function boomTrendLabel(trend) {
        if (trend === "up") return "Boom% trending up";
        if (trend === "down") return "Boom% trending down";
        if (trend === "flat") return "Boom% flat";
        return "";
    }

    function fmtMetricWithTrend(val, trend, labelFn) {
        const pct = fmtSavantPct(val);
        if (pct === "—" || !trend) return pct;
        const arrow = formTrendArrow(trend);
        const label = labelFn(trend);
        return `${pct}<span class="rs-form-trend rs-form-trend--${trend}" title="${label}" aria-label="${label}">${arrow}</span>`;
    }

    function fmtHrFormWithTrend(val, trend) {
        return fmtMetricWithTrend(val, trend, formTrendLabel);
    }

    function fmtBoomWithTrend(val, trend) {
        return fmtMetricWithTrend(val, trend, boomTrendLabel);
    }

    let formTrendHydrateGen = 0;

    function scheduleHrFormHydrate(playerIds) {
        const season = seasonFromDate(slate?.sheet_date || els.dateInput?.value || sheetDateFromQuery());
        const todo = [...new Set((playerIds || []).filter((id) => id && (!formTrendCache.has(id) || !boomTrendCache.has(id))))];
        if (!todo.length) return;
        const gen = ++formTrendHydrateGen;
        (async () => {
            for (let i = 0; i < todo.length; i += 8) {
                if (gen !== formTrendHydrateGen) return;
                const batch = todo.slice(i, i + 8);
                await Promise.all(
                    batch.map(async (id) => {
                        try {
                            const games = await fetchPlayerTrends(id, season);
                            formTrendCache.set(id, computeHrFormTrendFromGames(games));
                            boomTrendCache.set(id, computeBoomTrendFromGames(games));
                            const entry = collectSlateHitters().find((e) => e.row?.id === id);
                            const stats = entry ? hitterStats(entry.row) : {};
                            const boost = rollingHrBoostFromGames(games, stats);
                            if (boost != null) hrFormRollingCache.set(id, boost);
                        } catch {
                            formTrendCache.set(id, "flat");
                            boomTrendCache.set(id, "flat");
                        }
                    })
                );
            }
            if (gen !== formTrendHydrateGen) return;
            computeHrFormForSlate();
            computeBoomForSlate();
            clearSlatePresetCache();
            renderGoblinsPanel();
            if (columnReorderMode) return;
            renderTable();
            renderMobileCards();
            renderExplorePanel();
        })();
    }

    function fmtPitchCode(code) {
        if (!code) return "—";
        return String(code);
    }

    function mixTipForRow(row) {
        const game = activeGame();
        const pitcher = activeSide === "away" ? game?.homePitcher : game?.awayPitcher;
        const s = hitterStats(row);
        if (s.mixPlus == null && s.mixEdge == null) return null;
        const lines = [];
        if (pitcher?.arsenal && s.mixPlus != null) {
            lines.push(`vs ${pitcher.name || "SP"}: ${pitcher.arsenalLabel || formatArsenal(pitcher.arsenal)}`);
            lines.push(
                `Mix% ${fmtFormPct(s.mixPlus)} · mix xwOBA ${s.mixXwoba != null ? Number(s.mixXwoba).toFixed(3) : "—"}`
            );
        }
        if (s.mixEdge != null) {
            const bits = [`Edge% ${fmtFormPct(s.mixEdge)}`];
            if (s.matchupEdge != null) bits.push(`mix ${fmtFormPct(s.matchupEdge)}`);
            if (s.historyEdge != null) bits.push(`history ${fmtFormPct(s.historyEdge)}`);
            if (s.matchPitches != null) bits.push(`${s.matchPitches} career pitches vs ${pitcher?.name || "SP"}`);
            lines.push(bits.join(" · "));
        }
        const swm = s.matchWhiffPct ?? s.bvpKPct;
        if (swm != null) {
            lines.push(`SwM% ${fmtPct(swm)} vs ${pitcher?.name || "SP"} (Savant history)`);
        }
        return lines.length ? lines.join("\n") : null;
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

    function fmtAngle(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        return `${Number(v).toFixed(1)}°`;
    }

    function fmtLuck(v) {
        if (v == null || Number.isNaN(Number(v))) return "—";
        const n = Number(v);
        return `${n > 0 ? "+" : ""}${n.toFixed(1)}`;
    }

    function fmtNearHr(row) {
        const stats = hitterStats(row);
        const val = stats.nearHr;
        if (val == null || Number.isNaN(Number(val))) return "—";
        const src = stats.nearHrSource === "propfinder" ? "*" : "";
        return `${fmtNum(val)}${src}`;
    }

    function parkHrPctForHitter(game, hand) {
        if (!game) return null;
        const h = String(hand || "").toUpperCase();
        if (h === "L" && game.parkLhbPct != null) return Number(game.parkLhbPct);
        if (game.parkRhbPct != null) return Number(game.parkRhbPct);
        if (game.parkLhbPct != null) return Number(game.parkLhbPct);
        return game.parkHrPct != null ? Number(game.parkHrPct) : null;
    }

    /** Stadium structure only — live weather/wind applied in HR env model separately. */
    function parkStadiumPctForHitter(game, hand) {
        if (!game) return null;
        const h = String(hand || "").toUpperCase();
        if (h === "L" && game.parkLhbStadiumPct != null) return Number(game.parkLhbStadiumPct);
        if (game.parkRhbStadiumPct != null) return Number(game.parkRhbStadiumPct);
        const combined = parkHrPctForHitter(game, hand);
        if (combined != null && game.parkWeatherPct != null) return Number(combined) - Number(game.parkWeatherPct);
        if (game.parkStadiumPct != null) return Number(game.parkStadiumPct);
        return combined;
    }

    function hasDecomposedPark(game) {
        return !!(
            game?.parkLhbStadiumPct != null ||
            game?.parkRhbStadiumPct != null ||
            game?.parkStadiumPct != null ||
            game?.parkStadiumOnly
        );
    }

    function dimMultScaled(dimMult, decomposed) {
        const mult = Number(dimMult);
        if (!decomposed || Number.isNaN(mult)) return mult || 1;
        return 1 + (mult - 1) * 0.5;
    }

    function clearHrTicketCache() {
        hrTicketCache = new Map();
        hrTicketScale = { min: null, max: null, ready: false };
        ticketSlatePools = null;
    }

    function rebuildHrTicketScale() {
        rebuildTicketSlatePools();
    }

    function ticketScoreTo100(rawRank) {
        if (rawRank == null || Number.isNaN(Number(rawRank))) return null;
        return Math.max(1, Math.min(100, Math.round(Number(rawRank))));
    }

    function hrTicketScore100(entry) {
        return computeHrTicket(entry)?.score100 ?? null;
    }

    function handDingerSplitPct(ps, hand) {
        const h = (hand || "R").toUpperCase();
        if (h === "L") return ps.dingerRiskLhbPct ?? ps.vsLhbPct ?? null;
        return ps.dingerRiskRhbPct ?? ps.vsRhbPct ?? null;
    }

    function fmtSavantPct(val) {
        if (val == null || Number.isNaN(Number(val))) return "—";
        return `${Math.round(Number(val))}%`;
    }

    function fmtTicketScore(val) {
        if (val == null || Number.isNaN(Number(val))) return "—";
        return `${Math.round(Number(val))}/100`;
    }

    function ticketScoreTone(score) {
        if (score == null || Number.isNaN(Number(score))) return "mid";
        const n = Number(score);
        if (n >= 75) return "prime";
        if (n >= 55) return "mid";
        return "fade";
    }

    function fmtTicketBadge(score, compact) {
        if (score == null || Number.isNaN(Number(score))) return "—";
        const n = Math.round(Number(score));
        const tone = ticketScoreTone(n);
        const cls = compact ? " rs-ticket-badge--compact" : "";
        const suffix = compact ? "" : `<span class="rs-ticket-badge__suffix">/100</span>`;
        return `<span class="rs-ticket-badge rs-ticket-badge--${tone}${cls}">${n}${suffix}</span>`;
    }

    function idsMatch(a, b) {
        if (a == null || b == null || a === "" || b === "") return false;
        return String(a) === String(b);
    }

    function hitterEntryFromDom(el) {
        const tr = el?.closest?.("tr[data-hitter-id]");
        if (!tr) return null;
        const id = tr.getAttribute("data-hitter-id");
        if (!id) return null;
        const row = sortedActiveRows().find((r) => idsMatch(r.id, id));
        return entryForActiveRow(row);
    }

    function openHitterProfileFromDom(el) {
        const entry = hitterEntryFromDom(el);
        if (entry) openPlayerProfile(entry);
    }

    function entryForActiveRow(row) {
        if (!row) return null;
        const game = activeGame();
        if (!game) return null;
        return {
            row,
            game,
            gameIdx: activeGameIdx,
            side: activeSide,
            team: activeSide === "away" ? game.away : game.home,
            pitcher: activeSide === "away" ? game.homePitcher : game.awayPitcher,
        };
    }

    function fmtTicketBadgeForRow(row) {
        const entry = entryForActiveRow(row);
        if (!entry) return "—";
        return fmtTicketBadge(hrTicketScore100(entry), tableViewMode === "full");
    }

    function ticketPillarLine(ticket) {
        if (!ticket?.pillars) return "";
        const p = ticket.pillars;
        const parts = [];
        if (p.mix != null) parts.push(`Mix ${Math.round(p.mix)}`);
        if (p.environment != null) parts.push(`Env ${Math.round(p.environment)}`);
        if (p.pitcher != null) parts.push(`SP ${Math.round(p.pitcher)}`);
        if (p.form != null) parts.push(`Form ${Math.round(p.form)}`);
        return parts.join(" · ");
    }

    function powerContactSignal(stats) {
        const barrel = stats?.barrelPct;
        const hard = stats?.hardHitPct;
        const air = stats?.airPct ?? (stats?.fbPct != null && stats?.ldPct != null ? stats.fbPct + stats.ldPct : null);
        if (barrel == null && hard == null && air == null) return null;
        let sum = 0;
        let n = 0;
        if (barrel != null) {
            sum += Number(barrel) * 0.5;
            n += 0.5;
        }
        if (hard != null) {
            sum += Number(hard) * 0.3;
            n += 0.3;
        }
        if (air != null) {
            sum += Number(air) * 0.2;
            n += 0.2;
        }
        return n > 0 ? sum / n : null;
    }

    let ticketSlatePools = null;

    function platoonEdgeForEntry(entry, statsIn) {
        // Batter xwOBA vs today's SP hand relative to season xwOBA, shrunk by
        // split PA so tiny platoon samples don't swing the score.
        const stats = statsIn || hitterStats(entry.row);
        const spHand = (entry.pitcher?.throws || "").trim().toUpperCase();
        if (spHand !== "L" && spHand !== "R") return null;
        const xw = spHand === "L" ? stats.xwobaVsLhp : stats.xwobaVsRhp;
        const pa = spHand === "L" ? stats.paVsLhp : stats.paVsRhp;
        if (xw == null || Number.isNaN(Number(xw))) return null;
        const seasonXw = stats.xwoba != null && !Number.isNaN(Number(stats.xwoba)) ? Number(stats.xwoba) : 0.32;
        const conf = Math.min((Number(pa) || 0) / 100, 1);
        return Math.round((Number(xw) - seasonXw) * 1000 * conf) / 10;
    }

    function buildTicketSlatePools(entries) {
        const pools = {
            mixPlus: [],
            platoonEdge: [],
            pitcherSplit: [],
            hrEnv: [],
            hrFormPct: [],
            powerContact: [],
        };
        for (const entry of entries) {
            const stats = hitterStats(entry.row);
            if (stats.mixPlus != null && !Number.isNaN(Number(stats.mixPlus))) {
                pools.mixPlus.push(Number(stats.mixPlus));
            }
            const platoon = platoonEdgeForEntry(entry, stats);
            if (platoon != null && !Number.isNaN(Number(platoon))) {
                pools.platoonEdge.push(Number(platoon));
            }
            const hand = (entry.row?.hand || "R").toUpperCase();
            const ps = pitcherStats(entry.pitcher);
            const split = hand === "L" ? ps.dingerRiskLhbPct : ps.dingerRiskRhbPct;
            if (split != null && !Number.isNaN(Number(split))) pools.pitcherSplit.push(Number(split));
            const env = hrEnvScore(entry);
            if (env != null && !Number.isNaN(Number(env))) pools.hrEnv.push(Number(env));
            const form = stats.hrFormPct ?? stats.hrForm;
            if (form != null && !Number.isNaN(Number(form))) pools.hrFormPct.push(Number(form));
            const power = powerContactSignal(stats);
            if (power != null && !Number.isNaN(Number(power))) pools.powerContact.push(Number(power));
        }
        return pools;
    }

    function rebuildTicketSlatePools() {
        ticketSlatePools = buildTicketSlatePools(collectSlateHitters());
    }

    function pillarPercentile(pools, key, value, higherBetter = true) {
        if (value == null || Number.isNaN(Number(value))) return null;
        const pool = pools?.[key];
        if (!pool?.length) return null;
        return percentileRank(pool, Number(value), higherBetter);
    }

    function computeHrTicket(entry) {
        if (!entry) return null;
        const key = `${entry.row?.id}-${entry.gameIdx}-${entry.side}`;
        if (hrTicketCache.has(key)) return hrTicketCache.get(key);

        const { row, game, pitcher } = entry;
        const stats = hitterStats(row);
        const hand = (row.hand || "R").toUpperCase();
        const ps = pitcherStats(pitcher);
        let mixPlus = stats.mixPlus;
        if (mixPlus == null && pitcher?.arsenal && row?.id) {
            const batterPitch = pitchMixCache?.batterPitch || slate?.batter_pitch_lookup || {};
            const leagueAvgs = pitchMixCache?.leagueAvgs || slate?.league_pitch_avgs || {};
            const mix = scoreBatterVsArsenal(
                row.id,
                pitcher.arsenal,
                batterPitch[row.id] || batterPitch[String(row.id)],
                stats.xwoba,
                leagueAvgs
            );
            mixPlus = mix?.mixPlus ?? null;
        }

        if (!ticketSlatePools) rebuildTicketSlatePools();
        const pools = ticketSlatePools;
        const weights = HR_RESEARCH_CONFIG.ticket.pillars;

        const splitPct = handDingerSplitPct(ps, hand);
        const parkPct = parkHrPctForHitter(game, hand);
        const envRaw = hrEnvScore(entry);

        // Mix pillar: pitch-mix fit blended with the batter's platoon split
        // vs today's SP hand (70/30) when split data is available.
        const platoonEdge = platoonEdgeForEntry(entry, stats);
        const mixPct = pillarPercentile(pools, "mixPlus", mixPlus, true);
        const platoonPct = pillarPercentile(pools, "platoonEdge", platoonEdge, true);
        let mixPillar = mixPct;
        if (mixPct != null && platoonPct != null) {
            mixPillar = mixPct * 0.7 + platoonPct * 0.3;
        } else if (mixPct == null) {
            mixPillar = platoonPct;
        }

        const pillars = {
            mix: mixPillar,
            pitcher: pillarPercentile(pools, "pitcherSplit", splitPct, true),
            environment: pillarPercentile(pools, "hrEnv", envRaw, true),
            form: stats.hrFormPct ?? stats.hrForm ?? pillarPercentile(pools, "hrFormPct", stats.hrFormPct, true),
            power: pillarPercentile(pools, "powerContact", powerContactSignal(stats), true),
        };

        let weighted = 0;
        let totalW = 0;
        for (const [id, w] of Object.entries(weights)) {
            const val = pillars[id];
            if (val == null || Number.isNaN(Number(val))) continue;
            weighted += Number(val) * w;
            totalW += w;
        }

        const score100 =
            totalW > 0 ? Math.max(1, Math.min(100, Math.round(weighted / totalW))) : null;

        const metrics = {
            score100,
            rank: score100,
            pillars,
            mixPlus,
            platoonEdge,
            splitPct,
            riskPct: ps.dingerRiskPct ?? ps.dingerRisk ?? null,
            parkPct,
            envPct: envRaw,
            pillarLine: ticketPillarLine({ pillars }),
        };
        hrTicketCache.set(key, metrics);
        return metrics;
    }

    const WX_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
    const WX_RHO_ZERO = 1.225;
    const WX_DA_EXPONENT = 1 / (9.80665 / (287.053 * 0.0065) - 1);
    const WX_DISTANCE_BOOST_PER_1000FT = 2.75;
    let wxBaselineDaFt = null;

    const PARK_GAME_KEY_ALIASES = {
        "MIA @ WSH": "MIA @ WAS",
        "KC @ WSH": "KC @ WAS",
        "PHI @ WSH": "PHI @ WAS",
        "CLE @ CWS": "CLE @ CHW",
        "CWS @ MIN": "CHW @ MIN",
        "CWS @ NYY": "CHW @ NYY",
    };

    function normVenueKey(name) {
        return String(name || "")
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, "")
            .replace(/\s+/g, " ")
            .trim();
    }

    function normalizeRoof(roof) {
        const value = String(roof || "open").trim().toLowerCase();
        if (value === "dome" || value === "closed") return "dome";
        if (value === "retractable" || value === "ret") return "retractable";
        return "open";
    }

    const ROOF_CLIMATE_RULES = {
        "loandepot park": { closeTempF: 92, openMin: 58, openMax: 88, closePrecip: 45, highVariance: false },
        "minute maid park": { closeTempF: 92, openMin: 55, openMax: 90, closePrecip: 45, highVariance: false },
        "globe life field": { closeTempF: 92, openMin: 55, openMax: 90, closePrecip: 40, highVariance: false },
        "chase field": { closeTempF: 95, closeTempFLow: 58, openMin: 62, openMax: 92, closePrecip: 35, highVariance: false },
        "american family field": { closeTempFLow: 50, openMin: 58, openMax: 78, closePrecip: 40, highVariance: true },
        "rogers centre": { closeTempFLow: 45, openMin: 55, openMax: 82, closePrecip: 35, highVariance: true },
        "t mobile park": { closeTempFLow: 50, openMin: 55, openMax: 80, closePrecip: 40, highVariance: true },
    };
    const OUTDOOR_WIND_VARIANCE = new Set(["wrigley field", "fenway park"]);
    const ROOF_CLOSED_RE = /roof\s*closed|closed\s*roof|\bdome\b|\bindoor|retracted/i;
    const ROOF_OPEN_RE = /roof\s*open|open\s*air|\boutdoor\b/i;

    function climateRuleKey(venue) {
        const k = normVenueKey(venue);
        if (ROOF_CLIMATE_RULES[k]) return k;
        for (const key of Object.keys(ROOF_CLIMATE_RULES)) {
            if (k.includes(key) || key.includes(k)) return key;
        }
        return k;
    }

    function parseMlbWeatherRoof(...texts) {
        const blob = texts.filter(Boolean).join(" ");
        if (!blob) return null;
        if (ROOF_CLOSED_RE.test(blob)) return "closed";
        if (ROOF_OPEN_RE.test(blob)) return "open";
        return null;
    }

    function predictRoofByClimate(venue, { tempF, precipPct, condition }) {
        const stadium = lookupStadium(venue);
        if (!stadium || normalizeRoof(stadium.roof) === "open") return { state: null, reason: "outdoor_skip" };
        if (normalizeRoof(stadium.roof) === "dome") return { state: "closed", reason: "permanent_dome" };
        const rules = ROOF_CLIMATE_RULES[climateRuleKey(venue)];
        if (!rules || tempF == null) return { state: "unknown", reason: "missing_rules_or_temp" };
        if (rules.closeTempF != null && tempF >= rules.closeTempF) return { state: "closed", reason: `hot_${tempF}F` };
        if (rules.closeTempFLow != null && tempF <= rules.closeTempFLow) return { state: "closed", reason: `cold_${tempF}F` };
        if (precipPct != null && precipPct >= rules.closePrecip) return { state: "closed", reason: `rain_${precipPct}%` };
        if (tempF >= rules.openMin && tempF <= rules.openMax && (precipPct == null || precipPct < 25)) {
            if (rules.highVariance && (precipPct == null || precipPct >= 15)) {
                return { state: "unknown", reason: `borderline_${tempF}F` };
            }
            return { state: "open", reason: `comfort_${tempF}F` };
        }
        if (rules.highVariance) return { state: "unknown", reason: `borderline_${tempF}F` };
        return { state: "open", reason: `default_${tempF}F` };
    }

    async function fetchBoxscoreWeatherStrings(gamePk) {
        if (!gamePk) return {};
        try {
            const data = await mlbGet(`/game/${gamePk}/boxscore`);
            const out = {};
            for (const item of data.info || []) {
                const label = String(item.label || "").toLowerCase();
                if (label === "weather") out.weather = item.value;
                if (label === "wind") out.wind = item.value;
            }
            return out;
        } catch (_) {
            return {};
        }
    }

    function resolveRoofStatus(game, wx) {
        const venue = game?.venue || "";
        const stadium = lookupStadium(venue);
        const roofType = normalizeRoof(stadium?.roof);
        const mlb = game?.mlbWeather || {};
        if (roofType === "open") {
            const windComp = wx?.windComponentMph;
            const windMph = wx?.windMph;
            const key = normVenueKey(venue);
            let propPass = false;
            if (OUTDOOR_WIND_VARIANCE.has(key)) {
                if (windComp == null || Math.abs(Number(windComp)) <= 4) propPass = !(windMph >= 18);
            }
            return {
                state: "skip",
                effective: "open",
                source: "outdoor",
                propPass,
                reason: propPass ? "outdoor_wind_borderline_pass" : "outdoor_skip",
            };
        }
        if (roofType === "dome") {
            return { state: "dome", effective: "closed", source: "permanent_dome", propPass: false, reason: "permanent_dome" };
        }
        const parsed =
            parseMlbWeatherRoof(mlb.condition, mlb.wind) ||
            parseMlbWeatherRoof(wx?.roofStatus?.reason);
        if (parsed) {
            return {
                state: parsed,
                effective: parsed,
                source: "mlb_schedule",
                propPass: false,
                reason: `mlb_string_${parsed}`,
            };
        }
        const climate = predictRoofByClimate(venue, {
            tempF: wx?.tempF,
            precipPct: wx?.precipPct,
            condition: mlb.condition,
        });
        const rules = ROOF_CLIMATE_RULES[climateRuleKey(venue)];
        const highVariance = rules?.highVariance;
        if (climate.state === "open" || climate.state === "closed") {
            return {
                state: climate.state,
                effective: climate.state,
                source: "climate",
                propPass: false,
                reason: climate.reason,
                highVariance,
            };
        }
        return {
            state: "unknown",
            effective: "open",
            source: "climate",
            propPass: !!highVariance,
            reason: climate.reason || "roof_unknown",
            highVariance,
        };
    }

    async function applyRoofStatusToGame(game) {
        if (!game?.parkWeather || game.parkWeather.error) return;
        const wx = game.parkWeather;
        const stadium = lookupStadium(game.venue || "");
        if (!stadium) return;
        const box = await fetchBoxscoreWeatherStrings(game.gamePk);
        const boxParsed = parseMlbWeatherRoof(box.weather, box.wind);
        let roofStatus = resolveRoofStatus(game, wx);
        if (boxParsed) {
            roofStatus = {
                state: boxParsed,
                effective: boxParsed,
                source: "mlb_boxscore",
                propPass: false,
                reason: "mlb_boxscore_weather_string",
            };
        }
        game.roofStatus = roofStatus;
        game.propPass = !!roofStatus.propPass;
        wx.roofStatus = roofStatus;
        wx.propPass = game.propPass;
        if (roofStatus.effective === "closed" || roofStatus.state === "dome") {
            const closed = buildWeatherMetrics({
                tempF: null,
                humidityPct: null,
                pressureHpa: null,
                windMph: null,
                windFromDeg: null,
                stadium,
                roof: "dome",
                venue: game.venue,
                gameHourLocal: wx.gameHourLocal,
            });
            Object.assign(wx, closed, { roofStatus, propPass: false, roof: "closed" });
            game.propPass = false;
        }
    }

    async function loadStadiumCoords() {
        if (stadiumCoords) return stadiumCoords;
        try {
            const res = await fetchDataJson("stadium-coords.json");
            stadiumCoords = res.data?.venues || {};
        } catch (_) {
            stadiumCoords = {};
        }
        return stadiumCoords;
    }

    function attachParkFactorToGame(game, lookup) {
        if (!game || !lookup) return false;
        const byGame = lookup.by_game || {};
        const byVenue = lookup.by_venue || {};
        let key = String(game.matchup || "")
            .toUpperCase()
            .replace(/\s+/g, " ")
            .trim();
        key = PARK_GAME_KEY_ALIASES[key] || key;
        let ctx = byGame[key];
        if (!ctx) {
            const vk = normVenueKey(game.venue);
            ctx = byVenue[vk];
            if (!ctx && vk) {
                for (const [venueKey, entry] of Object.entries(byVenue)) {
                    if (vk.includes(venueKey) || venueKey.includes(vk)) {
                        ctx = entry;
                        break;
                    }
                }
            }
        }
        if (!ctx) return false;
        if (ctx.hr_pct != null) game.parkHrPct = ctx.hr_pct;
        if (ctx.park_lhb_pct != null) game.parkLhbPct = ctx.park_lhb_pct;
        if (ctx.park_rhb_pct != null) game.parkRhbPct = ctx.park_rhb_pct;
        if (ctx.stadium_pct != null) game.parkStadiumPct = ctx.stadium_pct;
        if (ctx.weather_pct != null) game.parkWeatherPct = ctx.weather_pct;
        if (ctx.lhb_stadium_pct != null) game.parkLhbStadiumPct = ctx.lhb_stadium_pct;
        if (ctx.rhb_stadium_pct != null) game.parkRhbStadiumPct = ctx.rhb_stadium_pct;
        if (ctx.venue) game.venue = game.venue || ctx.venue;
        if (lookup.stadium_only) game.parkStadiumOnly = true;
        if (lookup.source_label) game.parkFactorSource = lookup.source_label;
        return true;
    }

    async function ensureParkFactorsLookup(date) {
        if (parkFactorsLookup && parkFactorsLookupDate === date) return parkFactorsLookup;
        const res = await fetchDataJson(`park-factors-${date}.json`);
        const fileLookup = res.data;
        if (
            fileLookup &&
            (Object.keys(fileLookup.by_game || {}).length || Object.keys(fileLookup.by_venue || {}).length)
        ) {
            parkFactorsLookup = fileLookup;
            parkFactorsLookupDate = date;
            return parkFactorsLookup;
        }
        try {
            const apiRes = await fetch(`/api/park-factors?date=${encodeURIComponent(date)}`);
            if (apiRes.ok) {
                const data = await apiRes.json();
                if (Object.keys(data.by_game || {}).length || Object.keys(data.by_venue || {}).length) {
                    parkFactorsLookup = data;
                    parkFactorsLookupDate = date;
                    return parkFactorsLookup;
                }
            }
        } catch (err) {
            console.warn("park-factors", err);
        }
        parkFactorsLookup = fileLookup || null;
        parkFactorsLookupDate = date;
        return parkFactorsLookup;
    }

    async function applyParkFactors(date) {
        const lookup = await ensureParkFactorsLookup(date);
        if (!lookup || (lookup.source_date && lookup.source_date !== date)) return 0;
        let n = 0;
        for (const game of slate?.games || []) {
            if (attachParkFactorToGame(game, lookup)) n += 1;
        }
        return n;
    }

    function lookupStadium(venueName) {
        const venues = stadiumCoords || {};
        const key = normVenueKey(venueName);
        if (venues[key]) return venues[key];
        for (const [alias, data] of Object.entries(venues)) {
            const ak = normVenueKey(alias);
            if (key.includes(ak) || ak.includes(key)) return data;
        }
        return null;
    }

    function compassFromDeg(deg) {
        if (deg == null || Number.isNaN(Number(deg))) return "—";
        const idx = Math.round((((Number(deg) % 360) + 360) % 360) / 22.5) % 16;
        return WX_COMPASS[idx];
    }

    function calculateDensityAltitude(tempF, relativeHumidity, stationPressureHpa) {
        if (tempF == null || relativeHumidity == null || stationPressureHpa == null) return null;
        const tempC = ((tempF - 32) * 5) / 9;
        const tempK = tempC + 273.15;
        const es = 6.11 * Math.pow(10, (7.5 * tempC) / (237.3 + tempC));
        const e = (relativeHumidity / 100) * es;
        const rDry = 287.058;
        const rVapor = 461.495;
        const pPa = stationPressureHpa * 100;
        const pVaporPa = e * 100;
        const pDryPa = pPa - pVaporPa;
        const rho = pDryPa / (rDry * tempK) + pVaporPa / (rVapor * tempK);
        const altMeters = (288.15 / 0.0065) * (1 - Math.pow(rho / WX_RHO_ZERO, WX_DA_EXPONENT));
        return Math.round(altMeters * 3.28084);
    }

    function baselineDaFt() {
        if (wxBaselineDaFt == null) {
            wxBaselineDaFt = calculateDensityAltitude(75, 55, 1013.25) ?? 0;
        }
        return wxBaselineDaFt;
    }

    function typicalGameDaFt() {
        return baselineDaFt();
    }

    function clampDisplayPct(n, lo = -22, hi = 22) {
        if (n == null || Number.isNaN(Number(n))) return null;
        return Math.max(lo, Math.min(hi, Math.round(Number(n))));
    }

    /** Symmetric carry % vs a typical 75°F MLB game — not sea-level ideal air. */
    function displayHrCarryPct(wx) {
        const da = wx?.densityAltFt;
        if (da == null) return null;
        const daDelta = da - typicalGameDaFt();
        return clampDisplayPct(daDelta / 250);
    }

    /** Linear wind impact — 10 mph out ≈ +10%, 10 mph in ≈ −10%. */
    function displayWindPct(windComponentMph) {
        if (windComponentMph == null || Number.isNaN(Number(windComponentMph))) return null;
        return clampDisplayPct(Number(windComponentMph) * 1.0);
    }

    /** Fence boost vs league-average pull alley distance (377 ft). */
    function displayFencePct(wallFt, refFt = 377) {
        if (wallFt == null) return null;
        return clampDisplayPct(((refFt - Number(wallFt)) / 3) * 3.7);
    }

    function displayHumidityCarryPct(humidityPct) {
        if (humidityPct == null) return null;
        return clampDisplayPct((55 - Number(humidityPct)) * 0.15);
    }

    function displayPressureCarryPct(pressureHpa) {
        if (pressureHpa == null) return null;
        return clampDisplayPct((1013 - Number(pressureHpa)) * 0.12);
    }

    function displayDistanceBoostFt(wx) {
        const da = wx?.densityAltFt;
        if (da == null) return null;
        const delta = da - typicalGameDaFt();
        return Math.round((delta / 1000) * WX_DISTANCE_BOOST_PER_1000FT * 10) / 10;
    }

    function windComponentTowardCf(windFromDeg, windMph, cfBearingDeg) {
        if (windFromDeg == null || windMph == null || cfBearingDeg == null) return null;
        const windTo = (Number(windFromDeg) + 180) % 360;
        const angleRad = ((windTo - Number(cfBearingDeg)) * Math.PI) / 180;
        return Math.round(Number(windMph) * Math.cos(angleRad) * 10) / 10;
    }

    function distanceBoostFt(densityAltFt) {
        if (densityAltFt == null) return null;
        const delta = densityAltFt - baselineDaFt();
        return Math.round((delta / 1000) * WX_DISTANCE_BOOST_PER_1000FT * 10) / 10;
    }

    function hrCarryScoreFromWx({ densityAltFt, windComponentMph, roof }) {
        if (normalizeRoof(roof) === "dome") return { score: 0, label: "Dome — weather neutral" };
        let score = 0;
        const baseline = baselineDaFt();
        if (densityAltFt != null) {
            const daDelta = densityAltFt - baseline;
            if (daDelta >= 1500) score += 3;
            else if (daDelta >= 800) score += 2;
            else if (daDelta >= 300) score += 1;
            else if (daDelta <= -800) score -= 2;
            else if (daDelta <= -300) score -= 1;
        }
        if (windComponentMph != null) {
            if (windComponentMph >= 10) score += 2;
            else if (windComponentMph >= 5) score += 1;
            else if (windComponentMph <= -10) score -= 2;
            else if (windComponentMph <= -5) score -= 1;
        }
        if (score >= 2) return { score, label: "Helps HR carry" };
        if (score <= -2) return { score, label: "Suppresses carry" };
        return { score, label: "Neutral carry" };
    }

    function buildWeatherMetrics({
        tempF,
        humidityPct,
        pressureHpa,
        windMph,
        windFromDeg,
        stadium,
        roof,
        precipPct,
        gameHourLocal,
        venue,
    }) {
        const roofType = normalizeRoof(roof || stadium?.roof);
        const bearing = stadium?.bearing;

        if (roofType === "dome") {
            const carry = hrCarryScoreFromWx({ roof: roofType });
            return {
                source: "dome-neutral",
                venue,
                gameHourLocal,
                tempF: 72,
                humidityPct: 40,
                windMph: 0,
                windDirDeg: null,
                windDir: "—",
                windComponentMph: 0,
                pressureHpa: 1013.3,
                precipPct,
                roof: roofType,
                cfBearing: bearing,
                densityAltFt: 0,
                baselineDaFt: baselineDaFt(),
                distanceBoostFt: 0,
                hrCarryScore: carry.score,
                hrCarryLabel: carry.label,
            };
        }

        const densityAltFt = calculateDensityAltitude(tempF, humidityPct, pressureHpa);
        const windComponentMph = windComponentTowardCf(windFromDeg, windMph, bearing);
        const distBoost = distanceBoostFt(densityAltFt);
        const carry = hrCarryScoreFromWx({
            densityAltFt,
            windComponentMph,
            roof: roofType,
        });

        return {
            source: "open-meteo",
            venue,
            gameHourLocal,
            tempF,
            humidityPct,
            windMph: windMph == null ? null : Math.round(Number(windMph) * 10) / 10,
            windDirDeg: windFromDeg == null ? null : Math.round(Number(windFromDeg)),
            windDir: compassFromDeg(windFromDeg),
            windComponentMph,
            pressureHpa: pressureHpa == null ? null : Math.round(Number(pressureHpa) * 10) / 10,
            precipPct,
            roof: roofType,
            cfBearing: bearing,
            densityAltFt,
            baselineDaFt: baselineDaFt(),
            distanceBoostFt: distBoost,
            hrCarryScore: carry.score,
            hrCarryLabel: carry.label,
        };
    }

    function fmtHrPropPct(row, game) {
        const g = game || activeGame();
        if (row?.hrProp?.propPass || g?.propPass) return "PASS";
        const pct = row?.hrProp?.combinedPct;
        if (pct == null || Number.isNaN(Number(pct))) return "—";
        const n = Math.round(Number(pct) * 10) / 10;
        if (n === 0) return "0%";
        const sign = n > 0 ? "+" : "";
        return `${sign}${n}%`;
    }

    function hrPropHeatClass(row, game) {
        const g = game || activeGame();
        if (row?.hrProp?.propPass || g?.propPass) return "rs-cell-heat rs-cell-heat--mid";
        const pct = row?.hrProp?.combinedPct;
        if (pct == null || Number.isNaN(Number(pct))) return "";
        return `rs-cell-heat rs-cell-heat--${edgeTone(pct)}`;
    }

    function refreshHrEnvUi() {
        refreshAllHrProps();
        renderExplorePanel();
        renderTable();
        renderMobileCards();
    }

    function fmtPitcherRisk(stats) {
        if (!stats) return "";
        const parts = [];
        if (stats.dingerRiskPct != null) parts.push(`Dinger risk ${stats.dingerRiskPct}%`);
        else if (stats.dingerRisk != null) parts.push(`Dinger risk ${Math.round(stats.dingerRisk)}%`);
        if (stats.hrRiskPct != null) parts.push(`HR risk ${stats.hrRiskPct > 0 ? "+" : ""}${stats.hrRiskPct}%`);
        if (stats.hr9 != null) parts.push(`${Number(stats.hr9).toFixed(2)} HR/9`);
        if (stats.vsLhbPct != null && stats.vsRhbPct != null) {
            parts.push(`L ${stats.vsLhbPct > 0 ? "+" : ""}${stats.vsLhbPct}% · R ${stats.vsRhbPct > 0 ? "+" : ""}${stats.vsRhbPct}%`);
        }
        return parts.join(" · ");
    }

    function rawPitcherStats(pitcher) {
        return pitcher?.stats || {};
    }

    function pitcherStats(pitcher) {
        const stats = rawPitcherStats(pitcher);
        if (stats.hr9 != null && !Number.isNaN(Number(stats.hr9))) return stats;
        const hr9 = resolvePitcherHr9(pitcher, stats);
        if (hr9 != null) return { ...stats, hr9 };
        return stats;
    }

    function resolvePitcherHr9(pitcher, statsIn) {
        const stats = statsIn || rawPitcherStats(pitcher);
        if (stats.hr9 != null && !Number.isNaN(Number(stats.hr9))) return Number(stats.hr9);
        const ip = stats.inningsPitched ?? stats.ip;
        if (stats.hrAllowed != null && ip != null && Number(ip) > 0) {
            return Math.round((Number(stats.hrAllowed) / Number(ip)) * 9 * 100) / 100;
        }
        const lhb = handSavantStatsForPitcher(pitcher, "lhb");
        const rhb = handSavantStatsForPitcher(pitcher, "rhb");
        const parts = [lhb, rhb].filter((h) => h && h.hr9 != null && h.pa);
        if (parts.length) {
            const pa = parts.reduce((sum, h) => sum + Number(h.pa), 0);
            const weighted = parts.reduce((sum, h) => sum + Number(h.hr9) * Number(h.pa), 0);
            if (pa > 0) return Math.round((weighted / pa) * 100) / 100;
        }
        let hr = 0;
        let pa = 0;
        for (const h of [lhb, rhb]) {
            if (!h) continue;
            if (h.hrAllowed != null) hr += Number(h.hrAllowed);
            if (h.pa) pa += Number(h.pa);
        }
        if (pa > 0) return Math.round((hr / pa) * 27 * 100) / 100;
        return null;
    }

    function patchPitcherHr9OnSlate() {
        for (const entry of collectSlatePitcherEntries()) {
            const stats = entry.pitcher?.stats || {};
            if (stats.hr9 != null) continue;
            const hr9 = resolvePitcherHr9(entry.pitcher, stats);
            if (hr9 != null) entry.pitcher.stats = { ...stats, hr9, hr9Source: stats.hr9Source || "derived" };
        }
    }

    const PITCHER_GROUPS = [
        { id: "leak", label: "Contact leak" },
        { id: "command", label: "Command & outcomes" },
    ];

    const PITCHER_METRICS = [
        { key: "barrelPct", label: "Barrel%", stat: "barrelPct", group: "leak", fmt: (s) => fmtPct(s.barrelPct), tip: "Barrels allowed — batted balls with ideal exit velo and launch angle for damage. Higher Barrel% means hitters square this pitcher up more, which directly raises HR odds.", hrHigherIsGreen: true },
        { key: "hardHitPct", label: "Hard-Hit%", stat: "hardHitPct", group: "leak", fmt: (s) => fmtPct(s.hardHitPct), tip: "Hard contact allowed at 95+ mph. Harder contact carries farther; a high Hard-Hit% means batters are driving the ball with homer-level authority off this arm.", hrHigherIsGreen: true },
        { key: "avgEV", label: "EV", stat: "avgEV", group: "leak", fmt: (s) => fmtEv(s.avgEV), tip: "Average exit velocity allowed. Higher EV = more carry on fly balls and a better chance any contact leaves the yard.", hrHigherIsGreen: true },
        { key: "fbPct", label: "FB%", stat: "fbPct", group: "leak", fmt: (s) => fmtPct(s.fbPct), tip: "Fly-ball rate allowed. Homers need air — fly-ball pitchers give hitters more chances to lift one over the fence.", hrHigherIsGreen: true },
        { key: "hrFbPct", label: "HR/FB%", stat: "hrFbPct", group: "leak", fmt: (s) => fmtPct(s.hrFbPct), tip: "How often allowed fly balls become homers. High HR/FB% means when hitters get the ball in the air, this pitcher frequently pays for it.", hrHigherIsGreen: true },
        { key: "pullPct", label: "Pull%", stat: "pullPct", group: "leak", fmt: (s) => fmtPct(s.pullPct), tip: "Pull-side contact allowed. Pulled fly balls to the short porch are classic HR paths — higher Pull% can boost pull-side HR upside.", hrHigherIsGreen: true },
        { key: "sweetSpotPct", label: "Sweet Spot%", stat: "sweetSpotPct", group: "leak", fmt: (s) => fmtPct(s.sweetSpotPct), tip: "Contact allowed in the 8–32° launch-angle sweet spot. More sweet-spot contact = more balls hit at HR-friendly angles.", hrHigherIsGreen: true },
        { key: "meatballPct", label: "Meatball%", stat: "meatballPct", group: "leak", fmt: (s) => fmtPct(s.meatballPct), tip: "Middle-middle mistake pitches. More meatballs = more hittable pitches in the heart of the zone for batters to drive for power.", hrHigherIsGreen: true },
        { key: "zonePct", label: "Zone%", stat: "zonePct", group: "command", fmt: (s) => fmtPct(s.zonePct), tip: "In-zone pitch rate. More strikes in the zone can mean more contact chances — useful HR context when paired with high hard-hit or barrel rates allowed.", hrHigherIsGreen: true },
        { key: "edgePct", label: "Edge%", stat: "edgePct", group: "command", fmt: (s) => fmtPct(s.edgePct), tip: "Edge-of-zone pitch rate. Shows command shape; when edge-heavy profiles still leak barrels and fly balls, hitters can still find HR lanes.", hrHigherIsGreen: false },
        { key: "whiffPct", label: "Whiff%", stat: "whiffPct", group: "command", fmt: (s) => fmtPct(s.whiffPct), tip: "Swing-and-miss rate induced. Lower whiff often means more balls in play — which helps HR props when contact quality allowed is also high.", hrHigherIsGreen: false },
        { key: "kPct", label: "K%", stat: "kPct", group: "command", fmt: (s) => fmtPct(s.kPct), tip: "Strikeout rate. Lower K% = more contact opportunities. Contact-heavy arms can be HR-friendly when they also allow hard fly-ball damage.", hrHigherIsGreen: false },
        { key: "sierra", label: "SIERA", stat: "sierra", group: "command", fmt: (s) => fmtRate(s.sierra), tip: "Skill-interactive ERA proxy (Savant xERA). Higher = weaker contact suppression overall — more HR-friendly when paired with hard contact allowed.", hrHigherIsGreen: true },
        { key: "hr9", label: "HR/9", stat: "hr9", group: "command", fmt: (s) => (s.hr9 != null ? Number(s.hr9).toFixed(2) : "—"), tip: "Homers allowed per nine innings. Direct HR rate — higher HR/9 means this pitcher has already been taken deep often this season.", hrHigherIsGreen: true },
    ];

    const DINGER_RISK_TIPS = {
        Overall:
            "Weighted slate score from HR/9, barrels, fly balls, meatballs, and more. Higher % = greener = better overall HR target for batters today.",
        LHB: "HR vulnerability vs left-handed hitters on today's slate. Higher % = lefty bats have a better homer lane against this pitcher.",
        RHB: "HR vulnerability vs right-handed hitters on today's slate. Higher % = righty bats have a better homer lane against this pitcher.",
    };

    const DINGER_RISK_WEIGHTS = {
        hr9: 22,
        barrelPct: 20,
        hrFbPct: 16,
        hardHitPct: 14,
        fbPct: 10,
        meatballPct: 10,
        sweetSpotPct: 5,
        kPct: 3,
    };

    function collectSlatePitcherEntries() {
        const entries = [];
        for (const game of slate?.games || []) {
            for (const side of ["away", "home"]) {
                const key = side === "away" ? "awayPitcher" : "homePitcher";
                const pitcher = game[key];
                if (!pitcher?.name) continue;
                entries.push({ game, side, pitcher });
            }
        }
        return entries;
    }

    function percentileRank(values, value, higherIsRiskier) {
        if (!values.length) return 50;
        if (values.length === 1) return 50;
        const sorted = [...values].sort((a, b) => a - b);
        if (higherIsRiskier) {
            const below = sorted.filter((v) => v < value).length;
            const equal = sorted.filter((v) => v === value).length;
            return ((below + 0.5 * equal) / sorted.length) * 100;
        }
        const above = sorted.filter((v) => v > value).length;
        const equal = sorted.filter((v) => v === value).length;
        return ((above + 0.5 * equal) / sorted.length) * 100;
    }

    function ensurePitcherHandLookupSync() {
        if (pitcherHandLookup && Object.keys(pitcherHandLookup).length) return pitcherHandLookup;
        if (slate?.pitcher_hand_lookup && Object.keys(slate.pitcher_hand_lookup).length) {
            pitcherHandLookup = slate.pitcher_hand_lookup;
        }
        return pitcherHandLookup;
    }

    function computeDingerRiskForSlate() {
        ensurePitcherHandLookupSync();
        patchPitcherHr9OnSlate();
        const entries = collectSlatePitcherEntries();
        if (!entries.length) return;
        const metricPools = {};
        for (const key of Object.keys(DINGER_RISK_WEIGHTS)) {
            metricPools[key] = entries
                .map((e) => Number(pitcherStats(e.pitcher)[key]))
                .filter((n) => !Number.isNaN(n));
        }
        const ranked = [];
        for (const entry of entries) {
            const stats = pitcherStats(entry.pitcher);
            let weighted = 0;
            let totalWeight = 0;
            for (const [key, weight] of Object.entries(DINGER_RISK_WEIGHTS)) {
                const val = stats[key];
                if (val == null || Number.isNaN(Number(val))) continue;
                const pool = metricPools[key];
                if (!pool?.length) continue;
                const pct = percentileRank(pool, Number(val), key !== "kPct");
                weighted += pct * weight;
                totalWeight += weight;
            }
            if (totalWeight <= 0) continue;
            const score = Math.round((weighted / totalWeight) * 10) / 10;
            entry.pitcher.stats = { ...stats, dingerRisk: score, dingerRiskPct: Math.round(score) };
            ranked.push({ entry, score });
        }
        ranked.sort((a, b) => b.score - a.score);
        ranked.forEach(({ entry }, idx) => {
            entry.pitcher.stats = {
                ...pitcherStats(entry.pitcher),
                dingerRiskRank: idx + 1,
                dingerRiskSlateSize: ranked.length,
            };
        });

        const lhbPool = entries
            .map((e) => Number(pitcherStats(e.pitcher).vsLhb))
            .filter((n) => !Number.isNaN(n));
        const rhbPool = entries
            .map((e) => Number(pitcherStats(e.pitcher).vsRhb))
            .filter((n) => !Number.isNaN(n));
        for (const entry of entries) {
            const s = pitcherStats(entry.pitcher);
            const patch = {};
            if (s.vsLhb != null && !Number.isNaN(Number(s.vsLhb)) && lhbPool.length) {
                patch.dingerRiskLhbPct = Math.round(percentileRank(lhbPool, Number(s.vsLhb), true));
                patch.dingerRiskLhbPctSource = "propfinder";
            }
            if (s.vsRhb != null && !Number.isNaN(Number(s.vsRhb)) && rhbPool.length) {
                patch.dingerRiskRhbPct = Math.round(percentileRank(rhbPool, Number(s.vsRhb), true));
                patch.dingerRiskRhbPctSource = "propfinder";
            }
            if (Object.keys(patch).length) {
                entry.pitcher.stats = { ...s, ...patch };
            }
        }

        computeHandDingerFromSavant(entries, "lhb", "dingerRiskLhbPct");
        computeHandDingerFromSavant(entries, "rhb", "dingerRiskRhbPct");
    }

    function computeWeightedKPercentile(stats, weights, metricPools) {
        let weighted = 0;
        let totalWeight = 0;
        for (const [key, weight] of Object.entries(weights)) {
            const val = stats[key];
            if (val == null || Number.isNaN(Number(val))) continue;
            const pool = metricPools[key];
            if (!pool?.length) continue;
            const pct = percentileRank(pool, Number(val), true);
            weighted += pct * weight;
            totalWeight += weight;
        }
        if (totalWeight <= 0) return null;
        return Math.round((weighted / totalWeight) * 10) / 10;
    }

    function opposingLineupForPitcherEntry(entry) {
        const game = entry.game;
        return entry.side === "away" ? game.homeLineup || [] : game.awayLineup || [];
    }

    function avgLineupKPct(lineup) {
        const rows = lineup || [];
        if (!rows.length) return null;
        let weighted = 0;
        let totalW = 0;
        for (const r of rows) {
            const k = hitterStats(r).kPct;
            if (k == null || Number.isNaN(Number(k))) continue;
            const order = Number(r.order) || 9;
            const w = order <= 4 ? 1.3 : 1.0;
            weighted += Number(k) * w;
            totalW += w;
        }
        if (totalW <= 0) return null;
        return Math.round((weighted / totalW) * 10) / 10;
    }

    function lineupHandDominance(lineup) {
        let l = 0;
        let r = 0;
        for (const row of lineup || []) {
            const h = (row.hand || "R").toUpperCase();
            if (h === "L" || h === "S") l += 1;
            else r += 1;
        }
        const total = l + r;
        if (!total) return null;
        if (l / total >= 0.7) return "L";
        if (r / total >= 0.7) return "R";
        return null;
    }

    function computeHandKFromSavant(entries, handKey, statKey) {
        const pairs = [];
        for (const entry of entries) {
            const hstats = handSavantStatsForPitcher(entry.pitcher, handKey);
            if (hstats) pairs.push({ entry, hstats });
        }
        if (!pairs.length) return;
        const metricPools = {};
        for (const key of Object.keys(K_HAND_WEIGHTS)) {
            metricPools[key] = pairs
                .map((p) => Number(p.hstats[key]))
                .filter((n) => !Number.isNaN(n));
        }
        for (const { entry, hstats } of pairs) {
            const stats = pitcherStats(entry.pitcher);
            if (stats[statKey] != null) continue;
            const score = computeWeightedKPercentile(hstats, K_HAND_WEIGHTS, metricPools);
            if (score == null) continue;
            entry.pitcher.stats = {
                ...stats,
                [statKey]: Math.round(score),
                [`${statKey}Source`]: "savant-hand",
            };
        }
    }

    function computeKScoreForSlate() {
        const entries = collectSlatePitcherEntries();
        if (!entries.length) return;

        const stuffPools = {};
        for (const key of Object.keys(K_STUFF_WEIGHTS)) {
            stuffPools[key] = entries
                .map((e) => Number(pitcherStats(e.pitcher)[key]))
                .filter((n) => !Number.isNaN(n));
        }

        const lineupKPools = entries
            .map((e) => avgLineupKPct(opposingLineupForPitcherEntry(e)))
            .filter((v) => v != null && !Number.isNaN(Number(v)));

        const ranked = [];
        for (const entry of entries) {
            const stats = pitcherStats(entry.pitcher);
            let kStuff = computeWeightedKPercentile(stats, K_STUFF_WEIGHTS, stuffPools);
            const domHand = lineupHandDominance(opposingLineupForPitcherEntry(entry));
            if (domHand) {
                const handStat = domHand === "L" ? stats.kStuffLhbPct : stats.kStuffRhbPct;
                if (handStat != null && !Number.isNaN(Number(handStat))) {
                    kStuff =
                        kStuff != null
                            ? Math.round((kStuff * 0.55 + Number(handStat) * 0.45) * 10) / 10
                            : Number(handStat);
                }
            }
            const lineupK = avgLineupKPct(opposingLineupForPitcherEntry(entry));
            let kMatch = null;
            if (lineupK != null && lineupKPools.length) {
                kMatch = Math.round(percentileRank(lineupKPools, lineupK, true) * 10) / 10;
            }
            let kPick = null;
            if (kStuff != null && kMatch != null) {
                kPick = Math.round((kStuff * 0.7 + kMatch * 0.3) * 10) / 10;
            } else if (kStuff != null) {
                kPick = kStuff;
            }
            const patch = {};
            if (kStuff != null) {
                patch.kStuffPct = Math.round(kStuff);
                patch.kStuff = kStuff;
            }
            if (kMatch != null) {
                patch.kMatchPct = Math.round(kMatch);
                patch.lineupAvgKPct = lineupK;
            }
            if (kPick != null) {
                patch.kPickPct = Math.round(kPick);
                patch.kPick = kPick;
            }
            entry.pitcher.stats = { ...stats, ...patch };
            if (kPick != null) ranked.push({ entry, score: kPick });
        }

        ranked.sort((a, b) => b.score - a.score);
        ranked.forEach(({ entry }, idx) => {
            entry.pitcher.stats = {
                ...pitcherStats(entry.pitcher),
                kPickRank: idx + 1,
                kPickSlateSize: ranked.length,
            };
        });

        computeHandKFromSavant(entries, "lhb", "kStuffLhbPct");
        computeHandKFromSavant(entries, "rhb", "kStuffRhbPct");
        computeKProjectionsForSlate();
    }

    const K_PROJ_LEAGUE_K_PCT = 22.5;
    const K_PROJ_BF_PER_IP = 4.28;

    function median(nums) {
        const arr = nums.filter((n) => n != null && !Number.isNaN(Number(n))).sort((a, b) => a - b);
        if (!arr.length) return null;
        const mid = Math.floor(arr.length / 2);
        return arr.length % 2 ? arr[mid] : (arr[mid - 1] + arr[mid]) / 2;
    }

    function pitcherRollingStarts() {
        return slate?.stat_windows?.pitchers?.starts ?? 10;
    }

    function summarizePitcherStarts(games) {
        const starts = (games || []).filter((g) => g.ip != null && Number(g.ip) > 0);
        const n = pitcherRollingStarts();
        const recent = starts.slice(-n);
        if (!recent.length) return { k9Recent: null, medianIp: null, maxK: null, maxIp: null, avgK: null };
        let kSum = 0;
        let ipSum = 0;
        const k9s = [];
        const ks = [];
        const ips = [];
        for (const g of recent) {
            if (g.k != null) {
                kSum += Number(g.k);
                ks.push(Number(g.k));
            }
            if (g.ip != null) {
                ipSum += Number(g.ip);
                ips.push(Number(g.ip));
            }
            if (g.k != null && g.ip > 0) k9s.push((Number(g.k) / Number(g.ip)) * 9);
        }
        return {
            k9Recent: k9s.length ? k9s.reduce((a, b) => a + b, 0) / k9s.length : null,
            medianIp: median(ips),
            maxK: ks.length ? Math.max(...ks) : null,
            maxIp: ips.length ? Math.max(...ips) : null,
            avgK: ks.length ? kSum / ks.length : null,
        };
    }

    function seasonPitcherK9(stats, games) {
        // Only count starts that report both K and IP, so a log missing
        // strikeout data can't produce a bogus 0 K/9.
        const starts = (games || []).filter(
            (g) => g.ip != null && Number(g.ip) > 0 && g.k != null && !Number.isNaN(Number(g.k))
        );
        let k = 0;
        let ip = 0;
        for (const g of starts) {
            k += Number(g.k);
            ip += Number(g.ip);
        }
        if (ip >= 8) return (k / ip) * 9;
        const seasonIp = stats.inningsPitched ?? stats.ip;
        if (
            stats.kPct != null &&
            stats.pa != null &&
            seasonIp != null &&
            Number(seasonIp) > 0 &&
            !Number.isNaN(Number(stats.kPct))
        ) {
            const estK = (Number(stats.kPct) / 100) * Number(stats.pa);
            return (estK / Number(seasonIp)) * 9;
        }
        if (stats.kPct != null && !Number.isNaN(Number(stats.kPct))) {
            return (Number(stats.kPct) / 100) * K_PROJ_BF_PER_IP * 9;
        }
        return null;
    }

    function suggestKLine(expK, kPick) {
        if (expK == null || Number.isNaN(Number(expK))) return { line: null, lean: null };
        const exp = Number(expK);
        const line = Math.max(2.5, Math.round(exp * 2) / 2);
        const buffer = exp - line;
        const pick = kPick != null ? Number(kPick) : 50;
        let lean = "O";
        if (buffer < -0.3) lean = "U";
        else if (buffer < 0.12 && pick < 50) lean = "U";
        else if (buffer >= 0.32 || pick >= 65) lean = "O";
        else lean = buffer >= 0 ? "O" : "U";
        return { line, lean };
    }

    function opposingTeamLabel(entry) {
        const game = entry.game;
        return entry.side === "away" ? game.home : game.away;
    }

    function computeKProjection(entry, gameLog) {
        const stats = pitcherStats(entry.pitcher);
        const lineupK = avgLineupKPct(opposingLineupForPitcherEntry(entry));
        const startSum = summarizePitcherStarts(gameLog);
        const seasonIp = stats.inningsPitched ?? stats.ip;
        const startCount = (gameLog || []).filter((g) => g.ip != null && Number(g.ip) > 0).length || 0;
        const seasonIpPerStart =
            seasonIp != null && startCount > 0
                ? Number(seasonIp) / startCount
                : startSum.medianIp ?? 5.3;

        let expIp = startSum.medianIp != null ? startSum.medianIp * 0.62 + seasonIpPerStart * 0.38 : seasonIpPerStart;
        expIp = Math.max(3.8, Math.min(7.1, expIp));

        const seasonK9 = seasonPitcherK9(stats, gameLog);
        const whiffBoost = stats.whiffPct != null ? (Number(stats.whiffPct) - 24) * 0.07 : 0;
        let effK9 = seasonK9;
        if (effK9 != null && startSum.k9Recent != null) {
            effK9 = seasonK9 * 0.48 + startSum.k9Recent * 0.38 + (seasonK9 + whiffBoost) * 0.14;
        } else if (effK9 != null) {
            effK9 = effK9 + whiffBoost * 0.45;
        }

        const domHand = lineupHandDominance(opposingLineupForPitcherEntry(entry));
        if (domHand && effK9 != null) {
            const handKey = domHand === "L" ? "lhb" : "rhb";
            const hstats = handSavantStatsForPitcher(entry.pitcher, handKey);
            const handK9 = hstats ? seasonPitcherK9(hstats, null) : null;
            if (handK9 != null) {
                effK9 = effK9 * 0.64 + handK9 * 0.36;
            }
        }

        let matchMult = 1;
        if (lineupK != null) {
            matchMult = 1 + ((Number(lineupK) - K_PROJ_LEAGUE_K_PCT) / K_PROJ_LEAGUE_K_PCT) * 0.5;
            matchMult = Math.max(0.86, Math.min(1.2, matchMult));
        }

        // Use K stuff only — kPick already blends lineup K%, which matchMult
        // above accounts for, so using kPick here would double-count it.
        const kPick = stats.kPick ?? stats.kPickPct;
        const kStuff = stats.kStuff ?? stats.kStuffPct;
        const pickMult = kStuff != null ? 0.95 + (Number(kStuff) / 100) * 0.09 : 1;

        const expK =
            effK9 != null ? Math.round(((expIp / 9) * effK9 * matchMult * pickMult) * 10) / 10 : null;

        const ceilIp = Math.min(7.8, Math.max(startSum.maxIp ?? expIp, expIp + 1.0));
        const ceilK9 = effK9 != null ? effK9 * 1.12 : null;
        let ceilingK =
            ceilK9 != null
                ? Math.round(((ceilIp / 9) * ceilK9 * Math.min(matchMult * 1.05, 1.18)) * 10) / 10
                : null;
        if (startSum.maxK != null && ceilingK != null) {
            ceilingK = Math.round(Math.max(ceilingK, Number(startSum.maxK) + 0.5) * 10) / 10;
        }

        const { line, lean } = suggestKLine(expK, kPick);

        return {
            expK,
            ceilingK,
            expIp: Math.round(expIp * 10) / 10,
            effK9: effK9 != null ? Math.round(effK9 * 10) / 10 : null,
            suggestedLine: line,
            lean,
            lineupAvgKPct: lineupK,
            kPick,
        };
    }

    function pitcherGameLogFromCache(pitcher, season) {
        const id = pitcher?.id;
        if (!id) return [];
        return pitcherTrendsCache.get(`${id}:${season}`) || [];
    }

    function applyKProjectionToEntry(entry, gameLog) {
        const proj = computeKProjection(entry, gameLog);
        if (proj.expK == null) return;
        entry.pitcher.stats = {
            ...pitcherStats(entry.pitcher),
            kProjExp: proj.expK,
            kProjCeiling: proj.ceilingK,
            kProjIp: proj.expIp,
            kProjK9: proj.effK9,
            kProjLine: proj.suggestedLine,
            kProjLean: proj.lean,
            kProj: proj,
        };
    }

    function computeKProjectionsForSlate() {
        const season = seasonFromDate(slate?.sheet_date || els.dateInput?.value || sheetDateFromQuery());
        for (const entry of collectSlatePitcherEntries()) {
            const log = pitcherGameLogFromCache(entry.pitcher, season);
            applyKProjectionToEntry(entry, log);
        }
    }

    let kProjHydrateGen = 0;

    async function hydrateKProjectionsFromTrends() {
        const season = seasonFromDate(slate?.sheet_date || els.dateInput?.value || sheetDateFromQuery());
        const entries = collectSlatePitcherEntries();
        const gen = ++kProjHydrateGen;
        await Promise.all(
            entries.map(async (entry) => {
                const id = entry.pitcher?.id;
                if (!id) return;
                const games = await fetchPitcherTrends(id, season);
                if (gen !== kProjHydrateGen) return;
                applyKProjectionToEntry(entry, games);
            })
        );
        if (gen !== kProjHydrateGen) return;
        renderPitcherPanel().catch(() => {});
    }

    function computePitcherScoresForSlate() {
        computeDingerRiskForSlate();
        computeKScoreForSlate();
    }

    function handSavantStatsForPitcher(pitcher, handKey) {
        const lookup = ensurePitcherHandLookupSync() || {};
        const pid = pitcher?.id;
        const bucket = lookup?.[pid] || lookup?.[String(pid)];
        const split = bucket?.[handKey];
        if (!split) return null;
        const main = rawPitcherStats(pitcher);
        return { ...split, hr9: split.hr9 ?? main.hr9 };
    }

    function computeHandDingerFromSavant(entries, handKey, statKey) {
        const pairs = [];
        for (const entry of entries) {
            const hstats = handSavantStatsForPitcher(entry.pitcher, handKey);
            if (hstats) pairs.push({ entry, hstats });
        }
        if (!pairs.length) return;
        const metricPools = {};
        for (const key of Object.keys(DINGER_RISK_WEIGHTS)) {
            metricPools[key] = pairs
                .map((p) => Number(p.hstats[key]))
                .filter((n) => !Number.isNaN(n));
        }
        for (const { entry, hstats } of pairs) {
            const stats = pitcherStats(entry.pitcher);
            if (stats[statKey] != null) continue;
            let weighted = 0;
            let totalWeight = 0;
            for (const [key, weight] of Object.entries(DINGER_RISK_WEIGHTS)) {
                const val = hstats[key];
                if (val == null || Number.isNaN(Number(val))) continue;
                const pool = metricPools[key];
                if (!pool?.length) continue;
                const pct = percentileRank(pool, Number(val), key !== "kPct");
                weighted += pct * weight;
                totalWeight += weight;
            }
            if (totalWeight <= 0) continue;
            const score = Math.round((weighted / totalWeight) * 10) / 10;
            entry.pitcher.stats = {
                ...stats,
                [statKey]: Math.round(score),
                [`${statKey}Source`]: "savant-hand",
            };
        }
    }

    async function ensurePitcherHandLookup(season) {
        if (pitcherHandLookup && Object.keys(pitcherHandLookup).length) return pitcherHandLookup;
        if (slate?.pitcher_hand_lookup && Object.keys(slate.pitcher_hand_lookup).length) {
            pitcherHandLookup = slate.pitcher_hand_lookup;
            return pitcherHandLookup;
        }
        const cached = await fetchDataJson(`savant-pitcher-hand-${season}.json`);
        pitcherHandLookup = cached.data?.lookup || {};
        return pitcherHandLookup;
    }

    function fmtPitcherHand(pitcher, teamAbbr) {
        const hand = (pitcher?.throws || "").trim().toUpperCase();
        const handLabel = hand === "L" || hand === "R" || hand === "S" ? hand : "—";
        return teamAbbr ? `(${handLabel}, ${teamAbbr})` : `(${handLabel})`;
    }

    function pitcherMetricHeatClass(metric, statsList, stats) {
        if (metric.key === "dingerRisk") {
            const vals = statsList.map((s) => s.dingerRisk).filter((v) => v != null && !Number.isNaN(Number(v)));
            return heatClass(vals, stats.dingerRisk, true);
        }
        if (metric.hrHigherIsGreen == null) return "";
        const statKey = metric.stat;
        const vals = statsList.map((s) => Number(s[statKey])).filter((n) => !Number.isNaN(n));
        const val = stats[statKey];
        if (val == null || Number.isNaN(Number(val))) return "";
        // Hitter lens: green = this stat profile supports batter HR props.
        return heatClass(vals, Number(val), metric.hrHigherIsGreen);
    }

    function fmtDingerRiskValue(pct) {
        if (pct == null || Number.isNaN(Number(pct))) return "—";
        return `${Math.round(Number(pct))}%`;
    }

    function dingerRiskTone(score) {
        if (score == null || Number.isNaN(Number(score))) return "rs-pitcher-risk-card--mid";
        const n = Number(score);
        // Hitter lens: higher dinger risk = greener = better HR target.
        if (n >= 66) return "rs-pitcher-risk-card--prime";
        if (n >= 33) return "rs-pitcher-risk-card--mid";
        return "rs-pitcher-risk-card--fade";
    }

    function escapeTip(text) {
        return String(text || "")
            .replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/</g, "&lt;");
    }

    function renderDingerRiskCardHtml(label, pct, sublabel, tipKey) {
        const tone = dingerRiskTone(pct);
        const tip = DINGER_RISK_TIPS[tipKey || label];
        const tipAttr = tip ? ` class="rs-pitcher-risk-card rs-has-tip ${tone}" data-tip="${escapeTip(tip)}" tabindex="0"` : ` class="rs-pitcher-risk-card ${tone}"`;
        return `<div${tipAttr}>
            <span class="rs-pitcher-risk-card__label">${label}</span>
            <span class="rs-pitcher-risk-card__score">${fmtDingerRiskValue(pct)}</span>
            ${sublabel ? `<span class="rs-pitcher-risk-card__sub">${sublabel}</span>` : ""}
        </div>`;
    }

    function renderDingerRiskRowHtml(stats) {
        const rank =
            stats.dingerRiskRank != null
                ? `#${stats.dingerRiskRank}${stats.dingerRiskSlateSize ? ` of ${stats.dingerRiskSlateSize}` : ""}`
                : "";
        return `<div class="rs-pitcher-risk-row">
            ${renderDingerRiskCardHtml("Overall", stats.dingerRiskPct ?? stats.dingerRisk, rank || "All batters", "Overall")}
            ${renderDingerRiskCardHtml("LHB", stats.dingerRiskLhbPct, "vs lefties", "LHB")}
            ${renderDingerRiskCardHtml("RHB", stats.dingerRiskRhbPct, "vs righties", "RHB")}
        </div>`;
    }

    function kScoreTone(score) {
        if (score == null || Number.isNaN(Number(score))) return "rs-pitcher-k-card--mid";
        const n = Number(score);
        if (n >= 66) return "rs-pitcher-k-card--prime";
        if (n >= 33) return "rs-pitcher-k-card--mid";
        return "rs-pitcher-k-card--fade";
    }

    function renderKScoreCardHtml(label, pct, sublabel, tipKey, opts = {}) {
        const tone = opts.neutral ? "rs-pitcher-k-card--mid" : kScoreTone(pct);
        const tip = K_SCORE_TIPS[tipKey || label];
        const tipAttr = tip
            ? ` class="rs-pitcher-k-card rs-has-tip ${tone}" data-tip="${escapeTip(tip)}" tabindex="0"`
            : ` class="rs-pitcher-k-card ${tone}"`;
        const score = opts.raw ? String(pct ?? "—") : fmtDingerRiskValue(pct);
        return `<div${tipAttr}>
            <span class="rs-pitcher-k-card__label">${label}</span>
            <span class="rs-pitcher-k-card__score">${score}</span>
            ${sublabel ? `<span class="rs-pitcher-k-card__sub">${sublabel}</span>` : ""}
        </div>`;
    }

    function renderKPickRowHtml(stats) {
        const rank =
            stats.kPickRank != null
                ? `#${stats.kPickRank}${stats.kPickSlateSize ? ` of ${stats.kPickSlateSize}` : ""}`
                : "";
        const matchupSub =
            stats.lineupAvgKPct != null ? `opp ${fmtPct(stats.lineupAvgKPct)} K` : "Lineup K";
        return `<div class="rs-pitcher-k-row">
            ${renderKScoreCardHtml("K pick", stats.kPickPct ?? stats.kPick, rank || "Today's slate", "Pick")}
            ${renderKScoreCardHtml("K stuff", stats.kStuffPct ?? stats.kStuff, "Whiff · K · Edge", "Overall")}
            ${renderKScoreCardHtml("Matchup", stats.kMatchPct, matchupSub, "Matchup")}
        </div>${renderKProjectionRowHtml(stats)}`;
    }

    function renderKProjectionRowHtml(stats) {
        const p = stats.kProj || {};
        const expK = stats.kProjExp ?? p.expK;
        if (expK == null) return "";
        const ceil = stats.kProjCeiling ?? p.ceilingK;
        const ip = stats.kProjIp ?? p.expIp;
        const k9 = stats.kProjK9 ?? p.effK9;
        const line = stats.kProjLine ?? p.suggestedLine;
        const lean = stats.kProjLean ?? p.lean;
        const lineLabel = line != null && lean ? `${line} ${lean}` : "—";
        return `<div class="rs-pitcher-k-row rs-pitcher-k-row--proj">
            ${renderKScoreCardHtml("Exp K", expK, ip != null ? `${ip} IP · ${k9 ?? "—"} K/9` : "Projected", "ExpK", { raw: true, neutral: true })}
            ${renderKScoreCardHtml("Ceiling", ceil, "Max reach today", "CeilingK", { raw: true, neutral: true })}
            ${renderKScoreCardHtml("Line", lineLabel, "Suggested prop lean", "Line", { raw: true, neutral: true })}
        </div>`;
    }

    function renderPitcherKGrid(stats, statsList) {
        const keys = ["whiffPct", "kPct", "edgePct", "zonePct"];
        const cells = keys
            .map((key) => {
                const metric = pitcherMetricByKey(key);
                if (!metric) return "";
                const kMetric = { ...metric, hrHigherIsGreen: key !== "zonePct" };
                return pitcherStatCellHtml(kMetric, stats, statsList);
            })
            .join("");
        const handBits = [];
        if (stats.kStuffLhbPct != null) handBits.push(`vs L: ${stats.kStuffLhbPct}%`);
        if (stats.kStuffRhbPct != null) handBits.push(`vs R: ${stats.kStuffRhbPct}%`);
        const handLine = handBits.length
            ? `<p class="rs-pitcher-k__hand">${handBits.join(" · ")}</p>`
            : "";
        return `<div class="rs-pitcher-k">
            <p class="rs-pitcher-k__lede">Read K props: <strong>Whiff%</strong> is swing-and-miss skill, <strong>K%</strong> is the outcome, <strong>Edge%</strong> shows command on the borders (chase + called strikes). Pair with the opposing lineup's K% in the score cards below.</p>
            ${handLine}
            <div class="rs-pitcher-group__grid">${cells}</div>
        </div>`;
    }

    function pitcherMetricByKey(key) {
        return PITCHER_METRICS.find((m) => m.key === key);
    }

    function renderPitcherHandSplitsTable(pitcher, stats) {
        const lhb = handSavantStatsForPitcher(pitcher, "lhb");
        const rhb = handSavantStatsForPitcher(pitcher, "rhb");
        if (!lhb && !rhb) {
            return `<p class="rs-pitcher-splits__empty">Hand splits unavailable — refresh slate or open via local server.</p>`;
        }
        const cell = (val, fmt) => (val != null && !Number.isNaN(Number(val)) ? fmt(val) : "—");
        const rows = [
            ["Dinger risk", stats.dingerRiskLhbPct != null ? `${stats.dingerRiskLhbPct}%` : "—", stats.dingerRiskRhbPct != null ? `${stats.dingerRiskRhbPct}%` : "—"],
            ["Barrel%", cell(lhb?.barrelPct, fmtPct), cell(rhb?.barrelPct, fmtPct)],
            ["Hard-hit%", cell(lhb?.hardHitPct, fmtPct), cell(rhb?.hardHitPct, fmtPct)],
            ["EV allowed", cell(lhb?.avgEV, fmtEv), cell(rhb?.avgEV, fmtEv)],
            ["HR/9", cell(lhb?.hr9, (v) => Number(v).toFixed(2)), cell(rhb?.hr9, (v) => Number(v).toFixed(2))],
            ["HR/FB%", cell(lhb?.hrFbPct, fmtPct), cell(rhb?.hrFbPct, fmtPct)],
        ];
        return `<table class="rs-pitcher-splits"><thead><tr><th></th><th>vs LHB</th><th>vs RHB</th></tr></thead><tbody>${rows
            .map(([label, l, r]) => `<tr><th>${label}</th><td>${l}</td><td>${r}</td></tr>`)
            .join("")}</tbody></table>`;
    }

    function renderPitcherArsenalHtml(pitcher) {
        const arsenal = pitcher?.arsenal;
        if (!arsenal || !Object.keys(arsenal).length) {
            return `<p class="rs-pitcher-arsenal__empty">Arsenal mix unavailable for this starter.</p>`;
        }
        const rows = Object.entries(arsenal)
            .sort((a, b) => Number(b[1]) - Number(a[1]))
            .slice(0, 6)
            .map(([pt, pct]) => {
                const n = Math.round(Number(pct));
                return `<div class="rs-pitcher-arsenal__row"><span class="rs-pitcher-arsenal__label">${pt}</span><div class="rs-pitcher-arsenal__bar"><span style="width:${Math.min(n, 100)}%"></span></div><span class="rs-pitcher-arsenal__pct">${n}%</span></div>`;
            })
            .join("");
        const top = Object.entries(arsenal).sort((a, b) => Number(b[1]) - Number(a[1]))[0];
        const note = top
            ? `Heaviest pitch: <strong>${top[0]}</strong> (${Math.round(Number(top[1]))}% usage) — match hitters with strong results vs this pitch type.`
            : "";
        return `<div class="rs-pitcher-arsenal">${rows}<p class="rs-pitcher-arsenal__note">${note}</p></div>`;
    }

    function renderPitcherOverviewGrid(stats, statsList) {
        const cells = PITCHER_OVERVIEW_KEYS.map((key) => {
            const metric = pitcherMetricByKey(key);
            if (!metric) return "";
            return pitcherStatCellHtml(metric, stats, statsList);
        }).join("");
        return `<div class="rs-pitcher-group__grid rs-pitcher-group__grid--overview">${cells}</div>`;
    }

    function renderPitcherLeakGrid(stats, statsList) {
        const metrics = PITCHER_METRICS.filter((m) => m.group === "leak");
        const cells = metrics.map((m) => pitcherStatCellHtml(m, stats, statsList)).join("");
        return `<div class="rs-pitcher-group__grid">${cells}</div>`;
    }

    function pitcherStatCellHtml(metric, stats, statsList) {
        const heat = pitcherMetricHeatClass(metric, statsList, stats);
        const tip = metric.tip ? ` data-tip="${escapeTip(metric.tip)}" tabindex="0"` : "";
        const tone = heat.includes("--good") ? " rs-pitcher-stat--good" : heat.includes("--bad") ? " rs-pitcher-stat--bad" : heat.includes("--mid") ? " rs-pitcher-stat--mid" : "";
        return `<div class="rs-pitcher-stat rs-has-tip${tone}"${tip}><dt>${metric.label}</dt><dd>${metric.fmt(stats)}</dd></div>`;
    }

    function renderPitcherKTabHtml(stats, statsList) {
        return `${renderKPickRowHtml(stats)}${renderPitcherKGrid(stats, statsList)}`;
    }

    function renderPitcherCardHtml(pitcher, team, sideLabel, stats, statsList, gameIdx, side) {
        if (!pitcher?.name) return "";
        const hand = fmtPitcherHand(pitcher, team);
        const pid = pitcher.id || "";
        const overview = renderPitcherOverviewGrid(stats, statsList);
        const splits = renderPitcherHandSplitsTable(pitcher, stats);
        const leak = renderPitcherLeakGrid(stats, statsList);
        const kstrikeout = renderPitcherKTabHtml(stats, statsList);
        const arsenal = pitcher.arsenalLabel ? `<div class="rs-pitcher-card__mix">${pitcher.arsenalLabel}</div>` : "";
        return `<article class="rs-pitcher-card rs-pitcher-card--${sideLabel.toLowerCase()} rs-pitcher-card--clickable" data-pitcher-id="${pid}" data-game="${gameIdx}" data-side="${side}" role="button" tabindex="0" title="Open pitcher profile">
            <header class="rs-pitcher-card__head">
                <div class="rs-pitcher-card__top">
                    <span class="rs-pitcher-card__team">${sideLabel} · ${team}</span>
                    <span class="rs-pitcher-card__hand">${hand}</span>
                </div>
                <h3 class="rs-pitcher-card__name">${escAttr(pitcher.name || "—")}</h3>
                ${arsenal}
                ${renderDingerRiskRowHtml(stats)}
            </header>
            <nav class="rs-pitcher-card__tabs" aria-label="Pitcher card views">
                <button type="button" class="rs-pitcher-card__tab is-active" data-tab="overview">Overview</button>
                <button type="button" class="rs-pitcher-card__tab" data-tab="splits">Splits</button>
                <button type="button" class="rs-pitcher-card__tab" data-tab="leak"><span class="rs-tab-long">Contact leak</span><span class="rs-tab-short">Leak</span></button>
                <button type="button" class="rs-pitcher-card__tab" data-tab="kstrikeout"><span class="rs-tab-long">K / Strikeout</span><span class="rs-tab-short">K</span></button>
            </nav>
            <div class="rs-pitcher-card__body">
                <div class="rs-pitcher-card__pane" data-pane="overview">${overview}</div>
                <div class="rs-pitcher-card__pane" data-pane="splits" hidden>${splits}</div>
                <div class="rs-pitcher-card__pane" data-pane="leak" hidden>${leak}</div>
                <div class="rs-pitcher-card__pane" data-pane="kstrikeout" hidden>${kstrikeout}</div>
            </div>
        </article>`;
    }

    function wirePitcherCardTabs(card) {
        const tabs = card.querySelectorAll(".rs-pitcher-card__tab");
        const panes = card.querySelectorAll(".rs-pitcher-card__pane");
        tabs.forEach((btn) => {
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                const tab = btn.getAttribute("data-tab");
                tabs.forEach((t) => t.classList.toggle("is-active", t === btn));
                panes.forEach((p) => {
                    p.hidden = p.getAttribute("data-pane") !== tab;
                });
            });
        });
    }

    function wirePitcherCards() {
        els.pitcherCards?.querySelectorAll(".rs-pitcher-card--clickable").forEach((card) => {
            wirePitcherCardTabs(card);
            const open = () => {
                const id = Number(card.getAttribute("data-pitcher-id"));
                const gi = Number(card.getAttribute("data-game"));
                const side = card.getAttribute("data-side");
                const entry = collectSlatePitchers().find((e) => e.pitcher?.id === id && e.gameIdx === gi && e.side === side);
                if (entry) openPitcherProfile(entry);
            };
            card.addEventListener("click", open);
            card.addEventListener("keydown", (ev) => {
                if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    open();
                }
            });
        });
    }

    function collectSlatePitcherStatsList() {
        return collectSlatePitcherEntries().map((entry) => pitcherStats(entry.pitcher));
    }

    function statWindowLeadText() {
        const w = slate?.stat_windows || {};
        const hitter = w.hitters?.label || (w.hitters?.games ? `Last ${w.hitters.games} games` : null);
        const pitcher = w.pitchers?.label || (w.pitchers?.starts ? `Last ${w.pitchers.starts} starts` : null);
        if (hitter && pitcher) return `Hitter stats: ${hitter} · Pitcher stats: ${pitcher}`;
        if (hitter) return `Hitter stats: ${hitter}`;
        if (pitcher) return `Pitcher stats: ${pitcher}`;
        return null;
    }

    async function renderPitcherPanel() {
        if (!els.pitcherPanel) return;
        const game = activeGame();
        if (!game) {
            els.pitcherPanel.hidden = true;
            return;
        }
        const date = slate?.sheet_date || els.dateInput?.value || sheetDateFromQuery();
        await ensurePitcherHandLookup(seasonFromDate(date));
        computePitcherScoresForSlate();
        const away = game.awayPitcher;
        const home = game.homePitcher;
        if (!away?.name && !home?.name) {
            els.pitcherPanel.hidden = true;
            return;
        }
        els.pitcherPanel.hidden = false;
        const awayStats = pitcherStats(away);
        const homeStats = pitcherStats(home);
        const statsList = collectSlatePitcherStatsList();
        if (els.pitcherLead) {
            const windowLead = statWindowLeadText();
            els.pitcherLead.textContent = windowLead
                ? `Probable starters · ${windowLead}`
                : "Probable starters · Savant rolling window";
        }
        if (els.pitcherCards) {
            const gi = activeGameIdx;
            els.pitcherCards.innerHTML = [
                renderPitcherCardHtml(away, game.away, "AWY", awayStats, statsList, gi, "away"),
                renderPitcherCardHtml(home, game.home, "HOM", homeStats, statsList, gi, "home"),
            ].join("");
            wirePitcherCards();
        }
    }

    async function mergePitcherSavantIntoGames(season) {
        await ensurePitcherHandLookup(season);
        if (slate?.savant_pitcher_lookup && Object.keys(slate.savant_pitcher_lookup).length) {
            for (const game of slate.games || []) {
                for (const key of ["awayPitcher", "homePitcher"]) {
                    const pitcher = game[key];
                    if (!pitcher?.id) continue;
                    const sav = slate.savant_pitcher_lookup[pitcher.id] || slate.savant_pitcher_lookup[String(pitcher.id)];
                    if (!sav) continue;
                    const stats = { ...(pitcher.stats || {}) };
                    for (const [statKey, val] of Object.entries(sav)) {
                        if (val != null && stats[statKey] == null) stats[statKey] = val;
                    }
                    pitcher.stats = stats;
                }
            }
            computePitcherScoresForSlate();
            return { n: Object.keys(slate.savant_pitcher_lookup).length, source: "embedded" };
        }
        const cached = await fetchDataJson(`savant-pitcher-${season}.json`);
        const lookup = cached.data?.lookup || {};
        if (!Object.keys(lookup).length) {
            computePitcherScoresForSlate();
            return { n: 0, source: null, lastStatus: cached.lastStatus };
        }
        for (const game of slate.games || []) {
            for (const key of ["awayPitcher", "homePitcher"]) {
                const pitcher = game[key];
                if (!pitcher?.id) continue;
                const sav = lookup[pitcher.id] || lookup[String(pitcher.id)];
                if (!sav) continue;
                const stats = { ...(pitcher.stats || {}) };
                for (const [statKey, val] of Object.entries(sav)) {
                    if (val != null && stats[statKey] == null) stats[statKey] = val;
                }
                pitcher.stats = stats;
            }
        }
        computePitcherScoresForSlate();
        return { n: Object.keys(lookup).length, source: cached.url || "cache" };
    }

    const HR_REF_ALLEY_FT = 377;
    const HR_CARRY_PCT_PER_3FT = 0.11;
    const HR_WEATHER_DA_BLEND = 0.75;
    const HR_WEATHER_CARRY_BLEND = 0.25;
    const HR_CARRY_CHANNEL_SCALE = 0.45;
    const HR_WIND_SOFT_CAP_MPH = 12;
    const HR_WIND_SOFT_TAIL = 0.45;
    const HR_ENV_WEIGHTS = {
        stadium: 0.3,
        weather: 0.15,
        wind: 0.25,
        dim: 0.15,
        pitcher: 0.15,
    };
    const HR_ENV_FACTOR_CAP = 12;
    const HR_ENV_TOTAL_CAP = 18;

    function clampHrEnvMult(mult, lo = 0.88, hi = 1.12) {
        if (mult == null || Number.isNaN(Number(mult))) return 1;
        return Math.max(lo, Math.min(hi, Number(mult)));
    }

    function hrEnvFactorPct(mult) {
        if (mult == null || Number.isNaN(Number(mult))) return 0;
        const pct = (Number(mult) - 1) * 100;
        return Math.max(-HR_ENV_FACTOR_CAP, Math.min(HR_ENV_FACTOR_CAP, pct));
    }

    function combineHrEnvPct(factors) {
        let total = 0;
        for (const [key, mult] of Object.entries(factors)) {
            const weight = HR_ENV_WEIGHTS[key] ?? 0;
            total += hrEnvFactorPct(mult) * weight;
        }
        return clampDisplayPct(total, -HR_ENV_TOTAL_CAP, HR_ENV_TOTAL_CAP) ?? 0;
    }

    function hrCarryFeetToPct(carryFt) {
        return (carryFt / 3) * HR_CARRY_PCT_PER_3FT;
    }

    function hrDaCompoundMult(daDelta) {
        if (daDelta == null) return 1;
        const pct = clampDisplayPct(daDelta / 250, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP);
        return 1 + (pct ?? 0) / 100;
    }

    function hrWindCompoundMult(windOutMph) {
        if (windOutMph == null || Number.isNaN(Number(windOutMph))) return 1;
        const mph = Number(windOutMph);
        const sign = mph >= 0 ? 1 : -1;
        const absMph = Math.abs(mph);
        const effective =
            absMph <= HR_WIND_SOFT_CAP_MPH
                ? absMph
                : HR_WIND_SOFT_CAP_MPH + (absMph - HR_WIND_SOFT_CAP_MPH) * HR_WIND_SOFT_TAIL;
        const pct = clampDisplayPct(sign * effective, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP);
        return 1 + (pct ?? 0) / 100;
    }

    function hrWeatherCompoundMult(daDelta, carryBoostFt) {
        const daMult = hrDaCompoundMult(daDelta);
        const daPct = (daMult - 1) * 100;
        const boost = Number(carryBoostFt) || 0;
        const carryRaw = boost ? hrCarryFeetToPct(boost) * HR_CARRY_CHANNEL_SCALE : 0;
        const carryPct = clampDisplayPct(carryRaw, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP) ?? 0;
        const blended = daPct * HR_WEATHER_DA_BLEND + carryPct * HR_WEATHER_CARRY_BLEND;
        const clamped = clampDisplayPct(blended, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP) ?? 0;
        return 1 + clamped / 100;
    }

    function hrWallDistMult(wallFt) {
        const pct = displayFencePct(wallFt, HR_REF_ALLEY_FT);
        if (pct == null) return 1;
        return 1 + pct / 100;
    }

    function hrWallHeightMult(heightFt) {
        if (heightFt == null) return 1;
        let pct = 0;
        if (heightFt >= 20) pct = -3;
        else if (heightFt >= 10) pct = -1;
        else if (heightFt <= 5) pct = 2;
        return 1 + pct / 100;
    }

    function effectiveBatterHand(batterHand, pitcherThrows) {
        const hand = String(batterHand || "R").trim().toUpperCase();
        if (hand === "L" || hand === "R") return hand;
        const throws = String(pitcherThrows || "R").trim().toUpperCase();
        return throws === "L" ? "R" : "L";
    }

    function pullAlley(stadium, hand) {
        const walls = stadium?.walls || {};
        const heights = stadium?.heights || {};
        const cfBearing = stadium?.bearing;
        if (hand === "L") {
            const override = stadium?.pullL || {};
            const dist = override.dist ?? walls.rcf;
            let bearing = override.bearing;
            if (bearing == null && cfBearing != null) bearing = (cfBearing + 22) % 360;
            return { dist, bearing, height: heights.rf ?? heights.cf };
        }
        const override = stadium?.pullR || {};
        const dist = override.dist ?? walls.lcf;
        let bearing = override.bearing;
        if (bearing == null && cfBearing != null) bearing = (cfBearing - 22 + 360) % 360;
        return { dist, bearing, height: heights.lf ?? heights.cf };
    }

    function computeGameHrModel(game) {
        const stadium = lookupStadium(game?.venue || "");
        const wx = game?.parkWeather || {};
        if (!stadium) return game?.hrModel || null;
        const baseline = wx.baselineDaFt ?? baselineDaFt();
        const da = wx.densityAltFt;
        const daDelta = da == null ? null : da - baseline;
        const daMult = hrDaCompoundMult(daDelta);
        const carryBoost = Number(wx.distanceBoostFt) || 0;
        const carryPct = carryBoost
            ? clampDisplayPct(hrCarryFeetToPct(carryBoost) * HR_CARRY_CHANNEL_SCALE, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP)
            : null;
        const carryMult = 1 + (carryPct ?? 0) / 100;
        const weatherMult = clampHrEnvMult(hrWeatherCompoundMult(daDelta, carryBoost));
        const windFrom = wx.windDirDeg;
        const windMph = wx.windMph;
        let windOutL = null;
        let windOutR = null;
        if (windFrom != null && windMph != null) {
            windOutL = windComponentTowardCf(windFrom, windMph, pullAlley(stadium, "L").bearing);
            windOutR = windComponentTowardCf(windFrom, windMph, pullAlley(stadium, "R").bearing);
        } else {
            windOutR = wx.windComponentMph;
        }
        const pullL = pullAlley(stadium, "L");
        const pullR = pullAlley(stadium, "R");
        const walls = stadium.walls || {};
        return {
            daDeltaFt: daDelta,
            daMult: Math.round(daMult * 1000) / 1000,
            carryMult: Math.round(carryMult * 1000) / 1000,
            weatherMult: Math.round(weatherMult * 1000) / 1000,
            windOutLhbMph: windOutL,
            windOutRhbMph: windOutR,
            windMultLhb: Math.round(hrWindCompoundMult(windOutL) * 1000) / 1000,
            windMultRhb: Math.round(hrWindCompoundMult(windOutR ?? wx.windComponentMph) * 1000) / 1000,
            dimMultLhb: Math.round(hrWallDistMult(pullL.dist) * hrWallHeightMult(pullL.height) * 1000) / 1000,
            dimMultRhb: Math.round(hrWallDistMult(pullR.dist) * hrWallHeightMult(pullR.height) * 1000) / 1000,
            wallLfFt: walls.lf,
            wallCfFt: walls.cf,
            wallRfFt: walls.rf,
        };
    }

    function pitcherHrMult(pitcher, batterHand) {
        const stats = pitcher?.stats || {};
        const hand = effectiveBatterHand(batterHand, pitcher?.throws);
        const dingerPct =
            hand === "L"
                ? stats.dingerRiskLhbPct ?? stats.dingerRiskPct ?? stats.dingerRisk
                : stats.dingerRiskRhbPct ?? stats.dingerRiskPct ?? stats.dingerRisk;
        if (dingerPct != null && !Number.isNaN(Number(dingerPct))) {
            const dev = (Number(dingerPct) - 50) / 400;
            return clampHrEnvMult(1 + dev);
        }
        let score = hand === "L" ? stats.vsLhb : stats.vsRhb;
        if (score == null) score = stats.hrRisk;
        if (score == null) return 1;
        return clampHrEnvMult(1 + Number(score) * 0.12);
    }

    function computeHitterHrProp(row, game, pitcher) {
        const stadium = lookupStadium(game?.venue || "");
        if (!stadium) return row?.hrProp || null;
        const hand = effectiveBatterHand(row?.hand, pitcher?.throws);
        const hrModel = game.hrModel || computeGameHrModel(game);
        const decomposed = hasDecomposedPark(game);
        const parkPct = parkStadiumPctForHitter(game, hand);
        const stadiumMult =
            parkPct == null ? 1 : clampHrEnvMult(1 + (Number(parkPct) / 100) * 0.45);
        const windMult = clampHrEnvMult(hand === "L" ? hrModel?.windMultLhb ?? 1 : hrModel?.windMultRhb ?? 1);
        const dimRaw = hand === "L" ? hrModel?.dimMultLhb ?? 1 : hrModel?.dimMultRhb ?? 1;
        const dimMult = clampHrEnvMult(dimMultScaled(dimRaw, decomposed));
        const weatherMult = clampHrEnvMult(hrModel?.weatherMult ?? 1);
        const pitcherMult = pitcherHrMult(pitcher, hand);
        const propPass = !!(game.propPass || game.parkWeather?.propPass);
        if (propPass) {
            return {
                hand,
                combinedMult: null,
                combinedPct: null,
                propPass: true,
                stadiumMult: null,
                weatherMult: null,
                windMult: null,
                dimMult: null,
                pitcherMult: null,
                parkPct: parkHrPctForHitter(game, hand),
                windOutMph: null,
                pullWallFt: pullAlley(stadium, hand).dist,
                pullBearing: pullAlley(stadium, hand).bearing,
            };
        }
        const combinedPct = combineHrEnvPct({
            stadium: stadiumMult,
            weather: weatherMult,
            wind: windMult,
            dim: dimMult,
            pitcher: pitcherMult,
        });
        const combined = Math.round((1 + combinedPct / 100) * 1000) / 1000;
        const pull = pullAlley(stadium, hand);
        return {
            hand,
            combinedMult: combined,
            combinedPct,
            stadiumMult: Math.round(stadiumMult * 1000) / 1000,
            weatherMult: Math.round(weatherMult * 1000) / 1000,
            windMult: Math.round(windMult * 1000) / 1000,
            dimMult: Math.round(dimMult * 1000) / 1000,
            pitcherMult: Math.round(pitcherMult * 1000) / 1000,
            parkPct,
            windOutMph: hand === "L" ? hrModel?.windOutLhbMph : hrModel?.windOutRhbMph,
            pullWallFt: pull.dist,
            pullBearing: pull.bearing,
        };
    }

    function refreshGameHrProps(game) {
        if (!game) return;
        game.hrModel = game.hrModel || computeGameHrModel(game);
        const awayP = game.homePitcher;
        const homeP = game.awayPitcher;
        for (const row of game.awayLineup || []) row.hrProp = computeHitterHrProp(row, game, awayP);
        for (const row of game.homeLineup || []) row.hrProp = computeHitterHrProp(row, game, homeP);
    }

    function refreshAllHrProps() {
        clearHrTicketCache();
        for (const game of slate?.games || []) refreshGameHrProps(game);
    }

    function carryTone(score) {
        if (score == null || Number.isNaN(Number(score))) return "mid";
        if (score >= 2) return "good";
        if (score <= -2) return "bad";
        return "mid";
    }

    function multToPct(mult) {
        if (mult == null || Number.isNaN(Number(mult))) return null;
        return Math.round((Number(mult) - 1) * 1000) / 10;
    }

    function fmtSignedPct(pct) {
        if (pct == null || Number.isNaN(Number(pct))) return "—";
        const n = Math.round(Number(pct));
        const sign = n > 0 ? "+" : "";
        return `${sign}${n}%`;
    }

    function edgeTone(pct) {
        if (pct == null || Number.isNaN(Number(pct))) return "mid";
        if (pct >= 4) return "good";
        if (pct <= -4) return "bad";
        return "mid";
    }

    function computeHrCarryPct(wx) {
        return displayHrCarryPct(wx);
    }

    function computeWindOutPct(windComponentMph) {
        return displayWindPct(windComponentMph);
    }

    function computeEnvHrPct(wx, game) {
        const hm = game?.hrModel || (game ? computeGameHrModel(game) : null);
        if (hm?.weatherMult != null) {
            const airPct = multToPct(hm.weatherMult) ?? 0;
            const windPct = displayWindPct(wx?.windComponentMph) ?? 0;
            return Math.round(airPct * 0.6 + windPct * 0.4);
        }
        const carry = displayHrCarryPct(wx) ?? 0;
        const wind = displayWindPct(wx?.windComponentMph) ?? 0;
        return Math.round(carry * 0.6 + wind * 0.4);
    }

    const WX_TIPS = {
        hrCarry:
            "Thin air vs a typical 75°F game — not perfect sea-level air. Hot, dry, low-pressure days push positive; cold, humid, high-pressure days go negative.",
        windOut:
            "Wind blowing toward center field. Tailwind (+) pushes deep flies over the fence; headwind (−) turns would-be HRs into outs. Look for 10+ mph tailwind before hammering HR Overs.",
        windPullL:
            "Wind along the left-handed pull side (toward right field). LHB power hitters benefit most when this is positive. Same park can help LHB and hurt RHB depending on wind angle.",
        windPullR:
            "Wind along the right-handed pull side (toward left field). RHB sluggers get the boost here. Check this before betting RH batter HR props at parks like Yankee Stadium or Oracle Park.",
        parkFactor:
            "Ballpark Pal stadium structure (fence shape, dimensions). When decomposed, live Open-Meteo air + wind are applied separately — not double-counted.",
        fenceBoost:
            "Pull-side wall vs league-average distance (377 ft). Short porch = positive; deep alley = negative. Park shape only — not today's wind or air.",
        conditions:
            "Forecast at first-pitch hour. Hot and humid = slightly thinner air. Rain or a last-minute roof closure can flip your edge — recheck 60–90 minutes before first pitch.",
        humidity:
            "Relative humidity at game time. Shown with carry impact vs a 55% baseline — sticky air hurts carry, drier air helps a touch.",
        pressure:
            "Barometric pressure with carry impact vs ~1013 hPa. Lower pressure = thinner air (+); high pressure = denser air (−).",
        roof:
            "Dome or closed roof = no outdoor wind and controlled climate. If roof status is unknown on a retractable park, we flag PASS — skip HR props until confirmed open.",
        pass:
            "Roof or wind data is unreliable for this game. Books still post HR lines, but the edge is unknown. Wait for confirmation or pass on HR props here.",
    };

    function wxCell(label, value, tip, opts = {}) {
        const { tone, sub, hero, wide, pass } = opts;
        const mods = ["rs-weather__cell"];
        if (tone) mods.push(`rs-weather__cell--${tone}`);
        if (hero) mods.push("rs-weather__cell--hero");
        if (wide) mods.push("rs-weather__cell--wide");
        if (pass) mods.push("rs-weather__cell--pass");
        const tipAttr = tip ? ` data-tip="${escAttr(tip)}" tabindex="0"` : "";
        const tipCls = tip ? " rs-has-tip" : "";
        const subHtml = sub ? `<span class="rs-weather__sub">${sub}</span>` : "";
        return `<div class="${mods.join(" ")}${tipCls}"${tipAttr}><dt>${label}</dt><dd>${value}${subHtml}</dd></div>`;
    }

    function fmtWindPullSub(mph) {
        if (mph == null || Number.isNaN(Number(mph))) return "";
        const n = Math.round(Number(mph) * 10) / 10;
        if (Math.abs(n) < 1) return "Crosswind / calm";
        if (n > 0) return `${n} mph out to pull side`;
        return `${Math.abs(n)} mph in from pull side`;
    }

    function fmtRoofLabel(game, wx) {
        const rs = game?.roofStatus || wx?.roofStatus || {};
        const state = String(rs.state || wx?.roof || "unknown").toLowerCase();
        if (state === "dome") return "Dome — no outdoor wind";
        if (state === "closed") return "Roof closed";
        if (state === "open") return "Roof open";
        if (state === "unknown") return "Roof unknown";
        return state.charAt(0).toUpperCase() + state.slice(1);
    }

    async function fetchOpenMeteoWeather(game) {
        const venue = game?.venue || "";
        const startTime = game?.startTime || "";
        const stadium = lookupStadium(venue);
        if (!stadium || !startTime) return { error: "missing_coords", venue };

        const roofType = normalizeRoof(stadium.roof);
        if (roofType === "dome") {
            return buildWeatherMetrics({
                tempF: null,
                humidityPct: null,
                pressureHpa: null,
                windMph: null,
                windFromDeg: null,
                stadium,
                roof: roofType,
                venue,
            });
        }

        const start = new Date(startTime);
        if (Number.isNaN(start.getTime())) return { error: "bad_start", venue };

        const tz = stadium.tz || "America/New_York";
        const localParts = new Intl.DateTimeFormat("en-CA", {
            timeZone: tz,
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            hour12: false,
        }).formatToParts(start);
        const part = (t) => localParts.find((p) => p.type === t)?.value || "";
        const targetDate = `${part("year")}-${part("month")}-${part("day")}`;
        const targetHour = parseInt(part("hour"), 10);

        const params = new URLSearchParams({
            latitude: String(stadium.lat),
            longitude: String(stadium.lon),
            hourly: "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,precipitation_probability",
            timezone: tz,
            temperature_unit: "fahrenheit",
            wind_speed_unit: "mph",
            forecast_days: "3",
        });
        const res = await fetch(`https://api.open-meteo.com/v1/forecast?${params.toString()}`);
        if (!res.ok) throw new Error(`Open-Meteo ${res.status}`);
        const data = await res.json();
        const hourly = data.hourly || {};
        const times = hourly.time || [];
        let idx = times.findIndex((t) => t.startsWith(targetDate) && parseInt(t.slice(11, 13), 10) === targetHour);
        if (idx < 0) {
            let best = -1;
            let bestDiff = 999;
            times.forEach((t, i) => {
                if (!t.startsWith(targetDate)) return;
                const diff = Math.abs(parseInt(t.slice(11, 13), 10) - targetHour);
                if (diff < bestDiff) {
                    bestDiff = diff;
                    best = i;
                }
            });
            idx = best;
        }
        if (idx < 0) return { error: "no_hour", venue };

        return buildWeatherMetrics({
            tempF: hourly.temperature_2m?.[idx],
            humidityPct: hourly.relative_humidity_2m?.[idx],
            pressureHpa: hourly.surface_pressure?.[idx],
            windMph: hourly.wind_speed_10m?.[idx],
            windFromDeg: hourly.wind_direction_10m?.[idx],
            precipPct: hourly.precipitation_probability?.[idx],
            stadium,
            gameHourLocal: times[idx],
            venue,
        });
    }

    function weatherIsComplete(wx) {
        if (!wx || wx.error) return false;
        if (wx.source === "dome-neutral" || wx.roof === "dome") return true;
        return wx.source != null && wx.densityAltFt != null;
    }

    async function ensureGameWeather(game) {
        if (!game || game._weatherLoading) return game?.parkWeather || null;
        if (weatherIsComplete(game.parkWeather)) {
            if (!game.roofStatus) await applyRoofStatusToGame(game);
            return game.parkWeather;
        }
        game._weatherLoading = true;
        try {
            await loadStadiumCoords();
            const wx = await fetchOpenMeteoWeather(game);
            game.parkWeather = wx;
            game._weatherFetched = true;
            await applyRoofStatusToGame(game);
            refreshGameHrProps(game);
            return wx;
        } catch (err) {
            game.parkWeather = { error: String(err.message || err), venue: game.venue };
            game._weatherFetched = true;
            return null;
        } finally {
            game._weatherLoading = false;
        }
    }

    async function prefetchSlateWeather() {
        if (!slate?.games?.length) return;
        await loadStadiumCoords();
        await Promise.all(
            slate.games.map(async (game) => {
                if (weatherIsComplete(game.parkWeather)) {
                    if (!game.roofStatus) await applyRoofStatusToGame(game);
                    return;
                }
                await ensureGameWeather(game);
            })
        );
        renderGames();
        renderWeatherPanel();
        refreshHrEnvUi();
    }

    function rsReason(game) {
        return game?.roofStatus?.reason || game?.parkWeather?.roofStatus?.reason || "";
    }

    function weatherBadgeHtml(game) {
        if (game?.propPass) {
            return `<span class="rs-game-pill__wx rs-game-pill__wx--pass" data-tip="PASS — roof or wind unknown, skip HR props">PASS</span>`;
        }
        const wx = game?.parkWeather || {};
        const hm = game?.hrModel || computeGameHrModel(game);
        const pct = computeEnvHrPct(wx, game);
        if (pct == null || Number.isNaN(Number(pct))) return "";
        const tone = edgeTone(pct);
        const tip = `Today's air + CF wind HR boost vs average: ${fmtSignedPct(pct)}`;
        return `<span class="rs-game-pill__wx rs-game-pill__wx--${tone} rs-has-tip" data-tip="${escAttr(tip)}">${fmtSignedPct(pct)}</span>`;
    }

    const PARK_WALL_ANGLES = { lf: -45, lcf: -22, cf: 0, rcf: 22, rf: 45 };
    const DEFAULT_PARK_WALLS = { lf: 330, lcf: 375, cf: 400, rcf: 375, rf: 330 };

    function buildParkGeometry(stadium) {
        const walls = { ...DEFAULT_PARK_WALLS, ...(stadium?.walls || {}) };
        const cx = 84;
        const cy = 152;
        const maxDist = Math.max(walls.lf, walls.lcf, walls.cf, walls.rcf, walls.rf);
        const scale = 96 / maxDist;
        const keys = ["lf", "lcf", "cf", "rcf", "rf"];
        const pts = keys.map((key) => {
            const dist = walls[key];
            const deg = PARK_WALL_ANGLES[key];
            const rad = (deg * Math.PI) / 180;
            return {
                key,
                dist,
                x: cx + Math.sin(rad) * dist * scale,
                y: cy - Math.cos(rad) * dist * scale,
            };
        });
        const fmt = (n) => n.toFixed(1);
        const fillPath = `M ${fmt(cx)} ${fmt(cy)} ${pts.map((p) => `L ${fmt(p.x)} ${fmt(p.y)}`).join(" ")} Z`;
        const fencePath = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${fmt(p.x)} ${fmt(p.y)}`).join(" ");
        const foulPath = `M ${fmt(cx)} ${fmt(cy)} L ${fmt(pts[0].x)} ${fmt(pts[0].y)} M ${fmt(cx)} ${fmt(cy)} L ${fmt(pts[4].x)} ${fmt(pts[4].y)}`;
        const d = 13;
        const infieldPath = `M ${fmt(cx)} ${fmt(cy)} L ${fmt(cx + d)} ${fmt(cy - d * 0.72)} L ${fmt(cx)} ${fmt(cy - d * 1.28)} L ${fmt(cx - d)} ${fmt(cy - d * 0.72)} Z`;
        const labels = pts.map((p) => {
            const deg = PARK_WALL_ANGLES[p.key];
            const rad = (deg * Math.PI) / 180;
            return {
                x: p.x + Math.sin(rad) * 9,
                y: p.y - Math.cos(rad) * 9,
                text: String(Math.round(p.dist)),
            };
        });
        const hubX = cx;
        const hubY = cy - walls.cf * scale * 0.52;
        return { fillPath, fencePath, foulPath, infieldPath, labels, hubX, hubY, cx, cy };
    }

    function renderParkOutline(stadium) {
        const geo = buildParkGeometry(stadium);
        if (els.parkOutline) {
            const labelHtml = geo.labels
                .map(
                    (l) =>
                        `<text class="rs-wind-field__dim" x="${l.x.toFixed(1)}" y="${l.y.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${l.text}</text>`
                )
                .join("");
            els.parkOutline.innerHTML = `
                <path class="rs-wind-field__fill" d="${geo.fillPath}" />
                <path class="rs-wind-field__fence" d="${geo.fencePath}" />
                <path class="rs-wind-field__foul" d="${geo.foulPath}" />
                <path class="rs-wind-field__infield" d="${geo.infieldPath}" />
                ${labelHtml}
            `;
        }
        return geo;
    }

    function setWindArrowHub(geo) {
        if (!els.windArrow || !geo) return;
        const line = els.windArrow.querySelector(".rs-wind-field__arrow-line");
        const tip = els.windArrow.querySelector(".rs-wind-field__arrow-tip");
        const len = 10;
        const tipY = geo.hubY - len;
        const headY = tipY - 2;
        const baseY = tipY + 3;
        if (line) {
            line.setAttribute("x1", geo.hubX.toFixed(1));
            line.setAttribute("y1", geo.hubY.toFixed(1));
            line.setAttribute("x2", geo.hubX.toFixed(1));
            line.setAttribute("y2", tipY.toFixed(1));
        }
        if (tip) {
            tip.setAttribute(
                "points",
                `${geo.hubX.toFixed(1)},${headY.toFixed(1)} ${(geo.hubX - 2.5).toFixed(1)},${baseY.toFixed(1)} ${(geo.hubX + 2.5).toFixed(1)},${baseY.toFixed(1)}`
            );
        }
    }

    function windFieldInfoHtml(wx, component, roofClosed) {
        if (roofClosed) {
            return `<div class="rs-wind-field__row"><span>Wind</span><span>Roof closed</span></div>`;
        }
        const rows = [];
        if (wx.windMph != null) {
            const dir = wx.windDir ? ` ${wx.windDir}` : "";
            rows.push(`<div class="rs-wind-field__row"><span>Wind</span><span>${Math.round(Number(wx.windMph))} mph${dir}</span></div>`);
        }
        if (component != null && !Number.isNaN(Number(component))) {
            let effect = "Crosswind";
            if (component >= 5) effect = "Blowing out to CF";
            else if (component <= -5) effect = "Blowing in from CF";
            else if (component > 1) effect = "Slight tailwind out";
            else if (component < -1) effect = "Slight headwind in";
            const comp =
                component > 0 ? `+${component} mph out` : component < 0 ? `${component} mph out` : "minimal impact";
            rows.push(`<div class="rs-wind-field__row"><span>Ball carry</span><span>${effect} · ${comp}</span></div>`);
        }
        if (wx.tempF != null) {
            rows.push(`<div class="rs-wind-field__row"><span>Temp</span><span>${Math.round(wx.tempF)}°F</span></div>`);
        }
        if (wx.humidityPct != null) {
            rows.push(`<div class="rs-wind-field__row"><span>Humidity</span><span>${Math.round(wx.humidityPct)}%</span></div>`);
        }
        if (wx.pressureHpa != null) {
            rows.push(`<div class="rs-wind-field__row"><span>Air pressure</span><span>${wx.pressureHpa} hPa</span></div>`);
        }
        if (!rows.length) return `<div class="rs-wind-field__row"><span>Wind</span><span>—</span></div>`;
        return rows.join("");
    }

    function windFieldRotation(windFrom, bearing) {
        const windToDeg = (Number(windFrom) + 180) % 360;
        const relativeAngle = (windToDeg - Number(bearing) + 360) % 360;
        return relativeAngle - 90;
    }

    function setWindFieldTone(tone) {
        if (!els.windField) return;
        els.windField.classList.remove("rs-wind-field--good", "rs-wind-field--bad", "rs-wind-field--mid", "rs-wind-field--idle");
        if (tone) els.windField.classList.add(`rs-wind-field--${tone}`);
    }

    function renderWindFieldVisual(game) {
        if (!els.windField) return;
        const wx = game?.parkWeather || {};
        const stadium = lookupStadium(game?.venue || "");
        const geo = renderParkOutline(stadium);
        setWindArrowHub(geo);

        const roofClosed =
            wx.roof === "dome" ||
            wx.roof === "closed" ||
            game?.roofStatus?.effective === "closed" ||
            game?.roofStatus?.state === "dome";

        els.windField.hidden = false;

        if (game?._weatherLoading) {
            setWindFieldTone("idle");
            if (els.windInfo) els.windInfo.innerHTML = `<div class="rs-wind-field__row"><span>Wind</span><span>Loading…</span></div>`;
            if (els.windArrow) els.windArrow.setAttribute("opacity", "0");
            return;
        }

        if (roofClosed) {
            setWindFieldTone("mid");
            if (els.windInfo) els.windInfo.innerHTML = windFieldInfoHtml(wx, 0, true);
            if (els.windArrow) els.windArrow.setAttribute("opacity", "0");
            return;
        }

        const bearing = wx.cfBearing ?? stadium?.bearing ?? 0;
        const windFrom = wx.windDirDeg;
        const windMph = wx.windMph ?? 0;

        if (windFrom == null || windMph == null) {
            setWindFieldTone("idle");
            if (els.windInfo) {
                els.windInfo.innerHTML = `<div class="rs-wind-field__row"><span>Wind</span><span>${wx.error ? "Unavailable" : "Pending"}</span></div>`;
            }
            if (els.windArrow) els.windArrow.setAttribute("opacity", "0");
            return;
        }

        const component =
            wx.windComponentMph != null ? wx.windComponentMph : windComponentTowardCf(windFrom, windMph, bearing);
        const tone = component >= 5 ? "good" : component <= -5 ? "bad" : "mid";
        const rot = windFieldRotation(windFrom, bearing);
        const transform = `rotate(${rot} ${geo.hubX.toFixed(1)} ${geo.hubY.toFixed(1)})`;

        setWindFieldTone(tone);
        if (els.windArrow) {
            els.windArrow.setAttribute("transform", transform);
            els.windArrow.setAttribute("opacity", windMph < 2 ? "0.35" : "1");
        }
        if (els.windInfo) els.windInfo.innerHTML = windFieldInfoHtml(wx, component, false);
    }

    function renderWeatherPanel() {
        if (!els.weatherPanel || !els.weatherGrid) return;
        const game = activeGame();
        if (!game) {
            els.weatherPanel.hidden = true;
            return;
        }
        els.weatherPanel.hidden = false;
        const wx = game.parkWeather || {};
        const mlb = game.mlbWeather || {};
        const hm = game.hrModel || computeGameHrModel(game);
        const stadium = lookupStadium(game?.venue || "");
        const time = fmtTime(game.startTime);
        const status = game.status ? ` · ${game.status}` : "";
        els.weatherMeta.textContent = `${game.venue || "—"} · ${time}${status}`;

        if (game._weatherLoading) {
            els.weatherGrid.innerHTML = wxCell("Loading", "Fetching forecast…", WX_TIPS.conditions);
            renderWindFieldVisual(game);
            return;
        }

        const cells = [];

        if (game.propPass) {
            cells.push(
                wxCell("⚠️ HR Props", "PASS — wait for roof/wind", WX_TIPS.pass, { pass: true, wide: true, hero: true })
            );
        }

        const hrCarryPct = displayHrCarryPct(wx);
        if (hrCarryPct != null) {
            const boostFt = displayDistanceBoostFt(wx);
            const sub =
                boostFt != null
                    ? `${boostFt > 0 ? "+" : ""}${boostFt} ft vs typical game`
                    : wx.hrCarryLabel || "";
            cells.push(
                wxCell("HR Carry", fmtSignedPct(hrCarryPct), WX_TIPS.hrCarry, {
                    tone: edgeTone(hrCarryPct),
                    sub,
                    hero: !game.propPass,
                })
            );
        }

        const roofClosed =
            wx.roof === "dome" ||
            wx.roof === "closed" ||
            game?.roofStatus?.effective === "closed" ||
            game?.roofStatus?.state === "dome";

        const windOutPct = roofClosed ? null : displayWindPct(wx.windComponentMph);
        if (windOutPct != null && wx.windMph != null) {
            const comp = wx.windComponentMph;
            let sub = `${wx.windMph} mph ${wx.windDir || ""}`;
            if (comp != null) {
                sub += comp > 0 ? ` · ${comp} mph out to CF` : comp < 0 ? ` · ${Math.abs(comp)} mph in from CF` : " · crosswind";
            }
            cells.push(
                wxCell("Wind Out", fmtSignedPct(windOutPct), WX_TIPS.windOut, {
                    tone: edgeTone(windOutPct),
                    sub,
                })
            );
        }

        const pullL = stadium ? pullAlley(stadium, "L") : null;
        const pullR = stadium ? pullAlley(stadium, "R") : null;
        const windLPct = roofClosed ? null : displayWindPct(hm?.windOutLhbMph);
        const windRPct = roofClosed ? null : displayWindPct(hm?.windOutRhbMph);
        if (windLPct != null) {
            cells.push(
                wxCell("Wind Pull L", fmtSignedPct(windLPct), WX_TIPS.windPullL, {
                    tone: edgeTone(windLPct),
                    sub: fmtWindPullSub(hm?.windOutLhbMph),
                })
            );
        }
        if (windRPct != null) {
            cells.push(
                wxCell("Wind Pull R", fmtSignedPct(windRPct), WX_TIPS.windPullR, {
                    tone: edgeTone(windRPct),
                    sub: fmtWindPullSub(hm?.windOutRhbMph),
                })
            );
        }

        if (game.parkStadiumPct != null || game.parkLhbStadiumPct != null) {
            const stadiumPct =
                game.parkStadiumPct ??
                Math.round(((Number(game.parkLhbStadiumPct) || 0) + (Number(game.parkRhbStadiumPct) || 0)) / 2);
            cells.push(
                wxCell("Park (stadium)", fmtSignedPct(stadiumPct), WX_TIPS.parkFactor, {
                    tone: edgeTone(stadiumPct),
                    sub: "Structure only — live weather separate",
                })
            );
        } else if (game.parkHrPct != null) {
            cells.push(
                wxCell("Park Factor", fmtSignedPct(game.parkHrPct), WX_TIPS.parkFactor, {
                    tone: edgeTone(game.parkHrPct),
                    sub: "Ballpark Pal",
                })
            );
        }

        const fenceLPct = pullL?.dist != null ? displayFencePct(pullL.dist, 377) : null;
        const fenceRPct = pullR?.dist != null ? displayFencePct(pullR.dist, 377) : null;
        if (fenceLPct != null || fenceRPct != null) {
            const lf = hm?.wallLfFt;
            const rf = hm?.wallRfFt;
            const sub = lf != null && rf != null ? `LF ${lf} ft · RF ${rf} ft · vs 377 ft avg` : "vs league-average pull alley";
            cells.push(
                wxCell(
                    "Short Porch",
                    `L ${fmtSignedPct(fenceLPct)} · R ${fmtSignedPct(fenceRPct)}`,
                    WX_TIPS.fenceBoost,
                    { tone: edgeTone(Math.max(fenceLPct ?? 0, fenceRPct ?? 0)), sub, wide: true }
                )
            );
        } else if (game.parkLhbPct != null || game.parkRhbPct != null) {
            cells.push(
                wxCell(
                    "Park L / R",
                    `L ${fmtSignedPct(game.parkLhbPct)} · R ${fmtSignedPct(game.parkRhbPct)}`,
                    WX_TIPS.parkFactor,
                    { wide: true, sub: "Ballpark Pal" }
                )
            );
        }

        const condParts = [];
        if (wx.tempF != null) condParts.push(`${Math.round(wx.tempF)}°F`);
        else if (mlb.temp) condParts.push(String(mlb.temp));
        if (wx.precipPct != null && wx.precipPct >= 15) condParts.push(`${Math.round(wx.precipPct)}% rain`);
        if (mlb.condition && !condParts.length) condParts.push(String(mlb.condition));
        if (condParts.length) {
            cells.push(wxCell("Conditions", condParts.join(" · "), WX_TIPS.conditions, { wide: true }));
        }

        if (wx.humidityPct != null) {
            const hImpact = displayHumidityCarryPct(wx.humidityPct);
            cells.push(
                wxCell("Humidity", `${Math.round(wx.humidityPct)}%`, WX_TIPS.humidity, {
                    tone: hImpact != null ? edgeTone(hImpact) : undefined,
                    sub: hImpact != null ? `${fmtSignedPct(hImpact)} carry vs avg` : undefined,
                })
            );
        }

        if (wx.pressureHpa != null) {
            const pImpact = displayPressureCarryPct(wx.pressureHpa);
            cells.push(
                wxCell("Air Pressure", `${wx.pressureHpa} hPa`, WX_TIPS.pressure, {
                    tone: pImpact != null ? edgeTone(pImpact) : undefined,
                    sub: pImpact != null ? `${fmtSignedPct(pImpact)} carry vs avg` : undefined,
                })
            );
        }

        if (wx.roof || game.roofStatus) {
            const roofLabel = fmtRoofLabel(game, wx);
            const passNote = game.propPass ? " · PASS HR props" : "";
            const reason = rsReason(game);
            const tip = reason ? `${WX_TIPS.roof} ${reason}` : WX_TIPS.roof;
            cells.push(
                wxCell("Roof", `${roofLabel}${passNote}`, tip, {
                    pass: !!game.propPass,
                    sub: reason || undefined,
                })
            );
        }

        if (!cells.length) {
            cells.push(wxCell("Weather", wx.error || "Unavailable", WX_TIPS.conditions));
        }

        els.weatherGrid.innerHTML = cells.join("");
        renderWindFieldVisual(game);
    }

    function escAttr(s) {
        return String(s)
            .replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/</g, "&lt;");
    }

    function tipAttr(tip) {
        return tip ? ` class="rs-has-tip" data-tip="${escAttr(tip)}" tabindex="0"` : "";
    }

    function applyHeaderTip(el, tip) {
        if (!el || !tip) return;
        el.classList.add("rs-has-tip");
        el.setAttribute("data-tip", tip);
        el.setAttribute("tabindex", "0");
    }

    function wireExploreLeaderboardTips() {
        els.hrLeaderboard?.querySelectorAll("thead th").forEach((th) => {
            const sort = th.getAttribute("data-sort");
            const label = th.textContent.replace(/[↑↓]/g, "").trim();
            const tip = (sort && EXPLORE_HITTER_LB_TIPS[sort]) || EXPLORE_HITTER_LB_TIPS[label];
            applyHeaderTip(th, tip);
        });
        els.pitcherLeaderboard?.querySelectorAll("thead th").forEach((th) => {
            const sort = th.getAttribute("data-sort");
            const label = th.textContent.replace(/[↑↓]/g, "").trim();
            const tip = (sort && EXPLORE_PITCHER_LB_TIPS[sort]) || EXPLORE_PITCHER_LB_TIPS[label];
            applyHeaderTip(th, tip);
        });
    }

    function wireExploreLbNav() {
        const nav = document.getElementById("rsExploreLbNav");
        if (!nav) return;
        const panels = document.querySelectorAll("[data-lb-panel]");
        const btns = nav.querySelectorAll("[data-lb]");
        const setActive = (key) => {
            btns.forEach((b) => {
                const on = b.getAttribute("data-lb") === key;
                b.classList.toggle("is-active", on);
                b.setAttribute("aria-selected", on ? "true" : "false");
            });
            panels.forEach((p) => {
                p.classList.toggle("is-active", p.getAttribute("data-lb-panel") === key);
            });
        };
        btns.forEach((b) => {
            b.addEventListener("click", () => setActive(b.getAttribute("data-lb")));
        });
        const mq = window.matchMedia("(max-width: 768px)");
        const sync = () => {
            if (!mq.matches) {
                panels.forEach((p) => p.classList.add("is-active"));
                return;
            }
            const activeBtn = nav.querySelector(".rs-explore-lb-nav__btn.is-active");
            setActive(activeBtn?.getAttribute("data-lb") || "hitters");
        };
        mq.addEventListener("change", sync);
        sync();
    }

    function renderDataFreshness() {
        if (!els.lastUpdated) return;
        const ts = slate?.fetched_at;
        if (!ts) {
            els.lastUpdated.textContent = "";
            return;
        }
        const when = new Date(ts);
        els.lastUpdated.textContent = Number.isNaN(when.getTime())
            ? `Updated ${ts}`
            : `Updated ${when.toLocaleString()}`;
    }

    function statsForPlayerId(id) {
        const lookup = savantLookup || slate?.savant_lookup || {};
        return lookup?.[id] || lookup?.[String(id)] || {};
    }

    function exploreTicketField(entry, key) {
        const ticket = computeHrTicket(entry);
        const stats = hitterStats(entry.row);
        if (key === "ticketRank") return ticket?.score100 ?? ticket?.rank ?? null;
        if (key === "splitPct") return ticket?.splitPct ?? null;
        if (key === "riskPct") return ticket?.riskPct ?? null;
        if (key === "parkPct") return ticket?.parkPct ?? null;
        if (key === "mixPlus") return ticket?.mixPlus ?? stats.mixPlus ?? null;
        if (key === "formPct") return stats.hrFormPct ?? stats.hrForm ?? null;
        if (key === "matchWhiffPct") return stats.matchWhiffPct ?? stats.bvpKPct ?? null;
        if (key === "mixEdge") return stats.mixEdge ?? ticket?.mixEdge ?? null;
        if (key === "barrelPct") return stats.barrelPct ?? null;
        if (key === "airPct") return stats.airPct ?? null;
        if (key === "nearHr") return stats.nearHr ?? null;
        if (key === "avgEV") return stats.avgEV ?? null;
        return exploreSortValue(entry, key);
    }

    function syncExploreSortSelect(key) {
        exploreSortKey = key;
        if (els.exploreSort && [...els.exploreSort.options].some((o) => o.value === key)) {
            els.exploreSort.value = key;
        }
        els.hrLeaderboard?.querySelectorAll(".rs-lb-sort").forEach((th) => {
            th.classList.toggle("is-sorted", th.getAttribute("data-sort") === key);
        });
    }

    function resetExploreFilters() {
        const d = HR_RESEARCH_CONFIG.explore;
        if (els.exploreHand) els.exploreHand.value = d.hand || "";
        if (els.exploreMinScore) els.exploreMinScore.value = d.minScore ?? "";
        if (els.exploreMinPark) els.exploreMinPark.value = d.minPark ?? "";
        syncExploreSortSelect(d.sort || "ticketRank");
        renderExplorePanel();
    }

    function hrResearchPillarsHtml() {
        return HR_RESEARCH_CONFIG.pillars
            .map((p) => `<span class="rs-pillar"><strong>${p.label}</strong> — ${p.metrics}</span>`)
            .join("");
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
        let total = 0;
        let withMix = 0;
        for (const g of games || []) {
            for (const h of [...(g.awayLineup || []), ...(g.homeLineup || [])]) {
                if (!h?.id) continue;
                total += 1;
                if (h.stats?.mixPlus != null) withMix += 1;
            }
        }
        return { total, withMix, any: withMix > 0, full: total > 0 && withMix === total };
    }

    function opposingPitcher(game, offenseSide) {
        if (!game) return null;
        return offenseSide === "away" ? game.homePitcher : game.awayPitcher;
    }

    function pitchMixStatusForSide(game, offenseSide, season) {
        const pitcher = opposingPitcher(game, offenseSide);
        if (!pitcher?.id) {
            return { available: false, reason: "probable starter not announced yet" };
        }
        if (!pitcher.arsenal || !Object.keys(pitcher.arsenal).length) {
            return {
                available: false,
                reason: `${pitcher.name} has no Savant pitch-mix data yet (rookie or too few 2026 pitches)`,
            };
        }
        const priorSeason = pitcher.arsenalSeason != null && season && pitcher.arsenalSeason < season;
        return { available: true, priorSeason };
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

    // History (batter vs pitcher career) is noisy at small samples, so it needs a
    // real sample before it counts and never outweighs today's pitch-mix fit.
    const MATCHUP_EDGE_CAP = 25;
    const MIN_HISTORY_PITCHES = 20;
    const HISTORY_CONF_PITCHES = 90;
    const MATCHUP_BLEND = 0.7;
    const HISTORY_BLEND = 0.3;

    const matchupHistoryCache = new Map();
    let matchupHydrateGen = 0;

    function matchupPairKey(batterId, pitcherId) {
        return `${batterId}|${pitcherId}`;
    }

    function seasonStatsForMatchup(row) {
        const stats = { ...(row?.stats || {}) };
        const pid = row?.id;
        const sav =
            (slate?.savant_lookup && (slate.savant_lookup[pid] || slate.savant_lookup[String(pid)])) ||
            savantLookup?.[pid] ||
            savantLookup?.[String(pid)] ||
            {};
        for (const k of ["iso", "slg", "hr", "pa", "xwoba"]) {
            if (stats[k] == null && sav[k] != null) stats[k] = sav[k];
        }
        return stats;
    }

    function scoreSavantMatchupEdge(seasonStats, mixXwoba, history) {
        seasonStats = seasonStats || {};
        let seasonXwoba = seasonStats.xwoba != null ? Number(seasonStats.xwoba) : null;
        if (seasonXwoba == null || Number.isNaN(seasonXwoba)) seasonXwoba = 0.32;

        let matchupEdge = null;
        if (mixXwoba != null && !Number.isNaN(Number(mixXwoba))) {
            matchupEdge = Math.round((Number(mixXwoba) - seasonXwoba) * 1000) / 10;
        }

        let historyEdge = null;
        let pitches = 0;
        let histXwoba = null;
        let whiff = null;
        if (history) {
            pitches = Number(history.pitches) || 0;
            histXwoba = history.xwoba != null ? Number(history.xwoba) : null;
            whiff = history.whiffPct != null ? Number(history.whiffPct) : null;
            if (pitches >= MIN_HISTORY_PITCHES && histXwoba != null && !Number.isNaN(histXwoba)) {
                const conf = Math.min(pitches / HISTORY_CONF_PITCHES, 1);
                historyEdge = Math.round((histXwoba - seasonXwoba) * 100 * conf * 10) / 10;
            }
        }

        let mixEdge;
        if (matchupEdge != null && historyEdge != null) {
            mixEdge = Math.round((matchupEdge * MATCHUP_BLEND + historyEdge * HISTORY_BLEND) * 10) / 10;
        } else if (matchupEdge != null) {
            mixEdge = matchupEdge;
        } else if (historyEdge != null) {
            mixEdge = historyEdge;
        } else {
            return null;
        }

        mixEdge = Math.max(-MATCHUP_EDGE_CAP, Math.min(MATCHUP_EDGE_CAP, mixEdge));
        const out = { mixEdge, edgeSource: "savant-matchup" };
        if (matchupEdge != null) out.matchupEdge = matchupEdge;
        if (historyEdge != null) out.historyEdge = historyEdge;
        if (pitches) out.matchPitches = pitches;
        if (histXwoba != null) out.matchXwoba = Math.round(histXwoba * 1000) / 1000;
        if (whiff != null) {
            out.matchWhiffPct = whiff;
        }
        return out;
    }

    function clearMatchupEdgeStats(stats) {
        for (const key of [
            "mixEdge",
            "matchupEdge",
            "historyEdge",
            "matchPitches",
            "matchXwoba",
            "matchWhiffPct",
            "edgeSource",
            "bvpKPct",
            "bvpAb",
            "bvpHr",
            "bvpIso",
            "bvpSlg",
            "bvpAvg",
            "bvpObp",
            "bvpSource",
        ]) {
            delete stats[key];
        }
    }

    function applyMatchupEdgeToRow(row, opposingPitcher, historyLookup) {
        const enriched = { ...row };
        const stats = seasonStatsForMatchup(enriched);
        const batterId = enriched.id;
        const pitcherId = opposingPitcher?.id;
        const mixXwoba = stats.mixXwoba != null ? Number(stats.mixXwoba) : null;
        const history =
            historyLookup && batterId && pitcherId
                ? historyLookup[matchupPairKey(batterId, pitcherId)] ||
                  historyLookup.get?.(matchupPairKey(batterId, pitcherId))
                : matchupHistoryCache.get(matchupPairKey(batterId, pitcherId));

        const scored = scoreSavantMatchupEdge(stats, mixXwoba, history);
        if (scored) {
            Object.assign(stats, scored);
        } else {
            clearMatchupEdgeStats(stats);
        }
        enriched.stats = stats;
        return enriched;
    }

    function matchupHistoryLookupFromCache() {
        const out = {};
        for (const [key, val] of matchupHistoryCache.entries()) out[key] = val;
        return out;
    }

    function applyMatchupEdgeToAllLineups(historyLookup) {
        const lookup = historyLookup || matchupHistoryLookupFromCache();
        let n = 0;
        for (const game of slate.games || []) {
            game.awayLineup = (game.awayLineup || []).map((row) =>
                applyMatchupEdgeToRow(row, game.homePitcher, lookup)
            );
            game.homeLineup = (game.homeLineup || []).map((row) =>
                applyMatchupEdgeToRow(row, game.awayPitcher, lookup)
            );
            for (const h of [...(game.awayLineup || []), ...(game.homeLineup || [])]) {
                if (h.stats?.mixEdge != null) n += 1;
            }
        }
        return n;
    }

    function collectSlateMatchupPairs() {
        const pairs = new Map();
        for (const entry of collectSlateHitters()) {
            const batterId = entry.row?.id;
            const pitcherId = entry.pitcher?.id;
            if (!batterId || !pitcherId) continue;
            pairs.set(matchupPairKey(batterId, pitcherId), { batterId, pitcherId });
        }
        return [...pairs.values()];
    }

    async function fetchSavantMatchup(batterId, pitcherId) {
        const res = await fetch(
            `/api/savant-matchup?batterId=${encodeURIComponent(batterId)}&pitcherId=${encodeURIComponent(pitcherId)}`
        );
        if (!res.ok) return null;
        const data = await res.json();
        return data.matchup || null;
    }

    function scheduleMatchupEdgeHydrate() {
        const pairs = collectSlateMatchupPairs().filter(
            ({ batterId, pitcherId }) => !matchupHistoryCache.has(matchupPairKey(batterId, pitcherId))
        );
        if (!pairs.length) return;
        const gen = ++matchupHydrateGen;
        (async () => {
            // Probe once — if the proxy is missing entirely, skip the whole batch
            // instead of issuing hundreds of 404s.
            if (!(await proxyAvailable("/api/savant-matchup?batterId=660271&pitcherId=543037"))) return;
            for (let i = 0; i < pairs.length; i += 6) {
                if (gen !== matchupHydrateGen) return;
                const batch = pairs.slice(i, i + 6);
                await Promise.all(
                    batch.map(async ({ batterId, pitcherId }) => {
                        const key = matchupPairKey(batterId, pitcherId);
                        try {
                            const matchup = await fetchSavantMatchup(batterId, pitcherId);
                            matchupHistoryCache.set(key, matchup || { pitches: 0 });
                        } catch {
                            matchupHistoryCache.set(key, { pitches: 0 });
                        }
                    })
                );
            }
            if (gen !== matchupHydrateGen) return;
            applyMatchupEdgeToAllLineups();
            clearHrTicketCache();
            if (columnReorderMode) return;
            renderTable();
            renderMobileCards();
            renderExplorePanel();
        })();
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

    function attachPitcherArsenal(pitcher, pitcherArsenalLookup, priorLookup, season) {
        if (!pitcher) return pitcher;
        const out = { ...pitcher };
        const pid = out.id;
        let arsenal = normalizeArsenal(pitcherArsenalLookup?.[pid] || pitcherArsenalLookup?.[String(pid)]);
        let arsenalSeason = season;
        if (!Object.keys(arsenal).length && priorLookup) {
            arsenal = normalizeArsenal(priorLookup?.[pid] || priorLookup?.[String(pid)]);
            if (Object.keys(arsenal).length && season) arsenalSeason = season - 1;
        }
        if (Object.keys(arsenal).length) {
            out.arsenal = arsenal;
            let label = formatArsenal(arsenal);
            if (arsenalSeason && season && arsenalSeason < season) label += ` (${arsenalSeason} mix)`;
            out.arsenalLabel = label;
            out.arsenalSeason = arsenalSeason;
        }
        return out;
    }

    function enrichHitterPitchMix(row, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap, historyLookup) {
        const enriched = { ...row };
        const stats = { ...(enriched.stats || {}) };
        if (stats.mixPlus == null) {
            const pid = enriched.id;
            const pitcher = opposingPitcher || {};
            const batterPitch = batterPitchLookup?.[pid] || batterPitchLookup?.[String(pid)] || null;
            const overallXwoba = stats.xwoba ?? savantLookupMap?.[pid]?.xwoba ?? savantLookupMap?.[String(pid)]?.xwoba;
            const mix = scoreBatterVsArsenal(pid, pitcher.arsenal, batterPitch, overallXwoba, leagueAvgs);
            if (mix) Object.assign(stats, mix);
        }
        enriched.stats = stats;
        return applyMatchupEdgeToRow(enriched, opposingPitcher, historyLookup);
    }

    function enrichLineupPitchMix(lineup, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap, historyLookup) {
        return (lineup || []).map((row) =>
            enrichHitterPitchMix(row, opposingPitcher, batterPitchLookup, leagueAvgs, savantLookupMap, historyLookup)
        );
    }

    async function ensurePitchMixCaches(season) {
        if (pitchMixCache) return pitchMixCache;
        if (slate?.pitcher_arsenal_lookup && Object.keys(slate.pitcher_arsenal_lookup).length) {
            pitchMixCache = {
                pitcherArsenal: slate.pitcher_arsenal_lookup,
                pitcherArsenalPrior: slate.pitcher_arsenal_prior_lookup || {},
                batterPitch: slate.batter_pitch_lookup || {},
                leagueAvgs: slate.league_pitch_avgs || {},
            };
            return pitchMixCache;
        }
        const priorSeason = season > 2024 ? season - 1 : null;
        const fetches = [
            fetchDataJson(`savant-pitcher-arsenal-${season}.json`),
            fetchDataJson(`savant-batter-pitch-type-${season}.json`),
        ];
        if (priorSeason) fetches.push(fetchDataJson(`savant-pitcher-arsenal-${priorSeason}.json`));
        const results = await Promise.all(fetches);
        const [arsenalRes, batterRes, priorRes] = results;
        pitchMixCache = {
            pitcherArsenal: arsenalRes.data?.lookup || {},
            pitcherArsenalPrior: priorRes?.data?.lookup || {},
            batterPitch: batterRes.data?.lookup || {},
            leagueAvgs: batterRes.data?.leagueAvgs || {},
            lastStatus: `${arsenalRes.lastStatus}; ${batterRes.lastStatus}${priorRes ? `; ${priorRes.lastStatus}` : ""}`,
        };
        return pitchMixCache;
    }

    function savantLookupMapFromSlate() {
        const map = {};
        const src = slate?.savant_lookup || savantLookup || {};
        for (const [k, v] of Object.entries(src)) map[k] = v;
        return map;
    }

    async function applyPitchMixEnrichment(season, sheetDate) {
        const caches = await ensurePitchMixCaches(season);
        if (!Object.keys(caches.pitcherArsenal || {}).length && !Object.keys(caches.pitcherArsenalPrior || {}).length) {
            return { n: 0, source: null, lastStatus: caches.lastStatus };
        }
        const savMap = savantLookupMapFromSlate();
        const historyLookup = matchupHistoryLookupFromCache();
        let n = 0;
        for (const game of slate.games || []) {
            game.awayPitcher = attachPitcherArsenal(
                game.awayPitcher,
                caches.pitcherArsenal,
                caches.pitcherArsenalPrior,
                season
            );
            game.homePitcher = attachPitcherArsenal(
                game.homePitcher,
                caches.pitcherArsenal,
                caches.pitcherArsenalPrior,
                season
            );
            game.awayLineup = enrichLineupPitchMix(
                game.awayLineup,
                game.homePitcher,
                caches.batterPitch,
                caches.leagueAvgs,
                savMap,
                historyLookup
            );
            game.homeLineup = enrichLineupPitchMix(
                game.homeLineup,
                game.awayPitcher,
                caches.batterPitch,
                caches.leagueAvgs,
                savMap,
                historyLookup
            );
            for (const h of [...(game.awayLineup || []), ...(game.homeLineup || [])]) {
                if (h.stats?.mixPlus != null) n += 1;
            }
        }
        return { n, source: "pitch-mix-cache" };
    }

    function pitcherMissing(pitcher) {
        if (!pitcher?.name) return true;
        const name = String(pitcher.name).trim().toUpperCase();
        return name === "TBD" || !pitcher.id;
    }

    function lineupIsRosterProjection(rows) {
        return !(rows || []).length || (rows || []).every((r) => r.projected);
    }

    function rotowireLineupBetter(existing, incoming) {
        if (!(incoming || []).length || incoming.length < 7) return false;
        if (!(existing || []).length) return true;
        return lineupIsRosterProjection(existing);
    }

    function normalizeMatchupKey(matchup) {
        return String(matchup || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function applyRotowireGame(game, rwGame) {
        if (!game || !rwGame) return { pitchers: 0, lineups: 0 };
        let pitchers = 0;
        let lineups = 0;
        if (pitcherMissing(game.awayPitcher) && rwGame.awayPitcher?.name) {
            game.awayPitcher = { ...rwGame.awayPitcher };
            pitchers += 1;
        }
        if (pitcherMissing(game.homePitcher) && rwGame.homePitcher?.name) {
            game.homePitcher = { ...rwGame.homePitcher };
            pitchers += 1;
        }
        if (rotowireLineupBetter(game.awayLineup, rwGame.awayLineup)) {
            game.awayLineup = (rwGame.awayLineup || []).map((row) => ({ ...row, stats: row.stats || {} }));
            lineups += 1;
        }
        if (rotowireLineupBetter(game.homeLineup, rwGame.homeLineup)) {
            game.homeLineup = (rwGame.homeLineup || []).map((row) => ({ ...row, stats: row.stats || {} }));
            lineups += 1;
        }
        const awayConfirmed = (game.awayLineup || []).some((r) => !r.projected);
        const homeConfirmed = (game.homeLineup || []).some((r) => !r.projected);
        if (awayConfirmed && homeConfirmed) game.lineupStatus = "confirmed";
        else if (awayConfirmed || homeConfirmed) game.lineupStatus = "partial";
        else if ((game.awayLineup || []).length || (game.homeLineup || []).length) game.lineupStatus = "projected";
        return { pitchers, lineups };
    }

    async function applyRotowireFallback(date) {
        if (!slate?.games?.length) return { pitchers: 0, lineups: 0 };
        const needsPitcher = slate.games.some(
            (g) => pitcherMissing(g.awayPitcher) || pitcherMissing(g.homePitcher)
        );
        const needsLineup = slate.games.some(
            (g) => lineupIsRosterProjection(g.awayLineup) || lineupIsRosterProjection(g.homeLineup)
        );
        if (!needsPitcher && !needsLineup) return { pitchers: 0, lineups: 0 };
        if (!(await proxyAvailable(`/api/rotowire-lineups?date=${encodeURIComponent(date)}`))) {
            return { pitchers: 0, lineups: 0 };
        }
        try {
            const res = await fetch(`/api/rotowire-lineups?date=${encodeURIComponent(date)}`);
            if (!res.ok) return { pitchers: 0, lineups: 0, error: res.status };
            const data = await res.json();
            const byMatchup = new Map(
                (data.games || []).map((g) => [normalizeMatchupKey(g.matchup), g])
            );
            let pitchers = 0;
            let lineups = 0;
            for (const game of slate.games) {
                const rw = byMatchup.get(normalizeMatchupKey(game.matchup));
                if (!rw) continue;
                const applied = applyRotowireGame(game, rw);
                pitchers += applied.pitchers;
                lineups += applied.lineups;
            }
            slate.rotowire = {
                source: "rotowire-daily-lineups",
                pageDate: data.pageDate,
                pitchersFilled: pitchers,
                lineupsFilled: lineups,
            };
            return { pitchers, lineups, pageDate: data.pageDate };
        } catch (err) {
            console.warn("rotowire fallback", err);
            return { pitchers: 0, lineups: 0, error: String(err.message || err) };
        }
    }

    function mergePitcher(live, cached) {
        if (!cached) return live || null;
        if (!live) return { ...cached };
        return {
            ...cached,
            ...live,
            stats: { ...(cached.stats || {}), ...(live.stats || {}) },
            arsenal: cached.arsenal || live.arsenal,
            arsenalLabel: cached.arsenalLabel || live.arsenalLabel,
        };
    }

    function applyCachedEnrichment(live, cached) {
        if (!live || !cached) return;
        for (const key of [
            "savant_lookup",
            "savant_pitcher_lookup",
            "pitcher_hand_lookup",
            "propfinder_lookup",
            "zone_lookup",
            "pitcher_arsenal_lookup",
            "pitcher_arsenal_prior_lookup",
            "batter_pitch_lookup",
            "league_pitch_avgs",
            "season",
            "fetched_at",
            "stat_windows",
            "savant_only",
            "source",
            "rotowire",
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
            for (const field of [
                "parkHrPct",
                "parkLhbPct",
                "parkRhbPct",
                "parkStadiumPct",
                "parkWeatherPct",
                "parkLhbStadiumPct",
                "parkRhbStadiumPct",
                "parkWeather",
                "mlbWeather",
                "venue",
                "hrModel",
                "roofStatus",
                "propPass",
            ]) {
                if (cg[field] != null && game[field] == null) game[field] = cg[field];
            }
            if (cg.awayPitcher?.stats && game.awayPitcher) {
                game.awayPitcher.stats = { ...(cg.awayPitcher.stats || {}), ...(game.awayPitcher.stats || {}) };
            }
            if (cg.homePitcher?.stats && game.homePitcher) {
                game.homePitcher.stats = { ...(cg.homePitcher.stats || {}), ...(game.homePitcher.stats || {}) };
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
            if (lineupsHavePitchMix(slate?.games).any) {
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

    function isRollingStatProfile(stats) {
        if (!stats) return false;
        if (stats.statWindow) return true;
        const src = String(stats.source || "");
        return src.includes("savant-last") && (src.includes("g") || src.includes("st"));
    }

    function mergeStats(windowStats, savant, propfinder, existing) {
        const out = { ...(existing || {}) };
        const rolling = isRollingStatProfile(out);
        const sav = savant || {};
        const savantKeys = [
            "avg",
            "slg",
            "iso",
            "xwoba",
            "barrelPct",
            "hardHitPct",
            "avgEV",
            "launchAngle",
            "sweetSpotPct",
            "batSpeed",
            "swingStrength",
            "solidContactPct",
            "blastPct",
            "bip",
            "bipPct",
            "fbPct",
            "gbPct",
            "ldPct",
            "hrFbPct",
            "whiffPct",
            "kPct",
            "hr",
            "expectedHr",
            "hrLuckDiff",
            "mostlyGone",
            "noDoubters",
            "nearHr",
            "recentForm",
            "pullPct",
            "pullAirPct",
            "pullBarrelPct",
            "xwobaVsLhp",
            "paVsLhp",
            "xwobaVsRhp",
            "paVsRhp",
        ];
        for (const k of savantKeys) {
            if (rolling && out[k] != null) continue;
            if (sav[k] != null) out[k] = sav[k];
        }
        const pf = propfinder || {};
        if (out.nearHr == null && pf.nearHr != null) {
            out.nearHr = pf.nearHr;
            out.nearHrSource = "propfinder";
        } else if (out.nearHr != null && !out.nearHrSource) {
            out.nearHrSource = sav.hrTrackerSource || "savant-hr";
        }
        if (SAVANT_ONLY) {
            if (out.kPct == null && pf.kPct != null) out.kPct = pf.kPct;
            if (pf.nearHr != null) out.propfinderNearHr = pf.nearHr;
            const sources = [out.source || sav.source || "savant"];
            if (pf.nearHr != null || pf.kPct != null) sources.push("propfinder");
            out.source = [...new Set(sources.filter(Boolean))].join("+");
            return out;
        }
        const win = windowStats || {};
        if (out.nearHr == null && pf.nearHr != null) out.nearHr = pf.nearHr;
        for (const k of ["hr", "hits", "ab"]) {
            if (win[k] != null) out[k] = win[k];
        }
        if (out.hr == null && sav.hr != null) out.hr = sav.hr;
        if (out.nearHr == null && pf.nearHr != null) out.nearHr = pf.nearHr;
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
                    if (!pf) return row;
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

    async function buildProjectedLineup(teamId, season, lookup, windowRange, propfinderLookup) {
        const rosterSeason = season;
        let hitters = await fetchTeamHitters(teamId, rosterSeason);
        hitters.sort((a, b) => {
            const sa = lookup?.[a.id] || {};
            const sb = lookup?.[b.id] || {};
            return (sb.pa || 0) - (sa.pa || 0) || (sb.hr || 0) - (sa.hr || 0);
        });
        const lineup = hitters.map((h, i) => ({ ...h, order: i + 1 }));
        return enrichLineup(lineup, season, lookup, windowRange, propfinderLookup);
    }

    async function expandLineupWithRosterBench(lineup, teamId, season, lookup, windowRange, propfinderLookup) {
        if (!teamId || !(lineup || []).length) return lineup || [];
        const roster = await fetchTeamHitters(teamId, season);
        if (!roster.length) return lineup;
        const seenIds = new Set();
        const seenNames = new Set();
        for (const row of lineup) {
            if (row.id) seenIds.add(row.id);
            if (row.name) seenNames.add(nameLookupKey(row.name));
        }
        const benchSort = (h) => {
            const sav = lookup?.[h.id] || lookup?.[String(h.id)] || {};
            return (sav.pa || 0) * 1000 + (sav.hr || 0);
        };
        const bench = roster
            .filter(
                (h) =>
                    h.id &&
                    !seenIds.has(h.id) &&
                    !seenNames.has(nameLookupKey(h.name))
            )
            .sort((a, b) => benchSort(b) - benchSort(a));
        if (!bench.length) return lineup;
        let maxOrder = Math.max(0, ...lineup.map((h) => h.order || 0));
        const extra = bench.map((h) => {
            maxOrder += 1;
            return { ...h, order: maxOrder, projected: true };
        });
        return enrichLineup([...lineup, ...extra], season, lookup, windowRange, propfinderLookup);
    }

    async function expandAllLineupDepth(season, sheetDate) {
        if (!slate?.games?.length) return;
        const lookup = await loadSavantLookup(season);
        const windowRange =
            slate?.window_start && slate?.window_end
                ? { start: slate.window_start, end: slate.window_end }
                : windowBounds(sheetDate);
        const propfinderLookup = propfinderLookupFromSlate();
        for (const game of slate.games) {
            game.awayLineup = await expandLineupWithRosterBench(
                game.awayLineup || [],
                game.awayTeamId,
                season,
                lookup,
                windowRange,
                propfinderLookup
            );
            game.homeLineup = await expandLineupWithRosterBench(
                game.homeLineup || [],
                game.homeTeamId,
                season,
                lookup,
                windowRange,
                propfinderLookup
            );
        }
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
            const enriched = await enrichLineup(lineup, season, lookup, windowRange, propfinderLookup);
            game[key] = teamId
                ? await expandLineupWithRosterBench(
                      enriched,
                      teamId,
                      season,
                      lookup,
                      windowRange,
                      propfinderLookup
                  )
                : enriched;
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
            `/schedule?sportId=1&date=${encodeURIComponent(date)}&hydrate=probablePitcher,team,venue,weather`
        );
        const games = [];
        for (const day of data.dates || []) {
            for (const g of day.games || []) {
                const awayT = g.teams?.away?.team || {};
                const homeT = g.teams?.home?.team || {};
                const awayP = g.teams?.away?.probablePitcher;
                const homeP = g.teams?.home?.probablePitcher;
                const mlbWx = g.weather || null;
                games.push({
                    gamePk: g.gamePk,
                    matchup: `${awayT.abbreviation} @ ${homeT.abbreviation}`,
                    away: awayT.abbreviation,
                    home: homeT.abbreviation,
                    awayTeamId: awayT.id,
                    homeTeamId: homeT.id,
                    startTime: g.gameDate,
                    venue: g.venue?.name || "",
                    venueId: g.venue?.id,
                    status: g.status?.detailedState || "",
                    mlbWeather: mlbWx
                        ? {
                              condition: mlbWx.condition || "",
                              temp: mlbWx.temp || "",
                              wind: mlbWx.wind || "",
                          }
                        : null,
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

    function lineupHasMixPct(rows) {
        return (rows || []).some((r) => {
            const v = hitterStats(r).mixPlus;
            return v != null && !Number.isNaN(Number(v));
        });
    }

    function applyDefaultSort() {
        const rows = activeRows();
        sortKey = lineupHasMixPct(rows) ? "mixPlus" : "hardHitPct";
        sortDir = -1;
    }

    function saveSortPreference() {
        if (!sortUserOverride) return;
        try {
            sessionStorage.setItem(
                SORT_PREF_KEY,
                JSON.stringify({ sortKey, sortDir: sortDir > 0 ? 1 : -1 })
            );
        } catch {
            /* ignore quota / private mode */
        }
    }

    function restoreSortPreference() {
        try {
            const raw = sessionStorage.getItem(SORT_PREF_KEY);
            if (!raw) return false;
            const parsed = JSON.parse(raw);
            const k = parsed?.sortKey;
            if (!k || !COLS.some((c) => c.key === k)) return false;
            sortKey = k;
            sortDir = Number(parsed.sortDir) > 0 ? 1 : -1;
            sortUserOverride = true;
            return true;
        } catch {
            return false;
        }
    }

    function resetSortToDefault() {
        sortUserOverride = false;
        try {
            sessionStorage.removeItem(SORT_PREF_KEY);
        } catch {
            /* ignore */
        }
        applyDefaultSort();
    }

    function setSortColumn(key, { toggleDir = true } = {}) {
        if (!key || !COLS.some((c) => c.key === key)) return;
        sortUserOverride = true;
        if (toggleDir && sortKey === key) sortDir *= -1;
        else {
            sortKey = key;
            sortDir = key === "name" ? 1 : -1;
        }
        saveSortPreference();
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

    // ── Goblin power highlight (always on; purple row/card accent) ──
    const PRESET_GREEN_ONLY = ["hardHitPct", "gbPct", "airPct"];
    const PRESET_GREEN_OR_YELLOW = ["avgEV", "barrelPct", "whiffPct", "blastPct", "pullPct"];

    function presetHeatTier(colValues, higherBetter, key, val) {
        if (val == null || Number.isNaN(Number(val))) return null;
        const cls = heatClass(colValues[key] || [], Number(val), higherBetter[key] !== false);
        if (cls.indexOf("--good") !== -1) return "good";
        if (cls.indexOf("--mid") !== -1) return "mid";
        if (cls.indexOf("--bad") !== -1) return "bad";
        return null;
    }

    function rowMatchesPreset(row, colValues, higherBetter) {
        const stats = hitterStats(row);
        const tier = (key) => presetHeatTier(colValues, higherBetter, key, stats[key]);
        for (const key of PRESET_GREEN_ONLY) {
            if (tier(key) !== "good") return false;
        }
        for (const key of PRESET_GREEN_OR_YELLOW) {
            const t = tier(key);
            if (t !== "good" && t !== "mid") return false;
        }
        for (const [key, trendFn] of [
            ["boomPct", boomTrendForRow],
            ["hrFormPct", formTrendForRow],
        ]) {
            const t = tier(key);
            if (t === "good") continue;
            if (t !== "mid") return false;
            const trend = trendFn(row);
            if (trend !== "up" && trend !== "flat") return false;
        }
        return true;
    }

    /** Matching hitter ids for the current row set (view-independent heat tiers). */
    function presetMatchIds(rows) {
        const { colValues, higherBetter } = statHeatMap(rows);
        const ids = new Set();
        for (const row of rows) {
            if (row.id != null && rowMatchesPreset(row, colValues, higherBetter)) ids.add(String(row.id));
        }
        return ids;
    }

    function allLineupRows() {
        if (!slate?.games?.length) return [];
        const rows = [];
        for (const game of slate.games) {
            for (const side of ["awayLineup", "homeLineup"]) {
                for (const row of game[side] || []) rows.push(row);
            }
        }
        return rows;
    }

    let slatePresetIdsCache = null;

    function slatePresetMatchIds() {
        if (!slatePresetIdsCache) slatePresetIdsCache = presetMatchIds(allLineupRows());
        return slatePresetIdsCache;
    }

    function clearSlatePresetCache() {
        slatePresetIdsCache = null;
    }

    function presetIdsForViewRows(rows) {
        const slateIds = slatePresetMatchIds();
        const viewIds = new Set();
        for (const row of rows) {
            if (row.id != null && slateIds.has(String(row.id))) viewIds.add(String(row.id));
        }
        return viewIds;
    }

    function renderGoblinsPanel() {
        const section = document.getElementById("rsGoblinsSection");
        const list = document.getElementById("rsGoblinsList");
        if (!section || !list) return;
        const ids = slatePresetMatchIds();
        if (!ids.size) {
            section.hidden = true;
            list.innerHTML = "";
            return;
        }
        const seen = new Set();
        const entries = [];
        for (const entry of collectSlateHitters()) {
            const id = entry.row?.id != null ? String(entry.row.id) : null;
            if (!id || !ids.has(id) || seen.has(id)) continue;
            seen.add(id);
            entries.push(entry);
        }
        if (!entries.length) {
            section.hidden = true;
            list.innerHTML = "";
            return;
        }
        entries.sort((a, b) => {
            const ba = Number(hitterStats(a.row).boomPct);
            const bb = Number(hitterStats(b.row).boomPct);
            return (Number.isNaN(bb) ? -1 : bb) - (Number.isNaN(ba) ? -1 : ba);
        });
        section.hidden = false;
        list.innerHTML = entries
            .map((entry, i) => {
                const stats = hitterStats(entry.row);
                const mix = stats.mixPlus ?? resolveMixPlusForEntry(entry, stats);
                const park = entry.game?.parkHrPct;
                const vsSp = entry.pitcher?.name ? `vs ${entry.pitcher.name}` : "";
                return `<button type="button" class="rs-goblin-card" data-goblin-idx="${i}">
                    <span class="rs-goblin-card__rank">${i + 1}</span>
                    <span class="rs-goblin-card__who">
                        <span class="rs-goblin-card__name">${escAttr(entry.row.name || "—")}</span>
                        <span class="rs-goblin-card__game">${escAttr(entry.game?.matchup || "")}${vsSp ? ` · ${escAttr(vsSp)}` : ""}</span>
                    </span>
                    <span class="rs-goblin-card__stats">
                        <span class="rs-goblin-stat"><span class="rs-goblin-stat__label">Mix</span><span class="rs-goblin-stat__val">${fmtSignedPct(mix)}</span></span>
                        <span class="rs-goblin-stat"><span class="rs-goblin-stat__label">Boom</span><span class="rs-goblin-stat__val">${fmtPct(stats.boomPct)}</span></span>
                        <span class="rs-goblin-stat"><span class="rs-goblin-stat__label">Park</span><span class="rs-goblin-stat__val">${fmtSignedPct(park)}</span></span>
                        <span class="rs-goblin-stat"><span class="rs-goblin-stat__label">Hard Hit</span><span class="rs-goblin-stat__val">${fmtPct(stats.hardHitPct)}</span></span>
                    </span>
                </button>`;
            })
            .join("");
        list.querySelectorAll(".rs-goblin-card").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const entry = entries[parseInt(btn.getAttribute("data-goblin-idx"), 10)];
                if (!entry) return;
                activeGameIdx = entry.gameIdx;
                activeSide = entry.side;
                await renderAll();
                const rowEl =
                    els.tableBody?.querySelector(`tr[data-hitter-id="${entry.row.id}"]`) ||
                    els.cardList?.querySelector(`.rs-card[data-hitter-id="${entry.row.id}"]`);
                rowEl?.scrollIntoView({ behavior: "smooth", block: "center" });
                rowEl?.classList.add("rs-row--flash");
                setTimeout(() => rowEl?.classList.remove("rs-row--flash"), 1800);
            });
        });
    }

    function topHittersForGame(gameIdx, limit = 3) {
        return collectSlateHitters()
            .filter((e) => e.gameIdx === gameIdx)
            .map((e) => ({ entry: e, score: hrTicketScore100(e) }))
            .filter((x) => x.score != null)
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    }

    function renderMatchupSummary() {
        if (!els.matchupSummary) return;
        const game = activeGame();
        if (!game) {
            els.matchupSummary.hidden = true;
            return;
        }
        const awayP = game.awayPitcher;
        const homeP = game.homePitcher;
        const awayRisk = pitcherStats(awayP).dingerRiskPct ?? pitcherStats(awayP).dingerRisk;
        const homeRisk = pitcherStats(homeP).dingerRiskPct ?? pitcherStats(homeP).dingerRisk;
        const park = game.parkHrPct != null ? fmtSignedPct(game.parkHrPct) : "—";
        const tops = topHittersForGame(activeGameIdx, 3);
        const topLine = tops.length
            ? tops.map((t) => `${t.entry.row.name} ${t.score}`).join(", ")
            : "—";
        els.matchupSummary.hidden = false;
        els.matchupSummary.innerHTML = `
            <div class="rs-matchup-summary__grid">
                <div class="rs-matchup-summary__item"><span class="rs-matchup-summary__label">${escAttr(game.away || "")} SP</span><span class="rs-matchup-summary__val">${escAttr(awayP?.name || "TBD")}${awayRisk != null ? ` · Risk ${Math.round(awayRisk)}%` : ""}</span></div>
                <div class="rs-matchup-summary__item"><span class="rs-matchup-summary__label">${escAttr(game.home || "")} SP</span><span class="rs-matchup-summary__val">${escAttr(homeP?.name || "TBD")}${homeRisk != null ? ` · Risk ${Math.round(homeRisk)}%` : ""}</span></div>
                <div class="rs-matchup-summary__item"><span class="rs-matchup-summary__label">Park</span><span class="rs-matchup-summary__val">${park}</span></div>
                <div class="rs-matchup-summary__item rs-matchup-summary__item--wide"><span class="rs-matchup-summary__label">Top targets</span><span class="rs-matchup-summary__val">${topLine}</span></div>
            </div>`;
    }

    function renderGames() {
        if (!els.games || !slate?.games) return;
        computePitcherScoresForSlate();
        rebuildTicketSlatePools();
        els.games.innerHTML = slate.games
            .map((g, i) => {
                const time = fmtTime(g.startTime);
                const sp = escAttr(`${g.awayPitcher?.name || "?"} vs ${g.homePitcher?.name || "?"}`);
                const nAway = (g.awayLineup || []).length;
                const nHome = (g.homeLineup || []).length;
                const tops = topHittersForGame(i, 1);
                const top = tops[0];
                const topBadge = top
                    ? `<span class="rs-game-pill__top">${escAttr(top.entry.row.name || "")} <strong>${top.score}</strong></span>`
                    : "";
                const awayRisk = pitcherStats(g.awayPitcher).dingerRiskPct;
                const homeRisk = pitcherStats(g.homePitcher).dingerRiskPct;
                const riskBadge =
                    awayRisk != null || homeRisk != null
                        ? `<span class="rs-game-pill__risk">${awayRisk != null ? `A ${Math.round(awayRisk)}%` : ""}${awayRisk != null && homeRisk != null ? " · " : ""}${homeRisk != null ? `H ${Math.round(homeRisk)}%` : ""}</span>`
                        : "";
                return `<button type="button" class="rs-game-pill${i === activeGameIdx ? " is-active" : ""}" data-idx="${i}">
                    <span class="rs-game-pill__matchup">${escAttr(g.matchup || "")}${weatherBadgeHtml(g)}</span>
                    <span class="rs-game-pill__meta">${time}${time ? " · " : ""}${g.lineupStatus || ""} · ${nAway}/${nHome} hitters</span>
                    <span class="rs-game-pill__meta">${sp}</span>
                    ${topBadge}${riskBadge}
                </button>`;
            })
            .join("");
        els.games.querySelectorAll(".rs-game-pill").forEach((btn) => {
            btn.addEventListener("click", async () => {
                activeGameIdx = parseInt(btn.getAttribute("data-idx"), 10);
                pickDefaultSide();
                await renderAll();
                const game = activeGame();
                if (game && !weatherIsComplete(game.parkWeather)) {
                    await ensureGameWeather(game);
                    renderWeatherPanel();
                    renderGames();
                    refreshHrEnvUi();
                }
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
            const season = seasonFromDate(slate?.sheet_date || els.dateInput?.value || "");
            const mixStatus = pitchMixStatusForSide(game, activeSide, season);
            const mix = pitcher?.arsenalLabel || formatArsenal(pitcher?.arsenal);
            const risk = fmtPitcherRisk(pitcher?.stats);
            let sp = pitcher?.name
                ? `vs ${pitcher.name}${mix ? ` · ${mix}` : ""}${risk ? ` · ${risk}` : ""}`
                : "vs TBD";
            if (!mixStatus.available && rows.length) {
                sp += ` · Mix% / Edge% unavailable — ${mixStatus.reason}`;
            }
            els.matchupSp.textContent = sp;
        }
        if (els.sideAway) {
            els.sideAway.textContent = game.away;
            els.sideAway.classList.toggle("is-active", activeSide === "away");
        }
        if (els.sideHome) {
            els.sideHome.textContent = game.home;
            els.sideHome.classList.toggle("is-active", activeSide === "home");
        }
        renderMatchupSummary();
    }

    function sortedActiveRows() {
        let rows = activeRows();
        const col = COLS.find((c) => c.key === sortKey);
        if (!col) return rows;
        if (sortKey === "hrEnv") {
            return [...rows].sort((a, b) => {
                const av = a?.hrProp?.propPass ? -Infinity : a?.hrProp?.combinedPct;
                const bv = b?.hrProp?.propPass ? -Infinity : b?.hrProp?.combinedPct;
                return sortDir * ((av == null ? -Infinity : Number(av)) - (bv == null ? -Infinity : Number(bv)));
            });
        }
        if (sortKey === "ticketScore") {
            return [...rows].sort((a, b) => {
                const ea = entryForActiveRow(a);
                const eb = entryForActiveRow(b);
                const av = ea ? hrTicketScore100(ea) : null;
                const bv = eb ? hrTicketScore100(eb) : null;
                return sortDir * ((av == null ? -Infinity : Number(av)) - (bv == null ? -Infinity : Number(bv)));
            });
        }
        return [...rows].sort((a, b) => {
            if (col.text) return sortDir * String(col.fmt(a)).localeCompare(String(col.fmt(b)));
            const av = col.stat ? hitterStats(a)[col.stat] : a[sortKey];
            const bv = col.stat ? hitterStats(b)[col.stat] : b[sortKey];
            return sortDir * ((av == null ? -Infinity : Number(av)) - (bv == null ? -Infinity : Number(bv)));
        });
    }

    function statHeatMap(rows, cols) {
        const statCols = (cols || COLS).filter((c) => c.stat || c.hrProp || c.ticket);
        const higherBetter = {
            ticketScore: true,
            hrEnv: true,
            mixPlus: true,
            mixEdge: true,
            matchWhiffPct: false,
            hr: true,
            expectedHr: true,
            hrLuckDiff: true,
            nearHr: true,
            avg: true,
            iso: true,
            slg: true,
            xwoba: true,
            barrelPct: true,
            hardHitPct: true,
            avgEV: true,
            launchAngle: true,
            sweetSpotPct: true,
            batSpeed: true,
            swingStrength: true,
            solidContactPct: true,
            blastPct: true,
            bipPct: true,
            fbPct: true,
            hrFbPct: true,
            hrFormPct: true,
            boomPct: true,
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
                    rows
                        .map((r) => {
                            if (c.ticket) {
                                const entry = entryForActiveRow(r);
                                const score = entry ? hrTicketScore100(entry) : null;
                                return score == null ? null : Number(score);
                            }
                            if (c.hrProp) {
                                return r?.hrProp?.propPass ? null : Number(r?.hrProp?.combinedPct);
                            }
                            return Number(hitterStats(r)[c.stat]);
                        })
                        .filter((n) => n != null && !Number.isNaN(n)),
                ])
            ),
            higherBetter,
        };
    }

    function syncMobileSortDir() {
        if (!els.mobileSortDir) return;
        els.mobileSortDir.textContent = sortDir > 0 ? "↓" : "↑";
        els.mobileSortDir.title = sortDir > 0 ? "High to low (tap to reverse)" : "Low to high (tap to reverse)";
        els.mobileSortDir.setAttribute("aria-label", sortDir > 0 ? "Sort high to low" : "Sort low to high");
    }

    function syncMobileSortSelect() {
        if (!els.mobileSort) return;
        const options = visibleCols()
            .filter((c) => c.key !== "order")
            .map((c) => {
                const selected = c.key === sortKey ? " selected" : "";
                return `<option value="${c.key}"${selected}>${c.label}</option>`;
            });
        els.mobileSort.innerHTML = options.join("");
        syncMobileSortDir();
    }

    function renderExploreLbCards(hitters) {
        if (!els.exploreLbCards) return;
        els.exploreLbCards.innerHTML = hitters.length
            ? hitters
                  .map((e, idx) => {
                      const score = hrTicketScore100(e);
                      const ticket = computeHrTicket(e);
                      return `<article class="rs-lb-card" data-id="${e.row.id}" data-game="${e.gameIdx}" data-side="${e.side}">
                        <div class="rs-lb-card__rank">${idx + 1}</div>
                        <div class="rs-lb-card__main">
                            <button type="button" class="rs-lb-card__name">${escAttr(e.row.name || "—")}</button>
                            <span class="rs-lb-card__meta">${escAttr(e.game.matchup || "")} · vs ${escAttr(e.pitcher?.name || "TBD")}</span>
                            <span class="rs-lb-card__pillars">${ticket?.pillarLine || ""}</span>
                        </div>
                        <div class="rs-lb-card__score">${fmtTicketBadge(score)}</div>
                    </article>`;
                  })
                  .join("")
            : `<p class="rs-empty">No hitters match these filters.</p>`;
        els.exploreLbCards.querySelectorAll(".rs-lb-card").forEach((card) => {
            card.querySelector(".rs-lb-card__name")?.addEventListener("click", () => {
                jumpToLeaderboardEntry(card);
            });
        });
    }

    async function jumpToLeaderboardEntry(el) {
        const id = Number(el.getAttribute("data-id"));
        const gi = Number(el.getAttribute("data-game"));
        const side = el.getAttribute("data-side");
        activeGameIdx = gi;
        activeSide = side;
        await renderAll();
        const entry = collectSlateHitters().find((e) => e.row.id === id && e.gameIdx === gi && e.side === side);
        const rowEl =
            els.tableBody?.querySelector(`tr[data-hitter-id="${id}"]`) ||
            els.cardList?.querySelector(`.rs-card[data-hitter-id="${id}"]`);
        rowEl?.scrollIntoView({ behavior: "smooth", block: "center" });
        rowEl?.classList.add("rs-row--flash");
        setTimeout(() => rowEl?.classList.remove("rs-row--flash"), 1800);
        if (entry) {
            document.querySelector(".rs-section-title--hitters")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    function mobileCardStatHtml(c, row, colValues, higherBetter) {
        if (c.ticket) {
            return `<div class="rs-card-stat"><dt>${c.label}</dt><dd>${c.fmt(row)}</dd></div>`;
        }
        if (c.hrProp) {
            const pct = row?.hrProp?.combinedPct;
            const heat = hrPropHeatClass(row);
            return `<div class="rs-card-stat"><dt>${c.label}</dt><dd><span class="${heat}">${c.fmt(row)}</span></dd></div>`;
        }
        const val = hitterStats(row)[c.stat];
        const heat =
            val != null ? heatClass(colValues[c.key], Number(val), higherBetter[c.key] !== false) : "";
        return `<div class="rs-card-stat"><dt>${c.label}</dt><dd><span class="${heat}">${c.fmt(row)}</span></dd></div>`;
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
        const highlightCols = MOBILE_HIGHLIGHT_KEYS.map((k) => COLS.find((c) => c.key === k)).filter(Boolean);
        const presetIds = presetIdsForViewRows(rows);
        els.cardList.innerHTML = rows
            .map((row) => {
                const projected = row.projected ? '<span class="rs-hand rs-hand--proj">proj</span>' : "";
                const highlights = highlightCols
                    .map((c) => {
                        if (c.ticket) {
                            return `<div class="rs-card-highlight rs-card-highlight--score">${c.fmt(row)}</div>`;
                        }
                        if (c.hrProp) {
                            const heat = hrPropHeatClass(row);
                            return `<div class="rs-card-highlight"><span class="rs-card-highlight__label">${c.label}</span><span class="rs-card-highlight__val ${heat}">${c.fmt(row)}</span></div>`;
                        }
                        const val = hitterStats(row)[c.stat];
                        const heat =
                            val != null
                                ? heatClass(colValues[c.key], Number(val), higherBetter[c.key] !== false)
                                : "";
                        return `<div class="rs-card-highlight"><span class="rs-card-highlight__label">${c.label}</span><span class="rs-card-highlight__val ${heat}">${c.fmt(row)}</span></div>`;
                    })
                    .join("");
                const sections = cardGroups
                    .map((group) => {
                        const cols = COLS.filter((c) => c.group === group.id && (c.stat || c.hrProp));
                        if (!cols.length) return "";
                        const stats = cols.map((c) => mobileCardStatHtml(c, row, colValues, higherBetter)).join("");
                        const openAttr = MOBILE_CARD_OPEN_GROUPS.has(group.id) ? " open" : "";
                        return `<details class="rs-card__section rs-card__section--${group.id}"${openAttr}><summary class="rs-card__section-title">${group.label}<span class="rs-card__section-chev" aria-hidden="true"></span></summary><dl class="rs-card__stats">${stats}</dl></details>`;
                    })
                    .join("");
                const presetCls = presetIds && presetIds.has(String(row.id)) ? " rs-card--preset" : "";
                return `<article class="rs-card${presetCls}" data-hitter-id="${row.id || ""}">
                    <header class="rs-card__head">
                        <span class="rs-card__order">${row.order ?? "—"}</span>
                        <div class="rs-card__identity">
                            <div class="rs-card__name"><button type="button" class="rs-hitter-btn rs-card__name-btn">${escAttr(row.name || "—")}</button> <span class="rs-hand">${escAttr(row.position || "")}</span>${projected}</div>
                            <div class="rs-card__meta">Bats ${row.hand || "—"}${(() => {
                                const entry = entryForActiveRow(row);
                                const ticket = entry ? computeHrTicket(entry) : null;
                                const line = ticket?.pillarLine;
                                return line ? ` · ${line}` : "";
                            })()}</div>
                        </div>
                    </header>
                    <div class="rs-card__highlights">${highlights}</div>
                    ${sections}
                </article>`;
            })
            .join("");
        els.cardList.querySelectorAll(".rs-card__name-btn").forEach((btn) => {
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                const card = btn.closest(".rs-card");
                const id = card?.getAttribute("data-hitter-id");
                const row = sortedActiveRows().find((r) => idsMatch(r.id, id));
                const entry = entryForActiveRow(row);
                if (entry) openPlayerProfile(entry);
            });
        });
        els.cardList.querySelectorAll(".rs-cell-heat--good, .rs-card-highlight__val.rs-cell-heat--good").forEach((el) => {
            el.style.background = "var(--rs-good-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(134, 239, 172, 0.35)";
        });
        els.cardList.querySelectorAll(".rs-cell-heat--mid, .rs-card-highlight__val.rs-cell-heat--mid").forEach((el) => {
            el.style.background = "var(--rs-mid-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(253, 224, 71, 0.25)";
        });
        els.cardList.querySelectorAll(".rs-cell-heat--bad, .rs-card-highlight__val.rs-cell-heat--bad").forEach((el) => {
            el.style.background = "var(--rs-bad-bg)";
            el.style.boxShadow = "inset 0 0 0 1px rgba(252, 165, 165, 0.25)";
        });
    }

    function wireColumnReorderHeaders() {
        if (!columnReorderMode || !els.tableHead) return;
        const headers = els.tableHead.querySelectorAll("tr.rs-col-row th[data-key]");
        headers.forEach((th) => {
            const key = th.getAttribute("data-key");
            if (!key || IDENTITY_COL_KEYS.has(key)) {
                th.classList.add("rs-col--fixed");
                return;
            }
            th.draggable = true;
            th.classList.add("rs-col--draggable");
            th.addEventListener("dragstart", (e) => {
                colDragKey = key;
                th.classList.add("rs-col--dragging");
                e.dataTransfer.effectAllowed = "move";
                e.dataTransfer.setData("text/plain", key);
                if (e.dataTransfer.setDragImage) {
                    e.dataTransfer.setDragImage(th, 12, 12);
                }
            });
            th.addEventListener("dragend", () => {
                colDragKey = null;
                th.classList.remove("rs-col--dragging");
                els.tableHead.querySelectorAll(".rs-col--drop-target").forEach((el) => {
                    el.classList.remove("rs-col--drop-target");
                });
            });
            th.addEventListener("dragover", (e) => {
                if (!colDragKey || colDragKey === key || IDENTITY_COL_KEYS.has(key)) return;
                e.preventDefault();
                e.dataTransfer.dropEffect = "move";
                headers.forEach((h) => h.classList.remove("rs-col--drop-target"));
                th.classList.add("rs-col--drop-target");
            });
            th.addEventListener("dragleave", () => {
                th.classList.remove("rs-col--drop-target");
            });
            th.addEventListener("drop", (e) => {
                e.preventDefault();
                const dragKey = e.dataTransfer.getData("text/plain") || colDragKey;
                th.classList.remove("rs-col--drop-target");
                if (!dragKey || dragKey === key) return;
                moveColumnKey(dragKey, key);
                renderTable();
            });
        });
    }

    function renderTable() {
        if (!els.tableHead || !els.tableBody) return;
        const cols = visibleCols();
        const rows = sortedActiveRows();
        const table = els.tableWrap?.querySelector(".rs-table");
        if (table) {
            table.classList.toggle("rs-table--essential", tableViewMode === "essential");
            table.classList.toggle("rs-table--full", tableViewMode === "full");
        }

        els.tableHead.innerHTML = buildTableHeadHtml(cols);

        if (columnReorderMode) {
            wireColumnReorderHeaders();
        } else {
            els.tableHead.querySelectorAll("tr.rs-col-row th").forEach((th) => {
                th.addEventListener("click", () => {
                    const key = th.getAttribute("data-key");
                    setSortColumn(key);
                    renderTable();
                    renderMobileCards();
                    syncMobileSortSelect();
                });
            });
        }

        if (!rows.length) {
            els.tableBody.innerHTML = `<tr><td colspan="${cols.length}" class="rs-empty">Loading hitters… try Refresh API or pick the other team.</td></tr>`;
            return;
        }

        const { colValues, higherBetter } = statHeatMap(rows, cols);
        const presetIds = presetIdsForViewRows(rows);
        if (table) table.classList.remove("rs-table--preset-dim");

        els.tableBody.innerHTML = rows
            .map((r) => {
                const cells = cols.map((c) => {
                    const colAttr = ` data-col-key="${c.key}"`;
                    if (c.key === "name") {
                        const tag = r.projected ? ' <span class="rs-hand">proj</span>' : "";
                        const tip = c.tip ? tipAttr(c.tip) : "";
                        return `<td${colAttr}${tip}><button type="button" class="rs-hitter rs-hitter-btn" data-hitter-id="${r.id || ""}">${r.name || "—"}</button> <span class="rs-hand">${r.position || ""}</span>${tag}</td>`;
                    }
                    if (c.ticket) {
                        const entry = entryForActiveRow(r);
                        const ticket = entry ? computeHrTicket(entry) : null;
                        const tipText = ticket?.pillars
                            ? `Mix ${Math.round(ticket.pillars.mix ?? 0)} · SP ${Math.round(ticket.pillars.pitcher ?? 0)} · Env ${Math.round(ticket.pillars.environment ?? 0)} · Form ${Math.round(ticket.pillars.form ?? 0)} · Power ${Math.round(ticket.pillars.power ?? 0)}`
                            : c.tip;
                        const tip = tipAttr(tipText || c.tip || "");
                        return `<td${colAttr}${tip}>${c.fmt(r)}</td>`;
                    }
                    if (c.hrProp) {
                        const tip = c.tip ? tipAttr(c.tip) : "";
                        return `<td${colAttr}${tip}><span class="${hrPropHeatClass(r)}">${c.fmt(r)}</span></td>`;
                    }
                    const val = c.stat ? hitterStats(r)[c.stat] : r[c.key];
                    const heat =
                        c.stat && val != null ? heatClass(colValues[c.key], Number(val), higherBetter[c.key] !== false) : "";
                    const mixTip = c.key.startsWith("mix") ? mixTipForRow(r) : null;
                    const tip = mixTip ? tipAttr(mixTip) : c.tip ? tipAttr(c.tip) : "";
                    return `<td${colAttr}${tip}><span class="${heat}">${c.fmt(r)}</span></td>`;
                }).join("");
                const presetCls = presetIds && presetIds.has(String(r.id)) ? ' class="rs-row--preset"' : "";
                return `<tr data-hitter-id="${r.id || ""}"${presetCls}>${cells}</tr>`;
            })
            .join("");

        scheduleHrFormHydrate(rows.map((r) => r.id).filter(Boolean));

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

        els.tableBody.querySelectorAll(".rs-hitter-btn").forEach((btn) => {
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                openHitterProfileFromDom(btn);
            });
        });
        els.tableBody.querySelectorAll("tr[data-hitter-id]").forEach((tr) => {
            tr.addEventListener("click", () => openHitterProfileFromDom(tr));
        });
    }

    function buildTableHeadHtml(cols) {
        const columns = cols || visibleCols();
        if (tableViewMode === "essential") {
            const colCells = columns.map((c) => {
                const sort =
                    c.key === sortKey ? (sortDir > 0 ? "ascending" : "descending") : "none";
                const tipAttrParts = c.tip ? ` data-tip="${escAttr(c.tip)}" tabindex="0"` : "";
                const tipClass = c.tip ? " rs-has-tip" : "";
                const sortedClass = c.key === sortKey ? " rs-col--sorted" : "";
                const sortLabel = sortIndicator(c.key);
                return `<th class="${tipClass}${sortedClass}" data-key="${c.key}" data-col-key="${c.key}" aria-sort="${sort}"${tipAttrParts}>${c.label}${sortLabel}</th>`;
            }).join("");
            return `<tr class="rs-col-row rs-col-row--essential">${colCells}</tr>`;
        }
        const colCells = columns.map((c) => {
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
            const tipAttrParts = c.tip
                ? ` data-tip="${escAttr(c.tip)}" tabindex="0"`
                : "";
            const tipClass = c.tip ? " rs-has-tip" : "";
            const sortedClass = c.key === sortKey ? " rs-col--sorted" : "";
            const reorderClass =
                columnReorderMode && !IDENTITY_COL_KEYS.has(c.key) ? " rs-col--draggable" : "";
            const fixedClass = columnReorderMode && IDENTITY_COL_KEYS.has(c.key) ? " rs-col--fixed" : "";
            const dragHandle =
                columnReorderMode && !IDENTITY_COL_KEYS.has(c.key)
                    ? '<span class="rs-col-drag" aria-hidden="true">⋮⋮</span>'
                    : "";
            const sortLabel = columnReorderMode ? "" : sortIndicator(c.key);
            return `<th class="${colClass.trim()}${tipClass}${sortedClass}${reorderClass}${fixedClass}" data-key="${c.key}" data-col-key="${c.key}" aria-sort="${sort}"${tipAttrParts}>${dragHandle}${colDisplayLabel(c)}${sortLabel}</th>`;
        }).join("");
        return `<tr class="rs-col-row">${colCells}</tr>`;
    }

    function savantPlayerUrl(row, season) {
        const id = row?.id;
        if (!id) return null;
        const slug = String(row.name || "player")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
        return `https://baseballsavant.mlb.com/savant-player/${slug}-${id}?season=${season || 2026}`;
    }

    function savantPitcherUrl(pitcher, season) {
        const id = pitcher?.id;
        if (!id) return null;
        const slug = String(pitcher.name || "pitcher")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
        return `https://baseballsavant.mlb.com/savant-player/${slug}-${id}?season=${season || 2026}`;
    }

    function collectSlateHitters() {
        const out = [];
        for (let gi = 0; gi < (slate?.games || []).length; gi += 1) {
            const game = slate.games[gi];
            for (const side of ["away", "home"]) {
                const offense = side === "away" ? game.away : game.home;
                const pitcher = side === "away" ? game.homePitcher : game.awayPitcher;
                const lineup = side === "away" ? game.awayLineup : game.homeLineup;
                for (const row of lineup || []) {
                    if (!row?.name) continue;
                    out.push({
                        row,
                        game,
                        gameIdx: gi,
                        side,
                        team: offense,
                        pitcher,
                        hrProp: row.hrProp,
                    });
                }
            }
        }
        return out;
    }

    function collectSlatePitchers() {
        const out = [];
        for (let gi = 0; gi < (slate?.games || []).length; gi += 1) {
            const game = slate.games[gi];
            for (const side of ["away", "home"]) {
                const pitcher = side === "away" ? game.awayPitcher : game.homePitcher;
                if (!pitcher?.name) continue;
                out.push({
                    pitcher,
                    game,
                    gameIdx: gi,
                    side,
                    team: side === "away" ? game.away : game.home,
                });
            }
        }
        return out;
    }

    function hrEnvScore(entry) {
        const prop = entry?.hrProp || entry?.row?.hrProp;
        const game = entry?.game;
        if (prop?.propPass || game?.propPass) return null;
        const pct = prop?.combinedPct;
        return pct == null || Number.isNaN(Number(pct)) ? null : Number(pct);
    }

    function exploreSortValue(entry, key) {
        if (key === "ticketRank") return hrTicketScore100(entry);
        if (key === "hrEnv") return hrEnvScore(entry);
        const stats = hitterStats(entry.row);
        const val = stats[key];
        return val == null || Number.isNaN(Number(val)) ? null : Number(val);
    }

    function filteredExploreHitters() {
        const hand = els.exploreHand?.value || "";
        const sortKey = exploreSortKey || els.exploreSort?.value || "ticketRank";
        let rows = collectSlateHitters();
        if (hand) rows = rows.filter((e) => (e.row.hand || "").toUpperCase() === hand);
        const minScore = els.exploreMinScore?.value;
        if (minScore !== "" && minScore != null) {
            const min = Number(minScore);
            if (!Number.isNaN(min)) {
                rows = rows.filter((e) => (hrTicketScore100(e) ?? -1) >= min);
            }
        }
        const minPark = els.exploreMinPark?.value;
        if (minPark !== "" && minPark != null) {
            const min = Number(minPark);
            if (!Number.isNaN(min)) {
                rows = rows.filter((e) => {
                    const p = computeHrTicket(e)?.parkPct;
                    return p != null && p >= min;
                });
            }
        }
        rows.sort((a, b) => {
            const av = exploreTicketField(a, sortKey);
            const bv = exploreTicketField(b, sortKey);
            if (av == null && bv == null) return (a.row.name || "").localeCompare(b.row.name || "");
            if (av == null) return 1;
            if (bv == null) return -1;
            const cmp = Number(bv) - Number(av);
            if (sortKey === "matchWhiffPct") return -cmp;
            return cmp;
        });
        return rows;
    }

    function profileStatCell(label, value, tone) {
        const cls = tone ? ` rs-profile-stat--${tone}` : "";
        return `<div class="rs-profile-stat${cls}"><dt>${label}</dt><dd>${value}</dd></div>`;
    }

    function mlbHeadshotUrl(playerId) {
        if (!playerId) return "";
        return `https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${playerId}/headshot/67/current`;
    }

    function powerMetricTone(key, val) {
        if (val == null || Number.isNaN(Number(val))) return null;
        const n = Number(val);
        if (key === "hrLuckDiff") return n >= 1 ? "good" : n <= -1 ? "bad" : "mid";
        if (key === "hrFormPct") return n >= 66 ? "good" : n <= 33 ? "bad" : "mid";
        if (key === "boomPct") return n >= 66 ? "good" : n <= 33 ? "bad" : "mid";
        if (key === "recentForm" || key === "mixPlus" || key === "mixEdge") {
            if (n >= 5) return "good";
            if (n <= -5) return "bad";
            return "mid";
        }
        if (key === "barrelPct") return n >= 12 ? "good" : n >= 8 ? "mid" : "bad";
        if (key === "hardHitPct") return n >= 45 ? "good" : n >= 38 ? "mid" : "bad";
        if (key === "avgEV") return n >= 92 ? "good" : n >= 88 ? "mid" : "bad";
        if (key === "hrFbPct") return n >= 25 ? "good" : n >= 15 ? "mid" : "bad";
        if (key === "pullPct") return n >= 40 ? "good" : "mid";
        if (key === "sweetSpotPct") return n >= 35 ? "good" : "mid";
        if (key === "fbPct") return n >= 40 ? "good" : "mid";
        if (key === "gbPct") return n <= 35 ? "good" : n >= 45 ? "bad" : "mid";
        if (key === "launchAngle") return n >= 12 && n <= 28 ? "good" : "mid";
        return null;
    }

    function profileBlockSection(title, innerHtml) {
        return `<section class="rs-profile-block"><h3 class="rs-profile-block__title">${title}</h3>${innerHtml}</section>`;
    }

    function renderSparkline(values, { strokeClass = "rs-sparkline__line--barrel", width = 160, height = 44 } = {}) {
        const nums = (values || []).filter((v) => v != null && !Number.isNaN(Number(v))).map(Number);
        if (nums.length < 2) return `<span class="rs-profile-trends--loading">Not enough games</span>`;
        const min = Math.min(...nums);
        const max = Math.max(...nums);
        const range = max - min || 1;
        const pad = 4;
        const pts = nums.map((v, i) => {
            const x = pad + (i / (nums.length - 1)) * (width - pad * 2);
            const y = height - pad - ((v - min) / range) * (height - pad * 2);
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        });
        const last = pts[pts.length - 1].split(",");
        return `<svg class="rs-sparkline" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-hidden="true"><polyline class="rs-sparkline__line ${strokeClass}" points="${pts.join(" ")}"/><circle class="rs-sparkline__dot ${strokeClass}" cx="${last[0]}" cy="${last[1]}" r="2.5"/></svg>`;
    }

    // Trends proxies only exist on the local dev server. Requests fire in
    // parallel bursts, so probe each proxy once and gate every request behind
    // that probe — otherwise the live site spams dozens of 404s per load.
    const proxyProbes = new Map();

    async function proxyAvailable(path) {
        if (isFileProtocol()) return false;
        if (!proxyProbes.has(path)) {
            proxyProbes.set(
                path,
                (async () => {
                    try {
                        const res = await fetch(`${window.location.origin}${path}`);
                        return res.status !== 404;
                    } catch {
                        return false;
                    }
                })()
            );
        }
        return proxyProbes.get(path);
    }

    async function fetchPlayerTrends(playerId, season) {
        const key = `${playerId}:${season}`;
        if (trendsCache.has(key)) return trendsCache.get(key);
        const base = (await proxyAvailable("/api/player-trends?playerId=660271&season=2026&limit=1"))
            ? `${window.location.origin}/api/player-trends`
            : null;
        if (base) {
            try {
                const res = await fetch(`${base}?playerId=${encodeURIComponent(playerId)}&season=${encodeURIComponent(season)}&limit=30`);
                if (res.ok) {
                    const data = await res.json();
                    const games = Array.isArray(data.games) ? data.games : [];
                    if (games.length) {
                        trendsCache.set(key, games);
                        return games;
                    }
                }
            } catch (err) {
                console.warn("player trends proxy", err);
            }
        }
        try {
            const res = await fetch(
                `${MLB_API}/people/${encodeURIComponent(playerId)}/stats?stats=gameLog&group=hitting&season=${encodeURIComponent(season)}`
            );
            if (!res.ok) return [];
            const data = await res.json();
            const splits = data?.stats?.[0]?.splits || [];
            const games = splits.slice(-30).map((split) => {
                const st = split.stat || {};
                const avg = parseFloat(String(st.avg || "").replace(/^\./, "0.")) || null;
                const slg = parseFloat(String(st.slg || "").replace(/^\./, "0.")) || null;
                return {
                    date: (split.date || "").slice(0, 10),
                    pa: st.plateAppearances != null ? Number(st.plateAppearances) : null,
                    hr: st.homeRuns != null ? Number(st.homeRuns) : null,
                    slg,
                    iso: avg != null && slg != null ? Math.round((slg - avg) * 1000) / 1000 : null,
                };
            });
            trendsCache.set(key, games);
            return games;
        } catch (err) {
            console.warn("player trends mlb", err);
            return [];
        }
    }

    function summarizeTrendGames(games, days) {
        const slice = (games || []).slice(-days);
        let hr = 0;
        let pa = 0;
        let slgSum = 0;
        let slgN = 0;
        slice.forEach((g) => {
            hr += Number(g.hr) || 0;
            pa += Number(g.pa) || 0;
            if (g.slg != null) {
                slgSum += Number(g.slg);
                slgN += 1;
            }
        });
        const avgSlg = slgN ? Math.round((slgSum / slgN) * 1000) / 1000 : null;
        return { hr, pa, avgSlg, games: slice.length };
    }

    function renderProfileTrendsHtml(games, seasonStats) {
        if (!games.length) {
            return `<div class="rs-profile-trends rs-profile-trends--loading">Trend data unavailable — check your connection or restart <code>serve-research.py</code>.</div>`;
        }
        const last7 = summarizeTrendGames(games, 7);
        const last14 = summarizeTrendGames(games, 14);
        const hrSeries = games.map((g) => g.hr).filter((v) => v != null);
        const slgSeries = games.map((g) => (g.slg != null ? g.slg * 1000 : null)).filter((v) => v != null);
        const estBarrels =
            seasonStats?.barrelPct != null && last7.pa
                ? Math.round((Number(seasonStats.barrelPct) / 100) * last7.pa)
                : null;
        const summary = `Last 7 games: <strong>${last7.hr} HR</strong>${estBarrels != null ? `, ~<strong>${estBarrels} barrels</strong> (season rate)` : ""}${last7.avgSlg != null ? `, <strong>${last7.avgSlg.toFixed(3)} SLG</strong>` : ""}. Last 14: ${last14.hr} HR${last14.avgSlg != null ? ` · ${last14.avgSlg.toFixed(3)} SLG` : ""}.`;
        const lastHr = hrSeries.length ? hrSeries[hrSeries.length - 1] : null;
        const lastSlg = slgSeries.length ? slgSeries[slgSeries.length - 1] / 1000 : null;
        return `<div class="rs-profile-trends"><h3 class="rs-profile-block__title">Recent form &amp; trends</h3><p class="rs-profile-trends__summary">${summary}</p><div class="rs-profile-trends__charts"><div class="rs-profile-trend"><p class="rs-profile-trend__label">HR per game · last ${hrSeries.length}</p><p class="rs-profile-trend__value">${lastHr != null ? `${lastHr} HR latest` : "—"}</p>${renderSparkline(hrSeries, { strokeClass: "rs-sparkline__line--barrel" })}</div><div class="rs-profile-trend"><p class="rs-profile-trend__label">SLG by game · last ${slgSeries.length}</p><p class="rs-profile-trend__value">${lastSlg != null ? `${lastSlg.toFixed(3)} latest` : "—"}</p>${renderSparkline(slgSeries, { strokeClass: "rs-sparkline__line--ev" })}</div></div></div>`;
    }

    async function loadProfileTrends(playerId, season, seasonStats) {
        if (!els.profileTrends || !playerId) return;
        const gen = ++profileTrendsGen;
        els.profileTrends.hidden = false;
        els.profileTrends.innerHTML = `<div class="rs-profile-trends rs-profile-trends--loading">Loading recent trends…</div>`;
        const games = await fetchPlayerTrends(playerId, season);
        if (gen !== profileTrendsGen) return;
        els.profileTrends.innerHTML = renderProfileTrendsHtml(games, seasonStats);
    }

    async function fetchPitcherTrends(playerId, season) {
        const key = `${playerId}:${season}`;
        if (pitcherTrendsCache.has(key)) return pitcherTrendsCache.get(key);
        const base = (await proxyAvailable("/api/pitcher-trends?playerId=543037&season=2026&limit=1"))
            ? `${window.location.origin}/api/pitcher-trends`
            : null;
        if (base) {
            try {
                const res = await fetch(`${base}?playerId=${encodeURIComponent(playerId)}&season=${encodeURIComponent(season)}&limit=30`);
                if (res.ok) {
                    const data = await res.json();
                    const games = Array.isArray(data.games) ? data.games : [];
                    if (games.length) {
                        pitcherTrendsCache.set(key, games);
                        return games;
                    }
                }
            } catch (err) {
                console.warn("pitcher trends proxy", err);
            }
        }
        try {
            const res = await fetch(
                `${MLB_API}/people/${encodeURIComponent(playerId)}/stats?stats=gameLog&group=pitching&season=${encodeURIComponent(season)}`
            );
            if (!res.ok) return [];
            const data = await res.json();
            const splits = data?.stats?.[0]?.splits || [];
            const games = splits.slice(-30).map((split) => {
                const st = split.stat || {};
                const ipStr = String(st.inningsPitched || "").trim();
                let ip = null;
                if (ipStr && ipStr !== "-") {
                    const parts = ipStr.split(".");
                    const whole = parseInt(parts[0], 10) || 0;
                    const frac = parseInt(parts[1], 10) || 0;
                    ip = Math.round((whole + frac / 3) * 100) / 100;
                }
                return {
                    date: (split.date || "").slice(0, 10),
                    ip,
                    k: st.strikeOuts != null ? Number(st.strikeOuts) : null,
                    hr: st.homeRuns != null ? Number(st.homeRuns) : null,
                    bf: st.battersFaced != null ? Number(st.battersFaced) : null,
                    er: st.earnedRuns != null ? Number(st.earnedRuns) : null,
                };
            });
            pitcherTrendsCache.set(key, games);
            return games;
        } catch (err) {
            console.warn("pitcher trends mlb", err);
            return [];
        }
    }

    function summarizePitcherStarts(games, n) {
        const slice = (games || []).slice(-n);
        let hr = 0;
        let ip = 0;
        let er = 0;
        slice.forEach((g) => {
            hr += Number(g.hr) || 0;
            ip += Number(g.ip) || 0;
            er += Number(g.er) || 0;
        });
        return { hr, ip: Math.round(ip * 10) / 10, er, starts: slice.length };
    }

    function renderPitcherTrendsHtml(games) {
        if (!games.length) {
            return `<div class="rs-profile-trends rs-profile-trends--loading">Start log unavailable — check connection or restart <code>serve-research.py</code>.</div>`;
        }
        const last7 = summarizePitcherStarts(games, 7);
        const last14 = summarizePitcherStarts(games, 14);
        const hrSeries = games.map((g) => g.hr).filter((v) => v != null);
        const erSeries = games.map((g) => g.er).filter((v) => v != null);
        const summary = `Last 7 starts: <strong>${last7.hr} HR</strong> allowed, <strong>${last7.er} ER</strong> in ${last7.ip} IP. Last 14: ${last14.hr} HR · ${last14.er} ER.`;
        const lastHr = hrSeries.length ? hrSeries[hrSeries.length - 1] : null;
        const lastEr = erSeries.length ? erSeries[erSeries.length - 1] : null;
        return `<div class="rs-profile-trends"><h3 class="rs-profile-block__title">Recent starts</h3><p class="rs-profile-trends__summary">${summary}</p><div class="rs-profile-trends__charts"><div class="rs-profile-trend"><p class="rs-profile-trend__label">HR allowed · last ${hrSeries.length} starts</p><p class="rs-profile-trend__value">${lastHr != null ? `${lastHr} HR latest` : "—"}</p>${renderSparkline(hrSeries, { strokeClass: "rs-sparkline__line--barrel" })}</div><div class="rs-profile-trend"><p class="rs-profile-trend__label">ER by start · last ${erSeries.length}</p><p class="rs-profile-trend__value">${lastEr != null ? `${lastEr} ER latest` : "—"}</p>${renderSparkline(erSeries, { strokeClass: "rs-sparkline__line--ev" })}</div></div></div>`;
    }

    async function loadPitcherProfileTrends(playerId, season) {
        if (!els.profileTrends || !playerId) return;
        const gen = ++pitcherTrendsGen;
        els.profileTrends.hidden = false;
        els.profileTrends.innerHTML = `<div class="rs-profile-trends rs-profile-trends--loading">Loading recent starts…</div>`;
        const games = await fetchPitcherTrends(playerId, season);
        if (gen !== pitcherTrendsGen) return;
        els.profileTrends.innerHTML = renderPitcherTrendsHtml(games);
    }

    function renderProfileHeader(row, opts = {}) {
        const { team, game, player } = opts;
        const id = row?.id || player?.id;
        const name = row?.name || player?.name || "—";
        const hand = row?.hand || player?.hand || "—";
        const position = row?.position || player?.position || "—";
        const order = row?.order;
        const teamLabel = team || player?.team || "—";
        if (els.profileName) els.profileName.textContent = name;
        if (els.profileSub) {
            const parts = [teamLabel, position !== "—" ? position : null, `Bats ${hand}`, order != null ? `#${order} lineup` : null].filter(Boolean);
            els.profileSub.textContent = parts.join(" · ");
        }
        if (els.profilePhoto) {
            if (id) {
                els.profilePhoto.src = mlbHeadshotUrl(id);
                els.profilePhoto.alt = name;
                els.profilePhoto.hidden = false;
                els.profilePhoto.onerror = () => {
                    els.profilePhoto.hidden = true;
                };
            } else {
                els.profilePhoto.hidden = true;
            }
        }
        if (els.profileGame) {
            if (game) {
                const time = fmtTime(game.startTime);
                const date = slate?.sheet_date || sheetDateFromQuery() || "";
                els.profileGame.textContent = [game.matchup, time || date].filter(Boolean).join("\n");
            } else {
                els.profileGame.textContent = `${player?.team || "2026 season"} · league search`;
            }
        }
    }

    function renderProfileHeroHrEnv(row, game, prop, entry) {
        if (!els.profileHero) return;
        const ticket = entry ? computeHrTicket(entry) : null;
        const score = entry ? hrTicketScore100(entry) : null;
        const ticketBlock =
            score != null
                ? `<div class="rs-profile-hero rs-profile-hero--ticket rs-profile-hero--${ticketScoreTone(score)}"><span class="rs-profile-hero__label">HR ticket</span><span class="rs-profile-hero__value">${fmtTicketBadge(score)}</span><span class="rs-profile-hero__sub">${ticket?.pillarLine || "Slate-relative HR target score."}</span></div>`
                : "";
        if (prop.propPass || game?.propPass) {
            els.profileHero.innerHTML =
                ticketBlock +
                `<div class="rs-profile-hero rs-profile-hero--pass"><span class="rs-profile-hero__label">HR environment</span><span class="rs-profile-hero__value rs-profile-hero__value--pass">PASS</span><span class="rs-profile-hero__sub">Roof or weather data unreliable — skip HR props here.</span></div>`;
            return;
        }
        const env = fmtHrPropPct(row, game);
        const tone = edgeTone(prop.combinedPct);
        els.profileHero.innerHTML =
            ticketBlock +
            `<div class="rs-profile-hero rs-profile-hero--${tone}"><span class="rs-profile-hero__label">HR environment</span><span class="rs-profile-hero__value">${env}</span><span class="rs-profile-hero__sub">Park + weather + wind + dimensions × pitcher vulnerability for ${prop.hand || row.hand || "—"} bat path.</span></div>`;
    }

    function buildProfilePowerBlock(stats, title = "Power profile", row = null) {
        const top = [
            profileStatCell("HR", fmtNum(stats.hr)),
            profileStatCell("xHR", fmtXhr(stats.expectedHr)),
            profileStatCell("Due+", fmtLuck(stats.hrLuckDiff), powerMetricTone("hrLuckDiff", stats.hrLuckDiff)),
            profileStatCell("Barrel%", fmtPct(stats.barrelPct), powerMetricTone("barrelPct", stats.barrelPct)),
            profileStatCell("Hard-hit%", fmtPct(stats.hardHitPct), powerMetricTone("hardHitPct", stats.hardHitPct)),
            profileStatCell("EV", fmtEv(stats.avgEV), powerMetricTone("avgEV", stats.avgEV)),
        ];
        const bottom = [
            profileStatCell("HR/FB%", fmtPct(stats.hrFbPct), powerMetricTone("hrFbPct", stats.hrFbPct)),
            profileStatCell("Pull%", fmtPct(stats.pullPct), powerMetricTone("pullPct", stats.pullPct)),
            profileStatCell("Sweet%", fmtPct(stats.sweetSpotPct), powerMetricTone("sweetSpotPct", stats.sweetSpotPct)),
            profileStatCell("HR Form%", fmtHrFormWithTrend(stats.hrFormPct, row ? formTrendForRow(row) : null), powerMetricTone("hrFormPct", stats.hrFormPct)),
            profileStatCell("Boom%", fmtBoomWithTrend(stats.boomPct, row ? boomTrendForRow(row) : null), powerMetricTone("boomPct", stats.boomPct)),
        ];
        return profileBlockSection(
            title,
            `<div class="rs-profile-block__grid rs-profile-block__grid--power-top">${top.join("")}</div><div class="rs-profile-block__grid rs-profile-block__grid--power-bottom">${bottom.join("")}</div>`
        );
    }

    function buildProfileBattedBlock(stats) {
        const cells = [
            profileStatCell("FB%", fmtPct(stats.fbPct), powerMetricTone("fbPct", stats.fbPct)),
            profileStatCell("Air%", fmtPct(stats.airPct), powerMetricTone("fbPct", stats.airPct)),
            profileStatCell("GB%", fmtPct(stats.gbPct), powerMetricTone("gbPct", stats.gbPct)),
            profileStatCell("LD%", fmtPct(stats.ldPct)),
            profileStatCell("LA", fmtAngle(stats.launchAngle), powerMetricTone("launchAngle", stats.launchAngle)),
            profileStatCell("Pull%", fmtPct(stats.pullPct), powerMetricTone("pullPct", stats.pullPct)),
            profileStatCell("Sweet%", fmtPct(stats.sweetSpotPct), powerMetricTone("sweetSpotPct", stats.sweetSpotPct)),
        ];
        return profileBlockSection("Batted-ball profile", `<div class="rs-profile-block__grid">${cells.join("")}</div>`);
    }

    function buildProfileGridHtml(stats, pitcher, prop, game, row, { showHrEnv = true } = {}) {
        const pstats = pitcherStats(pitcher);
        const blocks = [];
        if (showHrEnv && !(prop.propPass || game?.propPass)) {
            const envCells = [
                profileStatCell("Stadium", fmtSignedPct(multToPct(prop.stadiumMult)), edgeTone(multToPct(prop.stadiumMult))),
                profileStatCell("Weather", fmtSignedPct(multToPct(prop.weatherMult)), edgeTone(multToPct(prop.weatherMult))),
                profileStatCell("Wind", fmtSignedPct(multToPct(prop.windMult)), edgeTone(multToPct(prop.windMult))),
                profileStatCell("Dimensions", fmtSignedPct(multToPct(prop.dimMult)), edgeTone(multToPct(prop.dimMult))),
                profileStatCell("Pitcher", fmtSignedPct(multToPct(prop.pitcherMult)), edgeTone(multToPct(prop.pitcherMult))),
            ];
            blocks.push(
                profileBlockSection(
                    "HR environment breakdown",
                    `<div class="rs-profile-block__grid rs-profile-block__grid--breakdown">${envCells.join("")}</div>`
                )
            );
        }
        blocks.push(buildProfilePowerBlock(stats, showHrEnv ? "Power profile" : "Power profile (2026)", row));
        blocks.push(buildProfileBattedBlock(stats));
        blocks.push(
            profileBlockSection(
                "Matchup & contact",
                `<div class="rs-profile-block__grid">${[
                    profileStatCell("Mix%", fmtFormPct(stats.mixPlus), powerMetricTone("mixPlus", stats.mixPlus)),
                    profileStatCell("Edge%", fmtFormPct(stats.mixEdge), powerMetricTone("mixEdge", stats.mixEdge)),
                    profileStatCell("xwOBA", fmtRate(stats.xwoba)),
                    profileStatCell("ISO", fmtRate(stats.iso)),
                    profileStatCell("Whiff%", fmtPct(stats.whiffPct)),
                    profileStatCell("K%", fmtPct(stats.kPct)),
                ].join("")}</div>`
            )
        );
        if (pitcher?.name) {
            const matchCells =
                stats.matchPitches != null || stats.matchWhiffPct != null
                    ? [
                          ...(stats.matchPitches != null
                              ? [profileStatCell("Match pitches", String(stats.matchPitches))]
                              : []),
                          ...(stats.matchXwoba != null ? [profileStatCell("Match xwOBA", fmtRate(stats.matchXwoba))] : []),
                          ...(stats.matchWhiffPct != null
                              ? [profileStatCell("Match SwM%", fmtPct(stats.matchWhiffPct))]
                              : []),
                      ]
                    : [];
            blocks.push(
                profileBlockSection(
                    `vs ${escAttr(pitcher.name || "SP")}`,
                    `<div class="rs-profile-block__grid">${[
                        ...matchCells,
                        profileStatCell("Dinger risk", pstats.dingerRiskPct != null ? `${pstats.dingerRiskPct}%` : "—"),
                        profileStatCell("vs LHB", pstats.dingerRiskLhbPct != null ? `${pstats.dingerRiskLhbPct}%` : "—"),
                        profileStatCell("vs RHB", pstats.dingerRiskRhbPct != null ? `${pstats.dingerRiskRhbPct}%` : "—"),
                        profileStatCell("Barrel% allowed", fmtPct(pstats.barrelPct)),
                        profileStatCell("HR/9", pstats.hr9 != null ? Number(pstats.hr9).toFixed(2) : "—"),
                    ].join("")}</div>`
                )
            );
        }
        return blocks.join("");
    }

    function loadBetTrackerEntries() {
        try {
            const raw = localStorage.getItem(BET_TRACKER_LS);
            const arr = raw ? JSON.parse(raw) : [];
            return Array.isArray(arr) ? arr : [];
        } catch (e) {
            return [];
        }
    }

    function persistBetTrackerEntries(entries) {
        try {
            localStorage.setItem(BET_TRACKER_LS, JSON.stringify(entries));
        } catch (e) {
            console.warn("bet tracker persist", e);
        }
    }

    function findResearchTrackerEntry(playerId, sheetDate) {
        if (!playerId) return null;
        return loadBetTrackerEntries().find(
            (e) => e.source === "research" && e.playerId === playerId && (e.sheetDate || "") === (sheetDate || "")
        );
    }

    function syncProfileTrackerBtn(entry) {
        if (!els.profileTracker) return;
        if (!entry) {
            els.profileTracker.hidden = true;
            return;
        }
        els.profileTracker.hidden = false;
        const sd = slate?.sheet_date || sheetDateFromQuery() || "";
        const tracked = !!findResearchTrackerEntry(entry.row?.id, sd);
        els.profileTracker.textContent = tracked ? "Saved to tracker ✓" : "Add to tracker";
        els.profileTracker.classList.toggle("is-on", tracked);
    }

    function showProfileToast(msg) {
        let toast = document.getElementById("rsProfileToast");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "rsProfileToast";
            toast.className = "rs-profile-toast";
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.classList.add("is-visible");
        clearTimeout(profileToastTimer);
        profileToastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2200);
    }

    function toggleProfileTracker() {
        if (!profileEntry?.row) return;
        const { row, game, team } = profileEntry;
        const sd = slate?.sheet_date || sheetDateFromQuery() || "";
        const entries = loadBetTrackerEntries();
        const existingIdx = entries.findIndex(
            (e) => e.source === "research" && e.playerId === row.id && (e.sheetDate || "") === sd
        );
        if (existingIdx >= 0) {
            entries.splice(existingIdx, 1);
            persistBetTrackerEntries(entries);
            syncProfileTrackerBtn(profileEntry);
            showProfileToast("Removed from bet tracker");
            return;
        }
        const ticket = computeHrTicket(profileEntry);
        const env = row.hrProp?.combinedPct;
        entries.push({
            id: `rs-${Date.now()}-${row.id}`,
            createdAt: new Date().toISOString(),
            sheetDate: sd,
            gi: null,
            ri: null,
            playerId: row.id,
            name: `${row.name}${row.hand ? ` (${row.hand})` : ""}`,
            line: "Research — O0.5 HR",
            matchup: game?.matchup || "",
            score: hrTicketScore100(profileEntry) ?? (env != null ? Math.round(env) : null),
            units: 1,
            americanOdds: null,
            result: null,
            notes: team ? `Research tab · ${team}` : "Research tab",
            source: "research",
        });
        persistBetTrackerEntries(entries);
        syncProfileTrackerBtn(profileEntry);
        showProfileToast("Added to bet tracker — open the cheat sheet to view");
    }

    function wireProfileSavant(row, season) {
        const savUrl = savantPlayerUrl(row, season);
        if (!els.profileSavant) return;
        if (savUrl) {
            els.profileSavant.href = savUrl;
            els.profileSavant.hidden = false;
        } else {
            els.profileSavant.hidden = true;
        }
    }

    function wirePitcherProfileSavant(pitcher, season) {
        const savUrl = savantPitcherUrl(pitcher, season);
        if (!els.profileSavant) return;
        if (savUrl) {
            els.profileSavant.href = savUrl;
            els.profileSavant.hidden = false;
        } else {
            els.profileSavant.hidden = true;
        }
    }

    function renderPitcherProfileHeader(pitcher, { team, game }) {
        if (els.profileName) els.profileName.textContent = pitcher?.name || "—";
        if (els.profileSub) {
            const parts = [team, fmtPitcherHand(pitcher, team), pitcher?.arsenalLabel].filter(Boolean);
            els.profileSub.textContent = parts.join(" · ");
        }
        if (els.profilePhoto) els.profilePhoto.hidden = true;
        if (els.profileGame) {
            const time = fmtTime(game?.startTime);
            const date = slate?.sheet_date || sheetDateFromQuery() || "";
            els.profileGame.textContent = [game?.matchup, time || date].filter(Boolean).join("\n");
        }
    }

    function renderPitcherProfileHero(stats) {
        if (!els.profileHero) return;
        const pct = stats.dingerRiskPct ?? stats.dingerRisk;
        const tone = dingerRiskTone(pct);
        const sub = fmtPitcherRisk(stats) || "Savant season contact allowed profile.";
        els.profileHero.innerHTML = `<div class="rs-profile-hero rs-profile-hero--${tone}"><span class="rs-profile-hero__label">Dinger risk</span><span class="rs-profile-hero__value">${pct != null ? `${Math.round(Number(pct))}%` : "—"}</span><span class="rs-profile-hero__sub">${sub}</span></div>`;
    }

    function buildPitcherProfileGridHtml(pitcher, stats, statsList) {
        const blocks = [];
        blocks.push(
            profileBlockSection("HR contact leak (season)", renderPitcherLeakGrid(stats, statsList))
        );
        blocks.push(profileBlockSection("Handedness splits", renderPitcherHandSplitsTable(pitcher, stats)));
        blocks.push(profileBlockSection("Pitch arsenal", renderPitcherArsenalHtml(pitcher)));
        const command = PITCHER_METRICS.filter((m) => m.group === "command");
        const cmdCells = command.map((m) => pitcherStatCellHtml(m, stats, statsList)).join("");
        blocks.push(profileBlockSection("Command & outcomes", `<div class="rs-pitcher-group__grid">${cmdCells}</div>`));
        blocks.push(
            profileBlockSection("K / Strikeout", renderPitcherKTabHtml(stats, statsList))
        );
        return blocks.join("");
    }

    function openPitcherProfile(entry) {
        if (!entry || !els.playerProfile) return;
        profileEntry = null;
        profilePitcherEntry = entry;
        if (els.profileJump) els.profileJump.hidden = false;
        if (els.profileTracker) els.profileTracker.hidden = true;
        const { pitcher, game, team } = entry;
        const season = seasonFromDate(slate?.sheet_date || sheetDateFromQuery());
        computePitcherScoresForSlate();
        const stats = pitcherStats(pitcher);
        const statsList = collectSlatePitcherStatsList();
        renderPitcherProfileHeader(pitcher, { team, game });
        renderPitcherProfileHero(stats);
        if (els.profileGrid) {
            els.profileGrid.innerHTML = buildPitcherProfileGridHtml(pitcher, stats, statsList);
        }
        wirePitcherProfileSavant(pitcher, season);
        loadPitcherProfileTrends(pitcher.id, season);
        if (typeof els.playerProfile.showModal === "function") els.playerProfile.showModal();
    }

    function openPlayerProfile(entry) {
        if (!entry || !els.playerProfile) return;
        profilePitcherEntry = null;
        profileEntry = entry;
        if (els.profileJump) els.profileJump.hidden = false;
        if (els.profileTracker) els.profileTracker.hidden = false;
        const { row, game, team, pitcher } = entry;
        const stats = hitterStats(row);
        const prop = row.hrProp || {};
        const season = seasonFromDate(slate?.sheet_date || sheetDateFromQuery());
        renderProfileHeader(row, { team, game });
        renderProfileHeroHrEnv(row, game, prop, entry);
        if (els.profileGrid) {
            els.profileGrid.innerHTML = buildProfileGridHtml(stats, pitcher, prop, game, row, { showHrEnv: true });
        }
        wireProfileSavant(row, season);
        syncProfileTrackerBtn(entry);
        loadProfileTrends(row.id, season, stats);
        if (typeof els.playerProfile.showModal === "function") els.playerProfile.showModal();
    }

    function closePlayerProfile() {
        profileEntry = null;
        profilePitcherEntry = null;
        if (els.profileTrends) {
            els.profileTrends.hidden = true;
            els.profileTrends.innerHTML = "";
        }
        if (els.playerProfile && typeof els.playerProfile.close === "function") els.playerProfile.close();
    }

    async function jumpToPitcherProfileEntry(entry) {
        if (!entry) return;
        activeGameIdx = entry.gameIdx;
        closePlayerProfile();
        await renderAll();
        els.pitcherPanel?.scrollIntoView({ behavior: "smooth", block: "start" });
        els.pitcherPanel?.classList.add("rs-row--flash");
        setTimeout(() => els.pitcherPanel?.classList.remove("rs-row--flash"), 1800);
    }

    async function jumpToProfileEntry(entry) {
        if (!entry) return;
        activeGameIdx = entry.gameIdx;
        activeSide = entry.side;
        closePlayerProfile();
        await renderAll();
        const rowEl =
            els.tableBody?.querySelector(`tr[data-hitter-id="${entry.row.id}"]`) ||
            els.cardList?.querySelector(`.rs-card[data-hitter-id="${entry.row.id}"]`);
        rowEl?.scrollIntoView({ behavior: "smooth", block: "center" });
        rowEl?.classList.add("rs-row--flash");
        setTimeout(() => rowEl?.classList.remove("rs-row--flash"), 1800);
    }

    function renderSearchResults(query) {
        if (!els.searchResults) return;
        const q = String(query || "").trim();
        if (!q) {
            els.searchResults.hidden = true;
            els.searchResults.innerHTML = "";
            return;
        }
        const matches = collectSlateHitters()
            .filter((e) => (e.row.name || "").toLowerCase().includes(q.toLowerCase()))
            .slice(0, 8);
        if (!matches.length) {
            els.searchResults.hidden = false;
            els.searchResults.innerHTML = `<div class="rs-search-empty">No hitters on this slate match “${escAttr(q)}”.</div>`;
            return;
        }
        els.searchResults.hidden = false;
        els.searchResults.innerHTML = matches
            .map(
                (e) =>
                    `<button type="button" class="rs-search-item" data-id="${e.row.id}" data-game="${e.gameIdx}" data-side="${e.side}"><span class="rs-search-item__name">${escAttr(e.row.name || "")}</span><span class="rs-search-item__meta">${escAttr(e.team || "")} · ${escAttr(e.game.matchup || "")} · vs ${escAttr(e.pitcher?.name || "TBD")}</span></button>`
            )
            .join("");
        wireSlateSearchItems();
    }

    function wireSlateSearchItems() {
        els.searchResults?.querySelectorAll(".rs-search-item[data-id]").forEach((btn) => {
            btn.addEventListener("mousedown", (ev) => ev.preventDefault());
            btn.addEventListener("click", () => {
                const id = Number(btn.getAttribute("data-id"));
                const gi = Number(btn.getAttribute("data-game"));
                const side = btn.getAttribute("data-side");
                const entry = collectSlateHitters().find((e) => e.row.id === id && e.gameIdx === gi && e.side === side);
                if (entry) {
                    if (els.playerSearch) els.playerSearch.value = entry.row.name || "";
                    renderSearchResults("");
                    openPlayerProfile(entry);
                }
            });
        });
    }

    function explorePitcherSortValue(entry, key) {
        const ps = pitcherStats(entry.pitcher);
        if (key === "kPick") return ps.kPickPct ?? ps.kPick ?? null;
        if (key === "risk") return ps.dingerRiskPct ?? ps.dingerRisk ?? null;
        if (key === "lhb") return ps.dingerRiskLhbPct ?? null;
        if (key === "rhb") return ps.dingerRiskRhbPct ?? null;
        return ps[key] ?? null;
    }

    function renderExplorePanel() {
        if (!els.hrLeaderboardBody) return;
        computeHrFormForSlate();
        computeBoomForSlate();
        computePitcherScoresForSlate();
        refreshAllHrProps();
        rebuildHrTicketScale();
        const hitters = filteredExploreHitters().slice(0, HR_RESEARCH_CONFIG.explore.topHitters);
        const sortKey = exploreSortKey || els.exploreSort?.value || "ticketRank";
        syncExploreSortSelect(sortKey);
        if (els.exploreLede) {
            els.exploreLede.innerHTML = `HR ticket score is a 1–100 slate scale (100 = best target today). It combines ${HR_RESEARCH_CONFIG.pillars.map((p) => p.label.toLowerCase()).join(", ")}. ${hrResearchPillarsHtml()}`;
        }
        if (els.exploreMeta) {
            const total = collectSlateHitters().length;
            const sortLabels = {
                ticketRank: "HR ticket score (/100)",
                hrEnv: "HR environment",
                mixPlus: "Pitch mix",
                mixEdge: "Savant edge",
                matchWhiffPct: "Swing & miss (Savant)",
                barrelPct: "Barrel%",
                boomPct: "Boom%",
                avgEV: "Exit velo",
                hrLuckDiff: "Due+",
                hardHitPct: "Hard-hit%",
                nearHr: "Near HR",
                airPct: "Air%",
                splitPct: "Split",
                riskPct: "Risk",
                parkPct: "Park",
                formPct: "HR Form%",
            };
            els.exploreMeta.textContent = `${hitters.length} of ${total} hitters · sorted by ${sortLabels[sortKey] || sortKey}`;
        }
        els.hrLeaderboardBody.innerHTML = hitters.length
            ? hitters
                  .map((e, idx) => {
                      const ticket = computeHrTicket(e);
                      const stats = hitterStats(e.row);
                      const score = hrTicketScore100(e);
                      return `<tr class="rs-leaderboard-row" data-id="${e.row.id}" data-game="${e.gameIdx}" data-side="${e.side}">
                        <td>${idx + 1}</td>
                        <td><button type="button" class="rs-leaderboard-link">${escAttr(e.row.name || "—")}</button></td>
                        <td>${escAttr(e.game.matchup || "")}</td>
                        <td>${escAttr(e.pitcher?.name || "TBD")}</td>
                        <td>${fmtTicketBadge(score)}</td>
                        <td>${fmtFormPct(ticket?.mixPlus)}</td>
                        <td>${fmtFormPct(stats.mixEdge)}</td>
                        <td>${fmtPct(stats.matchWhiffPct ?? stats.bvpKPct)}</td>
                        <td>${fmtHrFormWithTrend(stats.hrFormPct, formTrendForRow(e.row))}</td>
                        <td>${fmtPct(stats.barrelPct)}</td>
                    </tr>`;
                  })
                  .join("")
            : `<tr><td colspan="10" class="rs-empty">No hitters match these filters.</td></tr>`;

        renderExploreLbCards(hitters);

        scheduleHrFormHydrate(hitters.map((e) => e.row?.id).filter(Boolean));

        els.hrLeaderboardBody.querySelectorAll(".rs-leaderboard-row").forEach((tr) => {
            tr.querySelector(".rs-leaderboard-link")?.addEventListener("click", (ev) => {
                ev.stopPropagation();
                jumpToLeaderboardEntry(tr);
            });
            tr.addEventListener("click", () => jumpToLeaderboardEntry(tr));
        });

        els.hrLeaderboard?.querySelectorAll(".rs-lb-sort").forEach((th) => {
            th.replaceWith(th.cloneNode(true));
        });
        els.hrLeaderboard?.querySelectorAll(".rs-lb-sort").forEach((th) => {
            th.addEventListener("click", () => {
                const key = th.getAttribute("data-sort");
                if (!key) return;
                syncExploreSortSelect(key);
                renderExplorePanel();
            });
        });

        if (els.pitcherLeaderboardBody) {
            const sortKey = pitcherLbSortKey || "risk";
            let pitchers = collectSlatePitchers()
                .map((e) => ({
                    ...e,
                    risk: pitcherStats(e.pitcher).dingerRiskPct ?? pitcherStats(e.pitcher).dingerRisk,
                }))
                .filter((e) => e.risk != null && !Number.isNaN(Number(e.risk)))
                .filter((e) => Number(e.risk) >= HR_RESEARCH_CONFIG.explore.minPitcherRisk);
            pitchers.sort((a, b) => {
                const av = explorePitcherSortValue(a, sortKey);
                const bv = explorePitcherSortValue(b, sortKey);
                if (av == null && bv == null) return 0;
                if (av == null) return 1;
                if (bv == null) return -1;
                const cmp = Number(av) - Number(bv);
                return pitcherLbSortDir > 0 ? cmp : -cmp;
            });
            pitchers = pitchers.slice(0, HR_RESEARCH_CONFIG.explore.topPitchers);
            els.pitcherLeaderboardBody.innerHTML = pitchers.length
                ? pitchers
                      .map((e) => {
                          const ps = pitcherStats(e.pitcher);
                          return `<tr class="rs-leaderboard-row rs-pitcher-lb-row" data-pitcher-id="${e.pitcher.id || ""}" data-game="${e.gameIdx}" data-side="${e.side}"><td><button type="button" class="rs-leaderboard-link">${escAttr(e.pitcher.name || "—")}</button></td><td>${escAttr(e.game.matchup || "")}</td><td>${Math.round(Number(e.risk))}%</td><td>${ps.kPickPct != null ? `${ps.kPickPct}%` : "—"}</td><td>${fmtPct(ps.barrelPct)}</td><td>${ps.hr9 != null ? Number(ps.hr9).toFixed(2) : "—"}</td></tr>`;
                      })
                      .join("")
                : `<tr><td colspan="6" class="rs-empty">Pitcher dinger risk unavailable.</td></tr>`;
            els.pitcherLeaderboardBody.querySelectorAll(".rs-pitcher-lb-row").forEach((tr) => {
                tr.querySelector(".rs-leaderboard-link")?.addEventListener("click", () => {
                    const id = Number(tr.getAttribute("data-pitcher-id"));
                    const gi = Number(tr.getAttribute("data-game"));
                    const side = tr.getAttribute("data-side");
                    const entry = collectSlatePitchers().find((e) => e.pitcher?.id === id && e.gameIdx === gi && e.side === side);
                    if (entry) openPitcherProfile(entry);
                });
            });
            els.pitcherLeaderboard?.querySelectorAll(".rs-plb-sort").forEach((th) => {
                th.classList.toggle("is-sorted", th.getAttribute("data-sort") === sortKey);
            });
            els.pitcherLeaderboard?.querySelectorAll(".rs-plb-sort").forEach((th) => {
                th.replaceWith(th.cloneNode(true));
            });
            els.pitcherLeaderboard?.querySelectorAll(".rs-plb-sort").forEach((th) => {
                th.addEventListener("click", () => {
                    const key = th.getAttribute("data-sort");
                    if (!key) return;
                    if (pitcherLbSortKey === key) pitcherLbSortDir *= -1;
                    else {
                        pitcherLbSortKey = key;
                        pitcherLbSortDir = -1;
                    }
                    renderExplorePanel();
                });
            });
        }
        wireExploreLeaderboardTips();
        hydrateKProjectionsFromTrends();
    }

    function renderSourceBadge() {
        if (!els.sourceBadge) return;
        els.sourceBadge.style.display = "none";
    }

    async function renderAll() {
        pickDefaultSide();
        computeHrFormForSlate();
        computeBoomForSlate();
        computePitcherScoresForSlate();
        refreshAllHrProps();
        rebuildTicketSlatePools();
        clearSlatePresetCache();
        renderGoblinsPanel();
        renderGames();
        renderMatchupBar();
        renderWeatherPanel();
        await renderPitcherPanel();
        renderExplorePanel();
        hydrateKProjectionsFromTrends();
        renderTable();
        renderMobileCards();
        syncMobileSortSelect();
        renderSourceBadge();
        renderDataFreshness();
        clearStatus();
    }

    async function loadSlate(date, forceLive) {
        if (isFileProtocol()) {
            showFileProtocolError();
            return;
        }
        savantLookup = null;
        pitchMixCache = null;
        parkFactorsLookup = null;
        parkFactorsLookupDate = null;
        pitcherHandLookup = null;
        clearHrTicketCache();
        clearSlatePresetCache();
        formTrendCache.clear();
        boomTrendCache.clear();
        hrFormRollingCache.clear();
        formTrendHydrateGen += 1;
        matchupHistoryCache.clear();
        matchupHydrateGen += 1;
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

        await applyRotowireFallback(date);
        await expandAllLineupDepth(season, date);

        const savantMerge = await mergeSavantIntoAllLineups(season);
        const pitcherSavantMerge = await mergePitcherSavantIntoGames(season);
        const pitchMixMerge = await applyPitchMixEnrichment(season, date);
        applyMatchupEdgeToAllLineups();
        scheduleMatchupEdgeHydrate();
        const pfLookup = await ensurePropfinderLookup(date);
        applyPropfinderToAllLineups(pfLookup);
        await ensureBatterHands();
        await applyParkFactors(date);
        await loadStadiumCoords();

        activeGameIdx = Math.min(activeGameIdx, slate.games.length - 1);
        pickDefaultSide();
        refreshAllHrProps();
        if (!restoreSortPreference()) {
            applyDefaultSort();
            sortUserOverride = false;
        }
        await renderAll();
        prefetchSlateWeather().catch((err) => console.warn("weather prefetch", err));

        if (!lineupsHaveSavant(slate.games)) {
            const hint = cacheResult.lastStatus || savantMerge.lastStatus || "unknown";
            setStatus(
                `Savant stats missing for ${date}. Data file: ${hint}. From repo folder run: python fetch-research-slate.py --date ${date} then python serve-research.py — open http://localhost:8080/research/index.html?date=${date}`,
                true
            );
            return;
        }

        const mixCoverage = lineupsHavePitchMix(slate.games);
        if (!mixCoverage.any) {
            setStatus(
                `Pitch mix unavailable for ${date} — starter arsenal or batter pitch-type cache missing. Run: python fetch-research-slate.py --date ${date}`,
                true
            );
            return;
        }
        if (!mixCoverage.full) {
            console.info(
                `Pitch mix partial for ${date}: ${mixCoverage.withMix}/${mixCoverage.total} hitters (TBD starters or pitchers missing Savant arsenal).`
            );
        }

        clearStatus();
        renderDataFreshness();
    }

    function wireTopFab() {
        const fab = document.getElementById("rsTopFab");
        if (!fab) return;
        fab.hidden = false;
        const sync = () => {
            fab.classList.toggle("is-visible", window.scrollY > 900);
        };
        window.addEventListener("scroll", sync, { passive: true });
        sync();
        fab.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    }

    function wireUi() {
        wireTopFab();
        els.profileClose?.addEventListener("click", closePlayerProfile);
        els.profileJump?.addEventListener("click", () => {
            if (profileEntry) jumpToProfileEntry(profileEntry);
            else if (profilePitcherEntry) jumpToPitcherProfileEntry(profilePitcherEntry);
        });
        els.profileTracker?.addEventListener("click", toggleProfileTracker);
        els.playerProfile?.addEventListener("cancel", closePlayerProfile);
        els.playerSearch?.addEventListener("input", () => {
            clearTimeout(searchBlurTimer);
            renderSearchResults(els.playerSearch.value);
        });
        els.playerSearch?.addEventListener("focus", () => renderSearchResults(els.playerSearch.value));
        els.playerSearch?.addEventListener("blur", () => {
            searchBlurTimer = setTimeout(() => renderSearchResults(""), 150);
        });
        els.exploreHand?.addEventListener("change", () => renderExplorePanel());
        els.exploreMinScore?.addEventListener("input", () => renderExplorePanel());
        els.exploreMinPark?.addEventListener("input", () => renderExplorePanel());
        els.exploreSort?.addEventListener("change", () => {
            syncExploreSortSelect(els.exploreSort.value);
            renderExplorePanel();
        });
        els.exploreReset?.addEventListener("click", resetExploreFilters);
        syncExploreSortSelect(exploreSortKey);
        wireExploreLeaderboardTips();
        wireExploreLbNav();
        els.refreshBtn?.addEventListener("click", () => {
            const date = els.dateInput?.value || sheetDateFromQuery();
            loadSlate(date, true).catch((e) => setStatus(String(e.message || e), true));
        });
        els.dateInput?.addEventListener("change", () => {
            const date = els.dateInput.value;
            if (!date) return;
            sessionStorage.setItem(RESEARCH_KEEP_DATE_KEY, date);
            const url = new URL(window.location.href);
            url.searchParams.set("date", date);
            window.history.replaceState({}, "", url);
            loadSlate(date, false).catch((e) => setStatus(String(e.message || e), true));
        });
        els.sideAway?.addEventListener("click", () => {
            activeSide = "away";
            renderAll().catch((e) => setStatus(String(e.message || e), true));
        });
        els.sideHome?.addEventListener("click", () => {
            activeSide = "home";
            renderAll().catch((e) => setStatus(String(e.message || e), true));
        });
        els.mobileSort?.addEventListener("change", () => {
            setSortColumn(els.mobileSort.value || "order", { toggleDir: false });
            syncMobileSortDir();
            renderTable();
            renderMobileCards();
        });
        els.mobileSortDir?.addEventListener("click", () => {
            sortUserOverride = true;
            sortDir *= -1;
            saveSortPreference();
            syncMobileSortDir();
            renderTable();
            renderMobileCards();
        });
        if (els.weatherPanel && isMobileView()) {
            els.weatherPanel.removeAttribute("open");
        } else if (els.weatherPanel) {
            els.weatherPanel.setAttribute("open", "");
        }
        window.matchMedia("(max-width: 768px)").addEventListener("change", (e) => {
            syncMobileSortSelect();
            if (els.weatherPanel && !els.weatherPanel.hidden) {
                if (e.matches) els.weatherPanel.removeAttribute("open");
                else els.weatherPanel.setAttribute("open", "");
            }
        });
        els.themeToggle?.addEventListener("click", toggleTheme);
        syncThemeToggle();
        els.colReorderBtn?.addEventListener("click", () => {
            setColumnReorderMode(!columnReorderMode);
        });
        els.colResetBtn?.addEventListener("click", () => {
            resetColumnOrder();
            renderTable();
        });
        els.tableViewEssential?.addEventListener("click", () => setTableViewMode("essential"));
        els.tableViewFull?.addEventListener("click", () => setTableViewMode("full"));
        setTableViewMode(tableViewMode);
        let scrollTick = false;
        window.addEventListener(
            "scroll",
            () => {
                if (scrollTick) return;
                scrollTick = true;
                requestAnimationFrame(() => {
                    scrollTick = false;
                    els.header?.classList.toggle("rs-header--compact", window.scrollY > 72);
                });
            },
            { passive: true }
        );
    }

    function normalizePlayerKey(name) {
        return String(name || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s*\((?:l|r|s)\)\s*$/i, "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, " ")
            .trim();
    }

    async function jumpToPlayerFromQuery() {
        const raw = qs("player");
        if (!raw) return;
        const target = normalizePlayerKey(raw);
        if (!target) return;
        const hitters = collectSlateHitters();
        const entry =
            hitters.find((e) => normalizePlayerKey(e.row.name) === target) ||
            hitters.find((e) => {
                const key = normalizePlayerKey(e.row.name);
                return key.includes(target) || target.includes(key);
            });
        if (!entry) {
            setStatus(`"${raw}" is not in a projected lineup on this slate — pick their game manually.`, true);
            return;
        }
        activeGameIdx = entry.gameIdx;
        activeSide = entry.side;
        await renderAll();
        const rowEl =
            els.tableBody?.querySelector(`tr[data-hitter-id="${entry.row.id}"]`) ||
            els.cardList?.querySelector(`.rs-card[data-hitter-id="${entry.row.id}"]`);
        if (!rowEl) return;
        rowEl.scrollIntoView({ behavior: "smooth", block: "center" });
        rowEl.classList.add("rs-row--jump");
        setTimeout(() => rowEl.classList.remove("rs-row--jump"), 4000);
    }

    wireUi();
    loadSlate(initResearchDate(), false)
        .then(() => jumpToPlayerFromQuery())
        .catch((e) => setStatus(String(e.message || e), true));
})();
