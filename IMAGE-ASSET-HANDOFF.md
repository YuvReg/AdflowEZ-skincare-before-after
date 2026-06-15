# Mosswell Image Asset Handoff

Replace the temporary files in `assets/images/` with final image-gen assets using these exact names.

## Required Files

- `barrier-dew-serum-hero.png`
- `starter-serum-before.png`
- `ritual-shelf-family.png`
- `serum-texture-macro.png`
- `female-model-serum.png`
- `male-model-serum.png`

## Quality Bar

- Square images, ideally at least `1600x1600`.
- Sharp enough for desktop hero crops and mobile screenshots.
- No real brand logos or copied packaging.
- No prices, review stars, CTAs, badges, discounts, or long marketing copy inside the images.
- Product/package text should be minimal and readable: `MOSSWELL`, `Barrier Dew Serum`, `Peptide + Tremella`, `30 ml / 1 fl oz`.
- Human model images must have natural skin texture, realistic hands, and visible fictional product only.

## After Replacement

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\capture-screenshots.ps1
```

Then open `index.html` and check both Desktop and Mobile slider modes.
