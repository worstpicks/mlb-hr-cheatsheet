// Netlify: exit 0 skips; exit 1 builds. Uncertain comparisons always build.
import { spawnSync } from 'node:child_process';

const { CACHED_COMMIT_REF: previous, COMMIT_REF: current } = process.env;
if (!previous || !current || previous === current) process.exit(1);
const result = spawnSync('git', ['diff', '--quiet', previous, current, '--',
  'preview', 'netlify', 'tools', 'netlify.toml',
  'package.json', 'package-lock.json', 'npm-shrinkwrap.json', 'yarn.lock',
  'pnpm-lock.yaml', '.npmrc', '.nvmrc', '.node-version',
], { stdio: 'inherit' });
process.exit(result.status === 0 ? 0 : 1);
