const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const shots = [
        { url: "http://127.0.0.1:8080/index.html", w: 1440, h: 1000, name: "_shot-sheet-desktop.png" },
        { url: "http://127.0.0.1:8080/index.html", w: 390, h: 844, name: "_shot-sheet-mobile.png", mobile: true },
        { url: "http://127.0.0.1:8080/research/index.html?date=2026-07-02", w: 1440, h: 1000, name: "_shot-research-desktop.png" },
        { url: "http://127.0.0.1:8080/research/index.html?date=2026-07-02", w: 390, h: 844, name: "_shot-research-mobile.png", mobile: true },
    ];
    for (const s of shots) {
        const page = await browser.newPage();
        await page.setViewport({ width: s.w, height: s.h, isMobile: !!s.mobile, hasTouch: !!s.mobile, deviceScaleFactor: 1 });
        await page.goto(s.url, { waitUntil: "networkidle2", timeout: 60000 });
        await new Promise((r) => setTimeout(r, 2500));
        await page.screenshot({ path: s.name, fullPage: false });
        console.log("saved", s.name);
        await page.close();
    }
    await browser.close();
})();
