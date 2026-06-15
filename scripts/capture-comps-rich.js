// Captures the RICH before/after gallery cards (model photos + product) at the
// exact frame aspect, so object-fit:cover is a no-op and nothing is cut:
//   desktop 1280x720 (16:9) -> 2560x1440 @2x
//   mobile  390x488  (4:5)  -> 780x976   @2x
const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");

const sizes = [
  { width: 1280, height: 670, suffix: "desktop" }, // 1280:670 (full-homepage reference)
  { width: 390, height: 488, suffix: "mobile" },
];
const comps = [
  { rel: "pages/comp-before-rich.html", name: "comp-rich-before" },
  { rel: "pages/comp-after-rich.html", name: "comp-rich-after" },
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
      const out = path.join(screenshots, `${name}-${suffix}.jpg`);
      await page.screenshot({
        path: out, type: "jpeg", quality: 88, animations: "disabled",
        clip: { x: 0, y: 0, width, height },
      });
      console.log(`${name}-${suffix}.jpg  ${width * 2}x${height * 2}`);
    }
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
