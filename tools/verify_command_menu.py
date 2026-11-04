"""Comprobación del `CommandMenu` y de los submenús sobre el render, no sobre los
tokens (guía del equipo §3.1, fila 9).

    python tools/verify_command_menu.py raiz <png> <foco 0..3>
        Mide en una captura de 640 x 360 con ese mando elegido:
        - posición y tamaño de cada mando, encontrados por los colores de su marco;
        - contraste real de cada etiqueta contra su botón (piso 5,9:1);
        - etiqueta centrada y dentro del botón;
        - anillo solo en el elegido, dentro del viewport y sin pisar el aviso.

    python tools/verify_command_menu.py lista <png>
        Mide un submenú: la placa en `MENU_RECT`, el texto dentro de su alto útil
        y el contraste de cada tono contra lo que tiene alrededor (piso AA, 4,5:1).

    python tools/verify_command_menu.py referencia <png con foco 1>
        Compara píxel a píxel los mandos y el anillo con `combate_enfermo.png`.
        Separa dos diferencias que ya están en el sistema: esa imagen pinta la
        sombra de la etiqueta y, en LUCHAR y HUIR, la fila 27 del canto con el tono
        0 de la rampa, y ni el CSS (sombra `ink-1`) ni `cmd-*.png` lo hacen así.

Sale con código 1 si algo falla.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOKENS_GD = ROOT / "src" / "ui" / "design_tokens.gd"
FRAMES = ROOT / "assets" / "ui" / "marcos"
REFERENCE = ROOT / "docs/ux/sistema-de-diseno/project/assets/img/combate_enfermo.png"

SCREEN = (640, 360)
MENU = (432, 284, 204, 66)
MESSAGE = (6, 282, 420, 72)
LABEL_FLOOR = 5.9
AA_FLOOR = 4.5
RING = 2
## Lo que ocupa el canto de la placa, medido sobre `plate.png`.
PLATE_EDGE_TOP, PLATE_EDGE_BOTTOM, PLATE_EDGE_SIDE = 3, 2, 2

BUTTONS = [
    ("LUCHAR", "cmd-luchar", 432, 284),
    ("ECO", "cmd-eco", 536, 284),
    ("BOLSA", "cmd-bolsa", 432, 320),
    ("HUIR", "cmd-huir", 536, 320),
]
W, H = 100, 30

failures = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global failures
    failures += 0 if ok else 1
    print(f"  {'OK   ' if ok else 'FALLA'} {label} {detail}".rstrip())


def token(name: str) -> tuple[int, int, int]:
    """Valor de un token en `design_tokens.gd`, siguiendo un alias si lo es."""
    text = TOKENS_GD.read_text(encoding="utf-8")
    match = re.search(rf'^const {name} := (?:Color\("#([0-9a-f]{{6}})"\)|(\w+))', text, re.M)
    if match is None:
        raise SystemExit(f"No existe el token {name}")
    if match.group(2):
        return token(match.group(2))
    value = match.group(1)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def load(path: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    check("la captura mide 640 x 360", image.size == SCREEN, f"({image.size[0]} x {image.size[1]})")
    return image


def frame_colors(name: str) -> set[tuple[int, int, int]]:
    """Colores propios de un marco, sin la tinta de su canto, que es común a todos."""
    frame = Image.open(FRAMES / f"{name}.png").convert("RGBA")
    ink = token("TV_INK_0")
    pixels = (frame.getpixel((x, y)) for y in range(frame.height) for x in range(frame.width))
    return {p[:3] for p in pixels if p[3] == 255 and p[:3] != ink}


def find_button(image: Image.Image, colors: set) -> tuple[int, int, int, int] | None:
    """Caja del botón: la de sus colores más el canto de 1 px en tinta."""
    xs, ys = [], []
    for y in range(MENU[1] - 6, SCREEN[1]):
        for x in range(MESSAGE[0] + MESSAGE[2], SCREEN[0]):
            if image.getpixel((x, y)) in colors:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs) - 1, min(ys) - 1, max(xs) - min(xs) + 3, max(ys) - min(ys) + 3


def root(path: str, focus: int) -> None:
    image = load(path)
    white = token("TV_TEXT_ON_SLATE")
    ink = token("TV_INK_0")
    print(f"\n{Path(path).name}, foco en {BUTTONS[focus][0]}")
    for i, (name, frame, x, y) in enumerate(BUTTONS):
        box = find_button(image, frame_colors(frame))
        check(f"{name}: posición y tamaño", box == (x, y, W, H), f"(medido {box}, pedido {(x, y, W, H)})")
        if box is None:
            continue
        # Etiqueta: sus píxeles blancos, sin el borde del botón.
        text = [(px, py) for py in range(y + 1, y + H - 1) for px in range(x + 1, x + W - 1)
                if image.getpixel((px, py)) == white]
        check(f"{name}: hay etiqueta", bool(text))
        if not text:
            continue
        counts = Counter(image.getpixel((px, py)) for py in range(y + 2, y + H - 2)
                         for px in range(x + 2, x + W - 2))
        counts.pop(white, None)
        counts.pop(ink, None)
        background = counts.most_common(1)[0][0]
        ratio = contrast(white, background)
        check(f"{name}: contraste de la etiqueta contra el botón", ratio >= LABEL_FLOOR,
              f"({ratio:.2f}:1, #{background[0]:02x}{background[1]:02x}{background[2]:02x}, piso {LABEL_FLOOR})")
        xs = [p[0] for p in text]
        ys = [p[1] for p in text]
        left, right = min(xs) - x, x + W - 1 - max(xs)
        check(f"{name}: etiqueta centrada", abs(left - right) <= 2, f"({left} px a la izquierda, {right} a la derecha)")
        check(f"{name}: etiqueta dentro del botón",
              min(xs) >= x + 3 and max(xs) + 1 <= x + W - 3 and min(ys) >= y + 3 and max(ys) + 1 <= y + H - 3,
              f"(x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)})")

        # Anillo: el píxel blanco al otro lado del canto del botón, en los cuatro lados.
        mid_x, mid_y = x + W // 2, y + H // 2
        sides = [(mid_x, y - 1), (mid_x, y + H), (x - 1, mid_y), (x + W, mid_y)]
        ring = [image.getpixel(p) == white for p in sides]
        if i == focus:
            check(f"{name}: lleva el anillo por los cuatro lados", all(ring))
            outer = (x - RING, y - RING, W + RING * 2, H + RING * 2)
            for p in [(mid_x, y - RING), (mid_x, y + H + RING - 1), (x - RING, mid_y), (x + W + RING - 1, mid_y)]:
                if image.getpixel(p) != ink:
                    check(f"{name}: canto exterior del anillo en tinta", False, f"({p})")
            inside = outer[0] >= 0 and outer[1] >= 0 and outer[0] + outer[2] <= SCREEN[0] and outer[1] + outer[3] <= SCREEN[1]
            check(f"{name}: el anillo no se sale del viewport", inside,
                  f"(x {outer[0]}..{outer[0] + outer[2]}, y {outer[1]}..{outer[1] + outer[3]})")
            check(f"{name}: el anillo no pisa MESSAGE_RECT", outer[0] >= MESSAGE[0] + MESSAGE[2],
                  f"(empieza en x {outer[0]}, el aviso acaba en x {MESSAGE[0] + MESSAGE[2]})")
        else:
            check(f"{name}: sin anillo", not any(ring))

    # Lo que dice el aviso: tono de `_paper_tone` contra el papel y sin salirse.
    tone, paper = token("TV_PAPER_0"), token("TV_PAPER_4")
    lines = [(px, py) for py in range(MESSAGE[1], MESSAGE[1] + MESSAGE[3])
             for px in range(MESSAGE[0], MESSAGE[0] + MESSAGE[2]) if image.getpixel((px, py)) == tone]
    if lines:
        ys = [p[1] for p in lines]
        rows = sorted(set(ys))
        count = 1 + sum(1 for a, b in zip(rows, rows[1:]) if b - a > 3)
        ratio = contrast(tone, paper)
        check("aviso: contraste contra el papel", ratio >= AA_FLOOR, f"({ratio:.2f}:1)")
        check("aviso: el texto no se sale del papel", max(ys) < MESSAGE[1] + MESSAGE[3] - 3,
              f"({count} líneas, y {min(ys)}..{max(ys)}, el papel acaba en y {MESSAGE[1] + MESSAGE[3]})")

    # El aviso de verdad: su marco de madera en el render, no en la constante.
    edge = token("TV_PAPER_EDGE")
    paper_x = [x for y in range(MESSAGE[1], MESSAGE[1] + MESSAGE[3]) for x in range(SCREEN[0])
               if image.getpixel((x, y)) == edge]
    if paper_x:
        check("el aviso acaba antes de que empiece el menú", max(paper_x) + 1 <= MENU[0] - RING,
              f"(último píxel del marco en x {max(paper_x)}, el menú con anillo empieza en x {MENU[0] - RING})")


def text_contrast(image: Image.Image, tone: tuple[int, int, int],
                  box: tuple[int, int, int, int]) -> dict[tuple[int, int, int], int]:
    """Vecinos reales de un tono de texto: color -> cuántos píxeles lo tocan."""
    x0, y0, x1, y1 = box
    neighbours: Counter = Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if image.getpixel((x, y)) != tone:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                neighbour = image.getpixel((nx, ny))
                if neighbour != tone:
                    neighbours[neighbour] += 1
    return neighbours


def listing(path: str) -> None:
    image = load(path)
    print(f"\n{Path(path).name}, submenú")
    x, y, w, h = MENU
    ink = token("TV_INK_0")
    fill = token("TV_UI_1")
    check("placa en MENU_RECT",
          all(image.getpixel(p) == ink for p in [(x + w // 2, y), (x + w // 2, y + h - 1), (x, y + h // 2), (x + w - 1, y + h // 2)])
          and image.getpixel((x + w // 2, y - 1)) != ink and image.getpixel((x - 1, y + h // 2)) != ink,
          f"({x}, {y}, {w} x {h})")
    inner = (x + PLATE_EDGE_SIDE, y + PLATE_EDGE_TOP, x + w - PLATE_EDGE_SIDE, y + h - PLATE_EDGE_BOTTOM)
    tones = {
        "texto de pizarra": token("TV_TEXT_ON_SLATE"),
        "enfocado": token("TV_TEXT_HIGHLIGHT"),
        "coste que alcanza": token("TV_TEXT_MUTED_SLATE"),
        "coste que no alcanza": token("TV_RUST_4"),
    }
    text_tones = set(tones.values())
    found = []
    for label, tone in tones.items():
        # El borde de la placa no cuenta como vecino del texto: se mide dentro.
        neighbours = text_contrast(image, tone, inner)
        if not neighbours:
            continue
        found.append(tone)
        for neighbour, count in neighbours.most_common():
            if neighbour in text_tones:
                continue
            ratio = contrast(tone, neighbour)
            check(f"{label} contra #{neighbour[0]:02x}{neighbour[1]:02x}{neighbour[2]:02x}", ratio >= AA_FLOOR,
                  f"({ratio:.2f}:1, {count} contactos, piso {AA_FLOOR})")
    pixels = [(px, py) for py in range(y + h) for px in range(x - 8, min(x + w + 8, SCREEN[0]))
              if py >= y - 8 and image.getpixel((px, py)) in found]
    if pixels:
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        check("el texto queda dentro del alto y el ancho útiles",
              min(xs) >= inner[0] and max(xs) < inner[2] and min(ys) >= inner[1] and max(ys) < inner[3],
              f"(x {min(xs)}..{max(xs)} de {inner[0]}..{inner[2] - 1}, y {min(ys)}..{max(ys)} de {inner[1]}..{inner[3] - 1})")
    check("el fondo de la placa es pizarra", image.getpixel((x + w - 4, y + h - 4)) in (fill, token("TV_UI_0")))


def reference(path: str) -> None:
    image = load(path)
    ref = Image.open(REFERENCE).convert("RGB")
    print(f"\n{Path(path).name} contra {REFERENCE.name}")
    ink = token("TV_INK_0")
    for name, _frame, x, y in BUTTONS:
        total = same = shadow = edge = other = 0
        for py in range(y, y + H):
            for px in range(x, x + W):
                total += 1
                a, b = image.getpixel((px, py)), ref.getpixel((px, py))
                if a == b:
                    same += 1
                elif a == ink:
                    shadow += 1
                elif py - y == H - 3:
                    edge += 1
                else:
                    other += 1
        check(f"{name}: igual a la referencia", other == 0,
              f"({same} de {total} iguales; difieren {shadow} de sombra, {edge} de canto, {other} de otra cosa)")
    # Anillo de ECO, el elegido en la referencia.
    x, y = BUTTONS[1][2:]
    band = [(px, py) for py in range(y - RING, y + H + RING) for px in range(x - RING, x + W + RING)
            if not (x <= px < x + W and y <= py < y + H)]
    different = sum(image.getpixel(p) != ref.getpixel(p) and ref.getpixel(p) in (ink, token("TV_FOCUS_RING")) for p in band)
    check("anillo igual a la referencia", different == 0, f"({len(band)} píxeles, {different} distintos)")


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "raiz":
        root(args[1], int(args[2]))
    elif len(args) == 2 and args[0] == "lista":
        listing(args[1])
    elif len(args) == 2 and args[0] == "referencia":
        reference(args[1])
    else:
        raise SystemExit(__doc__)
    print(f"\n{'Todo en orden.' if failures == 0 else f'{failures} fallos.'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
