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
## En el motor (paso 3), con `WorldRoot`:
##   - un sprite por pieza en la capa de entidades, ordenada por altura, y un
##     cuerpo sólido por pieza sólida;
##   - andando hacia la puerta de una casa, Ilan se para fuera;
##   - en Valdehoja, el jardín está purificado al empezar, la arboleda no, y al
##     purificar el Bosque vuelven la arboleda y su fauna.
##
## Paso 4, movimiento (enmienda 8), cuadro a cuadro con `WorldAmbient.advance()`:
##   - el agua viva alterna sus dos cuadros cada DUR_AMBIENT_WATER; la enferma
##     no se mueve;
##   - la hierba purificada se mece cada DUR_AMBIENT_SWAY; la enferma no;
##   - un animal en lo purificado anda, en píxeles enteros, cerca de su sitio
##     y en suelo sano; uno en lo enfermo se queda quieto;
##   - con movimiento reducido no se mueve nada.
##
## Se declara pendiente: `verify_palette.py image --world` y la prueba de
## entrecerrar, que se miden sobre la captura con `tools/verify_squint.py`.

const SCREEN_COLUMNS := 30  ## 480 px de ancho en tiles de 16.
const LANDMARK_MIN_SIDE := 2
const LANDMARK_MAX_SIDE := 4
const LANDMARK_MIN_AREA := 6  ## 2 × 3 tiles.
## Composición de una zona regional (contrato «Rastro»). Son reglas de
## autoría, no de dibujo: viven aquí y no en DesignTokens.
const VIGNETTE_PATH_DISTANCE := 2     ## Una viñeta, a 2 tiles del camino como mucho.
const LANDMARK_SOURCE_DISTANCE := 3   ## El hito, a 3 tiles de la fuente como mucho.
## El hito asoma por primera vez a media zona: entre el 25 % y el 65 % del
## recorrido del camino principal hasta la fuente.
const LANDMARK_FIRST_VIEW_MIN := 0.25
const LANDMARK_FIRST_VIEW_MAX := 0.65
const CRYPT_ID := "greed_crypt"
const HOME_ID := "valdehoja"
## La parte `greed_crypt` es solo la bocamina: el paso cerrado de Valdehoja
## que se abre al purificar la Cripta (enmienda 12).
const HOME_PARTS := ["yara_garden", "ashen_forest", "tar_basin", "broken_coast",
	"withered_plain", "waning_peak", "greed_crypt"]
const TREES_ON_FLORA := ["tree", "tree_b", "burnt_tree", "bush", "pine", "boulder"]
## Lo que puede apoyarse en el muro de la Cripta (enmienda 10).
const ON_WALL := ["pillar", "root", "banner"]
## Decorado del daño (catálogo 2a, «decorado permitido»): lo que cuenta para el
## gradiente.
const DAMAGE_DECOR := ["stump", "ash", "burnt_tree", "litter", "crop_row", "oil", "barrel", "bottle", "torn_bag", "salt", "dark_rock", "crack", "meltwater", "coins"]
const STEPS := [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]

var _pass := 0
var _fail := 0
var _pending := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone_id: String = args[0] if not args.is_empty() else HOME_ID
	print("verify_zone: %s" % zone_id)
	_measure(zone_id)
	if not ZoneRules.load_deco(zone_id).is_empty():
		await _measure_engine(zone_id)
	print("\n%d de %d OK, %d pendientes" % [_pass, _pass + _fail, _pending])
	get_tree().quit(0 if _fail == 0 else 1)


