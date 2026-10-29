"""Genera los retratos de diálogo de *Ecos de la Tierra* (contrato «Columna»,
docs/ux/anexos/2026-10-28-dialogos.md, §3).

Busto de frente, 48×48, sobre fondo ASH_900 (la ventana del retrato dentro del
panel). Siete voces y **dos expresiones** cada una: la neutra y la que define
su arco. Como los sprites del grupo, **todo en la rampa de ceniza**: el verde
es de la purificación y la brasa del daño activo. Lo que distingue a cada uno
es la **silueta** (lo mismo que en su sprite de combate: capucha, trenza,
gafas, sombrero) y el valor.

    ilan   pelo corto y el Fragmento al cuello · neutral / determinado
    yara   el ave mensajera (Yara habla por ella) · neutral / alerta
    bruma  capucha · neutral / dolida (perdió su hogar en un incendio)
    coral  trenza sobre el hombro · neutral / risa (el alivio cómico)
    nix    pelo revuelto en punta y gafas de taller · neutral / concentrado (gafas puestas)
    suri   sombrero de ala ancha · neutral / firme
    rasgo  gorra de visera y cuello militar · neutral / duda (su arco)

Salida: assets/sprites/portraits/<voz>_<expresión>.png

Uso:
    python tools/gen_portraits.py
"""

from __future__ import annotations

import math
from pathlib import Path

from pixel import Canvas, color, ramp

SIZE = 48
CX = 23.5
OUT = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "portraits"

SKIN = ["ash_400", "ash_200", "ash_050"]
HEAD_CY, HEAD_RX, HEAD_RY = 21.0, 9.0, 10.5
EYE_Y = 22
EYE_DX = 4


