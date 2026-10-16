"""Shared SVG generation library for the NETRUNNER profile scenes.

Every animation goes through a Timeline. With t=None the Timeline emits SMIL
elements (<animate>, <animateTransform>, <set>). With a float t it evaluates every
keyframe track at that time and emits static attribute values only, so a frozen
frame can be rasterized with qlmanage and inspected.

Conventions:
  * Keyframe times are seconds. Repeating tracks live on [0, period] (period defaults
    to the scene loop length) and wrap; non repeating tracks run once and hold.
  * `begin` shifts a track in time. Negative begin is allowed for repeating tracks
    and means "already in progress at document time 0" (SMIL supports this).
  * Ink opacity on text is written as fill-opacity, so the plain `opacity`
    attribute stays free for visibility tracks (Timeline.visible).
"""

import math
import random
import numpy as np

PALETTE = {
    "BG": "#05050a",
    "BG2": "#0b0b16",
    "GRID": "#15152a",
    "CYAN": "#00f0ff",
    "CYAN_DIM": "#0a7f8a",
    "HILITE": "#dffcff",
    "MAGENTA": "#ff2a6d",
    "YELLOW": "#fcee0a",
    "PURPLE": "#7a2cff",
    "BONE": "#e8e6f0",
}
BG = PALETTE["BG"]
BG2 = PALETTE["BG2"]
GRID = PALETTE["GRID"]
CYAN = PALETTE["CYAN"]
CYAN_DIM = PALETTE["CYAN_DIM"]
HILITE = PALETTE["HILITE"]
MAGENTA = PALETTE["MAGENTA"]
YELLOW = PALETTE["YELLOW"]
PURPLE = PALETTE["PURPLE"]
BONE = PALETTE["BONE"]

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

# Monospace advance width as a fraction of font-size. SF Mono / Menlo are close to
# 0.6; glyph grids lock the row width with textLength anyway, this is only used to
# pick sensible default cell widths.
MONO_ADV = 0.6

# Glyph ink levels (DESIGN.md section 2): index by level 0..3. Level 4 is the
# figure's visor row: a YELLOW "1" at full opacity (figure.render_pose marks it).
# Level 5 is the photo pipeline's highlight: a HILITE "1" at full opacity for
# the brightest few percent of cells. Grids that never use 5 render as before.
LEVEL_CHAR = {0: " ", 1: "0", 2: "0", 3: "1", 4: "1", 5: "1"}
LEVEL_FILL = {1: CYAN_DIM, 2: CYAN, 3: CYAN, 4: YELLOW, 5: HILITE}
LEVEL_OPACITY = {1: 0.38, 2: 0.55, 3: 0.85, 4: 1.0, 5: 1.0}
MAX_LEVEL = 5

_ID_COUNTER = [0]


def reset_ids():
    """Reset the unique id counter so repeated builds are byte identical."""
    _ID_COUNTER[0] = 0


def uid(prefix="i"):
    _ID_COUNTER[0] += 1
    return f"{prefix}{_ID_COUNTER[0]}"


# ----------------------------------------------------------------------------
# formatting helpers
# ----------------------------------------------------------------------------

def fmt(v):
    """Format a number, tuple or string for an SVG attribute."""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        if not math.isfinite(v):
            return "0"
        s = f"{v:.3f}".rstrip("0").rstrip(".")
        if s in ("", "-0", "-"):
            s = "0"
        return s
    if isinstance(v, (tuple, list, np.ndarray)):
        return " ".join(fmt(x) for x in v)
    return str(v)


def _fmt_key(k):
    s = f"{k:.5f}".rstrip("0").rstrip(".")
    return s if s else "0"


