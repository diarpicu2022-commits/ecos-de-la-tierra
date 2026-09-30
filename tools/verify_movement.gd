extends Node2D

## Prueba medida del movimiento. Contrato «Umbral»
## (docs/ux/anexos/2026-09-30-movimiento-y-zonas.md, fase 5).
##   godot --headless --path . res://tools/verify_movement.tscn
##
## Paso 2 — el cuerpo. Cada caso se monta con el tileset real (follaje y agua
## sólidos, suelo pisable) y el cuerpo avanza cuadro a cuadro:
##   - velocidad: 1 y 2 px por cuadro y eje, también en diagonal;
##   - cero cuadros de aceleración, con el teclado de verdad;
##   - un paso de 16 px se cruza y uno de 0 px nunca;
##   - una esquina a CORNER_SLIP px o menos se rodea, a 1 px lateral por
##     cuadro, y a CORNER_SLIP + 1 no;
##   - pared plana: en diagonal se sigue por el eje libre; en recto, se para
##     tocándola, sin hueco;
##   - posición entera en todos los cuadros.
## Los pasos siguientes de la fase 5 añaden aquí sus casos (fundido, salidas,
## límites de la cámara).

const T := DesignTokens.TILE_SIZE
const HALF := DesignTokens.PLAYER_HITBOX.x / 2

var _layer := TileMapLayer.new()
var _body := PlayerBody.new()
var _pass := 0
var _fail := 0
var _frames := 0
var _fractional := 0


func _ready() -> void:
	_layer.tile_set = WorldTiles.build_tileset()
	add_child(_layer)
	_body.input_enabled = false
	add_child(_body)

	print("\n=== CUERPO: VELOCIDAD Y ACELERACION ===")
	await _map(["...................."].duplicate())
	await _test_speeds()
	await _test_keyboard()

	print("\n=== CUERPO: PASOS ESTRECHOS ===")
	await _test_corridors()

	print("\n=== CUERPO: ESQUINAS ===")
	await _test_corners()

	print("\n=== CUERPO: PARED PLANA ===")
	await _test_flat_wall()

	_check("posicion entera en los %d cuadros medidos" % _frames, _fractional == 0,
		"%d cuadros con subpixel" % _fractional)
	print("\n%d de %d" % [_pass, _pass + _fail])
	get_tree().quit(0 if _fail == 0 else 1)


# --- Casos -------------------------------------------------------------------


func _test_speeds() -> void:
	var cases := {
		"andar recto: 1 px por cuadro": [Vector2i(1, 0), false, Vector2i(1, 0)],
		"correr recto: 2 px por cuadro": [Vector2i(-1, 0), true, Vector2i(-2, 0)],
		"andar en diagonal: 1 + 1 px por cuadro (enmienda 4)": [Vector2i(1, 1), false, Vector2i(1, 1)],
		"correr en diagonal: 2 + 2 px por cuadro": [Vector2i(-1, -1), true, Vector2i(-2, -2)],
	}
	for label in cases:
		var c: Array = cases[label]
		_place(Vector2i(160, 160))
		var ok := true
		for _i in 30:
			_step(c[0], c[1])
			ok = ok and _body.last_step == c[2]
		_check(label + " durante 30 cuadros", ok, "ultimo paso %s" % _body.last_step)


func _test_keyboard() -> void:
	# Con el teclado de verdad: el cuerpo lee la entrada en su propio cuadro.
	# `physics_frame` se emite al empezar el cuadro, antes de que los nodos lo
	# procesen: entre dos señales seguidas cabe exactamente un cuadro del
	# cuerpo. Se pulsa, se espera al inicio del cuadro siguiente y se mide lo
	# que se movió en ese único cuadro.
	_place(Vector2i(160, 160))
	_body.input_enabled = true
	await get_tree().physics_frame
	Input.action_press("move_right")
	var first := await _one_frame()
	Input.action_release("move_right")
	var after_release := await _one_frame()
	Input.action_press("run")
	Input.action_press("move_up")
	var running := await _one_frame()
	Input.action_release("move_up")
	Input.action_release("run")
	await get_tree().physics_frame
	_body.input_enabled = false
	# Con un solo cuadro de aceleración, el primero daría 0 px.
	_check("se mueve en el mismo cuadro de la pulsacion (1 px)",
		first == Vector2(1, 0), "se movio %s" % first)
	_check("se para en el mismo cuadro en que se suelta (0 px)",
		after_release == Vector2.ZERO, "se movio %s" % after_release)
	_check("con Mayus izquierda corre desde el primer cuadro (2 px)",
		running == Vector2(0, -2), "se movio %s" % running)


## Lo que se mueve el cuerpo en un único cuadro de física.
func _one_frame() -> Vector2:
	var before := _body.global_position
	await get_tree().physics_frame
	return _body.global_position - before


