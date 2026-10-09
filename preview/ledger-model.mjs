export function makePick({ sport, name, market, event = '', date = '', odds = '' }) {
  if (!name?.trim() || !market?.trim()) return null;
  const pick = { sport: String(sport || '').slice(0, 12), name: name.trim().replace(/^★\s*/, '').replace(/\s*\([LRS]\)$/i, '').slice(0, 120),
    market: market.trim().replace(/\b(?:homeruns?|home runs?|hrs?)\b/ig, 'home runs').replace(/\bgoals\b/ig, 'goals').slice(0, 180), event: String(event).slice(0, 180), date: String(date).slice(0, 40), odds: String(odds).slice(0, 30) };
  pick.id = [pick.sport, pick.name, pick.market, pick.event, pick.date].join('|').toLowerCase();
  return pick;
}
export function mergePicks(current, added) {
  return [...new Map([...current, ...added].filter(Boolean).map(p => [p.id, p])).values()].slice(0, 40);
}
export function matchingText(picks) {
  return picks.map(p => [p.sport, p.name, p.market, p.event, p.date ? `Game date/time: ${p.date}` : ''].filter(Boolean).join(' — ')).join('\n');
}
export function footballMarket(player, variant = '') {
  if (variant === 'first') return 'First touchdown scorer';
  if (variant === 'two') return 'Over 1.5 touchdowns';
  if (player.mk === 'pass_td') return `Over ${player.line ?? 0.5} passing touchdowns`;
  if (player.mk === 'rush_td') return `Over ${player.line ?? 0.5} rushing touchdowns`;
  if (player.mk === 'td') return Number(player.line || 0.5) === 0.5 ? 'Anytime touchdown scorer' : `Over ${player.line} touchdowns`;
  return null;
}
