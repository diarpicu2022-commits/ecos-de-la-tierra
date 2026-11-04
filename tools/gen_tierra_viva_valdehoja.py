"""Valdehoja orgánica del sistema de diseño, puesta en el juego.

Encargo de Diego, 2026-11-03: «no quiero ver nada del viejo». La referencia es
`components/Overworld` (`assets/img/valdehoja_enfermo.png`, `valdehoja_sano.png`
y `v_*.png`), que sale de `tools/tierra_viva/village5.py`. Este generador usa
ese mismo código con semilla fija y separa lo que el prototipo aplana en una
sola imagen:

- `assets/world/tierra_viva/valdehoja_{enfermo,sano,sano_1}.png`, el suelo con
  sus calcos y sombras;
- `assets/sprites/world/tierra_viva/<id>_valdehoja_{sick,pure}.png`, cada pieza
  que se alza del suelo, para que Ilan pase por delante o por detrás;
- `data/world/zones/valdehoja.txt`, `.deco.txt` y `.parts.txt`, la matriz de
  90 × 64, el decorado con su desfase en píxeles y las partes de purificación.

Lo que el juego necesita y la referencia no trae se añade aquí, sin tocar el
prototipo (guía §4.3): la bocamina tapiada al noroeste, la salida al Bosque, el
jardín de Yara en la orilla este, las partes y la aparición.

    python tools/gen_tierra_viva_valdehoja.py
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gen_tierra_viva_terrain as tv  # noqa: E402

PROTO = ROOT / "tools" / "tierra_viva"
sys.path.insert(0, str(PROTO))
os.chdir(PROTO)  # el prototipo abre sus fuentes con rutas relativas
import buildings as B  # noqa: E402
import burnt as burnt_mod  # noqa: E402
import map2  # noqa: E402
import npc_vars  # noqa: E402
import px  # noqa: E402
import scene  # noqa: E402
import scene2  # noqa: E402
import village5 as v5  # noqa: E402
import world as world_mod  # noqa: E402
from scene2 import (BURNT, TREE, ashen, boat, bush2, crate_fish, fence, foot_x, fruit_tree, hay,  # noqa: E402
                    laundry, ring_planter, sign, solve_trees, tall_tuft)

T = 16
W, H = v5.W, v5.H
SPRITES = ROOT / "assets" / "sprites" / "world" / "tierra_viva"
TERRAIN = ROOT / "assets" / "world" / "tierra_viva"
ZONES = ROOT / "data" / "world" / "zones"

# Lo que añade el juego. Casillas (columna, fila).
EXIT_EAST_ROW = 33  # la calle mayor cruza el borde este, salida al Bosque
MINE = (3, 2)  # bocamina de 2 × 2, en una cara de roca; salida a la Cripta en (3, 0)
GARDEN = (82, 16, 88, 25)  # jardín de Yara (col0, fila0, col1, fila1), con su seto
SPAWN = (40, 31)  # en la calle mayor, al pie de la plaza: el encuadre de `v_plaza`


def game_spec() -> dict:
    """La matriz de `village5` con lo que el juego necesita."""
    spec = v5.spec()
    g = [list(r) for r in spec["ground"]]
    h = [[int(c) for c in r] for r in spec["height"]]
    # La bocamina: una cara de roca de dos filas al noroeste; la senda baja de
    # la salida (3, 0) a la mina y de la mina a la calle de la terraza.
    for r in range(0, 2):
        for c in range(0, 8):
            h[r][c] = 2
    for r in (0, 1):
        g[r][3] = "p"
    for r in range(4, 11):
        g[r][3] = g[r][4] = "p"
    # El jardín: hierba y flores en la orilla este, con su senda hasta la calle
    # mayor. La referencia ya pone ahí su campo de flores.
    c0, r0, c1, r1 = GARDEN
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            g[r][c] = "."
    for r in range(r0 + 1, r1):
        for c in range(c0 + 1, c1):
            if (c * 3 + r * 5) % 7 < 3:
                g[r][c] = "f"
    for r in range(r0 + 5, EXIT_EAST_ROW):
        g[r][84] = g[r][85] = "p"
    for r in range(r1 + 1, EXIT_EAST_ROW):
        for c in range(81, 89):
            if g[r][c] == "t":
                g[r][c] = "."
    return dict(ground=["".join(r) for r in g], height=["".join(str(v) for v in r) for r in h])


class Registry:
    """Una entrada por sprite distinto: id legible y su par de imágenes."""

    def __init__(self):
        self.by_key = {}
        self.images = {}
        self.count = {}

    def add(self, cat: str, sick: np.ndarray, pure: np.ndarray) -> tuple[str, int, int]:
        sick, pure = pad_pair(sick, pure)
        key = (cat, sick.tobytes(), pure.tobytes())
        if key not in self.by_key:
            n = self.count.get(cat, 0)
            self.count[cat] = n + 1
            sid = cat if n == 0 else f"{cat}_{n}"
            self.by_key[key] = sid
            self.images[sid] = (sick, pure)
        return self.by_key[key], sick.shape[1], sick.shape[0]


def pad_pair(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mismo lienzo para los dos estados, apoyados abajo a la izquierda, con al
    menos un tile de ancho: así la posición vale para el sano y el enfermo."""
    h = max(a.shape[0], b.shape[0])
    w = max(a.shape[1], b.shape[1], T)
    out = []
    for s in (a, b):
        c = np.zeros((h, w, 4), np.uint8)
        c[h - s.shape[0]:, :s.shape[1]] = s
        out.append(c)
    return out[0], out[1]


