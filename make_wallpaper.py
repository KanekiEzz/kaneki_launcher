import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 3840, 2160
EX, EY = 2500, 1010            # eye center (off-center: leaves room for the lock-screen clock)
RED = (225, 29, 72)
rnd = random.Random(7)
nrnd = np.random.default_rng(7)

# ---------- background (computed at 1/4 res, upscaled = perfectly smooth) ----------
w4, h4 = W // 4, H // 4
yy, xx = np.mgrid[0:h4, 0:w4].astype(np.float32)
d = np.sqrt((xx - EX / 4) ** 2 + (yy - EY / 4) ** 2)
glow = np.exp(-(d / 260) ** 2)[..., None]
glow2 = np.exp(-(d / 520) ** 2)[..., None]
bg = np.array([10, 10, 13], np.float32) + glow * np.array([80, 6, 24]) + glow2 * np.array([26, 2, 8])
vd = np.sqrt(((xx - w4 / 2) / (w4 / 2)) ** 2 + ((yy - h4 / 2) / (h4 / 2)) ** 2)
bg *= (1 - 0.40 * np.clip(vd - 0.45, 0, 1)[..., None])
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert("RGBA")

# ---------- orbit rings (same idea as the launcher) ----------
ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring)
for R, dot, step, col in ((920, 4, 1.2, (60, 60, 72, 255)), (1200, 3, 1.0, (44, 44, 54, 255)), (1560, 3, 0.8, (34, 34, 42, 255))):
    n = int(360 / step)
    for i in range(n):
        t = math.radians(i * step)
        x, y = EX + R * math.cos(t), EY + R * math.sin(t)
        rd.ellipse((x - dot, y - dot, x + dot, y + dot), fill=col)
img.alpha_composite(ring)

# ---------- the eye (drawn on a local canvas, 2x supersampled) ----------
SS = 2
A, B = 780, 430                 # half width / half height of the eye opening
IR, PR = 470, 165               # iris radius / pupil radius
cw, ch = 2 * 1000, 2 * 640
LW, LH = cw * SS, ch * SS
cx, cy = LW / 2, LH / 2

# lens (almond) = intersection of two big discs
r = (A * A + B * B) / (2 * B)
def disc(cy_off):
    m = Image.new("L", (LW, LH), 0)
    ImageDraw.Draw(m).ellipse(((cx - r * SS), cy + cy_off * SS - r * SS, cx + r * SS, cy + cy_off * SS + r * SS), fill=255)
    return m
lens = ImageChops.multiply(disc(r - B), disc(-(r - B)))

# iris colour: radial gradient + radial fibres
Y, X = np.mgrid[0:LH, 0:LW].astype(np.float32)
dx, dy = (X - cx) / SS, (Y - cy) / SS
dist = np.sqrt(dx * dx + dy * dy)
t = np.clip((dist - PR) / (IR - PR), 0, 1)[..., None]
inner = np.array([150, 10, 34], np.float32)
mid = np.array([255, 52, 92], np.float32)
edge = np.array([95, 6, 22], np.float32)
col = np.where(t < 0.55, inner + (mid - inner) * (t / 0.55), mid + (edge - mid) * ((t - 0.55) / 0.45))

fib = Image.new("L", (LW, LH), 0)
fd = ImageDraw.Draw(fib)
for _ in range(420):
    a = rnd.uniform(0, 2 * math.pi)
    r0 = rnd.uniform(PR * 1.05, PR * 1.6) * SS
    r1 = rnd.uniform(IR * 0.7, IR * 0.98) * SS
    v = rnd.randint(70, 200)
    fd.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
            fill=v, width=rnd.choice((3, 4, 6, 8)))
fib = fib.filter(ImageFilter.GaussianBlur(3.0))
fibn = np.asarray(fib, np.float32)[..., None] / 255
col = col * (0.78 + 0.55 * fibn)

