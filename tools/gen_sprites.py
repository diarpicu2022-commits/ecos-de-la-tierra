"""Genera los sprites de los monstruos de *Ecos de la Tierra*.

Cada monstruo se dibuja en dos variantes, porque la purificación es la decisión
dominante de la pantalla de batalla y tiene que verse, no solo leerse:

    <monstruo>.png            la causa sigue activa
    <monstruo>_purified.png   la causa se atajó

En la variante purificada desaparece la brasa y entra el verde `vital`, único
acento del contrato. Es la misma idea que sostiene la dirección «Ceniza y
Brasa»: el color vuelve al mundo cuando el jugador ataja el daño.

Uso:
    python tools/gen_sprites.py
"""

from __future__ import annotations

import math
from pathlib import Path

from pixel import CHAR_RAMP, Canvas, EMBER_RAMP, VITAL_RAMP, ValueNoise, color, ramp

SPRITE_SIZE = 48
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "monsters"


# --- Piezas comunes ----------------------------------------------------------


def draw_branch(canvas: Canvas, x0: float, y0: float, x1: float, y1: float,
                thickness: float, noise: ValueNoise, ramp_names: list[str]) -> None:
    """Rama carbonizada: una línea que adelgaza hacia la punta."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / steps
        cx = x0 + (x1 - x0) * t
        cy = y0 + (y1 - y0) * t
        half = thickness * (1.0 - 0.75 * t)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if math.hypot(dx, dy) > half:
                    continue
                px, py = int(round(cx)) + dx, int(round(cy)) + dy
                shade = noise.fbm(px * 0.3, py * 0.3, 2)
                canvas.set(px, py, ramp(ramp_names, 0.1 + shade * 0.55))


def draw_trunk(canvas: Canvas, noise: ValueNoise, ramp_names: list[str],
               top: int = 21, bottom: int = 47) -> None:
    """Tronco quemado con las raíces abriéndose en la base."""
    for y in range(top, bottom + 1):
        t = (y - top) / (bottom - top)
        # Perfil de tronco: estrecho arriba y con las raíces abriéndose de
        # golpe en las últimas filas, que es lo que lo distingue de un poste.
        half = 3.0 + 3.0 * t + 7.0 * pow(t, 6.0)
        for x in range(SPRITE_SIZE):
            d = abs(x - 23.5)
            if d > half:
                continue
            # Vetas verticales: el ruido se estira en Y para que la corteza
            # parezca fibra de madera y no grano de televisor.
            grain = noise.fbm(x * 0.62, y * 0.11, 3)
            core = 1.0 - d / half
            canvas.set(x, y, ramp(ramp_names, 0.06 + grain * 0.46 + core * 0.30))


def draw_eyes(canvas: Canvas, glint: str, cy: int = 20,
              socket: str = "ash_950", angry: bool = True) -> None:
    """Dos cuencas oscuras con un punto de luz. La mirada ancla la silueta.

    La cuenca se dibuja siempre en el tono más oscuro de la paleta: sobre un
    fuego claro es lo único que despega la mirada del fondo.
    """
    for side, cx in ((-1, 16), (1, 31)):
        for dy in range(-3, 4):
            for dx in range(-4, 5):
                # Párpado caído hacia el centro: la inclinación es lo que
                # convierte dos manchas en una mirada.
                tilt = (dx * side) * 0.30 if angry else 0.0
                if abs(dx) * 0.62 + abs(dy + tilt) > 3.1:
                    continue
                canvas.set(cx + dx, cy + dy, color(socket))
        for dx in (-1, 0, 1):
            canvas.set(cx + dx, cy, color(glint))
            canvas.set(cx + dx, cy - 1, color(glint))


# --- Llama de la Deforestación ----------------------------------------------


def deforestation_flame(purified: bool) -> Canvas:
    """Árbol calcinado envuelto en fuego. Purificado, le vuelve la copa."""
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    noise = ValueNoise(seed=1704)

    trunk_ramp = CHAR_RAMP if not purified else ["ash_800", "ash_700", "ash_600", "ash_400"]

    if purified:
        _draw_canopy(canvas, noise)
    else:
        _draw_flame(canvas, noise)

    # Las ramas van sobre la llama: siluetas oscuras recortadas contra el
    # fuego, que es lo que hace legible que esto fue un árbol.
    draw_branch(canvas, 22, 28, 8, 17, 2.6, noise, trunk_ramp)
    draw_branch(canvas, 25, 29, 39, 18, 2.6, noise, trunk_ramp)
    draw_trunk(canvas, noise, trunk_ramp)

    draw_eyes(canvas, "vital_500" if purified else "ember_300")
    canvas.outline(color("ash_950"))
    return canvas


# Lenguas de fuego: (centro x, base y, punta y, ancho). Una llama es un haz de
# lenguas de alturas distintas; un solo cono con ruido se lee como un triángulo.
FLAME_LOBES = [
    (23.5, 35, 4, 15.0),
    (14.5, 33, 13, 7.5),
    (32.5, 33, 11, 7.5),
    (19.0, 31, 7, 5.0),
    (28.5, 32, 9, 5.5),
    (10.0, 31, 21, 4.5),
    (37.0, 31, 19, 4.5),
]


def _draw_flame(canvas: Canvas, noise: ValueNoise) -> None:
    """Cuerpo de fuego formado por varias lenguas de distinta altura."""
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            # De todas las lenguas, manda la que más cubre este píxel.
            inside = -1.0
            for lx, y_base, y_tip, width in FLAME_LOBES:
                if not (y_tip <= y <= y_base):
                    continue
                t = (y - y_tip) / (y_base - y_tip)
                half = max(0.6, width * pow(t, 0.55))
                # Vaivén lateral: una llama recta no parece fuego.
                cx = lx + 1.9 * math.sin(y * 0.29 + lx)
                inside = max(inside, 1.0 - abs(x - cx) / half)
            if inside <= -1.0:
                continue

            n = noise.fbm(x * 0.19, y * 0.16, 3)
            edge = inside + (n - 0.5) * 0.60
            if edge <= 0.0:
                continue
            # El calor sube desde la base: el núcleo blanco vive abajo, donde
            # el fuego toca el tronco, y se apaga hacia las puntas.
            heat = pow(edge, 0.78) * (0.32 + 0.70 * (y / 34.0))
            # Una segunda octava fina pica el núcleo. Sin esto el blanco se
            # cuaja en losas planas y el fuego parece papel recortado.
            heat += (noise.sample(x * 0.9, y * 0.7) - 0.5) * 0.17
            canvas.set(x, y, ramp(EMBER_RAMP, heat))


# Masas de la copa: (centro x, centro y, radio). Varias masas solapadas leen
# como follaje; una sola elipse lee como un globo.
CANOPY_LOBES = [
    (23.5, 13.0, 11.5),
    (14.0, 18.0, 8.5),
    (33.0, 17.5, 8.5),
    (19.0, 8.0, 6.5),
    (29.0, 9.0, 6.0),
    (23.5, 22.0, 9.0),
]


def _draw_canopy(canvas: Canvas, noise: ValueNoise) -> None:
    """Copa que rebrota donde antes había fuego."""
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            inside = -1.0
            for lx, ly, radius in CANOPY_LOBES:
                d = math.hypot((x - lx) * 1.05, (y - ly) * 1.2) / radius
                inside = max(inside, 1.0 - d)
            if inside <= -1.0:
                continue

            n = noise.fbm(x * 0.24, y * 0.24, 3)
            if inside + (n - 0.5) * 0.48 <= 0.0:
                continue
            # La luz entra por arriba a la izquierda, como en el resto del
            # juego. El reflejo claro solo aparece en la cresta iluminada.
            light = 0.26 + 0.42 * n + 0.34 * max(0.0, 1.0 - y / 22.0)
            if x > 23.5:
                light -= 0.16
            canvas.set(x, y, ramp(VITAL_RAMP, light))


# --- Piezas reutilizables por el resto de monstruos --------------------------


def blob(canvas: Canvas, lobes: list[tuple[float, float, float]],
         noise: ValueNoise, ramp_names: list[str], frequency: float = 0.22,
         jitter: float = 0.46, light_from_top: float = 0.34,
         squash: float = 1.0) -> None:
    """Masa orgánica formada por lóbulos solapados.

    Una sola elipse se lee como un globo; varias solapadas se leen como un
    cuerpo. El ruido rompe el borde para que no parezca vectorial.
    """
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            inside = -1.0
            for lx, ly, radius in lobes:
                d = math.hypot(x - lx, (y - ly) * squash) / radius
                inside = max(inside, 1.0 - d)
            if inside <= -1.0:
                continue
            n = noise.fbm(x * frequency, y * frequency, 3)
            if inside + (n - 0.5) * jitter <= 0.0:
                continue
            # La luz entra por arriba a la izquierda en todo el juego.
            light = 0.24 + 0.44 * n + light_from_top * max(0.0, 1.0 - y / 30.0)
            if x > 23.5:
                light -= 0.14
            canvas.set(x, y, ramp(ramp_names, light))


def corruption_marks(canvas: Canvas, points: list[tuple[int, int]],
                     purified: bool, size: int = 1) -> None:
    """Marca de que la causa sigue activa: brasa mientras no se purifique.

    Es la regla que unifica a los seis monstruos. El daño ambiental se ve
    siempre del mismo color, sea fuego, petróleo o deshielo, y al purificar ese
    color pasa al verde. El jugador aprende el código una vez y le sirve para
    todo el juego.
    """
    tone = "vital_500" if purified else "ember_300"
    for cx, cy in points:
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dx) + abs(dy) > size:
                    continue
                canvas.set(cx + dx, cy + dy, color(tone))


def drips(canvas: Canvas, columns: list[tuple[int, int, int]],
          ramp_names: list[str], noise: ValueNoise) -> None:
    """Goterones colgando del cuerpo: (x, y de inicio, largo)."""
    for x, y0, length in columns:
        for i in range(length):
            shade = noise.fbm(x * 0.4, (y0 + i) * 0.4, 2)
            canvas.set(x, y0 + i, ramp(ramp_names, 0.18 + shade * 0.4))
        canvas.set(x, y0 + length, ramp(ramp_names, 0.55))


def block(canvas: Canvas, x: int, y: int, w: int, h: int,
          ramp_names: list[str], tone: float) -> None:
    """Bloque plano con una arista clara arriba y otra oscura abajo."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            shade = tone
            if yy == y or xx == x:
                shade += 0.22
            elif yy == y + h - 1 or xx == x + w - 1:
                shade -= 0.18
            canvas.set(xx, yy, ramp(ramp_names, shade))


