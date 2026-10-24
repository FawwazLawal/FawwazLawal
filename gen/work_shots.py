"""Frame screenshots of the in-development work in the profile's panel style.

Reads the raw captures from source/shots/ and writes framed composites to
assets/work/. The frame matches gen/stats_cards.py: near black ground, a cyan to
magenta gradient edge, bracket corners, and a faint scanline veil over the capture
so the shots sit in the same world as the rest of the page.

    python3 gen/work_shots.py                         # every layout
    python3 gen/work_shots.py hellogitty-dark.webp    # one layout

Needs Pillow. The raw captures are not committed. The HelloGitty pair expects
source/shots/hellogitty-dark.png and hellogitty-light.png, the same dashboard captured
in each theme.
"""

import os
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.join(ROOT, "source", "shots")
OUT = os.path.join(ROOT, "assets", "work")

W = 1200
PAD = 26
GAP = 18
BG = (5, 5, 10)
PANEL = (11, 11, 22)
CYAN = (0, 240, 255)
VIOLET = (122, 44, 255)
MAGENTA = (255, 42, 109)

# Light-theme twin of the panel, for captures shown through a <picture> theme pair.
# Same gradient edge and brackets, darkened so they keep 3:1 against the paper ground.
LIGHT = dict(panel=(246, 247, 250), cyan=(0, 105, 111), violet=(90, 26, 176), magenta=(196, 20, 78),
             bracket=(0, 105, 111), scan=0.96, glow=(0, 0, 0), glow_a=0.10, outline=(160, 170, 185))
DARK = dict(panel=PANEL, cyan=CYAN, violet=VIOLET, magenta=MAGENTA,
            bracket=(0, 150, 170), scan=0.86, glow=None, glow_a=0.55, outline=(0, 120, 140))


def lerp(a, b, f):
    return tuple(int(x + (y - x) * f) for x, y in zip(a, b))


def edge(img, t=DARK):
    """Gradient border plus bracket corners, drawn over the panel."""
    w, h = img.size
    d = ImageDraw.Draw(img)
    steps = 160
    for i in range(steps):
        f = i / (steps - 1)
        c = lerp(t["cyan"], t["violet"], f * 2) if f < 0.5 else lerp(t["violet"], t["magenta"], (f - 0.5) * 2)
        x0, x1 = int(w * f), int(w * (i + 1) / steps) + 1
        d.line([(x0, 0), (x1, 0)], fill=c, width=2)
        d.line([(x0, h - 2), (x1, h - 2)], fill=c, width=2)
        y0, y1 = int(h * f), int(h * (i + 1) / steps) + 1
        d.line([(0, y0), (0, y1)], fill=lerp(t["cyan"], t["magenta"], f), width=2)
        d.line([(w - 2, y0), (w - 2, y1)], fill=lerp(t["cyan"], t["magenta"], f), width=2)
    arm, ins = 26, 11
    for x, y, dx, dy in ((ins, ins, 1, 1), (w - ins, ins, -1, 1),
                         (ins, h - ins, 1, -1), (w - ins, h - ins, -1, -1)):
        d.line([(x, y), (x + arm * dx, y)], fill=t["bracket"], width=2)
        d.line([(x, y), (x, y + arm * dy)], fill=t["bracket"], width=2)
    return img


# Location masking for the operations captures. The console is pointed at a real place,
# so the satellite basemap is blurred, and the camera's agency badge and the state code in
# the camera toast are obscured. "panel" rectangles are opaque interface (the open camera
# feed, the planning sidebar's version label) and are pasted back whole. Inside each "keep"
# rectangle only the overlay controls are pasted back, traced by chrome_mask(), so no
# imagery around or between them survives.
MASKS = {
    "dd-map.webp": {
        "blur": [(405, 0, 2000, 1217)],
        "panel": [(427, 39, 923, 1152)],
        "keep": [(898, 18, 1512, 82), (1858, 196, 1952, 792),
                 (1842, 812, 1958, 1188), (938, 1042, 1472, 1178)],
        "redact": [(424, 46, 702, 118)],
        "fill": [((1087, 1068, 1122, 1098), (1080, 1083))],
    },
    "dd-planning.webp": {
        "blur": [(405, 38, 2000, 1225)],
        "panel": [],
        "keep": [(418, 52, 1182, 122), (1188, 236, 1292, 842),
                 (1158, 828, 1312, 1218), (1032, 1088, 1368, 1162),
                 (405, 1166, 548, 1224), (1350, 38, 2000, 1225)],
        "redact": [],
        "fill": [((1087, 1107, 1120, 1138), (1080, 1122))],
    },
}
BLUR_R = 9


def _odd(n):
    n = max(3, int(round(n)))
    return n + (n % 2 == 0)


