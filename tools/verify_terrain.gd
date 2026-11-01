extends Node

## El suelo de Tierra Viva en el motor (contrato «Piel nueva», paso 2), a
## 640 × 360 y con ventana:
##
##   godot --path . res://tools/verify_terrain.tscn -- [zona]
##
## Sin argumento, el Bosque (`ashen_forest`).
## - **Montaje:** existen los dos sprites del suelo, miden la zona (casillas ×
##   16) y están en el origen; la capa de tiles queda oculta.
## - **Colisión desde la matriz:** empujando contra el follaje durante 60
##   cuadros, Ilan no entra en ninguna casilla sólida.
## - **Se ve lo que se generó:** con el decorado e Ilan ocultos,
##   cada píxel de la pantalla es exactamente el píxel del PNG en esa posición
##   del mundo: sin filtro, sin escala y sin desfase. Las capturas se hacen
##   después, con todo visible (el decorado todavía es el viejo: paso 4).
## - **Estado:** enferma, se ve el enfermo; purificada, el sano.
## - **Ola:** a mitad de la ola, cada píxel visible del suelo es enfermo o
##   sano, nunca una mezcla, y hay de los dos.
## Capturas: docs/ux/capturas/2026-10-31-terreno-<zona>-{enfermo,ola,sano}.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/2026-10-31-terreno-%s-%s.png"
const MATCH_MIN := 1.0

## Casilla de cada zona desde la que se mira (junto al puente en el Bosque) y
## casilla de suelo con follaje al norte para la prueba de colisión.
const SPOT := {"ashen_forest": [Vector2i(44, 15), Vector2i(20, 11)]}

var _pass := 0
var _fail := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0] if args.size() > 0 else "ashen_forest"
	var state := get_node("/root/GameState")
	state.flags.clear()
	state.set_zone_purified(zone, false)
	DesignTokens.reduced_motion = false
	var world := WorldRoot.new()
	world.start_zone = zone
	world.start_cell = SPOT[zone][0]
	add_child(world)
	await get_tree().physics_frame
	world.label.visible = false
	if world.monster != null:
		world.monster.active = false

	print("Montaje")
	var sick := world.terrain_sick
	var pure := world.terrain_pure
	var size := world.zone_size * DesignTokens.TILE_SIZE
	_check("hay suelo enfermo y sano", sick != null and pure != null)
	if sick == null or pure == null:
		return _end()
	_check("miden la zona (%s) y están en el origen" % size,
		Vector2i(sick.texture.get_size()) == size and Vector2i(pure.texture.get_size()) == size
		and sick.position == Vector2.ZERO and pure.position == Vector2.ZERO and not sick.centered)
	_check("la capa de tiles queda oculta", not world._layer.visible)
	var sick_img := sick.texture.get_image()
	var pure_img := pure.texture.get_image()

	print("\nColisión desde la matriz")
	world.enter_zone(zone, SPOT[zone][1])
	await get_tree().physics_frame
	var lines := ZoneRules.load_zone(zone)
	var entered := 0
	for i in 60:
		world.body.step(Vector2i.UP, false)
		await get_tree().physics_frame
		var c := MapMonster.cell_of(Vector2i(world.body.global_position))
		if not ZoneRules.walkable(lines[c.y][c.x]):
			entered += 1
	_check("empujando al follaje 60 cuadros, ninguna casilla sólida pisada (%d)" % entered, entered == 0)

	print("\nEstado")
	world.enter_zone(zone, SPOT[zone][0])
	world.label.visible = false
	await _settle()
	var shot := await _bare(world)
	var m := _match(shot, world, sick_img)
	_check("enferma: se ve el enfermo en el %.0f %% de la pantalla (≥ %.0f %%)" % [m * 100, MATCH_MIN * 100],
		m >= MATCH_MIN and not world.terrain_pure.visible)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [zone, "enfermo"]))

	print("\nOla")
	var origin: Vector2i = SPOT[zone][0] + Vector2i(2, 0)
	world.purify_wave(origin)
	var frames := roundi(DesignTokens.DUR_ZONE_PURIFY * Engine.physics_ticks_per_second)
	for i in frames / 2:
		await get_tree().physics_frame
	world.label.visible = false
	shot = await _bare(world)
	var both := _mix(shot, world, sick_img, pure_img)
	_check("a mitad: %.0f %% del suelo es enfermo o sano y nunca mezcla (%d sano, %d enfermo)" % [
		both[0] * 100, both[1], both[2]], both[0] >= MATCH_MIN and both[1] > 0 and both[2] > 0)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [zone, "ola"]))
	await world.wave_finished
	world.label.visible = false
	if world.monster != null:
		world.monster.active = false
	await _settle()
	shot = await _bare(world)
	m = _match(shot, world, pure_img)
	_check("purificada: se ve el sano en el %.0f %% de la pantalla" % [m * 100],
		m >= MATCH_MIN and world.terrain_pure.visible)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [zone, "sano"]))
	state.set_zone_purified(zone, false)
	_end()


func _end() -> void:
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


func _settle() -> void:
	for i in 4:
		await get_tree().physics_frame


## La pantalla con solo el suelo: decorado e Ilan ocultos un cuadro.
func _bare(world: WorldRoot) -> Image:
	for n in [world.entities, world.solids]:
		n.visible = false
	var img := await _shot()
	for n in [world.entities, world.solids]:
		n.visible = true
	return img


func _shot() -> Image:
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


## Fracción de píxeles de pantalla iguales al píxel del PNG en esa posición.
func _match(shot: Image, world: WorldRoot, tex: Image) -> float:
	var view: Rect2i = world.camera.visible_rect()
	var hit := 0
	for y in shot.get_height():
		for x in shot.get_width():
			if _same(shot.get_pixel(x, y), tex.get_pixel(view.position.x + x, view.position.y + y)):
				hit += 1
	return float(hit) / (shot.get_width() * shot.get_height())


## [fracción enfermo-o-sano, píxeles que solo casan con el sano, solo con el enfermo].
func _mix(shot: Image, world: WorldRoot, sick: Image, pure: Image) -> Array:
	var view: Rect2i = world.camera.visible_rect()
	var hit := 0
	var p := 0
	var s := 0
	for y in shot.get_height():
		for x in shot.get_width():
			var c := shot.get_pixel(x, y)
			var wx := view.position.x + x
			var wy := view.position.y + y
			var is_s := _same(c, sick.get_pixel(wx, wy))
			var is_p := _same(c, pure.get_pixel(wx, wy))
			if is_s or is_p:
				hit += 1
			if is_p and not is_s:
				p += 1
			elif is_s and not is_p:
				s += 1
	return [float(hit) / (shot.get_width() * shot.get_height()), p, s]


func _same(a: Color, b: Color) -> bool:
	return a.to_rgba32() >> 8 == b.to_rgba32() >> 8