# --- Devorador de Petróleo ---------------------------------------------------

OIL_RAMP = ["ash_950", "ash_900", "ash_800", "ash_700", "ash_400"]
WATER_RAMP = ["vital_900", "vital_700", "vital_500", "ash_200"]


def oil_devourer(purified: bool) -> Canvas:
    """Marea viscosa de boca ancha. Purificada, agua clara en calma."""
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    noise = ValueNoise(seed=2208)
    body = WATER_RAMP if purified else OIL_RAMP

    if purified:
        # Purificado no es "lo mismo en verde": el bulto se derrumba en un
        # charco quieto. La silueta cambia de alto a plano, que es lo que se
        # percibe antes que el color.
        lobes = [(23.5, 38.0, 21.0), (11.0, 39.0, 12.0), (36.0, 39.0, 12.0)]
        blob(canvas, lobes, noise, body, frequency=0.18, jitter=0.26,
             squash=2.6, light_from_top=0.10)
        # Ondas en reposo, para que la calma se vea y no solo se lea.
        for wave, offset in ((0.5, 0), (0.7, 4)):
            for x in range(8, 40):
                y = 36 + offset + int(math.sin(x * wave) * 1.3)
                if canvas.filled(x, y):
                    canvas.set(x, y, color("ash_200"))
    else:
        lobes = [(23.5, 30.0, 17.0), (12.0, 33.0, 11.0), (35.0, 33.0, 11.0),
                 (23.5, 19.0, 13.0)]
        blob(canvas, lobes, noise, body, frequency=0.20, jitter=0.40,
             squash=1.25)
        # El crudo chorrea; el agua purificada no.
        drips(canvas, [(12, 40, 5), (20, 43, 4), (31, 42, 5), (37, 39, 4)],
              body, noise)

    corruption_marks(canvas, [(17, 18)] if not purified else [(17, 35)],
                     purified, size=2)
    corruption_marks(canvas, [(30, 18)] if not purified else [(30, 35)],
                     purified, size=2)
    canvas.outline(color("ash_950"))
    return canvas


