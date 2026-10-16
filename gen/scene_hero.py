"""S0 hero: assets/hero.svg, 1200 x 560, 18 s loop (DESIGN.md section 4, v2).

The reader is the POV, already inside the system. Far field: a 3D tunnel of
digit rings (elliptical rings of 0/1 glyphs with a thin rail, projected with
1 / z, flying toward the camera and recycling at the far end), a perspective
floor flowing toward the viewer, faint far rain and a purple depth glow at the
vanishing point. The floor and the tunnel share one time warp, so both surge
forward while she runs into the system. Left: the name block. Right: the
glance-back photograph dithered into glyphs, mirrored so she looks toward the
name and the viewer.

Timeline (seconds)
    0.0   floor and tunnel fade in from black (done at 1.2)
    0.3   the identity line types in (done at 2.3)
    2.0   she arrives from beyond the right edge with three ghost copies
          trailing, rows materializing in random order; slice glitch at 2.72
    2.3   the big name is revealed letter by letter; subtitles fade up at 2.9
    3.1   chromatic burst on the name (again at 12.4)
    3.4   data streaks burst off her silhouette (again at 6.6)
    4.2   chromatic split on her (again at 8.0); she breathes throughout
    6.0   the hand materializes between her and the name, over the floor and
          in front of her left edge, with a magenta fringe (a nearer object),
          and beckons four times at 2 Hz from 6.5, then holds
    7.0   the follow prompt types in and blinks
    9.3   the hand fades, gone at 9.5
    9.5   she turns to go: a 200 ms glitch cut swaps her for the profile head
          facing right
   11.0   the profile head scales toward the vanishing point while its cells
          rain off; the tunnel surges 11.5 to 13.0; glitch burst at 13.6
   14.0   calm, the prompt blinks; the name block cuts at 17.9 under a camera
          jolt and the far field dims to 0.35 across the seam, so the loop
          restarts from a dim tunnel, not from black

Every track repeats on the 18 s period (lib inserts the lead hold), so the
second and later passes play the whole story, and everything animates through
lib.Timeline and the photo.py helpers, so build.py's freeze mode is exact.
"""

import math
import random

import lib
from lib import (Timeline, el, text, glyph_rows, chromatic_title, rain, scanlines,
                 vignette, svg, typed, moving_group, clip_reveal,
                 BG, CYAN, CYAN_DIM, MAGENTA, YELLOW, BONE, PURPLE)
import photo

W, H = 1200, 560
DUR = 18.0
VP = (600, 300)
CW, CH = 4.4, 7.0

# story beats
T_ARRIVE, ARRIVE_DUR = 2.0, 0.7
T_GLITCH_IN = 2.72
T_STREAKS = (3.4, 6.6)
T_CHROMA = (4.2, 8.0)
T_HAND, HAND_DUR = 6.0, 0.5
T_BECKON0, T_BECKON1 = 6.5, 8.5
T_PROMPT = 7.0
T_TURN = 9.5
T_HAND_FADE, T_HAND_GONE = 9.3, 9.5
T_RUN0, T_RUN1 = 11.0, 13.5
T_SURGE0, T_SURGE1 = 11.5, 13.0
T_GLITCH_OUT = 13.6
T_FADE0 = 17.6
T_CUT = 17.9
FAR_SEAM = 0.35                     # far field opacity across the loop seam
NAME_BURSTS = (3.1, 12.4)

# name block
NX = 48
PANEL_X1 = 680
NAME_BAND_Y1 = 270                  # left going streaks fire from below this

# the hand: left edge (it sits between the name block and her, over the
# floor, overlapping only her dissolved sleeve edge)
HAND_X = 700

# figure placement: she is 518 px tall, right edge 40 px from the frame edge,
# bottom edge 12 px above the frame bottom (on the floor)
FIG_RIGHT_MARGIN = 40
FIG_BOTTOM = H - 12


