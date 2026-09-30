extends Node2D

## Paso 3 del contrato «Vereda»: la cámara del mundo, medida cuadro a cuadro.
##
## Mueve al personaje 600 cuadros en las ocho direcciones, andando y corriendo,
## y FALLA si en algún cuadro la posición de la cámara o la del personaje no es
## entera, si el personaje sale de la zona muerta, o si la anticipación se sale
## de su tope o de su ritmo (enmienda 5).
##   godot --headless --path . res://tools/verify_camera.tscn

const FRAMES := 600
const STOP_FRAMES := 90

const DIRECTIONS := {
	"norte": Vector2i(0, -1), "noreste": Vector2i(1, -1),
	"este": Vector2i(1, 0), "sureste": Vector2i(1, 1),
	"sur": Vector2i(0, 1), "suroeste": Vector2i(-1, 1),
	"oeste": Vector2i(-1, 0), "noroeste": Vector2i(-1, -1),
}

var _walker: Node2D = null
var _camera: WorldCamera = null
var _pass: int = 0
var _fail: int = 0


## El personaje de prueba: avanza un número entero de píxeles por cuadro, como
## pide la cláusula «Movimiento del personaje». Por eje, sin normalizar la
## diagonal (enmienda 4).
class Walker extends Node2D:
	var step := Vector2i.ZERO

	func _physics_process(_delta: float) -> void:
		position += Vector2(step)


func _ready() -> void:
	_walker = Walker.new()
	add_child(_walker)
	_camera = WorldCamera.new()
	_camera.target = _walker
	add_child(_camera)
	_camera.set_physics_process(false)
	_walker.set_physics_process(false)

	print("\n=== PROYECTO ===")
	_test_project()
	print("\n=== SESGO Y ZONA MUERTA ===")
	_test_deadzone()
	print("\n=== %d CUADROS EN LAS OCHO DIRECCIONES ===" % FRAMES)
	_test_directions()
	print("\n=== ANTICIPACIÓN (enmienda 5) ===")
	_test_lookahead()
	print("\n=== MOVIMIENTO REDUCIDO ===")
	_test_reduced_motion()
	print("\n=== EN EL MOTOR, CON EL RELOJ REAL ===")
	await _test_engine()

	print("\n%d comprobaciones superadas, %d fallidas." % [_pass, _fail])
	get_tree().quit(0 if _fail == 0 else 1)


func _check(label: String, condition: bool, detail: String = "") -> void:
	if condition:
		_pass += 1
		print("  OK    %s %s" % [label, detail])
	else:
		_fail += 1
		printerr("  FALLA %s %s" % [label, detail])


func _px_per_tick(speed: float) -> int:
	return int(speed) / Engine.physics_ticks_per_second


func _reset() -> void:
	_walker.position = Vector2.ZERO
	_camera.snap_to_target()


## Un cuadro a mano: primero se mueve el personaje y luego la cámara, el mismo
## orden que imponen las prioridades de proceso en el juego.
func _tick(step: Vector2i) -> void:
	_walker.position += Vector2(step)
	_camera.advance()


func _is_whole(v: Vector2) -> bool:
	return v == v.round()


func _test_project() -> void:
	_check("ajuste a píxel de transformaciones activo (enmienda 2)",
		bool(ProjectSettings.get_setting("rendering/2d/snap/snap_2d_transforms_to_pixel", false)))
	_check("ajuste a píxel de vértices activo (enmienda 2)",
		bool(ProjectSettings.get_setting("rendering/2d/snap/snap_2d_vertices_to_pixel", false)))
	_check("física a 60 Hz", Engine.physics_ticks_per_second == 60,
		"(%d)" % Engine.physics_ticks_per_second)
	for pair in [["andar", DesignTokens.WALK_SPEED], ["correr", DesignTokens.RUN_SPEED]]:
		var per_tick: float = pair[1] / Engine.physics_ticks_per_second
		_check("%s avanza píxeles enteros por cuadro" % pair[0],
			per_tick == floorf(per_tick), "(%.2f px)" % per_tick)
	_check("la cámara no usa el suavizado ni el arrastre de Godot",
		not _camera.position_smoothing_enabled
		and not _camera.drag_horizontal_enabled and not _camera.drag_vertical_enabled)


func _test_deadzone() -> void:
	_reset()
	var offset := Vector2i(_walker.position) - _camera.center
	_check("en reposo, el personaje queda 12 px bajo el centro", offset == Vector2i(0, 12),
		"(%s)" % offset)
	var zone := _camera.deadzone()
	_check("la zona muerta mide 28 x 48 px", zone.size == Vector2i(28, 48), "(%s)" % zone.size)
	_check("en reposo, el personaje está en el centro de la zona",
		zone.get_center() == Vector2i(_walker.position))

	# Andando, la anticipación abre 1 px por cuadro y el personaje avanza otro:
	# se acerca al borde a 2 px por cuadro. Holgura de 14 px en X y 24 en Y.
	for case in [["este", Vector2i(1, 0), 7], ["norte", Vector2i(0, -1), 12]]:
		_reset()
		var start := _camera.center
		var still := 0
		for _i in 40:
			_tick(case[1])
			if _camera.center != start:
				break
			still += 1
		_check("hacia el %s, la cámara espera %d cuadros antes de seguir" % [case[0], case[2]],
			still == case[2], "(esperó %d)" % still)


