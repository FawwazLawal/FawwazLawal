"""Raster film renderer for the profile hero: a first person camera moving through a
3D world built from binary glyphs, following a netrunner made of light and digits.

Everything is a pure function of time t in [0, T), and every moving part is periodic in T,
so frame N and frame 0 join without a seam.

    python3 gen/film.py hero --out <frames dir> [--frames 0,60,120] [--scale 0.5]

Requires numpy and Pillow. Source photos live in source/ (see gen/PHOTOS.md).
"""

import argparse
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"

W, H = 1200, 520
FPS = 24
T = 10.0
NF = int(round(T * FPS))
FOCAL = 620.0
HORIZON = H * 0.47
SEG = 8.0          # world period along z
ZMAX = 78.0        # draw distance

# palette
BLACK = np.array([3, 3, 9], float)
CYAN = np.array([0, 240, 255], float)
TEAL = np.array([0, 180, 200], float)
VIOLET = np.array([122, 44, 255], float)
DEEPV = np.array([48, 14, 110], float)
MAGENTA = np.array([255, 42, 109], float)
PINK = np.array([255, 150, 210], float)
ICE = np.array([225, 240, 255], float)
CRIMSON = np.array([230, 30, 60], float)
EMBER = np.array([255, 120, 40], float)
YELLOW = np.array([252, 238, 10], float)

_FONTS = {}


