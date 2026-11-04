extends Node

## La pantalla de resultado (`ResultOverlay`, guía del equipo §3.1, fila 14):
##
##   godot --path . res://tools/verify_result.tscn
##
## En cada desenlace mide que el texto cabe en la placa y la placa en el campo, y
## que el contraste llega a 4,5:1 sobre la pizarra. Con ventana, escribe
## docs/ux/capturas/<fecha>-resultado-<desenlace>.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-resultado-%s.png"
const MIN_CONTRAST := 4.5

var _pass := 0
var _fail := 0


func _ready() -> void:
	get_node("/root/GameState").flags.clear()
	var layer := CanvasLayer.new()
	add_child(layer)
	var screen := BattleScreen.new()
	screen.region = "ashen_forest"
	screen.companions_auto = true
	layer.add_child(screen)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(1):
		add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(0)
	add_child(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(1), Enums.Team.PLAYER)
	await get_tree().process_frame
	screen._step_timer.stop()
	screen._queue.clear()
	var overlay: ResultOverlay = screen._overlay
	overlay.continue_hint = "Enter para continuar"
	var font: Font = load(DesignTokens.FONT_PATH)
	var inner := ResultOverlay.PANEL_WIDTH - TvFrame.SLICE * 2.0
	var cases := [["victoria", Enums.BattleResult.VICTORY, 0],
		["derrota", Enums.BattleResult.DEFEAT, 12], ["retirada", Enums.BattleResult.FLED, 1]]
	for entry in cases:
		screen._phase = BattleScreen.Phase.FINISHED
		overlay.show_result(entry[1], entry[2], BattleScreen.FIELD_HEIGHT)
		var said := overlay.outcome()
		var title_w := TvFrame.width(font, said["headline"], DesignTokens.FONT_SIZE_TITLE)
		print(entry[0])
		_check("el titular de 22 px cabe (%.0f de %.0f px)" % [title_w, inner], title_w <= inner)
		var widest := TvFrame.width(font, said["hint"])
		for line in overlay.detail_lines():
			widest = maxf(widest, TvFrame.width(font, line))
		_check("el texto cabe (%.0f de %.0f px)" % [widest, inner], widest <= inner)
		_check("la placa cabe en la pantalla y queda centrada",
			Rect2(Vector2.ZERO, overlay.size).encloses(overlay.panel_rect())
			and absf(overlay.panel_rect().get_center().y - BattleScreen.SCREEN.y / 2.0) <= 1.0)
		var over_views := true
		for view in screen._monster_views:
			over_views = over_views and overlay.z_index > view.z_index
		_check("va delante de todo, también de los monstruos",
			overlay.get_index() == screen.get_child_count() - 1 and over_views)
		_check_contrast("el titular", said["tone"])
		if DisplayServer.get_name() != "headless":
			await get_tree().create_timer(0.3).timeout
			await RenderingServer.frame_post_draw
			var path := OUT % [Time.get_date_string_from_system(), entry[0]]
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
	print("general")
	_check_contrast("el detalle", DesignTokens.TV_TEXT_ON_SLATE)
	_check_contrast("la indicación", DesignTokens.TV_TEXT_HIGHLIGHT)
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check_contrast(what: String, tone: Color) -> void:
	var la := _luminance(tone)
	var lb := _luminance(DesignTokens.TV_SLATE)
	var ratio := (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)
	_check("%s se lee sobre la pizarra: %.2f:1" % [what, ratio], ratio >= MIN_CONTRAST)


func _luminance(c: Color) -> float:
	return 0.2126 * _linear(c.r) + 0.7152 * _linear(c.g) + 0.0722 * _linear(c.b)


func _linear(v: float) -> float:
	return v / 12.92 if v <= 0.03928 else pow((v + 0.055) / 1.055, 2.4)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