# ---------------------------------------------------------------------------
# the shared time warp: how far the camera has travelled in z. Base rate plus
# a sin^2 surge while she runs into the system. The loop travels exactly
# Z_LOOP units, a multiple of the floor span (12) and the tunnel span (3), so
# every ring and every floor line is back where it started at 18 s.
# ---------------------------------------------------------------------------

Z_LOOP = 12.0
Z_SURGE = 2.4                       # extra z during the surge
Z_RATE = (Z_LOOP - Z_SURGE) / DUR   # z per second when calm


def progress(t):
    """z travelled since 0 (monotonic, progress(DUR) == Z_LOOP)"""
    p = Z_RATE * t
    if t > T_SURGE0:
        u = (min(t, T_SURGE1) - T_SURGE0) / (T_SURGE1 - T_SURGE0)
        # integral of 2 sin^2(pi u) du = u - sin(2 pi u) / (2 pi)
        p += Z_SURGE * (u - math.sin(2 * math.pi * u) / (2 * math.pi))
    return p


def _solve_progress(target):
    """time at which progress(t) == target (bisection, progress is monotonic)"""
    lo, hi = 0.0, DUR
    for _ in range(50):
        mid = (lo + hi) / 2
        if progress(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def sample_times(wraps):
    """sample grid for a warped track: 0.2 s when calm, 0.05 s through the
    surge, plus a pair of samples 2 ms either side of every wrap so the jump
    back to the far end is never interpolated across a visible interval"""
    ts = set()
    t = 0.0
    while t < DUR - 1e-9:
        ts.add(round(t, 4))
        t += 0.2
    t = T_SURGE0 - 0.3
    while t < T_SURGE1 + 0.3:
        ts.add(round(t, 4))
        t += 0.05
    ts.add(DUR)
    for w in wraps:
        for s in (w - 0.002, w + 0.002):
            if 0.0 < s < DUR:
                ts.add(round(s, 4))
    return sorted(ts)


def _collapse(kfs):
    """drop keyframes that repeat the previous value (for discrete tracks)"""
    out = []
    for t, v in kfs:
        if not out or out[-1][1] != v:
            out.append((t, v))
    return out


def hero_floor(tl, n_lines=12, color=CYAN_DIM, opacity=0.75):
    """Perspective floor like lib.floor_grid, but the horizontal lines follow
    the shared time warp. Line i sits at z = 13 - ((progress + i) mod 12)."""
    vx, vy = VP
    out = []
    half = 17 // 2
    spread = W * 0.42
    for i in range(-half, half + 1):
        xb = vx + i * spread
        x2 = vx + (xb - vx) * 3.0
        y2 = vy + (H - vy) * 3.0
        out.append(f'<line x1="{lib.fmt(vx)}" y1="{lib.fmt(vy)}" x2="{lib.fmt(x2)}" y2="{lib.fmt(y2)}" '
                   f'stroke="{color}" stroke-width="1" stroke-opacity="0.6"/>')
    out.append(f'<line x1="0" y1="{lib.fmt(vy)}" x2="{W}" y2="{lib.fmt(vy)}" '
               f'stroke="{color}" stroke-width="1" stroke-opacity="0.8"/>')
    n = n_lines
    for i in range(n):
        wraps = []
        for k in range(int(Z_LOOP / n) + 2):
            target = k * n - i
            if 0 < target < Z_LOOP:
                wraps.append(_solve_progress(target))
        ykf, okf = [], []
        for t in sample_times(wraps):
            s = (progress(t) + i) % n
            if any(abs(t - w) < 0.003 for w in wraps):
                s = n - 1e-6 if s > n / 2 else 0.0
            z = 1.0 + (n - s)
            yy = (H - vy) / z
            op = min(1.0, max(0.08, 1.0 / z))
            ykf.append((t, (0, round(yy, 2))))
            okf.append((t, round(op, 3)))
        tf, ta = tl.transform(ykf, kind="translate")
        of, oa = tl.attr("stroke-opacity", okf)
        out.append(f'<g{tf}><line x1="0" y1="{lib.fmt(vy)}" x2="{W}" y2="{lib.fmt(vy)}" '
                   f'stroke="{color}" stroke-width="1"{of}>{oa}</line>{ta}</g>')
    clip = lib.uid("floor")
    return (f'<clipPath id="{clip}"><rect x="0" y="{lib.fmt(vy)}" width="{W}" '
            f'height="{lib.fmt(H - vy)}"/></clipPath>'
            f'<g clip-path="url(#{clip})" opacity="{lib.fmt(opacity)}">{"".join(out)}</g>')


TUN_RINGS = 12
TUN_SPAN = 3.0                       # z depth the rings cycle through
TUN_NEAR = 0.85
TUN_FAR = TUN_NEAR + TUN_SPAN
TUN_DZ = TUN_SPAN / TUN_RINGS
TUN_RX, TUN_RY = 440.0, 250.0        # ring radii at z = 1 (a wide corridor)
TUN_SIZE = 13                        # glyph size at z = 1 (texture, not type)
TUN_GLYPHS = 24
TUN_LIGHT_Z = 2.1                    # rings nearer than this are bright CYAN


def hero_tunnel(tl, opacity=1.0):
    """The 3D tunnel: TUN_RINGS elliptical rings of TUN_GLYPHS digits at fixed
    angles (alternate rings staggered by half a step so the digits form a
    lattice), each with a thin rail, scaled by 1 / z about the vanishing point.
    Far rings are dim CYAN_DIM at low opacity, they switch to bright CYAN as
    they pass TUN_LIGHT_Z and fade out as they fly past the camera. Ring i
    sits at z = TUN_FAR - ((progress + i * TUN_DZ) mod TUN_SPAN)."""
    rng = random.Random(3)
    rings = []
    for i in range(TUN_RINGS):
        spans = []
        stagger = 0.5 if i % 2 else 0.0
        for j in range(TUN_GLYPHS):
            a = 2 * math.pi * (j + stagger) / TUN_GLYPHS - math.pi / 2
            cx = TUN_RX * math.cos(a)
            cy = TUN_RY * math.sin(a) + TUN_SIZE * 0.35
            c = rng.choice("0011")
            op = 1.0 if c == "1" else 0.6
            spans.append(f'<tspan x="{lib.fmt(cx)}" y="{lib.fmt(cy)}" fill-opacity="{lib.fmt(op)}">{c}</tspan>')
        wraps = []
        for k in range(int(Z_LOOP / TUN_SPAN) + 2):
            target = k * TUN_SPAN - i * TUN_DZ
            if 0 < target < Z_LOOP:
                wraps.append(_solve_progress(target))
        skf, okf, fkf = [], [], []
        for t in sample_times(wraps):
            s = (progress(t) + i * TUN_DZ) % TUN_SPAN
            if any(abs(t - w) < 0.003 for w in wraps):
                s = TUN_SPAN - 1e-6 if s > TUN_SPAN / 2 else 0.0
            z = TUN_FAR - s
            sc = 1.0 / z
            fade_in = min(1.0, s / (2.0 * TUN_DZ))
            fade_out = min(1.0, (z - TUN_NEAR) / (1.0 * TUN_DZ))
            depth = 0.4 + 0.6 * (1.0 - (z - TUN_NEAR) / TUN_SPAN)
            op = max(0.0, min(1.0, fade_in * fade_out * depth))
            if fade_in < 1.0 or fade_out < 1.0:
                op = min(op, 0.0 if (s < 1e-5 or z < TUN_NEAR + 1e-5) else op)
            skf.append((t, round(sc, 4)))
            okf.append((t, round(op, 3)))
            fkf.append((t, CYAN if z < TUN_LIGHT_Z else CYAN_DIM))
        sf, sa = tl.transform(skf, kind="scale")
        of, oa = tl.attr("opacity", okf)
        ff, fa = tl.attr("fill", _collapse(fkf), calc="discrete")
        rail = (f'<ellipse rx="{lib.fmt(TUN_RX)}" ry="{lib.fmt(TUN_RY)}" fill="none" '
                f'stroke="{CYAN_DIM}" stroke-width="1.4" stroke-opacity="0.5"/>')
        rings.append(f'<g{of}><g{sf}>{rail}<text font-size="{TUN_SIZE}" text-anchor="middle"{ff}>'
                     f'{"".join(spans)}{fa}</text>{sa}</g>{oa}</g>')
    return (f'<g transform="translate({VP[0]} {VP[1]})" opacity="{lib.fmt(opacity)}">'
            f'{"".join(rings)}</g>')


def depth_glow():
    gid = lib.uid("glow")
    return (f'<radialGradient id="{gid}" cx="{VP[0] / W:.4f}" cy="{VP[1] / H:.4f}" r="0.5">'
            f'<stop offset="0" stop-color="{PURPLE}" stop-opacity="0.42"/>'
            f'<stop offset="0.35" stop-color="{PURPLE}" stop-opacity="0.14"/>'
            f'<stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')


def warp_streaks(tl):
    """radial streaks bursting out of the vanishing point while the tunnel
    surges: a group scaling up twice a second. Masked out over the name block
    so the headline never gets striped."""
    rng = random.Random(9)
    lines = []
    for k in range(16):
        a = 2 * math.pi * k / 16 + rng.uniform(-0.1, 0.1)
        r0 = rng.uniform(40, 90)
        r1 = r0 + rng.uniform(80, 200)
        op = rng.uniform(0.3, 0.7)
        lines.append(f'<line x1="{lib.fmt(r0 * math.cos(a))}" y1="{lib.fmt(r0 * math.sin(a))}" '
                     f'x2="{lib.fmt(r1 * math.cos(a))}" y2="{lib.fmt(r1 * math.sin(a))}" '
                     f'stroke="{CYAN}" stroke-width="2" stroke-opacity="{lib.fmt(op)}"/>')
    period = 0.5
    of, oa = tl.attr("opacity", [(0.0, 0.9), (period, 0.0)], begin=T_SURGE0, period=period)
    inner = f'<g{of}>{"".join(lines)}{oa}</g>'
    mid = lib.uid("warpmask")
    gid = lib.uid("warpfade")
    mask = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#000" stop-opacity="1"/>'
            f'<stop offset="0.68" stop-color="#000" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
            f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>'
            f'<rect x="0" y="80" width="{PANEL_X1 + 40}" height="250" fill="url(#{gid})"/></mask>')
    streaks = moving_group(tl, inner, translate=VP, scale=[(0.0, 0.3), (period, 3.4)],
                           spans=[(T_SURGE0, T_SURGE1)], begin=T_SURGE0, period=period, repeat=True)
    return f'{mask}<g mask="url(#{mid})">{streaks}</g>'