## Paso 3: la zona montada en el motor con `WorldRoot` y `WorldDecor`.
func _measure_engine(zone_id: String) -> void:
	print("\nEn el motor")
	var state := get_node_or_null("/root/GameState")
	if state != null:
		state.flags.clear()
	var deco := ZoneRules.load_deco(zone_id)
	var legend: Dictionary = deco["legend"]
	var pieces := WorldDecor.pieces(deco["rows"], legend)
	var spawn := Vector2i(-1, -1)
	var solid := 0
	for piece in pieces:
		var entry: Dictionary = legend[piece["ch"]]
		if entry["kind"] == "spawn":
			spawn = piece["at"]
		elif entry["solid"]:
			solid += 1
	var world := WorldRoot.new()
	world.start_zone = zone_id
	world.start_cell = spawn
	add_child(world)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var lookup := WorldDecor.purified_lookup(zone_id, state)
	var expected := 0
	for piece in pieces:
		var entry: Dictionary = legend[piece["ch"]]
		var size: Vector2i = entry["size"]
		var foot: Vector2i = piece["at"] + Vector2i(size.x / 2, size.y - 1)
		if entry["kind"] == "spawn" or (entry["kind"] == "fauna" and not lookup.call(foot)):
			continue
		expected += 1
	var sprites := world.entities.get_children().filter(func(n): return n != world.body)
	_check("%d sprites de decorado en la capa de entidades, ordenada por altura" % expected,
		sprites.size() == expected and world.entities.y_sort_enabled, "hay %d" % sprites.size())
	_check("%d cuerpos sólidos, uno por pieza sólida" % solid,
		world.solids.get_child_count() == solid, "hay %d" % world.solids.get_child_count())

	# Andar hacia la puerta de una casa: el cuerpo se para en el camino.
	for piece in pieces:
		var entry: Dictionary = legend[piece["ch"]]
		if not String(entry["id"]).begins_with("house"):
			continue
		var at: Vector2i = piece["at"]
		var size: Vector2i = entry["size"]
		var door := at + Vector2i(size.x / 2, size.y)
		world.enter_zone(zone_id, door)
		await get_tree().physics_frame
		await get_tree().physics_frame
		for _i in 40:
			world.body.step(Vector2i.UP, false)
		var feet_y := int(world.body.global_position.y)
		_check("andando hacia la puerta de la casa en %s, Ilan se para fuera" % at,
			feet_y >= (at.y + size.y) * DesignTokens.TILE_SIZE + DesignTokens.PLAYER_HITBOX.y,
			"pies en y = %d" % feet_y)
		break

	if zone_id != HOME_ID and state != null:
		await _measure_region_engine(world, zone_id, spawn, state)
	if zone_id != HOME_ID or state == null:
		world.queue_free()
		return
	# Valdehoja: cada parte sigue a su región.
	var parts := ZoneRules.load_parts(zone_id)
	var garden: Vector2i = parts["yara_garden"][0]
	var grove: Array = parts["ashen_forest"]
	var grove_soil := Vector2i(-1, -1)
	var lines := ZoneRules.load_zone(zone_id)
	for c: Vector2i in grove:
		if lines[c.y][c.x] == "." and grove.has(c + Vector2i.UP) and grove.has(c + Vector2i.DOWN) \
				and grove.has(c + Vector2i.LEFT) and grove.has(c + Vector2i.RIGHT):
			grove_soil = c
			break
	world.enter_zone(zone_id, spawn)
	await get_tree().physics_frame
	_check("al empezar, el jardín de Yara está purificado", _cell_pure(world, garden, lines))
	_check("al empezar, la arboleda está enferma", not _cell_pure(world, grove_soil, lines))
	var birds_before := _count_fauna(world)
	state.set_zone_purified("ashen_forest")
	world.enter_zone(zone_id, spawn)
	await get_tree().physics_frame
	await get_tree().physics_frame
	_check("purificado el Bosque, la arboleda vuelve", _cell_pure(world, grove_soil, lines))
	_check("y vuelve su fauna silvestre (%d -> %d)" % [birds_before, _count_fauna(world)],
		_count_fauna(world) > birds_before)
	await _measure_ambient(world, zone_id, spawn, lines, state)
	state.flags.clear()
	world.queue_free()


