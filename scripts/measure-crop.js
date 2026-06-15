const {chromium, devices} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({...devices['iPhone 13']});
  const p = await ctx.newPage();
  await p.goto('file:///c:/AdflowEZ-skincare-before-after/mosswell-slider-handoff.html');
  await p.waitForTimeout(800);
  const data = await p.evaluate(() => {
    const ba = document.querySelector('.ba');
    const img = ba ? ba.querySelector('img') : null;
    const r = ba ? ba.getBoundingClientRect() : null;
    return {
      frameW: r && Math.round(r.width),
      frameH: r && Math.round(r.height),
      imgNaturalW: img && img.naturalWidth,
      imgNaturalH: img && img.naturalHeight,
    };
  });
  // how many vertical px of the source are shown:
  // cover scales source so width fills frame; scale = frameW/naturalW
  const scale = data.frameW / data.imgNaturalW;
  const srcVisibleH = Math.round(data.frameH / scale);
  const pctVisible = (srcVisibleH / data.imgNaturalH * 100).toFixed(1);
  console.log(JSON.stringify({...data, scale:scale.toFixed(3), srcVisibleH, pctVisible}, null, 2));
  await b.close();
})();