def vanish_ring(tl):
    """a ring that blooms out of the vanishing point as she disappears there"""
    t0 = T_RUN1 - 0.1
    sf, sa = tl.transform([(t0, 0.1), (t0 + 0.5, 2.6)], kind="scale")
    of, oa = tl.attr("stroke-opacity", [(t0, 0.9), (t0 + 0.5, 0.0)])
    vf, va = tl.visible([(t0, t0 + 0.5)])
    return (f'<g{vf} transform="translate({VP[0]} {VP[1]})"><g{sf}>'
            f'<circle r="40" fill="none" stroke="{CYAN}" stroke-width="2"{of}>{oa}</circle>'
            f'{sa}</g>{va}</g>')


# ---------------------------------------------------------------------------
# the figures
# ---------------------------------------------------------------------------

def glance_figure(tl):
    """She arrives at 2.0 from beyond the right edge (ghost entrance, rows
    materializing), glitches on arrival, holds with a slow breath, chromatic
    splits at 4.2 and 8.0, streak bursts at 3.4 and 6.6, and is cut at 9.5
    under a slice glitch. Returns (fragment, levels, x, y)."""
    glv = photo.levels("glance", 74, CW, CH, flip=True)
    gw, gh = glv.shape[1] * CW, glv.shape[0] * CH
    gx, gy = W - FIG_RIGHT_MARGIN - gw, FIG_BOTTOM - gh

    def full():
        return photo.materialize(tl, glv, gx, gy, CW, CH, T_ARRIVE, ARRIVE_DUR, seed=3)

    def flat():
        return glyph_rows(glv, gx, gy, CW, CH, flat=True)

    # the ghosts are interlaced (every other row) so three trailing copies
    # cost half as many elements and read as scan doubled afterimages
    half = glv.copy()
    half[1::2] = 0

    def ghost():
        return glyph_rows(half, gx, gy, CW, CH, flat=True)

    dx_from = W - gx + 20
    ease = (0.2, 0.7, 0.3, 1)
    entrance = photo.ghost_entrance(tl, full, T_ARRIVE, ARRIVE_DUR, dx_from, ghost_fn=ghost,
                                    repeat=True)

    def chroma_fn(fill):
        if fill is None:
            return entrance
        return photo.recolor(flat(), fill)

    figure = photo.chromatic(tl, chroma_fn, list(T_CHROMA))
    figure = photo.slice_glitch(tl, figure, gx, gy, gw, gh, [T_GLITCH_IN, T_TURN - 0.14],
                                seed=1, glitch_fn=flat)
    # a ground coloured cutout behind her, sliding in on the same curve as the
    # entrance and fading up as her rows land, so the tunnel's digits do not
    # cross the photograph (0.7 and grow 1: a trace of the tunnel still shows
    # through and defines her edge; sparse rows get no cutout, so no dark
    # steps above her hair)
    cut = photo.knockout(glv, gx, gy, CW, CH, grow=1, opacity=0.7, min_ink=3)
    of, oa = tl.attr("opacity", [(T_ARRIVE, 0.0), (T_ARRIVE + ARRIVE_DUR, 1.0)])
    cut = moving_group(tl, f"<g{of}>{cut}{oa}</g>",
                       translate=[(T_ARRIVE, (dx_from, 0)), (T_ARRIVE + ARRIVE_DUR, (0, 0))],
                       calc="spline", splines=photo._loop_splines(T_ARRIVE, ease))
    figure = cut + figure
    # breathing: a slow scale about her feet, four cycles per loop
    bcx, bcy = gx + gw / 2, gy + gh
    period = DUR / 4
    inner = f'<g transform="translate({lib.fmt(-bcx)} {lib.fmt(-bcy)})">{figure}</g>'
    breath = moving_group(tl, inner, translate=(bcx, bcy),
                          scale=[(0.0, 1.0), (period / 2, 1.015), (period, 1.0)],
                          period=period)
    vf, va = tl.visible([(T_ARRIVE, T_TURN)])
    frag = f"<g{vf}>{breath}{va}</g>"
    # data streaks: right going from any row; left going only from rows below
    # the name band, with a shorter travel, so none crosses the headline
    frag += photo.streaks(tl, glv, gx, gy, CW, CH, list(T_STREAKS), seed=11, n=6,
                          repeat=True, sides=(1,))
    low = glv.copy()
    low[: int(math.ceil((NAME_BAND_Y1 - gy) / CH))] = 0
    frag += photo.streaks(tl, low, gx, gy, CW, CH, list(T_STREAKS), seed=12, n=5,
                          repeat=True, sides=(-1,), travel=(60, 140))
    return frag, glv, gx, gy


