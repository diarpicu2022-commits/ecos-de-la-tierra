"""Fondos del combate «Tierra Viva» (sistema de diseño, `assets/img/combate_*.png`).

    python tools/gen_tierra_viva_battle.py [zona ...]

Escribe `assets/sprites/battle/tierra_viva/<zona>_{enfermo,sano}.png` a
640 × 360, con las dos plataformas ya pintadas: la del monstruo, arriba a la
derecha (centro 470, 176), y la del grupo, abajo a la izquierda (centro 160,
268). Es el port de `tools/tierra_viva/battle.py`:

- **Bosque:** el del prototipo, tal como lo aprobó Diego en las referencias
  `combate_enfermo.png` y `combate_purificado.png`.
- **Las demás regiones son derivadas** (el sistema solo dibuja el Bosque): el
  mismo cielo por bandas tramadas, horizonte en capas y plataformas
  elípticas, con el material de cada región sacado de
  `gen_tierra_viva_terrain.palette`, que es la paleta aprobada del suelo. La
  Cripta es interior: muro y columnas en vez de cielo.

Paleta: todo píxel es un token `TV_*` permitido en su estado (se cuantiza al
final y se informa de cuántos píxeles movió). Semilla fija.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_tierra_viva_terrain as tv  # noqa: E402

ROOT = tv.ROOT
OUT = ROOT / "assets" / "sprites" / "battle" / "tierra_viva"
W, H = 640, 360
## Plataformas (centro, semiejes) del prototipo.
ENEMY_PLATFORM = (470, 176, 100, 22)
PARTY_PLATFORM = (160, 268, 130, 26)
GROUND_Y = 202


def c(v) -> np.ndarray:
    return np.array([v[0], v[1], v[2], 255], np.uint8)


def ellipse(cx, cy, rx, ry) -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1


def bands(img, y0, y1, colors) -> None:
    """Bandas de cielo con trama entre cada par: el degradado del pixel art."""
    n = len(colors)
    xx = np.arange(W)
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0) * (n - 1)
        i = int(t)
        f = t - i
        c0, c1 = colors[min(i, n - 1)], colors[min(i + 1, n - 1)]
        row = np.where(((f > 0.66) & ((xx + y) % 2 == 0)) | (f > 0.85), 1, 0)
        img[y, row == 0] = c(c0)
        img[y, row == 1] = c(c1)


def hills(img, base_y, amp, period, phase, color, top=None) -> None:
    xs = np.arange(W)
    ys = (base_y - amp * (0.6 * np.sin(xs / period + phase) + 0.4 * np.sin(xs / (period * 0.47) + phase * 2.1))).astype(int)
    for x in range(W):
        img[ys[x]:base_y + 200, x] = c(color)
        if top is not None:
            img[ys[x], x] = c(top)


def peaks(img, base_y, color, snow, seed) -> None:
    rng = np.random.default_rng(seed)
    x = -20
    while x < W + 20:
        h = int(rng.integers(40, 80))
        half = int(h * 0.9)
        for row in range(h):
            span = int((h - row) / h * half)
            y = base_y - row
            img[y, max(0, x - span):max(0, min(W, x + span))] = c(snow if row > h - 12 else color)
        x += int(rng.integers(60, 100))


def treeline(img, base_y, color, light, dark, step=11, size=9, seed=1) -> None:
    rng = np.random.default_rng(seed)
    x = -6
    while x < W + 10:
        r = size + int(rng.integers(-2, 3))
        cy = base_y - r + int(rng.integers(-2, 3))
        m = ellipse(x, cy, r * 0.8, r)
        img[m] = c(color)
        img[ellipse(x - r * 0.3, cy - r * 0.35, r * 0.4, r * 0.4) & m] = c(light)
        x += step + int(rng.integers(-2, 3))
    img[base_y:base_y + 3, :] = c(dark)


def burnt_line(img, base_y, color, seed=3) -> None:
    rng = np.random.default_rng(seed)
    x = 4
    while x < W:
        hgt = int(rng.integers(26, 46))
        img[base_y - hgt:base_y, x:x + 3] = c(color)
        for _ in range(int(rng.integers(1, 3))):
            by = base_y - hgt + int(rng.integers(4, hgt // 2))
            d = int(rng.choice([-1, 1]))
            for j in range(int(rng.integers(4, 9))):
                xx = x + 1 + d * (j + 1)
                if 0 <= xx < W:
                    img[by - j // 2, xx] = c(color)
        x += int(rng.integers(14, 28))


def derricks(img, base_y, color, seed=5) -> None:
    """Torres de bombeo de la Cuenca: armazón en triángulo y balancín."""
    rng = np.random.default_rng(seed)
    x = 30
    while x < W:
        h = int(rng.integers(34, 56))
        for row in range(h):
            span = max(1, int((h - row) / h * 9))
            y = base_y - row
            img[y, x - span:x - span + 2] = c(color)
            img[y, x + span - 1:x + span + 1] = c(color)
            if row % 8 == 0:
                img[y, x - span:x + span] = c(color)
        img[base_y - h - 3:base_y - h, x - 14:x + 16] = c(color)
        x += int(rng.integers(90, 150))


def silo_fence(img, base_y, color) -> None:
    """Silo y cercas de la Llanura."""
    img[base_y - 58:base_y, 330:356] = c(color)
    img[base_y - 64:base_y - 58, 326:360] = c(color)
    for x in range(0, W, 16):
        img[base_y - 9:base_y, x:x + 2] = c(color)
    img[base_y - 7:base_y - 6, :] = c(color)
    img[base_y - 3:base_y - 2, :] = c(color)


def platform(img, cx, cy, rx, ry, top, rim, under) -> None:
    img[ellipse(cx, cy + 3, rx, ry)] = c(under)
    img[ellipse(cx, cy, rx, ry)] = c(rim)
    img[ellipse(cx, cy + 1, rx - 3, ry - 2)] = c(top)


def speckle(img, n, y0, colors, rng) -> None:
    for _ in range(n):
        x, y = int(rng.integers(0, W)), int(rng.integers(y0, H))
        img[y, x] = c(colors[int(rng.integers(0, len(colors)))])


def smoke(img, rng, color) -> None:
    for _ in range(9):
        cx, cy = int(rng.integers(0, W)), int(rng.integers(20, 150))
        m = ellipse(cx, cy, int(rng.integers(20, 40)), int(rng.integers(4, 7)))
        yy, xx = np.nonzero(m)
        k = (xx + yy) % 2 == 0
        img[yy[k], xx[k]] = c(color)


def crypt(img, P, sick: bool) -> None:
    """La Cripta es interior: muro de sillares, columnas y suelo de losa."""
    st = P["stone"]
    img[:GROUND_Y] = c(st[0])
    for y in range(0, GROUND_Y, 12):
        img[y:y + 1, :] = c(st[1])
        off = 0 if (y // 12) % 2 else 14
        for x in range(off, W, 28):
            img[y:y + 12, x:x + 1] = c(st[1])
    for x in range(30, W, 120):
        img[:GROUND_Y, x:x + 22] = c(st[2])
        img[:GROUND_Y, x:x + 4] = c(st[3])
        img[:GROUND_Y, x + 19:x + 22] = c(st[1])
    img[GROUND_Y:] = c(st[2])
    rng = np.random.default_rng(8)
    if sick:
        smoke(img, rng, P["smog"][0])
        speckle(img, 60, GROUND_Y + 2, [P["gold"][3], P["gold"][4]], rng)
    else:
        # luz que entra desde arriba, en bandas (como el suelo de la Cripta)
        for x0 in (150, 410):
            for y in range(0, GROUND_Y):
                w = 30 + y // 6
                seg = img[y, x0 - w // 2:x0 + w // 2]
                k = (np.arange(seg.shape[0]) + y) % 2 == 0
                seg[k] = c(st[3])
        speckle(img, 120, GROUND_Y + 2, [st[3], st[1]], rng)
    platform(img, *ENEMY_PLATFORM, st[3], st[4], st[1])
    platform(img, *PARTY_PLATFORM, st[3], st[4], st[1])


def background(region: str, state: str) -> np.ndarray:
    sick = state == "enfermo"
    P = tv.palette(state, region)
    img = np.zeros((H, W, 4), np.uint8)
    if region == "cripta":
        crypt(img, P, sick)
        return img
    rng = np.random.default_rng(4)
    if sick:
        dusk, hill = tv.ramp("dusk"), tv.ramp("dusk_hill")
        bands(img, 0, GROUND_Y, dusk)
        if region == "cumbre":
            peaks(img, 176, hill[3], P["sand"][1], 11)
        else:
            hills(img, 168, 12, 70, 0.5, hill[3], hill[4])
        if region == "costa":
            sea = P["water"]
            img[180:GROUND_Y] = c(sea[3])
            for y in range(182, GROUND_Y, 4):
                img[y, (np.arange(W) + y * 3) % 9 == 0] = c(sea[5])
            speckle(img, 30, 182, [tv.ramp("plastic")[k] for k in (4, 5, 2)], rng)
        elif region == "bosque":
            burnt_line(img, 184, hill[1], 5)
            hills(img, 198, 7, 46, 1.7, hill[2])
            burnt_line(img, 206, hill[0], 9)
        elif region == "cuenca":
            derricks(img, 186, hill[1])
            hills(img, 198, 7, 46, 1.7, hill[2])
        elif region == "llanura":
            hills(img, 194, 6, 52, 1.2, hill[2])
            silo_fence(img, 200, hill[1])
        else:
            hills(img, 198, 7, 46, 1.7, hill[2])
        ground = P["ash"] if region == "bosque" else P["grass"]
        img[GROUND_Y:] = c(ground[2])
        speckle(img, 260, GROUND_Y, [ground[1], ground[1], ground[3]], rng)
        if region == "bosque":
            speckle(img, 40, 206, [P["fire"][3]], rng)
        elif region == "cuenca":
            for _ in range(14):
                img[ellipse(int(rng.integers(0, W)), int(rng.integers(214, H)), int(rng.integers(10, 26)), 3)] = c(tv.ramp("oil")[1])
        elif region == "llanura":
            speckle(img, 50, 208, [P["sludge"][0]], rng)
        smoke(img, rng, hill[5])
        top, rim, under = ground[3], ground[4], ground[1]
    else:
        sky = tv.ramp("sky")
        bands(img, 0, GROUND_Y, sky[:6])
        for cx, cy, r in [(90, 50, 26), (124, 56, 18), (380, 36, 30), (420, 44, 20), (560, 80, 16)]:
            m = ellipse(cx, cy, r, r * 0.45)
            img[m] = c(tv.ramp("ui")[6])
            img[ellipse(cx + 3, cy + 3, r * 0.9, r * 0.3) & m & ~ellipse(cx, cy - 1, r, r * 0.45 - 1)] = c(sky[6])
        far = tv.ramp("far_hill")
        if region == "cumbre":
            peaks(img, 176, P["grass"][2], P["sand"][4], 11)
        else:
            hills(img, 160, 14, 80, 0.4, far[0], far[1])
        if region == "costa":
            sea = P["water"]
            img[176:GROUND_Y] = c(sea[3])
            for y in range(178, GROUND_Y, 4):
                img[y, (np.arange(W) + y * 3) % 9 == 0] = c(sea[5])
        elif region == "cumbre":
            hills(img, 198, 7, 46, 1.7, P["grass"][3])
        else:
            leaf = P["leaf"]
            treeline(img, 182, leaf[3], leaf[4], leaf[1], step=12, size=10, seed=2)
            treeline(img, GROUND_Y, leaf[2], leaf[3], leaf[0], step=10, size=9, seed=6)
        ground = P["sand"] if region == "costa" else P["grass"]
        img[GROUND_Y:] = c(ground[-3])
        for _ in range(220):
            x, y = int(rng.integers(0, W - 2)), int(rng.integers(204, H - 1))
            img[y, x] = c(ground[-2])
            img[y + 1, x] = c(ground[-4])
        speckle(img, 30, 208, [P["flower"][k] for k in range(5)], rng)
        top, rim, under = ground[-3], ground[-2], P["dirt"][3]
    platform(img, *ENEMY_PLATFORM, top, rim, under)
    platform(img, *PARTY_PLATFORM, top, rim, under)
    return img


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for zone in argv or list(tv.REGION):
        for state in ("enfermo", "sano"):
            img = background(tv.REGION[zone], state)
            moved = tv.quantize(img, tv.allowed_colors(state))
            path = OUT / f"{zone}_{state}.png"
            Image.fromarray(img, "RGBA").save(path)
            print(f"  {path.relative_to(ROOT)}: {moved} px llevados a su token")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
