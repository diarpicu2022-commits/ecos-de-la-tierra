"""Motor de terreno «Tierra Viva» (contrato «Piel nueva», paso 2).

    python tools/gen_tierra_viva_terrain.py ashen_forest

Pinta el suelo de una zona **desde su matriz aprobada** de
`data/world/zones/<zona>.txt`, en sus dos estados, y escribe
`assets/world/tierra_viva/<zona>_enfermo.png` y `<zona>_sano.png`, a tamaño de
la zona (casillas × 16 px).

Es el port de `tools/tierra_viva/map2.py` y de lo que necesita de `scene2.py`
(matas, vida del agua y puentes), con estas diferencias:

- **Leyenda del repo** (`src/world/world_tiles.gd`, `LEGEND`): `.` suelo,
  `=` camino, `~` agua, `#` follaje sólido. Un `=` con agua a los dos lados
  es un puente. El repo no tiene cotas, así que no hay caras de roca.
- **El follaje sólido** se pinta como una masa de copas por racimos
  (`flora.clumps_canopy`), recortada a la máscara redondeada de sus casillas.
  Lleva el contorno del tono más oscuro de su propia rampa, nunca `ASH_050`
  (cláusula 3), y proyecta sombra al sur sobre el suelo.
- **La paleta sale de los tokens `TV_*`** de `tools/pixel.py`, no de
  `pal.py`, y la región sale de la zona.
- **Cuantizado final** (cláusula 2): todo píxel pasa al token `TV_*` más
  cercano de los permitidos en su estado. El enfermo no puede usar rampas de
  solo-purificado ni el sano, rampas de solo-enfermo.
- **Semilla fija:** dos ejecuciones dan los mismos bytes.

El decorado (árboles sueltos, viñetas, hito, fuente) no va aquí: es el paso 4.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import PALETTE, TV_PURIFIED_ONLY, TV_SICK_ONLY  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ZONES = ROOT / "data" / "world" / "zones"
OUT = ROOT / "assets" / "world" / "tierra_viva"
T = 16
SEED = 1

## Píxeles que los racimos del follaje asoman fuera de sus casillas. Menos de
## un cuarto de casilla: no tapan a quien anda junto al borde.
OVERHANG = 4

## Región de la paleta por zona (cláusula 2). Valdehoja va aparte: paso 5.
REGION = {"ashen_forest": "bosque", "tar_basin": "cuenca", "broken_coast": "costa",
          "withered_plain": "llanura", "waning_peak": "cumbre", "greed_crypt": "cripta"}


# --- paleta --------------------------------------------------------------------

def ramp(name: str) -> list[np.ndarray]:
    out, i = [], 0
    while f"tv_{name}_{i}" in PALETTE:
        out.append(np.array(PALETTE[f"tv_{name}_{i}"], np.uint8))
        i += 1
    if not out:
        raise KeyError(f"no hay rampa tv_{name}")
    return out


def seven(r: list[np.ndarray], idx: list[int]) -> list[np.ndarray]:
    """Rampa de 7 tonos a partir de otra, por índices: así toda rampa entra en
    los mismos huecos del dibujo aunque tenga 5 o 6 tonos."""
    return [r[i] for i in idx]


def palette(state: str, region: str) -> dict[str, list[np.ndarray]]:
    """Rampas de cada material en un estado. Mismos índices en los dos estados:
    el dibujo es el mismo y solo cambia el material. Las variantes de región
    son las de `tools/tierra_viva/map2.py` (`palette`), ya como tokens."""
    p = {k: ramp(k) for k in ("grass", "leaf", "dirt", "sand", "water", "stone", "wood", "flower",
                              "ash", "gold", "roof_red", "ink")}
    dead = seven(ramp("dead_leaf"), [0, 1, 2, 3, 4, 5, 5])
    p["dead"] = dead
    p["sludge"] = ramp("sludge")
    p["smog"] = ramp("smog")
    p["fire"] = ramp("fire")
    p["frailejon"] = seven(ramp("frailejon"), [0, 0, 1, 2, 3, 4, 4])
    if region == "cumbre":
        # páramo: pajonal y nieve en lo sano; pajonal seco y pedregal del
        # glaciar derretido en lo enfermo. Las matas son puyas.
        if state == "sano":
            p["grass"] = ramp("paramo")
            p["sand"] = ramp("snow")
            p["leaf"] = seven(ramp("puya"), [0, 0, 1, 2, 3, 4, 4])
        else:
            p["grass"] = ramp("paramo_dry")
            p["sand"] = ramp("scree")
            p["leaf"] = dead
            p["water"] = ramp("turbid")
            p["dirt"] = ramp("sick_soil")
        return p
    if state == "sano":
        return p
    p["leaf"] = dead
    if region == "cuenca":
        p["water"] = ramp("oil_water")
        p["grass"] = ramp("sludge_grass")
        p["dirt"] = ramp("ash")
        p["sand"] = ramp("ash")[2:7]
    elif region == "costa":
        p["water"] = ramp("plastic_water")
        p["grass"] = seven(ramp("dry_grass"), [0, 0, 1, 2, 3, 4, 5])
        # Dos tonos más oscura que la sana: con la arena gris en su sitio, la
        # playa pesaba casi igual sana que enferma y la Costa no llegaba al
        # piso de valor (1,34; con un tono, 1,50 en deuteranopía).
        gs = ramp("grey_sand")
        p["sand"] = [gs[0], gs[0], gs[0], gs[1], gs[2]]
    else:   # bosque y llanura
        p["grass"] = seven(ramp("dry_grass"), [0, 0, 1, 2, 2, 3, 4])
        p["water"] = ramp("turbid")
        p["dirt"] = ramp("sick_soil")
        p["sand"] = ramp("grey_sand")
    return p


def allowed_colors(state: str) -> np.ndarray:
    """Tokens `TV_*` que puede usar un render en `state` (cláusula 2)."""
    banned = TV_PURIFIED_ONLY if state == "enfermo" else TV_SICK_ONLY
    keep = []
    for name, v in PALETTE.items():
        if not name.startswith("tv_"):
            continue
        r = name[3:].rsplit("_", 1)[0]
        if r not in banned:
            keep.append(v[:3])
    return np.unique(np.array(keep, np.int32), axis=0)


def quantize(img: np.ndarray, colors: np.ndarray) -> int:
    """Lleva cada píxel opaco a su token permitido más cercano. Devuelve
    cuántos píxeles cambió."""
    flat = img[..., :3].reshape(-1, 3).astype(np.int32)
    uniq, inv = np.unique(flat, axis=0, return_inverse=True)
    d = ((uniq[:, None, :] - colors[None, :, :]) ** 2).sum(-1)
    near = colors[d.argmin(1)]
    changed = (near != uniq).any(1)
    out = near[inv.reshape(-1)].reshape(img.shape[0], img.shape[1], 3)
    moved = int(changed[inv.reshape(-1)].sum())
    img[..., :3] = out.astype(np.uint8)
    img[..., 3] = 255
    return moved


# --- máscaras (de map2.py) -------------------------------------------------------

def disk(r: int) -> np.ndarray:
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r + r * 0.8


def up(tiles: np.ndarray) -> np.ndarray:
    return np.kron(np.asarray(tiles, bool), np.ones((T, T), bool))


def rounded(tiles: np.ndarray, r: int, sigma: float = 0) -> np.ndarray:
    """Casillas -> máscara de píxeles con esquinas redondeadas de radio r; con
    sigma, además alisada (desenfoque y umbral): curva orgánica de borde limpio."""
    m = up(tiles)
    if sigma:
        pad = int(3 * sigma) + 2
        mm = np.pad(m.astype(float), pad, mode="edge")
        m = (ndi.gaussian_filter(mm, sigma) > 0.5)[pad:-pad, pad:-pad]
    pad = r + 2
    m = np.pad(m, pad, mode="edge")
    m = ndi.binary_closing(ndi.binary_opening(m, disk(r)), disk(r))
    return m[pad:-pad, pad:-pad]


def shift(m: np.ndarray, dy: int, dx: int, fill: bool = False) -> np.ndarray:
    out = np.full_like(m, fill)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def edge(m: np.ndarray, n: int = 1) -> np.ndarray:
    """Píxeles de m a distancia <= n de fuera."""
    return m & ~ndi.binary_erosion(m, iterations=n, border_value=1)


def tile_tex(h: int, w: int, tex: np.ndarray) -> np.ndarray:
    th, tw = tex.shape[:2]
    return np.tile(tex, (h // th + 1, w // tw + 1, 1))[:h, :w]


def blit(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    sh, sw = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + sw), min(H, y + sh)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    m = s[..., 3] > 0
    dst[y0:y1, x0:x1][m] = s[m]


def sprite(rows: list[str], cmap: dict) -> np.ndarray:
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in cmap:
                a[y, x] = cmap[ch]
    return a


# --- texturas (de map2.py) -------------------------------------------------------

def grass_tex(g: list[np.ndarray]) -> np.ndarray:
    """32x32: base media con matas en V sobre rejilla con desfase."""
    t = np.zeros((32, 32, 4), np.uint8)
    t[:] = g[4]
    v1 = [(0, 0, 3), (2, 0, 3), (1, 1, 2), (0, -1, 5), (2, -1, 5)]
    v2 = [(0, 0, 3), (1, 1, 3), (2, 0, 3), (3, 1, 3), (4, 0, 3), (1, -1, 5), (3, -1, 5)]
    for sx, sy, motif in [(3, 4, v1), (19, 2, v2), (11, 12, v1), (27, 13, v1), (5, 20, v2),
                          (21, 22, v1), (14, 28, v1), (29, 29, v2)]:
        for dx, dy, k in motif:
            t[(sy + dy) % 32, (sx + dx) % 32] = g[k]
    for x, y in [(9, 6), (25, 8), (2, 14), (17, 17), (30, 21), (9, 25), (24, 30)]:
        t[y, x] = g[5]
    for x, y in [(15, 5), (7, 16), (26, 25), (1, 29)]:
        t[y, x] = g[3]
    return t


def dirt_tex(d: list[np.ndarray]) -> np.ndarray:
    t = np.zeros((32, 32, 4), np.uint8)
    t[:] = d[4]
    rng = np.random.default_rng(11)
    for _ in range(26):
        x, y = rng.integers(0, 32, 2)
        t[y, x] = d[3]
    for x, y in [(5, 6), (20, 3), (13, 17), (27, 22), (8, 27), (24, 12)]:   # guijarros
        t[y, x] = d[5]; t[y, (x + 1) % 32] = d[5]
        t[(y + 1) % 32, x] = d[3]; t[(y + 1) % 32, (x + 1) % 32] = d[3]
    return t


# --- capas -------------------------------------------------------------------------

def paint_path(img, path, P, rng):
    """Camino de tierra: rodadas, centro gastado, bordillo de piedrecitas,
    piedras sueltas y briznas que pisan el borde (map2.render)."""
    H, W = path.shape
    yy, xx = np.indices(path.shape)
    chk = (xx + yy) % 2 == 0
    d = ndi.distance_transform_edt(path)
    img[path] = tile_tex(H, W, dirt_tex(P["dirt"]))[path]
    img[path & (d > 6.5) & (d <= 8) & chk] = P["dirt"][3]
    img[path & (d > 11)] = P["dirt"][5]
    img[path & (d > 10) & (d <= 11) & chk] = P["dirt"][5]
    img[edge(path, 1)] = P["dirt"][2]
    img[edge(path, 2) & ~edge(path, 1)] = P["dirt"][3]
    img[path & shift(~path, 2, 0, True) & ~edge(path, 1)] = P["dirt"][3]
    nz = ndi.gaussian_filter(rng.random((H // 4 + 2, W // 4 + 2)), 2.0)
    nz = ndi.zoom(nz, 4, order=1)[:H, :W]
    hi = np.quantile(nz, 0.82)
    img[path & (d > 3) & (nz > hi)] = P["dirt"][5]
    ring = path & (d > 1.5) & (d <= 3.2)
    for y, x in zip(*np.where(ring & ((xx * 5 + yy * 3) % 23 == 0) & (yy < H - 2) & (xx < W - 3))):
        img[y, x:x + 2] = P["stone"][4]
        img[y + 1, x:x + 2] = P["stone"][2]
    ys, xs = np.where(path & (d > 3) & (yy < H - 3) & (xx < W - 4))
    for k in rng.choice(len(ys), size=len(ys) // 260, replace=False) if len(ys) else []:
        y, x = ys[k], xs[k]
        w = 2 + (k % 2)
        img[y, x:x + w] = P["stone"][4]
        img[y + 1, x:x + w] = P["stone"][2]
        img[y + 1, x + w] = P["dirt"][2]
    ey, ex = np.where(edge(path, 1) & shift(~path, -1, 0))
    for k in rng.choice(len(ey), size=min(len(ey) // 14, 400), replace=False) if len(ey) else []:
        y, x = ey[k], ex[k]
        for dx, dy, kk in [(0, 0, 3), (1, -1, 4), (2, 0, 3), (1, 1, 2)]:
            if 0 <= y + dy < H and 0 <= x + dx < W:
                img[y + dy, x + dx] = P["grass"][kk]


def paint_sand(img, sand, P, rng):
    """Arena de playa (map2.render): tono medio con grano, borde oscuro de 1 px
    y franja de 3 px un tono más oscura."""
    sd = P["sand"]
    yy, xx = np.indices(sand.shape)
    img[sand] = sd[3]
    rr = rng.random(sand.shape)
    img[sand & (rr < 0.05)] = sd[2]
    img[sand & (rr > 0.97)] = sd[4]
    img[sand & ((xx * 3 + yy * 7) % 41 == 0)] = sd[1]
    img[edge(sand, 1)] = sd[1]
    img[edge(sand, 3) & ~edge(sand, 1)] = sd[2]


def paint_beach_water(img, wat, beach, P):
    """Donde el agua toca la playa no hay talud: bajío claro y espuma en ondas."""
    bw = wat & ndi.binary_dilation(beach, iterations=10)
    yy, xx = np.indices(wat.shape)
    dd = ndi.distance_transform_edt(wat)
    img[bw & (dd <= 3)] = P["water"][5]
    img[bw & (dd > 3) & (dd <= 6) & (((xx // 3 + yy) % 4) != 0)] = P["water"][4]
    img[bw & (dd > 8) & (dd <= 9) & (xx % 7 < 4)] = P["water"][5]


def paint_water(img, wat, land, P, rng):
    """Agua hundida: profundidad por distancia a la orilla, cara de tierra de
    6 px al norte, talud de 1 px en los lados, destellos en el agua abierta."""
    w = P["water"]
    d = ndi.distance_transform_edt(wat)
    yy, xx = np.indices(wat.shape)
    chk = (xx + yy) % 2 == 0
    img[wat] = w[2]
    img[wat & (d <= 9)] = w[3]
    img[wat & (d > 9) & (d <= 10) & chk] = w[3]
    img[wat & (d <= 4)] = w[4]
    img[wat & (d > 4) & (d <= 5) & chk] = w[4]
    img[wat & (d <= 1.5)] = w[1]
    open_ = wat & (d > 5)
    ys, xs = np.where(open_)
    for k in rng.choice(len(ys), size=max(1, len(ys) // 90), replace=False) if len(ys) else []:
        y, x = ys[k], xs[k]
        for i in range(2 + k % 3):
            if x + i < wat.shape[1] and open_[y, x + i]:
                img[y, x + i] = w[5]
    bank = np.zeros_like(wat)
    for k in range(1, 7):
        bank |= wat & shift(land, k, 0)
    face = np.zeros_like(wat)
    for k in range(1, 3):
        face |= wat & shift(land, k, 0)
    img[bank] = P["dirt"][2]
    img[bank & ~face & (((xx * 3) // 4) % 4 == 0)] = P["dirt"][1]
    img[face] = P["dirt"][3]
    img[bank & shift(land, 1, 0) & (xx % 6 < 2)] = P["grass"][3]
    under = wat & ~bank & shift(bank, 1, 0)
    img[under] = w[0]
    img[wat & ~bank & shift(bank, 2, 0) & ~under] = w[1]
    shore = land & ndi.binary_dilation(wat) & ~shift(wat, -1, 0)
    img[shore] = P["dirt"][2]
    img[land & shift(wat, -1, 0) & ~shift(wat, -2, 0)] = P["grass"][2]
    return bank


# --- masas del follaje (enmienda 14 y sistema de diseño) -------------------------
#
# «Los bosques se cierran con filas de árboles solapados (muro de árboles)»;
# «el árbol quemado es el mismo árbol sin copa, con hollín al pie»; «en lo
# enfermo los arbustos son ramitas secas, no manchas oscuras» (README del
# sistema de diseño «Tierra Viva» y sus tarjetas Overworld y Regiones).
# Cada región tiene su pieza en sano y en enfermo, y las dos se colocan en los
# mismos sitios: la ola descubre cada árbol sobre su versión quemada.

## (pieza sana, pieza enferma, paso horizontal, paso vertical) por región.
MASS = {
    "bosque": ("tree", "burnt_embers", 14, 10),
    "cuenca": ("tree", "burnt", 14, 10),
    "costa": ("bush", "twigs", 11, 8),
    "llanura": ("bush", "twigs", 11, 8),
    "cumbre": ("frailejon", "frailejon_dry", 10, 9),
}

## Píxeles que una pieza del borde norte de la masa puede asomar por encima
## de sus casillas: la copa sube, no se corta en recto.
RISE = 8


def clumps(W, H, circles, ramp, light=(-0.6, -0.8)):
    """Racimos de copa (flora.clumps_canopy): cada racimo es una esfera de 3-4
    tonos de la rampa, de atrás adelante, con su borde inferior separado."""
    img = np.zeros((H, W, 4), np.uint8)
    m = np.zeros((H, W), bool)
    yy, xx = np.mgrid[0:H, 0:W]
    lx, ly = light
    y0, y1 = min(c[1] for c in circles), max(c[1] for c in circles)
    for cx, cy, r in sorted(circles, key=lambda c: c[1]):
        dx = (xx + 0.5 - cx) / r
        dy = (yy + 0.5 - cy) / (r * 0.9)
        d2 = dx * dx + dy * dy
        inside = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        occl = 0.25 * (cy - y0) / max(1, y1 - y0)
        v = np.clip(-(dx * lx + dy * ly) * 0.8 + nz * 0.5, 0, 1) - occl
        idx = np.where(v > 0.78, 5, np.where(v > 0.52, 4, np.where(v > 0.28, 3, 2)))
        layer = np.zeros_like(img)
        for k in (2, 3, 4, 5):
            layer[inside & (idx == k)] = ramp[k]
        layer[inside & (d2 > 0.72) & ((dy > 0.1) | (dx > 0.55))] = ramp[1]
        img[inside] = layer[inside]
        m |= inside
    for cx, cy, r in circles:
        if cy - y0 <= (y1 - y0) * 0.5 and r > 5:
            x, y = int(cx - r * 0.4), int(cy - r * 0.45)
            if 0 <= y < H and 0 <= x < W - 1 and m[y, x]:
                img[y, x:x + 2] = ramp[6]
    return img, m


def outlined(img, color):
    """Contorno exterior de 1 px (cláusula 3: el tono más oscuro de la rampa
    de la propia pieza)."""
    m = img[..., 3] > 0
    ring = ndi.binary_dilation(m) & ~m
    out = img.copy()
    out[ring] = color
    return out


def line(img, x0, y0, x1, y1, color, width=1):
    H, W = img.shape[:2]
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for t in np.linspace(0, 1, n):
        x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
        if 0 <= y < H:
            img[y, max(0, x):max(0, min(W, x + width))] = color


def trunk(img, cx, top, bottom, ramp):
    """Tronco de 6 px con luz a la izquierda y raíces abiertas al pie."""
    img[top:bottom, cx - 3:cx + 3] = ramp[2]
    img[top:bottom, cx - 3:cx - 1] = ramp[3]
    img[top:bottom, cx + 2:cx + 3] = ramp[1]
    img[bottom - 2:bottom, cx - 5:cx + 5] = ramp[2]
    img[bottom - 1, cx - 5:cx - 3] = ramp[1]
    img[bottom - 1, cx + 3:cx + 5] = ramp[1]


def piece(kind, P, rs):
    """Una pieza de masa. El pie es el centro de su fila de abajo."""
    leaf, wood, ash = P["leaf"], P["wood"], P["ash"]
    if kind == "tree":
        W, H = 28, 38
        img = np.zeros((H, W, 4), np.uint8)
        trunk(img, 14, 22, H, wood)
        circles = [(14 + int(rs.integers(-1, 2)), 11, 10), (7, 15, 7), (21, 15, 7), (10, 7, 6), (19, 7, 6)]
        top, _ = clumps(W, 27, circles, leaf)
        top = outlined(top, leaf[0])
        blit(img, top, 0, 0)
        return img
    if kind in ("burnt", "burnt_embers"):
        # el mismo árbol sin copa: tronco y ramas carbonizados en ceniza
        W, H = 28, 38
        img = np.zeros((H, W, 4), np.uint8)
        trunk(img, 14, 14, H, ash)
        tips = []
        for a in (-2.3, -1.9, -1.4, -1.0, -0.6):
            a += rs.uniform(-0.15, 0.15)
            ln = rs.uniform(9, 13)
            x1, y1 = 14 + np.cos(a) * ln, 15 + np.sin(a) * ln
            line(img, 14, 16, x1, y1, ash[1], 2)
            tx, ty = x1 + np.cos(a - 0.5) * 4, y1 + np.sin(a - 0.5) * 4
            line(img, x1, y1, tx, ty, ash[2])
            tips.append((int(x1), int(y1)))
        img = outlined(img, ash[0])
        if kind == "burnt_embers" and rs.random() < 0.25:
            # brasas de `fire` en las ramas: la causa sigue activa
            fire = P["fire"]
            for k, (x, y) in enumerate(tips):
                if 0 <= y < H and 0 <= x < W:
                    img[y, x] = fire[4 if k % 2 else 3]
            img[16, 13:15] = fire[2]
        return img
    if kind == "bush":
        circles = [(9, 7, 6), (5, 9, 4), (13, 9, 4)]
        img, _ = clumps(18, 14, circles, leaf)
        return outlined(img, leaf[0])
    if kind == "twigs":
        W, H = 16, 12
        img = np.zeros((H, W, 4), np.uint8)
        dl = P["dead"]
        for k in range(7):
            a = -np.pi / 2 + rs.uniform(-1.0, 1.0)
            ln = rs.uniform(5, 10)
            line(img, 8, 11, 8 + np.cos(a) * ln, 11 + np.sin(a) * ln, dl[2 + k % 3])
        img[10:12, 6:10] = dl[1]
        return img
    if kind in ("frailejon", "frailejon_dry"):
        W, H = 14, 26
        img = np.zeros((H, W, 4), np.uint8)
        dry = kind == "frailejon_dry"
        # tronco cubierto de hojas secas, como el frailejón de verdad. En lo
        # sano, madera (neutra): `dead_leaf` es solo de lo enfermo y el
        # cuantizado la tapaba (111 494 px movidos en la Cumbre sana).
        skirt = P["dead"] if dry else P["wood"]
        img[9:H, 5:9] = skirt[2]
        img[9:H, 5:6] = skirt[3]
        img[9:H:3, 5:9] = skirt[1]
        ros = P["dead"] if dry else P["frailejon"]
        yy, xx = np.mgrid[0:11, 0:W]
        e = ((xx + 0.5 - 7) / 7) ** 2 + ((yy + 0.5 - 5) / 4.5) ** 2 <= 1
        top = np.zeros((11, W, 4), np.uint8)
        top[e] = ros[2]
        top[e & (yy < 5)] = ros[3]
        top[e & (yy < 3) & (xx < 8)] = ros[4]
        for x in range(1, W - 1, 3):
            top[e & (xx == x) & (yy > 1)] = ros[1]
        if not dry:
            top[1, 6:8] = P["gold"][4]
        img[:11][e] = top[e]
        return outlined(img, ros[0])
    raise KeyError(kind)


def paint_mass(img, mask, region, state, P, rng):
    """Muro de piezas sobre la máscara del follaje, ordenadas por el pie.
    Devuelve la silueta de la masa."""
    H, W = mask.shape
    pure_kind, sick_kind, sx, sy = MASS[region]
    kind = pure_kind if state == "sano" else sick_kind
    feet = []
    for y in range(sy, H + sy, sy):
        for x in range((y // sy % 2) * (sx // 2), W, sx):
            fx, fy = x + int(rng.integers(-3, 4)), y + int(rng.integers(-2, 3))
            if 0 <= fy < H and 0 <= fx < W and mask[fy, fx]:
                feet.append((fy, fx, int(rng.integers(0, 1 << 30))))
    feet.sort()
    reach = ndi.binary_dilation(mask, disk(OVERHANG))
    for k in range(1, RISE + 1):
        reach |= shift(mask, -k, 0)
    sick = state != "sano"
    yy, xx = np.indices(mask.shape)
    if sick:
        # hollín bajo lo muerto: el suelo de la masa se oscurece, tramado
        soot = mask & ((xx + yy) % 2 == 0)
        img[soot] = darker(img[soot], P)
        img[mask & ((xx * 3 + yy * 5) % 7 == 0)] = P["ash"][1]
    elif kind == "frailejon":
        img[mask] = P["grass"][2]
    else:
        img[mask] = P["leaf"][1]
    layer = np.zeros_like(img)
    for n, (fy, fx, seed) in enumerate(feet):
        if sick and kind.startswith("burnt") and n % 3 and mask[min(fy + 10, H - 1), fx]:
            # Lo quemado no es una espesura: queda el borde de la masa entero
            # y uno de cada tres árboles dentro, con el suelo en hollín a la
            # vista entre ellos (sistema de diseño, mapa del Bosque enfermo).
            continue
        spr = piece(kind, P, np.random.default_rng(seed))
        h, w = spr.shape[:2]
        blit(layer, spr, fx - w // 2, fy - h + 1)
    on = (layer[..., 3] > 0) & reach
    shape = on | mask
    shadow = shift(shape, 4, 2) & ~shape
    img[shadow] = darker(img[shadow], P)
    img[on] = layer[on]
    return shape


def darker(px, P):
    """Baja un tono cada píxel dentro de la rampa del estado a la que pertenece."""
    if len(px) == 0:
        return px
    lut = {}
    for r in P.values():
        for i, c in enumerate(r):
            lut.setdefault(tuple(int(v) for v in c[:3]), r[max(0, i - 1)])
    uniq, inv = np.unique(px.reshape(-1, 4), axis=0, return_inverse=True)
    mapped = np.array([lut.get(tuple(int(v) for v in u[:3]), u) for u in uniq], np.uint8)
    return mapped[inv.reshape(-1)].reshape(px.shape)


def paint_bridges(img, G, P):
    """Puente: casillas de camino con agua a los dos lados. Si el agua está
    arriba y abajo, el puente cruza en horizontal: tablas y barandillas."""
    w = P["wood"]
    H, W = img.shape[:2]
    water = G == "~"
    br = (G == "=") & ((np.roll(water, 1, 0) & np.roll(water, -1, 0)) |
                       (np.roll(water, 1, 1) & np.roll(water, -1, 1)))
    lab, n = ndi.label(br)
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        horiz = water[max(ys.min() - 1, 0), xs.min()]
        if horiz:
            y0, y1 = ys.min() * T, (ys.max() + 1) * T
            x0, x1 = max(0, xs.min() * T - 6), min(W, (xs.max() + 1) * T + 6)
            deck = img[y0:y1, x0:x1]
            deck[:] = w[3]
            for i in range(0, x1 - x0, 5):
                deck[:, i] = w[1]
                deck[:, i + 1] = w[4] if i + 1 < x1 - x0 else deck[:, i]
            deck[:2] = w[1]
            deck[-2:] = w[1]
            for yy in (y0 - 3, y1 - 1):
                img[yy:yy + 2, x0:x1] = w[4]
                img[yy + 2, x0:x1] = w[1]
                for x in range(x0, x1, 12):
                    img[yy - 2:yy + 4, x:x + 3] = w[2]
                    img[yy - 2, x:x + 3] = w[5]
        else:
            x0, x1 = xs.min() * T, (xs.max() + 1) * T
            y0, y1 = max(0, ys.min() * T - 6), min(H, (ys.max() + 1) * T + 6)
            deck = img[y0:y1, x0:x1]
            deck[:] = w[3]
            for i in range(0, y1 - y0, 5):
                deck[i, :] = w[1]
            deck[:, :2] = w[1]
            deck[:, -2:] = w[1]
    return br


TUFT = [".l.l.", "ldldl", ".ddd."]
CLUMP = ["..h...h.", ".hlh.hl.", ".lml.lmh", "dmmdlmml", ".dd.dd.d"]
REED = [".h..h", ".l.hl", "lm.lm", "mm.mm", "dd.dd"]


def paint_tufts(img, free, P, rng):
    """Matas sueltas en rejilla con desfase (scene2.tufts): detalle sin manchas."""
    g = P["grass"]
    H, W = free.shape
    small = sprite(TUFT, {"l": g[5], "d": g[3]})
    for y in range(6, H - 6, 22):
        for x in range(4 + (y // 22 % 2) * 11, W - 6, 22):
            jx, jy = x + rng.integers(-5, 6), y + rng.integers(-4, 5)
            if rng.random() < 0.55 and free[jy, jx]:
                blit(img, small, jx, jy)
    big = sprite(CLUMP, {"h": g[6], "l": g[5], "m": g[3], "d": g[2]})
    for y in range(14, H - 8, 38):
        for x in range(10 + (y // 38 % 2) * 19, W - 10, 38):
            jx, jy = x + rng.integers(-8, 9), y + rng.integers(-6, 7)
            if rng.random() < 0.6 and free[jy, jx] and free[min(jy + 4, H - 1), min(jx + 7, W - 1)]:
                blit(img, big, jx, jy)


def paint_water_life(img, wat, bank, state, P, rng):
    """Vida del agua (scene2.water_life): juncos y nenúfares solo en lo sano;
    piedras que asoman en los dos estados."""
    d = ndi.distance_transform_edt(wat)
    g = P["grass"]
    if state == "sano":
        reed = sprite(REED, {"h": g[6], "l": g[5], "m": g[3], "d": g[1]})
        ys, xs = np.where((d >= 1) & (d <= 2) & ~bank)
        for k in rng.choice(len(ys), size=min(len(ys) // 120, 40), replace=False) if len(ys) else []:
            blit(img, reed, xs[k] - 2, ys[k] - 4)
        lily = sprite([".gg.g", "gllgg", ".ggg."], {"g": g[3], "l": g[5]})
        ys, xs = np.where(d > 5)
        for k in rng.choice(len(ys), size=min(len(ys) // 300, 20), replace=False) if len(ys) else []:
            blit(img, lily, xs[k] - 2, ys[k] - 1)
            if k % 3 == 0:
                img[ys[k] - 1, xs[k]] = P["flower"][2]
    s = P["stone"]
    rock = sprite([".abb.", "abbbc", "ccccc", ".www."], {"a": s[5], "b": s[3], "c": s[1], "w": P["water"][5]})
    ys, xs = np.where(d > 5)
    for k in rng.choice(len(ys), size=min(len(ys) // 600, 8), replace=False) if len(ys) else []:
        blit(img, rock, xs[k] - 2, ys[k] - 2)


# --- render --------------------------------------------------------------------------

## Luz de la Cripta por bandas (cláusula 2: «la luz se hace en bandas de la
## rampa, nunca en degradado continuo»). Haces diagonales que entran por las
## grietas del techo: cada banda sube un tono la piedra que toca.
CRYPT_BEAM_PERIOD = 224
CRYPT_BEAMS = ((0, 26, 2), (26, 40, 1))   # (desde, hasta, tonos que sube)


def crypt_light(H: int, W: int) -> np.ndarray:
    """Tonos que sube cada píxel con la luz: 0, 1 o 2, en bandas con borde
    tramado de 2 px. Solo en lo sano: en la enferma el oro tapa las grietas."""
    yy, xx = np.indices((H, W))
    u = (xx + yy * 0.6) % CRYPT_BEAM_PERIOD
    chk = (xx + yy) % 2 == 0
    lift = np.zeros((H, W), np.int8)
    for a, b, k in CRYPT_BEAMS:
        lift[(u >= a) & (u < b)] = np.maximum(lift[(u >= a) & (u < b)], k)
        lift[(u >= b) & (u < b + 2) & chk] = np.maximum(lift[(u >= b) & (u < b + 2) & chk], k)
    return lift


def render_crypt(lines: list[str], state: str) -> np.ndarray:
    """Cripta de la Avaricia (cripta.py, a la matriz del repo): `%` muro,
    `,` losa, `=` alfombra. Lo sano es piedra con musgo y luz por bandas; lo
    enfermo, ceniza en penumbra con el oro derramado. El dibujo es el mismo:
    solo cambian la rampa de la piedra, la luz y lo que cubre el suelo."""
    rng = np.random.default_rng(SEED)
    P = palette(state, "cripta")
    G = np.array([list(r) for r in lines])
    H, W = G.shape[0] * T, G.shape[1] * T
    sick = state == "enfermo"
    stone = P["ash"] if sick else P["stone"]
    yy, xx = np.indices((H, W))
    wall = up(G == "%")
    floor = ~wall
    carpet = up(G == "=")
    img = np.zeros((H, W, 4), np.uint8)

    # losas de 32 x 24 en hileras desplazadas, con bisel y junta
    tone = np.zeros((H, W), np.int8)
    for r, y in enumerate(range(0, H, 24)):
        off = int(rng.integers(0, 32))
        for x in range(-off, W, 32):
            t = 3 + int(rng.random() < 0.35) - int(rng.random() < 0.25)
            m = (yy >= y) & (yy < y + 24) & (xx >= x) & (xx < x + 32)
            tone[m] = t
            tone[m & ((yy == y) | (xx == x))] = t + 1
            tone[m & ((yy == y + 23) | (xx == x + 31))] = 1
    # Penumbra: la enferma baja un tono toda la losa; la sana sube con la luz.
    # Con la piedra en su sitio en los dos estados, el valor se quedaba en 1,42.
    tone = tone + crypt_light(H, W) if not sick else tone - 1
    tone = np.clip(tone, 0, len(stone) - 1)
    for k in range(len(stone)):
        img[floor & (tone == k)] = stone[k]
    # grietas
    for _ in range(W * H // 2600):
        cx, cy, ang = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, np.pi)
        for t in range(int(rng.integers(5, 12))):
            xi, yi = int(cx + np.cos(ang) * t), int(cy + np.sin(ang) * t * 0.6)
            if 0 <= xi < W and 0 <= yi < H and floor[yi, xi]:
                img[yi, xi] = stone[1]
            ang += rng.uniform(-0.5, 0.5)

    # alfombra: ajedrezado de la rampa roja con ribete de oro
    rr = P["roof_red"]
    img[carpet] = rr[2]
    img[carpet & (((xx // 4) + (yy // 4)) % 2 == 0)] = rr[1]
    img[edge(carpet, 1)] = P["gold"][2]
    img[edge(carpet, 2) & ~edge(carpet, 1)] = rr[3]

    # muro visto desde arriba: corona de sillares y, donde da al suelo, su
    # cara de 8 px con hiladas y labio de luz
    face = np.zeros_like(wall)
    for k in range(1, 9):
        face |= wall & shift(floor, -k, 0)
    top = wall & ~face
    img[top] = stone[1]
    img[top & (yy % 8 == 0)] = stone[0]
    img[top & ((xx + (yy // 8 % 2) * 8) % 16 == 0)] = stone[0]
    img[face] = stone[3]
    img[face & (yy % 4 == 0)] = stone[2]
    img[face & ((xx + (yy // 4 % 2) * 6) % 12 == 0)] = stone[2]
    img[face & ~shift(face, 1, 0)] = stone[4]
    img[face & shift(floor, -1, 0)] = stone[1]
    img[edge(wall, 1) & ~face & ~shift(face, -1, 0)] = P["ink"][0]
    # sombra al pie del muro
    for k in range(1, 4):
        sel = floor & shift(wall, k, 0) & ~carpet
        img[sel] = darker(img[sel], P)

    # lo que cubre el suelo: musgo en lo sano, oro derramado en lo enfermo
    spots = floor & ~carpet & ndi.binary_dilation(shift(wall, 3, 0), iterations=2)
    ys, xs = np.where(spots)
    picks = rng.choice(len(ys), size=len(ys) // 70, replace=False) if len(ys) else []
    moss = sprite(["..l.l", ".lml.", "dmmmd"], {"l": P["leaf"][4], "m": P["leaf"][3], "d": P["leaf"][1]})
    for k in picks:
        if not sick:
            blit(img, moss, xs[k] - 2, ys[k] - 2)
    ys, xs = np.where(floor & ~wall)
    picks = rng.choice(len(ys), size=len(ys) // 280, replace=False) if len(ys) else []
    g = P["gold"]
    for k in picks:
        if sick:
            y, x = ys[k], xs[k]
            if x < W - 3 and y < H - 1:
                img[y, x:x + 3] = g[4]
                img[y + 1, x:x + 3] = g[2]
                img[y, x] = g[5]
    if sick:
        # smog: donde en lo sano entra la luz, en lo enfermo flotan jirones
        # finos de humo, tramados y escasos (es una rampa clara y baja el valor)
        wisp = floor & ~carpet & (crypt_light(H, W) > 0) & ((xx + yy * 3) % 5 == 0) & ((xx // 3 + yy) % 4 == 0)
        img[wisp] = P["smog"][0]
    return img


def paint_blight(img, ground, region: str, state: str, P: dict, rng) -> None:
    """El daño propio de cada región sobre el suelo libre (sistema de diseño,
    «Mundo enfermo, uno por región»): lodo de monocultivo en la Llanura y
    hollín en la Cumbre. El ruido se calcula en los dos estados para que la
    semilla no se desalinee; solo se pinta en lo enfermo."""
    H, W = ground.shape
    nz = ndi.gaussian_filter(rng.random((H // 8 + 2, W // 8 + 2)), 1.6)
    nz = ndi.zoom(nz, 8, order=1)[:H, :W]
    if state == "sano" or region not in ("llanura", "cumbre"):
        return
    yy, xx = np.indices(ground.shape)
    chk = (xx + yy) % 2 == 0
    if region == "llanura":
        # charcos de lodo en el tono más bajo de su rampa, con grumos sueltos
        # un tono arriba y borde de hierba seca oscura. Con el tono medio
        # salían verde lima, y en este juego el verde dice «purificado».
        blob = ground & (nz > np.quantile(nz, 0.93))
        blob = ndi.binary_opening(blob, disk(2))
        sl = P["sludge"]
        img[blob] = sl[0]
        img[blob & chk & ((xx * 3 + yy) % 7 == 0)] = sl[1]
        img[edge(blob, 1)] = P["grass"][1]
    else:
        # hollín tramado: manchas de ceniza sobre el pajonal seco
        blob = ground & (nz > np.quantile(nz, 0.80))
        img[blob & chk] = P["ash"][0]
        img[blob & ~chk & ((xx + 2 * yy) % 3 == 0)] = P["ash"][1]


def render(lines: list[str], state: str, region: str) -> np.ndarray:
    """La zona entera en un estado. Misma semilla en los dos estados: el
    dibujo coincide píxel a píxel y solo cambia el material."""
    if region == "cripta":
        return render_crypt(lines, state)
    rng = np.random.default_rng(SEED)
    P = palette(state, region)
    G = np.array([list(r) for r in lines])
    H, W = G.shape[0] * T, G.shape[1] * T
    img = tile_tex(H, W, grass_tex(P["grass"])).copy()

    water_t = G == "~"
    bridge_t = (G == "=") & ((np.roll(water_t, 1, 0) & np.roll(water_t, -1, 0)) |
                             (np.roll(water_t, 1, 1) & np.roll(water_t, -1, 1)))
    path = rounded((G == "=") & ~bridge_t, 4, sigma=5)
    path = ndi.binary_opening(path, disk(1))
    paint_path(img, path, P, rng)

    sand_t = G == ":"
    sand = rounded(sand_t, 6, sigma=10) if sand_t.any() else np.zeros(path.shape, bool)
    if sand.any():
        paint_sand(img, sand & ~path, P, rng)
    wat = rounded(water_t | bridge_t, 8, sigma=12)
    foliage = rounded(G == "#", 5, sigma=6) & ~wat
    beach = ndi.binary_dilation(sand, iterations=3) if sand.any() else sand
    # orilla con talud solo donde el agua no da a la playa
    bank = paint_water(img, wat, ~wat & ~beach, P, rng)
    if beach.any():
        paint_beach_water(img, wat, beach, P)
    paint_water_life(img, wat, bank, state, P, rng)
    paint_bridges(img, G, P)

    free = ~ndi.binary_dilation(path | wat | foliage | sand, iterations=4)
    paint_tufts(img, free, P, rng)
    paint_blight(img, free, region, state, P, rng)
    paint_mass(img, foliage, region, state, P, rng)
    return img


def main(argv: list[str]) -> int:
    zones = argv or list(REGION)
    OUT.mkdir(parents=True, exist_ok=True)
    for zone in zones:
        if zone not in REGION:
            print(f"  FALLA {zone}: sin región de paleta ({', '.join(REGION)})")
            return 1
        lines = (ZONES / f"{zone}.txt").read_text(encoding="utf8").split()
        for state in ("enfermo", "sano"):
            img = render(lines, state, REGION[zone])
            moved = quantize(img, allowed_colors(state))
            path = OUT / f"{zone}_{state}.png"
            Image.fromarray(img, "RGBA").save(path)
            print(f"  {path.relative_to(ROOT)}: {img.shape[1]}×{img.shape[0]}, "
                  f"{moved} px llevados a su token")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