def hand_figure(tl):
    """The hand materializes at 6.0 between the name block and her, over the
    floor, nearer the viewer than she is: a tight crop (palm and fingers), a
    fuller tone than hers, and a MAGENTA copy offset 3 px to the left under
    the cyan, so it separates as a nearer, chromatically split object instead
    of merging into her. It beckons four times at 2 Hz (still / rotated -7
    degrees about the wrist), holds, and fades 9.3 to 9.5, before the profile
    head appears. A ground coloured knockout (grow 1) under each pose covers
    the floor lines and her dissolved sleeve edge where they overlap; its
    opacity follows the materialize and the fade, so it never shows as a dark
    shape without a hand in it."""
    hlv = photo.levels("hand", 37, CW, CH, crop="hand_tight", black_cut=0.015, gamma=0.4,
                       contrast=(1.0, 97.0))
    hw, hh = hlv.shape[1] * CW, hlv.shape[0] * CH
    hx, hy = HAND_X, H - hh - 8
    halo = photo.knockout(hlv, hx, hy, CW, CH, grow=1, min_ink=2)
    t_mat_end = T_HAND + HAND_DUR
    fringe = photo.recolor(glyph_rows(hlv, hx - 3, hy, CW, CH, flat=True), MAGENTA)
    ink = glyph_rows(hlv, hx, hy, CW, CH)
    still = photo.materialize(tl, hlv, hx, hy, CW, CH, T_HAND, HAND_DUR, seed=4,
                              hold_until=t_mat_end, min_level=2)
    slots = tl.frames(2, 4, T_BECKON0, T_BECKON1)
    still_spans = [(T_HAND, T_BECKON0)] + slots[0] + [(T_BECKON1, T_HAND_GONE)]
    out = []
    # the halo fades up as the rows land and out with the hand
    hf, ha = tl.attr("opacity", [(T_HAND + 0.1, 0.0), (t_mat_end, 1.0),
                                 (T_HAND_FADE, 1.0), (T_HAND_GONE, 0.0)])
    vf, va = tl.visible(still_spans)
    out.append(f"<g{vf}><g{hf}>{halo}{ha}</g>{va}</g>")
    out.append(still)
    # the fringe fades in once the hand has landed
    ff, fa = tl.attr("opacity", [(t_mat_end, 0.0), (t_mat_end + 0.3, 0.55)])
    vf, va = tl.visible([(t_mat_end, T_BECKON0)] + slots[0] + [(T_BECKON1, T_HAND_GONE)])
    out.append(f"<g{vf}><g{ff}>{fringe}{fa}</g>{ink}{va}</g>")
    bent = halo + f'<g opacity="0.55">{fringe}</g>' + ink
    out.append(moving_group(tl, bent, rotate_kf=(-7, hx + hw * 0.5, hy + hh), spans=slots[1]))
    of, oa = tl.attr("opacity", [(T_HAND_FADE, 1.0), (T_HAND_GONE, 0.0)])
    vf, va = tl.visible([(T_HAND, T_HAND_GONE)])
    return f'<g{vf}><g{of}>{"".join(out)}{oa}</g>{va}</g>'