# eyelid shading (top/bottom darker) + iris only inside radius
lid = 1 - 0.62 * np.clip(np.abs(dy) / B, 0, 1) ** 2.6
col = col * lid[..., None]
sclera = np.array([6, 6, 8], np.float32)
in_iris = (dist <= IR)[..., None]
col = np.where(in_iris, col, sclera * (0.6 + 0.4 * lid[..., None]))
# pupil
col = np.where((dist <= PR)[..., None], np.array([3, 3, 4], np.float32), col)
eye = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")

# soft pupil rim + highlights
hl = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
hd = ImageDraw.Draw(hl)
def blob(x, y, rx, ry, a):
    hd.ellipse(((cx + x - rx) , (cy + y - ry), (cx + x + rx), (cy + y + ry)), fill=(255, 255, 255, a))
blob(-70 * SS, -78 * SS, 46 * SS, 34 * SS, 235)
blob(62 * SS, 52 * SS, 17 * SS, 15 * SS, 150)
hl = hl.filter(ImageFilter.GaussianBlur(4 * SS))
eye.alpha_composite(hl)
eye.putalpha(lens)

# glow + outline of the eyelid
edge_m = ImageChops.subtract(lens, lens.filter(ImageFilter.MinFilter(9)))
red = Image.new("RGBA", (LW, LH), RED + (255,))
outline = red.copy(); outline.putalpha(edge_m.point(lambda v: int(v * 0.95)))
halo = Image.new("RGBA", (LW, LH), RED + (255,))
halo.putalpha(edge_m.filter(ImageFilter.GaussianBlur(28 * SS)).point(lambda v: min(255, int(v * 2.4))))
wide = Image.new("RGBA", (LW, LH), (200, 20, 60, 255))
wide.putalpha(lens.filter(ImageFilter.GaussianBlur(70 * SS)).point(lambda v: int(v * 0.32)))

layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
layer.alpha_composite(wide)
layer.alpha_composite(halo)
layer.alpha_composite(eye)
layer.alpha_composite(outline)
layer = layer.resize((cw, ch), Image.LANCZOS)
img.alpha_composite(layer, (int(EX - cw / 2), int(EY - ch / 2)))

# ---------- clay speckles ----------
dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dots)
placed = 0
while placed < 46:
    x, y = rnd.uniform(80, W - 80), rnd.uniform(80, H - 80)
    if abs(x - EX) < 820 and abs(y - EY) < 470:      # keep the eye clean
        continue
    if x < 1500 and 1550 < y < 2000:                  # keep the text clean
        continue
    rr = rnd.choice((4, 5, 6, 8, 10, 13))
    c = RED + (rnd.randint(150, 235),) if rnd.random() < 0.6 else (70, 70, 82, 220)
    dd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c)
    placed += 1
img.alpha_composite(dots.filter(ImageFilter.GaussianBlur(0.8)))

# ---------- title ----------
draw = ImageDraw.Draw(img)
f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 210)
x = 250
for ch_ in "KANEKI":
    draw.text((x, 1700), ch_, font=f_big, fill=(244, 244, 245, 255))
    x += draw.textlength(ch_, font=f_big) + 34
draw.rectangle((254, 1985, 254 + 170, 1996), fill=RED)
try:
    f_jp = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 74, index=0)
    draw.text((254, 1600), "金木 研", font=f_jp, fill=(113, 113, 122, 255))
except Exception as e:
    print("kanji skipped:", e)

# ---------- film grain (kills gradient banding) ----------
arr = np.asarray(img.convert("RGB"), np.int16)
arr = arr + nrnd.integers(-2, 3, size=arr.shape[:2], dtype=np.int16)[..., None]
final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
final.save("/home/claude/wall/kaneki_lockscreen_4k.jpg", quality=95, subsampling=0)
final.resize((1920, 1080), Image.LANCZOS).save("/home/claude/wall/kaneki_lockscreen_1080p.jpg", quality=95, subsampling=0)
final.resize((1920, 1080), Image.LANCZOS).save("/tmp/wall_preview.png")
print("done")
