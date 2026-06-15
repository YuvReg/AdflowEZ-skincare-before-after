# Mosswell Skincare - Before/After Product Page Demo

Self-contained product-page before/after demo for AdflowEZ.

This project is intentionally separate from the clothing-store Shopify repo. It does not create or mutate a real Shopify store.

## Asset Contract

Drop final image-gen files into `assets/images/` using these exact names:

- `barrier-dew-serum-hero.png`
- `starter-serum-before.png`
- `ritual-shelf-family.png`
- `serum-texture-macro.png`
- `female-model-serum.png`
- `male-model-serum.png`

The current files are temporary placeholders. Final comparison screenshots are generated from the static pages.

## Pages

- `index.html` - before/after slider demo
- `pages/before-product.html` - credible starter product page
- `pages/after-product.html` - premium AdflowEZ rebuild product page
- `IMAGE-ASSET-HANDOFF.md` - exact image filenames and quality bar for the image-gen agent

## Handoff deliverable (single file)

- `mosswell-slider-handoff.html` - **the deliverable.** One self-contained file (images
  embedded as base64): a live drag-to-compare product-page slider whose **Expand** button opens
  the same comparison larger in a modal, plus image downloads and a copy-paste React component.
  Mirrors the clothing-store `adflowez-slider-handoff.html`.
- `components/BeforeAfter.jsx` - the React component the handoff hands off (drag-to-compare + expand).
- Rebuild after the screenshots or component change: `python scripts/build_handoff.py`
- Self-check the built file (drag, responsive swap, modal): `node scripts/verify-handoff.js`

## Visual QA Targets

- Desktop: 1280px wide
- Mobile: 390px wide
- Slider positions: 0%, 50%, 100%
- Expanded modal: opens, closes, and keeps the product-page comparison aligned

## Local Commands

- `python scripts\build_assets.py` regenerates temporary placeholder images.
- `powershell -ExecutionPolicy Bypass -File scripts\capture-screenshots.ps1` captures the four comparison screenshots.
