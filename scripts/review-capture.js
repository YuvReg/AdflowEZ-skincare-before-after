/**
 * Review capture script.
 *
 * Usage: node scripts/review-capture.js <mobile|desktop>
 *
 * Drives the installed Playwright (chromium) over the local file:// pages and
 * writes a comprehensive screenshot set for the requested viewport into
 * screenshots/review-<mode>/. Also reports console errors, page errors, and
 * failed resource requests per page so a reviewer can see runtime problems.
 */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const { pathToFileURL } = require("url");

const mode = (process.argv[2] || "").toLowerCase();
if (mode !== "mobile" && mode !== "desktop") {
  console.error('Pass a mode: "mobile" or "desktop".');
  process.exit(2);
}

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "screenshots", `review-${mode}`);
fs.mkdirSync(outDir, { recursive: true });

const viewport =
  mode === "mobile" ? { width: 390, height: 844 } : { width: 1280, height: 900 };

function urlFor(rel) {
  return pathToFileURL(path.join(root, rel)).href;
}

async function waitForImages(page) {
  await page.evaluate(async () => {
    const images = Array.from(document.images);
    await Promise.all(
      images.map((img) => {
        if (img.complete && img.naturalWidth > 0) return Promise.resolve();
        return new Promise((resolve) => {
          img.addEventListener("load", resolve, { once: true });
          img.addEventListener("error", resolve, { once: true });
        });
      }),
    );
  });
}

// Returns the list of <img> elements that failed to load (broken images).
async function brokenImages(page) {
  return page.evaluate(() =>
    Array.from(document.images)
      .filter((img) => !(img.complete && img.naturalWidth > 0))
      .map((img) => img.getAttribute("src")),
  );
}

function attachDiagnostics(page, problems) {
  page.on("console", (msg) => {
    if (msg.type() === "error") problems.push(`console.error: ${msg.text()}`);
  });
  page.on("pageerror", (err) => problems.push(`pageerror: ${err.message}`));
  page.on("requestfailed", (req) =>
    problems.push(`requestfailed: ${req.url()} (${req.failure()?.errorText})`),
  );
}

async function shot(page, name, opts = {}) {
  const file = path.join(outDir, name);
  await page.screenshot({ path: file, animations: "disabled", ...opts });
  console.log(`  saved ${path.relative(root, file)}`);
}

async function setSlider(page, value) {
  await page.evaluate((v) => {
    const range = document.querySelector("[data-comparison] .comparison-range");
    if (range) {
      range.value = String(v);
      range.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }, value);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const problems = [];
  attachDiagnostics(page, problems);

  // ---- index.html : the before/after slider demo ("this file") ----
  console.log(`[${mode}] index.html (slider demo)`);
  await page.goto(urlFor("index.html"), { waitUntil: "load" });
  // Select the matching viewport mode so the right comparison images load.
  await page.click(`[data-mode="${mode}"]`);
  await waitForImages(page);
  await page.waitForTimeout(150);

  await setSlider(page, 0);
  await page.waitForTimeout(100);
  await shot(page, `${mode}-demo-slider-0.png`);

  await setSlider(page, 50);
  await page.waitForTimeout(100);
  await shot(page, `${mode}-demo-slider-50.png`);

  await setSlider(page, 100);
  await page.waitForTimeout(100);
  await shot(page, `${mode}-demo-slider-100.png`);

  await shot(page, `${mode}-demo-full.png`, { fullPage: true });

  // Expanded modal
  await setSlider(page, 50);
  await page.click("[data-expand]");
  await page.waitForTimeout(250);
  await shot(page, `${mode}-demo-modal-open.png`);
  const demoBroken = await brokenImages(page);

  // ---- before-product.html : original starter page ----
  console.log(`[${mode}] pages/before-product.html`);
  await page.goto(urlFor("pages/before-product.html"), { waitUntil: "load" });
  await waitForImages(page);
  await page.waitForTimeout(150);
  await shot(page, `${mode}-before-top.png`);
  await shot(page, `${mode}-before-full.png`, { fullPage: true });
  const beforeBroken = await brokenImages(page);

  // ---- after-product.html : AdflowEZ rebuild page ----
  console.log(`[${mode}] pages/after-product.html`);
  await page.goto(urlFor("pages/after-product.html"), { waitUntil: "load" });
  await waitForImages(page);
  await page.waitForTimeout(150);
  await shot(page, `${mode}-after-top.png`);
  await shot(page, `${mode}-after-full.png`, { fullPage: true });
  const afterBroken = await brokenImages(page);

  await browser.close();

  console.log("\n===== DIAGNOSTICS =====");
  console.log(`viewport: ${viewport.width}x${viewport.height} (${mode})`);
  const allBroken = [
    ...demoBroken.map((s) => `index.html -> ${s}`),
    ...beforeBroken.map((s) => `before-product.html -> ${s}`),
    ...afterBroken.map((s) => `after-product.html -> ${s}`),
  ];
  console.log(
    allBroken.length
      ? `BROKEN IMAGES (${allBroken.length}):\n  ${allBroken.join("\n  ")}`
      : "BROKEN IMAGES: none",
  );
  console.log(
    problems.length
      ? `RUNTIME PROBLEMS (${problems.length}):\n  ${problems.join("\n  ")}`
      : "RUNTIME PROBLEMS: none",
  );
  console.log(`Screenshots written to ${path.relative(root, outDir)}`);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
