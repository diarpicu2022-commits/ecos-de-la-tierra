"""Genera el decorado, el hito y los animales del mundo (contrato «Rastro»,
fase 5, paso 2; enmiendas 6, 7 y 8 del 2026-10-28).

Cada pieza sale en `assets/sprites/world/decor/<id>_<estado>.png`, con estado
`sick` (enfermo) o `pure` (purificado). Lo que no cambia al purificar (casas,
pozo, rocas, personas, animales domésticos) solo tiene `sick`; lo que solo
existe purificado (el árbol de Yara, la fauna silvestre) solo tiene `pure`.

Reglas que se cumplen aquí y no en otro sitio:

- **Gramática de forma** (catálogo 2a): lo enfermo es diagonal y roto; lo
  purificado, redondo. Ningún decorado tiene silueta rectangular sólida ni
  contorno. Solo lo que responde (semillero, Yara) lleva contorno `ash_050`.
- **Paleta**: solo tokens de `pixel.py`. Lo enfermo, bajo el techo de 0,22 con
  las rampas de material, madera, tejado y ceniza. Lo purificado, con VITAL,
  AQUA y BLOOM (enmienda 6).
- **Hueco métrico**: los animales y la fauna miden 8x8 o 16x16, nunca entre 9 y
  15 px.

Semilla fija por pieza: regenerar no cambia nada.

Uso:
    python tools/gen_world_decor.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from pixel import Canvas, ValueNoise, color

OUT = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "world" / "decor"


# --- Utilidades de dibujo --------------------------------------------------------


def blob(c: Canvas, cx: float, cy: float, rx: float, ry: float, ink: str,
         noise: ValueNoise | None = None, rough: float = 0.0, scale: float = 0.35) -> None:
    """Mancha elíptica. Con `noise`, el borde se rompe (lo enfermo)."""
    for y in range(c.height):
        for x in range(c.width):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = math.sqrt(dx * dx + dy * dy)
            if noise is not None:
                d += (noise.fbm(x * scale, y * scale) - 0.5) * rough
            if d <= 1.0:
                c.set(x, y, color(ink))


def shade_blob(c: Canvas, cx: float, cy: float, rx: float, ry: float,
               dark: str, base: str, lit: str, top: str | None = None,
               noise: ValueNoise | None = None, rough: float = 0.0) -> None:
    """Copa con volumen: sombra abajo a la derecha, luz arriba a la izquierda."""
    blob(c, cx, cy, rx, ry, dark, noise, rough)
    blob(c, cx - rx * 0.12, cy - ry * 0.14, rx * 0.86, ry * 0.82, base, noise, rough)
    blob(c, cx - rx * 0.32, cy - ry * 0.36, rx * 0.46, ry * 0.40, lit, noise, rough * 0.6)
    if top:
        blob(c, cx - rx * 0.42, cy - ry * 0.48, rx * 0.18, ry * 0.16, top)


def line(c: Canvas, x0: int, y0: int, x1: int, y1: int, ink: str) -> None:
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        c.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), color(ink))


def grid(c: Canvas, rows: list[str], ink: dict[str, str], ox: int = 0, oy: int = 0) -> None:
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in ink:
                c.set(ox + x, oy + y, color(ink[ch]))


def ground_shadow(c: Canvas, cx: float, cy: float, rx: float, ink: str) -> None:
    blob(c, cx, cy, rx, max(2.0, rx * 0.35), ink)


# --- Árboles -----------------------------------------------------------------------


def tree(pure: bool, seed: int) -> Canvas:
    """Árbol de 32x40: copa de 2x2 tiles y tronco sobre la fila de abajo."""
    c = Canvas(32, 40)
    rng = random.Random(seed)
    noise = ValueNoise(seed)
    ground_shadow(c, 16, 36, 11, "vital_900" if pure else "soil_700")
    # Tronco: madera, con la base abierta en raíces.
    for y in range(26, 37):
        w = 3 if y < 33 else 4 + (y - 33)
        for x in range(16 - w // 2 - 1, 16 + w // 2 + 1):
            c.set(x, y, color("wood_500" if x < 16 else "wood_700"))
    line(c, 15, 28, 15, 34, "wood_300")
    if pure:
        # Copa redonda y llena, en tres masas que se solapan.
        shade_blob(c, 9, 21, 8, 7, "vital_900", "vital_700", "vital_500")
        shade_blob(c, 23, 21, 8, 7, "vital_900", "vital_700", "vital_500")
        shade_blob(c, 16, 13, 13, 11, "vital_900", "vital_700", "vital_500", "vital_300")
        for _ in range(5):
            x, y = rng.randint(7, 24), rng.randint(6, 20)
            if c.get(x, y) == color("vital_700"):
                c.set(x, y, color("vital_500"))
    else:
        # Copa enferma: rala, rota en diagonal, con ramas desnudas que asoman.
        for x0, y0, x1, y1 in ((16, 26, 5, 12), (16, 24, 28, 9), (16, 22, 14, 3)):
            line(c, x0, y0, x1, y1, "wood_700")
        shade_blob(c, 10, 18, 8, 7, "flora_700", "flora_500", "flora_300", noise=noise, rough=0.9)
        shade_blob(c, 22, 16, 8, 7, "flora_700", "flora_500", "flora_300", noise=noise, rough=0.9)
        shade_blob(c, 15, 10, 8, 6, "flora_700", "flora_500", "flora_300", noise=noise, rough=0.9)
        for _ in range(14):
            x, y = rng.randint(4, 27), rng.randint(4, 21)
            if c.filled(x, y) and c.get(x, y) != color("wood_700"):
                c.set(x, y, color("soil_700"))
        for x, y in ((5, 8), (27, 6), (14, 2)):
            line(c, x, y, x - 1, y - 2, "wood_700")
    return c


def yara_tree() -> Canvas:
    """El hito: el árbol del jardín de Yara, 48x64. Solo existe purificado."""
    c = Canvas(48, 64)
    rng = random.Random(7)
    ground_shadow(c, 24, 58, 18, "vital_900")
    # Tronco ancho con raíces que se abren.
    for y in range(40, 60):
        spread = 4 + max(0, y - 52)
        for x in range(24 - spread, 24 + spread + 1):
            c.set(x, y, color("wood_500" if x < 24 else "wood_700"))
    for x0, x1 in ((16, 10), (32, 38)):
        line(c, 24, 54, x0, 59, "wood_700")
        line(c, 24, 55, x1, 60, "wood_500")
    line(c, 21, 42, 21, 56, "wood_300")
    line(c, 26, 44, 27, 54, "wood_900")
    # Copa: cinco masas redondas, la mayor arriba.
    for cx, cy, rx, ry in ((11, 34, 11, 9), (37, 34, 11, 9), (15, 22, 13, 11),
                           (33, 22, 13, 11), (24, 15, 16, 13)):
        shade_blob(c, cx, cy, rx, ry, "vital_900", "vital_700", "vital_500", "vital_300")
    # Flores en la copa: el único árbol que florece al empezar el juego.
    for _ in range(18):
        x, y = rng.randint(4, 43), rng.randint(3, 34)
        if c.get(x, y) in (color("vital_700"), color("vital_500")):
            c.set(x, y, color(rng.choice(["bloom_500", "bloom_300", "bloom_100"])))
    return c


def bush(pure: bool, seed: int) -> Canvas:
    c = Canvas(16, 16)
    noise = ValueNoise(seed)
    ground_shadow(c, 8, 13, 6, "vital_900" if pure else "soil_700")
    if pure:
        shade_blob(c, 8, 9, 7, 5.5, "vital_900", "vital_700", "vital_500", "vital_300")
    else:
        shade_blob(c, 8, 9, 7, 5.5, "flora_700", "flora_500", "flora_300", noise=noise, rough=1.0)
        line(c, 3, 12, 1, 7, "wood_700")
        line(c, 12, 11, 15, 6, "wood_700")
    return c


# --- Lo construido -------------------------------------------------------------------


def house(stone: bool, seed: int) -> Canvas:
    """Casa de 48x48: tejado a dos aguas de 2 tiles y fachada de 1 tile.

    La silueta no es un rectángulo: el tejado sobresale y se escalona.
    """
    c = Canvas(48, 48)
    rng = random.Random(seed)
    ground_shadow(c, 24, 46, 22, "soil_700")
    wall_dark, wall, wall_lit = (("ash_700", "ash_600", "ash_400") if stone
                                 else ("wood_700", "wood_500", "wood_300"))
    # Fachada.
    c.rect(3, 26, 42, 20, color(wall))
    if stone:
        for y in range(27, 46, 4):
            off = 0 if (y // 4) % 2 else 3
            for x in range(3 + off, 45, 6):
                c.rect(x, y, 5, 3, color(wall_lit if rng.random() < 0.3 else wall))
                c.set(x + 5, y + 1, color(wall_dark))
            line(c, 3, y + 3, 44, y + 3, wall_dark)
    else:
        for x in range(3, 45, 4):
            line(c, x, 26, x, 45, wall_dark)
            line(c, x + 1, 26, x + 1, 45, wall_lit if x % 8 == 3 else wall)
    line(c, 44, 26, 44, 45, wall_dark)
    # Puerta y ventana.
    c.rect(20, 33, 8, 13, color("wood_900"))
    c.rect(21, 34, 6, 12, color("wood_700"))
    c.set(25, 40, color("ash_200"))
    for wx in (7, 33):
        c.rect(wx, 31, 8, 7, color("wood_300"))
        c.rect(wx + 1, 32, 6, 5, color("water_700"))
        line(c, wx + 4, 32, wx + 4, 36, "wood_300")
        c.set(wx + 1, 32, color("ash_600"))
    # Tejado a cuatro aguas: cumbrera corta arriba, faldones que se abren
    # hasta el alero y sobresalen 1 px por lado. Ocupa la mitad de la casa,
    # como en los pueblos de GBA: lo que se lee de lejos es el tejado.
    for y in range(3, 28):
        inset = max(0, 12 - y) * 2
        x0, x1 = 1 + inset, 47 - inset
        band = "roof_300" if y < 9 else "roof_500" if y < 19 else "roof_700"
        for x in range(x0, x1):
            ink = band
            if (y - 3) % 4 == 3:
                ink = "roof_700" if y < 19 else "roof_900"
            elif (x + ((y - 3) // 4) * 3) % 6 == 0:
                ink = "roof_700" if y < 19 else "roof_900"
            # Faldón lateral derecho en sombra, izquierdo con luz.
            if x >= x1 - 2 - (0 if y >= 12 else 1):
                ink = "roof_900"
            elif x <= x0 + 1:
                ink = "roof_100" if y < 12 else "roof_300"
            c.set(x, y, color(ink))
    line(c, 23, 3, 26, 3, "roof_100")
    line(c, 1, 27, 46, 27, "roof_900")
    # Sombra del alero sobre la fachada.
    line(c, 3, 28, 44, 28, wall_dark)
    # Chimenea de piedra.
    c.rect(34, 0, 5, 9, color("ash_600"))
    line(c, 34, 0, 38, 0, "ash_400")
    line(c, 38, 1, 38, 8, "ash_700")
    return c


def well() -> Canvas:
    """Pozo de piedra con tejadillo, 32x32."""
    c = Canvas(32, 32)
    ground_shadow(c, 16, 29, 13, "soil_700")
    blob(c, 16, 23, 12, 7, "ash_700")
    blob(c, 16, 22, 11, 6, "ash_600")
    blob(c, 15, 21, 9, 4.5, "ash_400")
    blob(c, 16, 21, 7, 3.2, "water_700")
    for x in (6, 25):
        c.rect(x, 6, 2, 16, color("wood_700"))
        c.set(x, 6, color("wood_300"))
    line(c, 7, 10, 25, 10, "wood_500")
    line(c, 16, 10, 16, 18, "ash_400")
    c.rect(14, 17, 4, 3, color("wood_500"))
    for y in range(1, 8):
        inset = max(0, 4 - y)
        line(c, 3 + inset, y, 28 - inset, y, "roof_500" if y < 6 else "roof_700")
    line(c, 6, 1, 25, 1, "roof_300")
    return c


def rock(seed: int) -> Canvas:
    c = Canvas(16, 16)
    ground_shadow(c, 8, 13, 6, "soil_700")
    # Piedra partida: aristas en diagonal (es decorado, nunca redonda del todo).
    rows = [
        "................",
        "................",
        "................",
        "................",
        "......aab.......",
        "....aaabbbc.....",
        "...aaabbbbcc....",
        "..aaabbbbbccc...",
        "..abbbbbbcccc...",
        "..bbbbbbccccc...",
        "...bbbcccccc....",
        "....cccccc......",
    ]
    grid(c, rows, {"a": "ash_400", "b": "ash_600", "c": "ash_700"})
    return c


# --- Plantas ---------------------------------------------------------------------------


def grass(pure: bool, seed: int) -> Canvas:
    """Hierba alta: hojas en abanico. Enferma, seca y doblada en diagonal."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    for i in range(7):
        x = 2 + i * 2 + rng.randint(0, 1)
        h = rng.randint(6, 10)
        lean = (i - 3) * 0.35 if pure else 1.1
        ink = ("vital_700", "vital_500", "vital_300")[i % 3] if pure else ("flora_700", "flora_500", "flora_300")[i % 3]
        for k in range(h):
            c.set(round(x + lean * k * (0.4 if pure else 0.7)), 15 - k, color(ink))
    return c