def profile_figure(tl, cx, cy):
    """At 9.5 the profile head (facing right, 420 px tall) takes her place
    under a slice glitch and a chromatic split. From 11.0 it scales toward
    the vanishing point while its cells rain off (dissolve_anim), gone by
    13.5. (cx, cy) is the centre it shares with her."""
    plv = photo.levels("profile", 60, CW, CH)
    pw, ph = plv.shape[1] * CW, plv.shape[0] * CH
    px, py = cx - pw / 2, cy - ph / 2

    def flat():
        return glyph_rows(plv, px, py, CW, CH, flat=True)

    plain = photo.dissolve_anim(tl, plv, px, py, CW, CH, T_RUN0, T_RUN1 - T_RUN0 - 0.3,
                                seed=9, steps=4, appear=T_TURN, fall=90, fall_dur=0.5,
                                repeat=True)

    def chroma_fn(fill):
        if fill is None:
            return plain
        return photo.recolor(flat(), fill)

    head = photo.chromatic(tl, chroma_fn, [T_TURN, 10.6])
    head = photo.slice_glitch(tl, head, px, py, pw, ph, [T_TURN], seed=8, glitch_fn=flat)
    # the run: scale 1.0 to 0.1 about her centre while the centre travels to
    # the vanishing point; the last residue fades as it lands
    inner = f'<g transform="translate({lib.fmt(-cx)} {lib.fmt(-cy)})">{head}</g>'
    run = moving_group(tl, inner, translate=[(T_RUN0, (cx, cy)), (T_RUN1, VP)],
                       scale=[(T_RUN0, 1.0), (T_RUN1, 0.1)],
                       calc="spline", splines=photo._loop_splines(T_RUN0, (0.5, 0.0, 0.8, 0.5)))
    of, oa = tl.attr("opacity", [(T_RUN1 - 0.4, 1.0), (T_RUN1, 0.0)])
    vf, va = tl.visible([(T_TURN, T_RUN1)])
    return f'<g{vf}><g{of}>{run}{oa}</g>{va}</g>'


