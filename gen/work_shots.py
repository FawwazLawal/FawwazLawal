"""Frame screenshots of the in-development work in the profile's panel style.

Reads the raw captures from source/shots/ and writes framed composites to
assets/work/. The frame matches gen/stats_cards.py: near black ground, a cyan to
magenta gradient edge, bracket corners, and a faint scanline veil over the capture
so the shots sit in the same world as the rest of the page.

    python3 gen/work_shots.py

Needs Pillow. The raw captures are not committed.
"""

import os

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


def lerp(a, b, f):
    return tuple(int(x + (y - x) * f) for x, y in zip(a, b))


def edge(img):
    """Gradient border plus bracket corners, drawn over the panel."""
    w, h = img.size
    d = ImageDraw.Draw(img)
    steps = 160
    for i in range(steps):
        f = i / (steps - 1)
        c = lerp(CYAN, VIOLET, f * 2) if f < 0.5 else lerp(VIOLET, MAGENTA, (f - 0.5) * 2)
        x0, x1 = int(w * f), int(w * (i + 1) / steps) + 1
        d.line([(x0, 0), (x1, 0)], fill=c, width=2)
        d.line([(x0, h - 2), (x1, h - 2)], fill=c, width=2)
        y0, y1 = int(h * f), int(h * (i + 1) / steps) + 1
        d.line([(0, y0), (0, y1)], fill=lerp(CYAN, MAGENTA, f), width=2)
        d.line([(w - 2, y0), (w - 2, y1)], fill=lerp(CYAN, MAGENTA, f), width=2)
    arm, ins = 26, 11
    for x, y, dx, dy in ((ins, ins, 1, 1), (w - ins, ins, -1, 1),
                         (ins, h - ins, 1, -1), (w - ins, h - ins, -1, -1)):
        d.line([(x, y), (x + arm * dx, y)], fill=(0, 150, 170), width=2)
        d.line([(x, y), (x, y + arm * dy)], fill=(0, 150, 170), width=2)
    return img


def treat(im, width):
    """Scale a capture, veil it with scanlines, and give it a cyan edge and glow."""
    h = round(im.height * width / im.width)
    im = im.convert("RGB").resize((width, h), Image.LANCZOS)
    a = np.asarray(im, float)
    scan = np.where(np.arange(h) % 3 == 0, 0.86, 1.0)[:, None, None]
    a = a * scan * 0.97
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    glow = Image.new("RGB", (width + 24, h + 24), (0, 0, 0))
    glow.paste(im, (12, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    g = np.asarray(glow, float) * 0.55
    out = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
    out.paste(im, (12, 12))
    d = ImageDraw.Draw(out)
    d.rectangle([11, 11, 12 + width, 12 + h], outline=(0, 120, 140), width=1)
    return out


def panel(rows):
    """rows: list of lists of (path, width). Each row is centred."""
    tiles = [[treat(Image.open(os.path.join(SHOTS, p)), w) for p, w in row] for row in rows]
    heights = [max(t.height for t in row) for row in tiles]
    H = PAD * 2 + sum(heights) + GAP * (len(tiles) - 1)
    img = Image.new("RGB", (W, H), PANEL)
    a = np.asarray(img, float)
    yy, xx = np.mgrid[0:H, 0:W]
    a += (np.exp(-(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2))[..., None]
          * np.array(VIOLET) * 0.05)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    y = PAD
    for row, tile_row, rh in zip(rows, tiles, heights):
        total = sum(t.width for t in tile_row) + GAP * (len(tile_row) - 1)
        x = (W - total) // 2
        for t in tile_row:
            img.paste(t, (x, y + (rh - t.height) // 2))
            x += t.width + GAP
        y += rh + GAP
    return edge(img)


LAYOUTS = {
    "fisher.webp": [[("fisher-home.png", 352), ("fisher-playlist.png", 352), ("fisher-player.png", 352)]],
    "domain-dispatch-map.webp": [[("dd-map.webp", 1120)]],
    "domain-dispatch-plan.webp": [[("dd-planning.webp", 1120)]],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, rows in LAYOUTS.items():
        p = os.path.join(OUT, name)
        panel(rows).save(p, quality=86, method=6)
        print(f"{name} {Image.open(p).size} {os.path.getsize(p) // 1024} KB")


if __name__ == "__main__":
    main()
