from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source"
OUT = ROOT / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

SERIF = Path(r"C:\Windows\Fonts\georgia.ttf")
SERIF_BOLD = Path(r"C:\Windows\Fonts\georgiab.ttf")
SANS = Path(r"C:\Windows\Fonts\segoeui.ttf")
SANS_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")


def font(path, size):
    return ImageFont.truetype(str(path), size)


def fit_text(draw, text, font_path, max_width, start_size, min_size=12):
    size = start_size
    while size >= min_size:
        trial = font(font_path, size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=trial)
        if right - left <= max_width:
            return trial
        size -= 1
    return font(font_path, min_size)


def text_center(draw, xy, text, font_obj, fill, anchor="mm", spacing=0):
    draw.text(xy, text, font=font_obj, fill=fill, anchor=anchor, spacing=spacing)


def rounded_label(size, radius, fill, outline=None, width=1):
    label = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(label)
    d.rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )
    return label


def add_soft_shadow(canvas, label, x, y, blur=18, opacity=52):
    shadow = Image.new("RGBA", label.size, (22, 20, 18, opacity))
    alpha = label.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    shadow.putalpha(alpha)
    canvas.alpha_composite(shadow, (x, y + 6))
    canvas.alpha_composite(label, (x, y))


def add_mosswell_label(base):
    img = base.convert("RGBA")
    draw = ImageDraw.Draw(img)
    ink = (21, 20, 18, 255)
    sage = (104, 121, 109, 255)
    brass = (155, 106, 47, 255)
    porcelain = (250, 248, 243, 88)

    # Carton face: subtle ink directly over the blank carton, no sticker shadow.
    carton = rounded_label((258, 420), 10, porcelain, (234, 228, 219, 120), 1)
    cd = ImageDraw.Draw(carton)
    cd.text((129, 58), "MOSSWELL", font=font(SERIF_BOLD, 25), fill=ink, anchor="mm")
    cd.line((73, 86, 185, 86), fill=(155, 106, 47, 185), width=2)
    cd.text((129, 148), "Barrier Dew", font=font(SERIF, 29), fill=ink, anchor="mm")
    cd.text((129, 184), "Serum", font=font(SERIF, 29), fill=ink, anchor="mm")
    cd.text((129, 244), "peptide + tremella", font=font(SANS, 17), fill=sage, anchor="mm")
    cd.text((129, 286), "barrier support", font=font(SANS, 16), fill=ink, anchor="mm")
    cd.text((129, 356), "30 ml / 1 fl oz", font=font(SANS, 16), fill=brass, anchor="mm")
    img.alpha_composite(carton, (382, 348))

    # Bottle front label: small frosted panel placed on the visible bottle face.
    bottle = rounded_label((168, 252), 56, (250, 248, 243, 168), (255, 255, 255, 130), 1)
    bd = ImageDraw.Draw(bottle)
    bd.text((84, 48), "MW", font=font(SERIF_BOLD, 34), fill=ink, anchor="mm")
    bd.text((84, 88), "MOSS", font=font(SERIF_BOLD, 16), fill=ink, anchor="mm")
    bd.text((84, 126), "Barrier", font=font(SERIF, 22), fill=ink, anchor="mm")
    bd.text((84, 154), "Dew", font=font(SERIF, 22), fill=ink, anchor="mm")
    bd.text((84, 198), "30 ml", font=font(SANS, 14), fill=brass, anchor="mm")
    img.alpha_composite(bottle, (676, 686))

    return img.convert("RGB")


def add_starter_label(base):
    img = base.convert("RGBA")
    soft = Image.new("RGBA", img.size, (245, 245, 245, 55))
    img = Image.alpha_composite(img, soft)
    ink = (58, 58, 58, 255)
    gray = (104, 104, 104, 255)
    label_fill = (255, 255, 255, 220)

    carton = rounded_label((260, 392), 6, label_fill, (218, 218, 218, 255), 2)
    cd = ImageDraw.Draw(carton)
    cd.text((130, 64), "SKINCARE CO.", font=font(SANS_BOLD, 24), fill=ink, anchor="mm")
    cd.text((130, 138), "Hydrating", font=font(SANS, 30), fill=ink, anchor="mm")
    cd.text((130, 176), "Face Serum", font=font(SANS, 30), fill=ink, anchor="mm")
    cd.text((130, 246), "Daily moisture", font=font(SANS, 18), fill=gray, anchor="mm")
    cd.text((130, 318), "30 ml", font=font(SANS, 17), fill=gray, anchor="mm")
    img.alpha_composite(carton, (372, 360))

    bottle = rounded_label((196, 250), 12, (255, 255, 255, 194), (230, 230, 230, 180), 1)
    bd = ImageDraw.Draw(bottle)
    bd.text((98, 58), "HYDRATING", font=font(SANS_BOLD, 20), fill=ink, anchor="mm")
    bd.text((98, 104), "SERUM", font=font(SANS, 28), fill=ink, anchor="mm")
    bd.text((98, 176), "30 ml", font=font(SANS, 16), fill=gray, anchor="mm")
    img.alpha_composite(bottle, (650, 666))

    return img.convert("RGB")


def save_web_image(src_name, dest_name, size=1600):
    image = Image.open(SOURCE / src_name).convert("RGB")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    image.save(OUT / dest_name, quality=94, optimize=True)


def main():
    base = Image.open(SOURCE / "packshot-base.png").convert("RGB")
    after_packshot = add_mosswell_label(base)
    before_packshot = add_starter_label(base)
    after_packshot.save(OUT / "barrier-dew-serum-hero.png", quality=95, optimize=True)
    before_packshot.save(OUT / "starter-serum-before.png", quality=92, optimize=True)

    # Backward-compatible placeholder aliases while the page contract settles.
    after_packshot.save(OUT / "barrier-dew-serum.png", quality=95, optimize=True)
    before_packshot.save(OUT / "starter-serum.png", quality=92, optimize=True)

    for src, dest in [
        ("serum-texture.png", "serum-texture-macro.png"),
        ("bathroom-shelf.png", "ritual-shelf-family.png"),
        ("model-woman-serum.png", "female-model-serum.png"),
        ("model-man-serum.png", "male-model-serum.png"),
    ]:
        save_web_image(src, dest)

    # Backward-compatible aliases for the first placeholder pass.
    save_web_image("serum-texture.png", "serum-texture.png")
    save_web_image("bathroom-shelf.png", "ritual-shelf.png")
    save_web_image("model-woman-serum.png", "model-woman-serum.png")
    save_web_image("model-man-serum.png", "model-man-serum.png")


if __name__ == "__main__":
    main()