func _test_directions() -> void:
	for speed_case in [["andar", DesignTokens.WALK_SPEED], ["correr", DesignTokens.RUN_SPEED]]:
		var px := _px_per_tick(speed_case[1])
		for name in DIRECTIONS:
			_reset()
			var step: Vector2i = DIRECTIONS[name] * px
			var errors := {"cámara": 0, "personaje": 0, "zona": 0, "tope": 0, "ritmo": 0, "salto": 0}
			var worst_jump := 0
			for frame in FRAMES + STOP_FRAMES:
				var before_center := _camera.center
				var before_look := _camera.lookahead
				_tick(step if frame < FRAMES else Vector2i.ZERO)
				if not _is_whole(_camera.global_position) or Vector2(_camera.center) != _camera.global_position:
					errors["cámara"] += 1
				if not _is_whole(_walker.global_position):
					errors["personaje"] += 1
				var p := Vector2i(_walker.position)
				var zone := _camera.deadzone()
				if p.x < zone.position.x or p.x > zone.end.x or p.y < zone.position.y or p.y > zone.end.y:
					errors["zona"] += 1
				if absi(_camera.lookahead.x) > DesignTokens.CAMERA_LOOKAHEAD or absi(_camera.lookahead.y) > DesignTokens.CAMERA_LOOKAHEAD:
					errors["tope"] += 1
				var look_delta := (_camera.lookahead - before_look).abs()
				if look_delta.x > 1 or look_delta.y > 1:
					errors["ritmo"] += 1
				var jump := (_camera.center - before_center).abs()
				worst_jump = maxi(worst_jump, maxi(jump.x, jump.y))
				if jump.x > px + 1 or jump.y > px + 1:
					errors["salto"] += 1
			var bad := []
			for key in errors:
				if errors[key] > 0:
					bad.append("%s en %d cuadros" % [key, errors[key]])
			_check("%-7s %-9s" % [speed_case[0], name], bad.is_empty(),
				"(salto máx. %d px/cuadro)" % worst_jump if bad.is_empty() else "— " + ", ".join(bad))


func _test_lookahead() -> void:
	_reset()
	var opened_at := -1
	for frame in 60:
		_tick(Vector2i(1, 0))
		if opened_at < 0 and _camera.lookahead.x == DesignTokens.CAMERA_LOOKAHEAD:
			opened_at = frame + 1
	_check("abre hasta 30 px en 30 cuadros (60 px/s)", opened_at == 30, "(%d cuadros)" % opened_at)
	_check("no pasa del tope", _camera.lookahead.x == DesignTokens.CAMERA_LOOKAHEAD)
	_check("el eje que no se mueve no anticipa", _camera.lookahead.y == 0)

	var closed_at := -1
	for frame in 120:
		_tick(Vector2i.ZERO)
		if _camera.lookahead.x == 0:
			closed_at = frame + 1
			break
	_check("al parar vuelve a neutro en 60 cuadros (30 px/s)", closed_at == 60, "(%d cuadros)" % closed_at)

	_reset()
	for _i in 60:
		_tick(Vector2i(-1, -1))
	_check("en diagonal anticipa en los dos ejes",
		_camera.lookahead == Vector2i(-30, -30), "(%s)" % _camera.lookahead)

	# Cambiar de sentido no salta: la anticipación cruza por cero a su ritmo.
	var before := _camera.lookahead.x
	_tick(Vector2i(1, 0))
	_check("al dar la vuelta, la anticipación se desplaza 1 px, no salta",
		absi(_camera.lookahead.x - before) == 1, "(%d → %d)" % [before, _camera.lookahead.x])


func _test_reduced_motion() -> void:
	var saved := DesignTokens.reduced_motion
	DesignTokens.reduced_motion = true
	_reset()
	var max_look := 0
	var outside := 0
	for _i in FRAMES:
		_tick(Vector2i(1, -1))
		max_look = maxi(max_look, maxi(absi(_camera.lookahead.x), absi(_camera.lookahead.y)))
		var zone := _camera.deadzone()
		var p := Vector2i(_walker.position)
		if p.x < zone.position.x or p.x > zone.end.x or p.y < zone.position.y or p.y > zone.end.y:
			outside += 1
	_check("sin anticipación", max_look == 0, "(máx. %d px)" % max_look)
	_check("la zona muerta se sigue cumpliendo", outside == 0, "(%d cuadros fuera)" % outside)
	DesignTokens.reduced_motion = saved


func _test_engine() -> void:
	_reset()
	_walker.step = Vector2i(1, -1) * _px_per_tick(DesignTokens.WALK_SPEED)
	_camera.make_current()
	_walker.set_physics_process(true)
	_camera.set_physics_process(true)
	var frames := 0
	var fractional := 0
	var mismatched := 0
	for _i in 120:
		await get_tree().physics_frame
		await get_tree().process_frame
		frames += 1
		var screen := _camera.get_screen_center_position()
		if not _is_whole(screen) or not _is_whole(_walker.global_position):
			fractional += 1
		if screen != Vector2(_camera.center):
			mismatched += 1
	_walker.set_physics_process(false)
	_camera.set_physics_process(false)
	_check("el centro de pantalla del motor siempre es entero", fractional == 0,
		"(%d de %d cuadros con subpíxel)" % [fractional, frames])
	_check("y coincide con la cuenta de la cámara", mismatched == 0,
		"(%d de %d cuadros distintos)" % [mismatched, frames])
