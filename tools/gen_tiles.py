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

Atlas: 16 columnas por 15 filas de 16 px.

    fila 0   suelo: 4 variantes enfermas y 4 purificadas (columnas 0-7)
    fila 1   camino enfermo      fila 2   camino purificado
    fila 3   agua enferma        fila 4   agua purificada
    fila 5   follaje enfermo     fila 6   follaje purificado
    fila 7   borde del prado: suelo purificado que linda con suelo enfermo
             (enmienda 6). La máscara dice qué vecinos están purificados.
    fila 8   agua purificada, segundo cuadro (enmienda 8): el brillo del agua.
    fila 9   arena enferma       fila 10  arena purificada (enmienda 9, la Costa)
    fila 11  muro enfermo        fila 12  muro purificado (enmienda 10, la Cripta)
    fila 13  losa enferma        fila 14  losa purificada (enmienda 10)

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
MEADOW_EDGE_ROW = 7
WATER_ALT_ROW = 8
SAND_ROW = 9  # 9 enferma, 10 purificada
WALL_ROW = 11  # 11 enfermo, 12 purificado
FLOOR_ROW = 13  # 13 enferma, 14 purificada


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
    # Enmienda 6 (2026-10-28): la tierra curada vuelve como prado, el suelo de
    # hierba de los pueblos de GBA. Base VITAL_600, verde de hierba más
    # amarillo que el acento (con VITAL_500 de base, un prado entero era
    # neón), y briznas de 2 px: pie VITAL_700, punta VITAL_400. Cada variante
    # cambia la colocación para que el prado no se lea como rejilla.
    #
    # Historia: hasta el 2026-10-28 era tierra SOIL_500 con matas redondas;
    # al juntarse en una zona entera se leía como lunares sobre barro.
    g = flat("vital_600")
    blades = 7 + variant
    for _ in range(blades):
        x, y = rng.randrange(1, T - 1), rng.randrange(2, T)
        stamp(g, x, y, "vital_700")
        stamp(g, x, y - 1, "vital_400")
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
    # Enmienda 6 (2026-10-28): el agua purificada recupera el azul (AQUA), por
    # encima del techo de saturación, como el verde. El destello deja de ser
    # verde: el azul ya dice por sí solo que el agua está viva.
    # Medido el mismo día: con base AQUA_500 y rizos AQUA_300, el contorno
    # ASH_050 de lo que responde bajaba a 1,10:1 (piso 3:1). Base AQUA_700 y
    # rizos AQUA_900: el azul sigue y el contorno se lee.
    g = flat("aqua_700")
    for x, y, n in ((2, 5, 4), (9, 12, 3), (11, 2, 2)):
        for dx in range(n):
            stamp(g, x + dx, y, "aqua_900")
    return g


def water_alt_tile(purified: bool) -> list[list[str]]:
    """Segundo cuadro del agua viva (enmienda 8, 2026-10-28): los mismos rizos
    corridos 2 px a la derecha, dando la vuelta al tile para que casen los
    vecinos. Solo existe purificado: el agua muerta no se mueve."""
    g = flat("aqua_700")
    for x, y, n in ((2, 5, 4), (9, 12, 3), (11, 2, 2)):
        for dx in range(n):
            stamp(g, (x + dx + 2) % T, y, "aqua_900")
    return g


def sand_tile(purified: bool) -> list[list[str]]:
    """Arena de la Costa (enmienda 9, 2026-10-28). Enferma: arena gris
    (ASH_700) con ondas rotas en diagonal y puntos de microplástico. Purificada:
    arena limpia, WOOD_500, con ondas redondas WOOD_700. Ningún color nuevo.

    Medido el mismo día:
    - con base SOIL_500, la arena enferma quedaba a dE 3,3 del camino, y los
      puntos ASH_400 bajaban el contorno a 2,31:1;
    - la purificada no llega a dE 9 del camino purificado con ningún token que
      pase el contorno y los acentos. WOOD_300 se quedaba en 2,62:1 con el
      verde y ROOF_300 en 2,46:1; WOOD_100 bajaba el contorno a 2,35:1.

    Diego aceptó un piso propio de 6 para ese par, porque la diferencia la cargan
    las ondas y el borde. WOOD_500 con ondas WOOD_700 da dE 6,9 y valor 1,56
    (verify_tileset)."""
    rng = random.Random(500 + (1 if purified else 0))
    if not purified:
        g = flat("ash_700")
        for x, y in ((1, 3), (7, 9), (10, 1)):
            diagonal(g, x, y, 4, "ash_600")
        for _ in range(9):
            stamp(g, rng.randrange(T), rng.randrange(T), "soil_300")
        return g
    g = flat("wood_500")
    for x, y, n in ((2, 4, 5), (8, 10, 6), (4, 14, 4)):
        for dx in range(n):
            stamp(g, x + dx, y + (1 if dx in (0, n - 1) else 0), "wood_700")
    return g


