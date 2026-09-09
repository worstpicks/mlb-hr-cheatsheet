/* Interaction test: profile modal, explore tabs, search, game switching. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (err) => errors.push(`PAGEERROR: ${err.message}`));
    page.on("console", (msg) => {
        if (msg.type() === "error" && !msg.text().includes("404")) errors.push(msg.text());
    });

    await page.goto("http://localhost:8080/research/index.html?date=2026-07-02", {
        waitUntil: "networkidle2",
        timeout: 90000,
    });
    await new Promise((r) => setTimeout(r, 8000));

    const step = async (name, fn) => {
        try {
            const out = await fn();
            console.log(`OK ${name}${out ? ": " + out : ""}`);
        } catch (err) {
            console.log(`FAIL ${name}: ${err.message}`);
        }
    };

    await step("click second game pill", async () => {
        const cards = await page.$$(".rs-game-pill");
        if (cards.length < 2) throw new Error(`only ${cards.length} game els`);
        await cards[1].click();
        await new Promise((r) => setTimeout(r, 1500));
        return `${cards.length} games`;
    });

    await step("open hitter profile from table", async () => {
        const clicked = await page.evaluate(() => {
            const b = document.querySelector(".rs-hitter-btn");
            if (!b) return false;
            b.click();
            return true;
        });
        if (!clicked) throw new Error("no hitter button found");
        await new Promise((r) => setTimeout(r, 2500));
        const visible = await page.evaluate(() => {
            const el = document.querySelector("#rsPlayerProfile, .rs-profile, .rs-modal");
            if (!el) return "no profile el";
            const style = getComputedStyle(el);
            return el.hidden || style.display === "none" ? "hidden" : "visible";
        });
        if (visible !== "visible") throw new Error(`profile ${visible}`);
    });

    await step("close profile", async () => {
        await page.keyboard.press("Escape");
        await new Promise((r) => setTimeout(r, 800));
    });

    await step("search for a player", async () => {
        const input = await page.$("#rsSearch, input[type='search'], .rs-search input");
        if (!input) throw new Error("no search input");
        await input.type("a", { delay: 40 });
        await new Promise((r) => setTimeout(r, 1200));
        const items = await page.$$(".rs-search-item");
        return `${items.length} results`;
    });

    await step("explore/leaderboard rows render", async () => {
        const rows = await page.$$(".rs-leaderboard-row");
        return `${rows.length} leaderboard rows`;
    });

    await step("pitcher K cards sane", async () => {
        const bad = await page.evaluate(() => {
            const cards = [...document.querySelectorAll(".rs-pitcher-k-card")];
            const exp = cards.filter((c) =>
                c.querySelector(".rs-pitcher-k-card__label")?.textContent === "Exp K"
            );
            return exp
                .map((c) => parseFloat(c.querySelector(".rs-pitcher-k-card__score")?.textContent))
                .filter((v) => !Number.isNaN(v) && v < 1).length;
        });
        if (bad > 0) throw new Error(`${bad} Exp K cards below 1`);
    });

    console.log("PAGEERRORS:", errors.length);
    errors.slice(0, 10).forEach((e) => console.log("  ", e));
    await browser.close();
})().catch((err) => {
    console.error("TEST FAIL:", err);
    process.exit(1);
});
