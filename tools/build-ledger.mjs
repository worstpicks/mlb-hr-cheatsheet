import { cp, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { siteNavigation } from './site-navigation.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = path.join(root, 'preview');
const output = path.join(root, 'dist');
await mkdir(output, { recursive: true });
await cp(source, output, { recursive: true });
let pages = 0;
async function visit(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) { await visit(file); continue; }
    if (!entry.name.endsWith('.html')) continue;
    let html = await readFile(file, 'utf8');
    if (!html.includes('</body>')) continue;
    if (!html.includes('aria-label="Sports navigation"')) {
      const page = '/' + path.relative(output, file).split(path.sep).join('/');
      html = html.replace('</head>', '<link rel="stylesheet" href="/site-navigation.css?v=20261024">\n</head>')
        .replace(/<body\b[^>]*>/i, tag => tag + '\n' + siteNavigation(page));
    }
    const assets = '<link rel="stylesheet" href="/goblins-ledger.css?v=20261009">\n<script type="module" src="/goblins-ledger.js?v=20261009"></script>\n';
    if (!html.includes('src="/goblins-ledger.js')) html = html.replace('</body>', assets + '</body>');
    await writeFile(file, html);
    pages++;
  }
}
await visit(output);
console.log(`Goblin's Ledger added to ${pages} pages. Source sheets preserved.`);
