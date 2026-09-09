/* Headless smoke test: load research page, capture console errors, check K projections. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    const errors = [];
    const warnings = [];
    page.on("console", (msg) => {
        if (msg.type() === "error") errors.push(msg.text());
        if (msg.type() === "warning") warnings.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(`PAGEERROR: ${err.message}`));
    page.on("requestfailed", (req) => {
        errors.push(`REQFAIL: ${req.url()} ${req.failure()?.errorText || ""}`);
    });
    const notFound = {};
    page.on("response", (res) => {
        if (res.status() === 404) {
            const u = new URL(res.url());
            const key = u.pathname;
            notFound[key] = (notFound[key] || 0) + 1;
        }
    });

    await page.goto("http://localhost:8080/research/index.html?date=2026-07-02", {
        waitUntil: "networkidle2",
        timeout: 90000,
    });
    // let async hydration (trends, matchup edge) settle
    await new Promise((r) => setTimeout(r, 15000));

    const result = await page.evaluate(() => {
        const cards = [...document.querySelectorAll(".rs-pitcher-k-card")];
        const kCards = cards.map((c) => ({
            label: c.querySelector(".rs-pitcher-k-card__label")?.textContent,
            score: c.querySelector(".rs-pitcher-k-card__score")?.textContent,
            sub: c.querySelector(".rs-pitcher-k-card__sub")?.textContent,
        }));
        const games = document.querySelectorAll(".rs-game-card, [data-game]").length;
        const tableRows = document.querySelectorAll("tbody tr").length;
        const status = document.querySelector("#rsStatus, .rs-status")?.textContent?.trim() || "";
        return { kCards, games, tableRows, status };
    });

    console.log("STATUS:", result.status || "(empty)");
    console.log("GAME ELS:", result.games, "TABLE ROWS:", result.tableRows);
    console.log("K CARDS:", JSON.stringify(result.kCards));
    console.log("CONSOLE ERRORS:", errors.length);
    errors.slice(0, 20).forEach((e) => console.log("  ERR:", e));
    console.log("CONSOLE WARNINGS:", warnings.length);
    warnings.slice(0, 10).forEach((w) => console.log("  WARN:", w));
    console.log("404s BY PATH:", JSON.stringify(notFound, null, 1));
    await browser.close();
})().catch((err) => {
    console.error("SMOKE FAIL:", err);
    process.exit(1);
});
