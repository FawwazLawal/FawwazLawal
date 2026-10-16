# Source photographs

The netrunner and the beckoning hand are rendered from these photographs, used under the
Unsplash License. The photos are not stored in this repo; put them in `source/` to rebuild.

| File | Photographer | Unsplash |
|---|---|---|
| `source/glance-back.jpg` | Galina Bogdanova | https://unsplash.com/photos/8LDtgqeKkws |
| `source/hand.jpg` | Tony Chen | https://unsplash.com/photos/PrKE6nWcZZU |

Rebuild (Python 3, numpy, Pillow):

    python3 gen/film.py hero --out frames
    python3 gen/film.py chapters --out assets

then encode `frames/` to `assets/hero.webp` (240 frames, 24 fps).
