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
        { key: "expectedHr", label: "xHR", group: "power", stat: "expectedHr", fmt: (r) => fmtXhr(hitterStats(r).expectedHr), tip: "Expected homers from contact quality — how many HRs Savant thinks this swing profile deserves (rounded)." },
        { key: "hrLuckDiff", label: "Due+", group: "power", stat: "hrLuckDiff", fmt: (r) => fmtLuck(hitterStats(r).hrLuckDiff), tip: "Homers owed (xHR minus actual HR). +1 or higher means the hitter is due for a jack." },
        { key: "nearHr", label: "Near HR", group: "power", stat: "nearHr", fmt: (r) => fmtNearHr(r), tip: "Near misses — balls that almost left the yard. PropFinder * fallback when Savant is missing." },
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
        { key: "hrFbPct", label: "HR/FB%", group: "plate", stat: "hrFbPct", fmt: (r) => fmtPct(hitterStats(r).hrFbPct), tip: "Home runs per fly ball — how often fly balls leave the yard. Power efficiency on balls in the air." },
        { key: "recentForm", label: "Form%", group: "plate", stat: "recentForm", fmt: (r) => fmtFormPct(hitterStats(r).recentForm), tip: "Recent form — wOBA vs expected wOBA gap. Positive means outperforming expected contact quality; negative means underperforming." },
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
    let stadiumCoords = null;
    let activeGameIdx = 0;
    let activeSide = "away";
    let sortKey = "mixPlus";
    let sortDir = -1;
    let sortUserOverride = false;

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
        mobileSortDir: document.getElementById("rsMobileSortDir"),
        cardList: document.getElementById("rsCardList"),
        weatherPanel: document.getElementById("rsWeatherPanel"),
        weatherGrid: document.getElementById("rsWeatherGrid"),
        weatherMeta: document.getElementById("rsWeatherMeta"),
        windField: document.getElementById("rsWindField"),
        parkOutline: document.getElementById("rsParkOutline"),
        windArrow: document.getElementById("rsWindArrow"),
        windInfo: document.getElementById("rsWindInfo"),
    };

    function isMobileView() {
        return window.matchMedia("(max-width: 768px)").matches;
    }

    const MOBILE_CARD_OPEN_GROUPS = new Set(["matchup", "power"]);
    const MOBILE_HIGHLIGHT_KEYS = [
        "hardHitPct",
        "blastPct",
        "recentForm",
        "hrFbPct",
        "fbPct",
        "barrelPct",
        "pullPct",
        "mixPlus",
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

    function sheetDateFromQuery() {
        const d = qs("date");
        if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) return d;
        return todayLocalIso();
    }

    function initResearchDate() {
        const date = sheetDateFromQuery();
        if (!qs("date")) {
            const url = new URL(window.location.href);
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

    const WX_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
    const WX_RHO_ZERO = 1.225;
    const WX_DA_EXPONENT = 1 / (9.80665 / (287.053 * 0.0065) - 1);
    const WX_DISTANCE_BOOST_PER_1000FT = 2.75;
    let wxBaselineDaFt = null;

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

    function fmtHrPropPct(row) {
        if (row?.hrProp?.propPass || activeGame()?.propPass) return "PASS";
        const pct = row?.hrProp?.combinedPct;
        if (pct == null || Number.isNaN(Number(pct))) return "—";
        const sign = pct > 0 ? "+" : "";
        return `${sign}${pct}%`;
    }

    function fmtPitcherRisk(stats) {
        if (!stats) return "";
        const parts = [];
        if (stats.hrRiskPct != null) parts.push(`HR risk ${stats.hrRiskPct > 0 ? "+" : ""}${stats.hrRiskPct}%`);
        if (stats.hr9 != null) parts.push(`${Number(stats.hr9).toFixed(2)} HR/9`);
        if (stats.vsLhbPct != null && stats.vsRhbPct != null) {
            parts.push(`L ${stats.vsLhbPct > 0 ? "+" : ""}${stats.vsLhbPct}% · R ${stats.vsRhbPct > 0 ? "+" : ""}${stats.vsRhbPct}%`);
        }
        return parts.join(" · ");
    }

    const HR_REF_ALLEY_FT = 380;
    const HR_CARRY_PCT_PER_3FT = 0.11;
    const HR_DA_MULT_PER_1000 = 0.1;
    const HR_WIND_MULT_AT_15 = 0.25;

    function hrCarryFeetToPct(carryFt) {
        return (carryFt / 3) * HR_CARRY_PCT_PER_3FT;
    }

    function hrDaCompoundMult(daDelta) {
        if (daDelta == null) return 1;
        if (daDelta <= 0) return Math.max(0.82, 1 + (daDelta / 1000) * 0.04);
        return Math.pow(1 + HR_DA_MULT_PER_1000, daDelta / 1000);
    }

    function hrWindCompoundMult(windOutMph) {
        if (windOutMph == null) return 1;
        return Math.max(0.72, 1 + (windOutMph / 15) * HR_WIND_MULT_AT_15);
    }

    function hrWallDistMult(wallFt) {
        if (wallFt == null) return 1;
        return Math.max(0.88, 1 + hrCarryFeetToPct(HR_REF_ALLEY_FT - wallFt));
    }

    function hrWallHeightMult(heightFt) {
        if (heightFt == null) return 1;
        if (heightFt >= 20) return 0.94;
        if (heightFt >= 10) return 0.97;
        if (heightFt <= 5) return 1.03;
        return 1;
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
        const carryMult = Math.max(0.85, 1 + hrCarryFeetToPct(Number(wx.distanceBoostFt) || 0));
        const weatherMult = daMult * carryMult;
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
        let score = hand === "L" ? stats.vsLhb : stats.vsRhb;
        if (score == null) score = stats.hrRisk;
        if (score == null) return 1;
        return Math.max(0.65, 1 + Number(score) * 0.5);
    }

    function computeHitterHrProp(row, game, pitcher) {
        const stadium = lookupStadium(game?.venue || "");
        if (!stadium) return row?.hrProp || null;
        const hand = effectiveBatterHand(row?.hand, pitcher?.throws);
        const hrModel = game.hrModel || computeGameHrModel(game);
        const parkPct = parkHrPctForHitter(game, hand);
        const stadiumMult = parkPct == null ? 1 : Math.max(0.7, 1 + parkPct / 100);
        const windMult = hand === "L" ? hrModel?.windMultLhb ?? 1 : hrModel?.windMultRhb ?? 1;
        const dimMult = hand === "L" ? hrModel?.dimMultLhb ?? 1 : hrModel?.dimMultRhb ?? 1;
        const weatherMult = hrModel?.weatherMult ?? 1;
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
        const combined = stadiumMult * weatherMult * windMult * dimMult * pitcherMult;
        const pull = pullAlley(stadium, hand);
        return {
            hand,
            combinedMult: Math.round(combined * 1000) / 1000,
            combinedPct: Math.round((combined - 1) * 1000) / 10,
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
        if (pct >= 6) return "good";
        if (pct <= -6) return "bad";
        return "mid";
    }

    function computeHrCarryPct(wx) {
        return displayHrCarryPct(wx);
    }

    function computeWindOutPct(windComponentMph) {
        return displayWindPct(windComponentMph);
    }

    function computeEnvHrPct(wx) {
        const carry = displayHrCarryPct(wx) ?? 0;
        const wind = displayWindPct(wx?.windComponentMph) ?? 0;
        return Math.round(carry + wind);
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
            "Historical HR boost from this stadium vs league average (PropFinder import). Positive = bandbox; negative = graveyard.",
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
        refreshAllHrProps();
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
        const pct = computeEnvHrPct(wx);
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

        if (game.parkHrPct != null) {
            cells.push(
                wxCell("Park Factor", fmtSignedPct(game.parkHrPct), WX_TIPS.parkFactor, {
                    tone: edgeTone(game.parkHrPct),
                    sub: "vs league-average HR rate",
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
                    { wide: true }
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

    async function applyPitchMixEnrichment(season) {
        const caches = await ensurePitchMixCaches(season);
        if (!Object.keys(caches.pitcherArsenal || {}).length && !Object.keys(caches.pitcherArsenalPrior || {}).length) {
            return { n: 0, source: null, lastStatus: caches.lastStatus };
        }
        const savMap = savantLookupMapFromSlate();
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
            "pitcher_arsenal_prior_lookup",
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
            for (const field of ["parkHrPct", "parkLhbPct", "parkRhbPct", "parkWeather", "mlbWeather", "venue", "hrModel", "roofStatus", "propPass"]) {
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
        ];
        for (const k of savantKeys) {
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

    function resetSortToDefault() {
        sortUserOverride = false;
        applyDefaultSort();
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
                    <span class="rs-game-pill__matchup">${g.matchup}${weatherBadgeHtml(g)}</span>
                    <span class="rs-game-pill__meta">${time}${time ? " · " : ""}${g.lineupStatus || ""} · ${nAway}/${nHome} hitters</span>
                    <span class="rs-game-pill__meta">${sp}</span>
                </button>`;
            })
            .join("");
        els.games.querySelectorAll(".rs-game-pill").forEach((btn) => {
            btn.addEventListener("click", async () => {
                activeGameIdx = parseInt(btn.getAttribute("data-idx"), 10);
                pickDefaultSide();
                resetSortToDefault();
                renderAll();
                const game = activeGame();
                if (game && !weatherIsComplete(game.parkWeather)) {
                    await ensureGameWeather(game);
                    renderWeatherPanel();
                    renderGames();
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

    function syncMobileSortDir() {
        if (!els.mobileSortDir) return;
        els.mobileSortDir.textContent = sortDir > 0 ? "↓" : "↑";
        els.mobileSortDir.title = sortDir > 0 ? "High to low (tap to reverse)" : "Low to high (tap to reverse)";
        els.mobileSortDir.setAttribute("aria-label", sortDir > 0 ? "Sort high to low" : "Sort low to high");
    }

    function syncMobileSortSelect() {
        if (!els.mobileSort) return;
        const options = COLS.filter((c) => c.key !== "order").map((c) => {
            const selected = c.key === sortKey ? " selected" : "";
            return `<option value="${c.key}"${selected}>${c.label}</option>`;
        });
        els.mobileSort.innerHTML = options.join("");
        syncMobileSortDir();
    }

    function mobileCardStatHtml(c, row, colValues, higherBetter) {
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
        els.cardList.innerHTML = rows
            .map((row) => {
                const projected = row.projected ? '<span class="rs-hand rs-hand--proj">proj</span>' : "";
                const highlights = highlightCols
                    .map((c) => {
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
                        const cols = COLS.filter((c) => c.group === group.id && c.stat);
                        if (!cols.length) return "";
                        const stats = cols.map((c) => mobileCardStatHtml(c, row, colValues, higherBetter)).join("");
                        const openAttr = MOBILE_CARD_OPEN_GROUPS.has(group.id) ? " open" : "";
                        return `<details class="rs-card__section rs-card__section--${group.id}"${openAttr}><summary class="rs-card__section-title">${group.label}<span class="rs-card__section-chev" aria-hidden="true"></span></summary><dl class="rs-card__stats">${stats}</dl></details>`;
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
                    <div class="rs-card__highlights">${highlights}</div>
                    ${sections}
                </article>`;
            })
            .join("");
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

    function renderTable() {
        if (!els.tableHead || !els.tableBody) return;
        const rows = sortedActiveRows();

        els.tableHead.innerHTML = buildTableHeadHtml();

        els.tableHead.querySelectorAll("tr.rs-col-row th").forEach((th) => {
            th.addEventListener("click", () => {
                const key = th.getAttribute("data-key");
                sortUserOverride = true;
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
                        return `<td${tip}><span class="rs-hitter" title="${escAttr(r.name || "")}">${r.name || "—"}</span> <span class="rs-hand">${r.position || ""}</span>${tag}</td>`;
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
        renderWeatherPanel();
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
        refreshAllHrProps();
        resetSortToDefault();
        renderAll();
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
            resetSortToDefault();
            renderAll();
        });
        els.sideHome?.addEventListener("click", () => {
            activeSide = "home";
            resetSortToDefault();
            renderAll();
        });
        els.mobileSort?.addEventListener("change", () => {
            sortUserOverride = true;
            sortKey = els.mobileSort.value || "order";
            sortDir = sortKey === "name" ? 1 : -1;
            syncMobileSortDir();
            renderTable();
            renderMobileCards();
        });
        els.mobileSortDir?.addEventListener("click", () => {
            sortUserOverride = true;
            sortDir *= -1;
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
    }

    wireUi();
    loadSlate(initResearchDate(), false).catch((e) => setStatus(String(e.message || e), true));
})();
