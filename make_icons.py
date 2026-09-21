#!/usr/bin/env python3
"""
Generates the 3D "clay blob" icons used by Kaneki Launcher.

    pip install pillow numpy
    python3 make_icons.py

Output: ./icons/*.png  and  ./kaneki.png (window / dock icon)

To add a new app icon: write a glyph function (see g_terminal), add it to ICONS,
run this script, then reference the file in APPS inside kaneki_launcher.py.
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ICON_DIR = ROOT / "icons"
SS = 4  # supersampling factor (smooth edges)

# ---------- Colors (change these to re-theme everything, e.g. green) ----------
RED = (225, 29, 72)
DARK = (46, 46, 54)
WHITE = (245, 245, 246)

STYLES = {
    "dark": {"base": DARK, "fg": RED},   # charcoal blob, red glyph
    "red": {"base": RED, "fg": WHITE},   # red blob, white glyph
}


# ---------- Glyphs (drawn as white-on-black masks, coords are 0..1) ----------
def stroke(d, pts, w, s):
    """Thick polyline with round caps."""
    p = [(x * s, y * s) for x, y in pts]
    d.line(p, fill=255, width=int(w * s), joint="curve")
    r = w * s / 2
    for x, y in (p[0], p[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)


def g_terminal(d, s):
    stroke(d, [(0.30, 0.36), (0.47, 0.51), (0.30, 0.66)], 0.075, s)
    stroke(d, [(0.52, 0.67), (0.70, 0.67)], 0.075, s)


def g_code(d, s):
    stroke(d, [(0.38, 0.34), (0.22, 0.50), (0.38, 0.66)], 0.07, s)
    stroke(d, [(0.62, 0.34), (0.78, 0.50), (0.62, 0.66)], 0.07, s)
    stroke(d, [(0.55, 0.30), (0.45, 0.70)], 0.06, s)


def g_globe(d, s):
    cx = cy = 0.5 * s
    R = 0.27 * s
    w = int(0.058 * s)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=w)
    r2 = R * 0.46
    d.ellipse((cx - r2, cy - R, cx + r2, cy + R), outline=255, width=int(w * 0.8))
    d.line((cx - R, cy, cx + R, cy), fill=255, width=int(w * 0.8))
    for dy in (-0.5, 0.5):
        half = math.sqrt(1 - dy * dy) * R
        d.line((cx - half, cy + dy * R, cx + half, cy + dy * R), fill=255, width=int(w * 0.7))


def g_gear(d, s):
    cx = cy = 0.5 * s
    r_body, r_out, r_hole, hw = 0.22 * s, 0.30 * s, 0.09 * s, 0.05 * s
    d.ellipse((cx - r_body, cy - r_body, cx + r_body, cy + r_body), fill=255)
    for i in range(8):
        a = 2 * math.pi * i / 8
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        pts = [
            (cx + ux * r_body * 0.9 + vx * hw, cy + uy * r_body * 0.9 + vy * hw),
            (cx + ux * r_out + vx * hw * 0.75, cy + uy * r_out + vy * hw * 0.75),
            (cx + ux * r_out - vx * hw * 0.75, cy + uy * r_out - vy * hw * 0.75),
            (cx + ux * r_body * 0.9 - vx * hw, cy + uy * r_body * 0.9 - vy * hw),
        ]
        d.polygon(pts, fill=255)
    d.ellipse((cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole), fill=0)


def _font(px):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if Path(p).exists():
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def g_K(d, s):
    font = _font(int(s * 0.54))
    bb = d.textbbox((0, 0), "K", font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((s - w) / 2 - bb[0], (s - h) / 2 - bb[1]), "K", font=font, fill=255)


# ---------- Rendering ----------
def blob_mask(size, seed):
    """Slightly irregular circle, like a piece of clay."""
    rnd = random.Random(seed)
    a2, a3 = rnd.uniform(0.02, 0.04), rnd.uniform(0.02, 0.035)
    p2, p3 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    c, R = size / 2, size * 0.47
    pts = []
    for i in range(360):
        t = 2 * math.pi * i / 360
        r = R * (1 + a2 * math.sin(2 * t + p2) + a3 * math.sin(3 * t + p3))
        pts.append((c + r * math.cos(t), c + r * math.sin(t)))
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def shade(size, base, mask):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.sqrt((xx - size * 0.36) ** 2 + (yy - size * 0.28) ** 2) / (size * 0.9)
    light = np.clip(1.0 - d, 0, 1)[..., None]
    rgb = np.array(base, dtype=np.float32) * (0.68 + 0.5 * light) + 255 * 0.16 * light ** 3
    inner = np.asarray(mask.filter(ImageFilter.GaussianBlur(size * 0.05)), dtype=np.float32) / 255
    rgb *= 0.55 + 0.45 * inner[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


def add_dots(glyph, size, seed):
    """Little clay speckles around the glyph."""
    rnd = random.Random(seed + 99)
    d = ImageDraw.Draw(glyph)
    ref = glyph.copy()
    placed = tries = 0
    while placed < 9 and tries < 500:
        tries += 1
        ang = rnd.uniform(0, 2 * math.pi)
        rad = rnd.uniform(0.30, 0.40) * size
        x, y = size / 2 + rad * math.cos(ang), size / 2 + rad * math.sin(ang)
        r = rnd.uniform(0.006, 0.014) * size
        box = (int(x - r * 3), int(y - r * 3), int(x + r * 3), int(y + r * 3))
        if ref.crop(box).getextrema()[1] > 0:
            continue
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)
        placed += 1


def render(glyph_fn, style, out_px, seed):
    size = out_px * SS
    st = STYLES[style]
    white = Image.new("RGB", (size, size), (255, 255, 255))
    black = Image.new("RGB", (size, size), (0, 0, 0))

    mask = blob_mask(size, seed)
    body = shade(size, st["base"], mask)

    # top-left rim light
    shifted = ImageChops.offset(mask, int(size * 0.018), int(size * 0.022))
    rim = ImageChops.subtract(mask, shifted).filter(ImageFilter.GaussianBlur(size * 0.006))
    body.paste(white, (0, 0), rim.point(lambda v: int(v * 0.55)))

    # glyph + speckles
    glyph = Image.new("L", (size, size), 0)
    glyph_fn(ImageDraw.Draw(glyph), size)
    add_dots(glyph, size, seed)

    # soft drop shadow under glyph
    shadow = ImageChops.offset(glyph, int(size * 0.010), int(size * 0.022))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.014)).point(lambda v: int(v * 0.6))
    body.paste(black, (0, 0), shadow)

    # glyph fill with vertical gradient
    fg = np.array(st["fg"], dtype=np.float32)
    grad = np.linspace(1.10, 0.82, size, dtype=np.float32)[:, None, None]
    fill = np.clip(fg[None, None, :] * grad, 0, 255) * np.ones((1, size, 1), dtype=np.float32)
    body.paste(Image.fromarray(fill.astype(np.uint8)), (0, 0), glyph)

    # glyph top-left edge highlight
    gshift = ImageChops.offset(glyph, int(size * 0.007), int(size * 0.010))
    edge = ImageChops.subtract(glyph, gshift).filter(ImageFilter.GaussianBlur(size * 0.003))
    body.paste(white, (0, 0), edge.point(lambda v: int(v * 0.7)))

    out = body.convert("RGBA")
    out.putalpha(mask)
    return out.resize((out_px, out_px), Image.LANCZOS)


# name -> (glyph, style, size in px, seed)
ICONS = {
    "terminal": (g_terminal, "dark", 128, 1),
    "firefox": (g_globe, "red", 128, 2),
    "settings": (g_gear, "dark", 128, 3),
    "vscode": (g_code, "red", 128, 4),
    "lock": (g_gear, "dark", 128, 5),
}


def main():
    ICON_DIR.mkdir(exist_ok=True)
    for name, (fn, style, px, seed) in ICONS.items():
        render(fn, style, px, seed).save(ICON_DIR / f"{name}.png")
        print("icons/", name)
    render(g_K, "red", 200, 7).save(ICON_DIR / "center.png")
    render(g_K, "red", 256, 7).save(ROOT / "kaneki.png")  # window / dock icon
    print("center.png, kaneki.png")


if __name__ == "__main__":
    main()
