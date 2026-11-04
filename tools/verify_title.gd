extends Node

## Pantalla de título (`src/ui/title_screen.gd`):
##   godot --path . res://tools/verify_title.tscn
##
## Con ventana escribe docs/ux/capturas/2026-11-04-titulo-*.png y mide el
## contraste del nombre sobre el render.

const OUT := "res://docs/ux/capturas/2026-11-04-titulo-%s.png"

var _pass := 0
var _fail := 0


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
		print("  OK    " + label)
	else:
		_fail += 1
		printerr("  FALLA " + label)


func _shot(tag: String) -> Image:
	if DisplayServer.get_name() == "headless":
		return null
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(ProjectSettings.globalize_path(OUT % tag))
	return img


static func _lum(c: Color) -> float:
	var f := func(v: float) -> float: return v / 12.92 if v <= 0.03928 else pow((v + 0.055) / 1.055, 2.4)
	return 0.2126 * f.call(c.r) + 0.7152 * f.call(c.g) + 0.0722 * f.call(c.b)


static func _ratio(a: Color, b: Color) -> float:
	var x := _lum(a)
	var y := _lum(b)
	return (maxf(x, y) + 0.05) / (minf(x, y) + 0.05)


func _ready() -> void:
	var scene := FileAccess.get_file_as_string("res://scenes/game.tscn")
	_check("la escena de juego empieza en el título", scene.contains("show_title = true"))
	var state := get_node("/root/GameState")
	state.flags.clear()
	DesignTokens.reduced_motion = true
	var flow := GameFlow.new()
	flow.show_title = true
	flow.play_opening = true
	add_child(flow)
	for i in 4:
		await get_tree().process_frame
	var t := flow.title

	print("El título")
	_check("se ve el título y Ilan espera escondido", t.visible and t.active
		and not flow.world.body.visible and not flow.world.body.input_enabled)
	_check("el fondo es Valdehoja real", flow.world.zone_id == "valdehoja")
	_check("el menú lleva «Créditos»", "Créditos" in TitleScreen.ENTRIES)
	_check("sin «Continuar» ni «Opciones», que no existen todavía",
		not "Continuar" in TitleScreen.ENTRIES and not "Opciones" in TitleScreen.ENTRIES)
	_check("dice «Partida nueva»", t.status_text() == "Partida nueva")
	var img := await _shot("nueva")
	if img != null:
		# El blanco del nombre contra su contorno de tinta.
		var white := 0
		for y in range(60, 140):
			for x in range(28, 200):
				if img.get_pixel(x, y).is_equal_approx(DesignTokens.TV_UI_6):
					white += 1
		var ratio := _ratio(DesignTokens.TV_UI_6, DesignTokens.TV_INK_0)
		_check("el nombre se pinta en blanco (%d px) con contorno de tinta, %.1f:1" % [white, ratio],
			white > 500 and ratio >= 7.0)

	var font: Font = load(DesignTokens.FONT_PATH)
	for k in [1, 2]:
		t.focused = k
		var entry: String = TitleScreen.ENTRIES[k]
		print("\n" + entry)
		t.choose()
		var lines := t.lines_of(entry)
		_check("«%s» se abre con su texto (%d líneas)" % [entry, lines.size()], t.showing == entry and lines.size() >= 3)
		var widest := 0.0
		var missing := ""
		for line in lines:
			widest = maxf(widest, TvFrame.width(font, line))
			for ch in line:
				if not font.has_char(ch.unicode_at(0)):
					missing += ch
		_check("cabe en su papel (%.0f de %.0f px, %d líneas)" % [widest, TitleScreen.NOTE.size.x - 24, lines.size()],
			widest <= TitleScreen.NOTE.size.x - 24 and 38 + 13 * lines.size() <= TitleScreen.NOTE.size.y - 14)
		_check("la fuente tiene todos sus caracteres (faltan: «%s»)" % missing, missing.is_empty())
		await _shot(entry.to_lower().replace("é", "e"))
		var back := InputEventAction.new()
		back.action = "confirm"
		back.pressed = true
		t._unhandled_input(back)
		_check("Enter vuelve al menú", t.showing == "" and t.active)

	print("\nNueva partida")
	t.focused = 0
	t.choose()
	# El fundido de salida dura dos medios fundidos de zona.
	for i in 40:
		await get_tree().process_frame
	_check("el título se va", not t.active and not t.visible)
	_check("Ilan aparece en su sitio", flow.world.body.visible
		and MapMonster.cell_of(Vector2i(flow.world.body.global_position)) == flow.start_cell)
	_check("y empieza la llamada de Yara", flow.world.dialogue.is_running()
		and flow.world.dialogue.conversation == "yara_llamada")

	print("\nCon algo devuelto")
	state.set_zone_purified("ashen_forest")
	_check("dice «Una región devuelta»", t.status_text() == "Una región devuelta")
	state.flags.clear()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)
