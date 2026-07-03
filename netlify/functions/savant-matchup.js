/** Proxy Baseball Savant batter-vs-pitcher career statcast history → JSON. */
const SEARCH_URL =
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=batter" +
    "&hfGT=R%7C&min_pitches=0&min_results=1" +
    "&group_by=name&sort_col=pitches&sort_order=desc" +
    "&batters_lookup%5B%5D={batter}&pitchers_lookup%5B%5D={pitcher}";

const HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    // Career matchup history changes slowly — let the CDN cache it for an hour.
    "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
};

function num(val) {
    if (val == null || val === "" || val === "-") return null;
    const n = parseFloat(String(val).replace("%", ""));
    return Number.isFinite(n) ? n : null;
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

function parseMatchupRow(row) {
    const whiff = num(row.whiff_percent) ?? num(row.swing_miss_percent);
    return {
        pitches: num(row.pitches) != null ? Math.trunc(num(row.pitches)) : 0,
        pa: num(row.pa) != null ? Math.trunc(num(row.pa)) : null,
        xwoba: num(row.xwoba),
        woba: num(row.woba),
        whiffPct: whiff,
        barrelPct: num(row.barrel_batted_rate) ?? num(row.barrels_per_pa_percent),
        avgEV: num(row.exit_velocity_avg),
        source: "savant-matchup",
    };
}

exports.handler = async (event) => {
    if (event.httpMethod === "OPTIONS") {
        return { statusCode: 204, headers: HEADERS, body: "" };
    }
    if (event.httpMethod !== "GET") {
        return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: "GET only" }) };
    }
    const batterId = parseInt(event.queryStringParameters?.batterId || "", 10);
    const pitcherId = parseInt(event.queryStringParameters?.pitcherId || "", 10);
    if (!batterId || !pitcherId || batterId < 0 || pitcherId < 0) {
        return {
            statusCode: 400,
            headers: HEADERS,
            body: JSON.stringify({ error: "batterId and pitcherId required" }),
        };
    }
    const key = `${batterId}|${pitcherId}`;
    try {
        const url = SEARCH_URL.replace("{batter}", String(batterId)).replace(
            "{pitcher}",
            String(pitcherId)
        );
        const res = await fetch(url, { headers: { "User-Agent": "WorstPickz-Research/1.0" } });
        if (!res.ok) throw new Error(`Savant ${res.status}`);
        const text = await res.text();
        if (!text.trim() || text.trimStart().startsWith("<!")) {
            return { statusCode: 200, headers: HEADERS, body: JSON.stringify({ key, matchup: null }) };
        }
        const rows = parseCsv(text);
        if (!rows.length) {
            return { statusCode: 200, headers: HEADERS, body: JSON.stringify({ key, matchup: null }) };
        }
        return {
            statusCode: 200,
            headers: HEADERS,
            body: JSON.stringify({ key, source: "savant-matchup", matchup: parseMatchupRow(rows[0]) }),
        };
    } catch (err) {
        return {
            statusCode: 502,
            headers: HEADERS,
            body: JSON.stringify({ error: String(err.message || err) }),
        };
    }
};
