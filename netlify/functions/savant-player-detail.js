/**
 * Proxy Baseball Savant pitch-level Statcast search -> compact player detail JSON.
 *
 * One CSV pull per player-season carries everything the profile deep-dive needs
 * (zone grid, pitch-type splits, batted-ball log, spray points), so the daily
 * research payload stays small and this stays on-demand behind the CDN cache.
 */
const SEARCH_URL =
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details" +
    "&hfGT=R%7C&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&sort_order=desc" +
    "&player_type={role}&hfSea={seasons}&{lookup}%5B%5D={playerId}";

const PEOPLE_URL = "https://statsapi.mlb.com/api/v1/people?personIds={ids}";

const HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    // Pitch-level history only moves once a day, so let the CDN carry it.
    "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
};

// Savant zones: 1-9 is the strike zone read left-to-right, top-to-bottom from
// the catcher's view; 11-14 are the four outside-the-zone quadrants.
const ZONE_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12", "13", "14"];

const WHIFF_DESCRIPTIONS = new Set(["swinging_strike", "swinging_strike_blocked", "missed_bunt"]);
const SWING_DESCRIPTIONS = new Set([
    "hit_into_play",
    "foul",
    "foul_tip",
    "foul_bunt",
    "bunt_foul_tip",
    "swinging_strike",
    "swinging_strike_blocked",
    "missed_bunt",
]);
const HIT_EVENTS = new Set(["single", "double", "triple", "home_run"]);

const MAX_BATTED_BALLS = 400;

function num(val) {
    if (val == null || val === "" || val === "-") return null;
    const n = parseFloat(String(val).replace("%", ""));
    return Number.isFinite(n) ? n : null;
}

function round(val, places = 1) {
    if (val == null || !Number.isFinite(val)) return null;
    const f = 10 ** places;
    return Math.round(val * f) / f;
}

function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/);
    if (lines.length < 2) return [];
    const headers = lines[0].split(",").map((h) => h.replace(/^"|"$/g, "").trim());
    return lines.slice(1).map((line) => {
        const cells = [];
        let cur = "";
        let inQ = false;
        for (let i = 0; i < line.length; i++) {
            const ch = line[i];
            if (ch === '"') inQ = !inQ;
            else if (ch === "," && !inQ) {
                cells.push(cur);
                cur = "";
            } else cur += ch;
        }
        cells.push(cur);
        const row = {};
        headers.forEach((h, i) => {
            row[h] = (cells[i] || "").replace(/^"|"$/g, "").trim();
        });
        return row;
    });
}

function emptyZone() {
    return {
        pitches: 0,
        swings: 0,
        whiffs: 0,
        bbe: 0,
        hr: 0,
        hits: 0,
        barrels: 0,
        hardHits: 0,
        xwobaSum: 0,
        xwobaN: 0,
        evSum: 0,
        evN: 0,
    };
}

function addPitch(bucket, row) {
    bucket.pitches += 1;
    const desc = row.description || "";
    if (SWING_DESCRIPTIONS.has(desc)) bucket.swings += 1;
    if (WHIFF_DESCRIPTIONS.has(desc)) bucket.whiffs += 1;

    const ev = num(row.launch_speed);
    const isBip = desc === "hit_into_play";
    if (isBip && ev != null) {
        bucket.bbe += 1;
        bucket.evSum += ev;
        bucket.evN += 1;
        if (ev >= 95) bucket.hardHits += 1;
        if (num(row.launch_speed_angle) === 6) bucket.barrels += 1;
    }
    if (row.events === "home_run") bucket.hr += 1;
    if (HIT_EVENTS.has(row.events)) bucket.hits += 1;

    const xwoba = num(row.estimated_woba_using_speedangle);
    if (xwoba != null) {
        bucket.xwobaSum += xwoba;
        bucket.xwobaN += 1;
    }
}

function finishZone(bucket, totalPitches) {
    const pct = (n, d) => (d > 0 ? round((n / d) * 100, 1) : null);
    return {
        pitches: bucket.pitches,
        usagePct: pct(bucket.pitches, totalPitches),
        swings: bucket.swings,
        whiffPct: pct(bucket.whiffs, bucket.swings),
        bbe: bucket.bbe,
        hr: bucket.hr,
        // HR per batted ball in the zone -- the most stable read at zone-level
        // sample sizes, and what the heatmap colours off.
        hrRate: pct(bucket.hr, bucket.bbe),
        hrPerPitch: pct(bucket.hr, bucket.pitches),
        hits: bucket.hits,
        barrelPct: pct(bucket.barrels, bucket.bbe),
        hardHitPct: pct(bucket.hardHits, bucket.bbe),
        xwoba: bucket.xwobaN ? round(bucket.xwobaSum / bucket.xwobaN, 3) : null,
        avgEV: bucket.evN ? round(bucket.evSum / bucket.evN, 1) : null,
    };
}

