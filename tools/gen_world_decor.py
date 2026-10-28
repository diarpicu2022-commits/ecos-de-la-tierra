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


# --- Bosque de las Cenizas: el daño y su vuelta --------------------------------------


def burnt_tree(pure: bool, seed: int) -> Canvas:
    """Árbol quemado, 32x40: tronco de carbón y ramas rotas en diagonal.
    Purificado: el carbón sigue, pero rebrota una copa redonda pequeña."""
    c = Canvas(32, 40)
    rng = random.Random(seed)
    ground_shadow(c, 16, 36, 10, "vital_900" if pure else "soil_700")
    for y in range(10, 37):
        w = 5 if y < 32 else 6 + (y - 32)
        for x in range(16 - w // 2, 16 + w // 2 + 1):
            c.set(x, y, color("ash_700" if x < 17 else "water_700"))
    line(c, 15, 14, 15, 34, "ash_600")
    for x0, y0, x1, y1 in ((16, 22, 4, 11), (16, 19, 28, 8), (16, 13, 12, 2), (17, 12, 22, 3),
                           (8, 15, 3, 8), (24, 12, 29, 4)):
        for k in range(3):
            line(c, x0, y0 + k, x1, y1 + k, "ash_700" if k < 2 else "water_700")
        line(c, x0, y0 - 1, x1, y1 - 1, "ash_600")
    for _ in range(5):
        x, y = rng.randint(14, 17), rng.randint(20, 33)
        c.set(x, y, color("ash_400"))
    if pure:
        shade_blob(c, 16, 10, 8, 6, "vital_900", "vital_700", "vital_500", "vital_300")
        blob(c, 7, 13, 3, 2.5, "vital_700")
        blob(c, 26, 9, 3, 2.5, "vital_700")
    return c


def burnt_oak(pure: bool) -> Canvas:
    """El hito del Bosque: el roble quemado mayor, 48x64. Enfermo, con la brasa
    todavía viva en las grietas: la causa sigue activa. Purificado, la copa
    vuelve redonda sobre el carbón."""
    c = Canvas(48, 64)
    rng = random.Random(31)
    ground_shadow(c, 24, 58, 18, "vital_900" if pure else "soil_700")
    for y in range(16, 60):
        spread = 7 + max(0, y - 50)
        for x in range(24 - spread, 24 + spread + 1):
            c.set(x, y, color("ash_700" if x < 25 else "water_700"))
    for y in range(20, 58, 3):
        line(c, 19, y, 20, y + 2, "ash_600")
    for x0, x1 in ((15, 9), (33, 39)):
        line(c, 24, 54, x0, 60, "ash_700")
        line(c, 24, 55, x1, 61, "water_700")
    # Ramas mayores, partidas.
    for x0, y0, x1, y1 in ((24, 30, 6, 14), (24, 26, 42, 10), (24, 22, 20, 2), (24, 24, 31, 4),
                           (10, 18, 4, 12), (36, 14, 44, 8), (15, 22, 12, 28)):
        for k in range(4):
            line(c, x0, y0 + k, x1, y1 + k, "ash_700" if k < 3 else "water_700")
        line(c, x0, y0 - 1, x1, y1 - 1, "ash_600")
    line(c, 21, 24, 21, 56, "ash_600")
    if pure:
        for cx, cy, rx, ry in ((10, 14, 9, 7), (38, 12, 9, 7), (22, 8, 12, 8), (30, 18, 8, 6)):
            shade_blob(c, cx, cy, rx, ry, "vital_900", "vital_700", "vital_500", "vital_300")
        line(c, 22, 44, 23, 40, "vital_500")
        c.set(22, 39, color("vital_300"))
    else:
        # Brasa en la grieta del tronco: el fuego no se ha apagado.
        for y in range(34, 50):
            c.set(26 + (y % 3 == 0), y, color("ember_700"))
        for y in (37, 41, 45):
            c.set(26, y, color("ember_500"))
        c.set(27, 41, color("ember_300"))
        for _ in range(6):
            x, y = rng.randint(4, 44), rng.randint(2, 20)
            if c.filled(x, y):
                c.set(x, y, color("ember_700"))
    return c


def felled_log(pure: bool) -> Canvas:
    """Tronco talado, 32x16: tendido, con el corte limpio a la vista."""
    c = Canvas(32, 16)
    ground_shadow(c, 16, 13, 14, "vital_900" if pure else "soil_700")
    c.rect(4, 6, 24, 6, color("wood_500"))
    line(c, 4, 6, 27, 6, "wood_300")
    line(c, 4, 11, 27, 11, "wood_700")
    for x in (9, 15, 22):
        line(c, x, 7, x + 2, 9, "wood_700")
    # El corte: anillos, la firma de la tala (no del fuego).
    blob(c, 28.5, 8.5, 3, 3.2, "wood_300")
    blob(c, 28.5, 8.5, 2, 2.2, "wood_100")
    c.set(28, 8, color("wood_300"))
    if pure:
        for x, y in ((8, 5), (13, 5), (19, 5)):
            blob(c, x + 0.5, y + 0.5, 1.6, 1.2, "vital_500")
        c.set(24, 4, color("bloom_300"))
        c.set(24, 5, color("vital_700"))
    return c


def log_pile(pure: bool) -> Canvas:
    """Troncos apilados, 32x32: la madera que se llevan. Tres hileras de cortes."""
    c = Canvas(32, 32)
    ground_shadow(c, 16, 29, 14, "vital_900" if pure else "soil_700")
    rows = ((6, 24, 4), (9, 18, 3), (12, 12, 2))
    for x0, y, n in rows:
        for i in range(n):
            cx = x0 + i * 7 + 3
            blob(c, cx, y, 3.6, 3.6, "wood_700")
            blob(c, cx - 0.4, y - 0.4, 2.8, 2.8, "wood_300")
            blob(c, cx - 0.4, y - 0.4, 1.4, 1.4, "wood_100")
    if pure:
        for x, y in ((9, 8), (24, 13)):
            blob(c, x, y, 2, 1.6, "vital_500")
            c.set(x, y - 1, color("vital_300"))
    return c


def ash(pure: bool, seed: int) -> Canvas:
    """Ceniza en el suelo: manchas en diagonal. Purificada, un brote."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    if pure:
        x, y = rng.randint(4, 10), rng.randint(8, 12)
        line(c, x, y + 2, x, y, "vital_700")
        c.set(x - 1, y, color("vital_500"))
        c.set(x + 1, y - 1, color("vital_500"))
        return c
    for i in range(4):
        x, y = rng.randint(2, 11), rng.randint(3, 12)
        line(c, x, y, x + 3, y + 3, "ash_600")
        c.set(x + 1, y, color("ash_400"))
    return c


def blocker(pure: bool) -> Canvas:
    """Paso cerrado del Bosque, 16x16: troncos en brasas cruzados en diagonal,
    puntiagudos y sin contorno (catálogo 2a). Desaparece con la ola."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 14, 7, "soil_700")
    for x0, y0, x1, y1 in ((0, 13, 15, 3), (1, 3, 15, 14), (4, 15, 11, 1)):
        line(c, x0, y0, x1, y1, "ash_700")
        line(c, x0, y0 - 1, x1, y1 - 1, "water_700")
    for x, y, ink in ((4, 10, "ember_500"), (8, 8, "ember_300"), (11, 5, "ember_500"),
                      (6, 5, "ember_700"), (12, 11, "ember_700"), (8, 3, "ember_500")):
        c.set(x, y, color(ink))
    return c


def flame_monster(pure: bool) -> Canvas:
    """La Llama de la Deforestación en el mapa, 16x24: brasa con borde
    EMBER_300, que es lo que se lee sobre el follaje (verify_tileset, parte 4).
    Purificada, ya no está."""
    c = Canvas(16, 24)
    if pure:
        return c
    ground_shadow(c, 8, 22, 6, "soil_700")
    rows = [
        "................",
        ".......a........",
        "......aa....a...",
        "......aba..aa...",
        ".....abba.aba...",
        "....abbbbabba...",
        "....abccbbbba...",
        "...abccccbbbba..",
        "...abcddccbbba..",
        "..abccddddcbba..",
        "..abcdddddccba..",
        "..abcddeeddcba..",
        "..abcdeeeedcba..",
        "..abcdeeeedcba..",
        "..abccdeedccba..",
        "...abccddccba...",
        "...abbccccbba...",
        "....abbbbbba....",
        ".....aabbaa.....",
        "......a..a......",
    ]
    grid(c, rows, {"a": "ember_300", "b": "ember_400", "c": "ember_500", "d": "ember_700", "e": "water_700"}, 0, 1)
    c.set(6, 12, color("ember_300"))
    c.set(9, 12, color("ember_300"))
    return c


# --- Cuenca de Alquitrán: el crudo y su vuelta ------------------------------------------


def oil(pure: bool, seed: int) -> Canvas:
    """Mancha de crudo en el suelo: charco oscuro con brillo sucio y bordes en
    diagonal. Purificada, desaparece: queda el suelo."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    noise = ValueNoise(seed)
    blob(c, 8, 10, 6, 3.5, "water_700", noise, 0.8)
    blob(c, 7, 9.5, 3, 1.5, "ash_700", noise, 0.6)
    x = rng.randint(4, 9)
    line(c, x, 9, x + 2, 9, "water_500")
    return c


def barrel(pure: bool) -> Canvas:
    """Barril volcado, 16x16, tumbado en diagonal y abollado. Purificado, se lo
    han llevado."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 13, 6, "soil_700")
    rows = [
        "................",
        "................",
        "................",
        "................",
        ".......aab......",
        "......abbbc.....",
        ".....abccbcc....",
        "....abccbbccd...",
        "...abccbbccdd...",
        "...bccbbccdd....",
        "...ecbbccdd.....",
        "...eebccdd......",
        "....eedd........",
    ]
    grid(c, rows, {"a": "roof_300", "b": "roof_500", "c": "roof_700", "d": "roof_900", "e": "water_700"})
    return c


def broken_pipe(pure: bool) -> Canvas:
    """Tubería partida, 32x16: el tubo de la refinería roto, con el extremo en
    diagonal. Purificada, la tapan: un tapón redondo y sin goteo."""
    c = Canvas(32, 16)
    ground_shadow(c, 14, 13, 13, "soil_700")
    c.rect(2, 6, 22, 5, color("ash_600"))
    line(c, 2, 6, 23, 6, "ash_400")
    line(c, 2, 10, 23, 10, "ash_700")
    for x in (7, 15):
        c.rect(x, 5, 2, 7, color("ash_700"))
        c.set(x, 5, color("ash_400"))
    if pure:
        blob(c, 24.5, 8.5, 3, 3, "ash_400")
        blob(c, 24.5, 8.5, 1.8, 1.8, "ash_600")
        return c
    # El extremo partido, en diagonal, y el crudo que sale.
    for y in range(6, 11):
        for x in range(24, 24 + (11 - y)):
            c.set(x, y, color("ash_600" if y > 6 else "ash_400"))
    line(c, 26, 10, 30, 14, "water_700")
    line(c, 27, 10, 31, 14, "water_700")
    c.set(28, 12, color("water_500"))
    return c


def boat(pure: bool) -> Canvas:
    """Barca de pesca varada, 32x16, escorada. Enferma, con el casco negro de
    crudo. Purificada, limpia: la madera vuelve."""
    c = Canvas(32, 16)
    ground_shadow(c, 16, 13, 14, "vital_900" if pure else "soil_700")
    hull = "wood_500" if pure else "water_700"
    hull_dark = "wood_700" if pure else "ash_700"
    for y in range(6, 12):
        inset = abs(y - 8)
        x0, x1 = 3 + inset * 2, 29 - inset
        line(c, x0, y, x1, y, hull if y < 10 else hull_dark)
    line(c, 5, 6, 28, 5, "wood_300")
    line(c, 12, 6, 12, 10, "wood_700")
    line(c, 20, 6, 20, 10, "wood_700")
    if not pure:
        for x, y in ((7, 11), (15, 11), (24, 10)):
            c.set(x, y, color("water_500"))
    return c


def torn_net(pure: bool) -> Canvas:
    """Red de pesca, 16x16. Enferma: rota, con el hueco en diagonal y manchada.
    Purificada: remendada, la cuadrícula entera."""
    c = Canvas(16, 16)
    ink = "ash_200" if pure else "ash_600"
    for x in range(2, 15, 3):
        line(c, x, 4, x, 13, ink)
    for y in range(4, 14, 3):
        line(c, 2, y, 14, y, ink)
    if not pure:
        for x, y in ((6, 6), (7, 7), (8, 8), (9, 9), (8, 7), (9, 8)):
            c.px[x, y] = (0, 0, 0, 0)
        c.set(11, 11, color("water_700"))
        c.set(12, 11, color("water_700"))
    return c


def reeds(pure: bool, seed: int) -> Canvas:
    """Juncos de la orilla. Enfermos: rotos y doblados en diagonal. Purificados:
    rectos, con la espiga."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    for i in range(5):
        x = 3 + i * 2 + rng.randint(0, 1)
        h = rng.randint(7, 11)
        if pure:
            line(c, x, 15, x, 15 - h, ("vital_700", "vital_600", "vital_500")[i % 3])
            c.set(x, 14 - h, color("wood_300"))
            c.set(x, 15 - h, color("wood_300"))
        else:
            line(c, x, 15, x, 15 - h // 2, "flora_500")
            line(c, x, 15 - h // 2, x + 3, 15 - h // 2 + 2, "flora_300")
    return c


def refinery_tower(pure: bool) -> Canvas:
    """El hito de la Cuenca: la refinería de Puerto Brea, 48x64. Un depósito
    redondo grande, la torre maciza con plataformas y la chimenea. Enferma, la
    antorcha de gas arde arriba (la causa sigue activa) y el humo queda
    quieto. Purificada, la antorcha se apaga y trepa la enredadera."""
    c = Canvas(48, 64)
    ground_shadow(c, 24, 60, 20, "vital_900" if pure else "soil_700")
    # Depósito: cilindro ancho a la izquierda.
    c.rect(2, 40, 20, 19, color("ash_600"))
    line(c, 2, 40, 2, 58, "ash_400")
    line(c, 21, 40, 21, 58, "ash_700")
    blob(c, 12, 40, 10, 3, "ash_400")
    blob(c, 12, 40, 8, 2, "ash_600")
    for y in (46, 52):
        line(c, 2, y, 21, y, "ash_700")
    line(c, 4, 58, 20, 58, "water_700")
    # Torre: cuerpo macizo que se estrecha, con plataformas.
    for y in range(12, 60):
        half = 4 + (y - 12) // 10
        for x in range(26 - half, 26 + half + 1):
            ink = "ash_400" if x <= 26 - half + 1 else "ash_700" if x >= 26 + half - 1 else "ash_600"
            c.set(x, y, color(ink))
        if (y - 12) % 9 == 0:
            line(c, 26 - half - 2, y, 26 + half + 2, y, "ash_200")
            line(c, 26 - half - 2, y + 1, 26 + half + 2, y + 1, "ash_700")
    for y in range(16, 58, 9):
        for x in range(23, 30, 3):
            c.set(x, y, color("water_700"))
    # Chimenea a la derecha, con anillos.
    c.rect(37, 18, 7, 42, color("ash_600"))
    line(c, 37, 18, 37, 59, "ash_400")
    line(c, 43, 18, 43, 59, "ash_700")
    for y in (26, 36, 46):
        line(c, 37, y, 43, y, "roof_500")
        line(c, 37, y + 1, 43, y + 1, "roof_700")
    if pure:
        for y in range(24, 60, 2):
            c.set(24 + (y % 4 == 0), y, color("vital_700"))
            c.set(38 + (y % 6 == 0), y, color("vital_700"))
            c.set(5 + (y % 4 == 0), max(y, 41), color("vital_700"))
        for x, y in ((23, 30), (25, 40), (39, 34), (38, 44), (6, 44), (14, 50)):
            blob(c, x, y, 2, 1.5, "vital_500")
            c.set(x - 1, y - 1, color("vital_300"))
    else:
        # La antorcha de gas, encima de la torre.
        flame = [("ember_700", 0, 0), ("ember_700", -1, -1), ("ember_500", 0, -1), ("ember_700", 1, -1),
                 ("ember_500", -1, -2), ("ember_400", 0, -2), ("ember_500", 1, -2),
                 ("ember_400", -1, -3), ("ember_300", 0, -3), ("ember_400", 1, -3),
                 ("ember_300", 0, -4), ("ember_400", -1, -4), ("ember_300", 0, -5), ("ember_300", 1, -6)]
        for ink, dx, dy in flame:
            c.set(26 + dx, 11 + dy, color(ink))
        # Humo quieto de la chimenea (enmienda 8: lo enfermo no se mueve).
        for x, y, r in ((40, 15, 3), (42, 11, 3.5), (39, 8, 3), (43, 5, 3.5), (40, 2, 2.5)):
            blob(c, x, y, r, r * 0.75, "ash_700")
            c.set(int(x) - 1, int(y) - 1, color("ash_600"))
    return c


def oil_monster(pure: bool) -> Canvas:
    """El Devorador de Petróleo en el mapa, 16x24: una masa de crudo con borde
    EMBER_300 (verify_tileset, parte 4) y dos ojos de brasa. Purificado, ya no
    está."""
    c = Canvas(16, 24)
    if pure:
        return c
    ground_shadow(c, 8, 22, 7, "soil_700")
    rows = [
        "................",
        "................",
        "......aaaa......",
        ".....abbbba.....",
        "....abbbbbba....",
        "...abbcbbcbba...",
        "...abbcbbcbba...",
        "..abbbbbbbbbba..",
        "..abbbbddbbbba..",
        ".abbbbddddbbbba.",
        ".abbbbbddbbbbba.",
        ".abbbbbbbbbbbba.",
        "abbbbbbbbbbbbbba",
        "abbebbbbbbbbebba",
        "abbbbbbbbbbbbbba",
        ".abbbbbbbbbbbba.",
        ".aabbbbbbbbbbaa.",
        "..aaaa.aa.aaaa..",
    ]
    grid(c, rows, {"a": "ember_300", "b": "water_700", "c": "ember_400", "d": "ash_700", "e": "water_500"}, 0, 4)
    return c


def pipe_blocker(pure: bool) -> Canvas:
    """Paso cerrado de la Cuenca, 16x16: tuberías retorcidas clavadas en el
    crudo, en diagonal y puntiagudas, sin contorno. Desaparece con la ola."""
    c = Canvas(16, 16)
    if pure:
        return c
    blob(c, 8, 13, 7, 2.5, "water_700")
    for x0, y0, x1, y1 in ((2, 14, 7, 1), (8, 14, 14, 3), (5, 13, 11, 5)):
        line(c, x0, y0, x1, y1, "ash_600")
        line(c, x0 + 1, y0, x1 + 1, y1, "ash_700")
        c.set(x1, y1, color("ash_400"))
    return c


# --- Costa Quebrada: el plástico y su vuelta ---------------------------------------------
# La basura de decorado es suelta, tumbada y en diagonal: nunca atada, en fardo
# ni en contenedor, que son las clases que responden de la Costa (catálogo 2a).
# El material se lee por silueta: botellas (trazos), red (cuadrícula), latas.


def snagged_bag(pure: bool) -> Canvas:
    """Arbusto de duna con bolsas de plástico enganchadas, 16x16. Purificado,
    el arbusto queda limpio y redondo."""
    c = bush(pure, 17)
    if pure:
        return c
    for x, y, ink in ((4, 5, "ash_200"), (5, 6, "ash_400"), (5, 5, "ash_200"),
                      (11, 7, "ash_400"), (12, 6, "ash_200"), (12, 7, "ash_400"), (9, 11, "ash_400")):
        c.set(x, y, color(ink))
    line(c, 3, 4, 2, 2, "ash_400")
    line(c, 13, 6, 15, 4, "ash_400")
    return c


def bottle(pure: bool, seed: int) -> Canvas:
    """Botella de plástico tumbada en diagonal. Purificada, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    x, y = rng.randint(3, 6), rng.randint(10, 12)
    for i in range(6):
        c.set(x + i, y - i // 2, color("ash_400" if i < 5 else "ash_200"))
        c.set(x + i, y - i // 2 + 1, color("ash_600"))
    c.set(x + 6, y - 3, color("roof_300"))
    return c


def ghost_net(pure: bool) -> Canvas:
    """Red fantasma enredada en las rocas, 32x16. Purificada, las rocas quedan
    limpias."""
    c = Canvas(32, 16)
    for cx, cy, rx in ((7, 10, 6), (19, 11, 7), (27, 9, 4)):
        blob(c, cx, cy + 1, rx, rx * 0.55, "ash_700")
        blob(c, cx - 0.6, cy, rx * 0.85, rx * 0.45, "ash_600")
        c.set(cx - 2, cy - 1, color("ash_400"))
    if pure:
        return c
    for x in range(2, 30, 3):
        line(c, x, 5, x + 3, 13, "ash_200" if x % 2 else "ash_400")
    for y in (6, 9, 12):
        line(c, 2, y, 29, y + 1, "ash_400")
    for x, y in ((12, 7), (13, 8), (14, 9), (22, 6), (23, 7)):
        c.px[x, y] = (0, 0, 0, 0)
    return c


def buoy(pure: bool) -> Canvas:
    """La boya de la red, varada y escorada, 16x16. Purificada, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 13, 5, "soil_700")
    rows = [
        "................",
        "................",
        "................",
        "................",
        "................",
        "........a.......",
        ".......aab......",
        "......abbbc.....",
        ".....abbbbcc....",
        "....dbbbbccc....",
        "....ddbbcccd....",
        ".....ddccdd.....",
        "......dddd......",
    ]
    grid(c, rows, {"a": "roof_100", "b": "roof_300", "c": "roof_500", "d": "roof_700"})
    line(c, 9, 5, 12, 2, "ash_400")
    return c


def torn_bag(pure: bool) -> Canvas:
    """Bolsa de basura rota, abierta en diagonal y vaciándose. Purificada, ya no
    está."""
    c = Canvas(16, 16)
    if pure:
        return c
    noise = ValueNoise(29)
    blob(c, 8, 10, 6, 4, "water_700", noise, 0.7)
    blob(c, 7, 9, 4, 2.5, "ash_700", noise, 0.5)
    line(c, 3, 7, 6, 10, "ash_600")
    for x, y, ink in ((11, 12, "ash_400"), (13, 11, "ash_200"), (12, 13, "roof_300"), (14, 13, "ash_400")):
        c.set(x, y, color(ink))
    return c


def trail(pure: bool, seed: int) -> Canvas:
    """El reguero: trozos de plástico en diagonal hacia la montaña. Purificado,
    ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    for i in range(5):
        x, y = 2 + i * 3, 13 - i * 2 + rng.randint(-1, 1)
        ink = ("ash_400", "ash_200", "roof_300", "ash_600", "ash_400")[i]
        c.set(x, y, color(ink))
        c.set(x + 1, y, color(ink))
        c.set(x + 1, y + 1, color("ash_700"))
    return c


def trash_mountain(pure: bool) -> Canvas:
    """El hito de la Costa: la montaña de basura del vertedero, 64x80 (asoma por
    encima de su base de 4x4). Enferma, un cerro alto de plástico en capas
    diagonales con siluetas de botella, red y lata, y gaviotas quietas.
    Purificada, el cerro se queda, pero es una duna: arena, hierba y flores."""
    c = Canvas(64, 80)
    rng = random.Random(53)
    noise = ValueNoise(53)
    ground_shadow(c, 32, 76, 30, "vital_900" if pure else "soil_700")
    if pure:
        blob(c, 32, 56, 30, 22, "wood_700")
        blob(c, 31, 53, 27, 19, "wood_500")
        blob(c, 27, 46, 14, 10, "wood_300")
        for _ in range(60):
            x, y = rng.randint(6, 58), rng.randint(36, 74)
            if c.get(x, y) in (color("wood_500"), color("wood_700")):
                line(c, x, y, x, y - 2, "vital_600")
                c.set(x, y - 3, color("vital_400"))
        for _ in range(16):
            x, y = rng.randint(8, 56), rng.randint(38, 72)
            if c.filled(x, y):
                c.set(x, y, color(rng.choice(["bloom_500", "bloom_300", "bloom_100"])))
        return c
    # Perfil de cerro: ancho abajo, pico arriba, en capas.
    for y in range(16, 78):
        t = (y - 16) / 62
        half = int(4 + t * 28 + (noise.fbm(y * 0.3, 1) - 0.5) * 6)
        for x in range(32 - half, 32 + half):
            ink = "water_700" if x > 32 + half - 4 or y > 74 else "ash_700"
            if x < 32 - half + 3 + int(t * 4):
                ink = "ash_600"
            c.set(x, y, color(ink))
    blob(c, 26, 44, 12, 14, "ash_600", noise, 0.4)
    for _ in range(44):
        x, y = rng.randint(6, 58), rng.randint(20, 74)
        if not c.filled(x, y):
            continue
        kind = rng.random()
        if kind < 0.4:
            for i in range(4):
                c.set(x + i, y - i // 2, color("ash_400"))
            c.set(x + 4, y - 2, color("roof_300"))
        elif kind < 0.7:
            for i in range(0, 6, 2):
                line(c, x + i, y, x + i + 2, y + 3, "ash_200")
            line(c, x, y + 1, x + 6, y + 2, "ash_400")
        else:
            c.set(x, y, color("ash_200"))
            c.set(x + 1, y + 1, color("ash_400"))
            c.set(x + 2, y + 1, color("water_500"))
    for x, y in ((16, 10), (44, 4), (52, 14), (30, 2)):
        line(c, x - 2, y, x, y + 1, "ash_400")
        line(c, x, y + 1, x + 2, y, "ash_400")
    return c


def plastic_monster(pure: bool) -> Canvas:
    """El Golem de Plástico en el mapa, 16x24: un cuerpo de basura compactada
    en diagonal, con borde EMBER_300 y ojos de brasa. Purificado, ya no está."""
    c = Canvas(16, 24)
    if pure:
        return c
    ground_shadow(c, 8, 22, 7, "soil_700")
    rows = [
        "................",
        ".....aaaaa......",
        "....abbcbba.....",
        "....abebeba.....",
        "....abbbbba.....",
        "...aabcbdbaa....",
        "..abbdbbbcbba...",
        ".abbcbbdbbbcba..",
        ".abdbbcbbdbbba..",
        "..abbbbbbbcba...",
        "..abcbbdbbbba...",
        "...abbbcbbba....",
        "...abba.abba....",
        "...abba.abba....",
        "..aabba.abbaa...",
        "..aaaa...aaaa...",
    ]
    grid(c, rows, {"a": "ember_300", "b": "ash_700", "c": "ash_400", "d": "roof_300", "e": "ember_400"}, 0, 6)
    return c


def scrap_blocker(pure: bool) -> Canvas:
    """Paso cerrado de la Costa, 16x16: chatarra y plástico retorcidos, en
    diagonal y puntiagudos, sin contorno. Desaparece con la ola."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 14, 7, "soil_700")
    for x0, y0, x1, y1, ink in ((1, 14, 13, 2, "ash_600"), (3, 3, 15, 13, "ash_700"),
                                (6, 15, 9, 1, "roof_500"), (0, 9, 14, 8, "ash_400")):
        line(c, x0, y0, x1, y1, ink)
        line(c, x0, y0 + 1, x1, y1 + 1, "water_700")
    return c


# --- Llanura Marchita: el monocultivo y su vuelta ----------------------------------------
# Las hileras van sin cerca: la parcela cercada es la clase que responde de la
# Llanura (catálogo 2a).


def sack(pure: bool) -> Canvas:
    """Saco de abono químico, abierto y tumbado en diagonal, 16x16, vertiendo
    polvo claro. No es un fardo atado (catálogo 2a). Purificado, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 13, 6, "soil_700")
    rows = [
        "................",
        "................",
        "................",
        "................",
        "......aa........",
        ".....abbb.......",
        "....abbbbc......",
        "...abbbbbcc.....",
        "...bbbbbbccd....",
        "...bbbbbccdd....",
        "....bbbccdd.ee..",
        ".....bccdd.eeee.",
        "......ddd...ee..",
    ]
    grid(c, rows, {"a": "ash_050", "b": "ash_200", "c": "ash_400", "d": "ash_600", "e": "ash_050"})
    return c


def salt(pure: bool, seed: int) -> Canvas:
    """Costra de sal en el suelo, en placas rotas: la tierra quemada por el
    abono (la aldea se llama Grano de Sal). Purificada, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    for _ in range(4):
        x, y = rng.randint(1, 10), rng.randint(3, 12)
        w = rng.randint(3, 5)
        for i in range(w):
            c.set(x + i, y + i // 2, color("ash_200"))
            c.set(x + i, y + i // 2 + 1, color("ash_400"))
    return c


def sprayer(pure: bool) -> Canvas:
    """La pulverizadora de agroquímicos, tumbada, 32x16: depósito y barra
    rota en diagonal. Purificada, la hierba la cubre: se queda, ya sin uso."""
    c = Canvas(32, 16)
    ground_shadow(c, 14, 13, 13, "vital_900" if pure else "soil_700")
    blob(c, 10, 8, 7, 4, "roof_700")
    blob(c, 9.5, 7.5, 6, 3.2, "roof_500")
    line(c, 5, 6, 13, 6, "roof_300")
    for k in range(2):
        line(c, 16, 9 + k, 30, 3 + k, "ash_600")
    for x in (19, 23, 27):
        c.set(x, 8 - (x - 19) // 3, color("ash_400"))
    blob(c, 6, 12, 2, 2, "water_700")
    blob(c, 14, 12, 2, 2, "water_700")
    if pure:
        for x in range(3, 30, 3):
            line(c, x, 14, x, 11, "vital_600")
            c.set(x, 10, color("vital_400"))
    return c


def wilted_row(pure: bool, seed: int) -> Canvas:
    """Hilera marchita: el cultivo muerto, doblado y gris. Purificada, cereal
    y legumbre alternos, como la hilera curada."""
    if pure:
        return crop_row(True, seed)
    c = Canvas(16, 16)
    rng = random.Random(seed)
    for x in range(1, 16, 3):
        h = rng.randint(4, 6)
        line(c, x, 15, x + 1, 15 - h, "ash_600")
        line(c, x + 1, 15 - h, x + 3, 13 - h + 2, "ash_400")
    line(c, 0, 15, 15, 15, "soil_700")
    return c


def silo(pure: bool) -> Canvas:
    """El hito de la Llanura: el silo de la aldea Grano de Sal, 48x64. Cilindro
    alto con cúpula y la tubería de vertido. Enfermo, oxidado y con la mancha
    clara del abono bajando. Purificado, la enredadera sube y anidan pájaros."""
    c = Canvas(48, 64)
    rng = random.Random(61)
    ground_shadow(c, 24, 60, 18, "vital_900" if pure else "soil_700")
    # Cuerpo: cilindro con sombreado por columnas.
    for x in range(10, 38):
        t = (x - 10) / 27
        ink = "ash_400" if t < 0.2 else "ash_600" if t < 0.75 else "ash_700"
        for y in range(16, 60):
            c.set(x, y, color(ink))
    for y in range(20, 60, 6):
        line(c, 10, y, 37, y, "ash_700")
    # Cúpula.
    blob(c, 24, 16, 14, 7, "roof_500")
    blob(c, 22, 14, 10, 4.5, "roof_300")
    blob(c, 24, 9, 3, 2.5, "roof_700")
    # Tubería de vertido hacia el suelo, en diagonal.
    for k in range(3):
        line(c, 37, 24 + k, 46, 40 + k, "ash_600" if k < 2 else "ash_700")
    if pure:
        for y in range(24, 60, 2):
            c.set(12 + (y % 4 == 0), y, color("vital_700"))
            c.set(34 + (y % 6 == 0), y, color("vital_700"))
        for x, y in ((12, 30), (13, 42), (34, 36), (35, 50), (20, 56)):
            blob(c, x, y, 2.2, 1.6, "vital_500")
            c.set(x - 1, y - 1, color("vital_300"))
        for x, y in ((18, 11), (30, 12)):
            c.set(x, y, color("aqua_300"))
            c.set(x + 1, y - 1, color("aqua_300"))
    else:
        # Óxido y el reguero claro del abono bajando por el costado.
        for _ in range(30):
            x, y = rng.randint(11, 36), rng.randint(18, 58)
            c.set(x, y, color("roof_700"))
        for y in range(26, 58):
            c.set(16 + (y // 7) % 2, y, color("ash_200"))
        line(c, 44, 41, 46, 46, "ash_200")
    return c


def specter_monster(pure: bool) -> Canvas:
    """El Espectro del Monocultivo en el mapa, 16x24: una figura pálida hecha de
    espigas iguales, con borde EMBER_300 y ojos de brasa. Purificado, ya no
    está."""
    c = Canvas(16, 24)
    if pure:
        return c
    ground_shadow(c, 8, 22, 6, "soil_700")
    rows = [
        "......a..a......",
        ".....aba.aba....",
        ".....abaaaba....",
        "....abbbbbbba...",
        "....abebbbeba...",
        "....abbbbbbba...",
        "...abbcbcbcbba..",
        "...abcbcbcbcba..",
        "..abbcbcbcbcbba.",
        "..abcbcbcbcbcba.",
        "..abbcbcbcbcbba.",
        "...abcbcbcbcba..",
        "...abbbbbbbbba..",
        "....abbbbbbba...",
        ".....abbbbba....",
        "......abbba.....",
        ".......aba......",
        "........a.......",
    ]
    grid(c, rows, {"a": "ember_300", "b": "ash_200", "c": "ash_400", "e": "ember_400"}, 0, 4)
    return c


def wire_blocker(pure: bool) -> Canvas:
    """Paso cerrado de la Llanura, 16x16: alambre de espino tendido en diagonal
    entre dos postes rotos, sin contorno. Desaparece con la ola."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 14, 7, "soil_700")
    line(c, 2, 15, 3, 4, "wood_700")
    line(c, 13, 15, 12, 5, "wood_700")
    for y0 in (6, 9, 12):
        line(c, 2, y0, 13, y0 + 2, "ash_400")
        for x in range(3, 13, 3):
            c.set(x, y0 + (x - 2) * 2 // 11 - 1, color("ash_200"))
            c.set(x, y0 + (x - 2) * 2 // 11 + 1, color("ash_200"))
    return c


# --- Cumbre Menguante: el deshielo y su vuelta ---------------------------------------------
# AQUA solo existe en lo purificado (enmienda 6): el hielo enfermo es gris
# (ASH), el que vuelve, blanco y azul. Nada se parece a una lona doblada: el
# manto reflectante es la clase que responde de la Cumbre (catálogo 2a).


def dark_rock(pure: bool, seed: int) -> Canvas:
    """Placa de roca oscura expuesta donde antes había nieve: es la que se
    calienta y derrite el resto. Purificada, la nieve vuelve a cubrirla."""
    c = Canvas(16, 16)
    noise = ValueNoise(seed)
    if pure:
        blob(c, 8, 10, 6.5, 3.5, "ash_200", noise, 0.5)
        blob(c, 7, 9, 4.5, 2.2, "ash_050", noise, 0.4)
        return c
    blob(c, 8, 10, 6.5, 3.5, "water_700", noise, 0.7)
    blob(c, 7.5, 9.5, 4.5, 2.4, "ash_700", noise, 0.6)
    line(c, 4, 9, 7, 12, "water_700")
    return c


def meltwater(pure: bool, seed: int) -> Canvas:
    """Reguero de deshielo, en diagonal. Purificado, ya no corre."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    x = rng.randint(2, 6)
    for i in range(10):
        c.set(x + i, 4 + i, color("water_500"))
        if i % 3 == 0:
            c.set(x + i + 1, 4 + i, color("water_300"))
    return c


def crack(pure: bool, seed: int) -> Canvas:
    """Grieta en el suelo de la montaña, en zigzag. Purificada, se cierra."""
    c = Canvas(16, 16)
    if pure:
        return c
    rng = random.Random(seed)
    x, y = 2, rng.randint(5, 9)
    for i in range(6):
        nx, ny = x + 2, y + rng.choice((-2, 2))
        line(c, x, y, nx, max(2, min(13, ny)), "water_700")
        x, y = nx, max(2, min(13, ny))
    return c


def pine(pure: bool, seed: int) -> Canvas:
    """Pino de montaña, 32x40: copa en pisos triangulares. Enfermo, pardo y
    ralo; purificado, verde."""
    c = Canvas(32, 40)
    rng = random.Random(seed)
    ground_shadow(c, 16, 36, 9, "vital_900" if pure else "soil_700")
    for y in range(28, 37):
        c.set(15, y, color("wood_700"))
        c.set(16, y, color("wood_500"))
    tiers = ((6, 6), (12, 9), (18, 12), (24, 14))
    dark, base, lit = (("vital_900", "vital_700", "vital_500") if pure
                       else ("flora_700", "flora_500", "flora_300"))
    for top, half in tiers:
        for k in range(8):
            y = top + k
            w = int(half * (k + 1) / 8)
            for x in range(16 - w, 16 + w + 1):
                ink = lit if x < 16 - w + 2 else dark if x > 16 + w - 2 else base
                if not pure and rng.random() < 0.12:
                    continue
                c.set(x, y, color(ink))
    c.set(16, 5, color(lit))
    return c


def boulder(seed: int) -> Canvas:
    """Peñasco de 32x32, de aristas partidas."""
    c = Canvas(32, 32)
    noise = ValueNoise(seed)
    ground_shadow(c, 16, 28, 13, "soil_700")
    blob(c, 16, 19, 13, 10, "ash_700", noise, 0.5)
    blob(c, 14.5, 17, 10, 7, "ash_600", noise, 0.5)
    blob(c, 12, 14, 5, 3.5, "ash_400", noise, 0.4)
    line(c, 9, 20, 15, 26, "water_700")
    return c


def stake(pure: bool) -> Canvas:
    """Estaca de medición del glaciar, 16x16: un poste con franjas que marcaba
    hasta dónde llegaba el hielo. Se queda: purificada, el hielo vuelve a su pie."""
    c = Canvas(16, 16)
    ground_shadow(c, 8, 14, 4, "soil_700")
    for y in range(1, 15):
        ink = "roof_300" if (y // 3) % 2 == 0 else "ash_200"
        c.set(7, y, color(ink))
        c.set(8, y, color("roof_500" if ink == "roof_300" else "ash_400"))
    if pure:
        blob(c, 8, 13.5, 6, 2.2, "ash_200")
        blob(c, 7, 13, 4, 1.4, "ash_050")
    return c


def moraine(pure: bool, seed: int) -> Canvas:
    """Morrena: piedras sueltas que dejó el glaciar al retirarse. Purificada,
    la hierba crece entre ellas."""
    c = Canvas(16, 16)
    rng = random.Random(seed)
    for _ in range(5):
        x, y = rng.randint(2, 12), rng.randint(5, 12)
        blob(c, x + 0.5, y + 0.5, 1.8, 1.3, "ash_600")
        c.set(x, y, color("ash_400"))
    if pure:
        for x in (4, 9, 13):
            line(c, x, 14, x, 12, "vital_600")
    return c


def ice_block(pure: bool) -> Canvas:
    """Bloque de hielo caído del glaciar, sucio y partido en diagonal. Gris: el
    azul solo vuelve purificado. Purificado, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 14, 6, "soil_700")
    rows = [
        "................",
        "................",
        "................",
        "......aab.......",
        ".....aabbbc.....",
        "....aabbbbcc....",
        "...aabbbbbccd...",
        "...abbbbbccdd...",
        "...bbbbbccddd...",
        "....bbbccddd....",
        ".....bccdd......",
        "......dd........",
    ]
    grid(c, rows, {"a": "ash_050", "b": "ash_200", "c": "ash_400", "d": "ash_600"}, 0, 2)
    line(c, 5, 6, 10, 11, "ash_600")
    return c


def meltpool(pure: bool, seed: int) -> Canvas:
    """Charca de deshielo, turbia. Purificada, ya no está."""
    c = Canvas(16, 16)
    if pure:
        return c
    noise = ValueNoise(seed)
    blob(c, 8, 10, 6.5, 3.5, "water_500", noise, 0.6)
    blob(c, 7, 9.5, 3.5, 1.6, "water_300", noise, 0.4)
    return c


def glacier(pure: bool) -> Canvas:
    """El hito de la Cumbre: el glaciar partido, 64x80, sobre el Refugio de
    Altahielo. Enfermo: hielo gris y sucio, partido por una grieta en diagonal,
    con la roca oscura asomando y la cascada de deshielo quieta (lo enfermo no
    se mueve). Purificado: entero, blanco y azul."""
    c = Canvas(64, 80)
    rng = random.Random(67)
    noise = ValueNoise(67)
    ground_shadow(c, 32, 76, 30, "vital_900" if pure else "soil_700")
    # Lengua de hielo: ancha abajo, con la cresta arriba.
    for y in range(8, 78):
        t = (y - 8) / 70
        half = int(8 + t * 23 + (noise.fbm(y * 0.25, 2) - 0.5) * 5)
        for x in range(32 - half, 32 + half):
            if pure:
                ink = "ash_050" if x < 32 - half + 6 else "aqua_100" if x < 32 + half - 6 else "aqua_300"
            else:
                ink = "ash_200" if x < 32 - half + 5 else "ash_400" if x < 32 + half - 5 else "ash_600"
            c.set(x, y, color(ink))
    # Bandas del hielo.
    for y in range(20, 76, 9):
        line(c, 32 - int(8 + (y - 8) / 70 * 23) + 3, y, 32 + int(8 + (y - 8) / 70 * 23) - 3, y + 2,
             "aqua_300" if pure else "ash_600")
    if not pure:
        # La grieta en diagonal, con la roca oscura asomando.
        for k in range(4):
            line(c, 18 + k, 14, 46 + k, 70, "water_700" if k < 3 else "ash_700")
        for _ in range(8):
            x, y = rng.randint(14, 50), rng.randint(30, 74)
            blob(c, x, y, 2.5, 1.8, "ash_700")
        # La cascada de deshielo, quieta.
        for y in range(40, 78):
            c.set(47 + (y % 3 == 0), y, color("water_500"))
            c.set(46, y, color("water_300") if y % 4 == 0 else color("water_500"))
    else:
        for x, y in ((24, 20), (36, 34), (28, 52)):
            c.set(x, y, color("ash_050"))
            c.set(x + 1, y, color("ash_050"))
    return c


def thaw_monster(pure: bool) -> Canvas:
    """El Coloso del Deshielo en el mapa, 16x24: hielo sucio que gotea, con borde
    EMBER_300 (el calor que lo derrite) y ojos de brasa. Purificado, ya no está."""
    c = Canvas(16, 24)
    if pure:
        return c
    ground_shadow(c, 8, 22, 7, "soil_700")
    rows = [
        "....aaaaaaa.....",
        "...abbbbbbba....",
        "..abbcbbbcbba...",
        "..abbebbbebba...",
        "..abbbbbbbbba...",
        ".aabbbbdbbbbaa..",
        "abbbbbdddbbbbba.",
        "abbbbbbdbbbbbba.",
        "abbcbbbbbbbcbba.",
        ".abbbbbbbbbbba..",
        "..abbbbbbbbba...",
        "..abba...abba...",
        "..abba...abba...",
        "..aaff...ffaa...",
        "....f.....f.....",
    ]
    grid(c, rows, {"a": "ember_300", "b": "ash_200", "c": "ash_050", "d": "ash_400", "e": "ember_400",
                   "f": "water_500"}, 0, 7)
    return c


def ice_blocker(pure: bool) -> Canvas:
    """Paso cerrado de la Cumbre, 16x16: esquirlas de hielo sucio y piedra
    clavadas en diagonal, puntiagudas y sin contorno. Desaparece con la ola."""
    c = Canvas(16, 16)
    if pure:
        return c
    ground_shadow(c, 8, 14, 7, "soil_700")
    for x0, y0, x1, y1, ink in ((2, 15, 6, 2, "ash_400"), (6, 15, 11, 3, "ash_200"),
                                (10, 15, 14, 5, "ash_600"), (0, 15, 3, 8, "ash_700")):
        line(c, x0, y0, x1, y1, ink)
        line(c, x0 + 1, y0, x1 + 1, y1, "ash_600")
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


def swayed(c: Canvas, below: int) -> Canvas:
    """Segundo cuadro del vaivén (enmienda 8): lo que está por encima de la
    fila `below` se corre 1 px a la derecha; el pie no se mueve."""
    out = Canvas(c.width, c.height)
    for y in range(c.height):
        for x in range(c.width):
            px = c.get(x, y)
            if px[3] == 0:
                continue
            out.set(x + (1 if y < below else 0), y, px)
    return out


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
    # Bosque de las Cenizas.
    for state, pure in (("sick", False), ("pure", True)):
        out[f"burnt_tree_{state}"] = burnt_tree(pure, 41)
        out[f"burnt_oak_{state}"] = burnt_oak(pure)
        out[f"felled_log_{state}"] = felled_log(pure)
        out[f"log_pile_{state}"] = log_pile(pure)
        out[f"ash_{state}"] = ash(pure, 12)
        out[f"blocker_ashen_forest_{state}"] = blocker(pure)
        out[f"monster_ashen_forest_{state}"] = flame_monster(pure)
        # Cuenca de Alquitrán.
        out[f"oil_{state}"] = oil(pure, 5)
        out[f"barrel_{state}"] = barrel(pure)
        out[f"broken_pipe_{state}"] = broken_pipe(pure)
        out[f"boat_{state}"] = boat(pure)
        out[f"torn_net_{state}"] = torn_net(pure)
        out[f"reeds_{state}"] = reeds(pure, 13)
        out[f"refinery_tower_{state}"] = refinery_tower(pure)
        out[f"monster_tar_basin_{state}"] = oil_monster(pure)
        out[f"blocker_tar_basin_{state}"] = pipe_blocker(pure)
        # Costa Quebrada.
        out[f"snagged_bag_{state}"] = snagged_bag(pure)
        out[f"bottle_{state}"] = bottle(pure, 3)
        out[f"ghost_net_{state}"] = ghost_net(pure)
        out[f"buoy_{state}"] = buoy(pure)
        out[f"torn_bag_{state}"] = torn_bag(pure)
        out[f"trail_{state}"] = trail(pure, 7)
        out[f"trash_mountain_{state}"] = trash_mountain(pure)
        out[f"monster_broken_coast_{state}"] = plastic_monster(pure)
        out[f"blocker_broken_coast_{state}"] = scrap_blocker(pure)
        # Llanura Marchita.
        out[f"sack_{state}"] = sack(pure)
        out[f"salt_{state}"] = salt(pure, 11)
        out[f"sprayer_{state}"] = sprayer(pure)
        out[f"wilted_row_{state}"] = wilted_row(pure, 9)
        out[f"silo_{state}"] = silo(pure)
        out[f"monster_withered_plain_{state}"] = specter_monster(pure)
        out[f"blocker_withered_plain_{state}"] = wire_blocker(pure)
        # Cumbre Menguante.
        out[f"dark_rock_{state}"] = dark_rock(pure, 71)
        out[f"meltwater_{state}"] = meltwater(pure, 72)
        out[f"crack_{state}"] = crack(pure, 73)
        out[f"pine_{state}"] = pine(pure, 74)
        out[f"stake_{state}"] = stake(pure)
        out[f"moraine_{state}"] = moraine(pure, 75)
        out[f"ice_block_{state}"] = ice_block(pure)
        out[f"meltpool_{state}"] = meltpool(pure, 76)
        out[f"glacier_{state}"] = glacier(pure)
        out[f"monster_waning_peak_{state}"] = thaw_monster(pure)
        out[f"blocker_waning_peak_{state}"] = ice_blocker(pure)
    out["boulder_sick"] = boulder(77)
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
    # Enmienda 8: segundo cuadro de lo que se mece, solo purificado.
    for name, below in (("grass", 12), ("flower", 11), ("weed", 11), ("crop_row", 11), ("reeds", 11)):
        out[f"{name}_pure_1"] = swayed(out[f"{name}_pure"], below)
    return out


def main() -> None:
    for name, canvas in pieces().items():
        canvas.save(OUT / f"{name}.png")
    print(f"  decorado: {len(pieces())} piezas en {OUT.relative_to(OUT.parents[3])}")


if __name__ == "__main__":
    main()
