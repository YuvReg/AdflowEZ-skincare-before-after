const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");

// before/after captured to the bottom of the PRODUCT section (the clean hero +
// product + buy area shown in the client's reference), matched per orientation
// so the two line up and the slider shows the whole product view (no cropping).
const pairs = [
  { width: 1280, before: "before-desktop.png", after: "after-desktop.png" },
  { width: 390, before: "before-mobile.png", after: "after-mobile.png" },
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
  await page.screenshot({ path: path.join(screenshots, outName), fullPage: false, animations: "disabled" });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  for (const { width, before, after } of pairs) {
    const hb = await sectionBottom(page, "pages/before-product.html", width, SECTION.before);
    const ha = await sectionBottom(page, "pages/after-product.html", width, SECTION.after);
    const h = Math.max(hb, ha);
    await captureTo(page, "pages/before-product.html", width, h, before);
    await captureTo(page, "pages/after-product.html", width, h, after);
    console.log(`${width}px  before=${hb}  after=${ha}  -> matched ${width}x${h}`);
  }

  for (const [name, relativePath, width, height] of demos) {
    await page.setViewportSize({ width, height });
    await page.goto(pathToFileURL(path.join(root, relativePath)).href, { waitUntil: "load" });
    await waitForImages(page);
    await page.screenshot({ path: path.join(screenshots, name), fullPage: false, animations: "disabled" });
    console.log(`${name} ${width}x${height}`);
  }

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
