const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

const pages = ["index.html", "pages/before-product.html", "pages/after-product.html"];

(async () => {
  const browser = await chromium.launch({ headless: true });

  for (const pagePath of pages) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const consoleErrors = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });

    await page.goto(pathToFileURL(path.resolve(pagePath)).href, { waitUntil: "load" });
    const images = await page.$$eval("img", (imgs) =>
      imgs.map((img) => ({
        src: img.getAttribute("src"),
        ok: img.complete && img.naturalWidth > 0,
        width: img.naturalWidth,
        height: img.naturalHeight,
      })),
    );

    const brokenImages = images.filter((img) => !img.ok);
    console.log(
      `${pagePath}: ${images.length} images, ${brokenImages.length} broken, ${consoleErrors.length} console errors`,
    );

    if (brokenImages.length > 0) {
      console.log(JSON.stringify(brokenImages, null, 2));
    }

    if (consoleErrors.length > 0) {
      console.log(JSON.stringify(consoleErrors, null, 2));
    }

    await page.close();
  }

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
