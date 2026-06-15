const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");

// before/after captured to the bottom of the PRODUCT section (the clean hero +
// product + buy area shown in the client's reference), matched per orientation
// so the two line up and the slider shows the whole product view (no cropping).
// Captured at 2x device scale (sharp when enlarged) and saved as JPEG (so the
// embedded handoff file stays small/fast despite the higher resolution).
const pairs = [
  { width: 1280, before: "before-desktop.jpg", after: "after-desktop.jpg" },
  { width: 390, before: "before-mobile.jpg", after: "after-mobile.jpg" },
];
const SECTION = { before: ".starter-product", after: ".premium-product" };

const demos = [
  ["demo-desktop.png", "index.html", 1280, 900],
  ["demo-mobile.png", "index.html", 390, 1080],
];

async function waitForImages(page) {
  await page.evaluate(async () => {
    const images = Array.from(document.images);
    await Promise.all(
      images.map((img) => {
        if (img.complete && img.naturalWidth > 0) return Promise.resolve();
        return new Promise((resolve, reject) => {
          img.addEventListener("load", resolve, { once: true });
          img.addEventListener("error", reject, { once: true });
        });
      }),
    );
  });
}

async function sectionBottom(page, relativePath, width, selector) {
  await page.setViewportSize({ width, height: 900 });
  await page.goto(pathToFileURL(path.join(root, relativePath)).href, { waitUntil: "load" });
  await waitForImages(page);
  return page.evaluate((sel) => {
    const el = document.querySelector(sel);
    return el ? Math.ceil(el.getBoundingClientRect().bottom) + 28 : document.documentElement.scrollHeight;
  }, selector);
}

async function captureTo(page, relativePath, width, height, outName) {
  await page.setViewportSize({ width, height });
  await page.goto(pathToFileURL(path.join(root, relativePath)).href, { waitUntil: "load" });
  await page.addStyleTag({ content: ".premium-mobile-bar{display:none !important;}" });
  await waitForImages(page);
  const opts = { path: path.join(screenshots, outName), fullPage: false, animations: "disabled" };
  if (outName.endsWith(".jpg")) opts.type = "jpeg", opts.quality = 88;
  await page.screenshot(opts);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  // Handoff before/after: 2x device scale for crisp enlargement, saved as JPEG.
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  for (const { width, before, after } of pairs) {
    const hb = await sectionBottom(page, "pages/before-product.html", width, SECTION.before);
    const ha = await sectionBottom(page, "pages/after-product.html", width, SECTION.after);
    const h = Math.max(hb, ha);
    await captureTo(page, "pages/before-product.html", width, h, before);
    await captureTo(page, "pages/after-product.html", width, h, after);
    console.log(`${width}px @2x  before=${hb}  after=${ha}  -> matched ${width}x${h} (jpeg)`);
  }
  await page.close();

  // Demo proof shots (1x PNG), unchanged.
  const page1 = await browser.newPage();
  for (const [name, relativePath, width, height] of demos) {
    await page1.setViewportSize({ width, height });
    await page1.goto(pathToFileURL(path.join(root, relativePath)).href, { waitUntil: "load" });
    await waitForImages(page1);
    await page1.screenshot({ path: path.join(screenshots, name), fullPage: false, animations: "disabled" });
    console.log(`${name} ${width}x${height}`);
  }

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
