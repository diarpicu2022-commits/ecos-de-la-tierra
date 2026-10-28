extends Node

## Prueba medida de una zona. Contrato «Rastro»
## (docs/ux/anexos/2026-10-01-las-siete-zonas.md, «Verificación de cada zona»).
##   godot --headless --path . res://tools/verify_zone.tscn -- <zona>
## Sin argumento, mide Valdehoja.
##
## Comunes a todas las zonas:
##   - las reglas de «Umbral» (`ZoneRules.check`). Una salida hacia una de las
##     siete zonas que todavía no está dibujada se da como PENDIENTE, no como
##     OK: existe en el mapa y no se puede cruzar hasta que se dibuje su zona;
##   - la capa de decorado mide lo mismo que la de materiales, cada carácter
##     está en su leyenda, se apoya en suelo o camino (un árbol, también en el
##     follaje; la fauna, también en el agua) y cada pieza de varios tiles
##     está entera;
##   - ningún decorado es de una clase del catálogo de lo que responde, y cada
##     entidad es una clase del catálogo de su región o global (`interactables.json`);
##   - un hito, de entre 2 × 3 y 4 × 4 tiles, que se alcanza;
##   - desde la aparición se alcanza cada salida y cada entidad;
##   - cada franja vertical de 480 px tiene al menos una pista (camino o hito).
##
## Valdehoja (adapta los puntos 2 a 4 del contrato):
##   - sin monstruos, sin pasos cerrados y sin viñetas;
##   - el camino principal lleva de la aparición al hito sin salir del camino;
##   - seis partes (`valdehoja.parts.txt`): el jardín de Yara y una por
##     región; cada una se alcanza, el hito está en el jardín y la fauna
##     silvestre solo está dentro de una parte;
##   - cada casa tiene un camino delante de la puerta.
##
## Se declara pendiente, porque necesita la captura del motor (paso 3):
## `verify_palette.py image --world` y la prueba de entrecerrar.

const SCREEN_COLUMNS := 30  ## 480 px de ancho en tiles de 16.
const LANDMARK_MIN_SIDE := 2
const LANDMARK_MAX_SIDE := 4
const LANDMARK_MIN_AREA := 6  ## 2 × 3 tiles.
const CRYPT_ID := "greed_crypt"
const HOME_ID := "valdehoja"
const HOME_PARTS := ["yara_garden", "ashen_forest", "tar_basin", "broken_coast",
	"withered_plain", "waning_peak"]
const TREES_ON_FLORA := ["tree", "tree_b"]
const STEPS := [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]

var _pass := 0
var _fail := 0
var _pending := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone_id: String = args[0] if not args.is_empty() else HOME_ID
	print("verify_zone: %s" % zone_id)
	_measure(zone_id)
	print("\n%d de %d OK, %d pendientes" % [_pass, _pass + _fail, _pending])
	get_tree().quit(0 if _fail == 0 else 1)