## Paso 4 — el movimiento de la enmienda 8, cuadro a cuadro: solo se mueve lo
## purificado, cada ciclo dura su token y con movimiento reducido no se mueve
## nada.
func _measure_ambient(world: WorldRoot, zone_id: String, spawn: Vector2i,
		lines: PackedStringArray, state: Node) -> void:
	print("\nMovimiento (enmienda 8)")
	state.flags.clear()
	state.set_zone_purified("broken_coast")
	state.set_zone_purified("tar_basin")
	world.enter_zone(zone_id, spawn)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var amb := world.ambient
	amb.set_physics_process(false)
	DesignTokens.reduced_motion = false
	var pure_water := -Vector2i.ONE
	var sick_water := -Vector2i.ONE
	for c in world._layer.get_used_cells():
		if lines[c.y][c.x] != "~":
			continue
		var row := world._layer.get_cell_atlas_coords(c).y
		if row == 4 and pure_water.x < 0:
			pure_water = c
		elif row == 3 and sick_water.x < 0:
			sick_water = c
	var sway_pure: Sprite2D = null
	var sway_sick: Sprite2D = null
	var animal_pure: Sprite2D = null
	var animal_sick: Sprite2D = null
	for n in world.entities.get_children():
		if not n is Sprite2D:
			continue
		var nm := String(n.name)
		if nm.begins_with("grass") and n.has_meta("frames") and sway_pure == null:
			sway_pure = n
		elif nm.begins_with("grass") and not n.has_meta("frames") and sway_sick == null:
			sway_sick = n
		elif n.has_meta("kind") and n.get_meta("kind") == "animal":
			var lookup := WorldDecor.purified_lookup(zone_id, state)
			if lookup.call(WorldAmbient._cell_of(n.position)):
				if animal_pure == null:
					animal_pure = n
			elif animal_sick == null:
				animal_sick = n
	var water_period := WorldAmbient._frames(DesignTokens.DUR_AMBIENT_WATER)
	var water_rows := {}
	var water_changes := 0
	var last_row := world._layer.get_cell_atlas_coords(pure_water).y
	var sick_row := world._layer.get_cell_atlas_coords(sick_water).y
	var sick_water_still := true
	var sway_changes := 0
	var sway_last: Texture2D = sway_pure.texture if sway_pure else null
	var sick_tex: Texture2D = sway_sick.texture if sway_sick else null
	var sick_grass_still := true
	var home: Vector2 = animal_pure.position if animal_pure else Vector2.ZERO
	var moved := false
	var integer := true
	var in_range := true
	var on_walkable := true
	var sick_animal_pos: Vector2 = animal_sick.position if animal_sick else Vector2.ZERO
	var sick_animal_still := true
	var frames := 600
	for _i in frames:
		amb.advance()
		var row := world._layer.get_cell_atlas_coords(pure_water).y
		water_rows[row] = true
		if row != last_row:
			water_changes += 1
			last_row = row
		if world._layer.get_cell_atlas_coords(sick_water).y != sick_row:
			sick_water_still = false
		if sway_pure and sway_pure.texture != sway_last:
			sway_changes += 1
			sway_last = sway_pure.texture
		if sway_sick and sway_sick.texture != sick_tex:
			sick_grass_still = false
		if animal_pure:
			var p := animal_pure.position
			moved = moved or p != home
			integer = integer and p == p.round()
			in_range = in_range and p.distance_to(home) <= DesignTokens.ANIMAL_RANGE + DesignTokens.ANIMAL_HOP_MAX
			on_walkable = on_walkable and amb._walkable.call(WorldAmbient._cell_of(p))
		if animal_sick and animal_sick.position != sick_animal_pos:
			sick_animal_still = false
	_check("el agua viva alterna sus dos cuadros cada %d cuadros (%d cambios en %d)" % [
		water_period, water_changes, frames],
		pure_water.x >= 0 and water_rows.has(4) and water_rows.has(WorldTiles.WATER_ALT_ROW)
		and water_changes == frames / water_period, "filas %s" % str(water_rows.keys()))
	_check("el agua enferma no se mueve", sick_water.x >= 0 and sick_water_still)
	_check("la hierba purificada se mece (%d cambios)" % sway_changes,
		sway_pure != null and sway_changes == frames / WorldAmbient._frames(DesignTokens.DUR_AMBIENT_SWAY))
	_check("la hierba enferma no se mueve", sway_sick != null and sick_grass_still)
	_check("un animal en lo purificado anda (%s)" % (animal_pure.name if animal_pure else "ninguno"),
		animal_pure != null and moved)
	_check("y siempre en píxeles enteros, cerca de su sitio y en suelo sano",
		integer and in_range and on_walkable)
	_check("un animal en lo enfermo se queda quieto", animal_sick != null and sick_animal_still)
	# Movimiento reducido: nada cambia.
	DesignTokens.reduced_motion = true
	var before_row := world._layer.get_cell_atlas_coords(pure_water).y
	var before_tex: Texture2D = sway_pure.texture
	var before_pos := animal_pure.position
	for _i in 300:
		amb.advance()
	_check("con movimiento reducido no se mueve nada",
		world._layer.get_cell_atlas_coords(pure_water).y == before_row
		and sway_pure.texture == before_tex and animal_pure.position == before_pos)
	DesignTokens.reduced_motion = false
	amb.set_physics_process(true)