function buildZoneGrid(rows) {
    const buckets = new Map();
    let total = 0;
    rows.forEach((row) => {
        const z = String(row.zone || "").trim();
        if (!ZONE_KEYS.includes(z)) return;
        if (!buckets.has(z)) buckets.set(z, emptyZone());
        addPitch(buckets.get(z), row);
        total += 1;
    });
    const out = {};
    ZONE_KEYS.forEach((z) => {
        out[z] = buckets.has(z) ? finishZone(buckets.get(z), total) : finishZone(emptyZone(), total);
    });
    return { zones: out, pitches: total };
}

function buildPitchTypes(rows) {
    const buckets = new Map();
    const names = new Map();
    const veloSum = new Map();
    const veloN = new Map();
    let total = 0;
    rows.forEach((row) => {
        const code = String(row.pitch_type || "").trim();
        if (!code) return;
        if (!buckets.has(code)) buckets.set(code, emptyZone());
        addPitch(buckets.get(code), row);
        if (row.pitch_name) names.set(code, row.pitch_name);
        const velo = num(row.release_speed);
        if (velo != null) {
            veloSum.set(code, (veloSum.get(code) || 0) + velo);
            veloN.set(code, (veloN.get(code) || 0) + 1);
        }
        total += 1;
    });
    const out = {};
    [...buckets.entries()]
        .sort((a, b) => b[1].pitches - a[1].pitches)
        .forEach(([code, bucket]) => {
            const done = finishZone(bucket, total);
            done.name = names.get(code) || code;
            done.avgVelo = veloN.get(code) ? round(veloSum.get(code) / veloN.get(code), 1) : null;
            out[code] = done;
        });
    return { pitchTypes: out, pitches: total };
}

// Savant's hit coordinates share the origin of its field image. Converting to a
// spray angle + distance keeps the chart independent of that image's scaling.
function sprayAngleDeg(hcX, hcY) {
    if (hcX == null || hcY == null) return null;
    const dx = hcX - 125.42;
    const dy = 198.27 - hcY;
    if (dy <= 0) return null;
    return round((Math.atan2(dx, dy) * 180) / Math.PI, 1);
}

function buildBattedBalls(rows, role) {
    const out = [];
    for (let i = rows.length - 1; i >= 0 && out.length < MAX_BATTED_BALLS; i--) {
        const row = rows[i];
        if (row.description !== "hit_into_play") continue;
        const ev = num(row.launch_speed);
        if (ev == null) continue;
        const hcX = num(row.hc_x);
        const hcY = num(row.hc_y);
        out.push({
            date: (row.game_date || "").slice(0, 10),
            // In a batter-view pull `player_name` is the batter, so the other
            // side is only an id until we resolve it below. Pitch names and the
            // player's own hand are looked up from `pitchTypes`/`hand` rather
            // than repeated on every row.
            oppId: num(role === "batter" ? row.pitcher : row.batter),
            oppName: null,
            oppHand: (role === "batter" ? row.p_throws : row.stand) || null,
            // The hitter's own side, per row -- switch hitters change it, and
            // pull/oppo can't be worked out without it.
            batSide: row.stand || null,
            count: row.balls != null && row.strikes != null ? `${row.balls}-${row.strikes}` : null,
            pitchType: row.pitch_type || null,
            pitchVelo: num(row.release_speed),
            ev,
            la: num(row.launch_angle),
            dist: num(row.hit_distance_sc),
            batSpeed: num(row.bat_speed),
            xwoba: round(num(row.estimated_woba_using_speedangle), 3),
            result: row.events || null,
            bbType: row.bb_type || null,
            isHr: row.events === "home_run",
            isBarrel: num(row.launch_speed_angle) === 6,
            // Negative is toward left field, positive toward right -- absolute
            // field direction, never mirrored by the hitter's hand.
            sprayAngle: sprayAngleDeg(hcX, hcY),
        });
    }
    return out;
}

