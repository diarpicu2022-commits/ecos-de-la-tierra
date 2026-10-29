extends Node

## La ola de purificación, medida sobre el render (enmienda 3, contrato
## «Persiana» paso 6):
##
##   godot --path . res://tools/verify_wave.tscn
##
## En el Bosque, desde la casilla de la Llama:
## - dura DUR_ZONE_PURIFY (54 cuadros);
## - en cada cuadro, todo píxel del suelo es el enfermo o el purificado de ese
##   mismo sitio: nunca una mezcla, nunca un tono nuevo. Se mide sin decorado
##   ni agua animada (la capa de entidades oculta y las referencias quietas):
##   el decorado cambia de estado al final de la ola, no con ella;
## - lo purificado crece cuadro a cuadro y nunca vuelve atrás;
## - cada pieza de decorado pasa a purificada en el cuadro en que el frente
##   llega a su pie, ni antes ni después;
## - a media ola, cerca del origen hay más purificado que lejos;
## - con movimiento reducido, de golpe.
## Captura a media ola: docs/ux/capturas/2026-10-28-ola-bosque.png.
## Sale con código 1 si algo falla.

const ZONE := "ashen_forest"
const OUT := "res://docs/ux/capturas/2026-10-28-ola-bosque.png"

var _pass := 0
var _fail := 0


func _ready() -> void:
	var state := get_node("/root/GameState")
	state.flags.clear()
	var world := WorldRoot.new()
	world.start_zone = ZONE
	world.start_cell = Vector2i(52, 22)
	add_child(world)
	await get_tree().physics_frame
	world.body.input_enabled = false
	world.label.visible = false
	var origin: Vector2i = world.monster.cell
	world.monster.queue_free()
	world.solids.get_node("solid_" + world.monster.name).queue_free()
	world.monster = null
	world.entities.visible = false
	DesignTokens.reduced_motion = true
	for _i in 4:
		await get_tree().physics_frame
	var sick := await _frame()
	# Referencia purificada: la misma vista con la zona purificada.
	state.set_zone_purified(ZONE)
	world.enter_zone(ZONE, world.start_cell)
	world.label.visible = false
	world.entities.visible = false
	for _i in 4:
		await get_tree().physics_frame
	var pure := await _frame()
	state.flags.clear()
	world.enter_zone(ZONE, world.start_cell)
	world.label.visible = false
	world.monster.queue_free()
	world.solids.get_node("solid_" + world.monster.name).queue_free()
	world.monster = null
	world.entities.visible = false
	for _i in 4:
		await get_tree().physics_frame

	print("Ola de purificación")
	DesignTokens.reduced_motion = false
	var first := Engine.get_physics_frames()
	world.purify_wave(origin)
	var frames := 0
	var checked := 0
	var late := 0
	var mixed := 0
	var shrank := false
	var prev_pure := -1
	var near_far := Vector2.ZERO
	var xf := get_viewport().get_canvas_transform()
	var o := xf * Vector2(origin * DesignTokens.TILE_SIZE + Vector2i(8, 8))
	while world.wave_radius >= 0.0 and frames < 200:
		var img := await _frame()
		frames += 1
		if world.wave_radius < 0.0:
			break
		# Pieza a pieza: purificada si y solo si el frente ya llegó a su pie.
		var wo := Vector2(origin * DesignTokens.TILE_SIZE + Vector2i(8, 8))
		for child in world.entities.get_children():
			if child is Sprite2D and child.has_meta("decor_id"):
				checked += 1
				if bool(child.get_meta("pure")) != (wo.distance_to(child.position) <= world.wave_radius):
					late += 1
		var count := 0
		var near := Vector2.ZERO
		var far := Vector2.ZERO
		for y in range(0, img.get_height(), 2):
			for x in range(0, img.get_width(), 2):
				var c := img.get_pixel(x, y)
				var a := sick.get_pixel(x, y)
				var b := pure.get_pixel(x, y)
				if a == b:
					continue
				var is_pure := c == b
				if c != a and not is_pure:
					mixed += 1
				count += int(is_pure)
				var d := o.distance_to(Vector2(x, y))
				if d < 120:
					near += Vector2(int(is_pure), 1)
				elif d > 200:
					far += Vector2(int(is_pure), 1)
		if count < prev_pure:
			shrank = true
		prev_pure = count
		if frames == 20:
			near_far = Vector2(near.x / maxf(near.y, 1), far.x / maxf(far.y, 1))
	var physics := Engine.get_physics_frames() - first
	var expected := roundi(DesignTokens.DUR_ZONE_PURIFY * 60)
	_check("dura %d cuadros de física (%d esperados)" % [physics, expected], absi(physics - expected) <= 1)
	_check("ningún píxel mezclado: cada uno es el enfermo o el purificado de su sitio (%d fuera)" % mixed,
		mixed == 0)
	_check("lo purificado crece y nunca vuelve atrás", not shrank)
	_check("el decorado vuelve pieza a pieza al paso del frente (%d desfases en %d comprobaciones)" % [
		late, checked], late == 0 and checked > 0)
	_check("a media ola, cerca del origen más purificado que lejos (%.0f %% frente a %.0f %%)" % [
		near_far.x * 100, near_far.y * 100], near_far.x > near_far.y)
	_check("al terminar, la zona queda purificada y montada", state.is_zone_purified(ZONE))
	# Movimiento reducido.
	state.flags.clear()
	world.enter_zone(ZONE, world.start_cell)
	DesignTokens.reduced_motion = true
	var start := Engine.get_physics_frames()
	await world.purify_wave(origin)
	_check("con movimiento reducido, de golpe (%d cuadros)" % (Engine.get_physics_frames() - start),
		Engine.get_physics_frames() - start == 0 and state.is_zone_purified(ZONE))
	DesignTokens.reduced_motion = false
	# Captura a media ola, ya con decorado: es lo que ve el jugador.
	state.flags.clear()
	world.enter_zone(ZONE, world.start_cell)
	world.label.visible = false
	world.entities.visible = true
	world.monster.queue_free()
	world.solids.get_node("solid_" + world.monster.name).queue_free()
	world.monster = null
	for _i in 4:
		await get_tree().physics_frame
	world.purify_wave(origin)
	for _i in 24:
		await get_tree().physics_frame
	(await _frame()).save_png(ProjectSettings.globalize_path(OUT))
	while world.wave_radius >= 0.0:
		await get_tree().physics_frame
	state.flags.clear()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _frame() -> Image:
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
