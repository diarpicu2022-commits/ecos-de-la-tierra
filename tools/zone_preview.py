"""Vista previa de una zona en texto, compuesta con el atlas real del terreno.

Sirve para revisar el paso 1 de cada zona (contrato «Rastro»: mapa en texto)
sin abrir el motor. Repite la regla de `src/world/world_tiles.gd` —máscara de
vecinos, fila del atlas por material, variante de suelo por celda— y por eso
sale el mismo terreno que pinta `WorldTiles.paint`. **Solo pinta materiales**:
el decorado, el hito y las entidades no tienen sprite hasta el paso 2. La
captura del motor (paso 3) sigue siendo la que vale para el contrato.

    python tools/zone_preview.py <zona> <png> [--purified all|none|<parte>,...]

Por defecto, en Valdehoja se pinta purificado solo el jardín de Yara (el
estado al empezar la partida) y, en el resto de zonas, nada.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TILE = 16
ATLAS = ROOT / "assets" / "tilesets" / "world.png"
ZONES = ROOT / "data" / "world" / "zones"
NAMES = ROOT / "data" / "world" / "zones.json"

# Mismo orden y mismas filas que WorldTiles.
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
SOIL_VARIANTS = 4
LEGEND = {".": "soil", "=": "path", "~": "water", "#": "flora"}
OVERLAY_ROW = {"path": 1, "water": 3, "flora": 5}


def load_zone(zone_id: str) -> list[str]:
    text = (ZONES / f"{zone_id}.txt").read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def load_parts(zone_id: str) -> dict[str, list[tuple[int, int, int, int]]]:
    data = json.loads(NAMES.read_text(encoding="utf-8"))
    raw = data["zones"].get(zone_id, {}).get("parts", {})
    return {k: [tuple(r) for r in v] for k, v in raw.items()}


def soil_variant(x: int, y: int) -> int:
    h = (x * 73856093) ^ (y * 19349663)
    return abs(h) % SOIL_VARIANTS


def neighbor_mask(grid: list[list[str]], x: int, y: int) -> int:
    material = grid[y][x]
    mask = 0
    for dx, dy, bit in ((0, -1, NORTH), (1, 0, EAST), (0, 1, SOUTH), (-1, 0, WEST)):
        nx, ny = x + dx, y + dy
        if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[ny]):
            mask |= bit
        elif grid[ny][nx] == material:
            mask |= bit
    return mask


def atlas_coords(material: str, purified: bool, mask: int, x: int, y: int) -> tuple[int, int]:
    if material == "soil":
        return soil_variant(x, y) + (SOIL_VARIANTS if purified else 0), 0
    return mask, OVERLAY_ROW[material] + (1 if purified else 0)


def render(zone_id: str, purified_parts: set[str]) -> Image.Image:
    lines = load_zone(zone_id)
    grid = [[LEGEND.get(ch, "soil") for ch in line] for line in lines]
    rects = [r for part, rs in load_parts(zone_id).items() if part in purified_parts for r in rs]

    def purified(x: int, y: int) -> bool:
        return any(rx <= x < rx + rw and ry <= y < ry + rh for rx, ry, rw, rh in rects)

    atlas = Image.open(ATLAS).convert("RGBA")
    out = Image.new("RGBA", (len(grid[0]) * TILE, len(grid) * TILE))
    for y, row in enumerate(grid):
        for x, material in enumerate(row):
            ax, ay = atlas_coords(material, purified(x, y), neighbor_mask(grid, x, y), x, y)
            tile = atlas.crop((ax * TILE, ay * TILE, (ax + 1) * TILE, (ay + 1) * TILE))
            out.paste(tile, (x * TILE, y * TILE))
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    zone_id, png = sys.argv[1], Path(sys.argv[2])
    parts = set(load_parts(zone_id))
    chosen = {"yara_garden"} & parts
    if "--purified" in sys.argv:
        value = sys.argv[sys.argv.index("--purified") + 1]
        chosen = parts if value == "all" else set() if value == "none" else set(value.split(","))
    render(zone_id, chosen).save(png)
    print(f"{png}: {zone_id}, purificado: {', '.join(sorted(chosen)) or 'nada'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
