"""Decorado «Tierra Viva» (contrato «Piel nueva», paso 4b; guía del equipo §4.2).

    python tools/gen_tierra_viva_decor.py ashen_forest

Dibuja los objetos del catálogo de una zona (`data/world/zones/<zona>.deco.txt`)
con el estilo del sistema de diseño (`docs/ux/sistema-de-diseno/project/README.md`
§Mundo) y los escribe en `assets/sprites/world/tierra_viva/` como
`<id>_<zona>_<estado>.png`, con estado `pure` o `sick`. `WorldDecor` busca
primero ahí y después en el decorado viejo (`tools/gen_world_decor.py`), así
que una zona cambia entera de estilo cuando tiene sus piezas aquí y las demás
siguen como estaban.

Reglas del sistema que se cumplen aquí:

- **Mismo vocabulario que la masa del suelo**: el árbol es el de
  `gen_tierra_viva_terrain.piece` (racimos de copa con luz arriba a la
  izquierda), y un árbol suelto del borde se lee igual que los del muro.
- **Contorno** del tono más oscuro de la rampa de la propia pieza. Solo lo que
  responde al jugador (el semillero) lleva `ash_050`.
- **El árbol quemado es el mismo árbol sin copa, con hollín al pie**, y la
  misma posición vale para el sano y el quemado.
- **En lo enfermo todo se asienta en el daño**: la madera, carbonizada; al pie
  de cada pieza, cerco de ceniza en vez de sombra sobre hierba.
- **Paleta**: cada píxel opaco es un token `TV_*` permitido en su estado (lo
  enfermo no usa rampas de solo-purificado, ni lo sano de solo-enfermo).
- **Semilla fija** por pieza: regenerar da los mismos bytes.

El monstruo del mapa no va aquí: es un personaje de 48 px del sistema
(PixelLab, `assets/source/pixellab/`) y entra con el grupo a esa escala.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_tierra_viva_terrain as tv  # noqa: E402
from pixel import PALETTE  # noqa: E402

ROOT = tv.ROOT
OUT = ROOT / "assets" / "sprites" / "world" / "tierra_viva"
INK = np.array(PALETTE["ash_050"], np.uint8)


def rgba(c) -> np.ndarray:
    return np.array([c[0], c[1], c[2], 255], np.uint8)


def canvas(w: int, h: int) -> np.ndarray:
    return np.zeros((h, w, 4), np.uint8)


def ellipse(w: int, h: int, cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1


def foot(img: np.ndarray, cx: float, cy: float, rx: float, ry: float, P: dict, sick: bool) -> None:
    """Lo que hay al pie, debajo de la pieza: sombra sobre hierba en lo sano;
    en lo enfermo, cerco de ceniza tramado con hollín en el centro."""
    h, w = img.shape[:2]
    m = ellipse(w, h, cx, cy, rx, ry) & (img[..., 3] == 0)
    if sick:
        ash = P["ash"]
        yy, xx = np.indices((h, w))
        core = ellipse(w, h, cx, cy, rx * 0.65, ry * 0.65)
        img[m] = rgba(ash[1])
        img[m & ~core & ((xx + yy) % 2 == 0)] = rgba(ash[2])
        img[m & core] = rgba(ash[0])
    else:
        g = P["grass"]
        core = ellipse(w, h, cx, cy, rx * 0.7, ry * 0.7)
        img[m] = rgba(g[2])
        img[m & core] = rgba(g[1])


def place(dst: np.ndarray, spr: np.ndarray, foot_x: int, foot_y: int) -> None:
    """Pega `spr` con el centro de su fila de abajo en (foot_x, foot_y)."""
    h, w = spr.shape[:2]
    tv.blit(dst, spr, foot_x - w // 2, foot_y - h + 1)


# --- piezas --------------------------------------------------------------------------

def canopy_tree(P: dict, rs, circles, W=28, H=38, crown=27) -> np.ndarray:
    """El árbol de la masa con otra copa (racimos dados)."""
    img = canvas(W, H)
    tv.trunk(img, W // 2, crown - 5, H, P["wood"])
    top, _ = tv.clumps(W, crown, circles, P["leaf"])
    tv.blit(img, tv.outlined(top, P["leaf"][0]), 0, 0)
    return img


def tree(P: dict, sick: bool, variant: int) -> np.ndarray:
    """Árbol de 2×2 casillas (32×40). Sano, con copa; enfermo, el mismo árbol
    sin copa (`burnt`). La variante cambia la copa y las ramas."""
    rs = np.random.default_rng(100 + variant)
    img = canvas(32, 40)
    foot(img, 16, 37, 13, 3.5, P, sick)
    if sick:
        spr = tv.piece("burnt_embers" if variant == 2 else "burnt", P, rs)
        if variant == 2:
            # el gradiente hacia la fuente: este siempre lleva brasas
            fire = P["fire"]
            spr[16, 13:15] = rgba(fire[2])
            for x, y in ((5, 6), (22, 5), (9, 3)):
                if spr[y, x, 3]:
                    spr[y, x] = rgba(fire[4])
    else:
        circles = [
            [(14, 11, 10), (7, 15, 7), (21, 15, 7), (10, 7, 6), (19, 7, 6)],
            [(13, 12, 9), (6, 16, 6), (22, 14, 7), (17, 6, 7), (8, 8, 5)],
            [(14, 10, 9), (8, 16, 7), (20, 16, 7), (14, 5, 6)],
        ][variant]
        spr = canopy_tree(P, rs, circles)
    place(img, spr, 16, 38)
    return img


def oak(P: dict, sick: bool) -> np.ndarray:
    """Hito: el roble mayor. Ocupa 3×4 casillas, pero el sprite mide 64×80 y
    desborda su huella hacia arriba y a los lados: es la pieza que se tiene
    que reconocer desde lejos (a 48×64 se confundía con el muro de árboles,
    captura del 2026-11-01). Sano, copa de muchos racimos sobre tronco ancho;
    enfermo, carbonizado con grietas en brasa (`arbol_quemado` del sistema),
    sobre su cerco de ceniza."""
    W, H = 64, 80
    cx = W // 2
    img = canvas(W, H)
    foot(img, cx, 76, 27, 5, P, sick)
    rs = np.random.default_rng(7)
    wood = P["ash"] if sick else P["wood"]
    t = canvas(W, H)
    # tronco de 14 px que se abre en raíces
    t[38:78, cx - 7:cx + 7] = rgba(wood[2])
    t[38:78, cx - 7:cx - 2] = rgba(wood[3])
    t[38:78, cx + 3:cx + 7] = rgba(wood[1])
    for x0, x1 in ((cx - 6, cx - 18), (cx + 6, cx + 18), (cx - 3, cx - 10), (cx + 3, cx + 10)):
        tv.line(t, x0, 70, x1, 78, rgba(wood[2]), 3)
    for y in range(42, 74, 4):
        t[y, cx - 1:cx + 1] = rgba(wood[1])
        t[y + 2, cx + 1:cx + 3] = rgba(wood[1])
    if sick:
        tips = []
        for a in (-2.85, -2.5, -2.15, -1.8, -1.57, -1.3, -0.95, -0.6, -0.3):
            a += rs.uniform(-0.08, 0.08)
            ln = rs.uniform(24, 30)
            x1, y1 = cx + np.cos(a) * ln, 40 + np.sin(a) * ln
            tv.line(t, cx, 42, x1, y1, rgba(wood[1]), 4)
            for d in (-0.6, 0.5):
                tx, ty = x1 + np.cos(a + d) * 9, y1 + np.sin(a + d) * 9
                tv.line(t, x1, y1, tx, ty, rgba(wood[2]), 2)
                tips.append((int(tx), int(ty)))
        t = tv.outlined(t, rgba(wood[0]))
        fire = P["fire"]
        # grietas en brasa por el tronco: la causa sigue activa
        for x, y0, y1 in ((cx - 3, 44, 54), (cx + 1, 56, 68), (cx - 4, 62, 66)):
            t[y0:y1, x] = rgba(fire[3])
            t[(y0 + y1) // 2, x] = rgba(fire[5])
        for k, (x, y) in enumerate(tips[::2]):
            if 0 <= y < H and 0 <= x < W and t[y, x, 3]:
                t[y, x] = rgba(fire[4 if k % 2 else 3])
    else:
        circles = [(cx, 22, 19), (13, 30, 12), (51, 30, 12), (19, 14, 13), (45, 14, 13),
                   (cx, 8, 11), (7, 21, 8), (57, 21, 8), (23, 37, 10), (41, 37, 10)]
        top, _ = tv.clumps(W, 50, circles, P["leaf"])
        tv.blit(t, top, 0, 0)
        t = tv.outlined(t, rgba(P["leaf"][0]))
    img[t[..., 3] > 0] = t[t[..., 3] > 0]
    return img


def stump(P: dict, sick: bool) -> np.ndarray:
    """Tocón de corte limpio (16×16): anillos arriba, corteza al lado."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7, 2.5, P, sick)
    w = P["ash"] if sick else P["wood"]
    s = canvas(16, 16)
    s[7:14, 3:13] = rgba(w[2])
    s[7:14, 3:5] = rgba(w[3])
    s[7:14, 11:13] = rgba(w[1])
    top = ellipse(16, 16, 8, 7, 5, 2.5)
    s[top] = rgba(w[4])
    s[ellipse(16, 16, 8, 7, 3, 1.4)] = rgba(w[3])
    s[7, 8] = rgba(w[5])
    s[13, 2:4] = rgba(w[2])
    s[13, 12:14] = rgba(w[2])
    s = tv.outlined(s, rgba(w[0]))
    if not sick:
        # brote nuevo junto al corte
        leaf = P["leaf"]
        s[3:6, 11] = rgba(leaf[3])
        s[3, 12] = rgba(leaf[5])
        s[4, 10] = rgba(leaf[4])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def log_end(s: np.ndarray, cx: int, cy: int, r: int, w: list) -> None:
    h, wd = s.shape[:2]
    s[ellipse(wd, h, cx, cy, r, r)] = rgba(w[4])
    s[ellipse(wd, h, cx, cy, r * 0.55, r * 0.55)] = rgba(w[3])
    s[cy, cx] = rgba(w[5])