async function resolveNames(ids) {
    const unique = [...new Set(ids.filter((id) => id != null))];
    if (!unique.length) return {};
    const map = {};
    // The people endpoint takes a comma list; chunk it so long slates stay
    // inside a sane URL length.
    for (let i = 0; i < unique.length; i += 100) {
        const chunk = unique.slice(i, i + 100);
        try {
            const res = await fetch(PEOPLE_URL.replace("{ids}", chunk.join(",")), {
                headers: { "User-Agent": "WorstPickz-Research/1.0" },
            });
            if (!res.ok) continue;
            const data = await res.json();
            (data.people || []).forEach((p) => {
                if (p?.id) map[p.id] = p.fullName || p.lastFirstName || null;
            });
        } catch {
            /* names are cosmetic -- a failure just leaves the id */
        }
    }
    return map;
}

function normalizeSeasons(raw, fallback) {
    const parts = String(raw || fallback)
        .split(/[,|]/)
        .map((s) => parseInt(s.trim(), 10))
        .filter((n) => Number.isFinite(n) && n >= 2015 && n <= 2100);
    const seasons = parts.length ? [...new Set(parts)].sort() : [fallback];
    return seasons;
}

exports.handler = async (event) => {
    if (event.httpMethod === "OPTIONS") {
        return { statusCode: 204, headers: HEADERS, body: "" };
    }
    if (event.httpMethod !== "GET") {
        return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: "GET only" }) };
    }

    const q = event.queryStringParameters || {};
    const playerId = parseInt(q.playerId || "", 10);
    if (!playerId || playerId < 0) {
        return { statusCode: 400, headers: HEADERS, body: JSON.stringify({ error: "playerId required" }) };
    }
    const role = q.role === "pitcher" ? "pitcher" : "batter";
    const seasons = normalizeSeasons(q.season, new Date().getFullYear());
    const lookup = role === "batter" ? "batters_lookup" : "pitchers_lookup";

    const url = SEARCH_URL.replace("{role}", role)
        .replace("{seasons}", seasons.map((s) => `${s}%7C`).join(""))
        .replace("{lookup}", lookup)
        .replace("{playerId}", String(playerId));

    try {
        const res = await fetch(url, { headers: { "User-Agent": "WorstPickz-Research/1.0" } });
        if (!res.ok) throw new Error(`Savant ${res.status}`);
        const text = await res.text();
        if (!text.trim() || text.trimStart().startsWith("<!")) {
            return {
                statusCode: 200,
                headers: HEADERS,
                body: JSON.stringify({ playerId, role, seasons, pitches: 0, empty: true }),
            };
        }
        const rows = parseCsv(text).filter((r) => r.game_date);
        rows.sort((a, b) => String(a.game_date).localeCompare(String(b.game_date)));
        if (!rows.length) {
            return {
                statusCode: 200,
                headers: HEADERS,
                body: JSON.stringify({ playerId, role, seasons, pitches: 0, empty: true }),
            };
        }

        // A batter's platoon split keys off the pitcher's hand and vice versa.
        const handKey = role === "batter" ? "p_throws" : "stand";
        const vsL = rows.filter((r) => r[handKey] === "L");
        const vsR = rows.filter((r) => r[handKey] === "R");

        const all = buildZoneGrid(rows);
        const mix = buildPitchTypes(rows);
        const battedBalls = buildBattedBalls(rows, role);
        const names = await resolveNames(battedBalls.map((b) => b.oppId));
        battedBalls.forEach((b) => {
            if (b.oppId && names[b.oppId]) b.oppName = names[b.oppId];
        });

        const payload = {
            playerId,
            playerName: rows[rows.length - 1].player_name || null,
            role,
            seasons,
            source: "savant-player-detail",
            pitches: all.pitches,
            firstGame: rows[0].game_date,
            lastGame: rows[rows.length - 1].game_date,
            hand: role === "batter" ? rows[0].stand || null : rows[0].p_throws || null,
            zones: all.zones,
            zonesVsL: buildZoneGrid(vsL).zones,
            zonesVsR: buildZoneGrid(vsR).zones,
            zonePitchesVsL: vsL.length,
            zonePitchesVsR: vsR.length,
            pitchTypes: mix.pitchTypes,
            pitchTypesVsL: buildPitchTypes(vsL).pitchTypes,
            pitchTypesVsR: buildPitchTypes(vsR).pitchTypes,
            battedBalls,
        };
        return { statusCode: 200, headers: HEADERS, body: JSON.stringify(payload) };
    } catch (err) {
        return {
            statusCode: 502,
            headers: HEADERS,
            body: JSON.stringify({ error: String(err.message || err) }),
        };
    }
};