# --- Gólem de Plástico -------------------------------------------------------

PLASTIC_RAMP = ["ash_900", "ash_700", "ash_600", "ash_400", "ash_200"]


def plastic_golem(purified: bool) -> Canvas:
    """Amasijo de residuos. Purificado, los residuos quedan separados y apilados.

    Es la única silueta del juego hecha a base de rectángulos: el contrato fija
    radio 0 en toda la interfaz, y aquí ese mismo criterio caracteriza al
    monstruo. Sin purificar, los bloques están revueltos y encajados a la
    fuerza; purificado, alineados en columnas, que es literalmente la
    contramedida (Separación en la Fuente).
    """
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    body = WATER_RAMP if purified else PLASTIC_RAMP

    if purified:
        # Tres columnas limpias: cada residuo, en su sitio.
        stacks = [(8, 3), (19, 4), (30, 3)]
        for sx, count in stacks:
            for i in range(count):
                block(canvas, sx, 44 - (i + 1) * 7, 11, 6, body,
                      0.36 + i * 0.13)
    else:
        # Bloques revueltos, con desalineaciones deliberadas.
        chunks = [
            (16, 6, 14, 9, 0.52), (11, 14, 11, 8, 0.30), (25, 15, 14, 10, 0.44),
            (9, 22, 13, 11, 0.58), (24, 25, 12, 9, 0.26), (14, 32, 10, 12, 0.40),
            (26, 34, 13, 10, 0.50), (19, 20, 8, 7, 0.66),
        ]
        for x, y, w, h, tone in chunks:
            block(canvas, x, y, w, h, body, tone)

    corruption_marks(canvas, [(20, 11), (28, 11)], purified, size=1)
    canvas.outline(color("ash_950"))
    return canvas


