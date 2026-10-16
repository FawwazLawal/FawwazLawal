"""Convert the Flow footage into a binary ASCII film for the profile hero.

Every frame is sampled onto a grid of 0/1 glyphs. Cell brightness picks the glyph and its
ink, the footage supplies the colour, edges get extra light, and a faint blurred copy of the
frame sits underneath as glow. Segments from the three shots are cut together with short
glyph dissolves, and the white-out at the gateway dissolves back into the opening so the
loop has no seam.

    python3 gen/ascii_film.py --out <frames dir> [--test]

Needs ffmpeg, numpy and Pillow. The footage lives in source/ (not committed).
"""

import argparse
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "source")
FONT = "/System/Library/Fonts/Menlo.ttc"

OUT_W, OUT_H = 1200, 672
CW, CH = 7, 12                       # glyph cell in output pixels
COLS, ROWS = OUT_W // CW, OUT_H // CH
FPS = 20

# (shot file, start s, end s). Cut list for the hero, in order.
CUTS = [
    ("Shot 1.mp4", 1.0, 9.8),        # corridor, she materializes, turns, eye contact
    ("Shot 2.mp4", 1.55, 2.95),      # the beckon
    ("Shot 2.mp4", 3.35, 8.7),       # she runs, we follow through the archway
    ("Shot 3.mp4", 7.25, 8.2),       # white-out at the gateway
]
DISSOLVE = 5                         # frames of glyph dissolve between cuts
BAND = 210                           # height of every banner on the page


def glyph_masks():
    f = ImageFont.truetype(FONT, 11)
    masks = {}
    for ch in "01":
        im = Image.new("L", (CW, CH), 0)
        d = ImageDraw.Draw(im)
        d.text((CW / 2, CH / 2), ch, font=f, fill=255, anchor="mm")
        masks[ch] = np.asarray(im, float) / 255.0
    return np.stack([masks["0"], masks["1"]])     # (2, CH, CW)


MASKS = glyph_masks()


