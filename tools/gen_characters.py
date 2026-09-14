"""Genera los sprites del grupo jugable de *Ecos de la Tierra*.

Vista de espaldas, 32×48 px: el grupo está en primer plano mirando al monstruo,
igual que en los RPG por turnos de los que parte el proyecto.

**Los cinco van en la rampa de ceniza, sin color propio.** El contrato reserva
el verde a la purificación y la brasa al daño activo, así que un personaje con
su propio color saturado rompería las dos reglas a la vez. La diferencia entre
ellos se juega donde el pixel art la juega de verdad: en la **silueta** (capucha,
trenza, mochila, sombrero) y en el **valor** (cada uno ocupa una franja distinta
de la rampa). El nombre lo pone su columna del HUD, justo debajo.

Uso:
    python tools/gen_characters.py
"""

from __future__ import annotations

import math
from pathlib import Path

from pixel import Canvas, ValueNoise, color, ramp

WIDTH, HEIGHT = 32, 48
CENTER = 15.5
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "party"

# Alturas del cuerpo, compartidas por los cinco para que el grupo se lea como
# un grupo y no como cinco muñecos de tamaños distintos.
HEAD_CY, HEAD_RX, HEAD_RY = 15.0, 5.0, 5.5
SHOULDER_Y, HIP_Y = 22, 34
FOOT_Y = 47

SKIN = ["ash_400", "ash_200", "ash_050"]