## Zona regional en el motor: enferma, el monstruo y el paso cerrado están y
## son sólidos; purificada (`purified_<zona>`), desaparecen con su cuerpo y el
## terreno se pinta purificado.
func _measure_region_engine(world: WorldRoot, zone_id: String, spawn: Vector2i, state: Node) -> void:
	print("\nZona regional en el motor")
	var lines := ZoneRules.load_zone(zone_id)
	var gone := func() -> int:
		return world.entities.get_children().filter(func(n):
			var nm := String(n.name)
			return nm.begins_with("monster") or nm.begins_with("blocker")).size()
	state.flags.clear()
	world.enter_zone(zone_id, spawn)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var sick_solids := world.solids.get_child_count()
	var sick_marks: int = gone.call()
	_check("enferma: el monstruo y el paso cerrado están (%d)" % sick_marks, sick_marks >= 2)
	state.set_zone_purified(zone_id)
	world.enter_zone(zone_id, spawn)
	await get_tree().physics_frame
	await get_tree().physics_frame
	# Lo sólido que desaparece al purificar: el paso cerrado, el monstruo y el
	# daño que se limpia (WorldDecor.VANISH_WHEN_PURE).
	var deco := ZoneRules.load_deco(zone_id)
	var vanish_solid := 0
	for piece in WorldDecor.pieces(deco["rows"], deco["legend"]):
		var entry: Dictionary = deco["legend"][piece["ch"]]
		if entry["solid"] and entry["id"] in WorldDecor.VANISH_WHEN_PURE:
			vanish_solid += 1
	_check("purificada: desaparecen, con su cuerpo (%d -> %d sólidos)" % [
		sick_solids, world.solids.get_child_count()],
		gone.call() == 0 and world.solids.get_child_count() == sick_solids - vanish_solid)
	# El suelo que se pisa: tierra o, en la Costa, arena.
	var soil := Vector2i(-1, -1)
	for c in world._layer.get_used_cells():
		if lines[c.y][c.x] in [".", ":", ","] and soil.x < 0:
			soil = c
	_check("purificada: el suelo se pinta purificado", soil.x >= 0 and _cell_pure(world, soil, lines))
	state.flags.clear()


## ¿La casilla está pintada en su estado purificado? El suelo purificado está
## en las columnas 4 a 7 de la fila 0 o en la fila del borde del prado.
func _cell_pure(world: WorldRoot, cell: Vector2i, lines: PackedStringArray) -> bool:
	var coords := world._layer.get_cell_atlas_coords(cell)
	if lines[cell.y][cell.x] == ".":
		return (coords.y == 0 and coords.x >= WorldTiles.SOIL_VARIANTS) or coords.y == WorldTiles.MEADOW_EDGE_ROW
	return coords.y % 2 == 0


