import { createHmac, timingSafeEqual } from 'node:crypto';
import { createUnabated } from '../unabated.mjs';
const json = (body, status = 200) => Response.json(body, { status, headers: { 'Cache-Control': 'no-store' } });
function sign(payload, key) { return createHmac('sha256', key).update('worstpickz-slip:' + payload).digest('base64url'); }
export function ticket(id, key) {
  const payload = Buffer.from(JSON.stringify({ id, expires: Date.now() + 15 * 60_000 })).toString('base64url');
  return payload + '.' + sign(payload, key);
}
export function verifyTicket(value, key) {
  if (typeof value !== 'string' || value.length > 1000) throw new Error('Invalid request ticket.');
  const [payload, signature] = value.split('.');
  if (value.split('.').length !== 2 || !payload || !signature) throw new Error('Invalid request ticket.');
  const expected = Buffer.from(sign(payload, key));
  const actual = Buffer.from(signature || '');
  if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) throw new Error('Invalid request ticket.');
  const job = JSON.parse(Buffer.from(payload, 'base64url').toString());
  if (!Number.isFinite(job.expires) || job.expires < Date.now()) throw new Error('Request expired.');
  return job.id;
}
export default async function handler(request) {
  if (request.method !== 'POST') return json({ error: 'Use POST.' }, 405);
  const origin = request.headers.get('origin');
  if (origin && origin !== new URL(request.url).origin) return json({ error: 'Origin not allowed.' }, 403);
  if (!request.headers.get('content-type')?.includes('application/json')) return json({ error: 'Use JSON.' }, 415);
  const raw = await request.text();
  if (raw.length > 16000) return json({ error: 'Slip is too large.' }, 413);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ error: 'Invalid JSON.' }, 400); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) return json({ error: 'Use a JSON object.' }, 400);
  try {
    const api = createUnabated();
    const key = process.env.UNABATED_API_KEY;
    if (body.action === 'generate') {
      const id = await api.submit(body.text);
      return json({ status: 'processing', ticket: ticket(id, key) });
    }
    if (body.action === 'status') {
      let id;
      try { id = verifyTicket(body.ticket, key); } catch { return json({ error: 'Invalid or expired request ticket.' }, 400); }
      return json(await api.status(id));
    }
    return json({ error: 'Unknown action.' }, 400);
  } catch (error) { return json({ error: error.message }, 502); }
}
export const config = { rateLimit: { windowLimit: 40, windowSize: 60, aggregateBy: ['ip', 'domain'] } };
