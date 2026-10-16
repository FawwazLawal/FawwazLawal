"""Photo to glyph pipeline (DESIGN.md sections 3 and 6): Floyd Steinberg.

A photograph is loaded with Pillow, turned into a single luminance channel,
cropped, optionally mirrored, resampled onto the glyph grid (cells are cw x ch
viewBox px, so the grid is non square), tone worked (black cut, contrast
stretch, gamma, unsharp mask for local contrast, per source extras) and then
quantized to the ink levels {0, 1, 2, 3, 5} with serpentine Floyd Steinberg
error diffusion. The background is forced to level 0 (no error is diffused into
it), the brightest few percent of cells get the HILITE level 5, and for the
front visor photo a curved band of cells is forced to level 4 (YELLOW).

Per source extras:
  front     the busy neon LED background goes through an HSV pass, v = L * (1 -
            k * S') with a soft knee on the saturation, a soft elliptical mask
            around head and collar, a grey opening that erases the white LED
            cores, a collar lift, a highlight knee so the blown out hair
            dithers into texture, and the visor band.
  profile   the rim light is a one cell line at 60 rows, so the rim is
            thickened with a max filter on the supersample before the reduce,
            and the enclosed head interior is seeded with a sparse level 1
            field (denser near the rim) so the head reads as a lit volume.
  glance    a face ellipse (source px) gets a local lift and a tight unsharp
            so her turned face is the brightest cluster after the sleeves; the
            bottom rows fade so the figure dissolves into the floor.
  all       seeded threshold jitter in the dither breaks the FS worms, lone
            level 5 cells become short strokes, lone specks are dropped.

Every animation helper here describes keyframes through lib.Timeline so a
frozen frame can be rendered at any time.
"""

import math
import os
import random
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import lib
from lib import (Timeline, glyph_rows, moving_group, uid, fmt, svg, BG, CYAN, MAGENTA,
                 CYAN_DIM)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SOURCES = {
    "glance": "source/glance-back.jpg",
    "profile": "source/profile.jpg",
    "front": "source/front-visor.jpg",
    "hand": "source/hand.jpg",
}

# curated crops in source pixels (x0, y0, x1, y1), tuned by looking at the photos
CROPS = {
    # head, back, bow and sleeves; the skirt is out so a row is 33 source px
    # and her face is about 10 rows tall at 74 rows
    "glance": (250, 540, 2160, 3000),
    "profile": (150, 330, 2250, 2900),
    # face and collar; the bottom is trimmed to the fur so the outro's rows
    # all carry ink
    "front": (650, 350, 1900, 1950),
    "hand": (600, 1080, 1420, 2500),
    # head and shoulders crop for the small divider figures (crop="glance_head")
    "glance_head": (780, 320, 2160, 2100),
    # head only (rows above the neck) for the profile dividers
    "profile_head": (150, 360, 2250, 2050),
    # the hand without the forearm (crop="hand_tight"): palm and fingers only
    "hand_tight": (600, 1100, 1420, 2350),
}

# the visor: VISOR is the bounding box of the band in source pixels (the
# contract); the band itself follows VISOR_CURVE, a polyline of centre points
# (x, y) along the chrome plus a half thickness, because the visor wraps around
# her head and a straight sheared band cannot follow it
VISOR = {"front": (830, 655, 1600, 1080)}
VISOR_CURVE = {"front": ([(830, 975), (900, 925), (1000, 847), (1100, 811), (1200, 786),
                          (1300, 770), (1400, 758), (1500, 758), (1560, 765), (1600, 775)],
                         90)}
VISOR_MIN_RUN = 3     # a band row needs at least this many consecutive cells
# how the band is painted (see levels): "solid" (every cell yellow) or
# "textured" (outline yellow, the chrome's bright stripes yellow, its dark
# stripes dim cyan zeros at VISOR_DARK_LEVEL or above)
VISOR_MODE = {"front": "textured"}
VISOR_DARK_LEVEL = 2        # the dark stripes: at least this level, at most 2
VISOR_STRETCH = (8, 92)     # percentiles of the band's tone mapped to 0..1
VISOR_SPLIT = 0.45          # stretched tone at or above this is yellow
VISOR_JITTER = 0.06

# reconstruction value of each ink level for the dither (what fraction of
# "white" a cell of that level reads as) and the level code it maps to
DITHER_VALUES = np.array([0.0, 0.21, 0.47, 0.76, 1.0])
DITHER_CODES = np.array([0, 1, 2, 3, 5])

# per source tone defaults: black cut on the raw luminance (anything at or
# below it is background), contrast stretch percentiles over the figure cells,
# gamma (below 1 lifts midtones), unsharp mask (radius in rows, amount),
# highlight budget (percent of inked cells allowed at level 5). Optional:
#   dilate      max filter radius in supersample px before the reduce (rim light)
#   knee        (start, slope): values above start are compressed by slope
#   fade_bottom rows at the bottom of the crop that fade to black
#   fill        True: seed the enclosed head interior (profile), see FILL
#   shadow      (radius in rows, strength, reference): shadow equalization, the
#               local mean over the radius is pulled toward the reference with
#               a gain of (reference / mean) ** strength, so the side of a face
#               away from the light keeps its cheek and jaw instead of cutting
#               to a few dim cells
#   shadow_clamp (lo, hi) bounds on that gain; lo 1.0 makes it a pure lift
#   contour     tone value forced (as a floor) on every figure cell that touches
#               the background, so a dark edge (hair, the shadow side of a
#               face) keeps a dim outline instead of vanishing into the ground
#   edge_dissolve  (side, depth, seed): the outermost `depth` columns of the
#               figure on that side of the grid ("left" or "right", after the
#               flip) dissolve in a seeded ragged pattern, so a crop or a
#               straight sleeve does not leave a vertical wall
TONE = {
    # the hair sits just above the background noise (cell means 0.02 against
    # 0.003), so the cut is low and the contour keeps the head's outline
    "glance": dict(black_cut=0.012, contrast=(0.5, 99.5), gamma=0.5,
                   unsharp=(2.5, 1.2), highlight_pct=3.0, fade_bottom=6,
                   contour=0.14, edge_dissolve=("left", 10, 5),
                   face_boost=dict(lift=1.0, hilite_weight=0.15)),
    "profile": dict(black_cut=0.035, contrast=(0.5, 99.0), gamma=0.9,
                    unsharp=(2.0, 0.6), highlight_pct=5.0, dilate=2, fill=True),
    # the shadow side hair sits at 0.03 to 0.06 after the neon suppression,
    # so the cut is low and the hair lift (COLLAR_LIFT) carries it; the
    # shadow pass may compress the lit cheek a little (clamp below 1) and the
    # knee lands the blown cheek just under the level 3 value, so it dithers
    # into a halftone of 1s and 0s instead of blocking up as solid 1s;
    # the bottom rows fade so the collar dissolves into the floor
    "front": dict(black_cut=0.04, contrast=(1.0, 99.0), gamma=0.76,
                  unsharp=(2.5, 0.9), highlight_pct=2.0, knee=(0.62, 0.3),
                  shadow=(6, 0.7, 0.5), shadow_clamp=(0.8, 2.2), fade_bottom=5),
    "hand": dict(black_cut=0.035, contrast=(0.5, 99.5), gamma=0.60,
                 unsharp=(2.5, 1.0), highlight_pct=4.0),
    # tone defaults keyed by a CROPS key take precedence over the source's
    "glance_head": dict(black_cut=0.02, contrast=(0.5, 99.5), gamma=0.38,
                        unsharp=(2.0, 1.0), highlight_pct=4.0),
    "profile_head": dict(black_cut=0.035, contrast=(0.5, 99.0), gamma=0.9,
                         unsharp=(1.5, 0.6), highlight_pct=5.0, dilate=2, fill=True),
    # the hand is low key: a wide stretch and a low gamma push palm and
    # fingers to levels 3 and 5 while the gaps between the fingers stay 0
    "hand_tight": dict(black_cut=0.04, contrast=(2.0, 98.0), gamma=0.5,
                       unsharp=(2.0, 1.2), highlight_pct=6.0),
}