# ---------------------------------------------------------------------------
# text, effects
# ---------------------------------------------------------------------------

def name_block(tl):
    static = []
    # dark panel so the name reads over the tunnel; it fades out before the
    # vanishing point so the tunnel's far end stays bright, and a vertical
    # mask softens its top and bottom edges where the ring rails cross it
    gid = lib.uid("namepanel")
    vid = lib.uid("panelfade")
    mid = lib.uid("panelmask")
    static.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
                  f'<stop offset="0" stop-color="{BG}" stop-opacity="0.92"/>'
                  f'<stop offset="0.7" stop-color="{BG}" stop-opacity="0.86"/>'
                  f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
                  f'<linearGradient id="{vid}" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                  f'<stop offset="0.2" stop-color="#fff" stop-opacity="1"/>'
                  f'<stop offset="0.8" stop-color="#fff" stop-opacity="1"/>'
                  f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="60" width="{PANEL_X1}" height="290">'
                  f'<rect x="0" y="60" width="{PANEL_X1}" height="290" fill="url(#{vid})"/></mask>')
    static.append(el("rect", {"x": 0, "y": 60, "width": PANEL_X1, "height": 290,
                              "fill": f"url(#{gid})", "mask": f"url(#{mid})"}))
    name = "FAWWAZ LAWAL"
    size, ls = 72, 6
    out = []
    # a dim ghost of the name sits under the reveal from the first frame
    out.append(f'<g font-weight="bold">{text(NX, 186, name, size, CYAN_DIM, opacity=0.16, ls=ls)}</g>')
    # typed identity line, 0.3 to 2.3 s; its cursor hands over to the follow
    # prompt at 7.0
    out.append(typed(tl, '> identity.load("FawwazLawal")', NX, 118, 14, CYAN_DIM, begin=0.3,
                     cps=15, cursor_end=T_PROMPT))
    # the big name, revealed letter by letter once the identity line has typed
    step = size * lib.MONO_ADV + ls
    t_name = 2.3
    wkf = [(0.0, 0)] + [(t_name + 0.05 * k, round(step * k + 12, 1)) for k in range(1, len(name) + 1)]
    title = chromatic_title(tl, name, NX, 186, size, bursts=list(NAME_BURSTS), ls=ls)
    out.append(clip_reveal(tl, title, NX - 12, 100, 110, wkf, repeat=True))
    # subtitle lines fade up
    of, oa = tl.attr("opacity", [(2.9, 0), (3.4, 1)])
    sub = (text(NX, 222, "SOFTWARE ENGINEER", 18, BONE, ls=8) +
           text(NX, 252, "GO  ·  SWIFT  ·  SWIFTUI  ·  SYSTEMS", 14, CYAN, ls=1))
    out.append(f"<g{of}>{sub}{oa}</g>")
    # the follow prompt
    out.append(typed(tl, "> follow her", NX, 298, 18, YELLOW, begin=T_PROMPT, cps=14))
    # everything cuts under the closing glitch so the loop can retype it
    vf, va = tl.visible([(0.0, T_CUT)])
    return f'{"".join(static)}<g{vf}>{"".join(out)}{va}</g>'