func _measure(zone_id: String) -> void:
	var lines := ZoneRules.load_zone(zone_id)
	var deco := ZoneRules.load_deco(zone_id)
	_check("la zona tiene mapa de materiales", not lines.is_empty())
	_check("la zona tiene capa de decorado", not deco.is_empty())
	if lines.is_empty() or deco.is_empty():
		return
	var size := Vector2i(lines[0].length(), lines.size())
	var catalog := _catalog()
	var planned := _planned_zones(catalog)

	print("\n«Umbral»")
	var zones := {zone_id: lines}
	var exits := ZoneRules.load_exits()
	for e in ZoneRules.exits_from(zone_id, exits):
		var to: String = e["to"]
		if to != zone_id and not ZoneRules.load_zone(to).is_empty():
			zones[to] = ZoneRules.load_zone(to)
	var problems := ZoneRules.check(zone_id, zones, exits)
	var real := PackedStringArray()
	for p in problems:
		var waiting := false
		for id in planned:
			if p.ends_with("(%s)" % id) and not zones.has(id):
				waiting = true
		if waiting:
			_wait(p.replace("lleva a una zona que no existe", "lleva a una zona aún sin dibujar"))
		else:
			real.append(p)
	_check("reglas de salida y borde", real.is_empty(), "; ".join(real))

	print("\nCapa de decorado")
	var legend: Dictionary = deco["legend"]
	var rows: PackedStringArray = deco["rows"]
	_check("tiene %d filas, como el mapa" % size.y, rows.size() == size.y,
		"tiene %d" % rows.size())
	var cells := {}
	var unknown := PackedStringArray()
	var off_ground := PackedStringArray()
	for y in mini(rows.size(), size.y):
		_check_row_length(y, rows[y], size.x)
		for x in mini(rows[y].length(), size.x):
			var ch := rows[y][x]
			if ch == " ":
				continue
			cells[Vector2i(x, y)] = ch
			if not legend.has(ch):
				unknown.append("'%s' en %s" % [ch, Vector2i(x, y)])
			elif not _ground_ok(legend[ch], lines[y][x]):
				off_ground.append("%s en %s" % [legend[ch]["id"], Vector2i(x, y)])
	_check("cada carácter está en la leyenda", unknown.is_empty(), ", ".join(unknown))
	_check("todo se apoya en suelo o camino (los árboles, también en el follaje)",
		off_ground.is_empty(), ", ".join(off_ground.slice(0, 5)))
	if not unknown.is_empty():
		return
	var broken := PackedStringArray()
	var pieces := _pieces(rows, legend, broken)
	_check("%d piezas, todas completas a su tamaño" % pieces.size(), broken.is_empty(),
		", ".join(broken.slice(0, 5)))
	for piece in pieces:
		var entry: Dictionary = legend[piece["ch"]]
		if String(entry["id"]).begins_with("house"):
			var at: Vector2i = piece["at"]
			var door := at + Vector2i(entry["size"].x / 2, entry["size"].y)
			_check("la puerta de la casa en %s da a un camino" % at,
				Rect2i(Vector2i.ZERO, size).has_point(door) and lines[door.y][door.x] == "=")

	print("\nCatálogo de lo que responde")
	var region := _region_of(zone_id)
	var as_decor := PackedStringArray()
	var foreign := PackedStringArray()
	for ch in legend:
		var entry: Dictionary = legend[ch]
		if entry["kind"] == "decor" and catalog.has(entry["id"]):
			as_decor.append(entry["id"])
		if entry["kind"] == "entity":
			var scope: String = catalog.get(entry["id"], "")
			if scope != "global" and scope != region:
				foreign.append(entry["id"])
	_check("ningún decorado es de una clase que responde", as_decor.is_empty(), ", ".join(as_decor))
	_check("cada entidad es del catálogo global o de su región", foreign.is_empty(), ", ".join(foreign))

	print("\nHito y alcance")
	var spawn := _of_kind(cells, legend, "spawn")
	_check("una sola aparición", spawn.size() == 1, "hay %d" % spawn.size())
	if spawn.size() != 1:
		return
	var reach := _flood(spawn[0], lines, cells, legend, false)
	var landmark := _of_kind(cells, legend, "landmark")
	var ids := {}
	for c in landmark:
		ids[cells[c]] = true
	var box := _bounds(landmark)
	var sides_ok := mini(box.size.x, box.size.y) >= LANDMARK_MIN_SIDE \
		and maxi(box.size.x, box.size.y) <= LANDMARK_MAX_SIDE \
		and box.size.x * box.size.y >= LANDMARK_MIN_AREA
	_check("un hito de %d × %d tiles, entre 2 × 3 y 4 × 4" % [box.size.x, box.size.y],
		ids.size() == 1 and sides_ok and box.size.x * box.size.y == landmark.size(),
		"%d hitos, %d tiles" % [ids.size(), landmark.size()])
	_check("el hito se alcanza", _touches(landmark, reach))
	for e in ZoneRules.exits_from(zone_id, exits):
		var cell := ZoneRules.cell_of(e, "cell")
		_check("la salida %s se alcanza desde la aparición" % cell, reach.has(cell))
	for c in _of_kind(cells, legend, "entity"):
		_check("%s en %s se alcanza" % [legend[cells[c]]["id"], c], _touches([c], reach))
	for x0 in range(0, size.x, SCREEN_COLUMNS):
		var x1 := mini(x0 + SCREEN_COLUMNS, size.x)
		var clue := false
		for y in size.y:
			for x in range(x0, x1):
				if lines[y][x] == "=" or Vector2i(x, y) in landmark:
					clue = true
		_check("pista en la franja de x %d a %d" % [x0, x1 - 1], clue)

	if zone_id == HOME_ID:
		_measure_home(zone_id, lines, cells, legend, spawn[0], reach, landmark)
	else:
		_wait("composición regional (camino a la fuente, 3 viñetas, paso cerrado): se mide desde el Bosque")
	_wait("verify_palette.py image --world y prueba de entrecerrar: necesitan la captura del paso 3")


func _measure_home(zone_id: String, lines: PackedStringArray, cells: Dictionary,
		legend: Dictionary, spawn: Vector2i, reach: Dictionary, landmark: Array) -> void:
	print("\nValdehoja")
	var forbidden := PackedStringArray()
	for ch in legend:
		var entry: Dictionary = legend[ch]
		if entry["id"] in ["monster", "blocker"] or entry["kind"] == "vignette":
			forbidden.append(entry["id"])
	_check("sin monstruos, pasos cerrados ni viñetas", forbidden.is_empty(), ", ".join(forbidden))
	var on_path := _flood(spawn, lines, cells, legend, true)
	_check("el camino principal lleva de la aparición al hito", _touches(landmark, on_path))

	var parts := ZoneRules.load_parts(zone_id)
	var names := parts.keys()
	names.sort()
	var expected := HOME_PARTS.duplicate()
	expected.sort()
	_check("seis partes: el jardín de Yara y una por región", names == expected, str(names))
	var owner := {}
	for id in parts:
		for c: Vector2i in parts[id]:
			owner[c] = id
	for id in parts:
		_check("la parte %s existe y se alcanza (%d tiles)" % [id, parts[id].size()],
			not parts[id].is_empty() and _touches(parts[id], reach))
	_check("el hito está en el jardín de Yara",
		landmark.all(func(c): return owner.get(c, "") == "yara_garden"))
	var stray := PackedStringArray()
	for c in cells:
		if legend[cells[c]]["kind"] == "fauna" and not owner.has(c):
			stray.append(str(c))
	_check("la fauna silvestre está dentro de una parte (solo vuelve al purificar)",
		stray.is_empty(), ", ".join(stray))


