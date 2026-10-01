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
##
## Paso 3 — el esqueleto: zonas de prueba con dos salidas.
##   - las reglas de salida del contrato se cumplen en las zonas de prueba, y
##     cada regla detecta su incumplimiento en un mapa estropeado a propósito;
##   - al cruzar una salida con la tecla pulsada se llega a la casilla de
##     destino, mirando igual, y se sigue andando sin perder un solo cuadro.
##
## Paso 4 — el resto: límites de la cámara, fundido, rótulo y GameState.
##   - la pantalla nunca enseña fuera de la zona, en ningún cuadro, y un mapa
##     menor que la pantalla se centra;
##   - el fundido dura DUR_ZONE_FADE + DUR_ZONE_FADE, es lineal, el cuerpo se
##     detiene durante el de salida y sigue andando solo durante el de entrada;
##   - con movimiento reducido, corte directo en el mismo cuadro;
##   - el rótulo dice el nombre de la zona, arriba a la izquierda, y entra, se
##     queda PLACE_LABEL_HOLD y se va; con movimiento reducido no se anima,
##     pero la espera se mantiene;
##   - GameState sabe en qué zona se está y hacia dónde se mira.
##
## Paso 5 — la pantalla completa: el sprite.
##   - el cuerpo está en la capa de entidades, ordenada por altura;
##   - el sprite mira hacia donde se anda (en diagonal manda el eje horizontal);
##   - la pose cambia cada STRIDE px recorridos, andando o corriendo, se pone
##     de pie al soltar y no da pasos empujando una pared.
##
## Paso 6 — los estados.
##   - un mapa menor que la pantalla se queda centrado, con bandas ASH_950;
##   - la bandera purified_<zona> de GameState pinta la zona purificada;
##   - las salidas hacia y desde la zona pequeña se cruzan con la tecla pulsada
##     (casos añadidos a «cruzar una salida»).
## El movimiento reducido, el borde del mapa y la salida con la tecla pulsada
## ya se miden en los pasos 3 y 4; la hoja `world_states_sheet.tscn` fuerza
## cada estado para verlo.

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

	print("
=== ESQUELETO: REGLAS DE SALIDA ===")
	_test_exit_rules()

	print("
=== ESQUELETO: CRUZAR UNA SALIDA ===")
	_layer.queue_free()
	_body.queue_free()
	await get_tree().physics_frame
	await _test_crossings()

	print("\n=== RESTO: LIMITES DE LA CAMARA ===")
	await _test_camera_limits()

	print("\n=== RESTO: FUNDIDO Y GAMESTATE ===")
	await _test_fade()

	print("\n=== RESTO: ROTULO DE LUGAR ===")
	await _test_label()

	print("\n=== PANTALLA: SPRITE ===")
	await _test_sprite()

	print("\n=== ESTADOS ===")
	await _test_states()

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


func _test_exit_rules() -> void:
	var exits := ZoneRules.load_exits()
	var zones := {"prueba_a": ZoneRules.load_zone("prueba_a"),
		"prueba_b": ZoneRules.load_zone("prueba_b"),
		"prueba_c": ZoneRules.load_zone("prueba_c")}
	for id in zones:
		var problems := ZoneRules.check(id, zones, exits)
		_check("%s cumple las reglas de salida" % id, problems.is_empty(), "; ".join(problems))

	# Cada regla, contra un mapa estropeado a propósito.
	var open_border := zones.duplicate()
	open_border["prueba_a"] = _edit(zones["prueba_a"], Vector2i(0, 5), ".")
	_expect_problem("un borde pisable que no es salida se detecta",
		ZoneRules.check("prueba_a", open_border, exits), "borde pisable")
	var not_path := zones.duplicate()
	not_path["prueba_a"] = _edit(zones["prueba_a"], Vector2i(39, 9), ".")
	_expect_problem("una salida que no es camino se detecta",
		ZoneRules.check("prueba_a", not_path, exits), "no es camino")
	var crowded := exits.duplicate()
	crowded.append({"from": "prueba_b", "cell": [29, 9], "to": "prueba_a", "to_cell": [38, 9]})
	var crowded_zones := zones.duplicate()
	crowded_zones["prueba_b"] = _edit(zones["prueba_b"], Vector2i(29, 9), "=")
	_expect_problem("tres salidas en una pantalla se detectan",
		ZoneRules.check("prueba_b", crowded_zones, crowded), "salidas en la pantalla")
	var into_water := exits.duplicate(true)
	into_water[0]["to_cell"] = [20, 12]
	_expect_problem("una llegada que no se pisa se detecta",
		ZoneRules.check("prueba_a", zones, into_water), "no se pisa")
	var one_way := exits.filter(func(e): return e["from"] != "prueba_b")
	_expect_problem("una salida sin vuelta se detecta",
		ZoneRules.check("prueba_a", zones, one_way), "de vuelta")


func _test_crossings() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	var cases := [
		["este: prueba_a -> prueba_b", "prueba_a", Vector2i(36, 9), "move_right",
			"prueba_b", Vector2i(1, 8), Vector2i.RIGHT],
		["sur: prueba_a -> prueba_b", "prueba_a", Vector2i(12, 16), "move_down",
			"prueba_b", Vector2i(15, 1), Vector2i.DOWN],
		["oeste: prueba_b -> prueba_a", "prueba_b", Vector2i(3, 8), "move_left",
			"prueba_a", Vector2i(38, 9), Vector2i.LEFT],
		["norte: prueba_b -> prueba_a", "prueba_b", Vector2i(15, 3), "move_up",
			"prueba_a", Vector2i(12, 18), Vector2i.UP],
		["norte: prueba_a -> prueba_c (menor que la pantalla)", "prueba_a", Vector2i(25, 4), "move_up",
			"prueba_c", Vector2i(10, 8), Vector2i.UP],
		["sur: prueba_c -> prueba_a", "prueba_c", Vector2i(10, 6), "move_down",
			"prueba_a", Vector2i(25, 1), Vector2i.DOWN],
	]
	for c in cases:
		world.enter_zone(c[1], c[2])
		await get_tree().physics_frame
		await get_tree().physics_frame
		Input.action_press(c[3])
		var arrived_at := Vector2i(-1, -1)
		var frames := 0
		while world.zone_id == c[1] and frames < 200:
			await get_tree().physics_frame
			frames += 1
			_count_frame(world.body)
		arrived_at = Vector2i(world.body.global_position)
		# Tras llegar, la tecla sigue pulsada: el cuerpo tiene que seguir
		# andando en cada cuadro, sin uno solo parado.
		var steady := true
		for _i in 20:
			var before := world.body.global_position
			await get_tree().physics_frame
			_count_frame(world.body)
			steady = steady and (world.body.global_position - before) == Vector2(c[6])
		Input.action_release(c[3])
		await get_tree().physics_frame
		var feet := WorldRoot.feet_of(c[5])
		# `WorldRoot` decide la salida después del paso del cuerpo, así que en el
		# cuadro del cambio los pies están exactamente en la casilla de destino.
		var off := arrived_at - feet
		_check("%s: llega a %s" % [c[0], c[4]], world.zone_id == c[4],
			"sigue en %s tras %d cuadros" % [world.zone_id, frames])
		_check("  aparece en la casilla de destino %s" % [c[5]],
			off == Vector2i.ZERO, "pies en %s, esperados %s" % [arrived_at, feet])
		_check("  mira igual al llegar", world.body.facing == c[6], "mira %s" % world.body.facing)
		_check("  con la tecla pulsada sigue andando, 1 px en cada cuadro", steady)
	world.queue_free()


func _test_camera_limits() -> void:
	# Un mapa menor que la pantalla se centra en ese eje.
	var cam := WorldCamera.new()
	var dot := Node2D.new()
	add_child(dot)
	cam.target = dot
	add_child(cam)
	cam.limits = Rect2i(0, 0, 320, 160)
	dot.position = Vector2(30, 40)
	cam.snap_to_target()
	var still := cam.center
	dot.position = Vector2(300, 150)
	for _i in 60:
		cam.advance()
	_check("un mapa menor que la pantalla se centra (320x160 -> centro 160,80)",
		still == Vector2i(160, 80) and cam.center == Vector2i(160, 80),
		"centro %s y luego %s" % [still, cam.center])
	cam.queue_free()
	dot.queue_free()

	# Recorrido hacia las cuatro esquinas de cada zona, corriendo.
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	world.camera.set_physics_process(false)
	world.body.input_enabled = false
	var outside := 0
	var frames := 0
	var outside_deadzone := 0
	for zone in ["prueba_a", "prueba_b"]:
		for dir in [Vector2i(-1, -1), Vector2i(1, -1), Vector2i(1, 1), Vector2i(-1, 1)]:
			world.enter_zone(zone, Vector2i(5, 8) if zone == "prueba_a" else Vector2i(10, 9))
			await get_tree().physics_frame
			for _i in 160:
				world.body.step(dir, true)
				world.camera.advance()
				frames += 1
				var map := Rect2i(Vector2i.ZERO, world.zone_size * T)
				if not map.encloses(world.camera.visible_rect()):
					outside += 1
				# La zona muerta cuenta sus dos bordes como dentro (WorldCamera.deadzone).
				var dz := world.camera.deadzone()
				if not Rect2i(dz.position, dz.size + Vector2i.ONE).has_point(
						Vector2i(world.body.global_position)):
					outside_deadzone += 1
	_check("hacia las esquinas la pantalla nunca sale de la zona (%d cuadros)" % frames,
		outside == 0, "%d cuadros enseñan fuera" % outside)
	# El contrato lo admite y la prueba lo distingue: junto al borde el cuerpo
	# sale de la zona muerta. Si nunca saliera, los límites no estarían actuando.
	_check("  y junto al borde el cuerpo sale de la zona muerta, como admite el contrato",
		outside_deadzone > 0, "nunca sale")
	world.queue_free()
	await get_tree().physics_frame


func _test_fade() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	var ticks := Engine.physics_ticks_per_second
	var expected := roundi(DesignTokens.DUR_ZONE_FADE * ticks)

	for reduced in [false, true]:
		DesignTokens.reduced_motion = reduced
		world.enter_zone("prueba_a", Vector2i(37, 9))
		await get_tree().physics_frame
		await get_tree().physics_frame
		Input.action_press("move_right")
		var alphas := []
		var phases := []
		var still_while_out := 0
		var moving_while_in := 0
		var camera_out := 0
		var cross_frame := -1
		var swap_frame := -1
		for f in 60:
			var before := world.body.global_position
			var zone_before := world.zone_id
			await get_tree().physics_frame
			var map := Rect2i(Vector2i.ZERO, world.zone_size * T)
			if not map.encloses(world.camera.visible_rect()):
				camera_out += 1
			phases.append(world.fade)
			alphas.append(world.curtain.modulate.a)
			if cross_frame < 0 and (world.fade != WorldRoot.Fade.NONE or world.zone_id != zone_before):
				cross_frame = f
			if swap_frame < 0 and world.zone_id != zone_before:
				swap_frame = f
			# El cuadro del cruce cuenta ya como fundido, pero en él el cuerpo sí
			# avanzó: ese paso es el que lo sacó del mapa. Se mide desde el siguiente.
			if world.fade == WorldRoot.Fade.OUT and f != cross_frame 					and world.body.global_position == before:
				still_while_out += 1
			if world.fade == WorldRoot.Fade.IN and world.body.global_position != before:
				moving_while_in += 1
		Input.action_release("move_right")
		await get_tree().physics_frame
		var outs := phases.count(WorldRoot.Fade.OUT)
		var ins := phases.count(WorldRoot.Fade.IN)
		var state := get_node("/root/GameState")
		if not reduced:
			var ms := 1000.0 / ticks
			_check("fundido de salida: %d cuadros (%.0f ms; contrato %d ms)" % [
				expected, expected * ms, roundi(DesignTokens.DUR_ZONE_FADE * 1000)],
				swap_frame - cross_frame == expected,
				"el cambio llega %d cuadros tras cruzar" % (swap_frame - cross_frame))
			_check("fundido de entrada: %d cuadros" % expected, ins == expected,
				"%d cuadros en IN" % ins)
			var out_alphas := alphas.slice(cross_frame + 1, swap_frame + 1)
			var linear := out_alphas.size() == expected
			for i in out_alphas.size():
				linear = linear and is_equal_approx(out_alphas[i], float(i + 1) / expected)
			_check("  lineal, y la zona cambia con la pantalla cubierta (opacidad 1)",
				linear, "opacidades %s" % [out_alphas])
			_check("  el cuerpo se detiene durante el fundido de salida, tras el paso que cruza",
				still_while_out == outs - 1, "%d de %d cuadros quieto" % [still_while_out, outs - 1])
			_check("  y con la tecla pulsada anda durante el de entrada, sin soltarla",
				moving_while_in == ins, "%d de %d cuadros andando" % [moving_while_in, ins])
			_check("  al acabar, la cortina queda transparente", alphas.back() == 0.0)
		else:
			_check("movimiento reducido: corte directo, la zona cambia en el cuadro de cruzar",
				swap_frame >= 0 and swap_frame == cross_frame,
				"cruza %d, cambia %d" % [cross_frame, swap_frame])
			_check("  sin un solo cuadro de cortina",
				alphas.max() == 0.0 and outs == 0 and ins == 0, "opacidad maxima %s" % alphas.max())
		_check("  la pantalla nunca enseña fuera de la zona al cruzar", camera_out == 0,
			"%d cuadros" % camera_out)
		_check("  GameState sabe la zona y hacia donde se mira",
			state.zone_id == "prueba_b" and state.facing == Vector2i.RIGHT,
			"%s mirando %s" % [state.zone_id, state.facing])
	DesignTokens.reduced_motion = false
	world.queue_free()
	await get_tree().physics_frame


func _test_label() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	var ticks := Engine.physics_ticks_per_second
	var in_frames := roundi(DesignTokens.DUR_PLACE_LABEL * ticks)
	var hold := roundi(DesignTokens.PLACE_LABEL_HOLD * ticks)
	for reduced in [false, true]:
		DesignTokens.reduced_motion = reduced
		world.enter_zone("prueba_b", Vector2i(10, 9))
		var lbl := world.label
		var phases := []
		var alphas := []
		for _i in in_frames * 2 + hold + 10:
			phases.append(lbl.phase)
			alphas.append(lbl.modulate.a)
			await get_tree().physics_frame
		var ins := phases.count(PlaceLabel.Phase.IN)
		var holds := phases.count(PlaceLabel.Phase.HOLD)
		var outs := phases.count(PlaceLabel.Phase.OUT)
		if not reduced:
			_check("rotulo: dice el nombre de la zona", lbl.text == "Ribera de prueba", lbl.text)
			_check("  arriba a la izquierda, margen SPACE_8",
				lbl.panel_rect().position == Vector2i(DesignTokens.SPACE_8, DesignTokens.SPACE_8),
				"%s" % lbl.panel_rect())
			var first_step: float = alphas[1] - alphas[0]
			var last_step: float = alphas[in_frames] - alphas[in_frames - 1]
			_check("  entra en %d cuadros (%d ms; contrato %d ms)" % [
				in_frames, roundi(in_frames * 1000.0 / ticks), roundi(DesignTokens.DUR_PLACE_LABEL * 1000)],
				ins == in_frames and alphas[in_frames] == 1.0,
				"%d cuadros en IN; opacidades %s" % [ins, alphas.slice(0, in_frames + 1)])
			_check("  con curva de salida: el primer cuadro sube mas que el ultimo",
				first_step > last_step, "primero %.3f, ultimo %.3f" % [first_step, last_step])
			_check("  se queda %d cuadros (%.1f s)" % [hold, DesignTokens.PLACE_LABEL_HOLD],
				holds == hold, "%d cuadros" % holds)
			_check("  y se va solo en %d cuadros" % in_frames,
				outs == in_frames and alphas.back() == 0.0, "%d cuadros en OUT" % outs)
		else:
			_check("rotulo con movimiento reducido: entra de golpe, sin animarse",
				ins == 0 and outs == 0 and alphas[0] == 1.0, "%d IN, %d OUT" % [ins, outs])
			_check("  pero la espera de %.1f s se mantiene" % DesignTokens.PLACE_LABEL_HOLD,
				holds == hold and alphas.back() == 0.0, "%d cuadros de espera" % holds)
	DesignTokens.reduced_motion = false
	world.queue_free()
	await get_tree().physics_frame


func _test_sprite() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	world.body.input_enabled = false
	world.body.set_physics_process(false)
	var b := world.body

	_check("el cuerpo esta en la capa de entidades, ordenada por altura",
		b.get_parent() == world.entities and world.entities.y_sort_enabled)

	var rows := {
		"abajo": [Vector2i.DOWN, PlayerBody.ROW_DOWN],
		"arriba": [Vector2i.UP, PlayerBody.ROW_UP],
		"izquierda": [Vector2i.LEFT, PlayerBody.ROW_LEFT],
		"derecha": [Vector2i.RIGHT, PlayerBody.ROW_RIGHT],
		"diagonal arriba-derecha (manda el eje horizontal)": [Vector2i(1, -1), PlayerBody.ROW_RIGHT],
	}
	var rows_ok := true
	var bad := []
	for label in rows:
		world.enter_zone("prueba_a", Vector2i(10, 6))
		b.step(rows[label][0], false)
		if b.sprite_row != rows[label][1]:
			rows_ok = false
			bad.append(label)
	_check("el sprite mira hacia donde se anda, en las 4 orientaciones y en diagonal",
		rows_ok, "falla en %s" % [bad])

	# Andando: la pose cambia exactamente a los 8, 16 y 24 px recorridos,
	# echando a andar desde parado.
	world.enter_zone("prueba_a", Vector2i(5, 9))
	b.step(Vector2i.ZERO, false)
	var changes := []
	var last := b.pose
	for f in range(1, 33):
		b.step(Vector2i.RIGHT, false)
		if b.pose != last:
			changes.append(f)
			last = b.pose
	_check("andando, la pose cambia cada %d px (a los 8, 16, 24 y 32)" % PlayerBody.STRIDE,
		changes == [8, 16, 24, 32], "cambia en los cuadros %s" % [changes])

	# Corriendo: la misma distancia en la mitad de cuadros.
	world.enter_zone("prueba_a", Vector2i(5, 9))
	b.step(Vector2i.ZERO, false)
	changes = []
	last = b.pose
	for f in range(1, 17):
		b.step(Vector2i.RIGHT, true)
		if b.pose != last:
			changes.append(f)
			last = b.pose
	_check("corriendo, cambia cada 4 cuadros (la misma distancia)",
		changes == [4, 8, 12, 16], "cambia en los cuadros %s" % [changes])

	# Al parar, de pie en ese mismo cuadro.
	for _i in 9:
		b.step(Vector2i.RIGHT, false)
	b.step(Vector2i.ZERO, false)
	_check("al soltar, de pie en el mismo cuadro", b.pose == 0, "pose %d" % b.pose)

	# Empujando una pared: primero se llega a tocarla; desde ahí el cuerpo no
	# avanza y el sprite no da pasos.
	world.enter_zone("prueba_a", Vector2i(10, 1))
	for _i in 20:
		b.step(Vector2i.UP, false)
	var poses := []
	for _i in 40:
		b.step(Vector2i.UP, false)
		poses.append(b.pose)
	_check("empujando una pared no da pasos: se distingue de andar",
		poses.count(0) == poses.size() and b.last_step == Vector2i.ZERO,
		"poses %s, ultimo paso %s" % [poses.slice(0, 12), b.last_step])

	world.queue_free()
	await get_tree().physics_frame


func _test_states() -> void:
	var world := WorldRoot.new()
	add_child(world)
	await get_tree().physics_frame
	world.body.input_enabled = false
	var state := get_node("/root/GameState")

	# Mapa menor que la pantalla en los dos ejes: se centra, y lo que queda
	# alrededor es ASH_950, las bandas del viewport.
	world.enter_zone("prueba_c", Vector2i(10, 8))
	var map := Rect2i(Vector2i.ZERO, world.zone_size * T)
	for dir in [Vector2i(-1, -1), Vector2i(1, -1), Vector2i(1, 1)]:
		for _i in 60:
			world.body.step(dir, true)
			world.camera.advance()
	_check("mapa menor que la pantalla (%dx%d): la camara se queda centrada" % [map.size.x, map.size.y],
		world.camera.center == map.get_center(), "centro %s, mapa %s" % [world.camera.center, map])
	_check("  y las bandas de alrededor son ASH_950, no el gris de Godot",
		RenderingServer.get_default_clear_color() == DesignTokens.ASH_950,
		"%s" % RenderingServer.get_default_clear_color())

	# Bandera de zona purificada: el mundo pinta el estado que dice GameState.
	var flora_cell := Vector2i(5, 12)  # follaje de prueba_b
	state.set_zone_purified("prueba_b", false)
	world.enter_zone("prueba_b", Vector2i(10, 9))
	var sick_row: int = world._layer.get_cell_atlas_coords(flora_cell).y
	state.set_zone_purified("prueba_b", true)
	world.enter_zone("prueba_b", Vector2i(10, 9))
	var pure_row: int = world._layer.get_cell_atlas_coords(flora_cell).y
	state.set_zone_purified("prueba_b", false)
	var flora_row: int = WorldTiles.OVERLAY_ROW[WorldTiles.Terrain.FLORA]
	_check("sin bandera, la zona se pinta enferma; con purified_<zona>, purificada",
		sick_row == flora_row and pure_row == flora_row + 1,
		"fila enferma %d, purificada %d" % [sick_row, pure_row])

	world.queue_free()
	await get_tree().physics_frame


func _count_frame(body: Node2D) -> void:
	_frames += 1
	if body.global_position != body.global_position.round():
		_fractional += 1


func _expect_problem(label: String, problems: PackedStringArray, needle: String) -> void:
	var found := false
	for p in problems:
		found = found or needle in p
	_check(label, found, "problemas: %s" % "; ".join(problems))


func _edit(lines: PackedStringArray, cell: Vector2i, ch: String) -> PackedStringArray:
	var out := lines.duplicate()
	var row := out[cell.y]
	out[cell.y] = row.substr(0, cell.x) + ch + row.substr(cell.x + 1)
	return out


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