def felled_log(P: dict, sick: bool) -> np.ndarray:
    """El tronco talado (2×1, 32×16), tendido de oeste a este."""
    img = canvas(32, 16)
    foot(img, 16, 13.5, 15, 2.5, P, sick)
    w = P["ash"] if sick else P["wood"]
    s = canvas(32, 16)
    s[5:13, 2:27] = rgba(w[2])
    s[5:7, 2:27] = rgba(w[3])
    s[11:13, 2:27] = rgba(w[1])
    for x in range(5, 25, 6):
        s[8, x:x + 3] = rgba(w[1])
    log_end(s, 27, 8, 4, w)
    s = tv.outlined(s, rgba(w[0]))
    if sick:
        s[9, 14:16] = rgba(P["fire"][2])
    else:
        leaf = P["leaf"]
        for x in (6, 13, 19):
            s[4, x:x + 2] = rgba(leaf[3])
            s[3, x] = rgba(leaf[5])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def log_pile(P: dict, sick: bool) -> np.ndarray:
    """La madera que se llevan (2×2, 32×32): troncos apilados de punta."""
    img = canvas(32, 32)
    foot(img, 16, 28.5, 15, 3, P, sick)
    w = P["ash"] if sick else P["wood"]
    s = canvas(32, 32)
    for row, (n, y) in enumerate(((4, 25), (3, 18), (2, 11))):
        x0 = 16 - (n - 1) * 3.5
        for k in range(n):
            log_end(s, int(round(x0 + k * 7)), y, 3, w)
    s = tv.outlined(s, rgba(w[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def ash_patch(P: dict, sick: bool) -> np.ndarray:
    """Ceniza en el suelo (16×16, pisable). Purificada, la ceniza da flores."""
    img = canvas(16, 16)
    rs = np.random.default_rng(12)
    if sick:
        # mancha de ceniza tramada que deja ver el suelo entre los granos: se
        # lee como suelo quemado, no como piedras sueltas (captura del
        # 2026-11-01: con núcleo claro parecían guijarros)
        ash = P["ash"]
        yy, xx = np.indices((16, 16))
        n = rs.random((16, 16))
        blob = (ellipse(16, 16, 6, 9, 5, 3.2) | ellipse(16, 16, 10.5, 10, 4.5, 3)) & (n > 0.15)
        img[blob & ((xx + yy) % 2 == 0)] = rgba(ash[2])
        img[blob & ((xx + yy) % 2 == 1) & (n > 0.6)] = rgba(ash[3])
        for x, y in ((5, 9), (11, 10), (8, 8)):
            img[y, x] = rgba(ash[4])
    else:
        fl, leaf = P["flower"], P["leaf"]
        for x, y, c in ((5, 8, 6), (10, 10, 4), (7, 12, 6)):
            img[y + 1:y + 3, x] = rgba(leaf[3])
            img[y, x - 1:x + 2] = rgba(fl[c - 2])
            img[y - 1:y + 2, x] = rgba(fl[c - 2])
            img[y, x] = rgba(fl[7])
    return img


def tall_grass(P: dict, sick: bool, sway: int) -> np.ndarray:
    """Hierba alta (16×16): una mata densa en V con forma, no un rectángulo.
    `sway` inclina las puntas un píxel (segundo cuadro del mecerse)."""
    img = canvas(16, 16)
    g = P["grass"]
    blades = [(1, 9), (3, 6), (5, 8), (7, 4), (9, 7), (11, 5), (13, 8), (14, 10), (6, 10), (10, 10)]
    for k, (x, top) in enumerate(blades):
        for y in range(top, 15):
            lean = sway if y < top + 3 else 0
            c = 4 if k % 2 else 5
            if y >= 12:
                c = 2
            img[y, min(15, max(0, x + lean))] = rgba(g[c])
        img[top, min(15, max(0, x + sway))] = rgba(g[6])
    img[14, 1:15] = rgba(g[1])
    img[15, 2:14] = rgba(g[0])
    return img


def rock(P: dict) -> np.ndarray:
    """Roca partida (16×16): piedra en bloque con grieta y luz arriba."""
    img = canvas(16, 16)
    st = P["stone"]
    m = ellipse(16, 16, 8, 10, 6.5, 4.5)
    s = canvas(16, 16)
    yy, xx = np.indices((16, 16))
    s[m] = rgba(st[3])
    s[m & (yy < 9)] = rgba(st[4])
    s[m & (yy < 8) & (xx < 8)] = rgba(st[5])
    s[m & (yy > 11)] = rgba(st[2])
    tv.line(s, 9, 6, 7, 11, rgba(st[1]))
    s = tv.outlined(s, rgba(st[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def seedbed(P: dict) -> np.ndarray:
    """Semillero del ramal norte (16×16): cajón de madera con tierra y
    semillas. Responde al jugador: contorno `ash_050`."""
    w, d, gold = P["wood"], P["dirt"], P["gold"]
    s = canvas(16, 16)
    s[6:14, 2:14] = rgba(w[2])
    s[6:8, 2:14] = rgba(w[4])
    s[8:14, 2:3] = rgba(w[3])
    s[10, 2:14] = rgba(w[1])
    s[7:9, 4:12] = rgba(d[2])
    for x in (5, 8, 11):
        s[7, x] = rgba(gold[4])
    return tv.outlined(s, rgba(INK))


def blocker(P: dict, sick: bool) -> np.ndarray:
    """Paso cerrado del Bosque (16×16): troncos cruzados en brasas. Con la ola
    desaparece; el sano es el mismo montón ya frío."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7.5, 2.5, P, True)
    a = P["ash"]
    s = canvas(16, 16)
    tv.line(s, 2, 12, 13, 5, rgba(a[2]), 2)
    tv.line(s, 2, 5, 13, 12, rgba(a[3]), 2)
    tv.line(s, 3, 9, 13, 9, rgba(a[1]), 2)
    s = tv.outlined(s, rgba(a[0]))
    if sick:
        fire = P["fire"]
        for x, y, c in ((7, 8, 5), (8, 8, 4), (5, 7, 3), (10, 10, 3), (8, 4, 2), (7, 3, 1)):
            s[y, x] = rgba(fire[c])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


# --- catálogo por zona -------------------------------------------------------------------

def forest() -> dict[str, np.ndarray]:
    out = {}
    for state in ("sick", "pure"):
        sick = state == "sick"
        P = tv.palette("enfermo" if sick else "sano", "bosque")
        out[f"tree_{state}"] = tree(P, sick, 0)
        out[f"tree_b_{state}"] = tree(P, sick, 1)
        out[f"burnt_tree_{state}"] = tree(P, sick, 2)
        out[f"burnt_oak_{state}"] = oak(P, sick)
        out[f"stump_{state}"] = stump(P, sick)
        out[f"felled_log_{state}"] = felled_log(P, sick)
        out[f"log_pile_{state}"] = log_pile(P, sick)
        out[f"ash_{state}"] = ash_patch(P, sick)
        out[f"grass_{state}"] = tall_grass(P, sick, 0)
        out[f"blocker_{state}"] = blocker(P, sick)
        if not sick:
            out["grass_pure_1"] = tall_grass(P, False, 1)
    P = tv.palette("enfermo", "bosque")
    out["rock_sick"] = rock(P)
    out["seedbed_sick"] = seedbed(P)
    return out


CATALOG = {"ashen_forest": forest}


def quantize(img: np.ndarray, state: str) -> int:
    """Como el del suelo, pero conserva la transparencia."""
    colors = tv.allowed_colors("enfermo" if state == "sick" else "sano")
    colors = np.vstack([colors, INK[None, :3].astype(np.int32)])
    m = img[..., 3] > 0
    px = img[m][:, :3].astype(np.int32)
    if len(px) == 0:
        return 0
    d = ((px[:, None, :] - colors[None, :, :]) ** 2).sum(-1)
    near = colors[d.argmin(1)]
    moved = int((near != px).any(1).sum())
    img[m, :3] = near.astype(np.uint8)
    img[m, 3] = 255
    return moved


def main(argv: list[str]) -> int:
    zones = argv or list(CATALOG)
    OUT.mkdir(parents=True, exist_ok=True)
    for zone in zones:
        if zone not in CATALOG:
            print(f"  FALLA {zone}: sin catálogo ({', '.join(CATALOG)})")
            return 1
        for name, img in CATALOG[zone]().items():
            state = "pure" if "_pure" in name else "sick"
            moved = quantize(img, state)
            stem, tail = name.rsplit(f"_{state}", 1)
            path = OUT / f"{stem}_{zone}_{state}{tail}.png"
            Image.fromarray(img, "RGBA").save(path)
            print(f"  {path.relative_to(ROOT)}: {img.shape[1]}×{img.shape[0]}, {moved} px llevados a su token")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
