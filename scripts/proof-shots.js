// Capture proof screenshots of the slider fix at the problem viewports.
const { chromium } = require("playwright");
const { pathToFileURL } = require("url");
const path = require("path");

const url = pathToFileURL(path.resolve(__dirname, "..", "index.html")).href;
const out = path.resolve(__dirname, "..", "tmp");

async function shot(w, h, mode, pos, file) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto(url, { waitUntil: "load" });
  await page.click(`[data-mode="${mode}"]`);
  await page.evaluate((p) => {
    const r = document.querySelector("[data-comparison] .comparison-range");
    r.value = String(p);
    r.dispatchEvent(new Event("input", { bubbles: true }));
  }, pos);
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, file), animations: "disabled" });
  console.log("saved", file);
  await browser.close();
}

(async () => {
  await shot(1340, 800, "desktop", 100, "fix-desktop-slider100.png");
  await shot(390, 740, "mobile", 50, "fix-mobile.png");
})().catch((e) => { console.error(e); process.exit(1); });
