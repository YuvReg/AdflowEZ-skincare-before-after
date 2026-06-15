#!/usr/bin/env python3
"""
Generate the Mosswell skincare image set by driving the local Codex CLI (gpt-5.5)
headlessly. gpt-5.5 creates photoreal product images natively AND typesets the
label text locally, so brand text is crisp and correctly spelled (see
C:\\Shopify for claude\\.claude\\memory\\codex-image-generation.md).

Working command pattern (verified here 2026-06-14):
    codex exec --sandbox workspace-write --skip-git-repo-check -o <report> "<prompt + exact save paths>"

Each shot-group is ONE codex session that saves multiple variant PNGs.
Phase 1 shots are independent (no reference). Phase 2 shots take the chosen hero
bottle as a -i reference so the bottle/brand stays consistent.

Run:
    python scripts/gen_mosswell.py phase=1
    python scripts/gen_mosswell.py phase=2 hero=assets/images/_gen/hero-2.png
    python scripts/gen_mosswell.py phase=1 only=hero,texture     # subset
    python scripts/gen_mosswell.py phase=1 --dry                  # show plan only
"""
import os, sys, subprocess

ROOT = r"c:\AdflowEZ-skincare-before-after"
os.chdir(ROOT)
OUT = os.path.join("assets", "images", "_gen")
LOGDIR = os.path.join("scripts", "_codexlog")
os.makedirs(OUT, exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)
CODEX_FALLBACK = r"C:\Users\yuval\AppData\Roaming\npm\codex.cmd"
PER_GROUP_TIMEOUT = 600  # seconds

STYLE = ("Photorealistic premium minimalist skincare catalog photography, soft natural light, "
         "calm muted palette (blush pink, sage green, warm stone, cream), gentle soft shadows, "
         "clean modern composition, square 1:1. No extra text anywhere, no other brand logos, "
         "no watermarks, no price, no badges.")

# The canonical label text. gpt-5.5 typesets this crisply.
LABEL = ('The label text must be REAL, crisp, sharp and correctly spelled, neatly typeset: '
         'brand "MOSSWELL" in small caps at top, then "Barrier Dew Serum", then smaller '
         '"Peptide + Tremella", then "30 ml / 1 fl oz".')

BOTTLE = ("a Mosswell Barrier Dew Serum: a frosted-glass dropper bottle with pale blush-pink serum "
          "and a matte white dropper cap")

# name -> (prompt_core, [variant_filenames], phase, needs_ref)
SHOTS = {
    "hero": (
        f"{BOTTLE}, shown next to its minimalist white carton box, arranged on a smooth stone slab "
        f"with a soft botanical leaf shadow and a muted sage-green backdrop. Both the bottle and the "
        f"carton carry the Mosswell label. {LABEL} {STYLE}",
        ["hero-1.png", "hero-2.png", "hero-3.png"], 1, False),

    "texture": (
        "an extreme close-up macro of skincare serum texture: a glossy translucent pale-pink gel "
        "swatch with tiny air bubbles and a few dewy droplets, on a smooth off-white surface, soft "
        f"diffused light. No bottle and absolutely NO text or label in the image. {STYLE}",
        ["texture-1.png", "texture-2.png"], 1, False),

    "female": (
        "a serene woman with natural healthy glowing skin in soft morning light, applying a few drops "
        "of Mosswell serum to her cheek with a glass dropper. Realistic hands and natural skin texture, "
        f"calm neutral bathroom setting, the product slightly out of focus. {STYLE}",
        ["female-1.png", "female-2.png"], 1, False),

    "male": (
        "a calm man with natural healthy skin in a softly lit modern minimalist bathroom, holding the "
        "Mosswell frosted-glass serum bottle. Realistic hands and skin texture, understated grooming "
        f"scene. {STYLE}",
        ["male-1.png", "male-2.png"], 1, False),

    # ---- phase 2 (use chosen hero as -i reference for bottle/brand consistency) ----
    "starter": (
        "the SAME Mosswell Barrier Dew Serum bottle from the reference image, photographed plainly and "
        "simply on a plain white seamless studio background as a basic flat e-commerce packshot, even "
        f"lighting, minimal styling (this is the simpler 'before' presentation). {LABEL} {STYLE}",
        ["starter-1.png", "starter-2.png"], 2, True),

    "shelf": (
        "a family of FOUR matching Mosswell skincare products arranged on a clean light bathroom shelf "
        "with a small green plant and soft daylight: a tall pump cleanser bottle, the frosted dropper "
        "serum from the reference, a small round cream jar, and a slim eye-cream bottle. Keep the bottle "
        "style and brand consistent with the reference. Each product has its own clean Mosswell label "
        f"with crisp, correctly-spelled text. {STYLE}",
        ["shelf-1.png", "shelf-2.png", "shelf-3.png"], 2, True),

    "bottle": (
        "the SAME Mosswell serum bottle from the reference image, alone and centered on a soft neutral "
        f"cream background, a clean premium catalog packshot. {LABEL} {STYLE}",
        ["bottle-1.png", "bottle-2.png"], 2, True),

    "lifestyle": (
        "the Mosswell serum bottle from the reference image on a marble bathroom counter beside a folded "
        "sage-green towel and a small ceramic dish with a flower, soft daylight, an aspirational but calm "
        f"lifestyle scene. {STYLE}",
        ["lifestyle-1.png", "lifestyle-2.png"], 2, True),
}