def esc(s):
    """Escape text content for XML."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def esc_attr(s):
    return esc(s).replace('"', "&quot;")


def _lerp(a, b, f):
    if isinstance(a, str) or isinstance(b, str):
        return a if f < 1.0 else b
    if isinstance(a, (tuple, list)):
        return tuple(_lerp(x, y, f) for x, y in zip(a, b))
    return a + (b - a) * f


def _bezier_y_at_x(spline, x):
    """Evaluate a CSS style cubic bezier (x1 y1 x2 y2) at horizontal position x."""
    x1, y1, x2, y2 = spline
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        bx = 3 * (1 - mid) ** 2 * mid * x1 + 3 * (1 - mid) * mid ** 2 * x2 + mid ** 3
        if bx < x:
            lo = mid
        else:
            hi = mid
    u = (lo + hi) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3


def _eval_track(kfs, u, calc, splines):
    """Evaluate a sorted keyframe list at local time u (clamped to the ends)."""
    if u <= kfs[0][0]:
        return kfs[0][1]
    if u >= kfs[-1][0]:
        return kfs[-1][1]
    for i in range(len(kfs) - 1):
        t0, v0 = kfs[i]
        t1, v1 = kfs[i + 1]
        if t0 <= u < t1:
            if calc == "discrete":
                return v0
            f = (u - t0) / (t1 - t0)
            if calc == "spline":
                sp = splines[i] if splines and i < len(splines) else (0.42, 0, 0.58, 1)
                if isinstance(sp, str):
                    sp = tuple(float(x) for x in sp.replace(",", " ").split())
                f = _bezier_y_at_x(sp, f)
            return _lerp(v0, v1, f)
    return kfs[-1][1]


def _spline_str(sp):
    if isinstance(sp, str):
        return sp
    return " ".join(fmt(x) for x in sp)


# ----------------------------------------------------------------------------
# Timeline
# ----------------------------------------------------------------------------

class Timeline:
    """Keyframe tracks that either emit SMIL or evaluate at a fixed time."""

    def __init__(self, dur, t=None):
        self.dur = float(dur)
        self.t = None if t is None else float(t)
        self.freeze = t is not None

    # -- core ---------------------------------------------------------------
    def _track(self, keyframes, calc, begin, repeat, period, splines):
        """Normalise a track. Returns a dict describing it, or None if static.

        keys: static (value), kfs, t0, span, begin, mode ('repeat'|'once'|'set')
        """
        kfs = sorted(((float(t), v) for t, v in keyframes), key=lambda k: k[0])
        if not kfs:
            return None
        if len(kfs) == 1:
            return {"static": kfs[0][1], "mode": "const", "kfs": kfs}
        if calc not in ("linear", "discrete", "spline"):
            raise ValueError(f"unknown calcMode {calc}")
        if repeat:
            p = float(period if period else self.dur)
            if kfs[0][0] > 0:
                kfs.insert(0, (0.0, kfs[0][1]))
            if kfs[-1][0] > p + 1e-9:
                raise ValueError(f"keyframe time {kfs[-1][0]} exceeds period {p}")
            if kfs[-1][0] < p:
                kfs.append((p, kfs[-1][1]))
            else:
                kfs[-1] = (p, kfs[-1][1])
            return {"static": kfs[0][1], "mode": "repeat", "kfs": kfs,
                    "t0": 0.0, "span": p, "begin": float(begin),
                    "calc": calc, "splines": splines}
        t0 = kfs[0][0]
        tn = kfs[-1][0]
        if tn - t0 <= 1e-9:
            return {"static": kfs[0][1], "mode": "set", "kfs": kfs,
                    "t0": t0, "span": 0.0, "begin": float(begin),
                    "final": kfs[-1][1], "calc": calc, "splines": splines}
        return {"static": kfs[0][1], "mode": "once", "kfs": kfs,
                "t0": t0, "span": tn - t0, "begin": float(begin),
                "calc": calc, "splines": splines}

    def _value_at(self, tr):
        """Evaluate a normalised track at self.t."""
        t = self.t
        if tr["mode"] == "const":
            return tr["static"]
        if tr["mode"] == "set":
            return tr["final"] if t >= tr["begin"] + tr["t0"] else tr["static"]
        if tr["mode"] == "repeat":
            if t < tr["begin"]:
                return tr["static"]
            u = (t - tr["begin"]) % tr["span"]
            return _eval_track(tr["kfs"], u, tr["calc"], tr["splines"])
        u = t - tr["begin"]
        return _eval_track(tr["kfs"], u, tr["calc"], tr["splines"])

    def _smil(self, tag, tr, head):
        """Build the SMIL element for a normalised track. `head` is the start of
        the tag including attributeName/type attributes."""
        if tr["mode"] == "const":
            return ""
        if tr["mode"] == "set":
            return (f'<set {head} to="{fmt(tr["final"])}" '
                    f'begin="{fmt(tr["begin"] + tr["t0"])}s" fill="freeze"/>')
        kfs = tr["kfs"]
        span = tr["span"]
        keys = [(t - tr["t0"]) / span for t, _ in kfs]
        keys[0] = 0.0
        keys[-1] = 1.0
        vals = ";".join(fmt(v) for _, v in kfs)
        kt = ";".join(_fmt_key(k) for k in keys)
        parts = [f"<{tag} {head}", f'values="{vals}"', f'keyTimes="{kt}"',
                 f'calcMode="{tr["calc"]}"']
        if tr["calc"] == "spline":
            n = len(kfs) - 1
            sp = tr["splines"] or []
            splines = [(_spline_str(sp[i]) if i < len(sp) else "0.42 0 0.58 1") for i in range(n)]
            parts.append(f'keySplines="{";".join(splines)}"')
        parts.append(f'dur="{fmt(span)}s"')
        b = tr["begin"] + tr["t0"]
        parts.append(f'begin="{fmt(b)}s"')
        if tr["mode"] == "repeat":
            parts.append('repeatCount="indefinite"')
        else:
            parts.append('fill="freeze"')
        return " ".join(parts) + "/>"

    # -- public ------------------------------------------------------------
    def attr(self, name, keyframes, calc="linear", begin=0.0, repeat=True,
             period=None, splines=None):
        """keyframes: list[(time, value)]. Returns (static_attr_fragment, animate_element).

        In freeze mode the fragment holds the value at t and the element is ''.
        In animate mode the fragment holds the first value and the element is the
        <animate> string (or <set> for a single step)."""
        tr = self._track(keyframes, calc, begin, repeat, period, splines)
        if tr is None:
            return "", ""
        if self.freeze or tr["mode"] == "const":
            v = self._value_at(tr) if self.freeze else tr["static"]
            return f' {name}="{fmt(v)}"', ""
        frag = f' {name}="{fmt(tr["static"])}"'
        return frag, self._smil("animate", tr, f'attributeName="{name}"')

    def transform(self, keyframes, kind="translate", calc="linear", begin=0.0,
                  repeat=True, period=None, splines=None):
        """Like attr() but for a transform of one kind: translate, scale, rotate.
        Values: translate (x, y); scale s or (sx, sy); rotate a or (a, cx, cy)."""
        tr = self._track(keyframes, calc, begin, repeat, period, splines)
        if tr is None:
            return "", ""
        if self.freeze or tr["mode"] == "const":
            v = self._value_at(tr) if self.freeze else tr["static"]
            return f' transform="{kind}({fmt(v)})"', ""
        frag = f' transform="{kind}({fmt(tr["static"])})"'
        return frag, self._smil("animateTransform", tr,
                                f'attributeName="transform" type="{kind}"')

    def visible(self, spans):
        """spans: list[(start, end)] during which the element is visible.
        Returns (' opacity="0|1"', animate element) using discrete opacity."""
        clean = []
        for a, b in spans:
            a = max(0.0, float(a))
            b = min(self.dur, float(b))
            if b > a + 1e-9:
                clean.append((a, b))
        clean.sort()
        merged = []
        for a, b in clean:
            if merged and a <= merged[-1][1] + 1e-9:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        if not merged:
            return ' opacity="0"', ""
        if len(merged) == 1 and merged[0][0] <= 1e-9 and merged[0][1] >= self.dur - 1e-9:
            return ' opacity="1"', ""
        kfs = []
        cur = 1 if merged[0][0] <= 1e-9 else 0
        kfs.append((0.0, cur))
        for a, b in merged:
            if a > 1e-9:
                kfs.append((a, 1))
            if b < self.dur - 1e-9:
                kfs.append((b, 0))
        return self.attr("opacity", kfs, calc="discrete")

    def frames(self, n_frames, fps, begin, end):
        """Visibility spans for frame flipping. Returns a list indexed by frame
        with the list of (start, end) spans during which that frame shows, cycling
        through the frames at fps between begin and end."""
        out = [[] for _ in range(n_frames)]
        step = 1.0 / fps
        k = 0
        t = float(begin)
        while t < end - 1e-9:
            t2 = min(end, t + step)
            out[k % n_frames].append((t, t2))
            k += 1
            t = t + step
        return out

    def phase(self, period, begin=0.0):
        """Fraction [0, 1) of a repeating period elapsed at t (freeze helper)."""
        if not self.freeze:
            return 0.0
        return ((self.t - begin) % period) / period


# ----------------------------------------------------------------------------
# element helpers
# ----------------------------------------------------------------------------

def el(tag, attrs, children="", anims=""):
    """Build an element. attrs is a dict (None values skipped) or a raw string
    of attribute fragments. children and anims are inner markup."""
    if isinstance(attrs, dict):
        a = "".join(f' {k}="{esc_attr(fmt(v))}"' for k, v in attrs.items() if v is not None)
    else:
        a = attrs or ""
        if a and not a.startswith(" "):
            a = " " + a
    inner = children + anims
    if inner:
        return f"<{tag}{a}>{inner}</{tag}>"
    return f"<{tag}{a}/>"


def text(x, y, s, size, fill, opacity=1, ls=0, anchor="start", extra="", anims=""):
    """A <text> element. Ink opacity uses fill-opacity so `opacity` stays free
    for visibility animation. `extra` is raw attribute text."""
    a = f' x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}" fill="{fill}"'
    if opacity != 1:
        a += f' fill-opacity="{fmt(opacity)}"'
    if ls:
        a += f' letter-spacing="{fmt(ls)}"'
    if anchor != "start":
        a += f' text-anchor="{anchor}"'
    if " " in s:
        a += ' xml:space="preserve"'
    if extra:
        a += " " + extra.strip()
    return f"<text{a}>{esc(s)}{anims}</text>"


_LEVEL_LUT = np.array([LEVEL_CHAR[i] for i in range(MAX_LEVEL + 1)])


def glyph_rows(levels, x, y, cw, ch, max_width=None, size=None, anims="", flat=False,
               min_level=1):
    """Emit a glyph grid. levels: int array HxW with values 0..5 (4 is the
    YELLOW visor row, see figure.py; 5 is the HILITE photo highlight; grids with
    0..3 render exactly as before).
    One <text> per ink level per row, textLength locked so the grid stays
    aligned regardless of the viewer's monospace font. Rows with no ink are skipped.
    Returns a <g>.

    Element budget helpers (a frame of a 48 column figure costs about 240 <text>
    elements in the default mode):
      flat=True   one <text> per row: every cyan level is drawn as CYAN at full
                  opacity and only the character ("1" bright, "0" mid) carries
                  the depth; the dim edge cells (level 1) are dropped, since at
                  full opacity they fatten the silhouette until limbs merge; the
                  visor row still gets its own yellow text, and highlight
                  cells (level 5) their own HILITE text.
      min_level   drop cells below this level (2 drops the dim edge cells)."""
    lv = np.asarray(levels)
    if lv.ndim != 2:
        raise ValueError("levels must be HxW")
    lv = np.clip(lv.astype(int), 0, MAX_LEVEL)
    if flat:
        min_level = max(min_level, 2)
    if min_level > 1:
        lv = np.where(lv < min_level, 0, lv)
    hgt, wid = lv.shape
    if max_width is not None and wid * cw > max_width:
        cw = max_width / wid
    fs = size if size else ch
    # one <g> per ink level carries the shared fill, opacity and font size; each
    # row is a <text> with leading blanks folded into its x offset, so a sparse
    # grid costs little. Output: <g><g level 1>..</g><g level 2>..</g>..</g>
    if flat:
        classes = ((3, (lv >= 1) & (lv <= 3)), (4, lv == 4), (5, lv == 5))
    else:
        classes = tuple((level, lv == level) for level in (1, 2, 3, 4, 5))
    groups = []
    for level, cls in classes:
        rows = []
        for r in range(hgt):
            row = lv[r]
            mask = cls[r]
            if not mask.any():
                continue
            chars = np.where(mask, _LEVEL_LUT[row], " ")
            s = "".join(chars.tolist()).rstrip()
            lead = len(s) - len(s.lstrip())
            s = s[lead:]
            n = len(s)
            by = y + r * ch + ch * 0.8
            # xml:space must sit on the <text> itself: WebKit ignores it when it
            # is inherited from the group and collapses the interior blanks, and
            # textLength then stretches the remaining glyphs over the gap.
            rows.append(f'<text x="{fmt(x + lead * cw)}" y="{fmt(by)}" '
                        f'textLength="{fmt(n * cw)}" lengthAdjust="spacingAndGlyphs" '
                        f'xml:space="preserve">{s}</text>')
        if rows:
            groups.append(f'<g fill="{LEVEL_FILL[level]}" fill-opacity="{fmt(LEVEL_OPACITY[level])}" '
                          f'font-size="{fmt(fs)}">{"".join(rows)}</g>')
    return f"<g>{''.join(groups)}{anims}</g>"


def chromatic_title(tl, s, x, y, size, bursts, ls=6, anchor="start", rest=2, extra=""):
    """Headline with a chromatic split: MAGENTA copy offset left, CYAN copy offset
    right, BONE on top. The offsets kick out in short bursts at the given times.
    `extra` is raw attribute text added to all three copies (for example a
    textLength lock so the title is the same width in every monospace font)."""
    mag = [(0.0, -rest)]
    cya = [(0.0, rest)]
    for b in bursts:
        b = float(b)
        if b < 0 or b >= tl.dur:
            continue
        for dt, dm, dc in ((0.0, -8, 8), (0.05, 4, -5), (0.1, -6, 6), (0.16, -rest, rest)):
            if b + dt < tl.dur:
                mag.append((b + dt, dm))
                cya.append((b + dt, dc))
    out = []
    ex = (" " + extra.strip()) if extra else ""
    for fill, kfs, op in ((MAGENTA, mag, 0.9), (CYAN, cya, 0.9)):
        frag, anim = tl.attr("dx", kfs, calc="discrete")
        out.append(text(x, y, s, size, fill, opacity=op, ls=ls, anchor=anchor,
                        extra=(frag.strip() + ex).strip(), anims=anim))
    out.append(text(x, y, s, size, BONE, ls=ls, anchor=anchor, extra=ex.strip()))
    return f'<g font-weight="bold">{"".join(out)}</g>'


def clip_reveal(tl, children, x, y, h, width_kf, calc="discrete", begin=0.0, repeat=False):
    """Wrap `children` in a clipPath rect at (x, y) of height h whose width
    follows width_kf ([(t, w)] keyframes through tl.attr). Animated: the rect
    carries an <animate>; frozen: the rect has the width at t. Used for typing
    reveals of markup that is not a single <text> (a chromatic title, a row of
    glyphs). Returns the clipPath plus the clipped group."""
    cid = uid("rev")
    wf, wa = tl.attr("width", width_kf, calc=calc, begin=begin, repeat=repeat)
    if not wf:
        wf = ' width="0"'
    return (f'<clipPath id="{cid}"><rect x="{fmt(x)}" y="{fmt(y)}" height="{fmt(h)}"{wf}>'
            f'{wa}</rect></clipPath><g clip-path="url(#{cid})">{children}</g>')


def rain(tl, x0, x1, y0, y1, n_cols, seed, opacity=0.35, speed=(40, 140), size=11,
         length=(8, 22), col_opacity=None):
    """Falling 0/1 columns inside the rect (x0,y0)-(x1,y1). Each column is one
    <text> made of stacked <tspan>s; the head (lowest) glyph is brightest. Column
    periods divide the loop length so the loop is seamless. length is the
    (min, max) number of glyphs per column; each glyph costs one <tspan>, so a
    scene on a tight element budget can pass a shorter range. col_opacity, if
    given, is a callable x -> 0..1 multiplier applied per column (for example
    to thin the rain toward the center so a figure stands in a clearing)."""
    rng = random.Random(seed)
    ch = size * 1.1
    cid = uid("rain")
    clip = (f'<clipPath id="{cid}"><rect x="{fmt(x0)}" y="{fmt(y0)}" '
            f'width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}"/></clipPath>')
    cols = []
    gap = (x1 - x0) / max(1, n_cols)
    if isinstance(length, (tuple, list)):
        len_lo, len_hi = int(length[0]), int(length[1])
    else:
        len_lo = len_hi = int(length)
    for i in range(n_cols):
        cx = x0 + gap * (i + 0.5) + rng.uniform(-gap * 0.3, gap * 0.3)
        length = rng.randint(len_lo, len_hi)
        spd = rng.uniform(speed[0], speed[1])
        travel = (y1 - y0) + length * ch
        k = max(1, round(tl.dur * spd / travel))
        p = tl.dur / k
        phase = rng.random()
        chars = [rng.choice("01") for _ in range(length)]
        spans = []
        for j, c in enumerate(chars):
            ly = -(length - 1 - j) * ch
            if j == length - 1:
                fill, op = CYAN, 1.0
            elif j >= length - 4:
                fill, op = CYAN, 0.75
            else:
                fill, op = CYAN_DIM, 0.55
            spans.append(f'<tspan x="{fmt(cx)}" y="{fmt(ly)}" fill="{fill}" '
                         f'fill-opacity="{fmt(op)}">{c}</tspan>')
        frag, anim = tl.transform([(0.0, (0, y0)), (p, (0, y1 + length * ch))],
                                  kind="translate", begin=-phase * p, period=p)
        if col_opacity is not None:
            frag += f' opacity="{fmt(max(0.0, min(1.0, float(col_opacity(cx)))))}"'
        cols.append(f'<g{frag}><text font-size="{fmt(size)}" text-anchor="middle">'
                    f'{"".join(spans)}</text>{anim}</g>')
    return (f'{clip}<g clip-path="url(#{cid})" opacity="{fmt(opacity)}">'
            f'{"".join(cols)}</g>')


def floor_grid(tl, w, h, vp, n_lines, speed, color, n_radial=17, opacity=1.0,
               rung_color=None, rung_width=1.0):
    """Perspective floor: radial lines to the vanishing point vp=(vx, vy) and
    horizontal lines (rungs) that flow toward the viewer. speed is line spacings
    per second; it is rounded so the loop is seamless. rung_color and rung_width
    let the moving rungs be brighter or heavier than the static radials (they
    default to color and 1)."""
    vx, vy = vp
    rung_color = rung_color or color
    k = max(1, round(tl.dur * speed))
    p = tl.dur / k
    out = []
    # radial lines
    half = n_radial // 2
    spread = w * 0.42
    for i in range(-half, half + 1):
        xb = vx + i * spread
        dxl = xb - vx
        dyl = h - vy
        # extend well past the bottom edge so wide angles still cross the canvas
        ext = 3.0
        x2 = vx + dxl * ext
        y2 = vy + dyl * ext
        out.append(f'<line x1="{fmt(vx)}" y1="{fmt(vy)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
                   f'stroke="{color}" stroke-width="1" stroke-opacity="0.6"/>')
    out.append(f'<line x1="0" y1="{fmt(vy)}" x2="{fmt(w)}" y2="{fmt(vy)}" '
               f'stroke="{color}" stroke-width="1" stroke-opacity="0.8"/>')
    # horizontal lines: z = 1 + (i + 1 - u), y = vy + (h - vy) / z
    samples = 10
    for i in range(n_lines):
        ykf = []
        okf = []
        for s in range(samples + 1):
            u = s / samples
            z = 1.0 + (i + 1 - u)
            yy = vy + (h - vy) / z
            op = min(1.0, max(0.08, 1.0 / z))
            ykf.append((u * p, (0, yy - vy)))
            okf.append((u * p, round(op, 3)))
        tf, ta = tl.transform(ykf, kind="translate", period=p)
        of, oa = tl.attr("stroke-opacity", okf, period=p)
        out.append(f'<g{tf}><line x1="0" y1="{fmt(vy)}" x2="{fmt(w)}" y2="{fmt(vy)}" '
                   f'stroke="{rung_color}" stroke-width="{fmt(rung_width)}"{of}>{oa}</line>{ta}</g>')
    clip = uid("floor")
    return (f'<clipPath id="{clip}"><rect x="0" y="{fmt(vy)}" width="{fmt(w)}" '
            f'height="{fmt(h - vy)}"/></clipPath>'
            f'<g clip-path="url(#{clip})" opacity="{fmt(opacity)}">{"".join(out)}</g>')


def tunnel(tl, w, h, vp, n_rings, depth, speed, seed, size=16, opacity=1.0):
    """Rings of 0/1 glyphs around vp, perspective projected (scale = 1/z), moving
    toward the camera and recycling to the far end. depth is the far z (the near
    plane is z = 0.5, a ring at z = 1 has radius h/2). speed is rings per second."""
    rng = random.Random(seed)
    vx, vy = vp
    z_near = 0.5
    dz = (depth - z_near) / n_rings
    k = max(1, round(tl.dur * speed))
    p = tl.dur / k
    r_unit = h * 0.5
    samples = 12
    rings = []
    for i in range(n_rings):
        m = rng.randint(18, 26)
        a0 = rng.uniform(0, 2 * math.pi)
        spans = []
        for j in range(m):
            a = a0 + 2 * math.pi * j / m + rng.uniform(-0.06, 0.06)
            rr = r_unit * rng.uniform(0.94, 1.06)
            cx = rr * math.cos(a)
            cy = rr * math.sin(a) + size * 0.35
            c = rng.choice("0011")
            op = 1.0 if c == "1" else 0.55
            spans.append(f'<tspan x="{fmt(cx)}" y="{fmt(cy)}" fill-opacity="{fmt(op)}">{c}</tspan>')
        skf = []
        okf = []
        for s in range(samples + 1):
            u = s / samples
            z = z_near + (i + 1 - u) * dz
            sc = 1.0 / z
            fade_in = min(1.0, (depth - z) / (1.5 * dz))
            fade_out = min(1.0, (z - z_near) / (0.7 * dz))
            op = max(0.0, min(1.0, fade_in * fade_out)) * 0.95
            skf.append((u * p, round(sc, 4)))
            okf.append((u * p, round(op, 3)))
        sf, sa = tl.transform(skf, kind="scale", period=p)
        of, oa = tl.attr("opacity", okf, period=p)
        rings.append(f'<g{of}><g{sf}><text font-size="{fmt(size)}" fill="{CYAN}" '
                     f'text-anchor="middle">{"".join(spans)}</text>{sa}</g>{oa}</g>')
    return (f'<g transform="translate({fmt(vx)} {fmt(vy)})" opacity="{fmt(opacity)}">'
            f'{"".join(rings)}</g>')


def scanlines(w, h, opacity=0.18):
    """1px dark lines every 3px over the whole frame."""
    pid = uid("scan")
    return (f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{fmt(w)}" height="3">'
            f'<rect width="{fmt(w)}" height="1" fill="{BG}"/></pattern>'
            f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="url(#{pid})" opacity="{fmt(opacity)}"/>')


def vignette(w, h, strength=0.85):
    """Radial gradient from transparent center to BG at the edges."""
    gid = uid("vig")
    return (f'<radialGradient id="{gid}" cx="50%" cy="50%" r="72%">'
            f'<stop offset="45%" stop-color="{BG}" stop-opacity="0"/>'
            f'<stop offset="100%" stop-color="{BG}" stop-opacity="{fmt(strength)}"/>'
            f'</radialGradient>'
            f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="url(#{gid})"/>')


def svg(w, h, body, title):
    """Document wrapper: xmlns, viewBox, size, title, BG ground, font stack."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" height="{fmt(h)}" '
            f'font-family="{FONT}">'
            f'<title>{esc(title)}</title>'
            f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="{BG}"/>'
            f'{body}</svg>')