def fill_ellipse(c: Canvas, cx: float, cy: float, rx: float, ry: float, ramp_names, base=0.34) -> None:
    """Elipse sombreada con la luz por arriba a la izquierda, sin interpolar.
    La luz es un plano inclinado (más a la izquierda y arriba), no un corte en
    el centro: el corte partía los hombros en dos mitades."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d > 1.0:
                continue
            slope = 0.10 * (cx - x) / rx + 0.08 * (cy - y) / ry
            light = base + (1.0 - d) * 0.28 + slope
            c.set(x, y, ramp(ramp_names, light))


def shoulders(c: Canvas, ramp_names) -> None:
    """Hombros y pecho: media elipse ancha que sale por abajo."""
    fill_ellipse(c, CX, 50.0, 20.0, 15.0, ramp_names, base=0.30)
    for y in range(30, 37):
        for x in range(int(CX) - 3, int(CX) + 5):
            c.set(x, y, color("ash_400"))   # cuello


def face(c: Canvas, mood: str) -> None:
    """Cabeza, ojos, cejas y boca. La expresión cambia cejas, ojos y boca."""
    fill_ellipse(c, CX, HEAD_CY, HEAD_RX, HEAD_RY, SKIN, base=0.40)
    ink = color("ash_950")
    brow = color("ash_800")
    for side in (-1, 1):
        ex = int(CX) + side * EYE_DX
        if mood == "laugh":
            # Ojos cerrados en arco: la risa se lee en los ojos.
            c.set(ex - 1, EYE_Y + 1, ink)
            c.set(ex, EYE_Y, ink)
            c.set(ex + 1, EYE_Y, ink)
            c.set(ex + 2, EYE_Y + 1, ink)
        elif mood == "wide":
            for dy in (-1, 0, 1):
                c.set(ex, EYE_Y + dy, ink)
                c.set(ex + 1, EYE_Y + dy, ink)
        else:
            c.set(ex, EYE_Y, ink)
            c.set(ex + 1, EYE_Y, ink)
            c.set(ex, EYE_Y + 1, ink)
            c.set(ex + 1, EYE_Y + 1, ink)
        # Cejas de 2 px de grueso: rectas, en ceño (bajan hacia el centro),
        # en pena (suben hacia el centro) o, en la duda, solo una alzada.
        for i in range(5):
            x = ex - 2 + i if side < 0 else ex + 3 - i
            if mood in ("frown", "focus"):
                y = EYE_Y - 4 + i // 2
            elif mood == "sad":
                y = EYE_Y - 2 - i // 2
            elif mood == "doubt":
                y = EYE_Y - 4 - (i // 2 if side > 0 else 0)
            elif mood == "laugh":
                y = EYE_Y - 4 - (1 if 0 < i < 4 else 0)
            else:
                y = EYE_Y - 4
            c.set(x, y, brow)
            c.set(x, y + 1, brow)
    mouth = color("ash_700")
    my = 28
    if mood == "laugh":
        # Boca abierta de tres filas.
        for x in range(int(CX) - 3, int(CX) + 5):
            c.set(x, my, ink)
        for x in range(int(CX) - 2, int(CX) + 4):
            c.set(x, my + 1, ink)
            c.set(x, my + 2, color("ash_800"))
    elif mood == "frown":
        # Labios apretados: línea corta y gruesa.
        for x in range(int(CX) - 1, int(CX) + 3):
            c.set(x, my, ink)
            c.set(x, my + 1, mouth)
    elif mood == "sad":
        for i, x in enumerate(range(int(CX) - 2, int(CX) + 4)):
            c.set(x, my + (0 if 0 < i < 5 else 1), mouth)
    elif mood == "doubt":
        for i, x in enumerate(range(int(CX) - 2, int(CX) + 4)):
            c.set(x, my + (1 if i < 3 else 0), mouth)
    else:
        for x in range(int(CX) - 2, int(CX) + 4):
            c.set(x, my, mouth)


def finish(c: Canvas) -> Canvas:
    """Contorno de personaje y fondo de la ventana del retrato."""
    c.outline(color("ash_950"))
    out = Canvas(SIZE, SIZE)
    out.rect(0, 0, SIZE, SIZE, color("ash_900"))
    for y in range(SIZE):
        for x in range(SIZE):
            px = c.get(x, y)
            if px[3] > 0:
                out.set(x, y, px)
    return out


def ilan(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    shoulders(c, ["ash_400", "ash_200", "ash_050"])
    face(c, "frown" if mood == "arc" else "neutral")
    # Pelo corto: casquete oscuro con flequillo recto.
    for y in range(9, 17):
        for x in range(13, 35):
            d = math.hypot((x - CX) / 10.0, (y - 16.5) / 8.0)
            if d <= 1.0 and y < 15 + (1 if 16 < x < 31 else 0):
                c.set(x, y, ramp(["ash_700", "ash_600", "ash_400"], 0.34 + (0.14 if x < CX else 0)))
    # El Fragmento del Vínculo: rombo al cuello.
    for dy in range(-3, 4):
        for dx in range(-2, 3):
            reach = abs(dx) * 1.5 + abs(dy)
            if reach <= 3:
                c.set(int(CX) + dx, 40 + dy, color("ash_050" if reach <= 1.5 else "ash_800"))
    return finish(c)


def yara(mood: str) -> Canvas:
    """El ave mensajera: cuerpo redondo de perfil, pico y cola. Alerta: alas
    abiertas."""
    c = Canvas(SIZE, SIZE)
    body = ["ash_600", "ash_400", "ash_200", "ash_050"]
    fill_ellipse(c, 24, 28, 11, 9, body, base=0.36)
    fill_ellipse(c, 31, 17, 6, 6, body, base=0.44)          # cabeza
    for i in range(4):                                        # pico
        c.set(37 + i, 17 + i // 2, color("ash_800"))
        c.set(37 + i, 18 + i // 2, color("ash_800"))
    c.set(32, 16, color("ash_950"))                           # ojo
    c.set(33, 16, color("ash_950"))
    for i in range(8):                                        # cola
        for w in range(3):
            c.set(13 - i, 30 + i // 2 + w, color("ash_600"))
    for x in range(20, 30, 3):                                # patas
        c.set(x, 37, color("ash_800"))
        c.set(x, 38, color("ash_800"))
    if mood == "arc":
        # Alas abiertas hacia arriba: la urgencia de una pista.
        for i in range(12):
            for w in range(3):
                c.set(14 + i, 20 - i // 2 - w, color("ash_400"))
                c.set(14 + i, 21 - i // 2, color("ash_700"))
    else:
        for i in range(10):
            c.set(17 + i, 27, color("ash_700"))
            c.set(17 + i, 28, color("ash_600"))
    return finish(c)


def bruma(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    cloak = ["ash_700", "ash_600", "ash_400", "ash_200"]
    shoulders(c, cloak)
    face(c, "sad" if mood == "arc" else "neutral")
    # Capucha calada: rodea la cara y cae sobre los hombros.
    for y in range(4, 36):
        for x in range(4, 44):
            d_out = math.hypot((x - CX) / 15.0, (y - 22.0) / 18.0)
            d_in = math.hypot((x - CX) / 8.6, (y - 22.5) / 10.0)
            if d_out <= 1.0 and d_in > 1.0:
                c.set(x, y, ramp(cloak, 0.30 + (0.16 if x < CX and y < 20 else 0)))
    return finish(c)


def coral(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    hair = ["ash_800", "ash_700", "ash_600"]
    shoulders(c, ["ash_600", "ash_400", "ash_200", "ash_050"])
    face(c, "laugh" if mood == "arc" else "neutral")
    fill_ellipse(c, CX, 14.5, 10.0, 6.0, hair, base=0.38)
    # Trenza que cae por el hombro derecho.
    for i in range(20):
        y = 20 + i
        x = 33 + (i // 6)
        w = 2 if i % 3 != 0 else 1
        for dx in range(-w, w + 1):
            c.set(x + dx, y, ramp(hair, 0.30 + (i % 3) * 0.14))
    return finish(c)


def nix(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    shoulders(c, ["ash_700", "ash_600", "ash_400", "ash_200"])
    face(c, "focus" if mood == "arc" else "neutral")
    hair = ["ash_800", "ash_700", "ash_600"]
    fill_ellipse(c, CX, 13.5, 9.6, 5.0, hair, base=0.36)
    # Pelo revuelto en punta: lo que separa su silueta de la de Ilan.
    for tip_x, tip_y in ((15, 3), (20, 1), (25, 2), (30, 4)):
        for y in range(tip_y, 12):
            half = (y - tip_y) // 3
            for x in range(tip_x - half, tip_x + half + 1):
                c.set(x, y, ramp(hair, 0.30 + (0.20 if x < CX else 0)))
    # Gafas de taller, más anchas que la cabeza: en la frente (neutral) o
    # puestas (concentrado).
    gy = EYE_Y if mood == "arc" else 13
    for x in range(9, 39):
        c.set(x, gy, color("ash_800"))                      # correa
    for side in (-1, 1):
        ex = int(CX) + side * (EYE_DX + 2)
        for dy in range(-2, 3):
            for dx in range(-3, 5):
                edge = abs(dy) == 2 or dx in (-3, 4)
                c.set(ex + dx, gy + dy, color("ash_800" if edge else "ash_200"))
    return finish(c)


def suri(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    hat = ["ash_700", "ash_600", "ash_400", "ash_200"]
    shoulders(c, ["ash_600", "ash_400", "ash_200", "ash_050"])
    face(c, "frown" if mood == "arc" else "neutral")
    # Ala ancha, la silueta más ancha por arriba, y la copa.
    fill_ellipse(c, CX, 13.0, 22.0, 3.6, hat, base=0.30)
    fill_ellipse(c, CX, 8.5, 9.0, 5.0, hat, base=0.44)
    return finish(c)


def rasgo(mood: str) -> Canvas:
    c = Canvas(SIZE, SIZE)
    coat = ["ash_800", "ash_700", "ash_600", "ash_400"]
    shoulders(c, coat)
    face(c, "doubt" if mood == "arc" else "frown")
    # Cuello alto militar y hombreras.
    for y in range(31, 38):
        for x in range(int(CX) - 7, int(CX) + 9):
            if abs(x - CX) > 3:
                c.set(x, y, color("ash_800"))
    for side in (-1, 1):
        for x in range(10):
            c.set(int(CX) + side * (13 + x // 2), 39, color("ash_200"))
            c.set(int(CX) + side * (13 + x // 2), 40, color("ash_400"))
    # Gorra de plato con visera.
    fill_ellipse(c, CX, 11.0, 11.0, 4.6, coat, base=0.36)
    for x in range(12, 37):
        c.set(x, 15, color("ash_950"))
        c.set(x, 16, color("ash_800"))
    # Cicatriz en la mejilla: la marca de los años de soldado.
    for i in range(4):
        c.set(int(CX) + 6 + (i // 2), 23 + i, color("ash_600"))
    return finish(c)


VOICES = {"ilan": ilan, "yara": yara, "bruma": bruma, "coral": coral, "nix": nix,
          "suri": suri, "rasgo": rasgo}
MOODS = {"ilan": ("neutral", "determinado"), "yara": ("neutral", "alerta"),
         "bruma": ("neutral", "dolida"), "coral": ("neutral", "risa"),
         "nix": ("neutral", "concentrado"), "suri": ("neutral", "firme"),
         "rasgo": ("neutral", "duda")}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for voice, draw in VOICES.items():
        neutral, arc = MOODS[voice]
        draw("neutral").save(OUT / f"{voice}_{neutral}.png")
        draw("arc").save(OUT / f"{voice}_{arc}.png")
        n += 2
    print(f"  retratos: {n} en {OUT.relative_to(OUT.parents[2])}")


if __name__ == "__main__":
    main()