def floor_tile(purified: bool) -> list[list[str]]:
    """Losa de la Cripta (enmienda 10, 2026-10-28). Enferma: losas frías
    (WATER_300) con juntas WATER_500; las grietas van en el decorado, para que
    no se repitan tile a tile. Purificada: la
    losa se calienta (SOIL_300) y el musgo vuelve entre las juntas. Más clara que el muro, para que el suelo se lea como suelo."""
    if not purified:
        g = flat("water_300")
        for y in range(8):
            stamp(g, 0, y, "water_500")
        for y in range(8, T):
            stamp(g, 8, y, "water_500")
        for x in range(T):
            stamp(g, x, 7, "water_500")
            stamp(g, x, 15, "water_500")
        return g
    g = flat("soil_300")
    for x in range(T):
        stamp(g, x, 7, "wood_500")
        stamp(g, x, 15, "wood_500")
    for y in range(8):
        stamp(g, 0, y, "wood_500")
    for y in range(8, T):
        stamp(g, 8, y, "wood_500")
    # El musgo crece en las juntas, en tramos cortos: con matas redondas en
    # cada tile, la Cripta purificada se leía como un prado de lunares.
    # Una mata grande sobre la junta y musgo que sigue la junta: con cuatro
    # matas iguales por tile, la Cripta purificada se leía como lunares.
    clump(g, 4, 7, 3, "vital_700", "vital_500", "vital_900")
    for x in range(8, 15):
        stamp(g, x, 15, "vital_700")
        stamp(g, x, 14, "vital_700" if x % 3 == 0 else "vital_500")
    for y in range(9, 14):
        stamp(g, 8, y, "vital_700")
    stamp(g, 9, 10, "vital_500")
    stamp(g, 9, 12, "vital_500")
    stamp(g, 7, 11, "vital_500")
    clump(g, 13, 3, 2, "vital_700", "vital_500", "vital_900")
    return g


