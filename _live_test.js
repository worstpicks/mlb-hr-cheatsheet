/* Live-site smoke test: research page + main sheet on worstpickz.win. */
const puppeteer = require("puppeteer");

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });

    for (const url of [
        "https://worstpickz.win/research/index.html?date=2026-07-02",
        "https://worstpickz.win/index.html",
    ]) {
        const page = await browser.newPage();
        const errors = [];
        const notFound = {};
        page.on("pageerror", (err) => errors.push(`PAGEERROR: ${err.message}`));
        page.on("console", (msg) => {
            if (msg.type() === "error") errors.push(msg.text());
        });
        page.on("response", (res) => {
            if (res.status() >= 400) {
                const u = new URL(res.url());
                notFound[`${res.status()} ${u.pathname}`] = (notFound[`${res.status()} ${u.pathname}`] || 0) + 1;
            }
        });
        await page.goto(url, { waitUntil: "networkidle2", timeout: 90000 });
        await new Promise((r) => setTimeout(r, 8000));
        const info = await page.evaluate(() => {
            const kCards = [...document.querySelectorAll(".rs-pitcher-k-card")]
                .filter((c) => c.querySelector(".rs-pitcher-k-card__label")?.textContent === "Exp K")
                .map((c) => c.querySelector(".rs-pitcher-k-card__score")?.textContent);
            return {
                title: document.title,
                textLen: document.body.innerText.length,
                expK: kCards,
                gaLoaded: typeof window.gtag === "function" || !!window.dataLayer,
            };
        });
        console.log("URL:", url);
        console.log("  title:", info.title, "| text:", info.textLen, "| GA:", info.gaLoaded);
        if (info.expK.length) console.log("  Exp K:", info.expK.join(", "));
        console.log("  errors:", errors.length);
        errors.slice(0, 8).forEach((e) => console.log("   ", e.slice(0, 150)));
        console.log("  4xx/5xx:", JSON.stringify(notFound));
        await page.close();
    }
    await browser.close();
})().catch((err) => {
    console.error("FAIL:", err);
    process.exit(1);
});
