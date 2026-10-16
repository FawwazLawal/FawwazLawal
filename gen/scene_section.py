"""Section dividers S1 to S4 (DESIGN.md section 4, v2: photo based) as one
parametrized module.

    sec-01-work        1200 x 150   her profile head materializes at the left
                                    of a corridor facing the work; data streaks
                                    shoot off her silhouette across the strip
                                    and the title types in behind them,
                                    chevrons flow
    sec-02-method      1200 x 150   the hand reaches up out of the bottom edge
                                    at the left; a thin yellow beam travels
                                    from the raised fingertip to the title and
                                    lights its letters in order
    sec-03-agents      1200 x 180   a true 3D icosahedron (30 edges, 60
                                    precomputed frames, depth sorted) inside a
                                    fainter outer shell; her profile head faces
                                    it, packets of digits orbit between them
    sec-04-background  1200 x 150   the quietest one: her profile head at the
                                    far right, facing the title, materializing
                                    slowly, one chromatic flicker, then she
                                    dissolves into rain at the loop end

Every loop is 8 s. All motion goes through lib.Timeline (photo.py's helpers
describe their keyframes through it) so build(t) freezes exactly.

Figures: every figure is a photo.levels grid built at the hero density (cells
4.4 x 7.0, font 7 px) with as many rows as the strip height allows, then the
whole figure group is scaled down to its target height (about 0.6). The glyph
font therefore never drops under 7 px in the document (no renderer minimum font
size can smear it) while the cells are about 2.7 x 4.3 px on screen: at a
glance she is a photograph made of texture, up close the texture is 0 and 1.
Every effect (materialize, streaks, slice glitch, chromatic split, dissolve)
is composed inside the scaled group in grid coordinates.

Looping rule: every track repeats with the 8 s loop, including the ones that
play once per loop (a streak, a falling dissolve group): a run once track is
emitted as fill="freeze" and never plays again after the first loop. The photo
helpers take repeat=True for that; the visibility spans hide the held values.
"""

import math
import random

import numpy as np

import lib
from lib import (Timeline, el, text, glyph_rows, chromatic_title, rain, floor_grid,
                 scanlines, vignette, svg, project, rotate, typed, moving_group,
                 clip_reveal, fmt, CYAN, CYAN_DIM, MAGENTA, YELLOW, BONE, PURPLE)
import photo

W = 1200
DUR = 8.0

# figure grid density (DESIGN.md section 3): the hero cells, scaled per figure
CW, CH = 4.4, 7.0

TITLE_SIZE = 34
TITLE_LS = 6
TITLE_Y = 84
MARGIN_R = 1150


# ----------------------------------------------------------------------------
# shared helpers
# ----------------------------------------------------------------------------

class Figure:
    """A photo figure: the level grid at hero density plus the scale that
    makes it `height` px tall. `rot` = -1 rotates the grid a quarter turn
    clockwise (the hand reaching right): the grid is built with the cell
    aspect swapped so the rotated cells keep the 4.4 x 7.0 aspect."""

    def __init__(self, name, rows, height, flip=False, crop=None, rot=0, seed=0, **kw):
        # extra keyword arguments are tone overrides for photo.levels
        if rot:
            lv = photo.levels(name, rows, CH, CW, flip=flip, crop=crop, seed=seed, **kw)
            lv = np.ascontiguousarray(np.rot90(lv, k=rot))
        else:
            lv = photo.levels(name, rows, CW, CH, flip=flip, crop=crop, seed=seed, **kw)
        self.lv = lv
        self.rows, self.cols = lv.shape
        self.gw, self.gh = self.cols * CW, self.rows * CH
        self.s = height / self.gh
        self.w, self.h = self.gw * self.s, height
        self.x = self.y = 0.0

    def place(self, x, y):
        self.x, self.y = float(x), float(y)
        return self

    def wrap(self, inner):
        return (f'<g transform="translate({fmt(self.x)} {fmt(self.y)}) scale({fmt(self.s)})">'
                f'{inner}</g>')

    def to_screen(self, gx, gy):
        return self.x + gx * self.s, self.y + gy * self.s

    def tip_right(self):
        """screen position of the rightmost inked cell (the fingertip of the
        rotated hand)"""
        inked = np.argwhere(self.lv > 0)
        c = int(inked[:, 1].max())
        rows = inked[inked[:, 1] == c][:, 0]
        r = float(rows.mean())
        return self.to_screen((c + 1) * CW, (r + 0.5) * CH)

    def tip_top(self):
        """screen position of the topmost inked cell (the raised fingertip of
        the upright hand)"""
        inked = np.argwhere(self.lv > 0)
        r = int(inked[:, 0].min())
        cols = inked[inked[:, 0] == r][:, 1]
        c = float(cols.mean())
        return self.to_screen((c + 0.5) * CW, r * CH)


