/** Tonight's NBA player-prop lines for one game, from PropLine (prop-line.com, free key).
 *
 *  GET /api/nba-props/2026-10-20/BOS-DET?away=Boston%20Celtics&home=Detroit%20Pistons
 *
 *  The key stays server-side (Netlify env PROPLINE_API_KEY). Netlify's CDN keeps each
 *  game's answer for 30 minutes, so a busy night costs a handful of the 1,000 free
 *  requests a day: one events call plus one odds call (every market at once) per refresh.
 *
 *  For each player and market we pick one line: the first book in BOOKS that posts a
 *  main over/under (its pair closest to even money), with that book's prices. `best`
 *  holds the best over and under at the same line across every sportsbook. DFS apps
 *  (PrizePicks, Underdog, Pick6) post no real prices, so they never set either.
 */
const API = 'https://api.prop-line.com/v1/sports/basketball_nba';
const MARKETS = {
  player_points: 'pts', player_rebounds: 'reb', player_assists: 'ast', player_threes: 'threem',
  player_points_rebounds_assists: 'pra', player_points_rebounds: 'pr', player_points_assists: 'pa',
  player_rebounds_assists: 'ra', player_steals: 'stl', player_blocks: 'blk', player_turnovers: 'tov',
  player_double_double: 'dd', player_triple_double: 'td',
};
const BOOKS = ['draftkings', 'fanduel', 'fanatics', 'betmgm', 'caesars', 'hardrock', 'espnbet', 'pinnacle', 'bovada'];
const DFS = new Set(['prizepicks', 'underdog', 'pick6', 'sleeper', 'betr', 'dabble']);
const BOOK_NAME = { draftkings: 'DK', fanduel: 'FD', fanatics: 'Fanatics', betmgm: 'MGM', caesars: 'CZR', hardrock: 'Hard Rock', espnbet: 'ESPN', pinnacle: 'Pinnacle', bovada: 'Bovada', novig: 'Novig', prophetx: 'ProphetX', onexbet: '1xBet', rebet: 'Rebet', sportzino: 'Sportzino', courtside: 'Courtside' };

// `durable` shares one cached copy across every Netlify edge, so a refresh costs one PropLine call, not one per edge.
// Errors are held 2 minutes (errorSeconds), so a PropLine outage or a spent quota can't turn every page view into a call.
// They go out as 200 so the CDN will hold them; the page reads any answer without `players` as "no lines".
const json = (body, cdnSeconds, errorSeconds) => Response.json(body, {
  status: body.error && !errorSeconds ? 502 : 200,
  headers: cdnSeconds
    ? { 'Cache-Control': 'public, max-age=120', 'Netlify-CDN-Cache-Control': `public, durable, max-age=${cdnSeconds}, stale-while-revalidate=300` }
    : errorSeconds
      ? { 'Cache-Control': 'no-store', 'Netlify-CDN-Cache-Control': `public, durable, max-age=${errorSeconds}` }
      : { 'Cache-Control': 'no-store' },
});

