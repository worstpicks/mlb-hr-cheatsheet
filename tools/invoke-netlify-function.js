/**
 * Dev-only helper: run a Netlify function handler from the CLI.
 *
 * `serve-research.py` shells out to this so local research runs the exact same
 * handler code the deployed site does, instead of a Python reimplementation
 * that could drift.
 *
 *   node tools/invoke-netlify-function.js savant-player-detail '{"playerId":"624413"}'
 *
 * Lives outside netlify/functions/ on purpose: everything in that directory is
 * bundled as a deployed function, and this file has no handler to export.
 *
 * Prints the JSON body on stdout and exits non-zero on handler failure.
 */
const path = require("path");

const FUNCTIONS_DIR = path.join(__dirname, "..", "netlify", "functions");

async function main() {
    const [, , name, rawQuery] = process.argv;
    if (!name || !/^[a-z0-9-]+$/.test(name)) {
        process.stderr.write("usage: invoke-netlify-function.js <function-name> [query-json]\n");
        process.exit(2);
    }
    let query = {};
    if (rawQuery) {
        try {
            query = JSON.parse(rawQuery);
        } catch (err) {
            process.stderr.write(`bad query json: ${err.message}\n`);
            process.exit(2);
        }
    }
    const mod = require(path.join(FUNCTIONS_DIR, `${name}.js`));
    if (typeof mod.handler !== "function") {
        process.stderr.write(`${name} has no exported handler\n`);
        process.exit(2);
    }
    const res = await mod.handler({ httpMethod: "GET", queryStringParameters: query });
    process.stdout.write(res.body || "");
    process.exit(res.statusCode >= 400 ? 1 : 0);
}

main().catch((err) => {
    process.stderr.write(String(err?.stack || err) + "\n");
    process.exit(1);
});
