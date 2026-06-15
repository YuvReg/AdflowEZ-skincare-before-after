// Verify slider geometry after the fix across viewports + modes.
const { chromium } = require("playwright");
const { pathToFileURL } = require("url");
const path = require("path");

const url = pathToFileURL(path.resolve(__dirname, "..", "index.html")).href;

async function probe(w, h, mode, label) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto(url, { waitUntil: "load" });
  await page.click(`[data-mode="${mode}"]`);
  await page.evaluate(() => {
    const r = document.querySelector("[data-comparison] .comparison-range");
    r.value = "100";
    r.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.waitForTimeout(120);
  const geo = await page.evaluate(() => {
    const rect = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: Math.round(r.x), w: Math.round(r.width), h: Math.round(r.height) };
    };
    return {
      innerH: window.innerHeight,
      shell: rect(".comparison-shell"),
      stage: rect("[data-comparison]"),
      divider: rect("[data-comparison] .comparison-divider"),
    };
  });
  const gap = geo.shell.w - geo.stage.w;
  const fitsH = geo.stage.h <= geo.innerH ? "fits viewport" : "TALLER than viewport";
  console.log(`\n=== ${label} (viewport ${w}x${h}, mode=${mode}) ===`);
  console.log(`  shell w=${geo.shell.w}  stage w=${geo.stage.w} (${Math.round(geo.stage.w / geo.shell.w * 100)}% of shell)  right-gap=${gap}px`);
  console.log(`  stage h=${geo.stage.h}  innerH=${geo.innerH}  -> ${fitsH}`);
  console.log(`  divider at x=${geo.divider.x} (stage right edge = x=${geo.stage.x + geo.stage.w})`);
  await browser.close();
}

(async () => {
  await probe(1340, 800, "desktop", "DESKTOP short window");
  await probe(1340, 800, "mobile", "MOBILE-mode on desktop");
  await probe(390, 740, "mobile", "REAL phone");
})().catch((e) => { console.error(e); process.exit(1); });
