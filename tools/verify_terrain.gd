extends Node

## El suelo de Tierra Viva en el motor (contrato «Piel nueva», paso 2), a
## 640 × 360 y con ventana:
##
##   godot --path . res://tools/verify_terrain.tscn -- [zona] [etiqueta] [x y]
##
## Sin argumento, el Bosque (`ashen_forest`). La etiqueta (por defecto
## «terreno») va en el nombre de las capturas, y `x y` cambia la casilla desde
## la que se mira, para encuadrar el decorado (paso 4b: «decorado» y el hito). Vale para las seis regiones
## (paso 3): se mira desde la casilla de llegada y se empuja contra la
## primera casilla de follaje o muro con suelo debajo.
## - **Montaje:** existen los dos sprites del suelo, miden la zona (casillas ×
##   16) y están en el origen; la capa de tiles queda oculta.
## - **Colisión desde la matriz:** empujando contra follaje o muro durante 60
##   cuadros, Ilan no entra en ninguna casilla sólida.
## - **Se ve lo que se generó:** con el decorado e Ilan ocultos,
##   cada píxel de la pantalla es exactamente el píxel del PNG en esa posición
##   del mundo: sin filtro, sin escala y sin desfase. Las capturas se hacen
##   después, con todo visible.
## - **Estado:** enferma, se ve el enfermo; purificada, el sano.
## - **Ola:** a mitad de la ola, cada píxel visible del suelo es enfermo o
##   sano, nunca una mezcla, y hay de los dos.
## Capturas: docs/ux/capturas/<fecha>-<etiqueta>-<zona>-{enfermo,ola,sano}.png,
## con la fecha del día.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-%s-%s-%s.png"
const MATCH_MIN := 1.0

## Casilla desde la que se mira, si no es la de llegada: en el Bosque, junto
## al puente.
const VIEW := {"ashen_forest": Vector2i(44, 15)}

var _pass := 0
var _fail := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var zone: String = args[0] if args.size() > 0 else "ashen_forest"
	var tag: String = args[1] if args.size() > 1 else "terreno"
	var day := Time.get_date_string_from_system()
	var state := get_node("/root/GameState")
	state.flags.clear()
	state.set_zone_purified(zone, false)
	DesignTokens.reduced_motion = false
	var lines := ZoneRules.load_zone(zone)
	var view_cell: Vector2i = VIEW.get(zone, _arrival(zone))
	if args.size() > 3:
		view_cell = Vector2i(int(args[2]), int(args[3]))
	var wall_cell := _against_wall(lines)
	var world := WorldRoot.new()
	world.start_zone = zone
	world.start_cell = view_cell
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
	world.enter_zone(zone, wall_cell)
	await get_tree().physics_frame
	var entered := 0
	for i in 60:
		world.body.step(Vector2i.UP, false)
		await get_tree().physics_frame
		var c := MapMonster.cell_of(Vector2i(world.body.global_position))
		if not ZoneRules.walkable(lines[c.y][c.x]):
			entered += 1
	_check("empujando al norte desde %s («%s» encima) 60 cuadros, ninguna casilla sólida pisada (%d)" % [
		wall_cell, lines[wall_cell.y - 1][wall_cell.x], entered], entered == 0)

	print("\nEstado")
	world.enter_zone(zone, view_cell)
	world.label.visible = false
	await _settle()
	var shot := await _bare(world)
	var m := _match(shot, world, sick_img)
	_check("enferma: se ve el enfermo en el %.0f %% de la pantalla (≥ %.0f %%)" % [m * 100, MATCH_MIN * 100],
		m >= MATCH_MIN and not world.terrain_pure.visible)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [day, tag, zone, "enfermo"]))

	print("\nOla")
	var origin: Vector2i = view_cell
	world.purify_wave(origin)
	var frames := roundi(DesignTokens.DUR_ZONE_PURIFY * Engine.physics_ticks_per_second)
	for i in frames / 2:
		await get_tree().physics_frame
	world.label.visible = false
	shot = await _bare(world)
	var both := _mix(shot, world, sick_img, pure_img)
	_check("a mitad: %.0f %% del suelo es enfermo o sano y nunca mezcla (%d sano, %d enfermo)" % [
		both[0] * 100, both[1], both[2]], both[0] >= MATCH_MIN and both[1] > 0 and both[2] > 0)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [day, tag, zone, "ola"]))
	await world.wave_finished
	world.label.visible = false
	if world.monster != null:
		world.monster.active = false
	await _settle()
	shot = await _bare(world)
	m = _match(shot, world, pure_img)
	_check("purificada: se ve el sano en el %.0f %% de la pantalla" % [m * 100],
		m >= MATCH_MIN and world.terrain_pure.visible)
	(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [day, tag, zone, "sano"]))
	state.set_zone_purified(zone, false)
	_end()


## Casilla de llegada de la primera salida que entra en la zona.
func _arrival(zone: String) -> Vector2i:
	for e in ZoneRules.load_exits():
		if e["to"] == zone:
			return ZoneRules.cell_of(e, "to_cell")
	return Vector2i(1, 1)


## Primera casilla pisable, con pisable a los lados, bajo una sólida que no es
## agua (follaje o muro): empujando al norte se choca contra ella.
func _against_wall(lines: PackedStringArray) -> Vector2i:
	for y in range(2, lines.size() - 1):
		for x in range(2, lines[y].length() - 2):
			if ZoneRules.walkable(lines[y][x]) and ZoneRules.walkable(lines[y][x - 1]) 					and ZoneRules.walkable(lines[y][x + 1]) and not ZoneRules.walkable(lines[y - 1][x]) 					and lines[y - 1][x] != "~":
				return Vector2i(x, y)
	return Vector2i(-1, -1)


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