# --- Espectro del Monocultivo ------------------------------------------------

SPECTER_RAMP = ["ash_950", "ash_800", "ash_700", "ash_600", "ash_400"]


def monoculture_specter(purified: bool) -> Canvas:
    """Figura enjuta sobre un surco. Sin purificar, todos los tallos idénticos.

    La uniformidad es el daño: el surco repite el mismo tallo a la misma altura
    y a la misma distancia. Purificado, el surco se vuelve irregular y diverso,
    que es en lo que consiste la rotación de cultivos.
    """
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    noise = ValueNoise(seed=3312)
    body = SPECTER_RAMP
    crop = WATER_RAMP if purified else SPECTER_RAMP

    # Surco. Sin purificar: paso y altura constantes. Purificado: variados.
    for index, x in enumerate(range(4, 45, 5)):
        if purified:
            height = 7 + int(abs(math.sin(index * 1.9)) * 8)
            lean = 1 if index % 3 == 0 else 0
        else:
            height, lean = 9, 0
        for i in range(height):
            canvas.set(x + (lean if i > height - 3 else 0), 46 - i,
                       ramp(crop, 0.30 + (i / max(1, height)) * 0.45))
        if purified and height > 11:
            canvas.set(x - 1, 46 - height, color("vital_500"))
            canvas.set(x + 1, 46 - height, color("vital_500"))

    # Cuerpo espectral: estrecho, alargado, con los brazos caídos. Existe en
    # las dos variantes: purificar no borra al espíritu, lo apacigua. Si
    # desapareciera, los ojos quedarían flotando sobre un campo vacío.
    calm = ["ash_700", "ash_600", "ash_400", "ash_200", "ash_050"]
    figure = calm if purified else body
    blob(canvas, [(23.5, 22.0, 9.0), (23.5, 12.0, 7.0)], noise, figure,
         frequency=0.26, jitter=0.22 if purified else 0.34, squash=0.72)
    for side in (-1, 1):
        # Sin purificar los brazos cuelgan; purificado se recogen.
        reach = 14 if not purified else 8
        for i in range(reach):
            canvas.set(int(23.5 + side * (8 + i * 0.35)), 16 + i,
                       ramp(figure, 0.22 + i * 0.03))

    corruption_marks(canvas, [(20, 12), (28, 12)], purified, size=1)
    canvas.outline(color("ash_950"))
    return canvas


# --- Coloso del Deshielo -----------------------------------------------------

ICE_RAMP = ["ash_700", "ash_600", "ash_400", "ash_200", "ash_050"]


