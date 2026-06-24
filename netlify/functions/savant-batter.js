/** Proxy Baseball Savant CSV → JSON (avoids browser CORS). */
const CUSTOM_CSV =
    "https://baseballsavant.mlb.com/leaderboard/custom" +
    "?year={season}&type=batter&filter=&min=10" +
    "&selections=player_id,player_name,woba,xwoba,xba,xiso,pa,home_run,k_percent,whiff_percent," +
    "barrel_batted_rate,hard_hit_percent,exit_velocity_avg,launch_angle_avg,sweet_spot_percent,flyballs_percent," +
    "groundballs_percent,linedrives_percent,flyballs,hr_flyball_percent" +
    "&chart=false&csv=true";

const EXPECTED_CSV =
    "https://baseballsavant.mlb.com/leaderboard/expected_statistics" +
    "?type=batter&year={season}&position=&team=&min=10&csv=true";

const BAT_CSV =
    "https://baseballsavant.mlb.com/leaderboard/custom" +
    "?year={season}&type=batter&filter=&min=10" +
    "&selections=player_id,avg_swing_speed,squared_up_contact,blasts_contact,solidcontact_percent" +
    "&chart=false&csv=true";

const HR_RAW_URL =
    "https://baseballsavant.mlb.com/leaderboard/home-runs" +
    "?player_type=Batter&year={season}&min=0&cat=adj_xhr&encode=raw";

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

function parseBatRow(row) {
    return {
        batSpeed: num(row?.avg_swing_speed),
        swingStrength: num(row?.squared_up_contact),
        solidContactPct: num(row?.solidcontact_percent),
        blastPct: num(row?.blasts_contact),
    };
}

function extractDataArray(html) {
    const match = html.match(/var\s+data\s*=\s*(\[)/);
    if (!match) return [];
    const start = match.index + match[0].length - 1;
    let depth = 0;
    for (let i = start; i < html.length; i++) {
        const ch = html[i];
        if (ch === "[") depth += 1;
        else if (ch === "]") {
            depth -= 1;
            if (depth === 0) return JSON.parse(html.slice(start, i + 1));
        }
    }
    return [];
}

function parseHrTrackerRow(row) {
    const xhr = num(row?.xhr);
    const hrTotal = num(row?.hr_total);
    const mostlyGone = num(row?.mostly_gone);
    const hrLuckDiff =
        xhr != null && hrTotal != null ? Math.round((xhr - hrTotal) * 10) / 10 : null;
    return {
        expectedHr: xhr,
        hrLuckDiff,
        mostlyGone: mostlyGone != null ? Math.trunc(mostlyGone) : null,
        noDoubters: num(row?.no_doubters) != null ? Math.trunc(num(row.no_doubters)) : null,
        doublers: num(row?.doubters) != null ? Math.trunc(num(row.doubters)) : null,
        nearHr: num(row?.non_hr_would_have_left) != null ? Math.trunc(num(row.non_hr_would_have_left)) : null,
        hrTrackerSource: "savant-hr",
    };
}

async function fetchHrTrackerLookup(season, ua) {
    const res = await fetch(HR_RAW_URL.replace("{season}", String(season)), { headers: ua });
    if (!res.ok) return {};
    const html = await res.text();
    const lookup = {};
    for (const row of extractDataArray(html)) {
        const pid = parseInt(row.player_id, 10);
        if (!pid) continue;
        const parsed = parseHrTrackerRow(row);
        if (parsed.expectedHr != null || parsed.nearHr != null || parsed.mostlyGone != null) {
            lookup[String(pid)] = parsed;
        }
    }
    return lookup;
}

function parseSavantRow(custom, expected, bat) {
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
    const pa = num(custom?.pa) ?? num(expected?.pa);
    const bip = num(expected?.bip);
    const bipPct = bip != null && pa > 0 ? Math.round((100 * bip) / pa * 10) / 10 : null;
    return {
        avg: ba,
        slg,
        iso,
        xwoba: num(custom?.xwoba) ?? num(expected?.est_woba),
        barrelPct: num(custom?.barrel_batted_rate),
        hardHitPct: num(custom?.hard_hit_percent),
        avgEV: num(custom?.exit_velocity_avg),
        launchAngle: num(custom?.launch_angle_avg),
        sweetSpotPct: num(custom?.sweet_spot_percent),
        batSpeed: bat?.batSpeed ?? null,
        swingStrength: bat?.swingStrength ?? null,
        solidContactPct: bat?.solidContactPct ?? null,
        blastPct: bat?.blastPct ?? null,
        bip,
        bipPct,
        fbPct: num(custom?.flyballs_percent),
        gbPct: num(custom?.groundballs_percent),
        ldPct: num(custom?.linedrives_percent),
        hrFbPct,
        kPct: num(custom?.k_percent),
        whiffPct: num(custom?.whiff_percent),
        pa,
        hr,
        recentForm: formDiff != null ? Math.round(formDiff * 1000) / 10 : null,
        source: "savant",
    };
}

async function fetchSavantLookup(season) {
    const ua = { "User-Agent": "WorstPickz-Research/1.0" };
    const [customRes, expectedRes, batRes] = await Promise.all([
        fetch(CUSTOM_CSV.replace("{season}", String(season)), { headers: ua }),
        fetch(EXPECTED_CSV.replace("{season}", String(season)), { headers: ua }),
        fetch(BAT_CSV.replace("{season}", String(season)), { headers: ua }),
    ]);
    if (!customRes.ok || !expectedRes.ok || !batRes.ok) {
        throw new Error(`Savant CSV ${customRes.status}/${expectedRes.status}/${batRes.status}`);
    }
    const customRows = parseCsv(await customRes.text());
    const expectedRows = parseCsv(await expectedRes.text());
    const batRows = parseCsv(await batRes.text());
    const expectedById = {};
    for (const row of expectedRows) {
        const pid = parseInt(row.player_id, 10);
        if (pid) expectedById[pid] = row;
    }
    const batById = {};
    for (const row of batRows) {
        const pid = parseInt(row.player_id, 10);
        if (pid) batById[pid] = parseBatRow(row);
    }
    const lookup = {};
    for (const row of customRows) {
        const pid = parseInt(row.player_id, 10);
        if (!pid) continue;
        lookup[String(pid)] = parseSavantRow(row, expectedById[pid], batById[pid]);
    }
    for (const row of expectedRows) {
        const pid = parseInt(row.player_id, 10);
        if (!pid || lookup[String(pid)]) continue;
        lookup[String(pid)] = parseSavantRow(null, row, batById[pid]);
    }
    try {
        const hrLookup = await fetchHrTrackerLookup(season, ua);
        for (const [pid, hrStats] of Object.entries(hrLookup)) {
            lookup[pid] = { ...(lookup[pid] || { source: "savant" }), ...hrStats };
        }
    } catch (_) {}
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