func _count_fauna(world: WorldRoot) -> int:
	return world.entities.get_children().filter(
		func(n): return String(n.name).begins_with("bird") or String(n.name).begins_with("butterfly")).size()


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

	# Enmienda 10: la piedra no convive con la tierra, el agua, el follaje ni la
	# arena (verify_tileset no exige su dE porque nunca comparten zona).
	var stone := false
	var apart := PackedStringArray()
	for row in lines:
		stone = stone or row.contains("%") or row.contains(",")
	if stone:
		for ch in [".", "~", "#", ":"]:
			for row in lines:
				if row.contains(ch):
					apart.append(ch)
					break
	_check("la piedra no comparte zona con tierra, agua, follaje ni arena",
		not stone or apart.is_empty(), " ".join(apart))

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
		# En una zona regional, la salida de ida está detrás del paso cerrado:
		# se mide en la composición regional. Aquí, solo la de vuelta.
		if zone_id != HOME_ID and _is_forward(cell, spawn[0]):
			continue
		# La bocamina de Valdehoja tiene su paso cerrado: se mide en Valdehoja.
		if zone_id == HOME_ID and e["to"] == CRYPT_ID:
			continue
		_check("la salida %s se alcanza desde la aparición" % cell, reach.has(cell))
	# Por pieza: una entidad de varios tiles (la bocamina, 2x2) se alcanza si
	# se llega al lado de cualquiera de sus casillas.
	for piece in pieces:
		var entry: Dictionary = legend[piece["ch"]]
		if entry["kind"] != "entity":
			continue
		var covered := []
		for j in entry["size"].y:
			for i in entry["size"].x:
				covered.append(piece["at"] + Vector2i(i, j))
		_check("%s en %s se alcanza" % [entry["id"], piece["at"]], _touches(covered, reach))
	for x0 in range(0, size.x, SCREEN_COLUMNS):
		var x1 := mini(x0 + SCREEN_COLUMNS, size.x)
		var clue := false
		for y in size.y:
			for x in range(x0, x1):
				if lines[y][x] == "=" or Vector2i(x, y) in landmark:
					clue = true
		_check("pista en la franja de x %d a %d" % [x0, x1 - 1], clue)

	if zone_id == HOME_ID:
		_measure_home(zone_id, lines, cells, legend, spawn[0], reach, landmark, exits)
	else:
		_measure_region(zone_id, lines, cells, legend, spawn[0], landmark, exits)
	print("  (la paleta y la prueba de entrecerrar se miden aparte: tools/verify_palette.py image --world"
		+ " sobre las capturas del motor y tools/verify_squint.py %s)" % zone_id)


func _measure_home(zone_id: String, lines: PackedStringArray, cells: Dictionary,
		legend: Dictionary, spawn: Vector2i, reach: Dictionary, landmark: Array, exits: Array) -> void:
	print("\nValdehoja")
	var forbidden := PackedStringArray()
	for ch in legend:
		var entry: Dictionary = legend[ch]
		if entry["id"] == "monster" or entry["kind"] == "vignette":
			forbidden.append(entry["id"])
	_check("sin monstruos ni viñetas", forbidden.is_empty(), ", ".join(forbidden))
	var on_path := _flood(spawn, lines, cells, legend, true)
	_check("el camino principal lleva de la aparición al hito", _touches(landmark, on_path))

	var parts := ZoneRules.load_parts(zone_id)
	var names := parts.keys()
	names.sort()
	var expected := HOME_PARTS.duplicate()
	expected.sort()
	_check("siete partes: el jardín de Yara, una por región y la bocamina", names == expected, str(names))
	var owner := {}
	for id in parts:
		for c: Vector2i in parts[id]:
			owner[c] = id

	# Enmienda 12: un solo paso cerrado, la bocamina. Se abre al purificar la
	# Cripta y no antes: la salida a la Cripta no se alcanza al empezar.
	var blockers := cells.keys().filter(func(c): return legend[cells[c]]["id"] == "blocker")
	var pieces := WorldDecor.pieces(ZoneRules.load_deco(zone_id)["rows"], legend).filter(
		func(p): return legend[p["ch"]]["id"] == "blocker")
	_check("un solo paso cerrado, en la bocamina", pieces.size() == 1
		and blockers.all(func(c): return owner.get(c, "") == CRYPT_ID), "%d pasos" % pieces.size())
	var open_cells := cells.duplicate()
	for c in blockers:
		open_cells.erase(c)
	var open_reach := _flood(spawn, lines, open_cells, legend, false)
	for e in ZoneRules.exits_from(zone_id, exits):
		if e["to"] != CRYPT_ID:
			continue
		var cell := ZoneRules.cell_of(e, "cell")
		_check("la salida a la Cripta %s no se alcanza al empezar" % cell, not reach.has(cell))
		_check("y se alcanza al abrir la bocamina", open_reach.has(cell))
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


## La salida de ida de una zona regional: toda la que no está junto a la
## aparición (la de vuelta es por donde se llega).
func _is_forward(cell: Vector2i, spawn: Vector2i) -> bool:
	return absi(cell.x - spawn.x) + absi(cell.y - spawn.y) > 2


