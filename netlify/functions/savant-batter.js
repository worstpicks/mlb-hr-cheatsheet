/** Proxy Baseball Savant CSV → JSON (avoids browser CORS). */
const CUSTOM_CSV =
    "https://baseballsavant.mlb.com/leaderboard/custom" +
    "?year={season}&type=batter&filter=&min=10" +
    "&selections=player_id,player_name,woba,xwoba,xba,xiso,pa,home_run,k_percent,whiff_percent," +
    "barrel_batted_rate,hard_hit_percent,exit_velocity_avg,flyballs_percent," +
    "groundballs_percent,linedrives_percent,flyballs,hr_flyball_percent" +
    "&chart=false&csv=true";

const EXPECTED_CSV =
    "https://baseballsavant.mlb.com/leaderboard/expected_statistics" +
    "?type=batter&year={season}&position=&team=&min=10&csv=true";

const HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Cache-Control": "public, max-age=300",
};

function num(val) {
    if (val == null || val === "" || val === "-") return null;
    const n = parseFloat(String(val).replace("%", ""));
    return Number.isFinite(n) ? n : null;
}

function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/);
    if (!lines.length) return [];
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

function parseSavantRow(custom, expected) {
    const hr = num(custom?.home_run);
    const flyballs = num(custom?.flyballs);
    let hrFbPct = num(custom?.hr_flyball_percent);
    if (hrFbPct == null && hr != null && flyballs > 0) {
        hrFbPct = Math.round((100 * hr) / flyballs * 10) / 10;
    }
    const ba = num(expected?.ba);
    const slg = num(expected?.slg);
    const iso = ba != null && slg != null ? +(slg - ba).toFixed(3) : num(custom?.xiso);
    const formDiff = num(expected?.est_woba_minus_woba_diff);
    return {
        avg: ba,
        iso,
        xwoba: num(custom?.xwoba) ?? num(expected?.est_woba),
        barrelPct: num(custom?.barrel_batted_rate),
        hardHitPct: num(custom?.hard_hit_percent),
        avgEV: num(custom?.exit_velocity_avg),
        fbPct: num(custom?.flyballs_percent),
        gbPct: num(custom?.groundballs_percent),
        ldPct: num(custom?.linedrives_percent),
        hrFbPct,
        kPct: num(custom?.k_percent),
        whiffPct: num(custom?.whiff_percent),
        pa: num(custom?.pa) ?? num(expected?.pa),
        hr,
        recentForm: formDiff != null ? Math.round(formDiff * 1000) / 10 : null,
        source: "savant",
    };
}

async function fetchSavantLookup(season) {
    const ua = { "User-Agent": "WorstPickz-Research/1.0" };
    const [customRes, expectedRes] = await Promise.all([
        fetch(CUSTOM_CSV.replace("{season}", String(season)), { headers: ua }),
        fetch(EXPECTED_CSV.replace("{season}", String(season)), { headers: ua }),
    ]);
    if (!customRes.ok || !expectedRes.ok) {
        throw new Error(`Savant CSV ${customRes.status}/${expectedRes.status}`);
    }
    const customRows = parseCsv(await customRes.text());
    const expectedRows = parseCsv(await expectedRes.text());
    const expectedById = {};
    for (const row of expectedRows) {
        const pid = parseInt(row.player_id, 10);
        if (pid) expectedById[pid] = row;
    }
    const lookup = {};
    for (const row of customRows) {
        const pid = parseInt(row.player_id, 10);
        if (!pid) continue;
        lookup[String(pid)] = parseSavantRow(row, expectedById[pid]);
    }
    for (const row of expectedRows) {
        const pid = parseInt(row.player_id, 10);
        if (!pid || lookup[String(pid)]) continue;
        lookup[String(pid)] = parseSavantRow(null, row);
    }
    return lookup;
}

exports.handler = async (event) => {
    if (event.httpMethod === "OPTIONS") {
        return { statusCode: 204, headers: HEADERS, body: "" };
    }
    if (event.httpMethod !== "GET") {
        return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: "GET only" }) };
    }
    const season = parseInt(event.queryStringParameters?.season || "2026", 10);
    try {
        const lookup = await fetchSavantLookup(season);
        return {
            statusCode: 200,
            headers: HEADERS,
            body: JSON.stringify({
                season,
                source: "savant-csv-proxy",
                batters: Object.keys(lookup).length,
                lookup,
            }),
        };
    } catch (err) {
        return {
            statusCode: 502,
            headers: HEADERS,
            body: JSON.stringify({ error: String(err.message || err) }),
        };
    }
};
