"""Hojas de personaje «Tierra Viva» (sistema de diseño, componente `Cast`).

    python tools/gen_tierra_viva_cast.py

Saca de los originales de PixelLab (`assets/source/pixellab/<nombre>/`) la
hoja que usa el mapa, en `assets/sprites/world/cast/<nombre>.png`:

- celdas de 48 × 48 (el lienzo del sistema), con los pies en la última fila;
- cuatro filas, en el orden de `PlayerBody`: abajo, arriba, izquierda,
  derecha;
- cinco columnas: de pie (la rotación de PixelLab) y los cuatro cuadros de la
  caminata (`walk_<dir>.gif`, «caminata de 4 cuadros»). Quien no trae
  caminata repite la rotación de pie, y se avisa.

Para el combate (referencias `combate_enfermo.png` y `combate_purificado.png`):

- el grupo de espaldas, la rotación norte-este al doble de escala
  (`battle-back: 96px`), en `assets/sprites/party/tierra_viva/<nombre>_back.png`;
- los seis monstruos en sus dos formas, recortados a su silueta, en
  `assets/sprites/monsters/tierra_viva/<clave>{,_purified}.png`, con la clave
  del script del monstruo, que es como los busca `MonsterView`.

No se repinta ni se recolorea nada: cada píxel es del original. Se mide con
`verify_palette.py image <hoja> --source assets/source/pixellab/<nombre>`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "pixellab"
OUT = ROOT / "assets" / "sprites" / "world" / "cast"
CELL = 48
## Filas de la hoja, en el orden de PlayerBody.ROW_*.
ROWS = ["south", "north", "west", "east"]
WALK_FRAMES = 4
## Los GIF de caminata vienen en lienzo de 80 × 80 con los pies en la fila 62
## o 63: este recorte los deja en la 46 o 47 de la celda, como la rotación.
WALK_CROP = (16, 16, 64, 64)
CAST = ["ilan", "bruma", "coral", "nix", "suri"]
## Monstruo de historia de cada región (componente `MonsterRoster`). En el
## mapa va a su tamaño de PixelLab, recortado a su silueta, como en la maqueta
## del sistema `referencias/combate_accion.png`; mira abajo a la izquierda.
MONSTERS = {"ashen_forest": "llama", "tar_basin": "devorador", "broken_coast": "golem",
            "withered_plain": "espectro", "waning_peak": "coloso", "greed_crypt": "sombra"}
## Clave del script de cada monstruo (`src/actors/monsters/<clave>.gd`).
BATTLE_KEY = {"llama": "deforestation_flame", "devorador": "oil_devourer", "golem": "plastic_golem",
              "espectro": "monoculture_specter", "coloso": "thaw_colossus", "sombra": "adaptive_boss"}
BATTLE_PARTY = ROOT / "assets" / "sprites" / "party" / "tierra_viva"
BATTLE_MONSTERS = ROOT / "assets" / "sprites" / "monsters" / "tierra_viva"


def sheet(name: str) -> Image.Image:
    out = Image.new("RGBA", (CELL * (1 + WALK_FRAMES), CELL * len(ROWS)), (0, 0, 0, 0))
    for row, d in enumerate(ROWS):
        stand = Image.open(SRC / name / f"{d}.png").convert("RGBA")
        assert stand.size == (CELL, CELL), f"{name}/{d}.png mide {stand.size}"
        out.paste(stand, (0, row * CELL))
        gif = SRC / name / f"walk_{d}.gif"
        frames = []
        if gif.exists():
            frames = [f.convert("RGBA").crop(WALK_CROP) for f in ImageSequence.Iterator(Image.open(gif))]
        if len(frames) != WALK_FRAMES:
            print(f"  AVISO {name}: sin caminata «{d}» de {WALK_FRAMES} cuadros; repite la de pie")
            frames = [stand] * WALK_FRAMES
        for k, f in enumerate(frames):
            out.paste(f, ((1 + k) * CELL, row * CELL))
    return out


def trimmed(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    return im.crop(im.getbbox())


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in argv or CAST:
        path = OUT / f"{name}.png"
        sheet(name).save(path)
        print(f"  {path.relative_to(ROOT)}")
    if not argv:
        for zone, name in MONSTERS.items():
            for state, form in (("sick", "corrupto"), ("pure", "purificado")):
                path = OUT / f"monster_{zone}_{state}.png"
                im = trimmed(SRC / "monsters" / f"{name}_{form}.png")
                im.save(path)
                print(f"  {path.relative_to(ROOT)}: {im.width}×{im.height}")
        BATTLE_PARTY.mkdir(parents=True, exist_ok=True)
        for name in CAST:
            back = trimmed(SRC / name / "north-east.png")
            back = back.resize((back.width * 2, back.height * 2), Image.NEAREST)
            path = BATTLE_PARTY / f"{name}_back.png"
            back.save(path)
            print(f"  {path.relative_to(ROOT)}: {back.width}×{back.height}")
        BATTLE_MONSTERS.mkdir(parents=True, exist_ok=True)
        for name, key in BATTLE_KEY.items():
            for suffix, form in (("", "corrupto"), ("_purified", "purificado")):
                path = BATTLE_MONSTERS / f"{key}{suffix}.png"
                trimmed(SRC / "monsters" / f"{name}_{form}.png").save(path)
                print(f"  {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