def ellipse(canvas: Canvas, cx: float, cy: float, rx: float, ry: float,
            ramp_names: list[str], base: float = 0.34) -> None:
    """Elipse sombreada con la luz entrando por arriba a la izquierda."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d > 1.0:
                continue
            light = base + (1.0 - d) * 0.30
            light += 0.16 if (x < cx and y < cy) else -0.10
            canvas.set(x, y, ramp(ramp_names, light))


def torso(canvas: Canvas, ramp_names: list[str], half_top: float = 6.0,
          half_bottom: float = 5.0) -> None:
    """Tronco visto de espaldas, más ancho de hombros que de cadera."""
    for y in range(SHOULDER_Y, HIP_Y + 1):
        t = (y - SHOULDER_Y) / float(HIP_Y - SHOULDER_Y)
        half = half_top + (half_bottom - half_top) * t
        for x in range(WIDTH):
            d = abs(x - CENTER)
            if d > half:
                continue
            # Un pliegue central marca la columna y evita que la espalda
            # parezca una tabla plana.
            light = 0.30 + (1.0 - d / half) * 0.22 - 0.14 * (x > CENTER)
            if d < 0.8:
                light -= 0.12
            canvas.set(x, y, ramp(ramp_names, light))


def arms(canvas: Canvas, ramp_names: list[str], spread: float = 6.6) -> None:
    for side in (-1, 1):
        for y in range(SHOULDER_Y + 1, HIP_Y):
            cx = CENTER + side * (spread + (y - SHOULDER_Y) * 0.08)
            for dx in (-1, 0, 1):
                canvas.set(int(round(cx)) + dx, y,
                           ramp(ramp_names, 0.24 + abs(dx) * 0.10))
        # Mano asomando bajo la manga.
        for dx in (-1, 0, 1):
            canvas.set(int(round(CENTER + side * (spread + 1.0))) + dx,
                       HIP_Y, ramp(SKIN, 0.5))


def legs(canvas: Canvas, ramp_names: list[str]) -> None:
    for side in (-1, 1):
        cx = CENTER + side * 2.6
        for y in range(HIP_Y + 1, FOOT_Y):
            for dx in (-1, 0, 1):
                canvas.set(int(round(cx)) + dx, y,
                           ramp(ramp_names, 0.22 + abs(dx) * 0.08))
        # Pie: dos filas más anchas, que apoyan la figura en el suelo.
        for dx in range(-2, 3):
            canvas.set(int(round(cx)) + dx, FOOT_Y, ramp(ramp_names, 0.14))


def head(canvas: Canvas) -> None:
    ellipse(canvas, CENTER, HEAD_CY, HEAD_RX, HEAD_RY, SKIN, base=0.30)
    # Cuello.
    for y in range(int(HEAD_CY + HEAD_RY) - 1, SHOULDER_Y):
        for dx in (-1, 0, 1):
            canvas.set(int(CENTER) + dx, y, ramp(SKIN, 0.22))


# --- Los cinco ---------------------------------------------------------------


def ilan() -> Canvas:
    """Protagonista. Pelo corto y el Fragmento del Vínculo a la espalda."""
    canvas = Canvas(WIDTH, HEIGHT)
    cloth = ["ash_400", "ash_200", "ash_050", "ash_050"]
    hair = ["ash_700", "ash_600", "ash_400"]

    head(canvas)
    ellipse(canvas, CENTER, HEAD_CY - 1.4, HEAD_RX + 0.4, HEAD_RY - 1.0, hair,
            base=0.34)
    torso(canvas, cloth)
    arms(canvas, cloth)
    legs(canvas, ["ash_700", "ash_600", "ash_400"])

    # El Fragmento del Vínculo: rombo entre los omóplatos. Es lo único que
    # distingue a Ilan de espaldas, y su túnica es la más clara del grupo, así
    # que el rombo necesita borde oscuro; en claro sobre claro desaparecía.
    for dy in range(-4, 5):
        for dx in range(-3, 4):
            reach = abs(dx) * 1.4 + abs(dy)
            if reach > 4:
                continue
            tone = "ash_050" if reach <= 2 else "ash_800"
            canvas.set(int(CENTER) + dx, 26 + dy, color(tone))
    return _finish(canvas)


def bruma() -> Canvas:
    """Guardabosques. Capucha calada: la silueta más cerrada del grupo."""
    canvas = Canvas(WIDTH, HEIGHT)
    cloak = ["ash_700", "ash_600", "ash_400", "ash_200"]

    head(canvas)
    torso(canvas, cloak, half_top=7.0, half_bottom=6.0)
    arms(canvas, cloak, spread=7.4)
    legs(canvas, ["ash_600", "ash_400", "ash_200"])
    # La capucha envuelve cabeza y hombros de una pieza.
    ellipse(canvas, CENTER, HEAD_CY - 0.6, HEAD_RX + 1.8, HEAD_RY + 1.4, cloak,
            base=0.30)
    for y in range(int(HEAD_CY + HEAD_RY) - 1, SHOULDER_Y + 3):
        half = 6.8 - (y - HEAD_CY - HEAD_RY) * 0.2
        for x in range(WIDTH):
            if abs(x - CENTER) <= half:
                canvas.set(x, y, ramp(cloak, 0.26))
    return _finish(canvas)


def coral() -> Canvas:
    """Hija de pescadores. Trenza larga que le cae por la espalda."""
    canvas = Canvas(WIDTH, HEIGHT)
    cloth = ["ash_600", "ash_400", "ash_200", "ash_050"]
    hair = ["ash_800", "ash_700", "ash_600"]

    head(canvas)
    ellipse(canvas, CENTER, HEAD_CY - 1.2, HEAD_RX + 0.6, HEAD_RY - 0.6, hair,
            base=0.38)
    torso(canvas, cloth)
    arms(canvas, cloth)
    legs(canvas, ["ash_600", "ash_400", "ash_200"])

    # La trenza baja por el centro del torso, sobre la ropa clara: es el
    # contraste lo que la hace visible a 32 px.
    for i in range(16):
        y = int(HEAD_CY + HEAD_RY) + i
        width = 2 if i % 3 != 0 else 1
        for dx in range(-width, width + 1):
            canvas.set(int(CENTER) + dx, y, ramp(hair, 0.30 + (i % 3) * 0.14))
    return _finish(canvas)


def nix() -> Canvas:
    """Ingeniero autodidacta. La mochila le ensancha toda la espalda."""
    canvas = Canvas(WIDTH, HEIGHT)
    cloth = ["ash_700", "ash_600", "ash_400", "ash_200"]
    pack = ["ash_400", "ash_200", "ash_050"]

    head(canvas)
    ellipse(canvas, CENTER, HEAD_CY - 1.6, HEAD_RX + 0.3, HEAD_RY - 1.4,
            ["ash_800", "ash_700", "ash_600"], base=0.36)
    torso(canvas, cloth)
    arms(canvas, cloth, spread=7.8)
    legs(canvas, ["ash_700", "ash_600", "ash_400"])

    # Mochila de chatarra: rectángulos desiguales, como el Gólem de Plástico.
    for x, y, w, h, tone in ((9, 21, 14, 11, 0.46), (11, 30, 10, 5, 0.30),
                             (20, 23, 5, 6, 0.60)):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                shade = tone + (0.20 if (yy == y or xx == x) else -0.14)
                canvas.set(xx, yy, ramp(pack, shade))
    return _finish(canvas)


def suri() -> Canvas:
    """Agricultora. Sombrero de ala ancha: la silueta más ancha por arriba."""
    canvas = Canvas(WIDTH, HEIGHT)
    cloth = ["ash_600", "ash_400", "ash_200", "ash_050"]
    hat = ["ash_700", "ash_600", "ash_400", "ash_200"]

    head(canvas)
    torso(canvas, cloth)
    arms(canvas, cloth)
    legs(canvas, ["ash_700", "ash_600", "ash_400"])

    # Ala del sombrero: una elipse muy aplastada que sobresale del cuerpo.
    ellipse(canvas, CENTER, HEAD_CY - 1.0, 10.5, 3.2, hat, base=0.30)
    ellipse(canvas, CENTER, HEAD_CY - 3.4, 4.2, 3.0, hat, base=0.44)
    return _finish(canvas)


def _finish(canvas: Canvas) -> Canvas:
    canvas.outline(color("ash_950"))
    return canvas


CHARACTERS = {
    "ilan": ilan,
    "bruma": bruma,
    "coral": coral,
    "nix": nix,
    "suri": suri,
}


def main() -> None:
    for name, builder in CHARACTERS.items():
        canvas = builder()
        path = OUT_DIR / f"{name}.png"
        canvas.save(path)
        print("  %s  (%dx%d)" % (path.name, canvas.width, canvas.height))
    print("Sprites del grupo en %s" % OUT_DIR)


if __name__ == "__main__":
    main()
