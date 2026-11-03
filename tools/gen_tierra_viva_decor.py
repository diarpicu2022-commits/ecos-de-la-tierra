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
    en lo enfermo, cerco del daño de la región (`stain`; ceniza si no hay)
    tramado, con el tono más oscuro en el centro."""
    h, w = img.shape[:2]
    m = ellipse(w, h, cx, cy, rx, ry) & (img[..., 3] == 0)
    if sick:
        ash = P.get("stain", P["ash"])
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


# --- piezas de la Cuenca -----------------------------------------------------------------
# Daño de crudo (`oil` + `sheen`, README del sistema §Mundo): lo enfermo se
# asienta en una mancha de crudo con reflejo irisado, no en ceniza. Lo que se
# limpia con la ola (crudo, barriles y el paso cerrado) solo tiene sprite
# enfermo: `WorldDecor.VANISH_WHEN_PURE` no lo monta purificado.

def oil_puddle(img: np.ndarray, cx: float, cy: float, rx: float, ry: float, P: dict) -> None:
    """Charco de crudo sobre lo transparente: borde, cuerpo, fondo y dos
    reflejos de `sheen`."""
    h, w = img.shape[:2]
    oil, sh = P["oil"], P["sheen"]
    m = ellipse(w, h, cx, cy, rx, ry) & (img[..., 3] == 0)
    img[m] = rgba(oil[2])
    img[m & ellipse(w, h, cx, cy, rx - 1, ry - 0.8)] = rgba(oil[1])
    img[m & ellipse(w, h, cx + 0.5, cy + 0.3, rx * 0.5, ry * 0.5)] = rgba(oil[0])
    for dx, c in ((-rx * 0.45, 2), (-rx * 0.45 + 1, 3)):
        x, y = int(cx + dx), int(cy - ry * 0.35)
        if 0 <= y < h and 0 <= x < w and m[y, x]:
            img[y, x] = rgba(sh[c])


def oil_patch(P: dict) -> np.ndarray:
    """Mancha de crudo en el suelo (16×16, pisable): dos lóbulos con el borde
    más claro y el reflejo irisado en arco."""
    img = canvas(16, 16)
    oil, sh = P["oil"], P["sheen"]
    blob = ellipse(16, 16, 6.5, 9, 5.5, 3.4) | ellipse(16, 16, 10.5, 10.5, 4, 2.6)
    img[blob] = rgba(oil[2])
    inner = tv.ndi.binary_erosion(blob)
    img[inner] = rgba(oil[1])
    img[inner & (ellipse(16, 16, 6.5, 9.5, 3, 1.8) | ellipse(16, 16, 11, 11, 2, 1.2))] = rgba(oil[0])
    for x, y, c in ((4, 8, 2), (5, 7, 3), (6, 7, 2), (9, 9, 1), (10, 9, 2)):
        img[y, x] = rgba(sh[c])
    return img


def barrel(P: dict) -> np.ndarray:
    """Barril volcado (16×16): bidón azul tendido, con la boca abierta hacia el
    este y el crudo que se sale."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7, 2.5, P, True)
    b, oil = P["roof_blue"], P["oil"]
    s = canvas(16, 16)
    s[5:13, 2:12] = rgba(b[3])
    s[5:7, 2:12] = rgba(b[4])
    s[11:13, 2:12] = rgba(b[2])
    s[5:13, 5] = rgba(b[1])
    s[5:13, 9] = rgba(b[1])
    s[ellipse(16, 16, 12, 9, 2.5, 4)] = rgba(b[2])
    s[ellipse(16, 16, 12.3, 9.3, 1.3, 2.6)] = rgba(oil[0])
    s = tv.outlined(s, rgba(b[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    oil_puddle(img, 14, 13.5, 2.5, 1.8, P)
    return img


def broken_pipe(P: dict, sick: bool) -> np.ndarray:
    """Tubería (2×1, 32×16) tendida de oeste a este. Enferma, partida por la
    mitad y soltando crudo; purificada, empalmada con un collar y con hierba
    que vuelve a crecer al pie."""
    img = canvas(32, 16)
    foot(img, 16, 13.5, 15, 2.5, P, sick)
    st, ru = P["stone"], P["rust"]
    s = canvas(32, 16)
    s[6:12, 1:31] = rgba(st[3])
    s[6, 1:31] = rgba(st[5])
    s[7, 1:31] = rgba(st[4])
    s[11, 1:31] = rgba(st[1])
    for x in (1, 27):
        s[4:14, x:x + 3] = rgba(ru[2])
        s[4, x:x + 3] = rgba(ru[3])
    if sick:
        # rotura: dos cabos dentados y la boca negra
        s[6:12, 14:18] = 0
        for y in (6, 8, 10):
            s[y, 14] = rgba(st[3])
        for y in (7, 9, 11):
            s[y, 17] = rgba(st[3])
        s[8:11, 13] = rgba(st[0])
        s[7:10, 18] = rgba(st[0])
    else:
        s[5:13, 13:19] = rgba(ru[2])
        s[5, 13:19] = rgba(ru[3])
        for x in (14, 17):
            s[8, x] = rgba(ru[4])
    s = tv.outlined(s, rgba(st[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    if sick:
        oil = P["oil"]
        img[9:13, 15:17] = rgba(oil[1])
        img[9, 15] = rgba(P["sheen"][2])
        oil_puddle(img, 16, 13.5, 6, 2.2, P)
    else:
        g = P["grass"]
        for x in (4, 9, 21, 25):
            img[12:14, x] = rgba(g[4])
            img[11, x] = rgba(g[5])
    return img


def boat(P: dict, sick: bool) -> np.ndarray:
    """Barca de pesca (2×1, 32×16), proa al este. Enferma, varada en el crudo
    con el casco negro hasta la línea del charco y la pintura apagada;
    purificada, limpia y con el remo dentro."""
    img = canvas(32, 16)
    foot(img, 16, 13, 15, 2.8, P, sick)
    w, red = P["wood"], P["roof_red"]
    yy, xx = np.indices((16, 32))
    # casco visto desde arriba y un poco de lado: la borda, el interior de
    # tablas y el costado sur, más oscuro
    # popa recta al oeste y proa en punta al este: se lee como barca, no como
    # disco (captura del 2026-11-02)
    taper = np.clip(1 - (xx + 0.5 - 20) / 12, 0, 1)
    hull = (np.abs(yy + 0.5 - 8.5) <= 6 * np.sqrt(taper)) & (xx >= 2)
    deck = (np.abs(yy + 0.5 - 7.8) <= 3.6 * np.sqrt(np.clip(1 - (xx + 0.5 - 18) / 10, 0, 1))) & (xx >= 4)
    s = canvas(32, 16)
    paint = (red[2], red[1], red[3]) if sick else (red[4], red[2], red[5])
    s[hull] = rgba(paint[0])
    s[hull & ~deck & (yy >= 10)] = rgba(paint[1])
    s[hull & ~deck & (yy <= 5)] = rgba(paint[2])
    s[deck] = rgba(w[3] if sick else w[4])
    s[deck & (yy <= 5)] = rgba(w[4] if sick else w[5])
    for x in (8, 15, 21):
        s[deck & (xx == x)] = rgba(w[1])
    if sick:
        s[hull & ~deck & (yy >= 11)] = rgba(P["oil"][1])
        s[12, 6:9] = rgba(P["sheen"][2])
    else:
        tv.line(s, 9, 9, 22, 8, rgba(w[1]))
        s[8, 22:24] = rgba(w[2])
    s = tv.outlined(s, rgba(red[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def torn_net(P: dict, sick: bool) -> np.ndarray:
    """La red de los pescadores tendida en el suelo (16×16, pisable). Enferma,
    rota y manchada de crudo; purificada, remendada y con los flotadores."""
    img = canvas(16, 16)
    yy, xx = np.indices((16, 16))
    area = ellipse(16, 16, 8, 10, 7, 4.5)
    mesh = area & (((xx + yy) % 3 == 0) | ((xx - yy) % 3 == 0))
    if sick:
        st, oil = P["stone"], P["oil"]
        mesh &= ~ellipse(16, 16, 6, 9, 2.2, 1.6) & ~ellipse(16, 16, 11, 11, 1.6, 1.2)
        # cuerda clara: sobre la hierba de lodo, la gris media no se veía
        # (captura del 2026-11-02)
        img[mesh] = rgba(st[5])
        img[mesh & ((xx + 2 * yy) % 7 == 0)] = rgba(st[3])
        img[mesh & ellipse(16, 16, 10, 8, 2.5, 1.5)] = rgba(oil[1])
        img[12, 3] = rgba(P["roof_red"][1])
    else:
        w, red = P["wood"], P["roof_red"]
        img[mesh] = rgba(w[5])
        img[mesh & ((xx + 2 * yy) % 7 == 0)] = rgba(w[3])
        for x, y in ((3, 8), (8, 6), (13, 9)):
            img[y, x:x + 2] = rgba(red[4])
            img[y + 1, x:x + 2] = rgba(red[2])
    return img


def refinery_tower(P: dict, sick: bool) -> np.ndarray:
    """Hito: la torre de la refinería de Puerto Brea. Huella de 3×4 casillas;
    el sprite (56×84) la desborda hacia arriba, como el roble del Bosque, para
    leerse desde lejos. Enferma, con la llama de la antorcha encendida y el
    crudo que chorrea; purificada, apagada y con la enredadera que la sube."""
    W, H = 56, 84
    cx = W // 2
    img = canvas(W, H)
    foot(img, cx, 80, 25, 4.5, P, sick)
    st, ru = P["stone"], P["rust"]
    t = canvas(W, H)
    # losa
    t[77:83, 8:48] = rgba(st[2])
    t[77, 8:48] = rgba(st[4])
    # columna principal con luz a la izquierda
    t[14:77, cx - 8:cx + 8] = rgba(st[3])
    t[14:77, cx - 8:cx - 4] = rgba(st[4])
    t[14:77, cx - 8] = rgba(st[5])
    t[14:77, cx + 5:cx + 8] = rgba(st[1])
    t[10:14, cx - 6:cx + 6] = rgba(st[4])
    t[10, cx - 4:cx + 4] = rgba(st[5])
    # columna lateral y su conducto
    t[40:77, 40:47] = rgba(st[3])
    t[40:77, 40:42] = rgba(st[4])
    t[38:40, 41:46] = rgba(st[4])
    t[50:53, cx + 8:40] = rgba(st[2])
    # antorcha
    t[3:10, cx + 1:cx + 3] = rgba(st[2])
    # plataformas con barandilla
    for y in (26, 44, 62):
        t[y:y + 3, cx - 12:cx + 12] = rgba(ru[2])
        t[y, cx - 12:cx + 12] = rgba(ru[3])
        t[y - 3:y, cx - 12] = rgba(ru[1])
        t[y - 3:y, cx + 11] = rgba(ru[1])
        t[y - 3, cx - 12:cx + 12:3] = rgba(ru[1])
    # escalera
    t[14:77, cx + 3] = rgba(ru[1])
    t[14:77, cx + 6] = rgba(ru[1])
    t[16:77:3, cx + 3:cx + 7] = rgba(ru[2])
    if sick:
        # óxido a manchas
        for x, y in ((cx - 6, 33), (cx - 2, 52), (43, 60), (cx - 5, 70)):
            t[y:y + 3, x:x + 2] = rgba(ru[1])
    t = tv.outlined(t, rgba(st[0]))
    if sick:
        oil, sh, fire = P["oil"], P["sheen"], P["fire"]
        for x, y0, y1 in ((cx - 3, 29, 44), (cx - 6, 47, 60), (43, 55, 76)):
            t[y0:y1, x] = rgba(oil[1])
            t[y1 - 1, x] = rgba(oil[0])
        t[35, cx - 3] = rgba(sh[2])
        # llama de la antorcha: la causa sigue activa
        flame = [(cx + 1, 2, 3), (cx + 2, 2, 3), (cx + 1, 1, 4), (cx + 2, 0, 5), (cx, 2, 2), (cx + 3, 1, 2),
                 (cx + 1, 0, 4)]
        for x, y, c in flame:
            t[y, x] = rgba(fire[c])
    else:
        # enredadera de hoja por la columna y el pie, y flores en la losa
        leaf, fl = P["leaf"], P["flower"]
        for k, y in enumerate(range(74, 34, -3)):
            x = cx - 8 + (k % 2)
            t[y:y + 2, x] = rgba(leaf[3])
            t[y, x + 1 - 2 * (k % 2)] = rgba(leaf[5])
        for x, y in ((12, 76), (18, 76), (44, 76)):
            t[y, x] = rgba(fl[5])
            t[y, x + 1] = rgba(leaf[4])
    img[t[..., 3] > 0] = t[t[..., 3] > 0]
    return img


def tar_blocker(P: dict) -> np.ndarray:
    """Paso cerrado de la Cuenca (16×16): tuberías retorcidas hundidas en el
    crudo. Con la ola desaparece (solo hay sprite enfermo)."""
    img = canvas(16, 16)
    oil_puddle(img, 8, 13, 7.5, 2.8, P)
    st, ru = P["stone"], P["rust"]
    s = canvas(16, 16)
    tv.line(s, 1, 12, 14, 4, rgba(st[3]), 2)
    tv.line(s, 2, 4, 9, 9, rgba(st[2]), 2)
    tv.line(s, 9, 9, 13, 13, rgba(st[2]), 2)
    s[6:8, 6:8] = rgba(ru[2])
    s[9:11, 9:11] = rgba(ru[3])
    s = tv.outlined(s, rgba(st[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    img[13, 3:6] = rgba(P["oil"][1])
    img[12, 11] = rgba(P["sheen"][2])
    return img


def shrub(P: dict, sick: bool) -> np.ndarray:
    """Arbusto de la marisma (18×16): enfermo, ramitas secas (regla del
    sistema); purificado, la mata de la masa con bayas."""
    img = canvas(18, 16)
    foot(img, 9, 14, 8, 2, P, sick)
    rs = np.random.default_rng(31)
    if sick:
        place(img, tv.piece("twigs", P, rs), 9, 15)
    else:
        b = tv.piece("bush", P, rs)
        for x, y in ((5, 6), (12, 5), (9, 9)):
            b[y, x] = rgba(P["flower"][4])
        place(img, b, 9, 15)
    return img


def reeds(P: dict, sick: bool, sway: int = 0) -> np.ndarray:
    """Juncos de la orilla (16×16). Purificados, verdes con espadañas de
    madera; enfermos, secos, doblados y con el pie en crudo. `sway` inclina las
    puntas (segundo cuadro del mecerse)."""
    img = canvas(16, 16)
    stems = [(2, 4), (4, 2), (6, 5), (8, 1), (10, 4), (12, 3), (14, 6)]
    g = P["dead"] if sick else P["grass"]
    for k, (x, top) in enumerate(stems):
        if sick and k % 3 == 1:
            top += 4   # el junco partido
        for y in range(top, 15):
            lean = sway if y < top + 4 else 0
            img[y, min(15, max(0, x + lean))] = rgba(g[4 if k % 2 else 3])
        img[top, min(15, max(0, x + sway))] = rgba(g[5])
        if not sick and k % 2 == 1:
            hx = min(15, max(0, x + sway))
            img[top + 1:top + 4, hx] = rgba(P["wood"][2])
            img[top + 1, hx] = rgba(P["wood"][3])
    if sick:
        oil = P["oil"]
        img[13:15, 1:15] = rgba(oil[1])
        img[15, 2:14] = rgba(oil[0])
        img[13, 4] = rgba(P["sheen"][2])
    else:
        img[14, 1:15] = rgba(g[1])
        img[15, 2:14] = rgba(g[0])
    return img


# --- piezas de la Costa ------------------------------------------------------------------
# Daño de residuos (`plastic`, README del sistema §Mundo): la basura va suelta y
# dispersa, nunca en fardos (`broken_coast.deco.txt`). La rampa `plastic` mezcla
# los colores de la basura de verdad (azul de botella, tapa roja y amarilla,
# blanco de bolsa); todo lo que se limpia con la ola solo tiene sprite enfermo.

def bottle_at(img: np.ndarray, x: int, y: int, pl: list, dx: int = 1) -> None:
    """Botella tumbada de 6 px hacia `dx`, con su tapa."""
    for k in range(5):
        img[y, x + dx * k] = rgba(pl[1])
        img[y - 1, x + dx * k] = rgba(pl[2] if k else pl[1])
    img[y - 1, x + dx] = rgba(pl[3])
    img[y, x + dx * 5] = rgba(pl[4])


def litter(P: dict) -> np.ndarray:
    """Basura suelta (16×16, pisable): una botella, tapas y un trozo de bolsa,
    separados, para que se lea como dispersa."""
    img = canvas(16, 16)
    pl, st = P["plastic"], P["stone"]
    bottle_at(img, 3, 6, pl)
    img[11, 11] = rgba(pl[4])
    img[4, 12] = rgba(pl[5])
    img[13, 4:6] = rgba(pl[6])
    img[12, 5] = rgba(st[5])
    img[9, 8] = rgba(pl[3])
    return img


def bottle(P: dict) -> np.ndarray:
    """Botella tumbada en la arena (16×16, pisable), en diagonal."""
    img = canvas(16, 16)
    pl = P["plastic"]
    s = canvas(16, 16)
    for k in range(8):
        x, y = 3 + k, 11 - k // 2
        s[y - 1:y + 1, x] = rgba(pl[1])
        s[y - 1, x] = rgba(pl[2])
    s[7, 6:9] = rgba(pl[3])
    s[6:8, 11] = rgba(pl[1])
    s[6, 12] = rgba(pl[4])
    s = tv.outlined(s, rgba(pl[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def torn_bag(P: dict) -> np.ndarray:
    """Bolsa rota (16×16, pisable): blanca, arrugada y con el desgarro."""
    img = canvas(16, 16)
    st = P["stone"]
    s = canvas(16, 16)
    s[ellipse(16, 16, 8, 10, 5.5, 3.5)] = rgba(st[6])
    s[ellipse(16, 16, 9, 11, 3.5, 2)] = rgba(st[5])
    for x, y in ((5, 9), (8, 10), (10, 9)):
        s[y, x] = rgba(st[4])
    s[7:10, 12:14] = 0   # el desgarro
    s[6, 4:6] = rgba(st[6])
    s = tv.outlined(s, rgba(st[1]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def trail(P: dict) -> np.ndarray:
    """El reguero (16×16, pisable): trozos pequeños en diagonal hacia el
    nordeste, hacia la montaña."""
    img = canvas(16, 16)
    pl, st = P["plastic"], P["stone"]
    for k, c in enumerate((pl[4], st[6], pl[2], pl[5], st[5], pl[1], pl[6])):
        x, y = 1 + 2 * k, 14 - 2 * k
        img[y, x] = rgba(c)
        if k % 2:
            img[y, x + 1] = rgba(c)
    return img


def buoy(P: dict) -> np.ndarray:
    """Boya varada (16×16): flotador rojo y blanco, medio hundido en la
    arena gris, con su cabo."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 6.5, 2.2, P, True)
    red, st = P["roof_red"], P["stone"]
    s = canvas(16, 16)
    body = ellipse(16, 16, 8, 8.5, 5, 5)
    yy, _ = np.indices((16, 16))
    s[body] = rgba(red[3])
    s[body & (yy >= 7) & (yy <= 9)] = rgba(st[6])
    s[body & (yy >= 11)] = rgba(red[2])
    s[5, 6:8] = rgba(red[5])
    s = tv.outlined(s, rgba(red[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    tv.line(img, 12, 11, 15, 14, rgba(P["wood"][3]))
    return img


def snagged_bag(P: dict, sick: bool) -> np.ndarray:
    """Arbusto de duna (16×16). Enfermo, ramitas secas con bolsas enganchadas
    por el viento; purificado, la mata con flores."""
    img = canvas(16, 16)
    foot(img, 8, 14, 7, 2, P, sick)
    rs = np.random.default_rng(41)
    if sick:
        b = tv.piece("twigs", P, rs)
        place(img, b, 8, 15)
        st, pl = P["stone"], P["plastic"]
        for x, y, c in ((4, 5, st[6]), (5, 5, st[5]), (4, 6, st[5]), (11, 7, pl[2]), (12, 7, pl[3]),
                        (11, 8, pl[1]), (8, 3, st[6])):
            img[y, x] = rgba(c)
    else:
        b = tv.piece("bush", P, rs)
        for x, y in ((5, 5), (12, 6), (9, 9)):
            b[y, x] = rgba(P["flower"][2])
        place(img, b, 8, 15)
    return img


def ghost_net(P: dict, sick: bool) -> np.ndarray:
    """Red fantasma enredada en las rocas (2×1, 32×16). Purificada, quedan
    las rocas limpias, con conchas."""
    img = canvas(32, 16)
    foot(img, 16, 13.5, 15, 2.5, P, sick)
    st = P["stone"]
    yy, xx = np.indices((16, 32))
    s = canvas(32, 16)
    for cx, rx, ry in ((9, 7, 5), (23, 6.5, 4.5)):
        m = ellipse(32, 16, cx, 9.5, rx, ry)
        s[m] = rgba(st[3])
        s[m & (yy < 9)] = rgba(st[4])
        s[m & (yy < 8) & (xx < cx)] = rgba(st[5])
        s[m & (yy > 12)] = rgba(st[2])
    s = tv.outlined(s, rgba(st[0]))
    if sick:
        pl = P["plastic"]
        # la red cuelga entre las dos rocas y por encima: las rocas se siguen
        # viendo debajo (si la red las tapa, se lee como una estera)
        net = ellipse(32, 16, 16, 8, 9, 5) & (yy < 12) & (((xx + yy) % 3 == 0) | ((xx - yy) % 3 == 0))
        s[net] = rgba(pl[2])
        s[net & ((xx + 2 * yy) % 7 == 0)] = rgba(pl[1])
        for x, y in ((6, 4), (17, 6), (27, 5)):
            s[y, x:x + 2] = rgba(pl[5])
    else:
        sand = P["sand"]
        for x, y in ((4, 14), (29, 14), (16, 13)):
            s[y, x:x + 2] = rgba(sand[4])
            s[y - 1, x] = rgba(P["flower"][2])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def trash_mountain(P: dict, sick: bool) -> np.ndarray:
    """Hito: la montaña de basura del vertedero. Huella de 4×4 casillas; el
    sprite (80×72) la desborda hacia arriba y a los lados. Es un montón ancho
    y escalonado, no una bola (captura del 2026-11-02: con silueta ovalada y
    basura en puntos sueltos se leía como un huevo moteado). Enferma, bolsas,
    botellas, cajas, latas y neumáticos de tamaño reconocible sobre una masa
    oscura; purificada, una duna con la misma silueta, hierba, conchas y
    flores."""
    W, H = 80, 72
    cx = W // 2
    img = canvas(W, H)
    foot(img, cx, 68, 37, 4, P, sick)
    yy, xx = np.indices((H, W))
    lumps = [(cx, 56, 36, 12), (cx - 12, 44, 20, 12), (cx + 12, 46, 18, 11), (cx - 2, 33, 15, 11),
             (cx + 14, 36, 10, 8), (cx - 18, 52, 14, 9)]
    hill = np.zeros((H, W), bool)
    for lx, ly, rx, ry in lumps:
        hill |= ellipse(W, H, lx, ly, rx, ry)
    hill &= yy < 68
    rs = np.random.default_rng(57)
    s = canvas(W, H)
    light = (xx - cx) * -0.5 + (yy - 40) * -0.9
    if sick:
        pl, st, red, w = P["plastic"], P["stone"], P["roof_red"], P["wood"]
        s[hill] = rgba(st[2])
        s[hill & (light > 4)] = rgba(st[3])
        s[hill & (light < -14)] = rgba(st[1])
        items = []
        for _ in range(70):
            x, y = int(rs.integers(4, W - 4)), int(rs.integers(22, 66))
            if hill[y, x]:
                items.append((y, x, int(rs.integers(0, 5))))
        for y, x, kind in sorted(items):
            if kind == 0:     # bolsa blanca
                m = ellipse(W, H, x, y, 3.5, 2.4) & hill
                s[m] = rgba(st[6])
                s[m & (yy > y)] = rgba(st[5])
            elif kind == 1:   # botella
                bottle_at(s, x - 2, y, pl, 1 if x % 2 else -1)
            elif kind == 2:   # caja
                s[y - 2:y + 2, x - 2:x + 3] = rgba(w[3])
                s[y - 2, x - 2:x + 3] = rgba(w[4])
                s[y + 1, x - 2:x + 3] = rgba(w[1])
            elif kind == 3:   # lata y tapa
                s[y - 1:y + 1, x - 1:x + 1] = rgba(red[3])
                s[y - 1, x - 1] = rgba(red[5])
                s[y, x + 2] = rgba(pl[5])
            else:             # neumático
                m = ellipse(W, H, x, y, 3, 2) & hill
                s[m] = rgba(st[0])
                s[ellipse(W, H, x, y, 1.2, 0.8)] = rgba(st[2])
        s[hill & ~tv.ndi.binary_erosion(hill)] = rgba(st[1])
        out = st[0]
    else:
        base, g, fl = P["sand"], P["grass"], P["flower"]
        s[hill] = rgba(base[2])
        s[hill & (light > 2)] = rgba(base[3])
        s[hill & (light > 16)] = rgba(base[4])
        s[hill & (light < -12)] = rgba(base[1])
        for _ in range(40):
            x, y = int(rs.integers(4, W - 4)), int(rs.integers(24, 66))
            if hill[y, x] and hill[min(H - 1, y + 2), x]:
                s[y - 2:y + 1, x] = rgba(g[4])
                s[y - 3, x] = rgba(g[6])
                s[y - 1, x + 1] = rgba(g[3])
                s[y, x - 1] = rgba(g[3])
        for x, y in ((22, 62), (44, 64), (58, 58), (30, 46), (50, 40)):
            s[y, x:x + 2] = rgba(base[4])
            s[y - 1, x] = rgba(fl[2])
        for x, y in ((26, 30), (48, 34), (36, 54), (62, 50)):
            s[y, x] = rgba(fl[4])
            s[y + 1, x] = rgba(g[3])
        out = base[0]
    s = tv.outlined(s, rgba(out))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def coast_blocker(P: dict) -> np.ndarray:
    """Paso cerrado de la Costa (16×16): chatarra y plástico retorcidos. Con la
    ola desaparece (solo hay sprite enfermo)."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7.5, 2.5, P, True)
    ru, pl = P["rust"], P["plastic"]
    s = canvas(16, 16)
    tv.line(s, 2, 12, 13, 4, rgba(ru[2]), 2)
    tv.line(s, 3, 5, 12, 12, rgba(ru[3]), 2)
    s[ellipse(16, 16, 8, 9, 3, 2)] = rgba(pl[1])
    s[8, 7:9] = rgba(pl[2])
    s = tv.outlined(s, rgba(ru[0]))
    s[4, 12] = rgba(pl[4])
    s[11, 4] = rgba(pl[5])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


# --- piezas de la Llanura ----------------------------------------------------------------
# Daño de agotamiento (`drygrass` + `sludge`, README del sistema §Mundo): el
# monocultivo en hileras iguales, el abono químico, la sal y el lodo tóxico.
# Las hileras van sin cerca (`withered_plain.deco.txt`). Lo que se limpia con
# la ola (saco y sal) solo tiene sprite enfermo.

def crop_row(P: dict, sick: bool, sway: int = 0, wilted: bool = False) -> np.ndarray:
    """Hilera de cultivo (16×16, pisable) sobre su surco. Enferma, un solo
    cultivo de paja, todas las matas iguales (`wilted`: dobladas y secas);
    purificada, cultivos mezclados con hoja, flor y grano. `sway` inclina las
    puntas (segundo cuadro del mecerse)."""
    img = canvas(16, 16)
    d = P["dirt"]
    img[12:15, 0:16] = rgba(d[2])
    img[12, 0:16] = rgba(d[3])
    img[14, 0:16] = rgba(d[1])
    if sick:
        st = P["straw"]
        for x in (2, 6, 10, 14):
            top = 7 if wilted else 3
            for y in range(top, 12):
                lean = (y - top) // 2 if wilted and y < top + 3 else 0
                img[y, min(15, x + lean)] = rgba(st[2])
            img[top, x] = rgba(st[3])
            if wilted:
                img[top - 1, x + 1] = rgba(P["dead"][3])
            else:
                img[5, x - 1] = rgba(st[1])
                img[6, x + 1] = rgba(st[1])
    else:
        leaf, fl, gold = P["leaf"], P["flower"], P["gold"]
        plants = [(2, 4, "grain"), (6, 6, "leaf"), (10, 3, "flower"), (13, 5, "leaf")]
        for x, top, kind in plants:
            for y in range(top, 12):
                lean = sway if y < top + 3 else 0
                img[y, min(15, max(0, x + lean))] = rgba(leaf[3])
            tx = min(15, max(0, x + sway))
            if kind == "grain":
                img[top:top + 3, tx] = rgba(gold[4])
                img[top, tx] = rgba(gold[5])
            elif kind == "flower":
                img[top, tx] = rgba(fl[3])
                img[top + 1, tx - 1:tx + 2] = rgba(leaf[4])
            else:
                img[top + 1, tx - 1] = rgba(leaf[5])
                img[top + 2, tx + 1] = rgba(leaf[4])
    return img


def sack(P: dict) -> np.ndarray:
    """Saco de abono químico abierto (16×16): costal claro con la etiqueta y el
    granulado blanco que se derrama."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7, 2.5, P, True)
    w, red, st = P["wall"], P["roof_red"], P["stone"]
    s = canvas(16, 16)
    s[ellipse(16, 16, 7, 9, 5, 4.5)] = rgba(w[3])
    s[ellipse(16, 16, 6, 8, 3, 3)] = rgba(w[4])
    s[9:11, 4:9] = rgba(red[3])
    s[4:6, 5:10] = rgba(w[2])   # la boca abierta
    s = tv.outlined(s, rgba(w[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    for x, y in ((11, 12), (13, 13), (12, 11), (14, 12), (10, 13)):
        img[y, x] = rgba(st[6])
    return img


def salt_crust(P: dict) -> np.ndarray:
    """Costra de sal (16×16, pisable): mancha blanca tramada con grietas."""
    img = canvas(16, 16)
    st, so = P["stone"], P["sick_soil"]
    yy, xx = np.indices((16, 16))
    blob = ellipse(16, 16, 8, 9, 6.5, 4)
    img[blob & ((xx + yy) % 2 == 0)] = rgba(st[6])
    img[blob & ((xx + yy) % 2 == 1)] = rgba(st[5])
    tv.line(img, 4, 8, 8, 10, rgba(so[2]))
    tv.line(img, 8, 10, 12, 9, rgba(so[2]))
    tv.line(img, 8, 10, 7, 12, rgba(so[2]))
    return img


def sprayer(P: dict, sick: bool) -> np.ndarray:
    """La pulverizadora (2×1, 32×16) tumbada de lado: depósito, rueda y la
    barra de boquillas. Enferma, goteando lodo químico; purificada, oxidada y
    con flores que crecen dentro."""
    img = canvas(32, 16)
    foot(img, 16, 13.5, 15, 2.5, P, sick)
    red, st, ru = P["roof_red"], P["stone"], P["rust"]
    s = canvas(32, 16)
    tank = ellipse(32, 16, 12, 8.5, 9, 4.5)
    yy, _ = np.indices((16, 32))
    s[tank] = rgba(red[3] if sick else ru[3])
    s[tank & (yy < 7)] = rgba(red[4] if sick else ru[4])
    s[tank & (yy > 10)] = rgba(red[2] if sick else ru[2])
    s[ellipse(32, 16, 4, 11, 3, 3)] = rgba(st[1])
    s[ellipse(32, 16, 4, 11, 1.3, 1.3)] = rgba(st[3])
    s[8:10, 21:31] = rgba(st[3])
    s[8, 21:31] = rgba(st[4])
    for x in (24, 27, 30):
        s[10, x] = rgba(st[2])
    s = tv.outlined(s, rgba(st[0]))
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    if sick:
        sl = P["sludge"]
        for x in (24, 27, 30):
            img[11:13, x] = rgba(sl[2])
        img[13, 23:31] = rgba(sl[1])
        img[13, 26] = rgba(sl[3])
    else:
        leaf, fl = P["leaf"], P["flower"]
        for x, y, c in ((9, 4, 1), (12, 3, 3), (15, 4, 2)):
            img[y + 1:y + 3, x] = rgba(leaf[3])
            img[y, x] = rgba(fl[c])
    return img


def silo(P: dict, sick: bool) -> np.ndarray:
    """Hito: el silo de Grano de Sal. Huella de 3×4 casillas; el sprite
    (56×84) la desborda hacia arriba. Cilindro de chapa con nervios, cúpula y
    escalera. Enfermo, chapa apagada con chorretones de óxido y la puerta
    rota; purificado, la cúpula roja y la enredadera al pie."""
    W, H = 56, 84
    cx = W // 2
    img = canvas(W, H)
    foot(img, cx, 80, 24, 4.5, P, sick)
    w, red, ru, st = P["wall"], P["roof_red"], P["rust"], P["stone"]
    t = canvas(W, H)
    yy, xx = np.indices((H, W))
    body = (np.abs(xx + 0.5 - cx) <= 17) & (yy >= 22) & (yy < 80)
    t[body] = rgba(w[2])
    t[body & (xx < cx - 6)] = rgba(w[3])
    t[body & (xx < cx - 12)] = rgba(w[4])
    t[body & (xx > cx + 10)] = rgba(w[1])
    for x in range(cx - 15, cx + 17, 5):
        t[22:80, x] = rgba(w[1])
    for y in (34, 50, 66):
        t[y, cx - 17:cx + 18] = rgba(w[1])
    dome = ellipse(W, H, cx, 22, 18, 13) & (yy <= 22)
    roof = (red[1], red[2], red[3]) if sick else (red[3], red[4], red[5])
    t[dome] = rgba(roof[0])
    t[dome & (xx < cx + 6)] = rgba(roof[1])
    t[dome & (xx < cx - 6) & (yy > 12)] = rgba(roof[2])
    t[6:10, cx - 3:cx + 3] = rgba(st[3])
    # escalera
    t[18:80, cx + 12] = rgba(ru[1])
    t[18:80, cx + 15] = rgba(ru[1])
    t[20:80:3, cx + 12:cx + 16] = rgba(ru[2])
    # puerta
    t[66:80, cx - 6:cx + 2] = rgba(P["wood"][2])
    t[66, cx - 6:cx + 2] = rgba(P["wood"][4])
    if sick:
        t[70:76, cx - 4:cx] = rgba(st[0])
        for x, y0, y1 in ((cx - 10, 24, 44), (cx + 4, 36, 58), (cx - 2, 52, 66)):
            t[y0:y1, x] = rgba(ru[2])
            t[y0:y1:4, x] = rgba(ru[1])
    t = tv.outlined(t, rgba(w[0]))
    if not sick:
        leaf, fl = P["leaf"], P["flower"]
        for k, y in enumerate(range(78, 52, -3)):
            x = cx - 17 + (k % 2)
            t[y:y + 2, x] = rgba(leaf[3])
            t[y, x + 1] = rgba(leaf[5])
        for x in (cx - 12, cx + 6, cx + 20):
            t[81, x] = rgba(fl[1])
            t[82, x] = rgba(leaf[4])
    img[t[..., 3] > 0] = t[t[..., 3] > 0]
    return img


def wire_blocker(P: dict) -> np.ndarray:
    """Paso cerrado de la Llanura (16×16): alambre de espino en diagonal entre
    dos postes. Con la ola desaparece (solo hay sprite enfermo)."""
    img = canvas(16, 16)
    foot(img, 8, 13.5, 7.5, 2.5, P, True)
    w, st = P["wood"], P["stone"]
    s = canvas(16, 16)
    s[3:14, 2:4] = rgba(w[2])
    s[3:14, 2] = rgba(w[3])
    s[7:14, 12:14] = rgba(w[2])
    s[7:14, 12] = rgba(w[3])
    s = tv.outlined(s, rgba(w[0]))
    for a, b in (((3, 4), (13, 8)), ((3, 8), (13, 11)), ((3, 11), (13, 13))):
        tv.line(s, a[0], a[1], b[0], b[1], rgba(st[4]))
    for x, y in ((6, 6), (9, 7), (6, 9), (10, 10), (7, 12)):
        s[y - 1, x] = rgba(st[5])
        s[y + 1, x] = rgba(st[2])
    img[s[..., 3] > 0] = s[s[..., 3] > 0]
    return img


def weed(P: dict, sick: bool, sway: int = 0) -> np.ndarray:
    """Matojo (16×16, pisable). Enfermo, cardo seco; purificado, mata de
    flores silvestres. `sway` inclina las puntas."""
    img = canvas(16, 16)
    if sick:
        dl = P["dead"]
        for x, top in ((4, 7), (7, 5), (9, 6), (12, 8)):
            img[top:14, x] = rgba(dl[3])
            img[top, x - 1:x + 2] = rgba(dl[4])
            img[top - 1, x] = rgba(dl[5])
        img[13:15, 3:13] = rgba(dl[1])
    else:
        g, fl = P["grass"], P["flower"]
        for k, (x, top) in enumerate(((3, 7), (6, 4), (9, 6), (12, 5))):
            for y in range(top, 14):
                lean = sway if y < top + 3 else 0
                img[y, min(15, x + lean)] = rgba(g[4])
            tx = min(15, x + sway)
            img[top - 1, tx] = rgba(fl[(0, 3, 5, 1)[k]])
            img[top, max(0, tx - 1)] = rgba(fl[(0, 3, 5, 1)[k]])
        img[14, 2:14] = rgba(g[1])
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


def basin() -> dict[str, np.ndarray]:
    out = {}
    for state in ("sick", "pure"):
        sick = state == "sick"
        P = tv.palette("enfermo" if sick else "sano", "cuenca")
        P["rust"] = tv.ramp("rust")
        P["roof_blue"] = tv.ramp("roof_blue")
        if sick:
            P["oil"], P["sheen"] = tv.ramp("oil"), tv.ramp("sheen")
            P["stain"] = P["oil"]
        # misma pieza que la masa de la Cuenca: árbol sano y quemado sin brasas
        out[f"tree_{state}"] = tree(P, sick, 0)
        out[f"tree_b_{state}"] = tree(P, sick, 1)
        out[f"refinery_tower_{state}"] = refinery_tower(P, sick)
        out[f"broken_pipe_{state}"] = broken_pipe(P, sick)
        out[f"boat_{state}"] = boat(P, sick)
        out[f"torn_net_{state}"] = torn_net(P, sick)
        out[f"bush_{state}"] = shrub(P, sick)
        out[f"reeds_{state}"] = reeds(P, sick)
        out[f"grass_{state}"] = tall_grass(P, sick, 0)
        if sick:
            out["oil_sick"] = oil_patch(P)
            out["barrel_sick"] = barrel(P)
            out["blocker_sick"] = tar_blocker(P)
            out["rock_sick"] = rock(P)
            out["seedbed_sick"] = seedbed(P)
        else:
            out["reeds_pure_1"] = reeds(P, False, 1)
            out["grass_pure_1"] = tall_grass(P, False, 1)
    return out


def coast() -> dict[str, np.ndarray]:
    out = {}
    for state in ("sick", "pure"):
        sick = state == "sick"
        P = tv.palette("enfermo" if sick else "sano", "costa")
        P["rust"] = tv.ramp("rust")
        if sick:
            P["plastic"] = tv.ramp("plastic")
            # el pie se asienta en la arena gris de la Costa enferma
            P["stain"] = P["sand"]
        out[f"trash_mountain_{state}"] = trash_mountain(P, sick)
        out[f"snagged_bag_{state}"] = snagged_bag(P, sick)
        out[f"ghost_net_{state}"] = ghost_net(P, sick)
        out[f"bush_{state}"] = shrub(P, sick)
        out[f"grass_{state}"] = tall_grass(P, sick, 0)
        if sick:
            out["litter_sick"] = litter(P)
            out["bottle_sick"] = bottle(P)
            out["torn_bag_sick"] = torn_bag(P)
            out["trail_sick"] = trail(P)
            out["buoy_sick"] = buoy(P)
            out["blocker_sick"] = coast_blocker(P)
            out["rock_sick"] = rock(P)
            out["seedbed_sick"] = seedbed(P)
        else:
            out["grass_pure_1"] = tall_grass(P, False, 1)
    return out


def plain() -> dict[str, np.ndarray]:
    out = {}
    for state in ("sick", "pure"):
        sick = state == "sick"
        P = tv.palette("enfermo" if sick else "sano", "llanura")
        P["rust"] = tv.ramp("rust")
        P["wall"] = tv.ramp("wall")
        P["straw"] = tv.ramp("straw")
        if sick:
            # el pie se asienta en la tierra agotada
            P["sick_soil"] = tv.ramp("sick_soil")
            P["stain"] = P["sick_soil"]
        out[f"tree_{state}"] = tree(P, sick, 0)
        out[f"tree_b_{state}"] = tree(P, sick, 1)
        out[f"stump_{state}"] = stump(P, sick)
        out[f"silo_{state}"] = silo(P, sick)
        out[f"crop_row_{state}"] = crop_row(P, sick)
        out[f"wilted_row_{state}"] = crop_row(P, sick, wilted=sick)
        out[f"sprayer_{state}"] = sprayer(P, sick)
        out[f"bush_{state}"] = shrub(P, sick)
        out[f"grass_{state}"] = tall_grass(P, sick, 0)
        out[f"weed_{state}"] = weed(P, sick)
        if sick:
            out["sack_sick"] = sack(P)
            out["salt_sick"] = salt_crust(P)
            out["blocker_sick"] = wire_blocker(P)
            out["rock_sick"] = rock(P)
            out["seedbed_sick"] = seedbed(P)
        else:
            out["crop_row_pure_1"] = crop_row(P, False, 1)
            out["grass_pure_1"] = tall_grass(P, False, 1)
            out["weed_pure_1"] = weed(P, False, 1)
    return out


CATALOG = {"ashen_forest": forest, "tar_basin": basin, "broken_coast": coast, "withered_plain": plain}


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
