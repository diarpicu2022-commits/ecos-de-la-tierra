"""Recortes para la prueba con personas de los materiales (paso 2b de «Vereda»).

    python tools/material_crops.py <enfermo.png> <purificado.png> <carpeta_salida>

Corta diez recortes de 64x64 de las capturas de `tools/tileset_sheet.tscn`
(480x270, el medio de salida real) y los guarda escalados 4x con filtro
`Nearest`, en orden barajado con semilla fija. Cada recorte está centrado en
un tile: la pregunta a la persona es «¿de qué material es el centro?».

La clave de respuestas se imprime por consola y **no** se guarda junto a los
recortes, para que quien hace la prueba no la vea.

Criterio (enmienda 1 del anexo de exploración): tres personas nombran el
material de los diez recortes sin error, o la separación dE 9,2 no basta.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image

T = 16
CROP = 64
SCALE = 4
SEED = 29

# (material, estado, columna, fila) del tile central, sobre el mapa de
# `tools/tileset_sheet.gd`. Cinco enfermos y cinco purificados; los cuatro
# materiales en los dos estados.
CASES = [
    ("follaje", "enfermo", 1, 1),
    ("agua", "enfermo", 17, 6),
    ("suelo", "enfermo", 10, 7),
    ("camino", "enfermo", 12, 10),
    ("follaje", "enfermo", 5, 10),
    ("suelo", "purificado", 4, 6),
    ("agua", "purificado", 21, 11),
    ("follaje", "purificado", 26, 1),
    ("camino", "purificado", 26, 7),
    ("suelo", "purificado", 23, 7),
]


def crop_box(col: int, row: int, width: int, height: int) -> tuple[int, int, int, int]:
    """Caja de 64x64 centrada en el tile, desplazada para no salir de la captura."""
    cx, cy = col * T + T // 2, row * T + T // 2
    x = min(max(cx - CROP // 2, 0), width - CROP)
    y = min(max(cy - CROP // 2, 0), height - CROP)
    return x, y, x + CROP, y + CROP


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    sources = {"enfermo": Image.open(sys.argv[1]).convert("RGB"),
               "purificado": Image.open(sys.argv[2]).convert("RGB")}
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)

    order = list(CASES)
    random.Random(SEED).shuffle(order)
    print("Clave (no enseñar a quien hace la prueba):")
    for i, (material, state, col, row) in enumerate(order, 1):
        img = sources[state]
        tile = img.crop(crop_box(col, row, img.width, img.height))
        tile = tile.resize((CROP * SCALE, CROP * SCALE), Image.NEAREST)
        tile.save(out / f"recorte-{i:02d}.png")
        print(f"  {i:2d}  {material:8} {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
