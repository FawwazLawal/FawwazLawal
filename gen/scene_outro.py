"""S5 outro: assets/outro.svg, 1200 x 320, 12 s loop (DESIGN.md section 4, v2).

The front visor photograph (source/front-visor.jpg through photo.levels, 46
rows at cw 4.4 x ch 6.5, 300 px tall, with the shadow pass in photo.TONE so
her shadow side keeps its cheek and jaw) stands centred in a perspective
corridor with a purple depth glow behind her and thin binary rain at the
edges.

  0.1 to 1.5   her rows materialize in a seeded random order, a few flickering,
               the visor band in yellow; the glow behind her comes up with her
  2.0          one chromatic split (magenta and cyan copies kicked apart for
               160 ms) and a burst of twelve data streaks off her silhouette,
               kept inside the clearing between the two text columns
  3.3          a slice glitch: the figure cut into horizontal bands shifted
               sideways for 160 ms (the band copy keeps every ink level, so
               the figure shifts rather than thins)
  4.0 to 7.0   she dissolves: cells drop in eleven seeded groups (top last)
               and fall as rain off the figure, each group drawing a dim
               vertical trail from the moment it drops (a group still standing
               is drawn plain); the glow dies with her and the rain closes
               over the clearing
  8.0          the closing line types across the clearing below the horizon,
               17 px BONE with the yellow cursor, which blinks after; the log
               dims to half once its last line has typed so the closing line
               holds the frame
  11.0         burst: the name takes its chromatic kick and the closing line
               splits magenta and cyan for 160 ms; every text, the prompt
               included, fades before 12 s so the loop closes on the empty
               corridor and she returns

Every animated value goes through lib.Timeline, so build(t) freezes exactly.
Every track repeats over the loop (the photo helpers run with repeat=True), so
the second and later passes look exactly like the first.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lib  # noqa: E402
from lib import (Timeline, glyph_rows, chromatic_title, rain, floor_grid, tunnel,  # noqa: E402
                 scanlines, vignette, svg, typed, text, fmt,
                 CYAN, CYAN_DIM, MAGENTA, BONE, PURPLE, GRID, BG)
import photo  # noqa: E402

W, H = 1200, 320
DUR = 12.0
VP = (600, 150)
FX = 600.0

ROWS = 46
CW, CH = 4.4, 6.5

T_MAT = 0.1            # materialize start
MAT_DUR = 1.4
T_CHROMA = 2.0
T_STREAK = 2.0
T_SLICE = 3.3
T_DISS = 4.0
DISS_DUR = 2.8         # the last group drops at 6.8 and is gone by 7.7
FALL_DUR = 0.9
T_TYPE = 8.0
T_BURST = 11.0
T_LOG_DIM = T_TYPE + 2.8   # the log drops to half ink once its last line has typed
T_FADE = 11.4          # the text fades out before the loop seam
STREAK_ZONE = (440, 760)   # streaks stay between the two text columns
CLOSING_Y = 212
CLOSING_SIZE = 17
CLOSING_LS = 2

LEFT_X = 64
RIGHT_X = 836
CLOSING = "> session closed. jack out when ready"


def figure_levels():
    return photo.levels("front", ROWS, CW, CH)


def depth_glow(tl, cx, cy):
    """purple glow behind her: rises with the materialize, dies with the
    dissolve, stays dark until she returns"""
    gid = lib.uid("glow")
    grad = (f'<radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{PURPLE}" stop-opacity="0.8"/>'
            f'<stop offset="0.5" stop-color="{PURPLE}" stop-opacity="0.3"/>'
            f'<stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>')
    kf = [(0.0, 0.0), (T_MAT, 0.0), (T_MAT + MAT_DUR, 0.55), (T_DISS, 0.55),
          (T_DISS + DISS_DUR, 0.0), (DUR, 0.0)]
    of, oa = tl.attr("opacity", kf)
    return grad + (f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="250" ry="190" '
                   f'fill="url(#{gid})"{of}>{oa}</ellipse>')


def horizon(tl):
    """a faint cyan glow at the vanishing point, a little brighter while she
    dissolves into the system"""
    gid = lib.uid("hz")
    grad = (f'<radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.5"/>'
            f'<stop offset="0.3" stop-color="{CYAN}" stop-opacity="0.2"/>'
            f'<stop offset="0.6" stop-color="{CYAN}" stop-opacity="0.06"/>'
            f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>')
    kf = [(0.0, 0.45), (T_DISS, 0.45), (T_DISS + DISS_DUR, 0.65), (T_TYPE, 0.45), (DUR, 0.45)]
    of, oa = tl.attr("opacity", kf)
    return grad + (f'<ellipse cx="{fmt(VP[0])}" cy="{fmt(VP[1])}" rx="240" ry="40" '
                   f'fill="url(#{gid})"{of}>{oa}</ellipse>')


TEXT_ZONES = ((LEFT_X - 10, 440), (RIGHT_X - 10, 1050))


def rain_clearing(x):
    """rain opacity per column: full at the edges, thin at the centre so she
    stands in a clearing, and halved over the two text columns"""
    d = abs(x - FX) / 400.0
    op = 0.25 + 0.75 * min(1.0, d * d)
    if any(a <= x <= b for a, b in TEXT_ZONES):
        op *= 0.45
    return op


def rain_holes(body, boxes):
    """clip `body` to the frame minus the given (x0, y0, x1, y1) boxes (an
    evenodd path), so no rain column or tunnel ring crosses the typed text
    and a bright glyph cannot sit against the log like a stray character"""
    cid = lib.uid("hole")
    d = f"M0 0h{fmt(W)}v{fmt(H)}h{fmt(-W)}z"
    for x0, y0, x1, y1 in boxes:
        d += f"M{fmt(x0)} {fmt(y0)}h{fmt(x1 - x0)}v{fmt(y1 - y0)}h{fmt(-(x1 - x0))}z"
    return (f'<clipPath id="{cid}"><path d="{d}" clip-rule="evenodd"/></clipPath>'
            f'<g clip-path="url(#{cid})">{body}</g>')


# the two text boxes the edge rain and the tunnel stay out of: the name
# block and the log
RAIN_HOLES = ((LEFT_X - 12, 84, 436, 192), (RIGHT_X - 36, 86, 1052, 206))


def closing_rain(tl):
    """the clearing closes after she is gone: a second rain layer over the
    centre fades in once the last cells have fallen and out before the seam"""
    body = rain(tl, 440, 760, 0, H, 10, seed=33, opacity=1.0, speed=(35, 90), size=10,
                length=(6, 12))
    kf = [(0.0, 0.0), (T_DISS + DISS_DUR, 0.0), (T_TYPE + 0.6, 0.3), (T_FADE, 0.3), (DUR, 0.0)]
    of, oa = tl.attr("opacity", kf)
    return f"<g{of}>{body}{oa}</g>"


def figure(tl, lv, gx, gy):
    """her glyph grid with every effect: materialize, chromatic split, slice
    glitch, breathing scale, the dissolve into rain, and the knockout
    silhouette that keeps the floor lines out of her digits"""
    gw, gh = lv.shape[1] * CW, lv.shape[0] * CH
    cx, cy = gx + gw / 2, gy + gh / 2

    def full():
        return photo.materialize(tl, lv, gx, gy, CW, CH, T_MAT, MAT_DUR, seed=7, flicker=4,
                                 hold_until=T_DISS)

    def flat():
        return glyph_rows(lv, gx, gy, CW, CH, flat=True)

    def plain():
        # every ink level, so the glitch bands carry her dim hair, shadow
        # cheek and collar sideways instead of dropping them
        return glyph_rows(lv, gx, gy, CW, CH)

    def chroma_fn(fill):
        if fill is None:
            return full()
        return photo.recolor(flat(), fill)

    body = photo.chromatic(tl, chroma_fn, [T_CHROMA])
    body = photo.slice_glitch(tl, body, gx, gy, gw, gh, [T_SLICE], seed=5, glitch_fn=plain)
    body += photo.dissolve_anim(tl, lv, gx, gy, CW, CH, T_DISS, DISS_DUR, seed=9, steps=11,
                                top_last=True, fall=140, fall_dur=FALL_DUR, appear=T_DISS,
                                repeat=True, trail=2, trail_rows=2.0,
                                trail_opacity=(0.4, 0.16))

    # breathing: a slow scale about her centre, two breaths per loop
    sf, sa = tl.transform([(0.0, 1.0), (3.0, 1.015), (6.0, 1.0), (9.0, 1.015), (12.0, 1.0)],
                          kind="scale", calc="spline",
                          splines=[(0.42, 0, 0.58, 1)] * 4)
    return (f'<g transform="translate({fmt(cx)} {fmt(cy)})"><g{sf}>'
            f'<g transform="translate({fmt(-cx)} {fmt(-cy)})">{body}</g>{sa}</g></g>')


def halo(tl, lv, gx, gy):
    """the ground coloured silhouette behind her keeps the floor and tunnel
    out of her digits; it sits under the depth glow so it reads as a shadow in
    the glow, not a hole. Two paths feather its edge (grown two cells at a
    lower opacity, grown one cell on top) so no stepped rim shows against the
    glow. It comes up with the rows and goes with the dissolve."""
    outer = photo.knockout(lv, gx, gy, CW, CH, grow=2, opacity=0.45)
    inner = photo.knockout(lv, gx, gy, CW, CH, grow=1, opacity=0.4)
    kf = [(0.0, 0.0), (T_MAT, 0.0), (T_MAT + MAT_DUR, 1.0), (T_DISS, 1.0),
          (T_DISS + DISS_DUR * 0.8, 0.0), (DUR, 0.0)]
    of, oa = tl.attr("opacity", kf)
    return f"<g{of}>{outer}{inner}{oa}</g>"


def text_fade(tl):
    """the fade every typed text shares before the loop seam"""
    return tl.attr("opacity", [(0.0, 1.0), (T_FADE, 1.0), (DUR - 0.15, 0.0), (DUR, 0.0)])


def name_block(tl):
    out = []
    # the prompt fades with the log before the seam and retypes at 0.4 as a
    # new session (its typing clip alone would blink off at the seam)
    pf, pa = text_fade(tl)
    out.append(f"<g{pf}>" + typed(tl, "> netrunner.disconnect()", LEFT_X, 100, 13, CYAN_DIM,
                                  begin=0.4, cps=24, cursor=False, opacity=0.9) + f"{pa}</g>")
    out.append(chromatic_title(tl, "FAWWAZ LAWAL", LEFT_X, 150, 34, bursts=[T_BURST], ls=6))
    out.append(text(LEFT_X, 178, "SOFTWARE ENGINEER // SIGNING OFF", 12, BONE, ls=4,
                    opacity=0.9))
    return "".join(out)


def closing_line(tl):
    """the closing line types across the clearing where she stood, below the
    horizon and clear of the log rows, in BONE with the yellow cursor; at the
    burst its magenta and cyan copies kick apart"""
    size = CLOSING_SIZE
    cw = size * lib.MONO_ADV + CLOSING_LS
    x = FX - len(CLOSING) * cw / 2
    y = CLOSING_Y

    def copy_fn(fill):
        if fill is None:
            return typed(tl, CLOSING, x, y, size, BONE, begin=T_TYPE, cps=22, opacity=0.95,
                         ls=CLOSING_LS)
        return typed(tl, CLOSING, x, y, size, fill, begin=T_TYPE, cps=22, cursor=False,
                     opacity=0.95, ls=CLOSING_LS)

    body = photo.chromatic(tl, copy_fn, [T_BURST])
    of, oa = text_fade(tl)
    return f"<g{of}>{body}{oa}</g>"


def status_lines(tl):
    """right column: a session log that follows the story through the loop"""
    lines = [("> session ....... ", "open", 0.8),
             ("> visor ......... ", "locked", T_MAT + MAT_DUR + 0.3),
             ("> uplink ........ ", "closing", T_DISS + 0.3),
             ("> trace ......... ", "none", T_DISS + DISS_DUR + 0.6),
             ("> buffer ........ ", "flushed", T_TYPE + 2.2)]
    size = 13
    cw = size * lib.MONO_ADV
    cps = 40
    out = []
    for i, (lead, val, t0) in enumerate(lines):
        y = 104 + i * 22
        out.append(typed(tl, lead, RIGHT_X, y, size, CYAN_DIM, begin=t0, cps=cps,
                         cursor=False, opacity=0.9))
        out.append(typed(tl, val, RIGHT_X + len(lead) * cw, y, size, CYAN,
                         begin=t0 + len(lead) / cps, cps=cps, cursor=False, opacity=0.85))
    # once the last line has typed the log drops to half ink, so the closing
    # line and its cursor are the only text at full strength
    of, oa = tl.attr("opacity", [(0.0, 1.0), (T_LOG_DIM, 1.0), (T_LOG_DIM + 0.5, 0.5),
                                 (T_FADE, 0.5), (DUR - 0.15, 0.0), (DUR, 0.0)])
    return f'<g{of}>{"".join(out)}{oa}</g>'


def build(t=None):
    lib.reset_ids()
    tl = Timeline(DUR, t)
    lv = figure_levels()
    gw, gh = lv.shape[1] * CW, lv.shape[0] * CH
    gx = FX - gw / 2
    gy = (H - gh) / 2
    body = []
    body.append(rain_holes(rain(tl, 0, W, 0, H, 28, seed=21, opacity=0.32, speed=(30, 95),
                                size=10, length=(6, 13), col_opacity=rain_clearing),
                           RAIN_HOLES))
    body.append(horizon(tl))
    body.append(rain_holes(tunnel(tl, W, H, VP, n_rings=6, depth=6.0, speed=0.4, seed=4,
                                  size=11, opacity=0.4), RAIN_HOLES))
    body.append(floor_grid(tl, W, H, VP, n_lines=8, speed=0.5, color=GRID, opacity=0.85,
                           rung_color=CYAN_DIM, rung_width=1.0))
    body.append(halo(tl, lv, gx, gy))
    body.append(depth_glow(tl, FX, gy + gh * 0.5))
    body.append(closing_rain(tl))
    body.append(figure(tl, lv, gx, gy))
    body.append(photo.streaks(tl, lv, gx, gy, CW, CH, [T_STREAK], seed=11, n=12,
                              length=(30, 120), repeat=True, x_range=STREAK_ZONE))
    body.append(closing_line(tl))
    body.append(name_block(tl))
    body.append(status_lines(tl))
    body.append(vignette(W, H, strength=0.7))
    body.append(scanlines(W, H))
    return svg(W, H, "".join(body), "NETRUNNER outro: session closed")


SCENES = {"outro": build}