def flower(pure: bool, seed: int) -> Canvas:
    """Mata de flores. Enferma: tallos grises y cabezas caídas."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    spots = [(4, 7), (10, 5), (7, 10), (12, 11)]
    if pure:
        for i, (x, y) in enumerate(spots):
            line(c, x, y + 1, x, 15, "vital_700")
            c.set(x - 1, y + 3, color("vital_500"))
            petal = ("bloom_500", "bloom_300", "bloom_100", "bloom_700")[(i + seed) % 4]
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                c.set(x + dx, y + dy, color(petal))
            c.set(x, y, color("ash_050"))
    else:
        for x, y in spots[:3]:
            line(c, x, y + 2, x + 1, 15, "ash_600")
            c.set(x - 1, y + 3, color("ash_700"))
            c.set(x - 2, y + 4, color("ash_700"))
    return c


def pebbles(seed: int) -> Canvas:
    """Piedrecitas sueltas: textura de suelo, sin volumen."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    for _ in range(3):
        x, y = rng.randint(2, 12), rng.randint(4, 13)
        c.set(x, y, color("soil_300"))
        c.set(x + 1, y, color("soil_300"))
        c.set(x, y + 1, color("soil_700"))
        c.set(x + 1, y + 1, color("soil_700"))
    return c


def weed(pure: bool, seed: int) -> Canvas:
    """Matojo bajo. Enfermo: tres hojas secas en diagonal. Purificado: mata
    redonda con una flor."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    x, y = rng.randint(4, 10), rng.randint(9, 12)
    if pure:
        for dx, dy, ink in ((0, 0, "vital_700"), (1, 0, "vital_700"), (-1, 1, "vital_700"),
                            (0, 1, "vital_900"), (1, 1, "vital_900"), (2, 1, "vital_700"),
                            (0, -1, "vital_500"), (1, -1, "vital_300")):
            c.set(x + dx, y + dy, color(ink))
        c.set(x + 3, y - 2, color(("bloom_500", "bloom_100", "bloom_300")[seed % 3]))
        c.set(x + 3, y - 1, color("vital_700"))
    else:
        for i in range(3):
            line(c, x + i * 2, y + 2, x + i * 2 + 2, y - 1, ("flora_300", "flora_500", "flora_700")[i])
    return c


def crop_row(pure: bool, seed: int) -> Canvas:
    """Hilera de cultivo. Enferma: un solo cultivo, seco y en fila. Purificada:
    cereal y legumbre alternos (la rotación que enseña la Llanura)."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    if not pure:
        for x in range(1, 16, 3):
            h = rng.randint(6, 9)
            line(c, x, 15, x + 2, 15 - h, "flora_300")
            c.set(x + 2, 15 - h, color("soil_300"))
        line(c, 0, 15, 15, 15, "soil_700")
        return c
    for x in range(1, 16, 4):
        line(c, x, 15, x, 7, "vital_700")
        for k in (7, 8, 9):
            c.set(x + 1, k, color("wood_100"))
    for x in (3, 11):
        blob(c, x + 0.5, 12.5, 2.2, 2.2, "vital_500")
        c.set(x, 11, color("vital_300"))
    return c


