"""Vista previa de una zona en texto, compuesta con el atlas real del terreno.

Sirve para revisar el paso 1 de cada zona (contrato «Rastro»: mapa en texto)
sin abrir el motor. Repite la regla de `src/world/world_tiles.gd` —máscara de
vecinos, fila del atlas por material, variante de suelo por celda y borde
del prado— y por eso
sale el mismo terreno que pinta `WorldTiles.paint`. Encima pinta la capa de
decorado (`<zona>.deco.txt`) con los sprites de `tools/gen_world_decor.py`,
ordenados por altura y en el estado de la parte en la que caen. La fauna
silvestre solo se pinta donde está purificado (enmienda 7). La captura del
motor (paso 3) sigue siendo la que vale para el contrato.

    python tools/zone_preview.py <zona> <png> [--purified all|none|<parte>,...]
                                 [--crop x,y] [--terrain-only]

`--crop x,y` recorta la pantalla de 480x270 centrada en la casilla (x, y),
encerrada en la zona como la cámara, y pinta a Ilan en la aparición.

Por defecto, en Valdehoja se pinta purificado solo el jardín de Yara (el
estado al empezar la partida) y, en el resto de zonas, nada.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TILE = 16
ATLAS = ROOT / "assets" / "tilesets" / "world.png"
ZONES = ROOT / "data" / "world" / "zones"
DECOR = ROOT / "assets" / "sprites" / "world" / "decor"
ILAN = ROOT / "assets" / "sprites" / "world" / "ilan.png"
SCREEN = (480, 270)

# Sprite de cada id de la leyenda cuando no se llama igual.
SPRITE = {"person": "yara", "chicken": "chicken_0", "bird": "bird_0", "butterfly": "butterfly_0"}
ENTRY = re.compile(r"^; (\S) = (\w+), (\w+), (sólido|pisable)(?:, (\d+)x(\d+))?")

# Mismo orden y mismas filas que WorldTiles.
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
SOIL_VARIANTS = 4
LEGEND = {".": "soil", "=": "path", "~": "water", "#": "flora"}
OVERLAY_ROW = {"path": 1, "water": 3, "flora": 5}
MEADOW_EDGE_ROW = 7


def load_zone(zone_id: str) -> list[str]:
    text = (ZONES / f"{zone_id}.txt").read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def load_parts(zone_id: str) -> dict[str, set[tuple[int, int]]]:
    """Celdas de cada parte, de `<zona>.parts.txt` (como ZoneRules.load_parts)."""
    path = ZONES / f"{zone_id}.parts.txt"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").replace("\r", "").split("\n")
    split = lines.index("---")
    ids = {}
    for line in lines[:split]:
        m = re.match(r"^; (\S) = (\w+)", line)
        if m:
            ids[m[1]] = m[2]
    parts: dict[str, set[tuple[int, int]]] = {i: set() for i in ids.values()}
    for y, row in enumerate(lines[split + 1:]):
        for x, ch in enumerate(row):
            if ch in ids:
                parts[ids[ch]].add((x, y))
    return parts


def load_deco(zone_id: str) -> tuple[dict, list[str]]:
    path = ZONES / f"{zone_id}.deco.txt"
    if not path.exists():
        return {}, []
    lines = path.read_text(encoding="utf-8").replace("\r", "").split("\n")
    split = lines.index("---")
    legend = {}
    for line in lines[:split]:
        m = ENTRY.match(line)
        if m:
            size = (int(m[5]), int(m[6])) if m[5] else (1, 1)
            legend[m[1]] = {"kind": m[2], "id": m[3], "size": size}
    rows = lines[split + 1:]
    if rows and rows[-1] == "":
        rows = rows[:-1]
    return legend, rows


def pieces(legend: dict, rows: list[str]) -> list[tuple[str, int, int]]:
    """Cada pieza, por su esquina superior izquierda."""
    claimed: set[tuple[int, int]] = set()
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == " " or (x, y) in claimed or ch not in legend:
                continue
            w, h = legend[ch]["size"]
            claimed.update((x + i, y + j) for j in range(h) for i in range(w))
            out.append((ch, x, y))
    return out


def gd_hash_v2i(x: int, y: int) -> int:
    """Sustituto estable de `absi(hash(Vector2i))` de Godot para la vista
    previa. No da el mismo número que Godot: la vista previa desplaza los
    árboles igual de poco, pero no al mismo píxel que el motor."""
    return abs((x * 73856093) ^ (y * 19349663) ^ 0x5bd1e995)


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


def purified_mask(grid: list[list[str]], x: int, y: int, purified) -> int:
    """Qué vecinos están purificados; fuera del mapa cuenta como purificado."""
    mask = 0
    for dx, dy, bit in ((0, -1, NORTH), (1, 0, EAST), (0, 1, SOUTH), (-1, 0, WEST)):
        nx, ny = x + dx, y + dy
        if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[ny]) or purified(nx, ny):
            mask |= bit
    return mask


def atlas_coords(material: str, purified: bool, mask: int, x: int, y: int) -> tuple[int, int]:
    if material == "soil":
        return soil_variant(x, y) + (SOIL_VARIANTS if purified else 0), 0
    return mask, OVERLAY_ROW[material] + (1 if purified else 0)


def render(zone_id: str, purified_parts: set[str], terrain_only: bool = False,
           player_at: tuple[int, int] | None = None) -> Image.Image:
    lines = load_zone(zone_id)
    grid = [[LEGEND.get(ch, "soil") for ch in line] for line in lines]
    parts = load_parts(zone_id)
    cells = set().union(*[c for part, c in parts.items() if part in purified_parts])
    # Una zona sin partes se purifica entera: «all» la pinta purificada.
    whole = not parts and "all" in purified_parts

    def purified(x: int, y: int) -> bool:
        return whole or (x, y) in cells

    atlas = Image.open(ATLAS).convert("RGBA")
    out = Image.new("RGBA", (len(grid[0]) * TILE, len(grid) * TILE))
    for y, row in enumerate(grid):
        for x, material in enumerate(row):
            ax, ay = atlas_coords(material, purified(x, y), neighbor_mask(grid, x, y), x, y)
            if material == "soil" and purified(x, y):
                around = purified_mask(grid, x, y, purified)
                if around != 15:
                    ax, ay = around, MEADOW_EDGE_ROW
            tile = atlas.crop((ax * TILE, ay * TILE, (ax + 1) * TILE, (ay + 1) * TILE))
            out.paste(tile, (x * TILE, y * TILE))
    if terrain_only:
        return out
    legend, rows = load_deco(zone_id)
    sprites = []
    for ch, x, y in pieces(legend, rows):
        entry = legend[ch]
        w, h = entry["size"]
        if entry["kind"] == "spawn":
            if player_at is not None:
                sprites.append(((y + 1) * TILE, x * TILE, (y + 1) * TILE, Image.open(ILAN).crop((0, 0, 16, 24))))
            continue
        # El estado lo da el pie de la pieza: la casilla central de abajo.
        pure = purified(x + w // 2, y + h - 1)
        if entry["kind"] == "fauna" and not pure:
            continue
        if pure and entry["id"] in ("blocker", "monster"):
            continue
        name = SPRITE.get(entry["id"], entry["id"])
        name = re.sub(r"^v\d_", "", name)
        path = None
        for state in (("pure", "sick") if pure else ("sick", "pure")):
            for base in (f"{name}_{zone_id}", name):
                if path is None and (DECOR / f"{base}_{state}.png").exists():
                    path = DECOR / f"{base}_{state}.png"
        img = Image.open(path).convert("RGBA")
        bottom = (y + h) * TILE
        if img.width < TILE:
            # Lo pequeño (animales, fauna) se apoya en el centro de su tile.
            bottom -= (TILE - img.height) // 2
        left = x * TILE + (w * TILE - img.width) // 2
        if entry["id"] in ("tree", "tree_b", "burnt_tree"):
            # Como WorldDecor: unos píxeles por árbol, para romper la cuadrícula.
            hsh = gd_hash_v2i(x, y)
            left += (hsh % 7) - 3
            bottom += ((hsh // 7) % 3) - 1
        sprites.append((bottom, left, bottom, img))
    for _, left, bottom, img in sorted(sprites, key=lambda s: s[0]):
        out.alpha_composite(img, (left, bottom - img.height))
    return out


def crop_screen(img: Image.Image, cell: tuple[int, int]) -> Image.Image:
    """La pantalla de 480x270 centrada en `cell`, encerrada en la zona."""
    cx, cy = cell[0] * TILE + TILE // 2, cell[1] * TILE + TILE // 2
    x = max(0, min(cx - SCREEN[0] // 2, img.width - SCREEN[0]))
    y = max(0, min(cy - SCREEN[1] // 2, img.height - SCREEN[1]))
    return img.crop((x, y, x + SCREEN[0], y + SCREEN[1]))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    zone_id, png = sys.argv[1], Path(sys.argv[2])
    parts = set(load_parts(zone_id))
    chosen = {"yara_garden"} & parts
    if "--purified" in sys.argv:
        value = sys.argv[sys.argv.index("--purified") + 1]
        chosen = (parts or {"all"}) if value == "all" else set() if value == "none" else set(value.split(","))
    crop = None
    if "--crop" in sys.argv:
        crop = tuple(int(v) for v in sys.argv[sys.argv.index("--crop") + 1].split(","))
    img = render(zone_id, chosen, "--terrain-only" in sys.argv, crop)
    if crop is not None:
        img = crop_screen(img, crop)
    img.save(png)
    print(f"{png}: {zone_id}, purificado: {', '.join(sorted(chosen)) or 'nada'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
