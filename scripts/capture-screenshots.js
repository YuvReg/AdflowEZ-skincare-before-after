const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");

const jobs = [
  ["before-desktop.png", "pages/before-product.html", 1280, 1000],
  ["after-desktop.png", "pages/after-product.html", 1280, 1000],
  ["before-mobile.png", "pages/before-product.html", 390, 1080],
  ["after-mobile.png", "pages/after-product.html", 390, 1080],
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

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  for (const [name, relativePath, width, height] of jobs) {
    await page.setViewportSize({ width, height });
    const url = pathToFileURL(path.join(root, relativePath)).href;
    await page.goto(url, { waitUntil: "load" });
    await waitForImages(page);
    await page.screenshot({
      path: path.join(screenshots, name),
      fullPage: false,
      animations: "disabled",
    });
    console.log(`${name} ${width}x${height}`);
  }

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
