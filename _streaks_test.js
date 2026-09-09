/* Headless check: straight-of-day streak badges + last-7 trackers render. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (err) => errors.push(`PAGEERROR: ${err.message}`));
    page.on("console", (msg) => {
        if (msg.type() === "error") errors.push(msg.text());
    });

    const url = process.argv[2] || "http://localhost:8123/index.html";
    await page.goto(url, { waitUntil: "networkidle2", timeout: 90000 });
    await new Promise((r) => setTimeout(r, 8000));

    const result = await page.evaluate(() => {
        const heroes = [...document.querySelectorAll(".straight-of-day-card .straight-pick-hero")];
        return heroes.map((h) => ({
            tag: h.querySelector(".straight-pick-tag")?.textContent,
            badge: h.querySelector(".straight-streak-badge")?.textContent,
            badgeTitle: h.querySelector(".straight-streak-badge")?.title,
            hot: h.classList.contains("straight-streak-hot"),
            last7: h.querySelector(".straight-last7")?.textContent,
            last7Titles: [...h.querySelectorAll(".straight-last7__day")].map((d) => d.title),
        }));
    });

    console.log(JSON.stringify(result, null, 2));
    console.log("PAGE ERRORS:", errors.length);
    errors.slice(0, 10).forEach((e) => console.log("  ERR:", e));
    await browser.close();
    if (!result.length || result.some((r) => !r.badge || !r.last7)) {
        console.error("STREAK TEST FAIL: missing badge or last-7 tracker");
        process.exit(1);
    }
    console.log("STREAK TEST OK");
})().catch((err) => {
    console.error("STREAK TEST FAIL:", err);
    process.exit(1);
});