# local boosts in source pixels: (cx, cy, rx, ry) ellipses with a feather
# (fraction of the radius), a multiplier on the tone before the black cut
# (lift), a tight unsharp (radius in rows, amount) applied inside only, and a
# weight that lets those cells win the level 5 budget
FACE_BOOST = {"glance": dict(ellipse=(1700, 1380, 240, 300), feather=0.35, lift=1.3,
                             unsharp=(1.0, 2.0), hilite_weight=0.5),
              # the face under the visor: no lift (the shadow pass does that),
              # a tight unsharp so the nose, lips and chin keep their lines,
              # and a negative highlight weight: the level 5 budget goes to
              # the lit hair and the collar, never to the mouth or the cheek
              # (a run of HILITE cells on the lip line reads as teeth)
              "front": dict(ellipse=(1270, 1250, 340, 340), feather=0.3, lift=1.0,
                            unsharp=(1.0, 1.2), hilite_weight=-0.6)}
# lifts applied before the black cut (one dict or a list per source): the fur
# collar, and the hair on her shadow side, which is nearly black in the
# source and would cut away, leaving the head without a right edge. An
# optional `cap` clips the tone inside the ellipse (before the lift) so the
# backlit strands in that hair do not take the highlight budget
COLLAR_LIFT = {"front": [dict(ellipse=(1270, 1640, 540, 300), feather=0.3, lift=1.4),
                         dict(ellipse=(1700, 1050, 200, 560), feather=0.35, lift=1.5,
                              cap=0.12)]}

# profile interior fill: closing radius in cells (hero / small grids), the
# chin row in source px (rows at or below it are never filled, so the fill
# cannot leak under the jaw), a limiting head ellipse in source px, and the
# seed density of level 1 near the rim (within `near` cells) and deep inside
FILL = {"profile": dict(radius=(3, 2), chin_y=1770, ellipse=(1120, 1120, 880, 780),
                        near=4, p_near=0.42, p_far=0.18, far=12)}

# break up solid level 3 blocks: a level 3 cell whose 8 neighbours are all
# level 3 drops to level 2 with this probability (seeded)
BREAKUP_P = 0.3

# front-visor.jpg neon suppression: saturation knee (S below lo is kept, above
# hi is removed), and soft ellipses (cx, cy, rx, ry) in source pixels
FRONT_SAT_KNEE = (0.55, 0.88)
FRONT_ELLIPSES = ((1255, 990, 470, 690),     # head and hair
                  (1270, 1640, 540, 300),    # the top of the fur collar
                  (1700, 1050, 210, 560))    # the hair on her shadow side
FRONT_FEATHER = 0.18
# the cyan LED light makes her right cheek as saturated as the LEDs themselves,
# so inside this core ellipse (face and visor, where no LED is visible) the
# saturation weight is not applied
FRONT_CORE = (1270, 1000, 380, 440)
# grey opening (min then max filter) in half resolution pixels: the white LED
# dot cores are desaturated, so saturation cannot catch them, but they are
# about 15 px wide while one grid cell covers about 26 x 37 source px, so an
# opening at this size erases the dots and costs the grid nothing it can see
FRONT_OPEN = 21

_CACHE = {}


# ----------------------------------------------------------------------------
# image helpers
# ----------------------------------------------------------------------------

def _smoothstep(lo, hi, x):
    t = np.clip((x - lo) / max(1e-6, hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _source_path(name):
    return os.path.join(ROOT, SOURCES[name])


def _load_gray(name):
    """Luminance in [0, 1] as a float32 array for the whole source photo. The
    front photo also gets its neon suppression here (section 3)."""
    if name in _CACHE:
        return _CACHE[name]
    im = Image.open(_source_path(name)).convert("RGB")
    lum = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    if name == "front":
        hsv = np.asarray(im.convert("HSV"), dtype=np.float32) / 255.0
        sat = hsv[..., 1]
        # v = L * (1 - k * S'), S' a soft knee so skin (S about 0.35) is kept
        # and the LEDs (S above 0.8) go to black
        weight = 1.0 - _smoothstep(FRONT_SAT_KNEE[0], FRONT_SAT_KNEE[1], sat)
        hgt, wid = lum.shape
        yy, xx = np.mgrid[0:hgt, 0:wid].astype(np.float32)
        cx, cy, rx, ry = FRONT_CORE
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        core = np.clip((1.12 - d) / 0.24, 0.0, 1.0)
        weight = np.maximum(weight, core)
        mask = np.zeros_like(lum)
        for cx, cy, rx, ry in FRONT_ELLIPSES:
            d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
            m = np.clip((1.0 + FRONT_FEATHER - d) / (2 * FRONT_FEATHER), 0.0, 1.0)
            mask = np.maximum(mask, m)
        lum = lum * weight * mask
        if FRONT_OPEN > 1:
            half = Image.fromarray((np.clip(lum, 0, 1) * 255).astype(np.uint8))
            half = half.reduce(2)
            opened = half.filter(ImageFilter.MinFilter(FRONT_OPEN)).filter(
                ImageFilter.MaxFilter(FRONT_OPEN))
            opened = np.asarray(opened.resize((lum.shape[1], lum.shape[0]), Image.BILINEAR),
                                dtype=np.float32) / 255.0
            # keep the opened image but let real structure through: nothing
            # brighter than its opened value plus a small margin. The core
            # (face and visor, no LED in it) is left alone: the opening would
            # erase the visor's chrome stripes, which are narrower than it
            opened = np.minimum(lum, opened + 0.03)
            lum = lum * core + opened * (1.0 - core)
    _CACHE[name] = lum.astype(np.float32)
    return _CACHE[name]


def _crop_box(name, crop):
    """crop may be None (the curated crop), a CROPS key or an explicit box."""
    if crop is None:
        return CROPS[name]
    if isinstance(crop, str):
        return CROPS[crop]
    return tuple(crop)


def _tone_key(name, crop):
    return crop if isinstance(crop, str) and crop in TONE else name


def grid_cols(name, rows, cw=4.4, ch=7.0, crop=None):
    """Number of columns the crop needs at `rows` rows with cells cw x ch."""
    x0, y0, x1, y1 = _crop_box(name, crop)
    return max(1, int(round((x1 - x0) / (y1 - y0) * rows * ch / cw)))


def block_size(name, rows, cw=4.4, ch=7.0, crop=None):
    """(width, height) in viewBox px of the glyph block."""
    return grid_cols(name, rows, cw, ch, crop) * cw, rows * ch


def _gauss1d(sigma):
    r = max(1, int(math.ceil(sigma * 3)))
    x = np.arange(-r, r + 1, dtype=np.float64)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    return k / k.sum()


def _blur(v, sigma_y, sigma_x):
    """Separable Gaussian blur with reflect padding."""
    out = v.astype(np.float64)
    for axis, sigma in ((0, sigma_y), (1, sigma_x)):
        if sigma <= 0:
            continue
        k = _gauss1d(sigma)
        r = len(k) // 2
        padded = np.pad(out, [(r, r) if a == axis else (0, 0) for a in range(2)], mode="reflect")
        acc = np.zeros_like(out)
        for i, w in enumerate(k):
            if axis == 0:
                acc += w * padded[i:i + out.shape[0], :]
            else:
                acc += w * padded[:, i:i + out.shape[1]]
        out = acc
    return out


def _maxfilter(a, r):
    """Square max filter of radius r (grey dilation)."""
    if r <= 0:
        return a
    p = np.pad(a, r, mode="edge")
    out = a.copy()
    h, w = a.shape
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            np.maximum(out, p[dy:dy + h, dx:dx + w], out=out)
    return out


def _dilate(m, r):
    """8 neighbour binary dilation by r cells."""
    out = m.copy()
    for _ in range(int(r)):
        p = np.pad(out, 1, mode="constant", constant_values=False)
        out = (p[:-2, :-2] | p[:-2, 1:-1] | p[:-2, 2:] | p[1:-1, :-2] | p[1:-1, 2:]
               | p[2:, :-2] | p[2:, 1:-1] | p[2:, 2:] | out)
    return out


def _neighbours8(m):
    """Count of True 8-neighbours per cell."""
    p = np.pad(m, 1, mode="constant", constant_values=False).astype(int)
    return (p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] + p[1:-1, :-2] + p[1:-1, 2:]
            + p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:])