def glitch_slices(tl):
    """thin horizontal slices of magenta and cyan during the bursts (none at
    the loop cut: the camera jolt and the name cut carry the restart)"""
    out = []
    g_in, g_turn, g_out = T_GLITCH_IN, T_TURN, T_GLITCH_OUT
    specs = [
        (150, 6, MAGENTA, 0.45, [(g_in, g_in + 0.08), (g_turn, g_turn + 0.1),
                                 (g_out, g_out + 0.1)]),
        (338, 4, CYAN, 0.4, [(g_in + 0.04, g_in + 0.12), (g_turn + 0.06, g_turn + 0.18),
                             (g_out + 0.06, g_out + 0.14)]),
        (412, 9, MAGENTA, 0.3, [(g_turn + 0.1, g_turn + 0.2), (g_out + 0.12, g_out + 0.2)]),
        (72, 3, CYAN, 0.5, [(g_turn + 0.02, g_turn + 0.1), (g_out, g_out + 0.06)]),
    ]
    for y, h, fill, op, spans in specs:
        vf, va = tl.visible(spans)
        out.append(el("rect", f'x="0" y="{y}" width="{W}" height="{h}" fill="{fill}" '
                              f'fill-opacity="{op}"{vf}', anims=va))
    return "".join(out)


def hud(tl):
    """corner brackets and a status line that follows the story; the status
    cuts at T_CUT with the name block"""
    out = []
    m, L = 14, 26
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x0 = m if sx > 0 else W - m
        y0 = m if sy > 0 else H - m
        pts = f"{x0},{y0 + sy * L} {x0},{y0} {x0 + sx * L},{y0}"
        out.append(f'<polyline points="{pts}" fill="none" stroke="{CYAN}" stroke-width="1.5" '
                   f'stroke-opacity="0.55"/>')
    states = [
        ("sys // link established  :  listening", CYAN_DIM, [(0.6, T_ARRIVE)]),
        ("sys // presence detected  :  she sees you", CYAN_DIM, [(T_ARRIVE, T_TURN)]),
        ("sys // she is leaving  :  follow", CYAN_DIM, [(T_TURN, T_RUN1)]),
        ("sys // signal lost  :  she went deeper", MAGENTA, [(T_RUN1, T_CUT)]),
    ]
    for s, fill, spans in states:
        vf, va = tl.visible(spans)
        out.append(text(m + 34, H - 20, s, 11, fill, opacity=0.9, extra=vf.strip(), anims=va))
    vf, va = tl.visible([(T_RUN1 + 0.4, T_CUT)])
    out.append(text(W - m - 34, H - 20, "follow her down the page  ↓", 11, CYAN_DIM,
                    anchor="end", extra=vf.strip(), anims=va))
    return "".join(out)


