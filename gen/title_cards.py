"""Re-title the animated glyph bands so their type survives a phone screen.

gen/ascii_film.py renders the bands from footage that is not committed. Its renders are
kept in assets/originals/ and this script works on them: it replaces each band's title
zone with a matching glyph field that flickers on the band's own loop (so the loop stays
seamless), redraws the title large enough for a 358 px phone column, optionally cuts a
shorter seamless loop with the same glyph-cell dissolve ascii_film.py uses, and writes a
still for prefers-reduced-motion.

Type floor: a 1200 px band is shown at 358 px on a phone (x0.298), so 12 px there needs
40.2 px here. Titles are 52 px and labels 42 px.

    python3 gen/title_cards.py              # every band
    python3 gen/title_cards.py hero 03      # some bands

Needs numpy and Pillow, and DejaVu Sans Mono (same lineage as Menlo, which ascii_film.py
used); Menlo is the fallback.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORIG = os.path.join(ROOT, "assets", "originals")
OUT = os.path.join(ROOT, "assets", "bands")

FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
         os.path.expanduser("~/Library/Fonts/DejaVuSansMono.ttf"),
         "/Library/Fonts/DejaVuSansMono.ttf",
         "/System/Library/Fonts/Menlo.ttc"]
FONT = next(p for p in FONTS if os.path.exists(p))
CW, CH = 7, 12                                       # glyph cell, as in ascii_film.py
CYAN, BONE = (0, 220, 240), (236, 234, 245)
CHROMA = ((-2, (150, 20, 70)), (2, (0, 140, 160)))   # the hero's chromatic split

# A line is (text, px, colour, chromatic split, x, y). "cursor" adds a blinking block
# after the last line; "cursor_off" lists frame ranges [a, b) where the footage has its own
# words and the cursor stays off. "cut" keeps frames [a, b) and closes them into a seamless
# loop; "start" rotates the loop so it opens on that frame (counted after the cut).
# "box" is the title zone (x0, y0, x1, y1); it must stay clear of the figure in every frame.
# "pips" is (chapter, chapters): a progress meter after the chapter number.
HERO_LINES = [("FAWWAZ LAWAL", 52, BONE, True, 44, 50), (">", 42, CYAN, False, 44, 118)]
SPECS = {
    "hero": dict(src="hero-band.webp", out="hero", box=(0, 34, 430, 178), cut=(160, 260), start=19,
                 still=185, cursor=True, lines=HERO_LINES),
    "film": dict(src="hero-band.webp", out="film", box=(0, 34, 430, 178), cut=None, still=185,
                 cursor=True, lines=HERO_LINES),
}


def chapter(num, title, src, box_x1, still, old, mode="plate", cursor=True, cursor_off=(), slug=None):
    """old: (num, title, subtitle) exactly as ascii_film.py drew them, for mode "strokes"."""
    return dict(src=src, out=f"chapter-{num}-{slug or title.lower().replace(' ', '-')}", box=(0, 46, box_x1, 156),
                cut=None, still=still, cursor=cursor, cursor_off=cursor_off, mode=mode, old=old,
                pips=(int(num), CHAPTERS),
                lines=[(f"{num} //", 42, CYAN, False, 44, 42), (title, 52, BONE, True, 44, 92)])


CHAPTERS = 5


# Footage -> chapter. Chapter 00 (the public work) has no band: the hero is its frame, so the
# first screen carries one moving element. The source bands keep their ascii_film.py names;
# box_x1 stops each title zone short of the figure or light in that footage (checked frame
# by frame). Chapter 02's footage has ACCESS DENIED passing under the title, so only the old
# letter strokes are repainted there, the cursor stays off while the sign is lit (frames
# 11-29), and its still is a lit frame.
SPECS.update({
    "01": chapter("01", "HELLOGITTY", "chapter-01-selected-work.webp", 470, 8, ("01", "SELECTED WORK", "what I have built")),
    "02": chapter("02", "RESTRICTED", "chapter-02-restricted.webp", 380, 20, ("02", "RESTRICTED", "private repositories"),
                  mode="strokes", cursor_off=[(11, 30)]),
    "03": chapter("03", "SYSTEMS", "chapter-03-systems.webp", 330, 15, ("03", "SYSTEMS", "how I engineer")),
    "04": chapter("04", "TOOLKIT", "chapter-04-toolkit.webp", 330, 27, ("04", "TOOLKIT", "what I build with")),
    "05": chapter("05", "EXIT", "chapter-05-exit.webp", 300, 27, ("05", "EXIT", "end of transmission")),
})


def old_text_mask(w, h, old, grow=9):
    """Where ascii_film.title_band drew its 15/38/13 px text, grown to cover Menlo vs DejaVu outlines."""
    num, title, sub = old
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    x, y = 44, 58
    d.text((x, y), f"{num} //", font=ImageFont.truetype(FONT, 15), fill=255)
    for dx in (-2, 2, 0):
        d.text((x + dx, y + 22), title, font=ImageFont.truetype(FONT, 38), fill=255)
    d.text((x, y + 72), "> " + sub, font=ImageFont.truetype(FONT, 13), fill=255)
    m = m.filter(ImageFilter.MaxFilter(grow)).filter(ImageFilter.GaussianBlur(2))
    return (np.asarray(m, float) / 255)[..., None]


def _mask(ch):
    m = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(m).text((CW / 2, CH / 2), ch, font=ImageFont.truetype(FONT, 11), fill=255, anchor="mm")
    return np.asarray(m, float) / 255


GLYPHS = np.stack([_mask("0"), _mask("1")])


def glyph_field(w, h, n, t, seed):
    """Sparse dim 0/1 field whose flicker period equals the loop length."""
    rng = np.random.default_rng(seed)
    rows, cols = h // CH + 1, w // CW + 1
    on = rng.uniform(size=(rows, cols)) < 0.13
    which = rng.integers(0, 2, (rows, cols))
    phase = rng.uniform(0, 2 * np.pi, (rows, cols))
    base = rng.uniform(0.18, 0.5, (rows, cols))
    ink = np.array([[40, 200, 230], [140, 80, 220]], float)[np.where(rng.uniform(size=(rows, cols)) < 0.72, 0, 1)]
    v = (base * (0.55 + 0.45 * np.sin(2 * np.pi * t / n + phase)) * on)[..., None] * ink
    blocks = GLYPHS[which][..., None] * v[:, :, None, None, :]
    return blocks.transpose(0, 2, 1, 3, 4).reshape(rows * CH, cols * CW, 3)[:h, :w]


def zone_mask(w, h, box, fade_x=70, fade_y=16):
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[0:h, 0:w]
    mx = np.clip((x1 - xx) / fade_x, 0, 1) * (xx >= x0)
    my = np.clip((yy - (y0 - fade_y)) / fade_y, 0, 1) * np.clip(((y1 + fade_y) - yy) / fade_y, 0, 1)
    return (mx * my)[..., None]


def read_frames(path):
    im = Image.open(path)
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append(np.asarray(im.convert("RGB"), float))
    return frames, im.info.get("duration") or 50


def seam(frames, k=6, seed=99):
    """Dissolve the last k frames into the first k cell by cell, as ascii_film.py does."""
    h, w = frames[0].shape[:2]
    r = np.random.default_rng(seed).uniform(size=(h // CH + 1, w // CW + 1)).repeat(CH, 0).repeat(CW, 1)[:h, :w, None]
    head, tail = frames[:k], frames[-k:]
    return frames[k:-k] + [np.where(r < (j + 1) / (k + 1), head[j], tail[j]) for j in range(k)]


def halo(im, s, fonts):
    """Soft dark shadow behind the new type, so it reads over busy footage (strokes mode)."""
    sh = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(sh)
    for text, px, _, _, x, y in s["lines"]:
        d.text((x, y), text, font=fonts[px], fill=255, stroke_width=6, stroke_fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    return Image.composite(Image.new("RGB", im.size, (3, 3, 8)), im, sh.point(lambda v: int(v * 0.85)))


def compose(a, s, mask, n, t, fonts, blink_on):
    h, w = a.shape[:2]
    f = a * (1 - mask) + glyph_field(w, h, n, t, seed=sum(map(ord, s["out"]))) * 0.55 * mask
    im = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    if s.get("mode") == "strokes":
        im = halo(im, s, fonts)
    d = ImageDraw.Draw(im)
    for text, px, col, chroma, x, y in s["lines"]:
        if chroma:
            for dx, c in CHROMA:
                d.text((x + dx, y), text, font=fonts[px], fill=c)
        d.text((x, y), text, font=fonts[px], fill=col)
    if s.get("pips"):
        n, total = s["pips"]
        text, px, _, _, x, y = s["lines"][0]
        x0, side, gap = x + d.textlength(text, font=fonts[px]) + 20, 15, 7
        top = y + px * 0.55 - side / 2 + 4
        for k in range(total):
            bx = x0 + k * (side + gap)
            box = [bx, top, bx + side, top + side]
            d.rectangle(box, fill=CYAN) if k < n else d.rectangle(box, outline=(0, 120, 136), width=2)
    if s.get("cursor") and blink_on:
        text, px, _, _, x, y = s["lines"][-1]
        x1 = x + d.textlength(text + " ", font=fonts[px])
        d.rectangle([x1, y + px * 0.18, x1 + px * 0.55, y + px * 1.08], fill=CYAN)
    return im


def cursor_on(s, i):
    return not any(a <= i < b for a, b in s.get("cursor_off", ()))


def render(key):
    s = SPECS[key]
    frames, dur = read_frames(os.path.join(ORIG, s["src"]))
    still_src = frames[s["still"]]
    if s["cut"]:
        frames = seam(frames[s["cut"][0]:s["cut"][1]])
    k = s.get("start", 0)
    frames = frames[k:] + frames[:k]                 # the loop is closed, so rotating keeps it seamless
    n = len(frames)
    h, w = frames[0].shape[:2]
    mask = old_text_mask(w, h, s["old"]) if s.get("mode") == "strokes" else zone_mask(w, h, s["box"])
    fonts = {px: ImageFont.truetype(FONT, px) for _, px, *_ in s["lines"]}
    halves = max(2, round(n * dur / 530))            # ~0.5 s on / off, an even count per loop so it stays seamless
    halves += halves % 2
    out = [compose(a, s, mask, n, i, fonts, (i * halves // n) % 2 == 0 and cursor_on(s, i))
           for i, a in enumerate(frames)]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, s["out"] + ".webp")
    out[0].save(path, save_all=True, append_images=out[1:], duration=int(dur), loop=0, quality=40, method=6)
    still = compose(still_src, s, mask, n, 0, fonts, cursor_on(s, s["still"]))
    spath = os.path.join(OUT, s["out"] + "-still.webp")
    still.save(spath, quality=82, method=6)
    print(f"{key}: {n} frames, {n * dur / 1000:.2f} s loop, {os.path.getsize(path) / 1e6:.2f} MB, "
          f"still {os.path.getsize(spath) // 1024} KB")


def main():
    for key in (sys.argv[1:] or SPECS):
        render(key)


if __name__ == "__main__":
    main()
