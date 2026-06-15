// Mobile-device review of the self-contained handoff: real phone profile,
// checks for horizontal overflow / fit, and exercises the slider + expand modal.
const { chromium, devices } = require("playwright");
const { pathToFileURL } = require("url");
const path = require("path");

const url = pathToFileURL(path.resolve(__dirname, "..", "mosswell-slider-handoff.html")).href;
const out = path.resolve(__dirname, "..", "tmp");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ ...devices["iPhone 13"] });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(300);

  const vw = page.viewportSize().width;

  // 1) Horizontal overflow check (page should never scroll sideways on mobile)
  const overflow = await page.evaluate(() => ({
    docScrollW: document.documentElement.scrollWidth,
    bodyScrollW: document.body.scrollWidth,
    innerW: window.innerWidth,
  }));
  const horizScroll = overflow.docScrollW > overflow.innerW + 1;

  // 2) Does any element stick out past the viewport edge?
  const offenders = await page.evaluate((w) => {
    const bad = [];
    document.querySelectorAll("*").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && (r.right > w + 1 || r.left < -1)) {
        bad.push({ tag: el.tagName, cls: el.className?.toString().slice(0, 40), right: Math.round(r.right), left: Math.round(r.left) });
      }
    });
    return bad.slice(0, 12);
  }, vw);

  // 3) Which image is the slider actually loading on mobile?
  const usedMobileImg = await page.locator(".ba__before img").evaluate(
    (img) => img.currentSrc === img.src
  );

  // 4) Slider frame metrics (does the 4:5 card fit the column?)
  const ba = await page.locator("#ba").boundingBox();

  await page.screenshot({ path: path.join(out, "mobile-review-full.png"), fullPage: true });
  await page.locator(".card").first().screenshot({ path: path.join(out, "mobile-review-card.png") });

  // 5) Expand modal on mobile
  await page.locator("#baExpand").scrollIntoViewIfNeeded();
  await page.locator("#baExpand").click();
  await page.waitForTimeout(300);
  const modalFits = await page.evaluate(() => {
    const mb = document.getElementById("modalBody");
    if (!mb) return null;
    const r = mb.getBoundingClientRect();
    return { right: Math.round(r.right), left: Math.round(r.left), innerW: window.innerWidth, fits: r.right <= window.innerWidth + 1 && r.left >= -1 };
  });
  await page.screenshot({ path: path.join(out, "mobile-review-modal.png") });

  console.log(JSON.stringify({
    viewport: vw,
    horizontalScroll: horizScroll,
    overflow,
    offenders,
    usedMobileImg,
    sliderCard: ba && { x: Math.round(ba.x), w: Math.round(ba.width), rightEdge: Math.round(ba.x + ba.width) },
    modalFits,
  }, null, 2));

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