def _source_coords(geom, rows, flip):
    """Source pixel coordinates (x, y meshgrids) of every cell centre."""
    x0, y0, x1, y1, cols = geom
    cc = (np.arange(cols) + 0.5) * (x1 - x0) / cols
    sx = (x1 - cc) if flip else (x0 + cc)
    sy = y0 + (np.arange(rows) + 0.5) * (y1 - y0) / rows
    return np.meshgrid(sx, sy)


def _ellipse_weight(sxg, syg, ellipse, feather):
    """1 inside the ellipse, feathered to 0 over `feather` of the radius."""
    cx, cy, rx, ry = ellipse
    d = np.sqrt(((sxg - cx) / rx) ** 2 + ((syg - cy) / ry) ** 2)
    return 1.0 - _smoothstep(1.0 - feather, 1.0 + feather, d)


def _fs_dither(v, fg, values, seed=0, serpentine=True, jitter=0.03):
    """Floyd Steinberg error diffusion of v (rows x cols, 0..1) onto the sorted
    palette `values`. Cells outside fg are forced to palette index 0 and their
    error is dropped, so the background stays exactly empty. A tiny seeded
    jitter on the thresholds (plus or minus `jitter` per cell) breaks the worm
    patterns FS makes in flat midtones at 70 to 90 columns without changing
    the tone (the jitter is not part of the propagated error)."""
    rows, cols = v.shape
    buf = v.astype(np.float64).copy()
    idx = np.zeros((rows, cols), dtype=int)
    vals = np.asarray(values, dtype=np.float64)
    mids = (vals[1:] + vals[:-1]) / 2.0
    jit = np.random.RandomState(seed).uniform(-jitter, jitter, (rows, cols))
    for r in range(rows):
        rev = serpentine and (r % 2 == 1)
        cols_iter = range(cols - 1, -1, -1) if rev else range(cols)
        step = -1 if rev else 1
        for c in cols_iter:
            if not fg[r, c]:
                idx[r, c] = 0
                continue
            old = buf[r, c]
            q = int(np.searchsorted(mids, old + jit[r, c]))
            idx[r, c] = q
            err = old - vals[q]
            # 7/16 ahead, 3/16 behind-below, 5/16 below, 1/16 ahead-below
            c1 = c + step
            if 0 <= c1 < cols:
                buf[r, c1] += err * (7.0 / 16.0)
            if r + 1 < rows:
                c2 = c - step
                if 0 <= c2 < cols:
                    buf[r + 1, c2] += err * (3.0 / 16.0)
                buf[r + 1, c] += err * (5.0 / 16.0)
                if 0 <= c1 < cols:
                    buf[r + 1, c1] += err * (1.0 / 16.0)
    return idx


_BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def _bayer_dither(v, fg, values):
    rows, cols = v.shape
    vals = np.asarray(values, dtype=np.float64)
    thr = np.tile(_BAYER4, (rows // 4 + 1, cols // 4 + 1))[:rows, :cols]
    n = len(vals) - 1
    scaled = v * n + (thr - 0.5)
    idx = np.clip(np.round(scaled), 0, n).astype(int)
    idx[~fg] = 0
    return idx


def _nearest(v, fg, values):
    vals = np.asarray(values, dtype=np.float64)
    mids = (vals[1:] + vals[:-1]) / 2.0
    idx = np.searchsorted(mids, v)
    idx[~fg] = 0
    return idx


# ----------------------------------------------------------------------------
# the profile interior
# ----------------------------------------------------------------------------

def _enclosed(fg, radius, allowed):
    """Cells enclosed by the figure: close fg by `radius`, flood the free cells
    from the frame border and from every cell outside `allowed`, and what is
    neither reached nor figure is a hole. The holes are grown back by the
    radius so they meet the figure, and clipped to `allowed`."""
    closed = _dilate(fg, radius)
    free = ~closed
    outside = free & ~allowed
    outside[0, :] |= free[0, :]
    outside[-1, :] |= free[-1, :]
    outside[:, 0] |= free[:, 0]
    outside[:, -1] |= free[:, -1]
    while True:
        grown = _dilate(outside, 1) & free
        if np.array_equal(grown, outside):
            break
        outside = grown
    holes = free & ~outside
    holes = _dilate(holes, radius) & ~fg & allowed
    return holes


def _rim_distance(fg, holes, cap):
    """Dilation distance (cells) from the figure for every hole cell."""
    dist = np.full(fg.shape, cap, dtype=int)
    reach = fg.copy()
    for d in range(1, cap + 1):
        reach = _dilate(reach, 1)
        dist[holes & reach & (dist == cap)] = d
    return dist


def _fill_interior(v, fg, geom, rows, flip, name):
    """Seed the enclosed interior with a sparse level 1 field: the fill value
    is the level 1 reconstruction value times a density that is p_near within
    `near` cells of the rim and falls to p_far at `far` cells, so the dither
    scatters 0 and 1 at that density (a lit volume, not a flat slab)."""
    f = FILL[name]
    radius = f["radius"][0] if rows >= 40 else f["radius"][1]
    sxg, syg = _source_coords(geom, rows, flip)
    allowed = syg < f["chin_y"]
    cx, cy, rx, ry = f["ellipse"]
    allowed &= (((sxg - cx) / rx) ** 2 + ((syg - cy) / ry) ** 2) < 1.0
    holes = _enclosed(fg, radius, allowed)
    if not holes.any():
        return v, fg, holes
    dist = _rim_distance(fg, holes, f["far"])
    t = np.clip((dist - f["near"]) / max(1, f["far"] - f["near"]), 0.0, 1.0)
    p = f["p_near"] + (f["p_far"] - f["p_near"]) * t
    fill = DITHER_VALUES[1] * p
    v = np.where(holes, np.maximum(v, fill), v)
    return v, fg | holes, holes


# ----------------------------------------------------------------------------
# the contract
# ----------------------------------------------------------------------------

def tone(name, rows, cw=4.4, ch=7.0, flip=False, gamma=None, contrast=None,
         black_cut=None, crop=None, unsharp=None):
    """The continuous tone map before quantization: (v, fg, geometry) where v is
    rows x cols in 0..1, fg marks figure cells (the background is False and
    exactly 0) and geometry is (x0, y0, x1, y1, cols) for the source mapping."""
    v, fg, geom, _ = _tone_full(name, rows, cw, ch, flip, gamma, contrast, black_cut,
                                crop, unsharp)
    return v, fg, geom


def _tone_full(name, rows, cw, ch, flip, gamma, contrast, black_cut, crop, unsharp):
    """tone() plus a dict with the hilite weight map and the hole mask."""
    t = dict(TONE[_tone_key(name, crop)])
    if gamma is not None:
        t["gamma"] = gamma
    if contrast is not None:
        t["contrast"] = contrast
    if black_cut is not None:
        t["black_cut"] = black_cut
    if unsharp is not None:
        t["unsharp"] = unsharp

    x0, y0, x1, y1 = _crop_box(name, crop)
    src = _load_gray(name)[y0:y1, x0:x1]
    if flip:
        src = src[:, ::-1]
    cols = grid_cols(name, rows, cw, ch, (x0, y0, x1, y1))
    geom = (x0, y0, x1, y1, cols)
    sxg, syg = _source_coords(geom, rows, flip)
    extra = {"hilite_w": np.zeros((rows, cols)), "holes": np.zeros((rows, cols), dtype=bool)}

    # resample: LANCZOS onto a 4x supersampled grid, then a 4x4 box reduce.
    # A rim light one or two source px wide is thickened first so it survives
    # the reduce as a two cell line
    im = Image.fromarray(np.ascontiguousarray(src), mode="F")
    ss = np.asarray(im.resize((cols * 4, rows * 4), Image.LANCZOS), dtype=np.float64)
    if t.get("dilate"):
        ss = _maxfilter(ss, int(t["dilate"]))
    v = ss.reshape(rows, 4, cols, 4).mean(axis=(1, 3))
    v = np.clip(v, 0.0, 1.0)

    # local lifts before the cut (the fur collar and the shadow side hair are
    # dim and would cut to specks); one dict or a list of them per source
    if name in COLLAR_LIFT:
        lifts = COLLAR_LIFT[name]
        if isinstance(lifts, dict):
            lifts = [lifts]
        for c in lifts:
            w = _ellipse_weight(sxg, syg, c["ellipse"], c["feather"])
            if c.get("cap") is not None:
                v = v + (np.minimum(v, float(c["cap"])) - v) * w
            v = np.clip(v * (1.0 + (c["lift"] - 1.0) * w), 0.0, 1.0)

    # black cut: the background is exactly 0 and never receives dither error
    cut = float(t["black_cut"])
    v = np.clip((v - cut) / max(1e-6, 1.0 - cut), 0.0, 1.0)
    fg = v > 0.0
    # isolated specks (fewer than two inked 8-neighbours) are background
    fg &= _neighbours8(fg) >= 2
    v[~fg] = 0.0
    if not fg.any():
        return v, fg, geom, extra

    # contrast stretch over the figure cells
    lo_p, hi_p = t["contrast"]
    lo, hi = np.percentile(v[fg], [lo_p, hi_p])
    if hi - lo > 1e-6:
        v = np.clip((v - lo) / (hi - lo), 0.0, 1.0)
    v[~fg] = 0.0

    # shadow equalization: the local mean over a wide window (radius in rows)
    # is pulled toward a reference, so a face lit hard from one side keeps
    # its shadow side (the gain is clamped so the lift stays a lift, not a
    # flattening: the lit side is compressed by at most 1/lo)
    if t.get("shadow"):
        sr, sk, sref = t["shadow"]
        sig_x = sr * ch / cw
        base = _blur(v, sr, sig_x)
        wgt = _blur(fg.astype(np.float64), sr, sig_x)
        base = base / np.maximum(wgt, 0.05)
        gain = np.power(float(sref) / np.maximum(base, 0.04), float(sk))
        lo, hi = t.get("shadow_clamp", (0.7, 3.0))
        v = np.clip(v * np.clip(gain, lo, hi), 0.0, 1.0)
        v[~fg] = 0.0

    # gamma (below 1 lifts the midtones)
    g = float(t["gamma"])
    if g and abs(g - 1.0) > 1e-6:
        v = np.power(v, g)

    # highlight knee: blown out areas compress so they dither into texture
    if t.get("knee"):
        k0, slope = t["knee"]
        v = np.where(v > k0, k0 + (v - k0) * slope, v)

    # local contrast: unsharp mask, radius in rows (isotropic in viewBox px)
    radius, amount = t["unsharp"]
    if radius > 0 and amount > 0:
        blurred = _blur(v, radius, radius * ch / cw)
        v = np.clip(v + amount * (v - blurred), 0.0, 1.0)
        v[~fg] = 0.0

    # face boost: lift and a tight unsharp inside the ellipse only (a TONE
    # entry can switch it off with face_boost=False, or override fields of
    # the FACE_BOOST entry with a dict)
    if name in FACE_BOOST and t.get("face_boost", True):
        fb = dict(FACE_BOOST[name])
        if isinstance(t.get("face_boost"), dict):
            fb.update(t["face_boost"])
        w = _ellipse_weight(sxg, syg, fb["ellipse"], fb["feather"])
        r2, a2 = fb["unsharp"]
        sharp = np.clip(v + a2 * (v - _blur(v, r2, r2 * ch / cw)), 0.0, 1.0)
        lifted = np.clip(sharp * fb["lift"], 0.0, 1.0)
        v = v + (lifted - v) * w
        v[~fg] = 0.0
        extra["hilite_w"] = w * fb["hilite_weight"]

    # the bottom rows fade so a figure cut by the crop dissolves into the floor
    n_fade = int(t.get("fade_bottom", 0))
    if n_fade > 0 and rows > n_fade:
        ramp = np.ones(rows)
        ramp[rows - n_fade:] = np.linspace(1.0, 0.0, n_fade + 1)[:-1] ** 1.5
        v = v * ramp[:, None]
        fg &= v > 0.0
        v[~fg] = 0.0

    # a dim outline where the figure meets the ground (the hair and the
    # shadow side of the face would otherwise fall to level 0 at the edge)
    if t.get("contour"):
        edge = fg & (_neighbours8(fg) < 8)
        v = np.where(edge, np.maximum(v, float(t["contour"])), v)

    # a ragged dissolve of the outermost columns on one side
    if t.get("edge_dissolve"):
        v, fg = _edge_dissolve(v, fg, *t["edge_dissolve"])

    # the enclosed interior of a rim lit head
    if t.get("fill") and name in FILL:
        v, fg, holes = _fill_interior(v, fg, geom, rows, flip, name)
        extra["holes"] = holes
    return v, fg, geom, extra


def _edge_dissolve(v, fg, side, depth, seed):
    """The outermost `depth` columns of the figure on `side` ("left" or
    "right") dissolve: per row, a seeded cut (smoothed over rows so the edge
    waves instead of jittering) removes up to 60% of the depth outright and
    the next cells ramp up from 0, so the dither scatters them into a ragged
    fringe. Returns (v, fg)."""
    rows, cols = v.shape
    rng = np.random.RandomState(seed + 7)
    noise = _blur(rng.random_sample(rows)[:, None], 2.0, 0.0)[:, 0]
    lo, hi = noise.min(), noise.max()
    noise = (noise - lo) / max(1e-6, hi - lo)
    jit = rng.random_sample((rows, cols)) * 0.5
    out = v.copy()
    for r in range(rows):
        inked = np.nonzero(fg[r])[0]
        if len(inked) == 0:
            continue
        cut = int(round(depth * 0.6 * noise[r]))
        ramp = max(1, depth - cut)
        if side == "left":
            c0 = int(inked[0])
            d = np.arange(cols) - c0
        else:
            c0 = int(inked[-1])
            d = c0 - np.arange(cols)
        f = np.clip((d - cut + jit[r]) / ramp, 0.0, 1.0)
        f[d < 0] = 1.0
        f[d < cut] = 0.0
        out[r] *= f
    fg = fg & (out > 0.0)
    out[~fg] = 0.0
    return out, fg


def _visor_band(geom, rows, flip, name):
    """Boolean mask of the visor band cells on the grid."""
    sxg, syg = _source_coords(geom, rows, flip)
    vx0, vy0, vx1, vy1 = VISOR[name]
    inside = (sxg >= vx0) & (sxg < vx1) & (syg >= vy0) & (syg < vy1)
    if name in VISOR_CURVE:
        pts, half = VISOR_CURVE[name]
        xs = np.array([p[0] for p in pts], dtype=float)
        ys = np.array([p[1] for p in pts], dtype=float)
        centre = np.interp(sxg, xs, ys)
        band = inside & (np.abs(syg - centre) <= half)
    else:
        band = inside
    # no stray lead ins: a band row needs VISOR_MIN_RUN consecutive cells
    for r in range(rows):
        row = band[r]
        if not row.any():
            continue
        c = 0
        cols = len(row)
        while c < cols:
            if row[c]:
                c2 = c
                while c2 < cols and row[c2]:
                    c2 += 1
                if c2 - c < VISOR_MIN_RUN:
                    row[c:c2] = False
                c = c2
            else:
                c += 1
    return band


def _visor_texture(lv, v, band, seed):
    """The chrome visor as a mirrored strip instead of a solid block: the
    band's top and bottom edges are solid yellow (the strip's silhouette) and
    inside it the tone is stretched over the band's own range and cut at
    VISOR_SPLIT, so the bright reflections turn yellow and the dark stripes
    between them stay dim cyan zeros (the cell's own level, raised to
    VISOR_DARK_LEVEL and capped at 2). A seeded jitter on the cut keeps the
    stripe edges from quantizing into straight columns."""
    rows, cols = band.shape
    above = np.zeros_like(band)
    below = np.zeros_like(band)
    above[1:] = band[:-1]
    below[:-1] = band[1:]
    edge = band & ~(above & below)
    bv = v[band]
    lo, hi = np.percentile(bv, VISOR_STRETCH)
    stretched = np.clip((v - lo) / max(1e-6, hi - lo), 0.0, 1.0)
    jit = np.random.RandomState(seed + 211).uniform(-VISOR_JITTER, VISOR_JITTER, (rows, cols))
    bright = band & (stretched + jit >= VISOR_SPLIT)
    out = np.where(edge | bright, 4, lv)
    dark = band & ~edge & ~bright
    out = np.where(dark, np.minimum(np.maximum(out, VISOR_DARK_LEVEL), 2), out)
    return out


def _strokes(lv, v, cap):
    """Lone level 5 cells become short horizontal strokes: a level 5 cell with
    no level 5 row neighbour promotes its brighter neighbour when that one is
    bright enough (so the pair reads as a specular stroke), else drops to 3.
    The total stays within 1.3 x cap."""
    rows, cols = lv.shape
    budget = int(round(cap * 1.3))
    hi = np.argwhere(lv == 5)
    for r, c in hi:
        if lv[r, c] != 5:
            continue
        left = lv[r, c - 1] == 5 if c > 0 else False
        right = lv[r, c + 1] == 5 if c + 1 < cols else False
        if left or right:
            continue
        cands = []
        if c > 0 and lv[r, c - 1] in (2, 3):
            cands.append((v[r, c - 1], c - 1))
        if c + 1 < cols and lv[r, c + 1] in (2, 3):
            cands.append((v[r, c + 1], c + 1))
        if cands and int((lv == 5).sum()) < budget:
            bv, bc = max(cands)
            if bv > 0.55:
                lv[r, bc] = 5
                continue
        lv[r, c] = 3
    return lv


def _breakup(lv, seed):
    """Solid level 3 blocks: a level 3 cell whose 8 neighbours are all level 3
    drops to level 2 with probability BREAKUP_P (seeded)."""
    is3 = lv == 3
    solid = is3 & (_neighbours8(is3) == 8)
    if not solid.any():
        return lv
    rng = np.random.RandomState(seed + 101)
    drop = solid & (rng.random_sample(lv.shape) < BREAKUP_P)
    return np.where(drop, 2, lv)


def levels(name, rows, cw=4.4, ch=7.0, flip=False, gamma=None, contrast=None,
           black_cut=None, dither="fs", highlight_pct=None, crop=None, visor=True,
           unsharp=None, seed=0):
    """int array (rows x cols), values in {0,1,2,3,4,5}; cols derived from the
    crop aspect and the cell aspect. Per-source defaults for gamma, contrast,
    black_cut, unsharp and highlight_pct live in TONE (a CROPS key with its own
    TONE entry wins over the source's); explicit arguments override them.
    dither is "fs" (Floyd Steinberg, the default), "bayer" or "none"."""
    if highlight_pct is None:
        highlight_pct = TONE[_tone_key(name, crop)].get("highlight_pct", 4.0)
    v, fg, geom, extra = _tone_full(name, rows, cw, ch, flip, gamma, contrast, black_cut,
                                    crop, unsharp)
    x0, y0, x1, y1, cols = geom
    if not fg.any():
        return np.zeros((rows, cols), dtype=int)

    # quantize
    if dither == "fs":
        idx = _fs_dither(v, fg, DITHER_VALUES, seed=seed)
    elif dither == "bayer":
        idx = _bayer_dither(v, fg, DITHER_VALUES)
    else:
        idx = _nearest(v, fg, DITHER_VALUES)
    lv = DITHER_CODES[idx]

    # highlight budget: level 5 is the brightest highlight_pct of inked cells;
    # the face weight lets her features win the budget over the sleeves
    inked = int((lv > 0).sum())
    cap = int(round(inked * float(highlight_pct) / 100.0))
    score = v * (1.0 + extra["hilite_w"])
    hi_cells = np.argwhere(lv == 5)
    if len(hi_cells) > cap:
        order = np.argsort(score[hi_cells[:, 0], hi_cells[:, 1]])
        for i in order[: len(hi_cells) - cap]:
            r, c = hi_cells[i]
            lv[r, c] = 3
    lv = _strokes(lv, v, cap)
    lv = _breakup(lv, seed)

    # the visor band: "solid" paints every band cell yellow; "textured" keeps
    # the chrome's own stripes: the band's outline is solid yellow, inside it
    # the cells the dither put at level 3 or 5 turn yellow and the darker
    # cells stay dim cyan zeros, so the mirrored stripes survive
    if visor and name in VISOR:
        band = _visor_band(geom, rows, flip, name)
        mode = VISOR_MODE.get(name, "solid")
        if mode == "textured" and band.any():
            lv = _visor_texture(lv, v, band, seed)
        else:
            lv = np.where(band, 4, lv)
        fg = fg | band
    lv = lv.astype(int)
    assert not (lv[~fg] != 0).any(), "ink outside the figure mask"
    return lv


def recolor(fragment, fill):
    """Replace every fill colour in an SVG fragment (used for chromatic copies)."""
    return re.sub(r'fill="#[0-9a-fA-F]{6}"', f'fill="{fill}"', fragment)


def glyph_block(tl, name, x, y, rows, cw=4.4, ch=7.0, anims="", **kw):
    """lib.glyph_rows of levels(...), positioned at x,y. Returns an SVG fragment.
    Keyword arguments for glyph_rows (flat, min_level, size, max_width) and a
    `fill` override are split off; the rest go to levels()."""
    rk = {k: kw.pop(k) for k in ("flat", "min_level", "size", "max_width") if k in kw}
    fill = kw.pop("fill", None)
    lv = levels(name, rows, cw, ch, **kw)
    frag = glyph_rows(lv, x, y, cw, ch, anims=anims, **rk)
    return recolor(frag, fill) if fill else frag


# ----------------------------------------------------------------------------
# animation helpers (all through lib.Timeline)
# ----------------------------------------------------------------------------

def dissolve(lv, seed, steps, top_last=True):
    """`steps` frames: frame 0 is the full grid, the last is empty. Cells drop
    in seeded random order biased so the top rows go last (or first)."""
    lv = np.asarray(lv)
    rows, cols = lv.shape
    rng = np.random.RandomState(seed)
    rnd = rng.random_sample((rows, cols))
    rr = (np.arange(rows)[:, None] + 0.5) / rows
    bias = (1.0 - rr) if top_last else rr
    key = 0.55 * bias + 0.45 * rnd
    frames = []
    for i in range(steps):
        frac = i / max(1, steps - 1)
        frames.append(np.where(key < frac, 0, lv).astype(int))
    return frames


def _loop_splines(t0, spline):
    """keySplines for a track that starts at t0: a repeating track gets a lead
    hold segment from 0 to t0 (lib inserts it), which takes splines index 0."""
    return [(0, 0, 1, 1), spline] if t0 > 1e-9 else [spline]


def dissolve_anim(tl, lv, x, y, cw, ch, t0, dur, seed, steps=8, top_last=True,
                  fall=70, fall_dur=0.45, appear=0.0, repeat=False, trail=0,
                  trail_rows=2.0, trail_opacity=(0.4, 0.18, 0.08), **rk):
    """Animated dissolve: the grid is split into `steps` seeded groups of cells
    (dissolve()); group i drops at t0 + dur * i / (steps - 1), falling `fall`
    px and fading over fall_dur (a rain of digits off the figure). Before t0
    the groups together are the full grid, visible from `appear`. Extra
    keyword arguments go to glyph_rows. Cost: about steps x rows x levels
    <text> elements. repeat=True makes the fall and fade tracks loop with the
    scene (a once-only track freezes at its end, so a looping scene would show
    the dissolve on the first pass only).

    trail > 0 gives every falling group that many dim copies of itself
    trail_rows rows apart above it (opacities from trail_opacity), so the
    fall draws a vertical streak instead of a loose scatter. The copies come
    from a <filter> per group (feOffset and feMerge), so they cost no <text>
    elements; the copies' alpha (the feFuncA slope) is held at 0 until the
    group's own drop time, so a group that is still standing is drawn exactly
    as the plain grid and the trail only appears once it falls. A frozen
    frame renders the slope at that time the same way."""
    lv = np.asarray(lv)
    rows, cols = lv.shape
    frames = dissolve(lv, seed, steps + 1, top_last=top_last)
    out = []
    up = trail * trail_rows * ch

    def trail_filter(ti):
        fid = uid("trail")
        nodes = []
        merge = []
        for k in range(1, trail + 1):
            op = trail_opacity[min(k - 1, len(trail_opacity) - 1)]
            sf, sa = tl.attr("slope", [(0.0, 0.0), (ti, op)], calc="discrete", repeat=repeat)
            nodes.append(f'<feOffset in="SourceGraphic" dy="{fmt(-k * trail_rows * ch)}" '
                         f'result="o{k}"/><feComponentTransfer in="o{k}" result="t{k}">'
                         f'<feFuncA type="linear"{sf}>{sa}</feFuncA></feComponentTransfer>')
            merge.append(f'<feMergeNode in="t{k}"/>')
        merge.reverse()
        return fid, (f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="{fmt(x - 40)}" '
                     f'y="{fmt(y - up - 10)}" width="{fmt(cols * cw + 80)}" '
                     f'height="{fmt(rows * ch + up + fall + 20)}" '
                     f'color-interpolation-filters="sRGB">{"".join(nodes)}'
                     f'<feMerge>{"".join(merge)}<feMergeNode in="SourceGraphic"/></feMerge>'
                     f'</filter>')

    for i in range(1, steps + 1):
        gone = (frames[i - 1] > 0) & (frames[i] == 0)
        if not gone.any():
            continue
        part = np.where(gone, lv, 0)
        ti = t0 + dur * (i - 1) / max(1, steps - 1)
        te = min(tl.dur, ti + fall_dur)
        of, oa = tl.attr("opacity", [(ti, 1.0), (te, 0.0)], repeat=repeat)
        filt = ""
        if trail > 0:
            fid, fdef = trail_filter(ti)
            out.append(fdef)
            filt = f' filter="url(#{fid})"'
        body = f"<g{of}{filt}>{glyph_rows(part, x, y, cw, ch, **rk)}{oa}</g>"
        sp = _loop_splines(ti, (0.4, 0, 1, 0.6)) if repeat else [(0.4, 0, 1, 0.6)]
        out.append(moving_group(tl, body, translate=[(ti, (0, 0)), (te, (0, fall))],
                                spans=[(appear, te)], repeat=repeat, calc="spline",
                                splines=sp))
    return "".join(out)


def knockout(lv, x, y, cw, ch, grow=2, fill=BG, opacity=1.0, min_ink=0):
    """A ground coloured silhouette behind a figure, grown by `grow` cells, so
    a figure drawn in front of another (the hand in front of her) separates
    instead of merging into one cyan mass. One <path> element: every row of
    the grown mask becomes a run of rectangles (subpaths). Rows with fewer
    than `min_ink` inked cells are left out (a sparse top row would otherwise
    show as a dark step above the figure)."""
    lv = np.asarray(lv)
    ink = lv > 0
    if min_ink > 0:
        ink = ink & ((ink.sum(axis=1) >= min_ink)[:, None])
    m = _dilate(ink, grow)
    parts = []
    for r in range(m.shape[0]):
        row = m[r]
        c = 0
        n = len(row)
        while c < n:
            if row[c]:
                c2 = c
                while c2 < n and row[c2]:
                    c2 += 1
                parts.append(f"M{fmt(x + c * cw)} {fmt(y + r * ch)}h{fmt((c2 - c) * cw)}"
                             f"v{fmt(ch)}h{fmt(-(c2 - c) * cw)}z")
                c = c2
            else:
                c += 1
    if not parts:
        return ""
    op = "" if opacity >= 1.0 else f' fill-opacity="{fmt(opacity)}"'
    return f'<path d="{"".join(parts)}" fill="{fill}"{op}/>'


def silhouette_edges(lv):
    """(row, left col, right col) for every row that has ink."""
    out = []
    for r in range(lv.shape[0]):
        cols = np.nonzero(lv[r] > 0)[0]
        if len(cols):
            out.append((r, int(cols[0]), int(cols[-1])))
    return out


def streaks(tl, lv, x, y, cw, ch, burst_times, seed, n=10, length=(40, 160), repeat=False,
            travel=(60, 200), fade=0.5, sides=(-1, 1), x_range=None):
    """Data streaks: horizontal runs of digits that leave the silhouette's
    left/right edge cells at each burst time, travel outward `travel` px (a
    (min, max) range, 60 to 200 by default) and fade over `fade` s (0.5).
    `sides` restricts the edges they leave from (-1 left, +1 right); the
    section dividers use it to fire every streak across the strip toward the
    title. x_range (x_min, x_max), if given, caps the travel so no run leaves
    that zone (a scene with text columns beside the figure). repeat=True makes
    the tracks loop with the scene (see dissolve_anim)."""
    rng = random.Random(seed)
    edges = silhouette_edges(np.asarray(lv))
    if not edges:
        return ""
    out = []
    for t0 in burst_times:
        t0 = float(t0)
        if t0 >= tl.dur:
            continue
        t1 = min(tl.dur, t0 + fade)
        for _ in range(n):
            r, c_left, c_right = rng.choice(edges)
            side = rng.choice(tuple(sides))
            px_len = rng.uniform(length[0], length[1])
            n_ch = max(2, int(px_len / cw))
            s = "".join(rng.choice("0011") for _ in range(n_ch))
            travel_px = rng.uniform(travel[0], travel[1]) * side
            by = y + r * ch + ch * 0.8
            if side > 0:
                bx = x + (c_right + 1) * cw
            else:
                bx = x + c_left * cw - n_ch * cw
            if x_range is not None:
                # the run's far end must stay inside the zone; a run that has
                # no room left is shortened first, then its travel is capped
                lo, hi = x_range
                if side > 0:
                    room = hi - bx
                    n_ch = max(2, min(n_ch, int(room / cw)))
                    travel_px = max(0.0, min(travel_px, room - n_ch * cw))
                else:
                    room = (x + c_left * cw) - lo
                    n_ch = max(2, min(n_ch, int(room / cw)))
                    bx = x + c_left * cw - n_ch * cw
                    travel_px = min(0.0, max(travel_px, -(bx - lo)))
                s = s[:n_ch]
            fill = CYAN if rng.random() < 0.75 else CYAN_DIM
            txt = (f'<text x="{fmt(bx)}" y="{fmt(by)}" font-size="{fmt(ch)}" fill="{fill}" '
                   f'textLength="{fmt(n_ch * cw)}" lengthAdjust="spacingAndGlyphs" '
                   f'xml:space="preserve">{s}</text>')
            of, oa = tl.attr("fill-opacity", [(t0, 0.95), (t1, 0.0)], repeat=repeat)
            sp = _loop_splines(t0, (0.1, 0.6, 0.4, 1)) if repeat else [(0.1, 0.6, 0.4, 1)]
            out.append(moving_group(tl, f"<g{of}>{txt}{oa}</g>",
                                    translate=[(t0, (0, 0)), (t1, (travel_px, 0))],
                                    spans=[(t0, t1)], repeat=repeat, calc="spline",
                                    splines=sp))
    return "".join(out)


def ghost_entrance(tl, block_fn, t0, dur, dx_from, ghost_fn=None, repeat=False):
    """Trailing copies on entrance: three ghosts at dx +18, +36, +54 (opacities
    0.35, 0.2, 0.1) slide in from dx_from a beat behind the figure and fade out
    once it has settled; the figure itself slides in last, on top. ghost_fn
    (defaults to block_fn) builds the ghost copies: pass a cheaper flat
    rendering of the same grid to keep the element count down. repeat=True
    makes the slide and fade tracks loop with the scene (see dissolve_anim)."""
    t0 = float(t0)
    ghost_fn = ghost_fn or block_fn
    ease = (0.2, 0.7, 0.3, 1)
    out = []
    for i, (dx, op) in enumerate(((54, 0.1), (36, 0.2), (18, 0.35))):
        lag = 0.08 * (3 - i)
        a = t0 + lag
        b = a + dur
        of, oa = tl.attr("opacity", [(a, op), (b, op), (b + 0.35, 0.0)], repeat=repeat)
        sp = _loop_splines(a, ease) if repeat else [ease]
        out.append(moving_group(tl, f"<g{of}>{ghost_fn()}{oa}</g>",
                                translate=[(a, (dx_from, 0)), (b, (dx, 0))],
                                spans=[(a, b + 0.35)], repeat=repeat, calc="spline",
                                splines=sp))
    sp = _loop_splines(t0, ease) if repeat else [ease]
    out.append(moving_group(tl, block_fn(),
                            translate=[(t0, (dx_from, 0)), (t0 + dur, (0, 0))],
                            spans=[(t0, tl.dur)], repeat=repeat, calc="spline",
                            splines=sp))
    return "".join(out)


def slice_glitch(tl, children, x, y, w, h, times, seed, glitch_fn=None):
    """Wrap children in 3 to 5 horizontal clip bands; at each time the bands
    shift by 10 to 24 px for 160 ms (discrete). The band copies cost n_bands
    times the children, so glitch_fn (a fragment builder) can supply a cheaper
    copy that is shown only during the glitch windows while the plain children
    show the rest of the time."""
    rng = random.Random(seed)
    n_bands = rng.randint(3, 5)
    cuts = sorted(rng.uniform(0.1, 0.9) for _ in range(n_bands - 1))
    bounds = [0.0] + cuts + [1.0]
    windows = [(float(t), min(tl.dur, float(t) + 0.16)) for t in times if float(t) < tl.dur]
    out = []
    if glitch_fn is not None:
        # the plain copy hides during the glitch windows
        rest = [(0.0, tl.dur)]
        for a, b in windows:
            nxt = []
            for p, q in rest:
                if b <= p or a >= q:
                    nxt.append((p, q))
                else:
                    if a > p:
                        nxt.append((p, a))
                    if b < q:
                        nxt.append((b, q))
            rest = nxt
        vf, va = tl.visible(rest)
        out.append(f"<g{vf}>{children}{va}</g>")
        sliced = glitch_fn()
    else:
        sliced = children
    for i in range(n_bands):
        by0 = y + h * bounds[i]
        by1 = y + h * bounds[i + 1]
        cid = uid("slc")
        kfs = [(0.0, (0, 0))]
        for a, b in windows:
            dx = rng.uniform(10, 24) * rng.choice((-1, 1))
            kfs.append((a, (dx, 0)))
            kfs.append((b, (0, 0)))
        tf, ta = tl.transform(kfs, kind="translate", calc="discrete")
        vf, va = tl.visible(windows) if glitch_fn is not None else ("", "")
        out.append(f'<clipPath id="{cid}"><rect x="{fmt(x - 60)}" y="{fmt(by0)}" '
                   f'width="{fmt(w + 120)}" height="{fmt(by1 - by0)}"/></clipPath>'
                   f'<g clip-path="url(#{cid})"{vf}><g{tf}>{sliced}{ta}</g>{va}</g>')
    return "".join(out)


def chromatic(tl, children_fn, times):
    """children_fn(fill_override) -> fragment; emits MAGENTA and CYAN copies
    offset at the given times plus the normal copy on top. The copies are only
    visible during the 160 ms bursts."""
    out = []
    spans = []
    for t in times:
        t = float(t)
        if t < tl.dur:
            spans.append((t, min(tl.dur, t + 0.16)))
    for fill, sign in ((MAGENTA, -1), (CYAN, 1)):
        kfs = [(0.0, (0, 0))]
        for t in times:
            t = float(t)
            if t >= tl.dur:
                continue
            for dt, d in ((0.0, 4), (0.05, -3), (0.1, 3), (0.16, 0)):
                if t + dt < tl.dur:
                    kfs.append((t + dt, (sign * d, 0)))
        out.append(moving_group(tl, f'<g opacity="0.85">{children_fn(fill)}</g>',
                                translate=kfs, spans=spans, calc="discrete"))
    out.append(children_fn(None))
    return "".join(out)


def row_texts(row, x, y, cw, ch, flat=False, min_level=1):
    """One row of a glyph grid as bare <text> elements (one per ink level
    present, fill and opacity inline, no wrapper groups), for helpers that
    wrap every row in its own animated group. Same look as lib.glyph_rows."""
    row = np.clip(np.asarray(row).astype(int), 0, lib.MAX_LEVEL)
    if flat:
        min_level = max(min_level, 2)
    if min_level > 1:
        row = np.where(row < min_level, 0, row)
    if flat:
        classes = ((3, (row >= 1) & (row <= 3)), (4, row == 4), (5, row == 5))
    else:
        classes = tuple((level, row == level) for level in (1, 2, 3, 4, 5))
    by = y + ch * 0.8
    out = []
    for level, mask in classes:
        if not mask.any():
            continue
        chars = np.where(mask, lib._LEVEL_LUT[row], " ")
        s = "".join(chars.tolist()).rstrip()
        lead = len(s) - len(s.lstrip())
        s = s[lead:]
        out.append(f'<text x="{fmt(x + lead * cw)}" y="{fmt(by)}" '
                   f'textLength="{fmt(len(s) * cw)}" lengthAdjust="spacingAndGlyphs" '
                   f'fill="{lib.LEVEL_FILL[level]}" fill-opacity="{fmt(lib.LEVEL_OPACITY[level])}" '
                   f'font-size="{fmt(ch)}" xml:space="preserve">{s}</text>')
    return "".join(out)


def materialize(tl, lv, x, y, cw, ch, t0, dur, seed, flicker=3, hold_until=None, **rk):
    """Rows appear in seeded random order between t0 and t0+dur (row visibility
    spans); a few rows flicker once as they land. hold_until ends the
    visibility (default: the loop end). Extra keyword arguments go to
    row_texts (flat, min_level). Cost: one <g> plus one <text> per ink level
    per row (about 5 elements a row)."""
    lv = np.asarray(lv)
    rows = lv.shape[0]
    rng = random.Random(seed)
    order = list(range(rows))
    rng.shuffle(order)
    flick = set(rng.sample(order, min(flicker, rows)))
    end = tl.dur if hold_until is None else float(hold_until)
    out = []
    for k, r in enumerate(order):
        if not (lv[r] > 0).any():
            continue
        t = t0 + dur * k / max(1, rows - 1)
        if r in flick and t + 0.12 < end:
            spans = [(t, t + 0.05), (t + 0.11, end)]
        else:
            spans = [(t, end)]
        vf, va = tl.visible(spans)
        out.append(f"<g{vf}>{row_texts(lv[r], x, y + r * ch, cw, ch, **rk)}{va}</g>")
    return f"<g>{''.join(out)}</g>"


# ----------------------------------------------------------------------------
# review artifacts
# ----------------------------------------------------------------------------

HERO_SPECS = (("glance", 74, True, None), ("profile", 60, False, None),
              ("front", 43, False, None), ("hand", 37, False, None))
DIVIDER_SPECS = (("glance", 21, True, "glance_head"), ("profile", 21, False, "profile_head"),
                 ("front", 21, False, None), ("hand", 21, True, None))


def _render_svg(lv, cw, ch, title, path, px_max=1200, pad=2):
    """Write a real SVG of the grid. The canvas is square with the figure
    centred, because qlmanage fits the document WIDTH to -s and clips a tall
    document at the bottom. Returns (x0, y0, x1, y1) of the figure as fractions
    of the canvas so a sheet can crop the thumbnail back to the figure."""
    rows, cols = lv.shape
    gw = cols * cw + 2 * pad
    gh = rows * ch + 2 * pad
    side = max(gw, gh)
    ox = (side - gw) / 2 + pad
    oy = (side - gh) / 2 + pad
    doc = svg(side, side, glyph_rows(lv, ox, oy, cw, ch), title)
    doc = re.sub(r'(<svg[^>]*?) width="[^"]*" height="[^"]*"',
                 lambda m: f'{m.group(1)} width="{fmt(px_max)}" height="{fmt(px_max)}"',
                 doc, count=1)
    with open(path, "w") as f:
        f.write(doc)
    return ((ox - pad) / side, (oy - pad) / side, (ox - pad + gw) / side, (oy - pad + gh) / side)


def _qlmanage(paths, outdir, px=1200):
    subprocess.run(["qlmanage", "-t", "-s", str(px), "-o", outdir] + list(paths),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return [os.path.join(outdir, os.path.basename(p) + ".png") for p in paths]


def level_stats(lv):
    inked = max(1, int((lv > 0).sum()))
    parts = []
    for level in (1, 2, 3, 4, 5):
        n = int((lv == level).sum())
        parts.append(f"L{level} {100.0 * n / inked:.0f}%")
    return f"{lv.shape[0]}x{lv.shape[1]}  ink {100.0 * inked / lv.size:.0f}%  " + "  ".join(parts)


def _pad_tile(t, min_w):
    out = Image.new("RGB", (min_w, t.height), (5, 5, 10))
    out.paste(t, ((min_w - t.width) // 2, 0))
    return out


def _check_ground(lv, label):
    """Every figure sits on an exact level 0 ground (levels() asserts that no
    cell outside the figure mask is inked); here the four corner cells must be
    empty and the top row nearly so (head crops touch the other edges)."""
    assert lv[0, 0] == 0 and lv[0, -1] == 0 and lv[-1, 0] == 0 and lv[-1, -1] == 0, \
        f"{label}: a corner cell is inked"
    frac = float((lv[0] > 0).mean())
    assert frac < 0.2, f"{label}: {100 * frac:.0f}% of the top row is inked"


def _sheet(path, specs, cw, ch, tag, px=1200, tile_h=1000):
    """One sheet: each figure big (tile_h px tall) with a 1:1 render (one
    viewBox px per screen px, the size the reader sees) beside it."""
    outdir = os.path.dirname(os.path.abspath(path))
    os.makedirs(outdir, exist_ok=True)
    svgs = []
    labels = []
    boxes = []
    sides = []
    for name, rows, flip, crop in specs:
        lv = levels(name, rows, cw, ch, flip=flip, crop=crop)
        what = crop if isinstance(crop, str) else name
        _check_ground(lv, what)
        sp = os.path.join(outdir, f"photo_{what}{tag}.svg")
        boxes.append(_render_svg(lv, cw, ch, f"photo {what} {rows} rows", sp, px_max=px))
        svgs.append(sp)
        sides.append(max(lv.shape[1] * cw, rows * ch) + 4)
        labels.append((f"{what}{'  (mirrored)' if flip else ''}  cw {cw} ch {ch}",
                       level_stats(lv)))
    pngs = _qlmanage(svgs, outdir, px)
    try:
        font = ImageFont.load_default(size=22)
        small = ImageFont.load_default(size=16)
    except TypeError:
        font = small = ImageFont.load_default()
    tiles = []
    for p, (fx0, fy0, fx1, fy1), side in zip(pngs, boxes, sides):
        im = Image.open(p).convert("RGB")
        im = im.crop((int(fx0 * im.width), int(fy0 * im.height),
                      int(math.ceil(fx1 * im.width)), int(math.ceil(fy1 * im.height))))
        k = tile_h / im.height
        big = im.resize((max(1, int(im.width * k)), tile_h), Image.LANCZOS)
        # 1:1: the square canvas was `side` viewBox px, rendered at px, so the
        # true size is the thumbnail scaled by side / px
        k1 = side / px
        one = im.resize((max(1, int(round(im.width * k1))), max(1, int(round(im.height * k1)))),
                        Image.LANCZOS)
        tile = Image.new("RGB", (big.width + one.width + 16, tile_h), (5, 5, 10))
        tile.paste(big, (0, 0))
        tile.paste(one, (big.width + 16, tile_h - one.height))
        tiles.append(tile)
    gap = 24
    label_h = 56
    min_w = 360
    tiles = [t if t.width >= min_w else _pad_tile(t, min_w) for t in tiles]
    W = sum(t.width for t in tiles) + gap * (len(tiles) + 1)
    H = tile_h + label_h + gap * 2
    sheet = Image.new("RGB", (W, H), (5, 5, 10))
    draw = ImageDraw.Draw(sheet)
    x = gap
    for t, (l1, l2) in zip(tiles, labels):
        draw.text((x, 8), l1, fill=(232, 230, 240), font=font)
        draw.text((x, 34), l2, fill=(10, 127, 138), font=small)
        sheet.paste(t, (x, label_h + gap))
        x += t.width + gap
    sheet.save(path)
    return path


def contact_sheet(path):
    """Renders every source at the densities in section 3 as REAL SVG
    (lib.glyph_rows), rasterizes with qlmanage, and tiles the PNGs into one
    sheet with labels (each figure enlarged, with its 1:1 render beside it).
    A second sheet at divider density (cw 3.6, ch 5.8, 21 rows, the glance
    and profile as head crops like the section dividers use) is written next
    to it with the suffix _divider. Every figure is checked for an exact
    level 0 ground."""
    _sheet(path, HERO_SPECS, 4.4, 7.0, "")
    stem, ext = os.path.splitext(path)
    _sheet(stem + "_divider" + ext, DIVIDER_SPECS, 3.6, 5.8, "_div", tile_h=500)
    return path


if __name__ == "__main__":
    contact_sheet(os.path.join(ROOT, "preview", "photo.png"))