# ---------------------------------------------------------------------------

def build(t=None):
    lib.reset_ids()
    tl = Timeline(DUR, t)
    # far field: dim across the loop seam (never black), full from 0.8 s
    far = []
    far.append(depth_glow())
    far.append(rain(tl, 330, 870, 0, VP[1] + 20, 6, seed=41, opacity=0.2, speed=(30, 90),
                    size=10, length=(6, 12)))
    far.append(hero_tunnel(tl, opacity=0.95))
    far.append(hero_floor(tl))
    far.append(warp_streaks(tl))
    far.append(vanish_ring(tl))
    of, oa = tl.attr("opacity", [(0.0, FAR_SEAM), (0.8, 1.0), (T_FADE0, 1.0), (DUR, FAR_SEAM)])
    body = [f'<g{of}>{"".join(far)}{oa}</g>']

    her, glv, gx, gy = glance_figure(tl)
    gcx = gx + glv.shape[1] * CW / 2
    gcy = gy + glv.shape[0] * CH / 2
    body.append(profile_figure(tl, gcx, gcy))
    body.append(her)
    body.append(hand_figure(tl))
    body.append(name_block(tl))
    body.append(hud(tl))
    body.append(glitch_slices(tl))
    # camera jolt on the glitch bursts; back to rest exactly at the loop end
    jkf = [(0.0, (0, 0))]
    for g in (T_TURN, T_GLITCH_OUT, T_CUT - 0.05):
        jkf += [(g, (-8, 3)), (g + 0.06, (5, -2)), (g + 0.12, (0, 0))]
    jkf.append((DUR, (0, 0)))
    jf, ja = tl.transform(jkf, calc="discrete")
    scene = f'<g{jf}>{"".join(body)}{ja}</g>'
    return svg(W, H, scene + vignette(W, H) + scanlines(W, H), "FawwazLawal // netrunner")


SCENES = {"hero": build}
