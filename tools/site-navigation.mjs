const destinations = [
  ['NBA', '/nba-research/prop-shop.html', '/nba-research/index.html'],
  ['NHL', '/nhl-research/atgs.html', '/nhl-research/index.html'],
  ['NFL', '/nfl-research/atd.html', '/nfl-research/index.html'],
  ['MLB', '/index.html', '/research/index.html'],
];

export function siteNavigation(page) {
  const current = page.startsWith('/archive/') ? '/index.html'
    : /\/(?:archive|prop-shop-archive)\//.test(page) ? destinations.find(([, sheet]) => page.startsWith(sheet.slice(0, sheet.lastIndexOf('/') + 1)))?.[1]
    : page;
  const rows = ['Cheat sheets', 'Research'].map((label, index) =>
    `<div class="wp-site-nav__row"><span class="wp-site-nav__label">${label}</span><div class="wp-site-nav__links">${destinations.map(([sport, ...urls]) =>
      `<a href="${urls[index]}"${current === urls[index] ? ' aria-current="page"' : ''} aria-label="${sport} ${label.toLowerCase()}">${sport}</a>`
    ).join('')}</div></div>`
  ).join('');
  return `<nav class="wp-site-nav" aria-label="Sports navigation">${rows}</nav>`;
}
