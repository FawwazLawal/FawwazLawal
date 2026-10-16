"""Build every scene.

    python3 gen/build.py                 writes assets/<scene>.svg for every scene
    python3 gen/build.py --freeze 0,3,6  also writes preview/<scene>_t<T>.svg and
                                         renders each to PNG with qlmanage
    python3 gen/build.py --only hero     restrict to scenes whose name contains "hero"
    python3 gen/build.py --no-render     skip qlmanage

Each gen/scene_*.py module exports SCENES = {name: builder} with builder(t=None)
returning an SVG string. A missing or broken module is reported and skipped.
"""

import argparse
import glob
import importlib
import os
import re
import shutil
import subprocess
import sys
import traceback
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
PREVIEW = os.path.join(ROOT, "preview")

EXPECTED = ["scene_hero", "scene_section", "scene_outro", "scene_selftest"]

if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lib  # noqa: E402


def load_scenes(only=None):
    names = list(EXPECTED)
    for path in sorted(glob.glob(os.path.join(HERE, "scene_*.py"))):
        mod = os.path.splitext(os.path.basename(path))[0]
        if mod not in names:
            names.append(mod)
    scenes = {}
    for mod in names:
        if not os.path.exists(os.path.join(HERE, mod + ".py")):
            print(f"[build] missing gen/{mod}.py, skipping")
            continue
        try:
            m = importlib.import_module(mod)
        except Exception:
            print(f"[build] FAILED to import gen/{mod}.py:")
            traceback.print_exc()
            continue
        table = getattr(m, "SCENES", None)
        if not isinstance(table, dict):
            print(f"[build] gen/{mod}.py has no SCENES dict, skipping")
            continue
        for name, builder in table.items():
            if only and only not in name:
                continue
            scenes[name] = builder
    return scenes


def check_svg(path, data):
    problems = []
    try:
        xml.dom.minidom.parseString(data.encode("utf-8"))
    except Exception as e:  # noqa: BLE001
        problems.append(f"XML parse error: {e}")
    if chr(0x2014) in data or chr(0x2013) in data:
        problems.append("contains an em-dash or en-dash")
    # opening tags only, the DESIGN.md section 8 measure (grep -o '<[a-z]')
    n_el = len(re.findall(r"<[a-z]", data))
    if n_el > 3000:
        problems.append(f"element count {n_el} over 3000")
    size_kb = len(data.encode("utf-8")) / 1024
    if size_kb > 900:
        problems.append(f"size {size_kb:.0f} KB over 900 KB")
    return problems, n_el, size_kb


def fmt_t(t):
    return f"{t:g}"


def render(svg_path, out_dir):
    """Render a frozen SVG to <out_dir>/<file>.svg.png at 1:1 scale.

    qlmanage quirk: given a wide SVG with width/height attributes it scales the
    content up and crops it to a square thumbnail. Nesting the scene inside a
    square outer document makes it render at scale 1 in the top band, which we
    then crop with Pillow."""
    data = open(svg_path, encoding="utf-8").read()
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', data)
    if not m:
        print(f"[build]   render: no viewBox in {svg_path}")
        return None
    w, h = float(m.group(1)), float(m.group(2))
    side = max(w, h)
    inner = re.sub(r"^\s*<svg[^>]*>", "", data, count=1)
    inner = re.sub(r"</svg>\s*$", "", inner, count=1)
    wrapped = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'viewBox="0 0 {side:g} {side:g}" width="{side:g}" height="{side:g}">'
               f'<svg viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" x="0" y="0" '
               f'font-family="{lib.FONT}">{inner}</svg></svg>')
    tmp_dir = os.path.join(out_dir, ".ql")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_svg = os.path.join(tmp_dir, os.path.basename(svg_path))
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(wrapped)
    cmd = ["qlmanage", "-t", "-s", str(int(side)), "-o", tmp_dir, tmp_svg]
    r = subprocess.run(cmd, capture_output=True, text=True)
    tmp_png = tmp_svg + ".png"
    if not os.path.exists(tmp_png):
        print(f"[build]   render failed for {svg_path}: {r.stderr.strip()[:300]}")
        return None
    png = os.path.join(out_dir, os.path.basename(svg_path) + ".png")
    try:
        from PIL import Image
        im = Image.open(tmp_png)
        sx = im.size[0] / side
        im = im.crop((0, 0, int(round(w * sx)), int(round(h * sx))))
        im.save(png)
        os.remove(tmp_png)
    except Exception as e:  # noqa: BLE001
        print(f"[build]   crop failed ({e}); keeping the raw thumbnail")
        os.replace(tmp_png, png)
    try:
        os.remove(tmp_svg)
    except OSError:
        pass
    return png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", default="", help="comma separated times, e.g. 0,3,6")
    ap.add_argument("--only", default="", help="substring filter on scene name")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    times = [float(x) for x in args.freeze.split(",") if x.strip() != ""]
    os.makedirs(ASSETS, exist_ok=True)
    if times:
        os.makedirs(PREVIEW, exist_ok=True)

    scenes = load_scenes(args.only or None)
    if not scenes:
        print("[build] no scenes found")
        return 1

    total_kb = 0.0
    failed = 0
    for name, builder in scenes.items():
        lib.reset_ids()
        try:
            data = builder(None)
        except Exception:
            print(f"[build] {name}: builder raised:")
            traceback.print_exc()
            failed += 1
            continue
        out = os.path.join(ASSETS, f"{name}.svg")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(data)
        problems, n_el, size_kb = check_svg(out, data)
        total_kb += size_kb
        n_anim = data.count("<animate") + data.count("<set ")
        print(f"[build] {name}.svg  {size_kb:.1f} KB  tags={n_el}  anims={n_anim}")
        for p in problems:
            print(f"[build]   PROBLEM: {p}")
            failed += 1
        for t in times:
            lib.reset_ids()
            try:
                frozen = builder(t)
            except Exception:
                print(f"[build]   freeze t={t}: builder raised:")
                traceback.print_exc()
                failed += 1
                continue
            if "<animate" in frozen or "<set " in frozen:
                print(f"[build]   PROBLEM: frozen frame t={t} still contains animation elements")
                failed += 1
            fp = os.path.join(PREVIEW, f"{name}_t{fmt_t(t)}.svg")
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(frozen)
            msg = f"[build]   preview/{os.path.basename(fp)}  {len(frozen.encode('utf-8')) / 1024:.1f} KB"
            if not args.no_render:
                png = render(fp, PREVIEW)
                if png:
                    msg += f"  -> {os.path.relpath(png, ROOT)}"
            print(msg)
    shutil.rmtree(os.path.join(PREVIEW, ".ql"), ignore_errors=True)
    print(f"[build] total assets {total_kb:.1f} KB in {len(scenes)} scene(s); problems: {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