def read_frames(path, t0, t1):
    """Decode [t0, t1) at FPS, scaled to the output size, as uint8 arrays."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", path,
           "-vf", f"fps={FPS},scale={OUT_W}:-2,crop={OUT_W}:{OUT_H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    n = len(raw) // (OUT_W * OUT_H * 3)
    return np.frombuffer(raw, np.uint8)[: n * OUT_W * OUT_H * 3].reshape(n, OUT_H, OUT_W, 3)


def to_ascii(frame, seed=0):
    img = Image.fromarray(frame)
    cell = np.asarray(img.resize((COLS, ROWS), Image.BOX), float) / 255.0     # (R, C, 3)
    lum = cell @ np.array([0.299, 0.587, 0.114])
    # edges at cell resolution brighten the silhouette and structure lines
    gy, gx = np.gradient(lum)
    edge = np.clip(np.hypot(gx, gy) * 3.0, 0, 1)
    # ink: per-frame contrast stretch so the haze drops to black and the subject pops
    lo, hi = np.percentile(lum, 42), np.percentile(lum, 99.6)
    glob = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1) ** 1.35
    # local contrast: detail relative to the neighbourhood, so a dark face against a
    # brighter wall still gets its features drawn
    L = Image.fromarray((lum * 255).astype(np.uint8))
    mu = np.asarray(L.filter(ImageFilter.GaussianBlur(5)), float) / 255
    sd = np.sqrt(np.asarray(Image.fromarray((np.clip((lum - mu) ** 2 * 4, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), float) / 255 / 4) + 0.02
    local = np.clip((lum - mu) / (sd * 2.5) * 0.5 + 0.5, 0, 1)
    detail = np.clip((local - 0.5) * 2, 0, 1)
    ink = np.clip(glob + edge * 0.6 * (glob > 0.02), 0, 1)
    ink[ink < 0.06] = 0
    # colour: hue from the footage, pushed toward saturation
    mx = cell.max(axis=2, keepdims=True)
    hue = cell / np.maximum(mx, 1e-3)
    hue = np.clip((hue - 0.35) / 0.65, 0, 1) * 0.75 + 0.25
    col = hue * (0.35 + 0.65 * ink[..., None]) * ink[..., None] ** 0.5 * 255 * 1.1
    # glyph choice: bright cells are 1, dim are 0; a stable per-cell hash breaks up runs
    rng = np.random.default_rng(seed + 11)
    jitter = np.random.default_rng(7).uniform(-0.08, 0.08, lum.shape)
    ch = (ink + jitter > 0.55).astype(int)
    m = MASKS[ch]                                 # (R, C, CH, CW)
    blocks = m[..., None] * col[:, :, None, None, :]
    glyphs = np.zeros((OUT_H, OUT_W, 3))
    gx0, gy0 = (OUT_W - COLS * CW) // 2, (OUT_H - ROWS * CH) // 2
    glyphs[gy0:gy0 + ROWS * CH, gx0:gx0 + COLS * CW] = blocks.transpose(0, 2, 1, 3, 4).reshape(ROWS * CH, COLS * CW, 3)
    # glow: a dim blurred copy of the frame underneath, plus bloom from the glyphs
    base = np.asarray(img.filter(ImageFilter.GaussianBlur(10)), float) * 0.05
    gimg = Image.fromarray(np.clip(glyphs, 0, 255).astype(np.uint8))
    small = gimg.resize((OUT_W // 3, OUT_H // 3), Image.BILINEAR)
    bloom = np.asarray(small.filter(ImageFilter.GaussianBlur(3)).resize((OUT_W, OUT_H), Image.BILINEAR), float)
    out = base + glyphs + bloom * 0.7
    # her: pale hair and skin are the only low-saturation bright things in the footage.
    # Let the real image resolve through there, under a veil of glyphs and scanlines.
    f = np.asarray(img, float) / 255
    mxp, mnp = f.max(2), f.min(2)
    sat = (mxp - mnp) / np.maximum(mxp, 1e-3)
    subj = ((sat < 0.38) & (mxp > 0.42)).astype(np.uint8) * 255
    subj[:110, :420] = 0                                   # keep the title area clean
    sm = Image.fromarray(subj).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    m = np.asarray(sm, float)[..., None] / 255 * 0.85
    scan = (np.arange(OUT_H) % 3 != 0).astype(float)[:, None, None] * 0.25 + 0.75
    real = np.asarray(img, float) * scan * 1.05
    out = out * (1 - m * 0.75) + real * m + glyphs * m * 0.35
    # slight chromatic split
    o = out.copy()
    o[:, 1:, 0] = out[:, :-1, 0]
    o[:, :-1, 2] = out[:, 1:, 2]
    return np.clip(o, 0, 255).astype(np.uint8)


def dissolve(a, b, k, n, seed):
    """Glyph-cell dissolve from frame a to frame b, step k of n."""
    r = np.random.default_rng(seed).uniform(size=(ROWS, COLS))
    m = (r < (k + 1) / (n + 1)).repeat(CH, 0).repeat(CW, 1)
    m = np.pad(m, ((0, OUT_H - m.shape[0]), (0, OUT_W - m.shape[1])), mode="edge")[..., None]
    return np.where(m, b, a)


def hud(img):
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 34)
    mid = ImageFont.truetype(FONT, 13)
    x, y = 40, 34
    for dx, c in ((-2, (150, 20, 70)), (2, (0, 140, 160)), (0, (236, 234, 245))):
        d.text((x + dx, y), "FAWWAZ LAWAL", font=big, fill=c)
    d.text((x, y + 46), "S O F T W A R E   E N G I N E E R", font=mid, fill=(200, 196, 220))
    d.text((x, y + 68), "GO  ·  SWIFT  ·  SWIFTUI  ·  SECURITY", font=mid, fill=(0, 220, 240))
    return img


# Virtual camera for the hero band: (output seconds, band top in frame pixels).
# Hand keyed against the footage: horizon, her materializing, the turn, eye contact
# and the beckon framed on her face, then the chase down the corridor.
CAMERA = [(0.0, 200), (1.8, 200), (2.8, 170), (4.3, 150), (5.8, 130), (6.8, 70),
          (7.6, 40), (8.3, 10), (9.4, 10), (9.7, 40), (10.3, 120), (11.0, 150),
          (13.0, 175), (14.5, 200), (15.7, 200)]


def track(frames):
    t = np.arange(len(frames)) / FPS
    kt = np.array([k[0] for k in CAMERA])
    kv = np.array([k[1] for k in CAMERA], float)
    lin = np.interp(t, kt, kv)
    k = np.exp(-0.5 * (np.arange(-12, 13) / 5.0) ** 2)
    k /= k.sum()
    pad = np.concatenate([lin[-12:], lin, lin[:12]])
    sm = np.convolve(pad, k, mode="same")[12:-12]
    return np.clip(sm, 0, OUT_H - BAND).astype(int)


def hero_band(im):
    big = ImageFont.truetype(FONT, 34)
    mid = ImageFont.truetype(FONT, 13)
    a = np.asarray(im, float)
    ramp = np.clip((np.arange(OUT_W) - 160) / 420, 0, 1)[None, :, None]
    im = Image.fromarray((a * (0.3 + 0.7 * ramp)).astype(np.uint8))
    d = ImageDraw.Draw(im)
    x, y = 44, 48
    for dx, c in ((-2, (150, 20, 70)), (2, (0, 140, 160)), (0, (236, 234, 245))):
        d.text((x + dx, y), "FAWWAZ LAWAL", font=big, fill=c)
    d.text((x, y + 50), "S O F T W A R E   E N G I N E E R", font=mid, fill=(200, 196, 220))
    d.text((x, y + 72), "GO  \u00b7  SWIFT  \u00b7  SWIFTUI  \u00b7  SECURITY", font=mid, fill=(0, 220, 240))
    for (bx, by, dx, dy) in ((12, 12, 1, 1), (OUT_W - 13, 12, -1, 1), (12, BAND - 13, 1, -1), (OUT_W - 13, BAND - 13, -1, -1)):
        d.line([(bx, by), (bx + 22 * dx, by)], fill=(0, 150, 170), width=1)
        d.line([(bx, by), (bx, by + 22 * dy)], fill=(0, 150, 170), width=1)
    return im


def _conv(args):
    i, frame, top, out = args
    band = Image.fromarray(to_ascii(frame, i)).crop((0, top, OUT_W, top + BAND))
    hero_band(band).save(os.path.join(out, f"a{i:04d}.png"))
    return i


def build(out, jobs=14):
    os.makedirs(out, exist_ok=True)
    segs = [read_frames(os.path.join(SRC, f), a, b) for f, a, b in CUTS]
    seq = []
    for si, seg in enumerate(segs):
        frames = list(seg)
        if seq:
            # dissolve the tail of the previous cut into the head of this one
            prev_tail = seq[-DISSOLVE:]
            seq = seq[:-DISSOLVE]
            for k in range(DISSOLVE):
                seq.append(("mix", prev_tail[k], frames[k], k, si))
            frames = frames[DISSOLVE:]
        seq.extend(frames)
    # loop seam: dissolve the white-out into the opening frames
    head = seq[:DISSOLVE]
    tail = seq[-DISSOLVE:]
    seq = seq[DISSOLVE:-DISSOLVE]
    seq.extend(("mix", tail[k], head[k], k, 99) for k in range(DISSOLVE))

    def resolve(x):
        if isinstance(x, tuple):
            _, a, b, k, s = x
            return dissolve(resolve(a), resolve(b), k, DISSOLVE, s)
        return x

    frames = [resolve(x) for x in seq]
    tops = track(frames)
    with Pool(jobs) as p:
        for _ in p.imap_unordered(_conv, [(i, f, int(tops[i]), out) for i, f in enumerate(frames)], chunksize=4):
            pass
    print(f"{len(frames)} frames, {len(frames) / FPS:.1f}s at {FPS} fps -> {out}")


LOOPS = [
    # num, title, subtitle, shot, start s, end s, band centre y
    ("01", "SELECTED WORK", "what I have built", "Shot 3.mp4", 0.0, 1.5, 300),
    ("02", "RESTRICTED", "private repositories", "Shot 2.mp4", 8.6, 10.0, 300),
    ("03", "SYSTEMS", "how I engineer", "Shot 1.mp4", 0.2, 2.4, 280),
    ("04", "TOOLKIT", "what I build with", "Shot 3.mp4", 1.6, 3.2, 260),
    ("05", "EXIT", "end of transmission", "Shot 3.mp4", 8.4, 10.0, 400),
]
LOOP_FPS = 15


def title_band(im, num, title, sub):
    big = ImageFont.truetype(FONT, 38)
    num_f = ImageFont.truetype(FONT, 15)
    sub_f = ImageFont.truetype(FONT, 13)
    a = np.asarray(im, float)
    ramp = np.clip((np.arange(OUT_W) - 120) / 380, 0, 1)[None, :, None]
    im = Image.fromarray((a * (0.35 + 0.65 * ramp)).astype(np.uint8))
    d = ImageDraw.Draw(im)
    x, y = 44, 58
    d.text((x, y), f"{num} //", font=num_f, fill=(0, 220, 240))
    for dx, c in ((-2, (150, 20, 70)), (2, (0, 140, 160)), (0, (236, 234, 245))):
        d.text((x + dx, y + 22), title, font=big, fill=c)
    d.text((x, y + 72), "> " + sub, font=sub_f, fill=(186, 156, 255))
    for (bx, by, dx, dy) in ((12, 12, 1, 1), (OUT_W - 13, 12, -1, 1), (12, BAND - 13, 1, -1), (OUT_W - 13, BAND - 13, -1, -1)):
        d.line([(bx, by), (bx + 22 * dx, by)], fill=(0, 150, 170), width=1)
        d.line([(bx, by), (bx, by + 22 * dy)], fill=(0, 150, 170), width=1)
    return im


def _loop_frame(args):
    i, fr, top = args
    return i, np.asarray(Image.fromarray(to_ascii(fr, i)).crop((0, top, OUT_W, top + BAND)))


def chapter_loops(out, jobs=14):
    os.makedirs(out, exist_ok=True)
    for num, title, sub, shot, t0, t1, cy in LOOPS:
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", os.path.join(SRC, shot),
               "-vf", f"fps={LOOP_FPS},scale={OUT_W}:-2,crop={OUT_W}:{OUT_H}",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(cmd, check=True, capture_output=True).stdout
        n = len(raw) // (OUT_W * OUT_H * 3)
        frames = np.frombuffer(raw, np.uint8)[: n * OUT_W * OUT_H * 3].reshape(n, OUT_H, OUT_W, 3)
        top = max(0, min(OUT_H - BAND, cy - BAND // 2))
        with Pool(jobs) as p:
            res = dict(p.map(_loop_frame, [(i, f, top) for i, f in enumerate(frames)]))
        seq = [res[i] for i in range(n)]
        # seamless loop: glyph-dissolve the tail into the head
        k = 6
        r = np.random.default_rng(int(num)).uniform(size=(BAND // CH + 1, COLS + 1))
        r = r.repeat(CH, 0).repeat(CW, 1)[:BAND, :OUT_W][..., None]
        head, tail = seq[:k], seq[-k:]
        seq = seq[k:-k] + [np.where(r < (j + 1) / (k + 1), head[j], tail[j]) for j in range(k)]
        ims = [title_band(Image.fromarray(f), num, title, sub) for f in seq]
        name = os.path.join(out, f"chapter-{num}-{title.lower().replace(' ', '-')}.webp")
        ims[0].save(name, save_all=True, append_images=ims[1:], duration=int(1000 / LOOP_FPS),
                    loop=0, quality=40, method=6)
        print(f"{os.path.basename(name)} {len(ims)} frames {os.path.getsize(name) // 1024} KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--test", action="store_true", help="convert a few single frames only")
    ap.add_argument("--chapter-loops", action="store_true", help="render animated chapter bands")
    a = ap.parse_args()
    if a.chapter_loops:
        chapter_loops(a.out)
        return
    if a.test:
        os.makedirs(a.out, exist_ok=True)
        for f, t in (("Shot 1.mp4", 5.0), ("Shot 1.mp4", 9.2), ("Shot 2.mp4", 2.3), ("Shot 2.mp4", 6.5)):
            fr = read_frames(os.path.join(SRC, f), t, t + 0.06)[0]
            hud(Image.fromarray(to_ascii(fr))).save(os.path.join(a.out, f"test_{f[5]}_{t}.png"))
        print("test frames written")
        return
    build(a.out)


if __name__ == "__main__":
    main()