def wall_tile(purified: bool) -> list[list[str]]:
    """Muro de la Cripta (enmienda 10). Enfermo: sillares oscuros (WATER_700)
    con la arista clara ASH_700 y una fisura en diagonal. Purificado: sillares
    ASH_700 y una hiedra que baja por las juntas (VITAL)."""
    if not purified:
        g = flat("water_700")
        for row in range(0, T, 4):
            off = 0 if (row // 4) % 2 == 0 else 4
            for x in range(T):
                stamp(g, x, row, "ash_700")
            for x in range(off, T, 8):
                for dy in range(4):
                    stamp(g, x, row + dy, "ash_700")
        diagonal(g, 3, 6, 6, "water_700")
        return g
    g = flat("ash_700")
    for row in range(0, T, 4):
        off = 0 if (row // 4) % 2 == 0 else 4
        for x in range(T):
            stamp(g, x, row, "ash_600")
        for x in range(off, T, 8):
            for dy in range(4):
                stamp(g, x, row + dy, "ash_600")
    # La hiedra baja por una junta vertical; no cubre el sillar entero.
    for y in range(1, 12):
        stamp(g, 4, y, "vital_700")
    for x, y in ((3, 2), (5, 4), (3, 6), (5, 8), (3, 10)):
        stamp(g, x, y, "vital_500")
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
    #
    # Calmado el 2026-09-29: con tres copas por tile la masa seguía leyéndose
    # como escamas. Dos copas y más base `VITAL_700` (SLYNYRD: espacio negativo
    # antes que más detalle). Una sola copa por tile se descartó: dibujaba una
    # retícula perfecta de lunares, peor que las escamas.
    g = flat("vital_700")
    for cx, cy, r in ((5, 5, 4), (12, 12, 3)):
        clump(g, cx, cy, r, "vital_700", "vital_500", "vital_900")
    return g


_CACHE: dict = {}


def fill_token(material: str, x: int, y: int, purified: bool) -> str:
    key = (material, purified)
    if key not in _CACHE:
        _CACHE[key] = {"path": path_tile, "water": water_tile, "water_alt": water_alt_tile,
                       "flora": flora_tile, "sand": sand_tile, "wall": wall_tile,
                       "floor": floor_tile}[material](purified)
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
    ("water_alt", True): "soil_300",
    ("sand", False): "soil_700",
    ("sand", True): "wood_700",
    ("wall", False): "water_700",
    ("wall", True): "vital_900",
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


def draw_stone(canvas: Canvas, ox: int, oy: int, material: str, purified: bool, mask: int) -> None:
    """La piedra de la Cripta (enmienda 10). La losa ocupa el tile entero: en
    una cripta no hay tierra debajo. El muro se dibuja sobre la losa, con el
    borde en sierra (enfermo) o en festón (purificado) como el follaje."""
    for y in range(T):
        for x in range(T):
            canvas.set(ox + x, oy + y, color(fill_token("floor", x, y, purified)))
    if material == "floor":
        return
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, purified):
                canvas.set(ox + x, oy + y, color(fill_token("wall", x, y, purified)))
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, purified):
                continue
            if any(0 <= x + dx < T and 0 <= y + dy < T and covered(x + dx, y + dy, mask, purified)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                canvas.set(ox + x, oy + y, color(EDGE_TOKEN[("wall", purified)]))


def draw_meadow_edge(canvas: Canvas, ox: int, oy: int, mask: int) -> None:
    """El prado entra en la tierra enferma con el festón redondo de lo
    purificado, y una línea VITAL_900 le da el canto. Sin esta fila, una parte
    purificada de Valdehoja acababa en escalones de tile entero."""
    for y in range(T):
        for x in range(T):
            canvas.set(ox + x, oy + y, color(soil_px(x, y, False, 0)))
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, True):
                canvas.set(ox + x, oy + y, color(soil_px(x, y, True, 2)))
    for y in range(T):
        for x in range(T):
            if covered(x, y, mask, True):
                continue
            if any(0 <= x + dx < T and 0 <= y + dy < T and covered(x + dx, y + dy, mask, True)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                canvas.set(ox + x, oy + y, color("vital_900"))


def draw_soil(canvas: Canvas, ox: int, oy: int, purified: bool, variant: int) -> None:
    for y in range(T):
        for x in range(T):
            canvas.set(ox + x, oy + y, color(soil_px(x, y, purified, variant)))


def main() -> None:
    canvas = Canvas(16 * T, 15 * T)
    for variant in range(4):
        draw_soil(canvas, variant * T, SOIL_ROW, False, variant)
        draw_soil(canvas, (4 + variant) * T, SOIL_ROW, True, variant)
    for i, material in enumerate(OVERLAYS):
        for purified in (False, True):
            row = 1 + i * 2 + (1 if purified else 0)
            for mask in range(16):
                draw_overlay(canvas, mask * T, row * T, material, purified, mask)
    for mask in range(16):
        draw_meadow_edge(canvas, mask * T, MEADOW_EDGE_ROW * T, mask)
        draw_overlay(canvas, mask * T, WATER_ALT_ROW * T, "water_alt", True, mask)
        draw_overlay(canvas, mask * T, SAND_ROW * T, "sand", False, mask)
        draw_overlay(canvas, mask * T, (SAND_ROW + 1) * T, "sand", True, mask)
        for i, purified in enumerate((False, True)):
            draw_stone(canvas, mask * T, (WALL_ROW + i) * T, "wall", purified, mask)
            draw_stone(canvas, mask * T, (FLOOR_ROW + i) * T, "floor", purified, mask)
    canvas.save(OUT)
    print(f"  tileset: {OUT.relative_to(OUT.parent.parent.parent)} ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()
