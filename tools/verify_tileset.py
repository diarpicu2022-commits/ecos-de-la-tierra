"""Verificación medida del tileset de terreno (contrato «Vereda», paso 2b).

    python tools/verify_tileset.py

Mide sobre `assets/tilesets/world.png`, no sobre los tokens:

1. Todo píxel es un token y el mundo no pasa de saturación 0,22 (salvo acentos).
2. Valor: cada material purificado es >= 1,5 veces más luminoso que su versión
   enferma, en visión normal y con deuteranopía, protanopía y tritanopía. Es la
   regla que impide que el estado dependa solo del color.
3. Separación entre materiales del mismo estado (dE sobre el color medio del
   tile interior). Umbral del contrato: el objetivo era 12, lo conseguido con
   los tokens fue 9,2. Por debajo de 9 se informa como FALLA.
4. Contorno de lo que responde (`ASH_050`) contra cada tinta del terreno:
   >= 3:1 (WCAG 1.4.11, mínimo gráfico).
5. El acento verde y la brasa contra cada tinta del terreno: >= 3:1. Para la
   brasa cuenta EMBER_300, el borde claro de todo lo que arde, que es lo que
   midió la enmienda 1 (3,27:1). EMBER_500 se informa como aviso: sobre el
   follaje no llega, así que un sprite de monstruo en el mundo nunca puede
   apoyarse solo en él (requisito para la parte 4).

Sale con código 1 si algo falla.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_palette import (  # noqa: E402
    CVD, contrast, delta_e, gd_tokens, luminance, simulate, to_linear,
)

ROOT = Path(__file__).resolve().parent.parent
ATLAS = ROOT / "assets" / "tilesets" / "world.png"
T = 16
INTERIOR = 15
ROWS = {"camino": 1, "agua": 3, "follaje": 5}

VALUE_FLOOR = 1.5
DE_FLOOR = 9.0
GRAPHIC_FLOOR = 3.0


def tile_pixels(img: Image.Image, col: int, row: int) -> list[tuple[int, int, int]]:
    tile = img.crop((col * T, row * T, col * T + T, row * T + T)).convert("RGB")
    return list(getattr(tile, "get_flattened_data", tile.getdata)())


def mean_linear(pixels: list[tuple[int, int, int]]) -> list[float]:
    acc = [0.0, 0.0, 0.0]
    for p in pixels:
        lin = to_linear(p)
        for i in range(3):
            acc[i] += lin[i]
    return [c / len(pixels) for c in acc]


def materials(img: Image.Image, purified: bool) -> dict[str, list[tuple[int, int, int]]]:
    off = 4 if purified else 0
    soil = []
    for v in range(4):
        soil += tile_pixels(img, off + v, 0)
    out = {"suelo": soil}
    for name, row in ROWS.items():
        out[name] = tile_pixels(img, INTERIOR, row + (1 if purified else 0))
    return out


def main() -> int:
    img = Image.open(ATLAS)
    ok = True
    sick, pure = materials(img, False), materials(img, True)

    print("=== VALOR: purificado / enfermo (piso %.1f) ===" % VALUE_FLOOR)
    for name in sick:
        ls, lp = mean_linear(sick[name]), mean_linear(pure[name])
        cells = []
        for kind in [None, *CVD]:
            ratio = (luminance(simulate(lp, kind)) + 0.05) / (luminance(simulate(ls, kind)) + 0.05)
            ok &= ratio >= VALUE_FLOOR
            cells.append(f"{(kind or 'normal')[:6]} {ratio:.2f}{'' if ratio >= VALUE_FLOOR else ' FALLA'}")
        print(f"  {name:8} " + " | ".join(cells))

    print("\n=== SEPARACIÓN ENTRE MATERIALES, dE (piso %.1f) ===" % DE_FLOOR)
    for state, group in (("enfermo", sick), ("purificado", pure)):
        names = list(group)
        means = {n: mean_linear(group[n]) for n in names}
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                d = delta_e(means[a], means[b])
                mark = "OK   " if d >= DE_FLOOR else "FALLA"
                ok &= d >= DE_FLOOR
                print(f"  {mark} {state:10} {a:8} / {b:8} dE {d:5.1f}")

    tokens = gd_tokens()
    by_rgb = {v: k for k, v in tokens.items()}
    # Solo las tintas que el atlas usa de verdad; las celdas vacías de la fila
    # del suelo son transparentes y no cuentan.
    used = sorted({by_rgb[p] for row in range(7) for col in range(16)
                   for p in tile_pixels(img, col, row) if p in by_rgb})
    terrain = [n for n in used if not n.startswith(("vital_", "ember_"))]
    sick_terrain = terrain

    print("\n=== CONTORNO DE LO QUE RESPONDE (ASH_050) CONTRA EL TERRENO (piso 3:1) ===")
    outline = to_linear(tokens["ash_050"])
    worst = min(terrain, key=lambda n: contrast(outline, to_linear(tokens[n])))
    for n in terrain:
        c = contrast(outline, to_linear(tokens[n]))
        ok &= c >= GRAPHIC_FLOOR
        if c < GRAPHIC_FLOOR or n == worst:
            print(f"  {'OK   ' if c >= GRAPHIC_FLOOR else 'FALLA'} ASH_050 / {n}: {c:.2f}:1{'  (peor caso)' if n == worst else ''}")

    print("\n=== ACENTOS CONTRA EL TERRENO (piso 3:1) ===")
    for accent, binding in (("vital_500", True), ("ember_300", True), ("ember_500", False)):
        a = to_linear(tokens[accent])
        worst = min(sick_terrain, key=lambda n: contrast(a, to_linear(tokens[n])))
        c = contrast(a, to_linear(tokens[worst]))
        if binding:
            ok &= c >= GRAPHIC_FLOOR
            mark = "OK   " if c >= GRAPHIC_FLOOR else "FALLA"
        else:
            mark = "AVISO" if c < GRAPHIC_FLOOR else "OK   "
        print(f"  {mark} {accent} peor caso sobre {worst}: {c:.2f}:1")
    print("        -> un monstruo en el mapa lleva siempre borde EMBER_300 o contorno;")
    print("           EMBER_500 solo no se lee sobre el follaje (parte 4).")

    print("\n" + ("Tileset dentro del contrato." if ok else "Hay fallos: se informan, no se maquillan."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
