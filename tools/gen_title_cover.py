"""La portada del título: Valdehoja que sana de izquierda a derecha.

    python tools/gen_title_cover.py

Toma la idea del componente `Cover` del sistema (losetas que pasan de ceniza a
verde por tramado ordenado 4 × 4, «el mapa que vuelve a ser verde, el mecanismo
del juego») y la hace con arte real: cada loseta de 16 px sale del render
enfermo o del sano de Valdehoja, en el mismo sitio, a un lado u otro de un
frente tramado, como el de la ola. Nunca se mezclan píxeles: cada uno es el de un estado o el
del otro, como en la ola de purificación.

Lee `docs/ux/capturas/nada-viejo/despues-valdehoja-{enfermo,sano}-mapa.png`
(Valdehoja entera a 1 ×) y escribe `assets/ui/portada.png` de 320 × 360.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "ux" / "capturas" / "nada-viejo"
OUT = ROOT / "assets" / "ui" / "portada.png"
# La plaza del Árbol del Vínculo con sus puestos y las casas de alrededor.
CROP = (480, 80, 800, 440)
TILE = 16
## Columna donde empieza el frente y su ancho, en losetas.
FRONT_AT = 9
FRONT = 4
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def main() -> int:
    sick = Image.open(SRC / "despues-valdehoja-enfermo-mapa.png").convert("RGB").crop(CROP)
    pure = Image.open(SRC / "despues-valdehoja-sano-mapa.png").convert("RGB").crop(CROP)
    w, h = sick.size
    out = sick.copy()
    cols, rows = w // TILE, h // TILE
    for r in range(rows):
        for c in range(cols):
            # Un frente como el de la ola: enfermo a la izquierda, sano a la
            # derecha y una franja tramada de FRONT columnas en medio, un poco
            # inclinada para que no parezca una costura.
            x = c - (FRONT_AT - r // 4)
            level = 16.0 * (x + 1) / (FRONT + 1)
            if BAYER[r % 4][c % 4] < level:
                box = (c * TILE, r * TILE, (c + 1) * TILE, (r + 1) * TILE)
                out.paste(pure.crop(box), box)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(f"  {OUT.relative_to(ROOT)}: {w}×{h}, {cols}×{rows} losetas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
