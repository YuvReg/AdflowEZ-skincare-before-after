// Captures the v4 rich premium hero cards at the EXACT reference frame aspects, so
// object-fit:cover is a no-op (nothing cut) and before/after share identical dims:
//   desktop 1280x670  -> 2560x1340 @2x   (matches reference .ba aspect 1280/670)
//   mobile  390x448   -> 780x896   @2x   (matches reference .ba aspect 390/448)
const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");

const sizes = [
  { width: 1280, height: 670, suffix: "desktop" }, // 1280:670 (reference desktop frame)
  { width: 390, height: 448, suffix: "mobile" },    // 390:448  (reference mobile frame)
];
const comps = [
  { rel: "pages/comp-v4-before.html", name: "comp-v4-before" },
  { rel: "pages/comp-v4-after.html", name: "comp-v4-after" },
];

async function waitReady(page) {
  await page.evaluate(async () => {
    await Promise.all(
      Array.from(document.images).map((img) =>
        img.complete && img.naturalWidth > 0
          ? Promise.resolve()
          : new Promise((res) => {
              img.addEventListener("load", res, { once: true });
              img.addEventListener("error", res, { once: true });
            }),
      ),
    );
    if (document.fonts && document.fonts.ready) {
      try { await document.fonts.ready; } catch (e) {}
    }
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  for (const { width, height, suffix } of sizes) {
    for (const { rel, name } of comps) {
      await page.setViewportSize({ width, height });
      await page.goto(pathToFileURL(path.join(root, rel)).href, { waitUntil: "load" });
      await waitReady(page);
      await page.waitForTimeout(150);
      const out = path.join(screenshots, `${name}-${suffix}.jpg`);
      await page.screenshot({
        path: out, type: "jpeg", quality: 90, animations: "disabled",
        clip: { x: 0, y: 0, width, height },
      });
      console.log(`${name}-${suffix}.jpg  ${width * 2}x${height * 2}`);
    }
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
