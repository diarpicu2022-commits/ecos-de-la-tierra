extends Node

## Las cifras de daño (`DamageNumbers`, guía del equipo §3.1, fila 13):
##
##   godot --path . res://tools/verify_numbers.tscn
##
## Mide que van a doble tamaño, que la fuente tiene `~` y `+`, que un golpe que el
## monstruo se quita de encima sale con `~` y que ninguna se sale de la pantalla.
## Con ventana, congela las cifras y escribe
## docs/ux/capturas/<fecha>-cifras-ashen_forest.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-cifras-ashen_forest.png"

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
	var numbers: DamageNumbers = screen._numbers
	var font: Font = load(DesignTokens.FONT_PATH)

	print("Tamaño y signos")
	_check("van a doble tamaño (%d px)" % DamageNumbers.SIZE,
		DamageNumbers.SIZE == DesignTokens.FONT_SIZE_BODY * 2)
	for sign_char in ["~", "+"]:
		_check("la fuente tiene «%s»" % sign_char, font.has_char(sign_char.unicode_at(0)))

	var over := numbers.z_index < ResultOverlay.FRONT_Z
	for view in screen._monster_views:
		over = over and numbers.z_index > view.z_index
	_check("van delante de los monstruos y detrás del resultado", over)

	print("\nEl golpe resistido")
	numbers.clear()
	screen._pending_numbers.clear()
	screen._pending_numbers.append({"target": monster, "amount": 4, "resisted": true, "healing": false})
	screen._release_numbers()
	_check("sale con ~ delante", numbers._entries.size() == 1 and numbers._entries[0]["text"] == "~4")

	print("\nDentro de la pantalla")
	var view := Rect2(Vector2.ZERO, BattleScreen.SCREEN)
	for point in [Vector2(0, 0), Vector2(BattleScreen.SCREEN.x, 0), Vector2(2, 180),
			Vector2(BattleScreen.SCREEN.x - 2, 180)]:
		var at := numbers.baseline_of(point, "~999", 1.0)
		var width := font.get_string_size("~999", HORIZONTAL_ALIGNMENT_LEFT, -1, DamageNumbers.SIZE).x
		var box := Rect2(at - Vector2(0, DamageNumbers.CELL_HEIGHT), Vector2(width, DamageNumbers.CELL_HEIGHT))
		_check("una cifra en %s no se sale" % point, view.encloses(box))
	var a := numbers.baseline_of(Vector2(320, 100), "38", 0.0)
	var b := numbers.baseline_of(Vector2(320 + DamageNumbers.FAN, 100), "38", 0.0)
	var two := font.get_string_size("38", HORIZONTAL_ALIGNMENT_LEFT, -1, DamageNumbers.SIZE).x
	_check("el abanico separa dos cifras de dos dígitos (%.0f px)" % two, b.x - a.x >= two)
	numbers.clear()
	numbers.spawn(Vector2(100, 100), "1", DesignTokens.TV_UI_6)
	numbers.spawn(Vector2(100, 100), "2", DesignTokens.TV_UI_6)
	numbers.spawn(Vector2(200, 100), "3", DesignTokens.TV_UI_6)
	_check("sobre el mismo objetivo se abren en abanico",
		numbers._entries[0]["origin"].x != numbers._entries[1]["origin"].x)
	_check("una cifra de otro objetivo no se empuja", numbers._entries[2]["origin"].x == 200.0)

	if DisplayServer.get_name() != "headless":
		numbers.clear()
		numbers.spawn(screen._anchor_for(monster), "~4", DesignTokens.TV_UI_4)
		numbers.spawn(screen._anchor_for(monster), "38", DesignTokens.TV_GOLD_4)
		numbers.spawn(screen._anchor_for(players[0]), "26", DesignTokens.TV_RUST_4)
		numbers.spawn(screen._anchor_for(players[1]) if players.size() > 1 else Vector2(240, 200),
			"+12", DesignTokens.TV_UI_6)
		numbers.set_process(false)
		numbers.queue_redraw()
		await get_tree().create_timer(0.3).timeout
		await RenderingServer.frame_post_draw
		var path := OUT % Time.get_date_string_from_system()
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
		print("captura: ", path)

	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])