## Casillas alcanzables desde `from` andando: suelo y camino sin decorado
## sólido. Con `path_only`, solo por camino.
func _flood(from: Vector2i, lines: PackedStringArray, cells: Dictionary,
		legend: Dictionary, path_only: bool) -> Dictionary:
	var size := Vector2i(lines[0].length(), lines.size())
	var seen := {from: true}
	var queue: Array[Vector2i] = [from]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		for step in STEPS:
			var n: Vector2i = c + step
			if seen.has(n) or not Rect2i(Vector2i.ZERO, size).has_point(n):
				continue
			var ch := lines[n.y][n.x]
			if not ZoneRules.walkable(ch) or (path_only and ch != "="):
				continue
			if cells.has(n) and legend[cells[n]]["solid"]:
				continue
			seen[n] = true
			queue.append(n)
	return seen


## Alguna casilla de `targets` está alcanzada o tiene un vecino alcanzado: lo
## sólido se alcanza cuando se puede llegar a su lado.
func _touches(targets: Array, reach: Dictionary) -> bool:
	for c: Vector2i in targets:
		if reach.has(c):
			return true
		for step in STEPS:
			if reach.has(c + step):
				return true
	return false


## Lo que cada pieza puede pisar: suelo o camino; un árbol, también el
## follaje (su copa cubre el borde del bosque); la fauna, también el agua.
func _ground_ok(entry: Dictionary, ground: String) -> bool:
	if ground in [".", "="]:
		return true
	if ground == "#":
		return entry["id"] in TREES_ON_FLORA
	return ground == "~" and entry["kind"] == "fauna"


## Las piezas de la capa por su esquina superior izquierda. Una pieza de
## varios tiles tiene que estar entera; si no, se anota en `broken`.
func _pieces(rows: PackedStringArray, legend: Dictionary, broken: PackedStringArray) -> Array:
	var claimed := {}
	var out := []
	for y in rows.size():
		for x in rows[y].length():
			var ch := rows[y][x]
			if ch == " " or claimed.has(Vector2i(x, y)):
				continue
			var size: Vector2i = legend[ch]["size"]
			var whole := true
			for j in size.y:
				for i in size.x:
					var c := Vector2i(x + i, y + j)
					if c.y >= rows.size() or c.x >= rows[c.y].length() or rows[c.y][c.x] != ch or claimed.has(c):
						whole = false
					claimed[c] = true
			if whole:
				out.append({"ch": ch, "at": Vector2i(x, y)})
			else:
				broken.append("%s en %s" % [legend[ch]["id"], Vector2i(x, y)])
	return out


func _of_kind(cells: Dictionary, legend: Dictionary, kind: String) -> Array:
	return cells.keys().filter(func(c): return legend[cells[c]]["kind"] == kind)


func _bounds(cells: Array) -> Rect2i:
	if cells.is_empty():
		return Rect2i()
	var box := Rect2i(cells[0], Vector2i.ONE)
	for c: Vector2i in cells:
		box = box.expand(c).expand(c + Vector2i.ONE)
	return box


## Id de cada clase del catálogo y su ámbito: `{"seedbed": "global", ...}`.
func _catalog() -> Dictionary:
	var data = JSON.parse_string(FileAccess.get_file_as_string("res://data/world/interactables.json"))
	var classes := {}
	if data is Dictionary:
		for c in data["classes"]:
			classes[c["id"]] = c["scope"]
	return classes


## Las siete zonas del juego: Valdehoja, una por región del catálogo y la Cripta.
func _planned_zones(catalog: Dictionary) -> Array:
	var planned := [HOME_ID, CRYPT_ID]
	for id in catalog:
		if catalog[id] != "global" and catalog[id] not in planned:
			planned.append(catalog[id])
	return planned


func _region_of(zone_id: String) -> String:
	return "global" if zone_id in [HOME_ID, CRYPT_ID] else zone_id


func _check_row_length(y: int, row: String, width: int) -> void:
	if row.length() > width:
		_check("la fila %d del decorado no pasa del mapa" % y, false, "mide %d" % row.length())


func _check(label: String, condition: bool, detail: String = "") -> void:
	if condition:
		_pass += 1
		print("  OK    %s" % label)
	else:
		_fail += 1
		print("  FALLA %s  (%s)" % [label, detail])


func _wait(label: String) -> void:
	_pending += 1
	print("  PENDIENTE %s" % label)
