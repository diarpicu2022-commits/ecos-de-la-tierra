"""Genera el tileset de terreno de *Ecos de la Tierra*.

Paso 2b de la fase 5 del contrato «Vereda»
(docs/ux/anexos/2026-09-14-exploracion-top-down.md). Cada material existe en
dos estados, y la diferencia entre ellos es la del lenguaje del entorno:

    enfermo      valor bajo, silueta diagonal y rota, sin fauna
    purificado   valor alto, silueta redonda y continua

No se dibuja el estado solo con color: el verde y la brasa colapsan con
daltonismo (medido el 2026-09-23), así que cada estado cambia también de valor y
de forma. Ningún tile lleva contorno `ASH_050`: el contorno es de lo que
responde, y el terreno no responde.

Atlas: 16 columnas por 7 filas de 16 px.

    fila 0   suelo: 4 variantes enfermas y 4 purificadas (columnas 0-7)
    fila 1   camino enfermo      fila 2   camino purificado
    fila 3   agua enferma        fila 4   agua purificada
    fila 5   follaje enfermo     fila 6   follaje purificado

En las filas 1-6, la columna es la máscara de vecinos del mismo material:
N = 1, E = 2, S = 4, O = 8. La columna 15 es el interior.

Uso:
    python tools/gen_tiles.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from pixel import Canvas, color

T = 16
OUT = Path(__file__).resolve().parent.parent / "assets" / "tilesets" / "world.png"

N, E, S, W = 1, 2, 4, 8

SOIL_ROW = 0
OVERLAYS = ["path", "water", "flora"]  # filas 1-2, 3-4, 5-6


# --- Texturas: base plana y pocas formas contadas --------------------------------
#
# Primera versión (descartada el 2026-09-23): ruido umbralizado píxel a píxel.
# A 16 px formaba glifos repetidos que se leían como letras, y el follaje vivo
# era un remolino verde. SLYNYRD lo advierte: pocas tintas por tile, espacio
# negativo, y grupos que cruzan el borde para ocultar la costura. Aquí cada
# tile es una base plana con un puñado de formas, estampadas con envoltura
# módulo 16 para que el tile repita sin costura.


def stamp(grid: list[list[str]], x: int, y: int, token: str) -> None:
    grid[y % T][x % T] = token


def flat(token: str) -> list[list[str]]:
    return [[token] * T for _ in range(T)]


def diagonal(grid, x, y, length, token, lit=None):
    """Trazo a 45 grados: la forma del daño."""
    for i in range(length):
        stamp(grid, x + i, y + i, token)
        if lit and i == 0:
            stamp(grid, x + i - 1, y + i, lit)


def pebble(grid, x, y, token):
    """Guijarro ovalado, 2 px arriba y 3 abajo: la forma de lo curado.
    (Una cruz de 5 px se leía como destello, no como piedra.)"""
    for dx, dy in ((0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        stamp(grid, x + dx, y + dy, token)


def tuft(grid, x, y):
    """Mata de hierba de 5 px, redonda: sombra abajo, luz arriba."""
    for dx, dy, token in ((0, -1, "vital_500"), (-1, 0, "vital_700"), (0, 0, "vital_700"),
                          (1, 0, "vital_700"), (0, 1, "vital_900")):
        stamp(grid, x + dx, y + dy, token)


def clump(grid, cx, cy, r, base, lit, shade):
    """Copa redonda: sombra en el borde inferior derecho y un arco corto de luz
    arriba a la izquierda, no un anillo entero."""
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = dx * dx + dy * dy
            if d > r * r + r * 0.6:
                continue
            token = base
            if d >= (r - 1) * (r - 1):
                if dx + dy > 0:
                    token = shade
                elif dx < 0 and dy < 0:
                    token = lit
            stamp(grid, cx + dx, cy + dy, token)


def soil_tile(purified: bool, variant: int) -> list[list[str]]:
    rng = random.Random(100 + variant * 13 + (7 if purified else 0))
    if not purified:
        # Tierra hundida: sombra plana con esquirlas de tierra removida, en diagonal.
        # Solo dos de cada cuatro variantes llevan esquirla: en todas, el
        # suelo entero se leía como lluvia.
        g = flat("soil_700")
        if variant in (1, 3):
            diagonal(g, rng.randrange(T), rng.randrange(T), 3, "soil_500")
        return g
    # Tierra curada: un escalón más de valor y guijarros redondos.
    # Medido el 2026-09-23: con base plana SOIL_500 el cociente de valor frente
    # al suelo enfermo era 1,43, bajo el piso de 1,5. Aclararlo con SOIL_300 lo
    # acercaba al camino (dE 7,9). Lo que lo levanta es la hierba que vuelve:
    # dos matas redondas por tile. Sube el valor y separa el matiz del camino,
    # que sigue siendo tierra.
    #
    # La misma cantidad de verde, agrupada: dos matas por tile se leían como
    # confeti. Un parche de hierba en una variante, una mata en otra y tierra
    # limpia en las dos restantes. Grupos mayores y espacio negativo (SLYNYRD).
    g = flat("soil_500")
    if variant in (0, 1):
        pebble(g, rng.randrange(T), rng.randrange(T), "soil_300")
    # Los parches no cruzan el borde: el tile vecino es de otra variante y el
    # parche quedaría partido en astillas.
    if variant == 2:
        clump(g, rng.randint(5, 10), rng.randint(5, 10), 4, "vital_700", "vital_500", "vital_900")
    if variant == 3:
        tuft(g, rng.randint(2, 13), rng.randint(2, 13))
        clump(g, rng.randint(3, 12), rng.randint(3, 12), 2, "vital_700", "vital_500", "vital_900")
    return g


def path_tile(purified: bool) -> list[list[str]]:
    rng = random.Random(300)
    if not purified:
        # Camino roto: grietas diagonales de dos píxeles de grueso. Con tres
        # esquirlas sueltas el cociente de valor quedaba en 1,44.
        g = flat("soil_500")
        for x, y in ((1, 2), (8, 6), (3, 11)):
            diagonal(g, x, y, 5, "soil_700")
            diagonal(g, x + 1, y, 4, "soil_700")
        return g
    # Camino curado: tierra lisa, sin motas. Es la tinta más clara del suelo y
    # la única forma de que el camino gane valor sin acercarse al suelo
    # enfermo (medido: con motas, 1,48; con más grietas en el enfermo, dE 8,8).
    return flat("soil_300")


def water_tile(purified: bool) -> list[list[str]]:
    if not purified:
        # Agua muerta: sin reflejo, con una veta de crudo en diagonal.
        g = flat("water_700")
        diagonal(g, 2, 9, 5, "water_500", lit="water_300")
        diagonal(g, 11, 1, 3, "water_500")
        return g
    # Agua viva: base clara y rizos horizontales escalonados; un destello de
    # vida lejos de ellos. (Dos arcos y un punto juntos se leían como una cara.)
    g = flat("water_300")
    for x, y, n in ((2, 5, 4), (9, 12, 3), (11, 2, 2)):
        for dx in range(n):
            stamp(g, x + dx, y, "water_500")
    stamp(g, 5, 13, "vital_500")
    return g


def flora_tile(purified: bool) -> list[list[str]]:
    if not purified:
        # Follaje enfermo: masa oliva con hojas partidas en diagonal y huecos.
        g = flat("flora_500")
        for x, y in ((2, 3), (9, 1), (5, 10), (12, 9)):
            diagonal(g, x, y, 3, "flora_700", lit="flora_300")
        return g
    # Follaje vivo: copas redondas de tamaños distintos y colocación irregular.
    # Una rejilla de copas iguales se leía como escamas, y el verde pasaba de
    # recompensa a papel pintado. Luz solo en el borde superior izquierdo.
    g = flat("vital_700")
    for cx, cy, r in ((4, 4, 4), (13, 7, 3), (6, 13, 3)):
        clump(g, cx, cy, r, "vital_700", "vital_500", "vital_900")
    return g


_CACHE: dict = {}


def fill_token(material: str, x: int, y: int, purified: bool) -> str:
    key = (material, purified)
    if key not in _CACHE:
        _CACHE[key] = {"path": path_tile, "water": water_tile, "flora": flora_tile}[material](purified)
    return _CACHE[key][y][x]


def soil_px(x: int, y: int, purified: bool, variant: int) -> str:
    key = ("soil", purified, variant)
    if key not in _CACHE:
        _CACHE[key] = soil_tile(purified, variant)
    return _CACHE[key][y][x]


# --- Silueta de borde: la parte del lenguaje que no depende del color -----------


def edge_depth(t: int, purified: bool) -> int:
    """Cuánto se retira el material del borde abierto, según la posición `t` a
    lo largo del borde. Periodo divisor de 16: dos tiles vecinos casan.

    Enfermo: dientes de sierra, diagonales y rotos (Schatz: lo diagonal niega
    la invitación). Purificado: festón redondo y continuo.
    """
    if not purified:
        tooth = t % 4
        return 1 + (tooth if tooth < 3 else 1)  # 1, 2, 3, 2 -> sierra
    # Festón: arcos de 8 px de periodo que asoman hacia fuera, 2 px de fondo.
    u = ((t % 8) - 3.5) / 4.0
    return 1 + round(2.0 * (1.0 - math.sqrt(1.0 - u * u)))


def covered(x: int, y: int, mask: int, purified: bool) -> bool:
    """¿Este píxel pertenece al material, dado qué vecinos lo continúan?"""
    if not mask & N and y < edge_depth(x, purified):
        return False
    if not mask & S and (T - 1 - y) < edge_depth(x, purified):
        return False
    if not mask & W and x < edge_depth(y, purified):
        return False
    if not mask & E and (T - 1 - x) < edge_depth(y, purified):
        return False
    return True


EDGE_TOKEN = {
    # Línea de transición entre material y suelo. No es contorno de interacción:
    # es sombra o orilla del propio material, siempre de su misma rampa o del
    # suelo, nunca ASH_050.
    ("path", False): "soil_700",
    ("path", True): "soil_500",
    # Orilla clara en el agua enferma: sin ella, WATER_700 contra SOIL_700
    # dejaba el río casi invisible, y el río es una barrera que hay que leer.
    ("water", False): "soil_500",
    ("water", True): "soil_300",
    ("flora", False): "flora_700",
    ("flora", True): "vital_900",
}


def draw_overlay(canvas: Canvas, ox: int, oy: int, material: str,
                 purified: bool, mask: int) -> None:
    for y in range(T):
        for x in range(T):
            base = soil_px(x, y, purified, 0)
            canvas.set(ox + x, oy + y, color(base))
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, purified):
                canvas.set(ox + x, oy + y, color(fill_token(material, x, y, purified)))
    # Orilla: el primer píxel de suelo junto al material.
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, purified):
                continue
            touches = any(
                0 <= x + dx < T and 0 <= y + dy < T and covered(x + dx, y + dy, mask, purified)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if touches:
                canvas.set(ox + x, oy + y, color(EDGE_TOKEN[(material, purified)]))
    if material == "flora" and not mask & S:
        # Sombra proyectada al sur: el follaje tiene volumen y el suelo no.
        shadow = "soil_700" if not purified else "vital_900"
        for x in range(T):
            depth = edge_depth(x, purified)
            y = T - depth
            if 0 <= y < T and not covered(x, y, mask, purified):
                canvas.set(ox + x, oy + y, color(shadow))


def draw_soil(canvas: Canvas, ox: int, oy: int, purified: bool, variant: int) -> None:
    for y in range(T):
        for x in range(T):
            canvas.set(ox + x, oy + y, color(soil_px(x, y, purified, variant)))


def main() -> None:
    canvas = Canvas(16 * T, 7 * T)
    for variant in range(4):
        draw_soil(canvas, variant * T, SOIL_ROW, False, variant)
        draw_soil(canvas, (4 + variant) * T, SOIL_ROW, True, variant)
    for i, material in enumerate(OVERLAYS):
        for purified in (False, True):
            row = 1 + i * 2 + (1 if purified else 0)
            for mask in range(16):
                draw_overlay(canvas, mask * T, row * T, material, purified, mask)
    canvas.save(OUT)
    print(f"  tileset: {OUT.relative_to(OUT.parent.parent.parent)} ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()