def thaw_colossus(purified: bool) -> Canvas:
    """Mole de hielo. Sin purificar está agrietada y chorreando.

    Aquí la brasa significa calor, que es exactamente la causa del daño: las
    grietas incandescentes son el deshielo en curso. Purificado, el hielo vuelve
    a estar entero y sin una sola veta de brasa.
    """
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    noise = ValueNoise(seed=4416)

    if purified:
        # El glaciar vuelve a estar entero: más masa, borde limpio y sin una
        # sola gota. La diferencia tiene que verse en la silueta, no solo en
        # que falten las grietas.
        lobes = [(23.5, 28.0, 19.0), (23.5, 11.0, 12.5), (10.0, 25.0, 9.5),
                 (37.0, 25.0, 9.5), (23.5, 40.0, 15.0)]
        blob(canvas, lobes, noise, ICE_RAMP, frequency=0.13, jitter=0.16,
             light_from_top=0.52)
    else:
        # Mermado y desigual: le falta hielo por todas partes.
        lobes = [(23.5, 31.0, 15.5), (23.5, 17.0, 9.0), (12.0, 29.0, 7.0),
                 (35.0, 29.0, 7.0)]
        blob(canvas, lobes, noise, ICE_RAMP, frequency=0.17, jitter=0.50,
             light_from_top=0.40)

    if not purified:
        # Grietas: líneas quebradas que bajan por el cuerpo.
        for start_x, start_y in ((16, 20), (29, 18), (23, 30)):
            x, y = start_x, start_y
            for step in range(11):
                canvas.set(x, y, color("ember_500"))
                if step % 3 == 0:
                    canvas.set(x, y, color("ember_300"))
                x += 1 if noise.sample(x * 0.7, y * 0.7) > 0.5 else -1
                y += 1
        drips(canvas, [(13, 39, 4), (24, 44, 3), (34, 38, 4)], ICE_RAMP, noise)

    corruption_marks(canvas, [(18, 16), (29, 16)] if not purified
                     else [(18, 12), (29, 12)], purified, size=1)
    canvas.outline(color("ash_950"))
    return canvas


# --- Sombra de la Avaricia (jefe final) --------------------------------------

SHADOW_RAMP = ["ash_950", "ash_950", "ash_900", "ash_800", "ash_700"]


def adaptive_boss(purified: bool) -> Canvas:
    """Masa de sombra con muchos ojos. Es el único que mira desde varios sitios.

    Los cinco pares de ojos no son adorno: el jefe exige cinco contramedidas
    distintas, y la silueta lo anuncia antes de que nadie lea una regla.
    """
    canvas = Canvas(SPRITE_SIZE, SPRITE_SIZE)
    noise = ValueNoise(seed=5520)
    # Al purificarse no se vuelve verde entero: la sombra sigue ahí y la luz
    # la va atravesando. Media rampa oscura, media vital.
    body = (["ash_900", "ash_800", "vital_900", "vital_700", "vital_500"]
            if purified else SHADOW_RAMP)

    lobes = [(23.5, 26.0, 16.0), (23.5, 13.0, 11.0), (13.0, 30.0, 9.0),
             (34.0, 30.0, 9.0), (23.5, 38.0, 12.0)]
    blob(canvas, lobes, noise, body, frequency=0.23, jitter=0.52,
         light_from_top=0.30)

    if not purified:
        # Bajo ragged: la sombra no se apoya en el suelo, se deshilacha.
        for x in range(SPRITE_SIZE):
            if not canvas.filled(x, 44):
                continue
            for i in range(int(noise.sample(x * 0.8, 9.0) * 4)):
                canvas.set(x, 45 + i, ramp(body, 0.2))

    # Cinco pares de ojos, uno por contramedida que exige.
    eyes = [(16, 14), (31, 14), (12, 26), (35, 26), (23, 34),
            (19, 20), (28, 20), (23, 8), (15, 34), (32, 34)]
    corruption_marks(canvas, eyes, purified, size=1)
    canvas.outline(color("ash_950"))
    return canvas


# --- Punto de entrada --------------------------------------------------------

MONSTERS = {
    "deforestation_flame": deforestation_flame,
    "oil_devourer": oil_devourer,
    "plastic_golem": plastic_golem,
    "monoculture_specter": monoculture_specter,
    "thaw_colossus": thaw_colossus,
    "adaptive_boss": adaptive_boss,
}


def main() -> None:
    for name, builder in MONSTERS.items():
        for purified in (False, True):
            canvas = builder(purified)
            suffix = "_purified" if purified else ""
            path = OUT_DIR / f"{name}{suffix}.png"
            canvas.save(path)
            print("  %s  (%dx%d)" % (path.name, canvas.width, canvas.height))
    print("Sprites en %s" % OUT_DIR)


if __name__ == "__main__":
    main()
