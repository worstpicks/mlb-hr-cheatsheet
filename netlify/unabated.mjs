// Server-only adapter shared by Discord and the Netlify betslip endpoint.
const BASE = 'https://data.unabated.com';
const UUID = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;
export function safeLink(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' && !u.username && !u.password && !u.port &&
      ['www.gambly.com', 'gambly.com', 'sportsbook.fanduel.com'].includes(u.hostname)
      && value.length <= 2000 ? value : null;
  } catch { return null; }
}
// Only used for URLs returned by the authenticated provider, never user input.
export function sportsbookLink(value) {
  try {
    const u = new URL(value);
    return typeof value === 'string' && value.length <= 2000 && u.protocol === 'https:' &&
      !u.username && !u.password && !u.port && /^[a-z0-9.-]+\.[a-z]{2,}$/i.test(u.hostname) &&
      !/\.(local|localhost|internal|test|invalid)$/i.test(u.hostname) ? value : null;
  } catch { return null; }
}
export function sportsbookSlips(result) {
  return (Array.isArray(result.betSlips) ? result.betSlips : [])
    .filter(s => s && typeof s.book === 'string' && s.book.trim())
    .map(s => {
      const requested = Number.isInteger(s.legsRequested) && s.legsRequested > 0 ? s.legsRequested : null;
      const matched = Number.isInteger(s.legsMatched) && s.legsMatched >= 0 ? s.legsMatched : null;
      const selections = (Array.isArray(s.betslipBets) ? s.betslipBets : []).slice(0, 30).map(b =>
        [b.player, b.event, b.betType, b.periodType,
          b.odds?.points != null ? `Line ${b.odds.points}` : null,
          b.odds?.value != null ? `Odds ${b.odds.value}` : null].filter(Boolean).join(' · ').slice(0, 800));
      const legs = (Array.isArray(s.betslipBets) ? s.betslipBets : []).slice(0, 30).map(b => ({
        player: String(b.player || '').slice(0, 100), event: String(b.event || '').slice(0, 200),
        market: String(b.betType || '').slice(0, 100), odds: b.odds || null,
      }));
      return { book: s.book.trim().slice(0, 100), requested, matched, selections,
        legs,
        complete: requested !== null && matched === requested && selections.length === matched,
        odds: Number.isFinite(s.overallOdds) ? s.overallOdds : null,
        // Generated links already carry partner attribution. Preserve them verbatim.
        url: matched > 0 && requested >= matched && selections.length > 0 ? sportsbookLink(s.deepLink) : null };
    });
}
export function createUnabated({ key = process.env.UNABATED_API_KEY,
  base = process.env.UNABATED_API_BASE_URL || BASE, fetchImpl = fetch } = {}) {
  if (!key || /^(your_|replace)/i.test(key)) throw new Error('Set UNABATED_API_KEY in the server environment.');
  if (base.replace(/\/$/, '') !== BASE) throw new Error('UNABATED_API_BASE_URL must be https://data.unabated.com.');
  async function request(path, options = {}) {
    let response;
    try {
      response = await fetchImpl(BASE + path, { ...options, redirect: 'error',
        headers: { 'X-Api-Key': key, 'Content-Type': 'application/json' }, signal: AbortSignal.timeout(20_000) });
    } catch { throw new Error('Unabated connection timed out or failed. Submission was not automatically retried.'); }
    if (!response.ok) {
      const labels = { 401: 'API key was rejected', 403: 'API tier or coverage does not allow this request',
        429: 'rate limit reached; wait before trying again', 503: 'service temporarily unavailable' };
      throw new Error(`Unabated HTTP ${response.status}: ${labels[response.status] || 'request failed'}.`);
    }
    try { return await response.json(); }
    catch { throw new Error('Unabated returned an unreadable response.'); }
  }
  return {
    async submit(text) {
      if (typeof text !== 'string' || !text.trim() || text.length > 12000) throw new Error('Use 1–12000 characters of bet selections.');
      const body = await request('/api/v1/bet/generate', { method: 'POST', body: JSON.stringify({
        type: 'text', generateMobileLinks: false, content: { text: text.trim() },
      }) });
      if (String(body.status).toLowerCase() === 'error' || !UUID.test(body.requestId ?? ''))
        throw new Error('Unabated could not accept this slip. Check the selections and API access.');
      return body.requestId;
    },
    async status(id) {
      if (!UUID.test(id)) throw new Error('Invalid betslip request ID.');
      const body = await request(`/api/v1/bet/status/${id}`);
      const status = String(body.status).toLowerCase();
      if (status === 'error') throw new Error('Unabated could not match this slip. Review the selection text.');
      if (!['processing', 'complete'].includes(status)) throw new Error('Unexpected Unabated processing status.');
      return { requestId: id, status, shareUrl: status === 'complete' ? safeLink(body.shareUrl) : null,
        slips: status === 'complete' ? sportsbookSlips(body) : [] };
    },
  };
}
export async function waitForSlip(client, id, { attempts = 30, sleep = ms => new Promise(r => setTimeout(r, ms)) } = {}) {
  for (let n = 0; n < attempts; n++) {
    const result = await client.status(id);
    if (result.status === 'complete') return result;
    await sleep(2000);
  }
  return { status: 'processing', requestId: id, slips: [] };
}