def run_codex(prompt, report, ref=None):
    cmd = ["codex", "exec", "--sandbox", "workspace-write", "--skip-git-repo-check"]
    if ref:
        cmd += ["-i", ref]
    cmd += ["-o", report, prompt]
    kw = dict(timeout=PER_GROUP_TIMEOUT, capture_output=True, text=True,
              encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    try:
        return subprocess.run(cmd, **kw)
    except FileNotFoundError:
        cmd[0] = CODEX_FALLBACK
        return subprocess.run(cmd, **kw)


def is_png(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"\x89PNG" and os.path.getsize(path) > 40000
    except OSError:
        return False


def main():
    dry = "--dry" in sys.argv
    phase = None
    only = None
    hero = None
    for a in sys.argv[1:]:
        if a.startswith("phase="):
            phase = int(a.split("=", 1)[1])
        elif a.startswith("only="):
            only = set(a.split("=", 1)[1].split(","))
        elif a.startswith("hero="):
            hero = a.split("=", 1)[1]

    todo = []
    for name, (core, files, ph, needs_ref) in SHOTS.items():
        if phase is not None and ph != phase:
            continue
        if only is not None and name not in only:
            continue
        todo.append((name, core, files, needs_ref))

    print(f"== Mosswell image gen: {len(todo)} shot-group(s)  phase={phase} ==", flush=True)
    if any(nr for _, _, _, nr in todo) and not hero and not dry:
        print("  NOTE: phase-2 shots need hero=<path>; none given.", flush=True)

    results = []
    for name, core, files, needs_ref in todo:
        out_paths = [os.path.join(OUT, fn) for fn in files]
        prompt = (f"Generate {len(out_paths)} DISTINCT photorealistic studio image variant(s). "
                  f"Subject: {core} ")
        for p in out_paths:
            prompt += f"Save one variant as a real PNG to exactly this path: {p}. "
        prompt += ("Make the variants meaningfully different (angle / crop / arrangement). "
                   "Each must be saved to its exact path. Do not ask questions; just generate and save.")

        ref = hero if needs_ref else None
        if dry:
            print(f"[DRY] {name}: {len(files)} variant(s) ref={ref} -> {', '.join(out_paths)}", flush=True)
            continue

        print(f"[GEN] {name}: {len(files)} variant(s) ref={ref} ...", flush=True)
        report = os.path.join(LOGDIR, f"mosswell-{name}.md")
        try:
            r = run_codex(prompt, report, ref)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            print(f"   TIMEOUT after {PER_GROUP_TIMEOUT}s", flush=True)
            rc = -9
        made = [os.path.basename(p) for p in out_paths if is_png(p)]
        missing = [os.path.basename(p) for p in out_paths if not is_png(p)]
        status = "OK" if not missing else ("PARTIAL" if made else "FAIL")
        print(f"   rc={rc} {status}  made={made}  missing={missing}", flush=True)
        results.append((name, status, made, missing))

    if not dry:
        print("\n== SUMMARY ==", flush=True)
        for name, status, made, missing in results:
            print(f"  {status:8} {name:10} made={len(made)} missing={len(missing)}", flush=True)


if __name__ == "__main__":
    main()
