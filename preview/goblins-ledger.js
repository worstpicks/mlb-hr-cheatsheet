import { makePick, mergePicks, matchingText, footballMarket } from './ledger-model.mjs';

const STORAGE = 'worstpickz-goblins-ledger-v1';
let picks = [];
try { picks = mergePicks([], JSON.parse(localStorage.getItem(STORAGE) || '[]').map(makePick)); } catch {}
const buttonPicks = new WeakMap();
let busy = false, job = null, lastFocus = null;
const el = (tag, text, cls) => { const node = document.createElement(tag); if (text != null) node.textContent = text; if (cls) node.className = cls; return node; };
const decode = value => { try { return decodeURIComponent(value || ''); } catch { return value || ''; } };
const setText = (node, value) => { if (node && node.textContent !== value) node.textContent = value; };
const fab = el('button', '', 'gl-fab'); fab.type = 'button'; fab.append(el('b', 'Bet slip'), el('span', String(picks.length)));
fab.setAttribute('aria-haspopup', 'dialog'); fab.setAttribute('aria-label', 'Open bet slip');
const dialog = el('dialog', null, 'gl-dialog'); dialog.setAttribute('aria-labelledby', 'gl-title');
const header = el('header', null, 'gl-header'), headingWrap = el('div');
const title = el('h2', 'Your bet slip'); title.id = 'gl-title';
const subtitle = el('p', 'Picks from every cheat sheet, together in one place.', 'gl-sub');
headingWrap.append(el('div', 'WORSTPICKZ / THE GOBLIN’S LEDGER', 'gl-kicker'), title, subtitle);
const close = el('button', 'Close', 'gl-close'); close.type = 'button'; header.append(headingWrap, close);
const body = el('div', null, 'gl-body'), list = el('ul', null, 'gl-list'), results = el('div');
const status = el('p', '', 'gl-status'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
body.append(list, status, results);
const footer = el('footer', null, 'gl-footer'), clear = el('button', 'Clear picks', 'gl-secondary'); clear.type = 'button';
const generate = el('button', "Open the Goblin's Ledger", 'gl-primary'); generate.type = 'button';
footer.append(clear, generate); dialog.append(header, body, footer); document.body.append(fab, dialog);

function notify(message) {
  document.querySelector('.gl-toast')?.remove();
  const toast = el('div', message, 'gl-toast'); toast.setAttribute('role', 'status'); document.body.append(toast);
  setTimeout(() => toast.remove(), 2200);
}
function persist() {
  try { localStorage.setItem(STORAGE, JSON.stringify(picks)); } catch { notify('Browser storage is unavailable; picks remain in this tab.'); }
  job = null; results.replaceChildren(); status.textContent = ''; title.textContent = 'Your bet slip';
  syncButtons(); renderPicks();
}
function changePick(pick) {
  if (busy) return notify('Wait for matching to finish before changing picks.');
  const exists = picks.some(p => p.id === pick.id);
  if (!exists && picks.length >= 40) return notify('Your slip can hold up to 40 picks.');
  picks = exists ? picks.filter(p => p.id !== pick.id) : mergePicks(picks, [pick]);
  persist(); notify(exists ? 'Removed from Bet slip' : `${pick.name} added to Bet slip`);
}
function syncButtons() {
  setText(fab.querySelector('span'), String(picks.length));
  document.querySelectorAll('.gl-add').forEach(button => {
    const pick = buttonPicks.get(button); if (!pick) return;
    const on = picks.some(p => p.id === pick.id), label = on ? 'Remove from Bet slip' : 'Add to Bet slip';
    setText(button, on ? '✓' : '+');
    if (button.getAttribute('aria-pressed') !== String(on)) button.setAttribute('aria-pressed', String(on));
    button.title = label; button.dataset.tooltip = label; button.setAttribute('aria-label', `${label}: ${pick.name}, ${pick.market}`);
    const checkbox = button.closest('.gambly-pick-wrap')?.querySelector('input'); if (checkbox) checkbox.checked = on;
  });
}
function displayDate(value) {
  if (!value) return '';
  const onlyDate = /^\d{4}-\d{2}-\d{2}$/.test(value);
  const date = new Date(onlyDate ? value + 'T12:00:00Z' : value);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric',
    ...(onlyDate ? {} : { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }) }).format(date);
}
function renderPicks() {
  list.replaceChildren();
  if (!picks.length) list.append(el('li', 'Tap a + on any cheat sheet to start your bet slip.', 'gl-empty'));
  for (const pick of picks) {
    const row = el('li', null, 'gl-pick'), details = el('div');
    details.append(el('strong', pick.name), el('div', pick.market, 'gl-market'),
      el('small', [pick.sport, pick.event, displayDate(pick.date)].filter(Boolean).join(' · ')));
    const remove = el('button', '×', 'gl-remove'); remove.type = 'button'; remove.setAttribute('aria-label', `Remove ${pick.name}, ${pick.market}`);
    remove.disabled = busy; remove.onclick = () => changePick(pick); row.append(details, remove); list.append(row);
  }
  generate.disabled = busy || !picks.length; clear.disabled = busy || !picks.length;
  generate.textContent = busy ? 'Matching your picks…' : "Open the Goblin's Ledger";
}
function openLedger() {
  lastFocus = document.activeElement; renderPicks();
  if (!dialog.open) dialog.showModal();
}
fab.onclick = openLedger; close.onclick = () => dialog.close();
dialog.addEventListener('close', () => { if (lastFocus?.isConnected) lastFocus.focus(); });
clear.onclick = () => { picks = []; persist(); };
window.addEventListener('storage', event => {
  if (event.key !== STORAGE || busy) return;
  try { picks = mergePicks([], JSON.parse(event.newValue || '[]').map(makePick)); job = null; results.replaceChildren(); syncButtons(); renderPicks(); } catch {}
});
async function call(payload) {
  const response = await fetch('/.netlify/functions/unabated-slip', { method: 'POST',
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(25000) });
  let result; try { result = await response.json(); } catch { throw new Error('The betslip service is unavailable. Try again shortly.'); }
  if (!response.ok) throw new Error(result.error || 'Could not match these picks.');
  return result;
}
function showResult(result) {
  results.replaceChildren();
  const slips = result.slips.filter(s => s.url);
  if (!slips.length && !result.shareUrl) { status.textContent = 'No sportsbook links were available. Check the dates and markets in your picks.'; return; }
  status.textContent = 'Choose your sportsbook, then review its matched picks and odds.';
  if (result.shareUrl) {
    const link = el('a', 'Open shared betslip ↗', 'gl-link'); link.href = result.shareUrl; link.target = '_blank'; link.rel = 'noopener noreferrer'; results.append(link);
  }
  if (!slips.length) return;
  results.append(el('p', 'AVAILABLE SPORTSBOOKS', 'gl-section-label'));
  const select = el('select', null, 'gl-books'); select.setAttribute('aria-label', 'Choose your sportsbook');
  const placeholder = el('option', 'Choose your sportsbook'); placeholder.value = ''; select.append(placeholder);
  slips.forEach((slip, i) => { const option = el('option', `${slip.book} · ${slip.matched ?? '?'}/${slip.requested ?? '?'} picks${slip.complete ? '' : ' · partial'}`); option.value = String(i); select.append(option); });
  const detail = el('div'); results.append(select, detail);
  select.onchange = () => {
    detail.replaceChildren(); if (select.value === '') return;
    const slip = slips[Number(select.value)], card = el('section', null, 'gl-result');
    card.append(el('h3', slip.book), el('p', `${slip.complete ? 'Ready for review' : 'Partial / unverified match'} — ${slip.matched ?? '?'} of ${slip.requested ?? '?'} picks matched.`));
    if (slip.odds !== null) card.append(el('p', `Returned combined odds: ${slip.odds > 0 ? '+' : ''}${slip.odds}`));
    const returned = el('ol'); slip.selections.forEach(s => returned.append(el('li', s))); card.append(returned);
    const link = el('a', `Open ${slip.book} ↗`, 'gl-link'); link.href = slip.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
    card.append(link, el('p', 'Review every selection at the sportsbook. Odds and availability can change; no bet has been placed.', 'gl-sub')); detail.append(card);
  };
}
generate.onclick = async () => {
  if (busy || !picks.length) return;
  busy = true; title.textContent = "The Goblin's Ledger"; renderPicks(); results.replaceChildren();
  const text = matchingText(picks);
  try {
    if (job?.expires <= Date.now()) { job = null; try { sessionStorage.removeItem('gl-pending'); } catch {} }
    if (!job || job.text !== text) {
      try { const saved = JSON.parse(sessionStorage.getItem('gl-pending')); if (saved?.text === text && saved.expires > Date.now()) job = saved; } catch {}
    }
    if (!job || job.text !== text) {
      status.textContent = 'Sending your selected picks to Unabated / Gambly…';
      const accepted = await call({ action: 'generate', text });
      job = { text, ticket: accepted.ticket, expires: Date.now() + 14 * 60000 };
      try { sessionStorage.setItem('gl-pending', JSON.stringify(job)); } catch {}
    }
    for (let n = 0; n < 24; n++) {
      status.textContent = 'Matching your picks across available sportsbooks…';
      const result = await call({ action: 'status', ticket: job.ticket });
      if (result.status === 'complete') { showResult(result); return; }
      if (!dialog.open) return;
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    status.textContent = 'Still matching. Open the Ledger again to check this request without resubmitting.';
  } catch (error) { status.textContent = error.message; }
  finally { busy = false; renderPicks(); }
};

function wire(button, pick) {
  if (!pick) return;
  button.type = 'button'; button.classList.add('gl-add'); buttonPicks.set(button, pick);
}
function addTo(container, pick) {
  if (!container || !pick || container.querySelector(':scope > .gl-add')) return;
  const button = el('button'); wire(button, pick); container.append(button);
}
function pageDate() {
  return (document.querySelector('#sheetDatePicker')?.value || document.querySelector('#rsDate')?.value) || window.ATGS_SHEET?.date || '';
}
function addLines(text) {
  const added = text.split('\n').filter(Boolean).map(line => {
    const split = line.match(/^(.+?)\s+[—–-]\s+(.+)$/);
    if (!split) return null;
    let pick = makePick({ sport: 'MLB', name: split[1], market: split[2], date: pageDate() });
    for (const button of document.querySelectorAll('.gl-add')) {
      const known = buttonPicks.get(button);
      if (known?.name === pick.name) { pick = makePick({ ...known, market: pick.market }); break; }
    }
    return pick;
  });
  picks = mergePicks(picks, added); persist(); openLedger();
}
function scanSheet() {
  document.querySelectorAll('[data-ledger-pick]').forEach(card => {
    try { addTo(card.querySelector('.sheet-top-card__head') || card, makePick(JSON.parse(card.dataset.ledgerPick))); } catch {}
  });
  document.querySelectorAll('.gambly-pick-btn').forEach(button => {
    if (buttonPicks.has(button)) return;
    const row = button.closest('.pick-row'); if (!row) return;
    const name = decode(row.dataset.gamblyBatter) || row.querySelector('.pick-name,.table-player-name')?.textContent?.replace(/^★\s*/, '').trim();
    const odds = decode(row.dataset.gamblyOdds) || row.querySelector('.pick-odds')?.textContent || '';
    const line = odds.match(/over\s+([\d.]+)\s*(?:hr|home)/i)?.[1] || '0.5';
    const game = document.getElementById(`game-${row.dataset.gi}`);
    const event = game?.querySelector('h3')?.textContent?.split(' - ')[0] || '';
    wire(button, makePick({ sport: 'MLB', name, market: `Over ${line} home runs`, event, date: pageDate() }));
  });
  for (const [sheet, sport] of [[window.ATD_SHEET, 'NFL'], [window.ATGS_SHEET, 'NHL']]) {
    if (!sheet?.games) continue;
    const players = new Map();
    for (const game of sheet.games) for (const side of Object.values(game.sides || {})) for (const player of side) players.set(String(player.id), { player, game });
    const selector = sport === 'NFL' ? '.atd-play,.atd-top-card' : '.sheet-play,.sheet-top-card';
    document.querySelectorAll(selector).forEach(card => {
      const nameNode = card.querySelector('[data-pid]'); const found = players.get(nameNode?.dataset.pid || card.dataset.id);
      if (!found) return;
      const { player, game } = found;
      const market = sport === 'NHL' ? (player.market || 'Over 0.5 goals') : footballMarket(player, card.classList.contains('atd-first-card') ? 'first' : card.classList.contains('atd-two-card') ? 'two' : '');
      const pick = makePick({ sport, name: player.name || player.n, market, event: `${game.away_name || game.away} @ ${game.home_name || game.home}`, date: game.kick || sheet.date || '' });
      addTo(card.querySelector('.atd-play__top,.atd-top-card__head,.sheet-play__head') || card, pick);
    });
  }
  document.querySelectorAll('#exportGamblySlip,#exportGambly').forEach(b => { setText(b, "Open the Goblin's Ledger"); b.disabled = !picks.length; });
  document.querySelectorAll('[data-goblin-gambly-lines],[data-parlay-gambly]').forEach(b => {
    if (b.dataset.glRelabeled) return; b.dataset.glRelabeled = '1'; b.title = 'Add these picks to Bet slip'; setText(b, '+ Add picks to Bet slip');
  });
  // Research exports already know each parlay's markets. Reuse their selected text,
  // then replace the old copy/paste modal with the common Ledger.
  document.querySelectorAll('#gamblyExportModal,.rs-gambly-modal').forEach(modal => {
    const text = modal.querySelector('textarea')?.value; if (!text) return;
    modal.remove(); addLines(text);
  });
  syncButtons();
}
document.addEventListener('click', event => {
  const button = event.target.closest('.gl-add');
  if (button && buttonPicks.has(button)) { event.preventDefault(); event.stopImmediatePropagation(); changePick(buttonPicks.get(button)); return; }
  const bundle = event.target.closest('[data-goblin-gambly-lines]');
  if (bundle) {
    event.preventDefault(); event.stopImmediatePropagation();
    if (busy) { notify('Wait for matching to finish before changing picks.'); return; }
    try { const lines = JSON.parse(bundle.getAttribute('data-goblin-gambly-lines')); if (Array.isArray(lines)) addLines(lines.join('\n')); } catch {}
    return;
  }
  if (event.target.closest('#exportGamblySlip,#exportGambly,#mySlipFab')) { event.preventDefault(); event.stopImmediatePropagation(); openLedger(); }
}, true);
let scheduled = false;
new MutationObserver(records => {
  if (records.every(r => dialog.contains(r.target) || fab.contains(r.target) || r.target.closest?.('.gl-add,.gl-toast'))) return;
  if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; scanSheet(); });
}).observe(document.body, { childList: true, subtree: true });
scanSheet(); renderPicks();