## La composición regional del contrato «Rastro»: camino a la fuente, tres
## viñetas, hito en la fuente, paso cerrado detrás y gradiente de daño.
func _measure_region(zone_id: String, lines: PackedStringArray, cells: Dictionary,
		legend: Dictionary, spawn: Vector2i, landmark: Array, exits: Array) -> void:
	print("\nComposición regional («Rastro»)")
	var size := Vector2i(lines[0].length(), lines.size())
	var sources := cells.keys().filter(func(c): return legend[cells[c]]["id"] == "monster")
	_check("una fuente: el monstruo de historia", sources.size() == 1, "hay %d" % sources.size())
	if sources.size() != 1:
		return
	var source: Vector2i = sources[0]
	# 1. Paso cerrado: la salida de ida, inalcanzable en enfermo y alcanzable
	#    sin los blocker.
	var sick := _flood(spawn, lines, cells, legend, false)
	var open_cells := cells.duplicate()
	for c in cells:
		if legend[cells[c]]["id"] in ["blocker", "monster"]:
			open_cells.erase(c)
	var pure := _flood(spawn, lines, open_cells, legend, false)
	var forward := 0
	for e in ZoneRules.exits_from(zone_id, exits):
		var cell := ZoneRules.cell_of(e, "cell")
		if not _is_forward(cell, spawn):
			continue
		forward += 1
		_check("la salida de ida %s es inalcanzable sin purificar" % cell, not sick.has(cell))
		_check("y se alcanza al purificar (sin los pasos cerrados)", pure.has(cell))
	# En la Cripta, la de ida sube a Valdehoja por detrás de la Sombra (enmienda 12).
	_check("hay salida de ida", forward >= 1)
	# 2. La fuente, por el camino y sin paso cerrado delante.
	var on_path := _flood(spawn, lines, cells, legend, true)
	_check("el camino principal lleva de la llegada a la fuente", _touches([source], on_path))
	_check("ningún paso cerrado antes de la fuente", _touches([source], sick))
	# Recorrido del camino principal, de la llegada a la fuente.
	var route := _route(spawn, source, lines)
	_check("recorrido del camino principal: %d tiles" % route.size(), route.size() > 1)
	if route.size() < 2:
		return
	var order := {}
	for i in route.size():
		order[route[i]] = i
	# 3. Tres viñetas, de dos elementos, junto al camino, en orden y una por pantalla.
	var groups := {}
	for c in cells:
		var entry: Dictionary = legend[cells[c]]
		if entry["kind"] != "vignette":
			continue
		var n := String(entry["id"]).substr(1, 1).to_int()
		if not groups.has(n):
			groups[n] = {"cells": [], "ids": {}}
		groups[n]["cells"].append(c)
		groups[n]["ids"][entry["id"]] = true
	var numbers := groups.keys()
	numbers.sort()
	# La Cripta lleva cinco: una bóveda por región (decisión de Diego, 2026-10-28).
	var expected_n := 5 if zone_id == CRYPT_ID else 3
	var expected := range(1, expected_n + 1)
	_check("exactamente %d viñetas, numeradas de 1 a %d" % [expected_n, expected_n],
		numbers == expected, str(numbers))
	var at_route := {}
	for n in groups:
		_check("la viñeta %d une dos elementos (%s)" % [n, ", ".join(groups[n]["ids"].keys())],
			groups[n]["ids"].size() >= 2)
		var far := 0
		var best := route.size()
		for c: Vector2i in groups[n]["cells"]:
			var near := route.size()
			for r: Vector2i in route:
				if maxi(absi(r.x - c.x), absi(r.y - c.y)) <= VIGNETTE_PATH_DISTANCE:
					near = mini(near, order[r])
			if near == route.size():
				far += 1
			best = mini(best, near)
		_check("la viñeta %d está junto al camino principal (≤ %d tiles)" % [
			n, VIGNETTE_PATH_DISTANCE], far == 0, "%d elementos lejos" % far)
		at_route[n] = best
	if numbers == expected:
		var steps := PackedStringArray()
		var ordered := true
		for n in expected:
			steps.append(str(at_route[n]))
			if n > 1 and at_route[n - 1] >= at_route[n]:
				ordered = false
		_check("las viñetas aparecen en orden hacia la fuente (tile %s de %d)" % [
			", ".join(steps), route.size()], ordered)
		var shared := PackedStringArray()
		for a in expected:
			for b in expected:
				if a >= b:
					continue
				for ca: Vector2i in groups[a]["cells"]:
					for cb: Vector2i in groups[b]["cells"]:
						if absi(ca.x - cb.x) < ZoneRules.SCREEN_TILES.x and absi(ca.y - cb.y) < ZoneRules.SCREEN_TILES.y:
							shared.append("%d y %d" % [a, b])
		_check("nunca dos viñetas en la misma pantalla", shared.is_empty(),
			", ".join(_unique(shared)))
	# 4. Hito: en la fuente, asoma a media zona y se pierde antes de llegar.
	var close := false
	for c: Vector2i in landmark:
		close = close or maxi(absi(c.x - source.x), absi(c.y - source.y)) <= LANDMARK_SOURCE_DISTANCE
	_check("el hito está en la fuente (≤ %d tiles)" % LANDMARK_SOURCE_DISTANCE, close)
	var first := -1
	var hidden_after := false
	for i in route.size():
		var seen := _landmark_visible(route[i], landmark, size)
		if seen and first < 0:
			first = i
		elif not seen and first >= 0:
			hidden_after = true
	var fraction := float(first) / route.size()
	_check("el hito asoma por primera vez a media zona (al %d %% del camino)" % roundi(fraction * 100),
		first >= 0 and fraction >= LANDMARK_FIRST_VIEW_MIN
		and fraction <= LANDMARK_FIRST_VIEW_MAX,
		"entre el %d y el %d %%" % [roundi(LANDMARK_FIRST_VIEW_MIN * 100),
			roundi(LANDMARK_FIRST_VIEW_MAX * 100)])
	_check("y el follaje lo tapa al menos una vez antes de la fuente", hidden_after)
	# 5. Gradiente: más daño cerca de la fuente.
	var bands := [[0, 0], [0, 0], [0, 0]]
	for y in size.y:
		for x in size.x:
			var c := Vector2i(x, y)
			if lines[y][x] not in [".", "=", ":", ","]:
				continue
			var d := Vector2(x - source.x, (y - source.y) * 1.6).length()
			var band := 0 if d < 16.0 else 1 if d < 34.0 else 2
			bands[band][1] += 1
			if cells.has(c) and (legend[cells[c]]["kind"] == "vignette"
					or legend[cells[c]]["id"] in DAMAGE_DECOR):
				bands[band][0] += 1
	var dens := []
	for b in bands:
		dens.append(float(b[0]) / maxi(1, b[1]))
	_check("gradiente: el daño se densifica hacia la fuente (%.2f > %.2f > %.2f por tile)" % dens,
		dens[0] > dens[1] and dens[1] > dens[2])