def stump(pure: bool) -> Canvas:
    c = Canvas(16, 16)
    ground_shadow(c, 8, 13, 6, "soil_700" if not pure else "vital_900")
    # Corte limpio en diagonal: la tala, que es la causa.
    rows = [
        "................",
        "................",
        "................",
        "................",
        "................",
        "......abbb......",
        ".....abbbbc.....",
        "....dacccbcc....",
        "....ddeeeeee....",
        "....ddeeeeee....",
        "...dddeeeeeee...",
        "..dd.deeeeee.ee.",
        "................",
    ]
    grid(c, rows, {"a": "wood_100", "b": "wood_300", "c": "wood_500", "d": "wood_700", "e": "wood_900"})
    if pure:
        # Un brote redondo: el bosque vuelve desde el tocón.
        blob(c, 11.5, 5.5, 2.2, 2.2, "vital_500")
        c.set(11, 4, color("vital_300"))
        line(c, 10, 7, 10, 8, "vital_700")
    return c


def litter(pure: bool, seed: int) -> Canvas:
    """Basura suelta y dispersa. Al purificar la Costa, desaparece."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    # Botella tumbada en diagonal, lata y un jirón de red: siluetas, no color.
    line(c, 2, 12, 6, 8, "ash_400")
    line(c, 3, 12, 7, 8, "ash_600")
    c.set(7, 7, color("ash_200"))
    blob(c, 11.5, 11.5, 1.8, 1.8, "ash_600")
    c.set(11, 11, color("ash_400"))
    for x, y in ((9, 3), (11, 4), (13, 3), (10, 5), (12, 6)):
        c.set(x + rng.randint(0, 1), y, color("ash_700"))
    return c


# --- Lo que responde (contorno ash_050) --------------------------------------------------


def seedbed() -> Canvas:
    """Semillero, 16x16: cajón de madera con brote verde (catálogo 2a)."""
    c = Canvas(16, 16)
    c.rect(2, 7, 12, 7, color("wood_500"))
    line(c, 2, 7, 13, 7, "wood_300")
    line(c, 2, 10, 13, 10, "wood_700")
    line(c, 2, 13, 13, 13, "wood_700")
    c.rect(3, 6, 10, 1, color("soil_500"))
    line(c, 8, 6, 8, 3, "vital_700")
    blob(c, 6.5, 3.5, 1.8, 1.4, "vital_500")
    blob(c, 9.5, 2.5, 1.8, 1.4, "vital_500")
    c.outline(color("ash_050"))
    return c


def yara() -> Canvas:
    """Yara, 16x24: pañuelo, chal y bastón. Persona: contorno ash_050."""
    c = Canvas(16, 24)
    rows = [
        "................",
        "................",
        "......hhhh......",
        ".....hHHHHh.....",
        ".....hsssshh....",
        ".....hsese.h....",
        "......ssss......",
        ".....rrrrrr.....",
        "....rRRRRRrr....",
        "....rRRRRRrr..w.",
        "...rrRRRRRrrr.w.",
        "...ssrRRRRrrssw.",
        "....rrrrrrrr..w.",
        "....ttttttttt.w.",
        "....tTTTTTttt.w.",
        "....tTTTTTttt.w.",
        "....tTTTTTtttww.",
        "...ttTTTTTtttt..",
        "...ttTTTTTtttt..",
        "...tttttttttt...",
        "....ll....ll....",
        "....ll....ll....",
        "................",
        "................",
    ]
    grid(c, rows, {"h": "ash_200", "H": "ash_050", "s": "wood_300", "e": "water_700",
                   "r": "roof_500", "R": "roof_300", "t": "wood_700", "T": "wood_500",
                   "l": "wood_900", "w": "wood_300"})
    c.outline(color("ash_050"))
    return c


# --- Animales (enmienda 7) y fauna silvestre ----------------------------------------------


def chicken(frame: int) -> Canvas:
    c = Canvas(8, 8)
    rows = [
        [
            "..r.....",
            ".wwb....",
            ".www....",
            "..wwww..",
            "..wwwwg.",
            "...www..",
            "...y.y..",
            "........",
        ],
        [
            "........",
            "..r.....",
            ".wwb....",
            ".wwwwww.",
            "..wwwwg.",
            "...www..",
            "..y..y..",
            "........",
        ],
    ][frame]
    grid(c, rows, {"r": "roof_300", "w": "ash_050", "g": "ash_400", "b": "wood_100", "y": "wood_100"})
    return c


def dog() -> Canvas:
    c = Canvas(16, 16)
    rows = [
        "................",
        "................",
        "................",
        "................",
        "...........dd...",
        "..........dbbd..",
        "..........bbbbe.",
        "...b......bbbb..",
        "...bbbbbbbbbb...",
        "....bbbbbbbbb...",
        "....bLbbbbbbb...",
        "....bb.b..b.b...",
        "....d..d..d.d...",
        "................",
    ]
    blob(c, 8, 13.5, 6, 1.2, "soil_700")
    grid(c, rows, {"b": "wood_300", "L": "wood_100", "d": "wood_700", "e": "water_700"})
    return c


def goat() -> Canvas:
    c = Canvas(16, 16)
    rows = [
        "................",
        "................",
        "................",
        "..........h.h...",
        "...........hh...",
        "..........gggg..",
        "..........gggge.",
        "..........ggg...",
        "...gggggggggg...",
        "..ggwwwwwwggg...",
        "...gwwwwwwgg....",
        "...gggggggg.....",
        "...g.g...g.g....",
        "...k.k...k.k....",
        "................",
    ]
    blob(c, 8, 13.5, 6, 1.2, "soil_700")
    grid(c, rows, {"h": "ash_600", "g": "ash_200", "w": "ash_050", "e": "water_700", "k": "ash_700"})
    return c


def bird(frame: int) -> Canvas:
    """Pájaro silvestre, 8x8: vuelve con la purificación."""
    c = Canvas(8, 8)
    rows = [
        ["........", "b......b", ".bb..bb.", "...bb...", "...ak...", "........", "........", "........"],
        ["........", "........", "...bb...", ".bbakbb.", "b......b", "........", "........", "........"],
    ][frame]
    grid(c, rows, {"b": "aqua_300", "a": "aqua_100", "k": "wood_100"})
    return c


def butterfly(frame: int) -> Canvas:
    c = Canvas(8, 8)
    rows = [
        ["........", ".pp.pp..", "pPPbPPp.", ".pPbPp..", "..p.p...", "........", "........", "........"],
        ["........", "........", "..pbp...", ".pPbPp..", "..pbp...", "........", "........", "........"],
    ][frame]
    grid(c, rows, {"p": "bloom_500", "P": "bloom_300", "b": "water_700"})
    return c


# --- Salida --------------------------------------------------------------------------------


def pieces() -> dict[str, Canvas]:
    out: dict[str, Canvas] = {}
    for state, pure in (("sick", False), ("pure", True)):
        out[f"tree_{state}"] = tree(pure, 11)
        out[f"tree_b_{state}"] = tree(pure, 23)
        out[f"bush_{state}"] = bush(pure, 5)
        out[f"grass_{state}"] = grass(pure, 3)
        out[f"flower_{state}"] = flower(pure, 2)
        out[f"crop_row_{state}"] = crop_row(pure, 9)
        out[f"stump_{state}"] = stump(pure)
        out[f"litter_{state}"] = litter(pure, 4)
        out[f"weed_{state}"] = weed(pure, 6)
    out["yara_tree_pure"] = yara_tree()
    out["house_sick"] = house(False, 1)
    out["house_stone_sick"] = house(True, 2)
    out["well_sick"] = well()
    out["rock_sick"] = rock(1)
    out["pebbles_sick"] = pebbles(8)
    out["seedbed_sick"] = seedbed()
    out["yara_sick"] = yara()
    out["dog_sick"] = dog()
    out["goat_sick"] = goat()
    for f in (0, 1):
        out[f"chicken_{f}_sick"] = chicken(f)
        out[f"bird_{f}_pure"] = bird(f)
        out[f"butterfly_{f}_pure"] = butterfly(f)
    return out


def main() -> None:
    for name, canvas in pieces().items():
        canvas.save(OUT / f"{name}.png")
    print(f"  decorado: {len(pieces())} piezas en {OUT.relative_to(OUT.parents[3])}")


if __name__ == "__main__":
    main()