def font(px):
    px = int(max(6, min(120, round(px))))
    f = _FONTS.get(px)
    if f is None:
        f = ImageFont.truetype(FONT_PATH, px)
        _FONTS[px] = f
    return f


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = np.clip(x, 0.0, 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = np.clip(x, 0.0, 1.0)
    return x ** 2.2


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between."""
    if b <= a:
        return float(t >= a)
    return float(smooth((t - a) / (b - a)))


def hash01(*a):
    v = np.zeros_like(np.asarray(a[0], float))
    for i, x in enumerate(a):
        v = v + np.asarray(x, float) * (12.9898 + 37.719 * i)
    return np.mod(np.sin(v) * 43758.5453, 1.0)


def grad(stops, x):
    """Piecewise linear colour gradient. stops: list of (pos, rgb array)."""
    x = np.clip(np.asarray(x, float), 0, 1)
    out = np.zeros(x.shape + (3,))
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops])
    for c in range(3):
        out[..., c] = np.interp(x, pos, cols[:, c])
    return out


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------

def camera(t):
    """Camera position. Speed is slow while she appears (2 to 5 s) and fast while we
    follow her (7 to 9 s). Total travel over T is exactly 5 segments, so the corridor
    tiles seamlessly."""
    v0, a = 4.0, 1.9
    w = 2 * math.pi / T
    cz = v0 * t + a / w * (math.sin(w * (t - 8.0)) - math.sin(w * (-8.0)))
    cx = 0.22 * math.sin(w * t)
    cy = 1.25 + 0.07 * math.sin(2 * w * t)
    return cx, cy, cz


# ----------------------------------------------------------------------------
# glyph batches: dict of arrays x, y, z (world), size (world), rgb (N,3), a (alpha), ch
# ----------------------------------------------------------------------------

def batch(x, y, z, size, rgb, a, ch, layer=0):
    n = len(x)
    rgb = np.asarray(rgb, float)
    if rgb.ndim == 1:
        rgb = np.tile(rgb, (n, 1))
    return dict(x=np.asarray(x, float), y=np.asarray(y, float), z=np.asarray(z, float),
                size=np.broadcast_to(np.asarray(size, float), (n,)).copy(),
                rgb=rgb, a=np.broadcast_to(np.asarray(a, float), (n,)).copy(),
                ch=np.broadcast_to(np.asarray(ch), (n,)).copy(),
                layer=np.full(n, layer, int))


def cat(batches):
    batches = [b for b in batches if b is not None and len(b["x"])]
    return {k: np.concatenate([b[k] for b in batches]) for k in batches[0]}


def seg_range(cz):
    k0 = int(math.floor(cz / SEG)) - 1
    k1 = int(math.floor((cz + ZMAX) / SEG)) + 1
    return range(k0, k1 + 1)


def bits(seed, t, rate=0.6):
    """0/1 per glyph that changes slowly and periodically in T."""
    ph = hash01(seed, seed * 1.7 + 3.1)
    steps = np.floor((t / T + ph) * max(1, round(rate * T)))
    return (hash01(seed, steps) > 0.5).astype(int)


# ---------------- world pieces ----------------

def _floor_base():
    xs = np.arange(-14.0, 14.01, 1.75)
    zs = np.arange(0.0, SEG, 0.5)
    X, Z = np.meshgrid(xs, zs)
    lines = (X.ravel(), Z.ravel())
    cx = np.arange(-14.0, 14.01, 0.5)
    cross = []
    for zc in (0.0, SEG / 2):
        cross.append((cx, np.full_like(cx, zc)))
    x = np.concatenate([lines[0]] + [c[0] for c in cross])
    z = np.concatenate([lines[1]] + [c[1] for c in cross])
    return x, z


FLOOR = _floor_base()


def floor(t, cam):
    cx, cy, cz = cam
    out = []
    for k in seg_range(cz):
        x, z = FLOOR
        zz = z + k * SEG
        seed = x * 3.3 + zz * 7.1
        ch = bits(seed, t, 0.8)
        dz = zz - cz
        near = np.clip(1 - dz / 40, 0, 1)
        rgb = grad([(0, DEEPV), (0.5, VIOLET * 0.9), (1, CYAN)], near)
        a = (0.22 + 0.5 * near) * np.clip((dz - 1.0) / 6.0, 0.15, 1.0)
        # pulse travelling along the floor lines toward the horizon
        pulse = np.exp(-((np.mod(zz - 9.0 * t, 40.0) - 20.0) / 1.2) ** 2)
        rgb = rgb + pulse[:, None] * (ICE - rgb) * 0.7
        a = np.minimum(1, a + pulse * 0.5)
        out.append(batch(x, np.zeros_like(x), zz, 0.26, rgb, a, ch))
    return cat(out)


def _gate_base():
    pts = []
    w, h, c, s = 4.6, 5.6, 0.9, 0.32
    path = [(-w, 0), (-w, h - c), (-w + c, h), (w - c, h), (w, h - c), (w, 0)]
    for (x0, y0), (x1, y1) in zip(path[:-1], path[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(L / s))
        for i in range(n):
            f = i / n
            pts.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, 0.0))
            pts.append((x0 + (x1 - x0) * f * 0.985 + (0.35 if x0 < 0 and x1 <= x0 + 1e-6 else 0),
                        y0 + (y1 - y0) * f - (0.35 if y0 > h - c - 0.01 and y1 > h - c - 0.01 else 0), 0.35))
    return np.array(pts)


GATE = _gate_base()


def gates(t, cam):
    cx, cy, cz = cam
    out = []
    for k in seg_range(cz):
        if k % 2:
            continue
        zz = k * SEG + SEG * 0.6
        p = GATE
        dz = zz - cz
        near = np.clip(1 - dz / 55, 0, 1)
        idx = np.arange(len(p))
        ch = bits(idx * 1.3 + k * 17.0, t, 1.2)
        tone = 0.5 + 0.5 * np.sin(idx * 0.21 + t * 2 * math.pi / T * 3)
        rgb = grad([(0, VIOLET), (0.6, MAGENTA), (1, PINK)], tone * near + 0.2)
        rgb = rgb * (0.5 + 0.35 * near)
        a = 0.3 + 0.4 * near
        out.append(batch(p[:, 0], p[:, 1], zz + p[:, 2], 0.42, rgb, a, ch))
    return cat(out)


def _tower_base():
    rng = np.random.default_rng(7)
    pts = []
    for side in (-1, 1):
        for j in range(2):
            x0 = side * (6.4 + rng.uniform(0, 3.0))
            z0 = j * SEG / 2 + rng.uniform(0, 1.0)
            depth = rng.uniform(2.0, 3.4)
            height = rng.uniform(4.0, 13.0)
            warm = rng.uniform() < 0.25
            sp = 0.42
            ys = np.arange(0.3, height, sp)
            zs = np.arange(z0, z0 + depth, sp)
            for yy in ys:
                for zz in zs:
                    v = rng.uniform()
                    if v < 0.42:
                        continue
                    kind = 2 if (warm and rng.uniform() < 0.18) else (1 if rng.uniform() < 0.12 else 0)
                    pts.append((x0, yy, zz, kind, v))
            # roof edge
            for zz in zs:
                pts.append((x0, height, zz, 1, 1.0))
    return np.array(pts)


TOWERS = _tower_base()


def towers(t, cam):
    cx, cy, cz = cam
    out = []
    p = TOWERS
    for k in seg_range(cz):
        zz = p[:, 2] + k * SEG
        dz = zz - cz
        near = np.clip(1 - dz / 60, 0, 1)
        kind = p[:, 3]
        base = grad([(0, DEEPV * 0.8), (1, VIOLET * 0.85)], near)
        lit = grad([(0, TEAL * 0.5), (1, CYAN)], near)
        warm = grad([(0, CRIMSON * 0.6), (1, EMBER)], near)
        rgb = np.where((kind == 1)[:, None], lit, np.where((kind == 2)[:, None], warm, base))
        a = (0.2 + 0.55 * near) * (0.6 + 0.4 * p[:, 4])
        seed = p[:, 1] * 5.1 + zz * 2.3 + p[:, 0]
        ch = bits(seed, t, 0.5)
        out.append(batch(p[:, 0], p[:, 1], zz, 0.36, rgb, a, ch))
    return cat(out)


def _streams_base():
    rng = np.random.default_rng(11)
    s = []
    for i in range(46):
        side = rng.choice([-1, 1])
        x = side * rng.uniform(1.8, 6.0)
        y = rng.uniform(2.2, 7.5)
        z0 = rng.uniform(0, 60)
        speed = rng.choice([6.0, 12.0, 18.0])   # speed*T multiple of 60: periodic
        n = rng.integers(8, 18)
        s.append((x, y, z0, speed, n))
    return s


STREAMS = _streams_base()


def streams(t, cam):
    cx, cy, cz = cam
    xs, ys, zs, rgbs, aa, chs = [], [], [], [], [], []
    for i, (x, y, z0, speed, n) in enumerate(STREAMS):
        head = np.mod(z0 - speed * t, 60.0) + 1.0
        for j in range(n):
            zr = head + j * 0.38
            f = j / n
            xs.append(x)
            ys.append(y)
            zs.append(cz + zr)
            col = ICE if j == 0 else (CYAN if f < 0.5 else TEAL)
            rgbs.append(col)
            aa.append((1.0 - f) * 0.95 * min(1, zr / 3))
            chs.append(int(hash01(i * 7 + j, math.floor(t * 6 + i)) > 0.5))
    return batch(xs, ys, zs, 0.3, np.array(rgbs), aa, chs)


def _ico():
    p = (1 + 5 ** 0.5) / 2
    v = np.array([[-1, p, 0], [1, p, 0], [-1, -p, 0], [1, -p, 0], [0, -1, p], [0, 1, p],
                  [0, -1, -p], [0, 1, -p], [p, 0, -1], [p, 0, 1], [-p, 0, -1], [-p, 0, 1]], float)
    v /= np.linalg.norm(v[0])
    edges = []
    for i in range(12):
        for j in range(i + 1, 12):
            if abs(np.linalg.norm(v[i] - v[j]) - 1.0515) < 0.05:
                edges.append((i, j))
    pts = []
    for i, j in edges:
        for f in np.linspace(0, 1, 16, endpoint=False):
            pts.append(v[i] + (v[j] - v[i]) * f)
    return np.array(pts)


ICO = _ico()


def rot(p, ax, ay):
    ca, sa, cb, sb = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay)
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    y, z = y * ca - z * sa, y * sa + z * ca
    x, z = x * cb + z * sb, -x * sb + z * cb
    return np.stack([x, y, z], 1)


def landmarks(t, cam):
    cx, cy, cz = cam
    w = 2 * math.pi * t / T
    out = []
    for (px, py, pz, r, ax, ay, col) in ((-34, 20, 120, 16, 1, 1, VIOLET),
                                          (40, 26, 150, 22, 2, -1, MAGENTA * 0.8)):
        p = rot(ICO, ax * w, ay * w) * r
        z = cz + pz + p[:, 2]
        depthf = 0.5 + 0.5 * (-p[:, 2] / r)
        rgb = col[None, :] * (0.45 + 0.55 * depthf[:, None])
        idx = np.arange(len(p))
        out.append(batch(cx * 0.5 + px + p[:, 0], py + p[:, 1], z, 1.4, rgb,
                         0.35 + 0.4 * depthf, bits(idx + px, t, 0.8)))
    return cat(out)


def _dust_base():
    rng = np.random.default_rng(5)
    n = 150
    return dict(x=rng.uniform(-5, 5, n), y=rng.uniform(-0.2, 5.5, n),
                z0=rng.uniform(0, 12, n), sp=rng.choice([3.6, 7.2], n), s=rng.uniform(0.6, 1.0, n))


DUST = _dust_base()


def dust(t, cam):
    cx, cy, cz = cam
    d = DUST
    zr = np.mod(d["z0"] - d["sp"] * t, 12.0) + 0.6
    tone = hash01(d["x"], d["y"])
    rgb = grad([(0, CYAN), (0.7, VIOLET), (1, MAGENTA)], tone)
    a = np.clip(zr / 2.0, 0, 1) * np.clip((12.6 - zr) / 3, 0, 1) * 0.75
    ch = (tone > 0.5).astype(int)
    return batch(d["x"], d["y"], cz + zr, 0.12 * d["s"], rgb, a, ch, layer=1)


# ----------------------------------------------------------------------------
# the netrunner
# ----------------------------------------------------------------------------

def _load(name, crop, cols, rows, mirror):
    im = Image.open(os.path.join(ROOT, "source", name)).convert("L").crop(crop)
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    big = im.resize((cols * 4, rows * 4), Image.LANCZOS)
    a = np.asarray(big, float) / 255.0
    a = a.reshape(rows, 4, cols, 4).mean(axis=(1, 3))
    return a


def _cloud(name, crop, cols, rows, height, mirror, cut, gamma, seed, fade_bottom=0.0,
           floor_ink=0.0, mask_cut=0.012, key=None):
    raw = _load(name, crop, cols, rows, mirror)
    lum = np.clip((raw - cut) / (1 - cut), 0, 1) ** gamma
    if key is not None:
        # key light: keep the face bright, push everything else down a stop
        kx, ky, kr = key
        yy, xx = np.mgrid[0:rows, 0:cols]
        g = np.exp(-(((xx / cols - kx) / kr) ** 2 + ((yy / rows - ky) / (kr * cols / rows * 0.9)) ** 2))
        lum = lum * (0.5 + 0.7 * g)
    # silhouette: everything that is not the pure black backdrop
    m = np.asarray(Image.fromarray((raw * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), float) / 255
    mask = m > mask_cut
    hair = mask & (lum < floor_ink)
    # hair: sparse, textured ink that follows the photo's own faint strand detail
    tex = np.clip(raw / 0.06, 0, 1)
    rng0 = np.random.default_rng(seed + 7)
    keep_h = rng0.uniform(size=raw.shape) < (0.25 + 0.55 * tex)
    hair = hair & keep_h
    mask = mask & ~(mask & (lum < floor_ink) & ~keep_h)
    lum = np.where(hair, floor_ink * (0.45 + 0.55 * tex), lum)
    sil = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)), float) / 255
    gy, gx = np.gradient(sil)
    gy2, gx2 = np.gradient(lum)
    edge = np.clip(np.hypot(gx, gy) * 2.6 + np.hypot(gx2, gy2) * 0.6, 0, 1)
    # hair volume: the dark mass inside the silhouette becomes sparse lavender light,
    # denser at the silhouette edge (rim)
    hmask = (m > 0.006) & (lum <= 0.05)
    sil2 = np.asarray(Image.fromarray(((m > 0.006) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3)), float) / 255
    hy_, hx_ = np.gradient(sil2)
    hedge = np.clip(np.hypot(hx_, hy_) * 3.0, 0, 1)
    rngh = np.random.default_rng(seed + 9)
    hsel = hmask & (rngh.uniform(size=raw.shape) < (0.16 + 0.8 * hedge)) if floor_ink >= 0 else hmask & False
    lum = np.where(hsel, 0.18 + 0.5 * hedge, lum)
    edge = np.maximum(edge, hedge * hsel)
    hair = hsel
    rr, cc = np.nonzero((lum > 0.05) | hsel)
    v = lum[rr, cc]
    e = edge[rr, cc]
    hz = hair[rr, cc]
    cell = height / rows
    jit = np.random.default_rng(seed + 3)
    x = (cc - cols / 2 + jit.uniform(-0.5, 0.5, len(cc))) * cell
    y = (rows - rr + jit.uniform(-0.5, 0.5, len(rr))) * cell
    keep = np.ones(len(x), bool)
    if fade_bottom:
        f = rr / rows
        rng = np.random.default_rng(seed)
        keep = rng.uniform(size=len(x)) > smooth((f - (1 - fade_bottom)) / fade_bottom)
    rng = np.random.default_rng(seed + 1)
    return dict(x=x[keep], y=y[keep], v=v[keep], e=e[keep], hair=hz[keep], cell=cell,
                r=rng.uniform(size=keep.sum()), r2=rng.uniform(size=keep.sum()),
                r3=rng.uniform(size=keep.sum()))


HER = None
HAND = None


def _init_chars():
    global HER, HAND
    if HER is None:
        crop = (420, 600, 2300, 2760)
        key = (0.33, 0.36, 0.16)
        HER = (_cloud("glance-back.jpg", crop, 168, 193, 2.85, True, cut=0.03, gamma=0.62,
                      seed=21, fade_bottom=0.3, floor_ink=0.0, mask_cut=0.04, key=key),
               _cloud("glance-back.jpg", crop, 66, 76, 2.85, True, cut=0.03, gamma=0.62,
                      seed=22, fade_bottom=0.3, floor_ink=0.0, mask_cut=0.04, key=key))
        HAND = (_cloud("hand.jpg", (560, 1080, 1460, 2700), 60, 108, 1.3, True,
                       cut=0.05, gamma=0.75, seed=31, fade_bottom=0.35),
                _cloud("hand.jpg", (560, 1080, 1460, 2700), 24, 43, 1.3, True,
                       cut=0.05, gamma=0.75, seed=32, fade_bottom=0.35))


LAVENDER = np.array([186, 156, 255], float)
HER_GRAD = [(0.0, DEEPV), (0.22, VIOLET), (0.45, MAGENTA), (0.72, PINK), (1.0, ICE)]


def her_track(t):
    """Her anchor relative to the camera: (x, y, z_rel) and visibility state."""
    # approach: she is ahead, the camera slowly gains on her
    z_rel = 7.0 - 0.9 * ramp(t, 1.4, 5.8)
    # she leaves: accelerate away down the corridor
    go = ease_in((t - 6.2) / 3.0) if t > 6.2 else 0.0
    z_rel += 30.0 * go
    x = 1.15 - 0.95 * go
    walk = 0.05 * math.sin((t - 6.2) * 2 * math.pi * 1.8) * (1 if t > 6.2 else 0)
    y = 0.45 + walk + 0.03 * math.sin(t * 1.3)
    return x, y, z_rel, go


def netrunner(t, cam):
    _init_chars()
    cx, cy, cz = cam
    if t < 1.3 or t > 9.85:
        return None
    hx, hy, hz, go = her_track(t)
    return cat([_her_cloud(t, cam, HER[0], 2, 1.0), _her_cloud(t, cam, HER[1], 3, 0.55)])


def _her_cloud(t, cam, c, layer, gain):
    cx, cy, cz = cam
    hx, hy, hz, go = her_track(t)
    # materialize: each cell flies in from the surrounding data field
    delay = 0.9 * c["r"] * 0.6 + 0.9 * 0.4 * (1 - c["y"] / 2.85)
    m = ease_out((t - 1.4 - delay) / 0.75)
    sx = (c["r2"] - 0.5) * 9.0
    sy = (c["r3"] - 0.5) * 6.0 + 1.5
    sz = (c["r"] - 0.3) * 14.0
    # dissolve at the end: cells peel off and stream forward
    dsv = smooth((t - 8.7 - 0.8 * c["r2"]) / 0.6)
    lx = c["x"] * (1 - m) * 0 + c["x"]
    x = hx + lx + (1 - m) * sx + dsv * (c["r3"] - 0.5) * 3
    y = hy + c["y"] + (1 - m) * sy + dsv * (c["r"] - 0.5) * 2
    relief = -0.22 * c["v"]
    z = cz + hz + relief + (1 - m) * sz + dsv * 9 * c["r"]
    v = c["v"]
    rgb = grad(HER_GRAD, v)
    # luminous lavender hair: the dark mass of her hair gets its own light
    rgb = np.where(c["hair"][:, None], LAVENDER * (0.5 + 0.7 * v[:, None]), rgb)
    # rim light: silhouette edges go cyan / ice
    rim = c["e"] ** 1.4
    rgb = rgb + rim[:, None] * (CYAN - rgb) * 0.75
    # notice beat: a light sweep runs across her at 3.0 to 3.8 s
    if 2.9 < t < 4.0:
        sweep = np.exp(-((c["x"] + 1.8 - 4.0 * (t - 3.0)) / 0.25) ** 2)
        rgb = rgb + sweep[:, None] * (ICE - rgb) * 0.8
    a = (0.3 + 0.7 * np.maximum(v, rim)) * m * (1 - dsv) * gain
    # while she runs, the far half of her trails into data
    ch = ((v > 0.5) ^ (hash01(c["x"] * 9, np.floor(t * 3)) > 0.93)).astype(int)
    size = c["cell"] * 1.45
    out = [batch(x, y, z, size, rgb, a, ch, layer=layer)]
    if go > 0.02 and layer == 2:
        for k, fa in ((1, 0.32), (2, 0.16), (3, 0.08)):
            out.append(batch(x + 0.06 * k * (c["r2"] - 0.5), y, z - 0.55 * k * (0.5 + go),
                             size, rgb * 0.9, a * fa * min(1, go * 4), ch, layer=2))
    return cat(out)


def beckon(t, cam):
    _init_chars()
    cx, cy, cz = cam
    if t < 3.3 or t > 6.4:
        return None
    return cat([_hand_cloud(t, cam, HAND[0], 2, 1.0), _hand_cloud(t, cam, HAND[1], 3, 0.6)])


def _hand_cloud(t, cam, c, layer, gain):
    cx, cy, cz = cam
    hx, hy, hz, go = her_track(t)
    m = ease_out((t - 3.35 - 0.35 * c["r"]) / 0.55)
    # beckon: rotate about the wrist, two slow "come here" curls
    ang = math.radians(16) * math.sin(2 * math.pi * 1.25 * max(0, t - 3.9)) * ramp(t, 3.8, 4.1) * (1 - ramp(t, 5.4, 5.7))
    px, py = c["x"], c["y"]
    rx = px * math.cos(ang) - py * math.sin(ang)
    ry = px * math.sin(ang) + py * math.cos(ang)
    # absorbed back into her at the end
    ab = smooth((t - 5.7 - 0.4 * c["r2"]) / 0.5)
    ax0 = hx - 1.7
    ay0 = hy + 0.95
    az0 = cz + hz - 1.0
    tx = hx + c["x"] * 0.2
    ty = hy + 1.6 + c["y"] * 0.3
    tz = cz + hz
    x = (ax0 + rx) * (1 - ab) + tx * ab + (1 - m) * (c["r2"] - 0.5) * 5
    y = (ay0 + ry) * (1 - ab) + ty * ab + (1 - m) * (c["r3"] - 0.5) * 4
    z = az0 * (1 - ab) + tz * ab + (1 - m) * (c["r"] - 0.2) * 8
    v = c["v"]
    rgb = grad([(0, VIOLET), (0.45, MAGENTA), (0.8, PINK), (1, ICE)], v)
    rgb = rgb + (c["e"] ** 1.2)[:, None] * (CYAN - rgb) * 0.8
    a = (0.3 + 0.7 * v) * m * (1 - 0.6 * ab) * (1 - ramp(t, 6.1, 6.4)) * gain
    ch = (v > 0.5).astype(int)
    return batch(x, y, z, c["cell"] * 1.5, rgb, a, ch, layer=layer)


# ----------------------------------------------------------------------------
# frame
# ----------------------------------------------------------------------------

def project(b, cam):
    cx, cy, cz = cam
    dz = b["z"] - cz
    ok = dz > 0.35
    for k in list(b):
        b[k] = b[k][ok]
    dz = dz[ok]
    sx = W / 2 + FOCAL * (b["x"] - cx) / dz
    sy = HORIZON - FOCAL * (b["y"] - cy) / dz
    px = FOCAL * b["size"] / dz
    fog = np.clip(1 - (dz - 18) / (ZMAX - 18), 0, 1) ** 1.3
    fog = np.where(b["layer"] == 2, 1.0, fog)
    fog = np.where(b["size"] > 1.0, 1.0, fog)  # landmarks are lit, not fogged
    haze = np.clip((dz - 12) / 60, 0, 1)[:, None]
    rgb = b["rgb"] * (1 - 0.45 * haze) + VIOLET[None, :] * 0.45 * haze * 0.6
    return sx, sy, px, rgb * (b["a"] * fog)[:, None], b["ch"], dz, b["layer"]


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.zeros((H, W, 3)) + BLACK
    d = np.hypot((xx - W / 2) / (W * 0.5), (yy - HORIZON) / (H * 0.35))
    glow = np.exp(-d ** 2 * 2.2)
    img += glow[..., None] * (VIOLET * 0.15 + MAGENTA * 0.04)
    band = np.exp(-((yy - HORIZON) / 5.0) ** 2) * np.exp(-((xx - W / 2) / (W * 0.4)) ** 2)
    img += band[..., None] * (MAGENTA * 0.16 + VIOLET * 0.14)
    sky = np.clip((HORIZON - yy) / HORIZON, 0, 1)
    img += sky[..., None] * DEEPV * 0.12
    return img


BG = None


def render(t, scale=1.0, overlay=None):
    global BG
    if BG is None:
        BG = background()
    cam = camera(t)
    parts = [floor(t, cam), towers(t, cam), gates(t, cam), streams(t, cam),
             landmarks(t, cam), netrunner(t, cam), beckon(t, cam)]
    world = cat(parts)
    sx, sy, px, col, ch, dz, layer = project(world, cam)
    buf = BG.copy()
    inside = (sx > -40) & (sx < W + 40) & (sy > -40) & (sy < H + 40)
    # tiny glyphs: additive pixel dust
    tiny = inside & (px < 6.5) & (layer != 2) & (layer != 3)
    ix = np.clip(sx[tiny].astype(int), 0, W - 1)
    iy = np.clip(sy[tiny].astype(int), 0, H - 1)
    wgt = np.clip(px[tiny] / 6.5, 0.25, 1.0)[:, None]
    np.add.at(buf, (iy, ix), col[tiny] * wgt * 0.9)
    # her fine layer: 2x2 splats, full weight, for photographic detail
    fine = inside & (layer == 2)
    fx = np.clip(sx[fine].astype(int), 0, W - 2)
    fy = np.clip(sy[fine].astype(int), 0, H - 2)
    fc = col[fine] * 0.62
    for oy in (0, 1):
        for ox in (0, 1):
            np.add.at(buf, (fy + oy, fx + ox), fc)
    img = Image.fromarray(np.clip(buf, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    big = np.nonzero(inside & (((px >= 6.5) & (layer == 0)) | (layer == 3)))[0]
    big = big[np.argsort(-dz[big])]
    for i in big:
        c = col[i]
        if c.max() < 6:
            continue
        d.text((sx[i], sy[i]), "1" if ch[i] else "0", font=font(px[i]),
               fill=(int(min(255, c[0])), int(min(255, c[1])), int(min(255, c[2]))), anchor="mm")
    # foreground dust on its own layer, blurred for depth of field
    du = dust(t, cam)
    fsx, fsy, fpx, fcol, fch, fdz, _ = project(du, cam)
    fg = Image.new("RGB", (W, H))
    fd = ImageDraw.Draw(fg)
    for i in np.argsort(-fdz):
        c = fcol[i]
        if c.max() < 6 or not (-60 < fsx[i] < W + 60 and -60 < fsy[i] < H + 60):
            continue
        fd.text((fsx[i], fsy[i]), "1" if fch[i] else "0", font=font(fpx[i]),
                fill=tuple(int(min(255, v)) for v in c), anchor="mm")
    fg = fg.filter(ImageFilter.GaussianBlur(2.2))
    arr = np.asarray(img, float) + np.asarray(fg, float)
    # bloom
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    small = base.resize((W // 2, H // 2), Image.BILINEAR)
    b1 = np.asarray(small.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR), float)
    b2 = np.asarray(small.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR), float)
    arr = arr + b1 * 0.45 + b2 * 0.4
    # chromatic aberration grows toward the frame edges
    out = arr.copy()
    out[:, 2:, 0] = arr[:, :-2, 0] * 0.6 + arr[:, 2:, 0] * 0.4
    out[:, :-2, 2] = arr[:, 2:, 2] * 0.6 + arr[:, :-2, 2] * 0.4
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.55 * np.clip(np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) - 0.35, 0, 1) ** 1.6
    out *= vig[..., None]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    (overlay or hud)(img, t)
    if scale != 1.0:
        img = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    return img


BEATS = [(0.0, "sys // link established"), (1.4, "sys // presence detected"),
         (3.0, "sys // she sees you"), (4.0, "sys // she wants you to follow"),
         (6.2, "sys // pursuit"), (8.8, "sys // deeper"), (9.6, "sys // link established")]


def hud(img, t):
    d = ImageDraw.Draw(img)
    f_big = font(40)
    f_mid = font(15)
    f_sm = font(12)
    x0, y0 = 48, 50
    # name with a quiet chromatic split
    d.text((x0 - 2, y0), "FAWWAZ LAWAL", font=f_big, fill=(150, 20, 70))
    d.text((x0 + 2, y0), "FAWWAZ LAWAL", font=f_big, fill=(0, 140, 160))
    d.text((x0, y0), "FAWWAZ LAWAL", font=f_big, fill=(236, 234, 245))
    d.text((x0, y0 + 54), "S O F T W A R E   E N G I N E E R", font=f_mid, fill=(200, 196, 220))
    d.text((x0, y0 + 80), "GO  ·  SWIFT  ·  SWIFTUI  ·  SECURITY", font=f_sm, fill=(0, 220, 240))
    beat = [b for b in BEATS if b[0] <= t][-1][1]
    d.text((x0, H - 40), "> " + beat, font=f_sm, fill=(0, 170, 190))
    # corner brackets
    for (x, y, dx, dy) in ((14, 14, 1, 1), (W - 15, 14, -1, 1), (14, H - 15, 1, -1), (W - 15, H - 15, -1, -1)):
        d.line([(x, y), (x + 26 * dx, y)], fill=(0, 150, 170), width=1)
        d.line([(x, y), (x, y + 26 * dy)], fill=(0, 150, 170), width=1)
    # follow prompt
    if 4.2 <= t < 9.3:
        on = (t * 2) % 1 < 0.6
        d.text((x0, y0 + 112), "> follow her" + ("_" if on else " "), font=f_mid, fill=(252, 238, 10))


CHAPTERS = [
    ("01", "ENTRY", "identity", 7.6),
    ("02", "SYSTEMS", "how I engineer", 7.9),
    ("03", "SELECTED WORK", "what I have built", 8.4),
    ("04", "TOOLKIT", "what I build with", 8.95),
    ("05", "EXIT", "end of transmission", 9.55),
]
BAND = 210


def chapter(k):
    num, title, sub, t = CHAPTERS[k]

    def overlay(img, _t):
        d = ImageDraw.Draw(img)
        top = int(HORIZON - BAND * 0.55)
        x0, y0 = 48, top + 62
        f_num = font(15)
        f_t = font(38)
        f_s = font(13)
        d.text((x0, y0), f"{num} //", font=f_num, fill=(0, 220, 240))
        for dx, col in ((-2, (150, 20, 70)), (2, (0, 140, 160)), (0, (236, 234, 245))):
            d.text((x0 + dx, y0 + 22), title, font=f_t, fill=col)
        d.text((x0, y0 + 72), "> " + sub, font=f_s, fill=(186, 156, 255))
        for (x, y, dx, dy) in ((14, top + 12, 1, 1), (W - 15, top + 12, -1, 1),
                               (14, top + BAND - 13, 1, -1), (W - 15, top + BAND - 13, -1, -1)):
            d.line([(x, y), (x + 22 * dx, y)], fill=(0, 150, 170), width=1)
            d.line([(x, y), (x, y + 22 * dy)], fill=(0, 150, 170), width=1)

    img = render(t, overlay=overlay)
    top = int(HORIZON - BAND * 0.55)
    return img.crop((0, top, W, top + BAND))


def _work(args):
    i, out, scale = args
    t = i / FPS
    render(t, scale).save(os.path.join(out, f"f{i:04d}.png"))
    return i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", nargs="?", default="hero")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", default="")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--jobs", type=int, default=14)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.scene == "chapters":
        for k, c in enumerate(CHAPTERS):
            chapter(k).save(os.path.join(a.out, f"chapter-{c[0]}-{c[1].lower().replace(' ', '-')}.png"), optimize=True)
        print("rendered chapters")
        return
    idx = [int(x) for x in a.frames.split(",")] if a.frames else list(range(NF))
    with Pool(a.jobs) as p:
        for i in p.imap_unordered(_work, [(i, a.out, a.scale) for i in idx]):
            pass
    print(f"rendered {len(idx)} frames to {a.out}")


if __name__ == "__main__":
    main()
