// Verify the self-contained handoff: drag, responsive swap, expand modal.
const { chromium } = require("playwright");
const { pathToFileURL } = require("url");
const path = require("path");

const url = pathToFileURL(path.resolve(__dirname, "..", "mosswell-slider-handoff.html")).href;
const out = path.resolve(__dirname, "..", "tmp");

// Drag the handle to a target percentage of the .ba frame width.
async function dragTo(page, pct) {
  const box = await page.locator("#ba").boundingBox();
  const handle = await page.locator("#baHandle").boundingBox();
  const startX = handle.x + handle.width / 2;
  const startY = handle.y + handle.height / 2;
  const endX = box.x + (box.width * pct) / 100;
  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(endX, startY, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(120);
}

async function clip(page) {
  return page.locator("#baAfter").evaluate((el) => el.style.clipPath);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  // ---- desktop ----
  const dp = await browser.newPage({ viewport: { width: 1280, height: 820 } });
  await dp.goto(url, { waitUntil: "load" });
  await dp.waitForTimeout(200);

  await dragTo(dp, 5);
  console.log("desktop clip @drag-left:", await clip(dp));
  await dp.screenshot({ path: path.join(out, "handoff-desktop-0.png") });

  await dragTo(dp, 50);
  await dp.screenshot({ path: path.join(out, "handoff-desktop-50.png") });

  await dragTo(dp, 95);
  console.log("desktop clip @drag-right:", await clip(dp));
  await dp.screenshot({ path: path.join(out, "handoff-desktop-100.png") });

  // expand modal
  await dp.click("#baExpand");
  await dp.waitForTimeout(200);
  const modalOpen = await dp.locator("#modal").evaluate((m) => m.classList.contains("open"));
  const cloneCount = await dp.locator("#modalBody .ba").count();
  console.log("modal open:", modalOpen, "| cloned slider present:", cloneCount === 1);
  await dp.screenshot({ path: path.join(out, "handoff-modal-open.png") });

  // esc closes
  await dp.keyboard.press("Escape");
  await dp.waitForTimeout(150);
  const modalClosed = await dp.locator("#modal").evaluate((m) => !m.classList.contains("open"));
  console.log("modal closed on Esc:", modalClosed);

  await dp.close();

  // ---- mobile (responsive swap) ----
  const mp = await browser.newPage({ viewport: { width: 390, height: 780 } });
  await mp.goto(url, { waitUntil: "load" });
  await mp.waitForTimeout(200);
  const usedSrc = await mp.locator(".ba__before img").evaluate((img) => img.currentSrc.slice(0, 40));
  const before = await mp.locator(".ba__before img").evaluate((img) => img.src.slice(0, 40));
  console.log("mobile currentSrc matches mobile img (not desktop source):", usedSrc === before);
  await mp.screenshot({ path: path.join(out, "handoff-mobile.png") });
  await mp.close();

  await browser.close();
  console.log("done");
})().catch((e) => { console.error(e); process.exit(1); });