def project(points_xyz, cam_dist, scale, center):
    """Perspective projection. points_xyz: Nx3 (z positive = away from camera).
    Returns Nx3: screen x, screen y, depth factor f = cam_dist / (cam_dist + z)
    (larger f = nearer)."""
    pts = np.asarray(points_xyz, dtype=float)
    f = cam_dist / (cam_dist + pts[:, 2])
    out = np.empty_like(pts)
    out[:, 0] = center[0] + scale * pts[:, 0] * f
    out[:, 1] = center[1] + scale * pts[:, 1] * f
    out[:, 2] = f
    return out


def rotate(points, ax, ay, az):
    """Rotate Nx3 points by ax, ay, az radians about x, then y, then z."""
    pts = np.asarray(points, dtype=float)
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return pts @ rx.T @ ry.T @ rz.T


def typed(tl, s, x, y, size, fill, begin, cps=18, cursor=True, opacity=1.0, blink=0.5,
          cursor_end=None, ls=0):
    """Typewriter reveal. Animated: the full string sits under a clip rect whose
    width steps one cell per character. Frozen: the revealed prefix only. A YELLOW
    block cursor sits after the last character, solid while typing, blinking after;
    cursor_end (seconds) switches the cursor off for the rest of the loop, so a
    scene with several typed lines shows one cursor at a time. ls is a letter
    spacing in px: every cell (and the textLength lock) widens by it."""
    n = len(s)
    cw = size * MONO_ADV + ls
    t_end = begin + n / cps
    out = []
    if n:
        if tl.freeze:
            # the animated clip loops with the document, so a frozen frame
            # past the loop length shows the same phase as t mod dur
            k = int(math.floor((tl.t % tl.dur - begin) * cps + 1e-9))
            k = max(0, min(n, k))
            if k > 0:
                out.append(text(x, y, s[:k], size, fill, opacity=opacity, ls=ls,
                                extra=f'textLength="{fmt(k * cw)}" lengthAdjust="spacingAndGlyphs"'))
        else:
            cid = uid("typ")
            wkf = [(begin + k / cps, k * cw) for k in range(0, n + 1)]
            wf, wa = tl.attr("width", wkf, calc="discrete")
            out.append(f'<clipPath id="{cid}"><rect x="{fmt(x - 1)}" y="{fmt(y - size * 1.1)}" '
                       f'height="{fmt(size * 1.5)}"{wf}>{wa}</rect></clipPath>')
            out.append(f'<g clip-path="url(#{cid})">' +
                       text(x, y, s, size, fill, opacity=opacity, ls=ls,
                            extra=f'textLength="{fmt(n * cw)}" lengthAdjust="spacingAndGlyphs"') +
                       "</g>")
    if cursor:
        xkf = [(begin + k / cps, x + k * cw + 1) for k in range(0, n + 1)]
        xf, xa = tl.attr("x", xkf, calc="discrete")
        okf = []
        if begin > 0:
            okf.append((0.0, 0))
        okf.append((begin, 1))
        tt = t_end + blink
        on = 0
        stop = tl.dur if cursor_end is None else min(tl.dur, float(cursor_end))
        while tt < stop:
            okf.append((round(tt, 4), on))
            on = 1 - on
            tt += blink
        if stop < tl.dur:
            okf.append((round(stop, 4), 0))
        of, oa = tl.attr("opacity", okf, calc="discrete")
        out.append(f'<rect{xf} y="{fmt(y - size * 0.8)}" width="{fmt(cw * 0.85)}" '
                   f'height="{fmt(size * 0.95)}" fill="{YELLOW}"{of}>{xa}{oa}</rect>')
    return f"<g>{''.join(out)}</g>"


def moving_group(tl, children, translate=None, scale=None, rotate_kf=None, spans=None,
                 calc="linear", begin=0.0, repeat=True, period=None, splines=None, extra=""):
    """Nest groups: [visibility + translate] > [scale] > [rotate] > children.
    translate/scale/rotate_kf are keyframe lists, or a constant (tuple/number)."""
    def track(v, kind):
        if v is None:
            return "", ""
        if isinstance(v, (tuple, int, float)):
            return f' transform="{kind}({fmt(v)})"', ""
        return tl.transform(v, kind=kind, calc=calc, begin=begin, repeat=repeat,
                            period=period, splines=splines)

    vf, va = tl.visible(spans) if spans is not None else ("", "")
    tf, ta = track(translate, "translate")
    sf, sa = track(scale, "scale")
    rf, ra = track(rotate_kf, "rotate")
    inner = children
    if rf or ra:
        inner = f"<g{rf}>{inner}{ra}</g>"
    if sf or sa:
        inner = f"<g{sf}>{inner}{sa}</g>"
    ex = (" " + extra.strip()) if extra else ""
    return f"<g{vf}{tf}{ex}>{inner}{va}{ta}</g>"