def figure_layer(tl, fig, t_in, dur_in, t_out, glitch_times, chroma_times, seed,
                 breathe=0.012, flicker=3):
    """The standard figure treatment: rows materialize in seeded order from
    t_in over dur_in and hold until t_out; the magenta/cyan split kicks at
    chroma_times and horizontal slice bands shift at glitch_times (both show a
    cheap flat copy for 160 ms); a slow breathing scale about the figure's
    centre. Returns the positioned group."""
    lv = fig.lv

    def plain():
        return photo.materialize(tl, lv, 0, 0, CW, CH, t_in, dur_in, seed=seed,
                                 hold_until=t_out, flicker=flicker)

    def flat():
        return glyph_rows(lv, 0, 0, CW, CH, flat=True)

    def chroma_fn(fill):
        if fill is None:
            return plain()
        return photo.recolor(flat(), fill)

    inner = photo.chromatic(tl, chroma_fn, chroma_times) if chroma_times else plain()
    if glitch_times:
        inner = photo.slice_glitch(tl, inner, 0, 0, fig.gw, fig.gh, glitch_times,
                                   seed=seed + 1, glitch_fn=flat)
    if breathe:
        cx, cy = fig.gw / 2, fig.gh / 2
        sf, sa = tl.transform([(0.0, 1.0), (DUR / 2, 1.0 + breathe), (DUR, 1.0)], kind="scale",
                              calc="spline", splines=[(0.42, 0, 0.58, 1), (0.42, 0, 0.58, 1)])
        inner = (f'<g transform="translate({fmt(cx)} {fmt(cy)})"><g{sf}>'
                 f'<g transform="translate({fmt(-cx)} {fmt(-cy)})">{inner}</g>{sa}</g></g>')
    return fig.wrap(inner)


def title_metrics(s, size, ls):
    """(cell advance, locked total width) of a letter spaced monospace title"""
    cw = size * lib.MONO_ADV
    n = len(s)
    return cw + ls, n * cw + (n - 1) * ls


def title(tl, s, x, y, bursts, size=TITLE_SIZE, ls=TITLE_LS, anchor="end"):
    """chromatic title with its width locked (lengthAdjust=spacing spreads the
    letters, so no letter-spacing attribute is needed and every monospace font
    gives the same width)"""
    _, w = title_metrics(s, size, ls)
    return chromatic_title(tl, s, x, y, size, bursts, ls=0, anchor=anchor,
                           extra=f'textLength="{fmt(w)}" lengthAdjust="spacing"')


def backdrop(tl, h, vp, seed, rain_op=0.2, grid_op=0.5, ceiling=True, speed=0.5,
             n_rain=30, glow=0.3, n_lines=7):
    """purple depth glow at the vanishing point, far field rain, a perspective
    floor flowing toward the viewer and (optionally) its mirror as a ceiling,
    which turns the strip into a corridor"""
    vx, vy = vp
    out = []
    gid = lib.uid("glow")
    out.append(f'<radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
               f'<stop offset="0%" stop-color="{PURPLE}" stop-opacity="{fmt(glow)}"/>'
               f'<stop offset="100%" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>')
    out.append(el("ellipse", {"cx": vx, "cy": vy, "rx": 540, "ry": 78, "fill": f"url(#{gid})"}))
    out.append(rain(tl, 0, W, 0, h, n_rain, seed, opacity=rain_op, size=10, length=(6, 14)))
    out.append(floor_grid(tl, W, h, vp, n_lines=n_lines, speed=speed, color=CYAN_DIM,
                          n_radial=15, opacity=grid_op))
    if ceiling:
        out.append(f'<g transform="translate(0 {fmt(2 * vy)}) scale(1 -1)">'
                   + floor_grid(tl, W, h, vp, n_lines=n_lines, speed=speed, color=CYAN_DIM,
                                n_radial=15, opacity=grid_op * 0.55)
                   + "</g>")
    return "".join(out)