def chrome_mask(crop, s=1.8, dark=62, min_side=14):
    """The overlay controls in a crop, as a mask: dark neutral panels and accent-blue chips
    that are big enough to be controls, filled row by row so their text and icons stay
    whole. s is the capture's scale against a 1,120 px wide tile."""
    a = np.asarray(crop.convert("RGB"), float)
    mx, mn = a.max(2), a.min(2)
    panel = (mx < dark) & ((mx - mn) / np.maximum(mx, 1) < 0.45)
    chip = (a[..., 2] - a[..., 0] > 70) & (a[..., 2] > 110) & (a[..., 2] > a[..., 1] + 25)
    m = Image.fromarray(((panel | chip) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(_odd(5 * s))).filter(ImageFilter.MaxFilter(_odd(5 * s)))
    g = np.asarray(m) > 0
    h, w = g.shape
    seen = np.zeros_like(g)
    keep = np.zeros_like(g)
    for y, x in zip(*np.nonzero(g)):
        if seen[y, x]:
            continue
        q, comp = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            cy, cx = q.popleft()
            comp.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < h and 0 <= nx < w and g[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        ys, xs = zip(*comp)
        if max(xs) - min(xs) < min_side * s or max(ys) - min(ys) < min_side * s:
            continue
        rows = {}
        for cy, cx in comp:
            lo, hi = rows.get(cy, (cx, cx))
            rows[cy] = (min(lo, cx), max(hi, cx))
        for cy, (lo, hi) in rows.items():
            keep[cy, lo:hi + 1] = True
    return Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(_odd(2 * s)))


def mask(im, name):
    cfg = MASKS.get(name)
    if not cfg:
        return im
    im = im.convert("RGB")
    sharp = im.copy()
    for box in cfg["blur"]:
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(BLUR_R)), box[:2])
    for box in cfg["panel"]:
        im.paste(sharp.crop(box), box[:2])
    for box in cfg["keep"]:
        crop = sharp.crop(box)
        im.paste(Image.composite(crop, im.crop(box), chrome_mask(crop)), box[:2])
    for box in cfg["redact"]:
        patch = im.crop(box).filter(ImageFilter.GaussianBlur(22))
        im.paste(Image.blend(patch, Image.new("RGB", patch.size, (14, 14, 18)), 0.45), box[:2])
    for box, ref in cfg["fill"]:
        im.paste(im.getpixel(ref), box)
    return im


def treat(im, width, t=DARK):
    """Scale a capture, veil it with scanlines, and give it an edge and glow (a soft shadow on light)."""
    h = round(im.height * width / im.width)
    im = im.convert("RGB").resize((width, h), Image.LANCZOS)
    a = np.asarray(im, float)
    scan = np.where(np.arange(h) % 3 == 0, t["scan"], 1.0)[:, None, None]
    a = a * scan * 0.97
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if t["glow"] is None:
        glow = Image.new("RGB", (width + 24, h + 24), (0, 0, 0))
        glow.paste(im, (12, 12))
        g = np.asarray(glow.filter(ImageFilter.GaussianBlur(10)), float) * t["glow_a"]
        out = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
    else:
        out = Image.new("RGB", (width + 24, h + 24), t["panel"])
        shade = Image.new("L", out.size, 0)
        ImageDraw.Draw(shade).rectangle([12, 14, 12 + width, 14 + h], fill=int(255 * t["glow_a"]))
        out = Image.composite(Image.new("RGB", out.size, t["glow"]), out, shade.filter(ImageFilter.GaussianBlur(8)))
    out.paste(im, (12, 12))
    d = ImageDraw.Draw(out)
    d.rectangle([11, 11, 12 + width, 12 + h], outline=t["outline"], width=1)
    return out


def panel(rows, t=DARK):
    """rows: list of lists of (path, width). Each row is centred."""
    tiles = [[treat(mask(Image.open(os.path.join(SHOTS, p)), p), w, t) for p, w in row] for row in rows]
    heights = [max(tl.height for tl in row) for row in tiles]
    H = PAD * 2 + sum(heights) + GAP * (len(tiles) - 1)
    img = Image.new("RGB", (W, H), t["panel"])
    a = np.asarray(img, float)
    yy, xx = np.mgrid[0:H, 0:W]
    if t is DARK:
        a += (np.exp(-(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2))[..., None]
              * np.array(VIOLET) * 0.05)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    y = PAD
    for row, tile_row, rh in zip(rows, tiles, heights):
        total = sum(tl.width for tl in tile_row) + GAP * (len(tile_row) - 1)
        x = (W - total) // 2
        for tl in tile_row:
            img.paste(tl, (x, y + (rh - tl.height) // 2))
            x += tl.width + GAP
        y += rh + GAP
    return edge(img, t)


# name: (rows, theme). The HelloGitty pair is shown through <picture> so the capture
# follows the viewer's GitHub theme.
LAYOUTS = {
    "fisher.webp": ([[("fisher-home.png", 352), ("fisher-playlist.png", 352), ("fisher-player.png", 352)]], DARK),
    "domain-dispatch-map.webp": ([[("dd-map.webp", 1120)]], DARK),
    "domain-dispatch-plan.webp": ([[("dd-planning.webp", 1120)]], DARK),
    "hellogitty-dark.webp": ([[("hellogitty-dark.png", 1120)]], DARK),
    "hellogitty-light.webp": ([[("hellogitty-light.png", 1120)]], LIGHT),
}


def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    for name, (rows, t) in LAYOUTS.items():
        if only and name not in only:
            continue
        p = os.path.join(OUT, name)
        panel(rows, t).save(p, quality=86, method=6)
        print(f"{name} {Image.open(p).size} {os.path.getsize(p) // 1024} KB")


if __name__ == "__main__":
    import sys
    main(set(sys.argv[1:]) or None)
