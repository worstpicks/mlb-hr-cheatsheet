/* Screenshot the straight-of-day card: as-is, and with hot border forced for preview. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 900 });
    await page.goto("http://localhost:8123/index.html", { waitUntil: "networkidle2", timeout: 90000 });
    await new Promise((r) => setTimeout(r, 8000));
    const card = await page.$(".straight-of-day-card");
    await card.screenshot({ path: "_straights-card-current.png" });
    await page.evaluate(() => {
        const hero = document.querySelector(".straight-pick-hero:not(.straight-pick-hero--o15)");
        hero.classList.add("straight-streak-hot");
        const b = hero.querySelector(".straight-streak-badge");
        b.textContent = "🔥 3 days";
        b.classList.remove("straight-streak-badge--zero");
    });
    await new Promise((r) => setTimeout(r, 900));
    await card.screenshot({ path: "_straights-card-hot-preview.png" });
    await browser.close();
    console.log("shots saved");
})().catch((err) => {
    console.error("SHOT FAIL:", err);
    process.exit(1);
});
