/* Smoke test for the main cheatsheet landing page. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (err) => errors.push(`PAGEERROR: ${err.message}`));
    page.on("console", (msg) => {
        if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto("http://localhost:8080/index.html", {
        waitUntil: "networkidle2",
        timeout: 60000,
    });
    await new Promise((r) => setTimeout(r, 5000));
    const info = await page.evaluate(() => ({
        title: document.title,
        cards: document.querySelectorAll("article, .card, .game").length,
        bodyLen: document.body.innerText.length,
    }));
    console.log("TITLE:", info.title, "| cards:", info.cards, "| text len:", info.bodyLen);
    console.log("ERRORS:", errors.length);
    errors.slice(0, 10).forEach((e) => console.log("  ", e));
    await browser.close();
})().catch((err) => {
    console.error("FAIL:", err);
    process.exit(1);
});
