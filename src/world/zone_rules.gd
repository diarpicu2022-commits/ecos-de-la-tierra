class_name ZoneRules
extends RefCounted

## Carga de zonas y salidas, y las reglas del contrato «Umbral» sobre ellas
## (docs/ux/anexos/2026-09-30-movimiento-y-zonas.md):
##
## 1. Una salida solo existe donde el camino pisado cruza el borde del mapa.
## 2. Ningún borde de mapa pisable que no sea salida (arquitectura prohibida).
## 3. Como mucho `MAX_EXITS_PER_SCREEN` salidas en cualquier pantalla de 480 px.
## 4. Cada salida lleva a una casilla pisable, un tile dentro de la zona de
##    destino, junto a una salida que devuelve a la zona de origen: siempre se
##    puede volver por donde se vino.
##
## `check()` devuelve la lista de incumplimientos, en español y legibles. La
## usan `verify_movement.gd` y, en la parte 3, la prueba de cada zona.

const ZONES_DIR := "res://data/world/zones/"
const EXITS_PATH := "res://data/world/exits.json"
const NAMES_PATH := "res://data/world/zones.json"

## Pantalla en tiles: 480 x 270 px con tiles de 16 px. La última fila visible
## queda cortada a 14 px, así que una pantalla abarca hasta 17 filas.
const SCREEN_TILES := Vector2i(30, 17)


## Líneas del mapa de texto de una zona, sin líneas vacías.
static func load_zone(zone_id: String) -> PackedStringArray:
	var text := FileAccess.get_file_as_string(ZONES_DIR + zone_id + ".txt")
	var lines := PackedStringArray()
	for line in text.split("\n"):
		var clean := line.strip_edges()
		if not clean.is_empty():
			lines.append(clean)
	return lines


## Todas las salidas del juego, tal como están en `exits.json`.
static func load_exits() -> Array:
	var data = JSON.parse_string(FileAccess.get_file_as_string(EXITS_PATH))
	return data["exits"] if data is Dictionary else []


## Nombre visible de cada zona, por id: `{"prueba_a": "Claro de prueba"}`.
static func load_names() -> Dictionary:
	var data = JSON.parse_string(FileAccess.get_file_as_string(NAMES_PATH))
	var names := {}
	if data is Dictionary:
		for id in data["zones"]:
			names[id] = data["zones"][id]["name"]
	return names


## Las salidas que parten de `zone_id`.
static func exits_from(zone_id: String, exits: Array) -> Array:
	return exits.filter(func(e): return e["from"] == zone_id)


static func cell_of(exit: Dictionary, key: String) -> Vector2i:
	return Vector2i(int(exit[key][0]), int(exit[key][1]))


static func walkable(ch: String) -> bool:
	return WorldTiles.LEGEND.get(ch, WorldTiles.Terrain.SOIL) not in WorldTiles.SOLID


static func on_border(cell: Vector2i, size: Vector2i) -> bool:
	return cell.x == 0 or cell.y == 0 or cell.x == size.x - 1 or cell.y == size.y - 1


## Incumplimientos de la zona `zone_id`. `zones` da las líneas de cada zona por
## id, para poder comprobar también el destino de cada salida.
static func check(zone_id: String, zones: Dictionary, exits: Array) -> PackedStringArray:
	var problems := PackedStringArray()
	var lines: PackedStringArray = zones[zone_id]
	var size := Vector2i(lines[0].length(), lines.size())
	for y in size.y:
		if lines[y].length() != size.x:
			problems.append("%s: la fila %d mide %d, no %d" % [zone_id, y, lines[y].length(), size.x])
			return problems
	var own := exits_from(zone_id, exits)
	var exit_cells := {}
	for e in own:
		exit_cells[cell_of(e, "cell")] = e

	# Reglas 1 y 2: el borde.
	for y in size.y:
		for x in size.x:
			var cell := Vector2i(x, y)
			if not on_border(cell, size):
				continue
			var ch := lines[y][x]
			if exit_cells.has(cell):
				if ch != "=":
					problems.append("%s: la salida %s no es camino ('%s')" % [zone_id, cell, ch])
			elif walkable(ch):
				problems.append("%s: borde pisable %s que no es salida" % [zone_id, cell])
	for cell in exit_cells:
		if not on_border(cell, size):
			problems.append("%s: la salida %s no está en el borde" % [zone_id, cell])

	# Regla 3: densidad por pantalla, en todas las posiciones de la pantalla.
	var window := Vector2i(mini(SCREEN_TILES.x, size.x), mini(SCREEN_TILES.y, size.y))
	for oy in size.y - window.y + 1:
		for ox in size.x - window.x + 1:
			var inside := 0
			for cell: Vector2i in exit_cells:
				if Rect2i(Vector2i(ox, oy), window).has_point(cell):
					inside += 1
			if inside > DesignTokens.MAX_EXITS_PER_SCREEN:
				problems.append("%s: %d salidas en la pantalla que empieza en %s" % [
					zone_id, inside, Vector2i(ox, oy)])
				break

	# Regla 4: el destino existe, se pisa y permite volver.
	for e in own:
		var to: String = e["to"]
		if not zones.has(to):
			problems.append("%s: la salida %s lleva a una zona que no existe (%s)" % [
				zone_id, cell_of(e, "cell"), to])
			continue
		var dest: PackedStringArray = zones[to]
		var dsize := Vector2i(dest[0].length(), dest.size())
		var tc := cell_of(e, "to_cell")
		if not Rect2i(Vector2i.ZERO, dsize).has_point(tc) or not walkable(dest[tc.y][tc.x]):
			problems.append("%s: la salida %s aparece en %s:%s, que no se pisa" % [
				zone_id, cell_of(e, "cell"), to, tc])
			continue
		var back := false
		for r in exits_from(to, exits):
			var rc := cell_of(r, "cell")
			if r["to"] == zone_id and absi(rc.x - tc.x) + absi(rc.y - tc.y) == 1:
				back = true
		if not back:
			problems.append("%s: desde %s:%s no hay salida de vuelta junto a la llegada" % [
				zone_id, to, tc])
	return problems