## El camino principal de `from` a la fuente: el recorrido más corto sobre
## tiles de camino, hasta el tile de camino que toca la fuente.
func _route(from: Vector2i, source: Vector2i, lines: PackedStringArray) -> Array:
	var size := Vector2i(lines[0].length(), lines.size())
	var parent := {from: from}
	var queue: Array[Vector2i] = [from]
	var goal := Vector2i(-1, -1)
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		if maxi(absi(c.x - source.x), absi(c.y - source.y)) <= 2:
			goal = c
			break
		for step in STEPS:
			var n: Vector2i = c + step
			if parent.has(n) or not Rect2i(Vector2i.ZERO, size).has_point(n) or lines[n.y][n.x] != "=":
				continue
			parent[n] = c
			queue.append(n)
	if goal.x < 0:
		return []
	var out := [goal]
	while out[0] != from:
		out.push_front(parent[out[0]])
	return out


## ¿Se ve el hito con la cámara en `cell`? La pantalla de 30 x 17 tiles,
## centrada y encerrada en la zona como la cámara.
func _landmark_visible(cell: Vector2i, landmark: Array, size: Vector2i) -> bool:
	var s := ZoneRules.SCREEN_TILES
	var origin := Vector2i(clampi(cell.x - s.x / 2, 0, maxi(0, size.x - s.x)),
		clampi(cell.y - s.y / 2, 0, maxi(0, size.y - s.y)))
	var view := Rect2i(origin, s)
	for c: Vector2i in landmark:
		if view.has_point(c):
			return true
	return false


func _unique(items: PackedStringArray) -> PackedStringArray:
	var out := PackedStringArray()
	for i in items:
		if not out.has(i):
			out.append(i)
	return out


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
	if ground in [".", "=", ":", ","]:
		return true
	if ground == "#":
		return entry["id"] in TREES_ON_FLORA
	if ground == "%":
		return entry["id"] in ON_WALL
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