func _test_corridors() -> void:
	# Muro horizontal en la fila 4 con un hueco de un tile en la columna 10.
	var wall := "##########.#########"
	await _map(_rows(wall, 4))
	var gap_center := 10 * T + T / 2
	var wall_top := 4 * T
	var passes: Array = []
	var stops: Array = []
	for m in range(-8, 9):
		_place(Vector2i(gap_center + m, 8 * T))
		for _i in 90:
			_step(Vector2i.UP, false)
		if _body.global_position.y <= wall_top:
			passes.append(m)
		else:
			stops.append(m)
	var limit := (T - DesignTokens.PLAYER_HITBOX.x) / 2 + DesignTokens.CORNER_SLIP
	var expected := range(-limit, limit + 1)
	_check("un paso de 16 px se cruza descentrado hasta %d px" % limit,
		passes == expected, "cruza con %s" % [passes])
	_check("descentrado %d px o mas, no se cruza" % (limit + 1),
		stops.has(limit + 1) and stops.has(-limit - 1), "se para con %s" % [stops])

	# Paso de cero tiles: muro entero, de follaje y de agua.
	for material in ["#", "~"]:
		await _map(_rows(material.repeat(20), 4))
		_place(Vector2i(gap_center, 8 * T))
		for _i in 120:
			_step(Vector2i.UP, false)
		var feet := int(_body.global_position.y)
		var gap := feet - DesignTokens.PLAYER_HITBOX.y - (wall_top + T)
		_check("un paso de 0 px nunca se cruza (%s)" % ("follaje" if material == "#" else "agua"),
			feet > wall_top + T, "pies en y %d" % feet)
		_check("y se para tocando el muro, sin hueco (%s)" % ("follaje" if material == "#" else "agua"),
			gap == 0, "hueco de %d px" % gap)


func _test_corners() -> void:
	# Un solo tile de follaje en la columna 10, fila 4. El cuerpo sube con su
	# borde derecho metido `k` px en el canto izquierdo del tile.
	await _map(_single_block(10, 4))
	var block_left := 10 * T
	var block_top := 4 * T
	for run in [false, true]:
		var mode := "corriendo" if run else "andando"
		for k in range(1, DesignTokens.CORNER_SLIP + 2):
			_place(Vector2i(block_left + k - HALF, 8 * T))
			var lateral_ok := true
			var slid := 0
			for _i in 90:
				_step(Vector2i.UP, run)
				if _body.last_step.x != 0:
					slid += absi(_body.last_step.x)
					lateral_ok = lateral_ok and absi(_body.last_step.x) == 1
			var passed := _body.global_position.y <= block_top
			if k <= DesignTokens.CORNER_SLIP:
				_check("esquina a %d px %s: se rodea" % [k, mode], passed and slid == k,
					"pies en y %d, deslizo %d px" % [int(_body.global_position.y), slid])
				_check("  y a 1 px lateral por cuadro", lateral_ok)
			else:
				_check("esquina a %d px %s: se para, sin deslizar" % [k, mode],
					not passed and slid == 0, "deslizo %d px" % slid)


func _test_flat_wall() -> void:
	await _map(_rows("#".repeat(20), 4))
	var wall_bottom := 5 * T
	var touching := wall_bottom + DesignTokens.PLAYER_HITBOX.y
	# Diagonal contra el muro: sigue por el eje libre.
	_place(Vector2i(4 * T, touching))
	var ok := true
	for _i in 30:
		_step(Vector2i(1, -1), false)
		ok = ok and _body.last_step == Vector2i(1, 0)
	_check("diagonal contra pared plana: sigue por el eje libre, 1 px por cuadro", ok,
		"ultimo paso %s" % _body.last_step)
	# Paralelo al muro, tocándolo: el margen de test_move no debe frenarlo.
	_place(Vector2i(4 * T, touching))
	ok = true
	for _i in 30:
		_step(Vector2i.RIGHT, true)
		ok = ok and _body.last_step == Vector2i(2, 0)
	_check("rozando la pared en paralelo no se frena (2 px por cuadro)", ok,
		"ultimo paso %s" % _body.last_step)
	# Recto contra el muro, lejos de cualquier canto: se para y no desliza.
	_place(Vector2i(10 * T, touching))
	ok = true
	for _i in 30:
		_step(Vector2i.UP, false)
		ok = ok and _body.last_step == Vector2i.ZERO
	_check("recto contra pared plana: se para y no desliza", ok,
		"ultimo paso %s" % _body.last_step)


# --- Ayudas ------------------------------------------------------------------


func _step(direction: Vector2i, run: bool) -> void:
	_body.step(direction, run)
	_frames += 1
	if _body.global_position != _body.global_position.round():
		_fractional += 1


func _place(feet: Vector2i) -> void:
	_body.global_position = Vector2(feet)
	_body.last_step = Vector2i.ZERO


## Mapa de 20 x 12 de suelo con `rows` pintadas encima desde la fila 0.
func _map(rows: Array) -> void:
	var lines := PackedStringArray()
	for y in 12:
		lines.append(rows[y] if y < rows.size() else ".".repeat(20))
	_layer.clear()
	WorldTiles.paint(_layer, WorldTiles.parse(lines), func(_c: Vector2i) -> bool: return false)
	# El TileMapLayer crea sus cuerpos de colisión al final del cuadro.
	await get_tree().physics_frame
	await get_tree().physics_frame


func _rows(line: String, at: int) -> Array:
	var rows := []
	for y in at:
		rows.append(".".repeat(20))
	rows.append(line)
	return rows


func _single_block(col: int, row: int) -> Array:
	var line := ".".repeat(col) + "#" + ".".repeat(19 - col)
	return _rows(line, row)


func _check(label: String, condition: bool, detail: String = "") -> void:
	if condition:
		_pass += 1
		print("  OK    %s" % label)
	else:
		_fail += 1
		print("  FALLA %s  (%s)" % [label, detail])