def hud_corners(h, m=6.0, leg=16.0):
    """four thin corner brackets, the HUD frame of every divider"""
    pts = [
        ((m, m + leg), (m, m), (m + leg, m)),
        ((W - m - leg, m), (W - m, m), (W - m, m + leg)),
        ((m, h - m - leg), (m, h - m), (m + leg, h - m)),
        ((W - m - leg, h - m), (W - m, h - m), (W - m, h - m - leg)),
    ]
    out = []
    for a, b, c in pts:
        out.append(f'<polyline points="{fmt(a)} {fmt(b)} {fmt(c)}" fill="none" stroke="{CYAN}" '
                   f'stroke-opacity="0.55" stroke-width="1"/>')
    return "".join(out)


def glitch_bars(tl, x0, x1, y0, y1, windows, seed, n=6):
    """thin horizontal slices of CYAN and MAGENTA that flash inside the given
    (start, end) windows, the visual of a corrupted frame"""
    rng = random.Random(seed)
    out = []
    for k in range(n):
        yy = rng.uniform(y0, y1)
        hh = rng.uniform(1.5, 4.5)
        ww = rng.uniform(0.2, 0.8) * (x1 - x0)
        xx = x0 + rng.uniform(0, (x1 - x0) - ww)
        color = (MAGENTA, CYAN, CYAN)[k % 3]
        spans = []
        for a, b in windows:
            s = a + rng.uniform(0, (b - a) * 0.6)
            e = min(b, s + rng.uniform(0.05, 0.12))
            spans.append((s, e))
        vf, va = tl.visible(spans)
        out.append(f'<rect x="{fmt(xx)}" y="{fmt(yy)}" width="{fmt(ww)}" height="{fmt(hh)}" '
                   f'fill="{color}" fill-opacity="0.5"{vf}>{va}</rect>')
    return "".join(out)


def overlay(h):
    return vignette(W, h, strength=0.7) + scanlines(W, h) + hud_corners(h)


def typing_title(tl, s, x, y, t_type, cps, bursts, hide_at, size=TITLE_SIZE, ls=TITLE_LS):
    """a start anchored chromatic title typed in character by character under a
    clip, with a yellow block cursor while it types"""
    cell, w = title_metrics(s, size, ls)
    n = len(s)
    width_kf = [(t_type + k / cps, k * cell) for k in range(n)] + [(t_type + n / cps, w + 16)]
    t_done = t_type + n / cps
    ttl = title(tl, s, x, y, bursts=bursts, size=size, ls=ls, anchor="start")
    ttl = clip_reveal(tl, ttl, x - 8, y - size, size * 1.4, width_kf, repeat=True)
    xkf = [(t_type + k / cps, x + k * cell + 2) for k in range(n + 1)]
    xf, xa = tl.attr("x", xkf, calc="discrete")
    cvf, cva = tl.visible([(t_type, t_done + 0.5)])
    cursor = (f'<rect{xf} y="{fmt(y - size * 0.8)}" width="{fmt(cell * 0.38)}" '
              f'height="{fmt(size * 0.92)}" fill="{YELLOW}"{cvf}>{xa}{cva}</rect>')
    tvf, tva = tl.visible([(t_type, hide_at)])
    return f'<g{tvf}>{ttl}{cursor}{tva}</g>', t_done, w


def prompt(tl, s, x, y, begin, hide_at, size=10, cps=22):
    """the typed terminal prompt of a divider: it types in from `begin` and
    is cut at `hide_at` (inside the end glitch window), so the frame at the
    loop seam equals frame 0 and the retype on the next loop reads as the
    glitch having reset the terminal"""
    vf, va = tl.visible([(0.0, hide_at)])
    return f'<g{vf}>{typed(tl, s, x, y, size, CYAN_DIM, begin=begin, cps=cps)}{va}</g>'