// "Nikola Jokić", "Jaren Jackson Jr." and "Ausar Thompson (DET)" all reduce to plain lowercase words.
export const nameKey = (s) => String(s || '').replace(/\s*\([^)]*\)\s*$/, '').normalize('NFD').replace(/[̀-ͯ]/g, '')
  .toLowerCase().replace(/[.'’]/g, '').replace(/\b(jr|sr|ii|iii|iv)\b/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
const nickname = (s) => nameKey(s).split(' ').pop();
const prob = (a) => (a < 0 ? -a / (100 - a) : 100 / (a + 100));
const better = (a, b) => b == null || prob(a) < prob(b);

async function get(url, key) {
  const res = await fetch(url, { headers: { 'X-API-Key': key }, signal: AbortSignal.timeout(9000) });
  if (!res.ok) throw new Error(`PropLine ${res.status}`);
  return res.json();
}

const easternDay = (iso) => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(iso));

/** Every sportsbook's over/under pairs → one line per player and market. Exported for the local test. */
export function boardFrom(odds) {
  const pairs = {}; // player → market → book → line → {over, under}
  for (const book of odds.bookmakers || []) {
    if (DFS.has(book.key)) continue;
    for (const market of book.markets || []) {
      const stat = MARKETS[market.key];
      if (!stat) continue;
      for (const o of market.outcomes || []) {
        const yesNo = stat === 'dd' || stat === 'td';
        const side = yesNo ? { yes: 'over', no: 'under' }[String(o.name).toLowerCase()] : { over: 'over', under: 'under' }[String(o.name).toLowerCase()];
        const line = yesNo ? 0.5 : o.point;
        if (!side || !Number.isFinite(line) || !Number.isFinite(o.price) || !o.description) continue;
        const slot = ((((pairs[nameKey(o.description)] ??= {})[stat] ??= {})[book.key] ??= {})[line] ??= {});
        slot[side] = o.price;
      }
    }
  }
  const players = {};
  for (const [player, markets] of Object.entries(pairs)) {
    for (const [stat, books] of Object.entries(markets)) {
      // each book's main line: a full over/under pair, the one closest to even money
      const main = {};
      for (const [book, lines] of Object.entries(books)) {
        let best = null;
        for (const [line, p] of Object.entries(lines)) {
          if (p.over == null || p.under == null) continue;
          const gap = Math.abs(prob(p.over) - prob(p.under));
          if (!best || gap < best.gap) best = { line: Number(line), gap };
        }
        if (best) main[book] = best.line;
      }
      const source = BOOKS.find((b) => b in main) || Object.keys(main)[0];
      if (!source) continue;
      const line = main[source], own = books[source][line];
      const pick = { line, book: BOOK_NAME[source] || source, over: own.over, under: own.under, books: 0, best: {} };
      for (const [book, lines] of Object.entries(books)) {
        const p = lines[line];
        if (!p) continue;
        pick.books++;
        for (const side of ['over', 'under'])
          if (p[side] != null && better(p[side], pick.best[side])) Object.assign(pick.best, { [side]: p[side], [side + 'Book']: BOOK_NAME[book] || book });
      }
      (players[player] ??= {})[stat] = pick;
    }
  }
  return players;
}

export default async function handler(request, context) {
  const url = new URL(request.url);
  const key = process.env.PROPLINE_API_KEY;
  if (!key) return Response.json({ error: 'PROPLINE_API_KEY is not set.' }, { status: 503 });
  // The schedule changes rarely, so it has its own route that the CDN keeps for an hour. Game lookups read it
  // through the CDN, which leaves one PropLine request per game refresh (worst case ~15 games × 48 + 24 < 1,000/day).
  if (url.pathname === '/api/nba-props-events') {
    try {
      const events = await get(`${API}/events`, key);
      return json((Array.isArray(events) ? events : []).map(({ id, away_team, home_team, commence_time }) => ({ id, away_team, home_team, commence_time })), 3600);
    } catch (e) {
      return json({ error: String(e.message || e) }, 0, 120);
    }
  }
  const { date, matchup } = context.params || {};
  const away = url.searchParams.get('away') || '', home = url.searchParams.get('home') || '';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date || '') || !/^[A-Z]{2,4}-[A-Z]{2,4}$/.test(matchup || '') || !away || !home || away.length > 60 || home.length > 60)
    return Response.json({ error: 'Use /api/nba-props/YYYY-MM-DD/AWY-HOM?away=<team>&home=<team>.' }, { status: 400 });
  try {
    const listed = await fetch(`${url.origin}/api/nba-props-events`, { signal: AbortSignal.timeout(9000) });
    if (!listed.ok) throw new Error(`events ${listed.status}`);
    const events = await listed.json();
    const event = (Array.isArray(events) ? events : []).find((e) => nickname(e.away_team) === nickname(away) && nickname(e.home_team) === nickname(home) && easternDay(e.commence_time) === date);
    // Not posted yet: say so, and look again in 10 minutes rather than 30.
    if (!event) return json({ date, matchup, players: {}, note: 'No lines posted for this game yet.' }, 600);
    const odds = await get(`${API}/events/${encodeURIComponent(event.id)}/odds?markets=${Object.keys(MARKETS).join(',')}`, key);
    const players = boardFrom(odds);
    // 30 minutes even when the board is still empty: that's what keeps a game at ≤48 PropLine calls a day.
    return json({ date, matchup, built: new Date().toISOString(), source: 'PropLine', players }, 1800);
  } catch (e) {
    return json({ error: String(e.message || e) }, 0, 120);
  }
}

export const config = { path: ['/api/nba-props/:date/:matchup', '/api/nba-props-events'] };