def piece(cat, sick, pure, x, yb, shadow=0, solid="base", rows=1, kind="decor"):
    return dict(cat=cat, sick=sick, pure=pure, x=x, yb=yb, shadow=shadow, solid=solid, rows=rows, kind=kind)


def both(cat, s, x, yb, **kw):
    return piece(cat, ashen(s), s, x, yb, **kw)


def pieces(info) -> tuple[list[dict], dict]:
    """Las piezas de `village5.objects`, con nombre y en los dos estados. Mismo
    orden, mismas semillas y mismas posiciones que la referencia. Devuelve
    también los calcos de suelo por estado."""
    rng = np.random.default_rng(11)
    out = []
    decals = {"enfermo": [], "sano": []}
    for p in v5.layout():
        spr, x, yb, door_cx = p["spr"], p["x"], p["yb"], p["door_cx"]
        o = both(f"house_{p['name']}", spr, x, yb, solid="house")
        o["door"] = (p["c"], p["r_door"])
        out.append(o)
        y = p["yard"]
        if y == "valla":
            pots = bool(rng.integers(0, 2))
            w = spr.shape[1]
            fy = yb + 14
            left_w = door_cx - 14 - (x + 4)
            right_w = (x + w - 4) - (door_cx + 14)
            if left_w >= 16:
                out.append(both("fence", fence(left_w // 12), x + 4, fy))
            if right_w >= 16:
                n = right_w // 12
                out.append(both("fence", fence(n), door_cx + 14 + (right_w - (n * 12 + 4)), fy))
            if pots:
                out.append(both("pot", B.pot_plant(door_cx), door_cx - 20, yb + 4, solid=None))
                out.append(both("pot", B.pot_plant(door_cx + 1), door_cx + 13, yb + 4, solid=None))
        elif y == "seto":
            for k, dx in enumerate((-30, 18)):
                out.append(piece("hedge", bush2("enfermo", k + p["c"]), bush2("sano", k + p["c"]),
                                 door_cx + dx - 6, yb + 14, shadow=22, solid="cell"))
        elif y == "huerto":
            out.append(both("pot", B.pot_plant(p["c"]), door_cx - 20, yb + 4, solid=None))
            out.append(both("hay", hay(), x + spr.shape[1] - 10, yb + 4))
        elif p["name"] in ("posada", "tienda", "alcaldia", "panaderia", "escuela"):
            out.append(both("pot", B.pot_plant(p["c"]), door_cx - 20, yb + 4, solid=None))
            out.append(both("pot", B.pot_plant(p["c"] + 1), door_cx + 13, yb + 4, solid=None))
    # La plaza del Árbol del Vínculo.
    cx, cy = 40 * T, 23 * T + 8
    for st in decals:
        decals[st].append((ring_planter(st), cx - 42, cy - 17))
    out.append(piece("bond_tree", BURNT.copy(), TREE.copy(), cx - foot_x(BURNT), cy, shadow=60, rows=2))
    out.append(both("stall", B.stall(), 31 * T, 21 * T, rows=2))
    out.append(both("stall", B.stall(("roofb", "paper"), "tela"), 46 * T + 6, 21 * T, rows=2))
    out.append(both("stall", B.stall(("roofr", "paper"), "fruta"), 32 * T, 26 * T + 4, rows=2))
    out.append(both("stall", B.stall(("eco", "paper"), "tela"), 45 * T, 26 * T - 4, rows=2))
    out.append(both("bench", B.bench(), cx - 84, cy + 34))
    out.append(both("bench", B.bench(), cx + 52, cy + 30))
    lamp = B.lamp_post()
    for x, y in [(30 * T + 2, 18 * T + 14), (50 * T - 10, 19 * T), (31 * T, 28 * T - 2), (49 * T - 4, 28 * T - 2)]:
        out.append(piece("lamp", lamp, lamp, x, y, shadow=6))
    f = B.fountain()
    out.append(both("fountain", f, 41 * T - f.shape[1] // 2, 53 * T, rows=2))
    out.append(both("bench", B.bench(), 36 * T, 54 * T))
    out.append(piece("lamp", lamp, lamp, 34 * T + 2, 49 * T, shadow=6))
    out.append(piece("lamp", lamp, lamp, 47 * T - 6, 55 * T, shadow=6))
    for i, (x, y) in enumerate([(x, y) for y in (18 * T, 21 * T + 6) for x in range(4 * T, 16 * T, 58)]):
        fruit = [3, 0, 1][i % 3]
        out.append(piece("fruit_tree", fruit_tree("enfermo", i, fruit), fruit_tree("sano", i, fruit),
                         x + int(rng.integers(-6, 7)), y + int(rng.integers(-4, 5)), shadow=26, solid="cell"))
    out.append(both("well", B.well(), 27 * T, 20 * T, rows=2))
    for st in decals:
        decals[st].append((boat(), 71 * T, 48 * T + 4))
    out.append(both("crate", crate_fish(), 66 * T, 54 * T))
    sg = sign()
    for x, y in [(2 * T, v5.srow("mayor", 2) * T - 12), (86 * T, v5.srow("mayor", 86) * T - 12), (42 * T + 4, 63 * T)]:
        out.append(piece("sign", sg, sg, x, y, shadow=10))
    out.append(both("laundry", laundry(), 9 * T, 41 * T, solid=None))
    for i, (x, y) in enumerate([(37 * T - 8, 15 * T), (41 * T + 4, 15 * T)]):
        out.append(piece("hedge", bush2("enfermo", i), bush2("sano", i), x, y, shadow=22, solid="cell"))
    # Árboles: los sitios de la referencia, sin el del rincón de la bocamina ni
    # los que caerían en el jardín.
    spots = [(-40, 70), (1300, 60), (1380, 170), (1320, 320), (1380, 460), (1300, 600), (1380, 760),
             (1320, 1040), (60, 1060), (220, 1050), (420, 1060), (760, 1060), (980, 1050), (1160, 1060),
             (-40, 600), (-40, 820),
             (300, 400), (820, 420), (700, 640), (560, 860), (300, 880), (900, 820), (120, 120), (1000, 120)]
    gx0, gy0, gx1, gy1 = GARDEN[0] * T - 60, GARDEN[1] * T - 16, GARDEN[2] * T + 40, GARDEN[3] * T + 60
    for i, x, y in solve_trees(spots, info, "valdehoja5"):
        if x < 40 and y < 140 or (gx0 <= x <= gx1 and gy0 <= y <= gy1):
            continue
        flip = not i % 2
        s, u = (BURNT[:, ::-1], TREE[:, ::-1]) if flip else (BURNT, TREE)
        out.append(piece("oak_flip" if flip else "oak", s, u, x, y, shadow=54, solid="trunk"))
    # Los vecinos con nombre.
    places = list(v5.NPCS)
    for p in v5.layout():
        if p["name"] == "capilla":
            places.append(("julian", "south", p["door_cx"] + 22, p["yb"] + 14))
        if p["name"] == "molino":
            places.append(("aurelio", "west", p["door_cx"] + 30, p["yb"] + 18))
        if p["name"] == "botes":
            places.append(("mariela", "south-west", p["door_cx"] + 26, p["yb"] + 22))
    for n, d, x, y in places:
        s = scene.trim(np.array(Image.open(f"../../assets/source/pixellab/npc/{n}/{d}.png")))
        out.append(piece(f"npc_{n}", s, s, x - s.shape[1] // 2, y, shadow=22, solid="cell"))
    out += garden()
    return out, decals


def garden() -> list[dict]:
    """El jardín de Yara: seto de arbustos, el roble sano, Yara y el semillero.
    Siempre purificado (parte `yara_garden`)."""
    c0, r0, c1, r1 = GARDEN
    out = []
    def hedge(k, x, y):
        s = bush2("sano", k)
        out.append(piece("hedge", s, s, x, y, shadow=0, solid="cell"))
    k = 0
    for c in range(c0, c1 + 1):
        hedge(k, c * T - 6, (r0 + 1) * T)
        k += 1
        if c not in (84, 85):
            hedge(k, c * T - 6, (r1 + 1) * T)
            k += 1
    for r in range(r0 + 1, r1):
        hedge(k, c0 * T - 6, (r + 1) * T)
        hedge(k + 1, c1 * T - 6, (r + 1) * T)
        k += 2
    return out


def yara_sprite() -> np.ndarray:
    """Yara, la anciana curandera: variante de Toña por `npc_vars` hasta que
    tenga su original de PixelLab (`components/Regiones`, «Vecinos»)."""
    skin = npc_vars.skin_colors("tona")
    a = np.array(Image.open("../../assets/source/pixellab/npc/tona/south.png").convert("RGBA"))
    return scene.trim(npc_vars.recolor(a, skin, 0.33, 0.9, 0.95, 0.85, None))


def ground(spec, state, frame, pcs, decals):
    """El suelo como `scene2.render`, sin las piezas que se alzan."""
    flat = dict(spec)
    flat["ground"] = [r.replace("t", ".") for r in spec["ground"]]  # las matas son piezas
    img, info = map2.render(flat, state, frame)
    P = info["P"]
    scene2.tufts(img, info, P)
    scene2.water_life(img, info, P, state)
    scene2.bridge(img, info, P)
    scene2.overlays(img, info, P, frame % 2, state)
    for spr, x, y in decals[state]:
        px.blit(img, spr, x, y)
    if state != "sano":
        for o in pcs:
            if o["cat"] in ("oak", "oak_flip"):
                cx = o["x"] + foot_x(o["sick"])
                px.blit(img, burnt_mod.soot(64, 14, seed=abs(int(cx))), cx - 32, o["yb"] - 9)
    for o in pcs:
        if o["shadow"]:
            spr = o["sick"] if state != "sano" else o["pure"]
            h_, w_ = spr.shape[:2]
            sw = o["shadow"]
            sh_h = max(3, sw // 3)
            world_mod.shadow(img, world_mod.ellipse_mask(sw, sh_h), o["x"] + (w_ - sw) // 2 + 2,
                             o["yb"] - sh_h // 2 - 1, 1)
    return img, info


def matrix(spec, info) -> list[list[str]]:
    G = np.array([list(r) for r in spec["ground"]])
    face = info["face"]
    rows = [["."] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            ch = G[r, c]
            if ch == "w":
                rows[r][c] = "~"
            elif ch in "pSBc":
                rows[r][c] = "="
            if ch not in "SB" and face[r * T:(r + 1) * T, c * T:(c + 1) * T].mean() >= 0.4:
                rows[r][c] = "#"
    # La escalera de la plaza: la cara de roca no corta su casilla de abajo.
    for r in range(H - 1):
        for c in range(W):
            if G[r, c] == "S":
                rows[r][c] = "="
                rows[r + 1][c] = "="
    # Borde cerrado (reglas de «Umbral»), salvo las dos salidas.
    for r in range(H):
        for c in (0, W - 1):
            rows[r][c] = "~" if rows[r][c] == "~" else "#"
    for c in range(W):
        for r in (0, H - 1):
            rows[r][c] = "~" if rows[r][c] == "~" else "#"
    rows[EXIT_EAST_ROW][W - 1] = "="
    # La mina: nada al norte de su cara se alcanza sin abrirla.
    for r in (0, 1):
        for c in range(0, 9):
            rows[r][c] = "#"
    rows[0][3] = rows[1][3] = "="
    for r in (2, 3):
        for c in (MINE[0], MINE[0] + 1):
            rows[r][c] = "."
    return rows


class Grid:
    """Reparte las piezas en la capa de decorado: cada casilla, de una sola."""

    def __init__(self, rows):
        self.rows = rows
        self.taken = {}

    def free(self, c, r, solid_ok=False):
        if not (0 < c < W - 1 and 0 < r < H - 1):
            return False
        if (c, r) in self.taken:
            return False
        return self.rows[r][c] in ".="

    def box_free(self, c, r, w, h):
        return all(self.free(c + i, r + j) for j in range(h) for i in range(w))

    def claim(self, c, r, w, h, who):
        for j in range(h):
            for i in range(w):
                self.taken[(c + i, r + j)] = who

    def nearest(self, c, r, w, h):
        for d in range(0, 8):
            for dy in range(-d, d + 1):
                for dx in range(-d, d + 1):
                    if max(abs(dx), abs(dy)) == d and self.box_free(c + dx, r + dy, w, h):
                        return c + dx, r + dy
        return None


def footprint(o, sw, sh):
    """Casillas sólidas de una pieza: (col, fila, ancho, alto), o None si se pisa."""
    x, yb = o["x"], o["yb"]
    bottom = (yb - 1) // T
    if o["solid"] == "cell":
        return max(1, min(W - 2, (x + sw // 2) // T)), max(1, min(H - 2, bottom)), 1, 1
    if o["solid"] == "house":
        # El escalón pisa 4 px la casilla de la puerta: esa casilla es del camino.
        bottom = (yb - 5) // T
        c0 = max(1, (x + 8) // T)
        c1 = min(W - 2, (x + sw - 8) // T)
        rows = max(2, (sh - 20) // T)
        return c0, max(1, bottom - rows + 1), c1 - c0 + 1, rows
    if o["solid"] == "trunk":
        cx = x + foot_x(o["sick"])
        return max(1, min(W - 3, cx // T - 1 + (cx % T >= 8))), min(H - 2, bottom), 2, 1
    if o["solid"] is None:
        return None
    c0 = (x + 3) // T
    c1 = (x + sw - 4) // T
    return c0, bottom - o["rows"] + 1, max(1, c1 - c0 + 1), o["rows"]


LEGEND_POOL = [chr(c) for c in list(range(0x41, 0x5B)) + list(range(0x61, 0x7B)) + list(range(0x30, 0x3A))
               + list(range(0xC0, 0x17F)) + list(range(0x391, 0x3CA)) + list(range(0x410, 0x450))
               if chr(c) not in "vmkdGSpXYg×÷ΐ"]


def main() -> int:
    spec = game_spec()
    info0 = map2.render(spec, "enfermo", 0)[1]
    pcs, decals = pieces(info0)
    # Yara y su roble, centrados en el jardín.
    c0, r0, c1, r1 = GARDEN
    ground_imgs = {}
    for state, frame in (("enfermo", 0), ("sano", 0), ("sano", 1)):
        img, info = ground(spec, state, frame, pcs, decals)
        moved = tv.quantize(img, tv.allowed_colors(state))
        ground_imgs[(state, frame)] = img
        name = f"valdehoja_{state}{'_1' if frame else ''}.png"
        Image.fromarray(img, "RGBA").save(TERRAIN / name)
        print(f"  {name}: {img.shape[1]}×{img.shape[0]}, {moved} px llevados a su token")
    rows = matrix(spec, info0)

    reg = Registry()
    grid = Grid(rows)
    legend = {}  # char -> línea
    cells = {}  # (c, r) -> char
    pool = iter(LEGEND_POOL)
    shared = {}

    def emit(kind, sid, solid, size, offset, at, comment=""):
        key = (kind, sid, solid, size, offset)
        share = size == (1, 1)
        if share and key in shared:
            ch = shared[key]
        else:
            ch = next(pool)
            sz = f", {size[0]}x{size[1]}"
            off = f", {offset[0]:+d}{offset[1]:+d}" if offset != (0, 0) else ""
            legend[ch] = f"; {ch} = {kind}, {sid}, {'sólido' if solid else 'pisable'}{sz}{off}"
            if share:
                shared[key] = ch
        for j in range(size[1]):
            for i in range(size[0]):
                cells[(at[0] + i, at[1] + j)] = ch

    def place(o):
        sid, sw, sh = reg.add(o["cat"], o["sick"], o["pure"])
        fp = footprint(o, sw, sh)
        solid = fp is not None
        if fp is None:
            fp = (max(1, min(W - 2, (o["x"] + sw // 2) // T)), max(1, min(H - 2, (o["yb"] - 1) // T)), 1, 1)
        c, r, w, h = fp
        if not grid.box_free(c, r, w, h):
            # Si la huella tropieza con otra pieza o con roca, se encoge; si no
            # cabe nada, una casilla libre cerca sostiene el sprite y la pieza
            # se pisa: el dibujo no cambia de sitio (va con su desfase).
            while h > 1 and not grid.box_free(c, r, w, h):
                r, h = r + 1, h - 1
            while w > 1 and not grid.box_free(c, r, w, h):
                w -= 1
                if not grid.box_free(c, r, w, h):
                    c += 1
                    if not grid.box_free(c, r, w, h):
                        c -= 1
            if not grid.box_free(c, r, w, h):
                near = grid.nearest(c, r, 1, 1)
                if near is None:
                    raise ValueError(f"sin sitio para {sid}")
                print(f"  aviso: {sid} se pisa, huella en {near} (quería {fp})")
                c, r = near
                w, h, solid = 1, 1, False
        grid.claim(c, r, w, h, sid)
        dx = o["x"] + sw // 2 - (c * T + w * T // 2)
        dy = o["yb"] - (r + h) * T
        emit(o["kind"], sid, solid, (w, h), (dx, dy), (c, r))

    # Primero lo grande: las casas y lo de la plaza no ceden su sitio.
    order = sorted(pcs, key=lambda o: (0 if o["solid"] == "house" else 1 if o["rows"] > 1 else
                                       2 if o["solid"] == "base" else 3 if o["solid"] in ("trunk", "cell") else 4))
    # El hito y el jardín reservan sus casillas antes que nada.
    oak_pure = TREE
    yara_oak = piece("yara_tree", oak_pure, oak_pure, 84 * T + 8 - foot_x(oak_pure), 21 * T, shadow=0,
                     solid="base", rows=4, kind="landmark")
    sid, sw, sh = reg.add("yara_tree", oak_pure, oak_pure)
    grid.claim(83, 18, 3, 3, sid)
    grid.claim(83, 17, 3, 1, sid)
    dx = yara_oak["x"] + sw // 2 - (83 * T + 3 * T // 2)
    emit("landmark", sid, True, (3, 4), (dx, 0), (83, 17))
    # Sombra del roble en el suelo sano: se pinta aparte, va al pie.
    yara = yara_sprite()
    sid, sw, sh = reg.add("yara", yara, yara)
    grid.claim(86, 21, 1, 1, sid)
    emit("entity", "person", True, (1, 1), (0, 0), (86, 21))
    grid.claim(83, 22, 1, 1, "seedbed")
    emit("entity", "seedbed", True, (1, 1), (0, 0), (83, 22))
    for o in order:
        place(o)

    # La bocamina, la aparición, las matas, los animales y la fauna.
    grid.claim(MINE[0], MINE[1], 2, 2, "blocker")
    emit("entity", "blocker", True, (2, 2), (0, 0), MINE)
    grid.claim(SPAWN[0], SPAWN[1], 1, 1, "spawn")
    emit("spawn", "start", False, (1, 1), (0, 0), SPAWN)
    G = np.array([list(r) for r in spec["ground"]])
    for (r, c) in np.argwhere(G == "t"):
        if grid.free(c, r):
            grid.claim(c, r, 1, 1, "grass")
            emit("decor", "grass", False, (1, 1), (0, 0), (c, r))
    for kind, sid, spots in (
            ("animal", "chicken", [(34, 28), (37, 29), (43, 29), (46, 28)]),
            ("animal", "dog", [(44, 37)]),
            ("animal", "goat", [(37, 38), (41, 39)]),
            ("fauna", "bird", [(84, 22), (30, 58), (20, 20), (60, 9)]),
            ("fauna", "butterfly", [(83, 23), (87, 19), (41, 19), (14, 60), (84, 57)])):
        for at in spots:
            spot = grid.nearest(at[0], at[1], 1, 1)
            grid.claim(*spot, 1, 1, sid)
            emit(kind, sid, False, (1, 1), (0, 0), spot)

    write_zone(rows, legend, cells)
    write_parts(rows, G, cells, legend)
    write_sprites(reg, info0)
    # Comprobación: cada puerta da a su senda.
    for o in pcs:
        if "door" in o:
            c, rd = o["door"]
            if rows[rd][c] != "=" and rows[rd][c + 1] != "=":
                print(f"  FALLA puerta de {o['cat']} en {c},{rd}: no da a un camino")
                return 1
    print(f"  {len(legend)} entradas de leyenda, {len(reg.images)} sprites")
    return 0


def write_zone(rows, legend, cells):
    (ZONES / "valdehoja.txt").write_text("\n".join("".join(r) for r in rows) + "\n", encoding="utf8", newline="\n")
    head = ["; Valdehoja, decorado de la matriz orgánica de 90 × 64. Lo escribe",
            "; tools/gen_tierra_viva_valdehoja.py: no se edita a mano.",
            ";",
            "; Leyenda: carácter = tipo, id, sólido|pisable, ancho x alto en tiles[, desfase]",
            "; El desfase (+x-y, en píxeles) coloca el sprite donde lo pone la referencia."]
    body = []
    for r in range(H):
        body.append("".join(cells.get((c, r), " ") for c in range(W)).rstrip())
    text = "\n".join(head + list(legend.values()) + ["---"] + body) + "\n"
    (ZONES / "valdehoja.deco.txt").write_text(text, encoding="utf8", newline="\n")


def write_parts(rows, G, cells, legend):
    water = G == "w"
    near = ndi.binary_dilation(water, iterations=1)
    fields = ndi.binary_dilation(np.isin(G, ["u", "t"]), iterations=1)
    part = np.full((H, W), ".", dtype="<U1")
    part[1:15, 5:77] = "A"           # la terraza norte
    part[15:30, 1:29] = "L"          # el huerto y el pozo
    part[fields] = "L"
    part[55:63, 1:76] = "B"          # la arboleda del sur
    part[fields] = "L"
    part[16:30, 29:53] = "K"         # la plaza del Árbol del Vínculo
    part[near] = "C"                 # el río y el lago
    part[:13][near[:13]] = "A"       # lo alto del río: la acequia de la terraza
    part[0:4, 2:6] = "G"             # la bocamina
    c0, r0, c1, r1 = GARDEN
    # El jardín llega hasta el borde del mapa; el río sigue siendo del río.
    garden_mask = np.zeros((H, W), bool)
    garden_mask[r0:r1 + 1, c0:W] = True
    part[garden_mask & ~near] = "Y"
    head = ["; Valdehoja, partes del pueblo. Lo escribe tools/gen_tierra_viva_valdehoja.py.",
            "; Y = yara_garden", "; B = ashen_forest", "; C = tar_basin", "; K = broken_coast",
            "; L = withered_plain", "; A = waning_peak", "; G = greed_crypt", "---"]
    text = "\n".join(head + ["".join(r) for r in part]) + "\n"
    (ZONES / "valdehoja.parts.txt").write_text(text, encoding="utf8", newline="\n")


def write_sprites(reg, info):
    for sid, (sick, pure) in reg.images.items():
        for state, img in (("sick", sick), ("pure", pure)):
            Image.fromarray(img, "RGBA").save(SPRITES / f"{sid}_valdehoja_{state}.png")
    # Las matas de hierba alta, de la misma mano que la referencia.
    for state, tag in (("enfermo", "sick"), ("sano", "pure")):
        P = map2.palette(state, "bosque")
        Image.fromarray(tall_tuft(P, seed=3, sway=0), "RGBA").save(SPRITES / f"grass_valdehoja_{tag}.png")
        if tag == "pure":
            Image.fromarray(tall_tuft(P, seed=3, sway=1), "RGBA").save(SPRITES / "grass_valdehoja_pure_1.png")


if __name__ == "__main__":
    sys.exit(main())