def chevrons(tl, x0, x1, cy, spans, font=13):
    """a row of >>> flowing right between x0 and x1, faded at both ends"""
    ccw = font * lib.MONO_ADV
    pattern = ">>>   "
    cells = int((x1 - x0) / ccw) + 8
    chev_s = (pattern * (cells // len(pattern) + 1))[:cells]
    gid = lib.uid("chevgrad")
    mid = lib.uid("chevmask")
    out = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
           f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
           f'<stop offset="0.3" stop-color="#fff" stop-opacity="1"/>'
           f'<stop offset="0.7" stop-color="#fff" stop-opacity="1"/>'
           f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
           f'<mask id="{mid}"><rect x="{fmt(x0)}" y="{fmt(cy - 14)}" width="{fmt(x1 - x0)}" '
           f'height="20" fill="url(#{gid})"/></mask>')
    p = DUR / 16
    row = text(x0 - 6 * ccw, cy, chev_s, font, CYAN, opacity=0.95,
               extra=f'textLength="{fmt(cells * ccw)}" lengthAdjust="spacingAndGlyphs"')
    out += (f'<g mask="url(#{mid})">'
            + moving_group(tl, row, translate=[(0.0, (0, 0)), (p, (6 * ccw, 0))], period=p)
            + "</g>")
    vf, va = tl.visible(spans)
    return f'<g{vf}>{out}{va}</g>'


# ----------------------------------------------------------------------------
# S1  01 // SELECTED WORK
# ----------------------------------------------------------------------------

def build_s1(t=None):
    tl = Timeline(DUR, t)
    H = 150
    VP = (600, 68)
    body = [backdrop(tl, H, VP, seed=11, rain_op=0.2, grid_op=0.5, speed=0.6)]

    # her profile head, 126 px tall at the left, facing right into the work:
    # the glance-back crop does not read as a woman at this size (the lit
    # face is a sliver beside the hair mass), the rim lit profile does
    fig = Figure("profile", 34, 126, crop="profile_head").place(56, 13)
    t_in, t_out = 0.5, 7.7
    body.append(figure_layer(tl, fig, t_in, 0.7, t_out, glitch_times=[7.4],
                             chroma_times=[1.1, 4.6], seed=3))

    # data streaks: digits shoot rightward off her silhouette across the
    # whole strip (grid coordinates inside the scaled group), two bursts
    inv = 1.0 / fig.s
    streak = (photo.streaks(tl, fig.lv, 0, 0, CW, CH, [1.0], seed=11, n=12, repeat=True,
                            travel=(640 * inv, 1060 * inv), fade=1.1, sides=(1,),
                            length=(50, 180))
              + photo.streaks(tl, fig.lv, 0, 0, CW, CH, [1.3, 5.2], seed=12, n=7, repeat=True,
                              travel=(300 * inv, 820 * inv), fade=0.9, sides=(1,),
                              length=(40, 140)))
    body.append(fig.wrap(streak))

    # the title types in at x 420 as the streaks pass, with a chromatic burst
    # when it lands; chevrons flow right under it; all of it dies in the glitch
    t_type = 1.3
    ttl, t_done, w = typing_title(tl, "01 // SELECTED WORK", 420, TITLE_Y, t_type, 18,
                                  bursts=[2.5, 7.5], hide_at=7.85)
    body.append(ttl)
    body.append(chevrons(tl, 420, 420 + w, 112, spans=[(t_done - 0.1, 7.85)]))

    body.append(glitch_bars(tl, 380, 1160, 36, 128, [(t_done + 0.1, t_done + 0.3), (7.45, 7.85)],
                            seed=5, n=7))
    body.append(prompt(tl, "> cd ./work && ls", 420, 36, begin=0.3, hide_at=7.6))
    body.append(overlay(H))
    return svg(W, H, "".join(body), "01 // SELECTED WORK")


# ----------------------------------------------------------------------------
# S2  02 // HOW I WORK
# ----------------------------------------------------------------------------

def build_s2(t=None):
    tl = Timeline(DUR, t)
    H = 150
    VP = (600, 68)
    body = [backdrop(tl, H, VP, seed=22, rain_op=0.18, grid_op=0.45, speed=0.4)]

    # the hand upright, reaching up out of the bottom edge of the strip (the
    # photo's own composition, which reads as a hand at once where the
    # rotated grid read as a claw), palm and fingers only, the thumb toward
    # the title; the beam leaves the raised index fingertip
    fig = Figure("hand", 36, 128, crop="hand_tight").place(72, 20)
    t_in, t_out = 0.6, 7.6
    body.append(figure_layer(tl, fig, t_in, 0.5, t_out, glitch_times=[7.35],
                             chroma_times=[4.4], seed=4, flicker=4))
    tip = fig.tip_top()

    # the title, letter by letter, lit from the fingertip outward
    title_s = "02 // HOW I WORK"
    cell, w = title_metrics(title_s, TITLE_SIZE, TITLE_LS)
    x0 = MARGIN_R - w
    target = (x0 - 10, TITLE_Y - TITLE_SIZE * 0.36)
    t_beam = 1.2
    t_arrive = 2.0
    t_light = [t_arrive + i * 0.055 for i in range(len(title_s))]
    t_off = 7.5
    burst_times = [t_arrive + 1.2, 7.4]

    def burst_track(rest):
        """the chromatic kick of lib.chromatic_title as a group translate"""
        sg = -1 if rest < 0 else 1
        kfs = [(0.0, (rest, 0))]
        for b in burst_times:
            for dt, m in ((0.0, 8), (0.05, -4.5), (0.1, 6)):
                kfs.append((b + dt, (sg * m, 0)))
            kfs.append((b + 0.16, (rest, 0)))
        return kfs

    layers = []
    for fill, rest, op in ((MAGENTA, -2, 0.9), (CYAN, 2, 0.9)):
        letters = []
        for i, chv in enumerate(title_s):
            if chv == " ":
                continue
            vf, va = tl.visible([(t_light[i] + 0.08, t_off)])
            letters.append(text(x0 + i * cell, TITLE_Y, chv, TITLE_SIZE, fill, opacity=op,
                                extra=vf.strip(), anims=va))
        tf, ta = tl.transform(burst_track(rest), kind="translate", calc="discrete")
        layers.append(f'<g{tf}>{"".join(letters)}{ta}</g>')
    letters = []
    for i, chv in enumerate(title_s):
        if chv == " ":
            continue
        okf = [(0.0, 0.14), (t_light[i], 1), (t_light[i] + 0.04, 0.14), (t_light[i] + 0.08, 1),
               (t_off, 0.14)]
        of, oa = tl.attr("opacity", okf, calc="discrete")
        letters.append(text(x0 + i * cell, TITLE_Y, chv, TITLE_SIZE, BONE, extra=of.strip(),
                            anims=oa))
    layers.append(f"<g>{''.join(letters)}</g>")
    body.append(f'<g font-weight="bold">{"".join(layers)}</g>')

    # the yellow beam from the fingertip to the first letter: the endpoint
    # travels once per loop (repeating tracks, held at the tip before t_beam
    # and at the title after t_arrive, both hidden by the visibility span)
    bvf, bva = tl.visible([(t_beam, 7.3)])
    travel = [(t_beam, tip), (t_arrive, target)]
    x2f, x2a = tl.attr("x2", [(a, v[0]) for a, v in travel])
    y2f, y2a = tl.attr("y2", [(a, v[1]) for a, v in travel])
    body.append(f'<g{bvf}>'
                f'<line x1="{fmt(tip[0])}" y1="{fmt(tip[1])}"{x2f}{y2f} stroke="{CYAN}" '
                f'stroke-width="5" stroke-opacity="0.18">{x2a}{y2a}</line>'
                f'<line x1="{fmt(tip[0])}" y1="{fmt(tip[1])}"{x2f}{y2f} stroke="{YELLOW}" '
                f'stroke-width="1.2" stroke-opacity="0.85">{x2a}{y2a}</line>{bva}</g>')
    cxf, cxa = tl.attr("cx", [(a, v[0]) for a, v in travel])
    cyf, cya = tl.attr("cy", [(a, v[1]) for a, v in travel])
    body.append(f'<circle{cxf}{cyf} r="2.4" fill="{YELLOW}"{bvf}>{cxa}{cya}{bva}</circle>')
    body.append(f'<circle cx="{fmt(tip[0])}" cy="{fmt(tip[1])}" r="3.2" fill="{YELLOW}" '
                f'fill-opacity="0.6"{bvf}>{bva}</circle>')
    # digit packets travelling along the beam
    p = DUR / 10
    for j, chv in enumerate(("1", "0", "1")):
        pvf, pva = tl.visible([(t_arrive + 0.2, 7.3)])
        tf, ta = tl.transform([(0.0, (tip[0], tip[1] - 4)), (p, (target[0], target[1] - 4))],
                              kind="translate", begin=-j * p / 3, period=p)
        body.append(f'<g{pvf}><g{tf}>{text(0, 0, chv, 10, CYAN, anchor="middle")}{ta}</g>{pva}</g>')
    # a small streak burst off the fingers as the beam fires
    body.append(fig.wrap(photo.streaks(tl, fig.lv, 0, 0, CW, CH, [t_beam], seed=21, n=6,
                                       repeat=True, sides=(1,), travel=(80, 260), fade=0.6)))

    body.append(glitch_bars(tl, 240, 1160, 30, 130, [(7.4, 7.8)], seed=9, n=7))
    # the prompt sits above the title, clear of the HUD corner and the beam
    body.append(prompt(tl, "> cat ./method.md", x0, 40, begin=0.2, hide_at=7.55))
    body.append(overlay(H))
    return svg(W, H, "".join(body), "02 // HOW I WORK")


# ----------------------------------------------------------------------------
# S3  03 // WORKING WITH AGENTS
# ----------------------------------------------------------------------------

def solid_verts(kind, radius):
    """unit solid scaled to `radius`: vertices (N, 3) and the edge list"""
    if kind == "icosahedron":
        phi = (1 + math.sqrt(5)) / 2
        raw = []
        for a in (-1, 1):
            for b in (-phi, phi):
                raw += [(0, a, b), (a, b, 0), (b, 0, a)]
        edge_len = 2.0
        n_edges = 30
    elif kind == "octahedron":
        raw = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        edge_len = math.sqrt(2)
        n_edges = 12
    else:
        raise ValueError(kind)
    verts = np.array(raw, dtype=float)
    r0 = np.linalg.norm(verts[0])
    edges = []
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            if abs(np.linalg.norm(verts[i] - verts[j]) - edge_len) < 1e-6:
                edges.append((i, j))
    assert len(edges) == n_edges, len(edges)
    return verts * (radius / r0), edges


def solid_frames(verts, n_frames, spin, tilt, cam, center):
    """projected vertices (n_frames, N, 3) of a solid rotating `spin` (turns
    about x, turns about y) per loop; integer spins make the loop seamless"""
    frames = []
    for k in range(n_frames):
        a = 2 * math.pi * k / n_frames
        pts = rotate(verts, a * spin[0] + tilt[0], a * spin[1] + tilt[1], tilt[2])
        frames.append(project(pts, cam_dist=cam, scale=1.0, center=center))
    return np.array(frames)


def icosahedron(tl, center, radius, n_frames=60, spin=(1, 1), tilt=(0.35, 0.0, 0.25),
                cam=300.0, opacity=(0.14, 1.0), stroke=1.3, glyphs=True, glyph_size=11,
                seed=3, fps=None, kind="icosahedron"):
    """wireframe solid (an icosahedron by default), depth sorted opacity per
    edge, a 0/1 glyph at each vertex, every attribute a discrete track of
    n_frames values"""
    fps = fps or n_frames / tl.dur
    verts, edges = solid_verts(kind, radius)
    frames = solid_frames(verts, n_frames, spin, tilt, cam, center)
    n_verts = len(verts)
    fmin, fmax = frames[:, :, 2].min(), frames[:, :, 2].max()

    def depth_op(f):
        u = (f - fmin) / max(fmax - fmin, 1e-6)
        return round(opacity[0] + (opacity[1] - opacity[0]) * u, 2)

    rng = random.Random(seed)
    out = []
    for i, j in edges:
        kf = {"x1": [], "y1": [], "x2": [], "y2": [], "stroke-opacity": []}
        for k in range(n_frames):
            tt = k / fps
            pr = frames[k]
            kf["x1"].append((tt, round(pr[i, 0], 1)))
            kf["y1"].append((tt, round(pr[i, 1], 1)))
            kf["x2"].append((tt, round(pr[j, 0], 1)))
            kf["y2"].append((tt, round(pr[j, 1], 1)))
            kf["stroke-opacity"].append((tt, depth_op((pr[i, 2] + pr[j, 2]) / 2)))
        frags, anims = "", ""
        for name, keys in kf.items():
            f, a = tl.attr(name, keys, calc="discrete")
            frags += f
            anims += a
        out.append(f'<line{frags} stroke="{CYAN}" stroke-width="{fmt(stroke)}">{anims}</line>')
    if glyphs:
        for i in range(n_verts):
            xk = [(k / fps, round(frames[k][i, 0], 1)) for k in range(n_frames)]
            yk = [(k / fps, round(frames[k][i, 1] + glyph_size * 0.35, 1)) for k in range(n_frames)]
            ok = [(k / fps, depth_op(frames[k][i, 2])) for k in range(n_frames)]
            xf, xa = tl.attr("x", xk, calc="discrete")
            yf, ya = tl.attr("y", yk, calc="discrete")
            of, oa = tl.attr("fill-opacity", ok, calc="discrete")
            chv = rng.choice("01")
            out.append(f'<text{xf}{yf}{of} font-size="{fmt(glyph_size)}" fill="{CYAN}" '
                       f'text-anchor="middle" font-weight="bold">{chv}{xa}{ya}{oa}</text>')
    return f"<g>{''.join(out)}</g>"


def orbit_packets(tl, center, rx, ry, labels, period, seed, size=10, front_scale=1.2):
    """small digit packets on an elliptical orbit: brighter and larger at the
    front (bottom of the ellipse), dim and small at the back"""
    rng = random.Random(seed)
    cx, cy = center
    samples = 24
    out = []
    for j, label in enumerate(labels):
        tkf, okf, skf = [], [], []
        for q in range(samples + 1):
            u = q / samples
            a = 2 * math.pi * u
            x = cx + rx * math.cos(a)
            y = cy + ry * math.sin(a)
            front = (math.sin(a) + 1) / 2
            tkf.append((u * period, (round(x, 1), round(y, 1))))
            okf.append((u * period, round(0.3 + 0.7 * front, 2)))
            skf.append((u * period, round(0.7 + (front_scale - 0.7) * front, 3)))
        begin = -(j / len(labels) + rng.uniform(-0.04, 0.04)) * period
        of, oa = tl.attr("opacity", okf, period=period, begin=begin)
        tf, ta = tl.transform(tkf, kind="translate", period=period, begin=begin)
        sf, sa = tl.transform(skf, kind="scale", period=period, begin=begin)
        glyph = text(0, size * 0.35, label, size, CYAN, anchor="middle",
                     extra=f'textLength="{fmt(len(label) * size * lib.MONO_ADV)}" lengthAdjust="spacingAndGlyphs"'
                     if len(label) > 1 else "")
        out.append(f'<g{of}><g{tf}><g{sf}>{glyph}{sa}</g>{ta}</g>{oa}</g>')
    return "".join(out)


def build_s3(t=None):
    tl = Timeline(DUR, t)
    H = 180
    VP = (600, 84)
    OBJ = (180, 92)
    body = [backdrop(tl, H, VP, seed=33, rain_op=0.18, grid_op=0.45, speed=0.45, n_lines=8)]

    # outer shell, faint, turning the other way; then the core object
    body.append(f'<g opacity="0.22">'
                + icosahedron(tl, OBJ, 76, spin=(-1, 1), tilt=(0.9, 0.3, 0.6), opacity=(0.2, 1.0),
                              stroke=0.8, glyphs=False)
                + "</g>")
    body.append(icosahedron(tl, OBJ, 58, spin=(1, 1), tilt=(0.35, 0.0, 0.25), stroke=1.4, seed=3))

    # her profile head, 140 px tall at x 330, facing the object (mirrored)
    fig = Figure("profile", 32, 140, flip=True, crop="profile_head").place(330, 22)
    t_in, t_out = 0.4, 7.7
    body.append(figure_layer(tl, fig, t_in, 0.6, t_out, glitch_times=[7.45],
                             chroma_times=[3.2, 6.1], seed=8))
    # streaks off her silhouette toward the object as the link opens
    body.append(fig.wrap(photo.streaks(tl, fig.lv, 0, 0, CW, CH, [1.6, 5.0], seed=31, n=7,
                                       repeat=True, sides=(-1,), travel=(60, 160), fade=0.6)))

    # packets orbiting between her and the object, on a faint orbit ring
    ORB = (268, 108)
    body.append(el("ellipse", {"cx": ORB[0], "cy": ORB[1], "rx": 56, "ry": 20, "fill": "none",
                               "stroke": CYAN_DIM, "stroke-opacity": 0.35, "stroke-width": 0.8,
                               "stroke-dasharray": "3 4"}))
    body.append(orbit_packets(tl, ORB, 56, 20, ("01", "1", "10", "0", "11", "001"),
                              period=DUR / 3, seed=4))

    title_s = "03 // WORKING WITH AGENTS"
    size = 28
    cell, w = title_metrics(title_s, size, TITLE_LS)
    body.append(title(tl, title_s, MARGIN_R, 94, bursts=[2.4, 7.5], size=size))
    body.append(prompt(tl, "> agents.spawn(parallel=true)", MARGIN_R - w, 122, begin=1.0,
                       hide_at=7.6, size=11))

    body.append(glitch_bars(tl, 60, 1160, 30, 160, [(7.45, 7.8)], seed=12, n=7))
    body.append(overlay(H))
    return svg(W, H, "".join(body), "03 // WORKING WITH AGENTS")


# ----------------------------------------------------------------------------
# S4  04 // BACKGROUND
# ----------------------------------------------------------------------------

def build_s4(t=None):
    tl = Timeline(DUR, t)
    H = 150
    VP = (600, 68)
    body = [backdrop(tl, H, VP, seed=44, rain_op=0.12, grid_op=0.35, speed=0.3, n_rain=22,
                     glow=0.22)]

    # her profile head, 110 px, at the far right facing left toward the title
    fig = Figure("profile", 26, 110, flip=True, crop="profile_head")
    fig.place(W - 36 - fig.w, 22)
    t_in, t_dis = 0.6, 6.4
    body.append(figure_layer(tl, fig, t_in, 1.5, t_dis, glitch_times=[], chroma_times=[4.6],
                             seed=5, flicker=2))
    # she dissolves into rain at the end of the loop
    body.append(fig.wrap(photo.dissolve_anim(tl, fig.lv, 0, 0, CW, CH, t_dis, 1.1, seed=7,
                                             steps=6, appear=t_dis, fall=60, fall_dur=0.5,
                                             repeat=True)))

    tx = fig.x - 44
    body.append(title(tl, "04 // BACKGROUND", tx, TITLE_Y, bursts=[2.6, 7.5]))
    body.append(glitch_bars(tl, 560, 1160, 40, 120, [(7.5, 7.75)], seed=19, n=4))
    # the prompt is inset past the HUD corner bracket (x 6..22, y 6..22)
    body.append(prompt(tl, "> whoami", 36, 40, begin=0.4, hide_at=7.6))
    body.append(overlay(H))
    return svg(W, H, "".join(body), "04 // BACKGROUND")


SCENES = {
    "sec-01-work": build_s1,
    "sec-02-method": build_s2,
    "sec-03-agents": build_s3,
    "sec-04-background": build_s4,
}
