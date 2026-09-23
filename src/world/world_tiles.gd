class_name WorldTiles
extends RefCounted

## Traduce un mapa de materiales al atlas de terreno generado por
## `tools/gen_tiles.py`. Contrato «Vereda», fase 5, paso 2b.
##
## El atlas no usa los terrenos automáticos de Godot: la máscara de vecinos se
## calcula aquí, en código legible, porque el método de autoría de las zonas
## (mapa de texto o pintado en el editor) se decide en la parte 3 y esta clase
## sirve a los dos.

const ATLAS_PATH := "res://assets/tilesets/world.png"

enum Terrain { SOIL, PATH, WATER, FLORA }

## Máscara de vecinos del mismo material. Mismo orden que en gen_tiles.py.
const NORTH := 1
const EAST := 2
const SOUTH := 4
const WEST := 8
const INTERIOR := 15

const SOIL_VARIANTS := 4

## Fila del atlas de cada material superpuesto, en su estado enfermo. El
## purificado va en la fila siguiente.
const OVERLAY_ROW := {
	Terrain.PATH: 1,
	Terrain.WATER: 3,
	Terrain.FLORA: 5,
}

## Leyenda de los mapas de texto: un carácter por tile.
const LEGEND := {
	".": Terrain.SOIL,
	"=": Terrain.PATH,
	"~": Terrain.WATER,
	"#": Terrain.FLORA,
}


## TileSet de una sola fuente con el atlas entero.
static func build_tileset() -> TileSet:
	var tileset := TileSet.new()
	tileset.tile_size = Vector2i(DesignTokens.TILE_SIZE, DesignTokens.TILE_SIZE)
	var source := TileSetAtlasSource.new()
	source.texture = load(ATLAS_PATH)
	source.texture_region_size = tileset.tile_size
	var columns := source.texture.get_width() / DesignTokens.TILE_SIZE
	var rows := source.texture.get_height() / DesignTokens.TILE_SIZE
	for y in rows:
		for x in columns:
			source.create_tile(Vector2i(x, y))
	tileset.add_source(source, 0)
	return tileset


## Coordenada del atlas para una celda.
static func atlas_coords(material: Terrain, purified: bool, mask: int, cell: Vector2i) -> Vector2i:
	if material == Terrain.SOIL:
		var variant := _soil_variant(cell)
		return Vector2i(variant + (SOIL_VARIANTS if purified else 0), 0)
	return Vector2i(mask, OVERLAY_ROW[material] + (1 if purified else 0))


## Máscara de una celda: qué vecinos continúan su mismo material. Fuera del
## mapa se cuenta como continuación, para que el borde de la zona no dibuje una
## orilla falsa.
static func neighbor_mask(grid: Array, cell: Vector2i) -> int:
	var material: int = grid[cell.y][cell.x]
	var mask := 0
	var steps := [[Vector2i.UP, NORTH], [Vector2i.RIGHT, EAST], [Vector2i.DOWN, SOUTH], [Vector2i.LEFT, WEST]]
	for step in steps:
		var n: Vector2i = cell + step[0]
		if n.y < 0 or n.y >= grid.size() or n.x < 0 or n.x >= grid[n.y].size():
			mask |= step[1]
		elif grid[n.y][n.x] == material:
			mask |= step[1]
	return mask


## Convierte un mapa de texto en una rejilla de materiales.
static func parse(lines: PackedStringArray) -> Array:
	var grid: Array = []
	for line in lines:
		var row: Array = []
		for ch in line:
			row.append(LEGEND.get(ch, Terrain.SOIL))
		grid.append(row)
	return grid


## Pinta la rejilla en una capa. `purified_at` decide, por celda, el estado.
static func paint(layer: TileMapLayer, grid: Array, purified_at: Callable) -> void:
	for y in grid.size():
		for x in grid[y].size():
			var cell := Vector2i(x, y)
			var material: Terrain = grid[y][x]
			var mask := neighbor_mask(grid, cell)
			layer.set_cell(cell, 0, atlas_coords(material, purified_at.call(cell), mask, cell))


## Variante de suelo estable por celda: el mismo mapa sale siempre igual.
static func _soil_variant(cell: Vector2i) -> int:
	var h := (cell.x * 73856093) ^ (cell.y * 19349663)
	return absi(h) % SOIL_VARIANTS
