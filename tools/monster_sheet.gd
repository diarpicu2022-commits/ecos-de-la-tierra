extends Node2D

## Paso 2 del contrato «Persiana»: el monstruo de mapa en sus posturas, en su
## fuente y a 480x270, y la sombra de alerta medida sobre el render.
##
##   godot --path . res://tools/monster_sheet.tscn
##
## Por región, tres capturas con Ilan a MONSTER_SIGHT_TILES del monstruo:
## reposo, alerta (sombra estirada MONSTER_ALERT_STEPS tiles hacia Ilan) y
## persecución. Después compara, píxel a píxel, la banda de la sombra en la
## captura de alerta con el mismo sitio en la de reposo, por tinta: la brasa
## y el filo oscuro (enmienda 1). La señal se lee si una de las dos llega a
## 3:1, el piso de las formas que informan (guía §1.5). Sale con código 1 si
## alguna región no llega.

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"
const ZONES := ["ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak", "greed_crypt"]
const SLUG := {"ashen_forest": "bosque", "tar_basin": "cuenca", "broken_coast": "costa",
	"withered_plain": "llanura", "waning_peak": "cumbre", "greed_crypt": "cripta"}
const DECOR := "res://assets/sprites/world/decor/"
const MIN_CONTRAST := 3.0
## Por debajo del piso con permiso: sobre la losa de valor medio de la Cripta
## ninguna tinta autorizada llega a 3:1. Lleva filo de 2 px (Diego, 2026-10-28).
## Se mide y se imprime igual; no cuenta como fallo.
const BELOW_FLOOR_ALLOWED := ["greed_crypt"]

var _world := WorldRoot.new()
var _fails := 0


func _ready() -> void:
	get_node("/root/GameState").flags.clear()
	_world.start_zone = ZONES[0]
	_world.start_cell = Vector2i(1, 1)
	add_child(_world)
	await get_tree().physics_frame
	DesignTokens.reduced_motion = true
	_world.body.input_enabled = false
	for zone in ZONES:
		await _sheet(zone)
	print("\n%s" % ("Todo en verde." if _fails == 0 else "%d regiones no llegan a %.1f:1." % [_fails, MIN_CONTRAST]))
	get_tree().quit(1 if _fails else 0)


func _sheet(zone: String) -> void:
	var deco := ZoneRules.load_deco(zone)
	var lines := ZoneRules.load_zone(zone)
	var monster_at := Vector2i(-1, -1)
	var solid := {}
	for piece in WorldDecor.pieces(deco["rows"], deco["legend"]):
		var entry: Dictionary = deco["legend"][piece["ch"]]
		if entry["id"] == "monster":
			monster_at = piece["at"]
		if entry["solid"]:
			for j in entry["size"].y:
				for i in entry["size"].x:
					solid[piece["at"] + Vector2i(i, j)] = true
	# Ilan, a MONSTER_SIGHT_TILES en línea recta y con suelo libre en medio.
	var dir := Vector2i.ZERO
	for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.UP]:
		var clear := true
		for k in range(1, DesignTokens.MONSTER_SIGHT_TILES + 1):
			var c: Vector2i = monster_at + d * k
			if c.y < 0 or c.y >= lines.size() or c.x < 0 or c.x >= lines[0].length() \
					or not ZoneRules.walkable(lines[c.y][c.x]) or solid.has(c):
				clear = false
				break
		if clear:
			dir = d
			break
	print("\n%s: monstruo en %s, Ilan hacia %s" % [zone, monster_at, dir])
	if dir == Vector2i.ZERO:
		_fails += 1
		print("  FALLA no hay línea libre de %d tiles desde el monstruo" % DesignTokens.MONSTER_SIGHT_TILES)
		return
	var ilan: Vector2i = monster_at + dir * DesignTokens.MONSTER_SIGHT_TILES
	_world.enter_zone(zone, ilan)
	_world.label.visible = false
	# El componente real, quieto: la hoja fuerza cada estado (paso 3).
	var mon := _world.monster
	mon.target = null
	mon.active = false
	mon.facing = dir
	mon.force(MapMonster.State.PATROL)
	var rest := await _shot(zone, "reposo")
	# Alerta: erguido, mirando a Ilan, y la señal estirada hacia él.
	mon.force(MapMonster.State.ALERT, ilan)
	mon.alert_steps = DesignTokens.MONSTER_ALERT_STEPS
	mon._sync()
	var t := DesignTokens.TILE_SIZE
	var band := {}
	for s in mon._bands:
		var at := Vector2i(s.global_position)
		var img := s.texture.get_image()
		for y in img.get_height():
			for x in img.get_width():
				var px := img.get_pixel(x, y)
				if px.a > 0:
					var ink := "brasa" if px.r > 0.5 else "filo"
					if not band.has(ink):
						band[ink] = []
					band[ink].append(at + Vector2i(x, y))
	var alert := await _shot(zone, "alerta")
	mon.force(MapMonster.State.CHASE, ilan)
	await _shot(zone, "persecucion")
	_measure(zone, rest, alert, band)


## Contraste de cada tinta de la señal contra el mismo sitio en reposo. Las
## coordenadas del mundo pasan a la pantalla con la transformada del lienzo.
func _measure(zone: String, rest: Image, alert: Image, band: Dictionary) -> void:
	var xf := get_viewport().get_canvas_transform()
	var best := 0.0
	var parts := PackedStringArray()
	for ink in band:
		var lum_rest := 0.0
		var lum_alert := 0.0
		var n := 0
		for w: Vector2i in band[ink]:
			var p := Vector2i(xf * Vector2(w))
			if p.x < 0 or p.y < 0 or p.x >= rest.get_width() or p.y >= rest.get_height():
				continue
			lum_rest += _lum(rest.get_pixelv(p))
			lum_alert += _lum(alert.get_pixelv(p))
			n += 1
		if n == 0:
			continue
		lum_rest /= n
		lum_alert /= n
		var ratio := (maxf(lum_rest, lum_alert) + 0.05) / (minf(lum_rest, lum_alert) + 0.05)
		best = maxf(best, ratio)
		parts.append("%s %.2f:1" % [ink, ratio])
	var ok := best >= MIN_CONTRAST
	var allowed := not ok and zone in BELOW_FLOOR_ALLOWED
	_fails += 0 if ok or allowed else 1
	print("  %s señal de alerta sobre el suelo: %s (piso %.1f:1 en una de las dos)" % [
		"OK   " if ok else ("EXCEPCIÓN" if allowed else "FALLA"), ", ".join(parts), MIN_CONTRAST])


func _lum(c: Color) -> float:
	var ch := func(v: float) -> float:
		return v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4)
	return 0.2126 * ch.call(c.r) + 0.7152 * ch.call(c.g) + 0.0722 * ch.call(c.b)


func _shot(zone: String, tag: String) -> Image:
	for _i in 4:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(ProjectSettings.globalize_path(OUT_DIR + "%s-%s-monstruo-%s.png" % [DATE, SLUG[zone], tag]))
	return img
