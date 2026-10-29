extends Node

## Paso 5 del contrato «Persiana»: el fondo de cada región en «Ceniza y
## Brasa», a 480x270, y lo que se mide de él:
##
##   godot --path . res://tools/battle_bg_sheet.tscn
##
## - Parallax de entrada: la capa cercana sale a 3 × BATTLE_PARALLAX px, baja
##   sin retroceder y queda en 0 a los DUR_BATTLE_BLINDS; con movimiento
##   reducido, 0 desde el primer cuadro.
## - Cada captura, solo tokens (se comprueba aparte con verify_palette.py).
## - El monstruo se lee sobre su fondo: contraste de luminancia entre el borde
##   EMBER_300 del monstruo y el fondo de su región en el mismo campo, ≥ 3:1.
## Sale con código 1 si algo falla.

const OUT_DIR := "res://docs/ux/capturas/"
const DATE := "2026-10-28"
const SLUG := {"ashen_forest": "bosque", "tar_basin": "cuenca", "broken_coast": "costa",
	"withered_plain": "llanura", "waning_peak": "cumbre", "greed_crypt": "cripta"}

var _fails := 0


func _ready() -> void:
	await _parallax()
	for zone in GameFlow.ZONE_ENCOUNTER:
		await _shot(zone, GameFlow.ZONE_ENCOUNTER[zone])
	print("\n%s" % ("Todo en verde." if _fails == 0 else "%d fallos." % _fails))
	get_tree().quit(1 if _fails else 0)


func _check(label: String, ok: bool) -> void:
	_fails += 0 if ok else 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


func _parallax() -> void:
	print("Parallax de entrada")
	var screen := _battle("ashen_forest", 0)
	var start := screen.parallax_offset(3)
	var prev := start
	var monotonic := true
	var frames := 0
	while screen.parallax_offset(3) > 0 and frames < 100:
		await get_tree().physics_frame
		frames += 1
		monotonic = monotonic and screen.parallax_offset(3) <= prev
		prev = screen.parallax_offset(3)
	var expected := roundi(DesignTokens.DUR_BATTLE_BLINDS * 60)
	_check("la capa cercana sale a %d px y llega a 0 en %d cuadros (≤ %d), sin retroceder" % [
		start, frames, expected], start == 3 * DesignTokens.BATTLE_PARALLAX and frames <= expected and monotonic)
	DesignTokens.reduced_motion = true
	_check("con movimiento reducido, quieto desde el primer cuadro", screen.parallax_offset(3) == 0)
	DesignTokens.reduced_motion = false
	screen.get_parent().queue_free()
	await get_tree().process_frame


func _battle(zone: String, index: int) -> BattleScreen:
	var holder := Node.new()
	add_child(holder)
	var screen := BattleScreen.new()
	screen.region = zone
	holder.add_child(screen)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(index):
		holder.add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(index)
	holder.add_child(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(index))
	return screen


func _shot(zone: String, index: int) -> void:
	print("\n%s" % zone)
	var screen := _battle(zone, index)
	for _i in 40:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(ProjectSettings.globalize_path(OUT_DIR + "%s-combate-fondo-%s.png" % [DATE, SLUG[zone]]))
	# Fondo del campo, fuera de sprites y paneles: la franja de cielo y suelo
	# junto al monstruo (x 200-250), donde no hay nadie.
	var lum := 0.0
	var n := 0
	for y in range(20, 170, 3):
		for x in range(200, 250, 3):
			lum = maxf(lum, _lum(img.get_pixel(x, y)))
			n += 1
	var ember := _lum(DesignTokens.EMBER_300)
	var ratio := (ember + 0.05) / (lum + 0.05)
	_check("el borde del monstruo (EMBER_300) sobre el tono más claro del fondo: %.2f:1 (≥ 3:1)" % ratio,
		ratio >= 3.0)
	screen.get_parent().queue_free()
	await get_tree().process_frame


func _lum(c: Color) -> float:
	var ch := func(v: float) -> float:
		return v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4)
	return 0.2126 * ch.call(c.r) + 0.7152 * ch.call(c.g) + 0.0722 * ch.call(c.b)
