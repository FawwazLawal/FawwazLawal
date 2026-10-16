# Hero footage

The hero is three clips generated with Google Flow (`source/Shot 1.mp4`, `Shot 2.mp4`,
`Shot 3.mp4`, 1280x720, 24 fps). The clips are not stored in this repo.

`gen/ascii_film.py` cuts them together (see `CUTS`), renders every frame as a grid of
0/1 glyphs with the footage's colour, lets her face and hair resolve through under a glyph
veil, and dissolves the gateway white-out back into the opening so the loop is seamless.

    python3 gen/ascii_film.py --out frames          # 313 frames, 20 fps
    python3 gen/ascii_film.py --chapter-loops --out assets

The hero is a 1200x210 band that follows her along a hand-keyed camera path (`CAMERA`).
Encode `frames/` to `assets/hero.webp` at 20 fps (WebP quality 36).
Needs ffmpeg, numpy and Pillow.
