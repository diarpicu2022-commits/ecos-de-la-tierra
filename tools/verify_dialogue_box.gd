extends Node2D

## Prueba de la caja de diálogo (contrato «Columna», paso 2), en el motor y a
## 480 × 270:
##
##   godot --path . res://tools/verify_dialogue_box.tscn
##
## - Geometría: 312 × 52, a 8 px abajo, a la izquierda (x = 8) o a la derecha
##   (x = 160); el retrato en el lado exterior; 240 px de texto; el ▼ fuera de
##   la columna de texto y del retrato.
## - Texto: partido por palabras en ≤ 40 caracteres; las líneas no cambian
##   mientras se escribe; ninguna línea pasa de 240 px medida con la fuente.
## - Ritmo: cuadros hasta completar = los esperados por DUR_TYPE_CHAR y
##   DUR_TYPE_PAUSE; `confirm` completa y después avanza; con movimiento
##   reducido, completo en el primer cuadro.
## - Contraste medido sobre el render: texto, nombre y nombre de Rasgo en
##   brasa ≥ 4,5:1 sobre el panel; el ▼ ≥ 3:1.
## Capturas en docs/ux/capturas/2026-10-28-dialogo-*.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/2026-10-28-dialogo-%s.png"
const YARA := "La tierra no enferma sola, Ilan. Alguien la exprimió durante generaciones."
const RASGO := "La Compañía da pan a mil familias. ¿Y tú qué les das?"

var _pass := 0
var _fail := 0
var _box := DialogueBox.new()


func _ready() -> void:
	RenderingServer.set_default_clear_color(DesignTokens.ASH_950)
	var layer := CanvasLayer.new()
	add_child(layer)
	layer.add_child(_box)
	await get_tree().process_frame
	_geometry()
	_wrapping()
	await _rhythm()
	await _contrast()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


func _geometry() -> void:
	print("Geometría")
	DesignTokens.reduced_motion = true
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT)
	_check("a la izquierda: %s, %s" % [_box.position, _box.size],
		_box.position == Vector2(8, 210) and _box.size == Vector2(312, 52))
	var pr := _box.portrait_rect()
	var tr := _box.text_rect()
	_check("retrato fuera a la izquierda (%s) y texto de %d px" % [pr, tr.size.x],
		pr.position.x == 8 and pr.size == Vector2(48, 48) and tr.size.x == 240 and tr.position.x == 64)
	_box.show_line("Rasgo", RASGO, DialogueBox.Side.RIGHT)
	pr = _box.portrait_rect()
	tr = _box.text_rect()
	_check("a la derecha: %s, retrato fuera a la derecha (x = %d)" % [_box.position, pr.position.x],
		_box.position == Vector2(160, 210) and pr.end.x == 312 - 8 and tr.position.x == 8)
	for s in [DialogueBox.Side.LEFT, DialogueBox.Side.RIGHT]:
		_box.show_line("Yara", YARA, s)
		var c := _box.continue_origin()
		var arrow := Rect2(c, Vector2(6, 12))
		tr = _box.text_rect()
		_check("  el ▼ no toca el texto ni el retrato (lado %s)" % ["izquierdo", "derecho"][s],
			arrow.position.x >= tr.end.x and not arrow.intersects(_box.portrait_rect())
			and arrow.end.x <= _box.size.x)
	DesignTokens.reduced_motion = false


func _wrapping() -> void:
	print("\nTexto partido")
	var font: Font = load(DesignTokens.FONT_PATH)
	for text in [YARA, RASGO, "Corto.", "Una palabra larguísima: contrarrevolucionariamente sí cabe en su línea."]:
		var lines := DialogueBox.wrap_text(text)
		var ok := " ".join(lines) == " ".join(text.split(" ", false))
		var widest := 0.0
		for l in lines:
			ok = ok and l.length() <= DesignTokens.DIALOGUE_CHARS
			widest = maxf(widest, font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY).x)
		_check("«%s…»: %d líneas, la más ancha %d px (≤ 240)" % [text.substr(0, 20), lines.size(), widest],
			ok and widest <= 240)
	_check("la frase de Yara (73 caracteres) cabe en 2 líneas", DialogueBox.wrap_text(YARA).size() == 2)


func _rhythm() -> void:
	print("\nRitmo")
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT)
	var lines := _box.lines.duplicate()
	var expected := 0
	var step := roundi(DesignTokens.DUR_TYPE_CHAR * 60)
	var pause := roundi(DesignTokens.DUR_TYPE_PAUSE * 60)
	for l in lines:
		for ch in l:
			expected += step + (pause if DesignTokens.TYPE_PAUSE_AFTER.contains(ch) else 0)
	# El último carácter no espera después de sí.
	var last: String = lines[-1][-1]
	expected -= step + (pause if DesignTokens.TYPE_PAUSE_AFTER.contains(last) else 0)
	expected += 1
	var frames := 0
	var stable := true
	var arrow_early := false
	while not _box.is_complete() and frames < 2000:
		await get_tree().physics_frame
		frames += 1
		stable = stable and _box.lines == lines
		if frames == 20:
			(await _shot()).save_png(ProjectSettings.globalize_path(OUT % "escribiendo"))
	_check("se escribe en %d cuadros (%d esperados)" % [frames, expected], absi(frames - expected) <= 1)
	_check("las líneas no cambian mientras se escribe", stable)
	var got := [false]
	var cb := func(): got[0] = true
	_box.advanced.connect(cb)
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT)
	_box.confirm()
	_check("el primer confirm completa sin avanzar", _box.is_complete() and not got[0])
	_box.confirm()
	_check("el segundo confirm avanza", got[0])
	_box.advanced.disconnect(cb)
	DesignTokens.reduced_motion = true
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT)
	_check("con movimiento reducido, completo al instante", _box.is_complete())
	DesignTokens.reduced_motion = false


## Contraste sobre el render: el tono más presente de cada cosa contra el panel.
func _contrast() -> void:
	print("\nContraste medido sobre el render")
	DesignTokens.reduced_motion = true
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT, load("res://assets/sprites/portraits/yara_neutral.png"))
	var left := await _shot()
	left.save_png(ProjectSettings.globalize_path(OUT % "izquierda"))
	var bg := _lum(DesignTokens.PANEL_FILL)
	var tr := _box.text_rect()
	var o := _box.position
	_check("texto sobre el panel: %.1f:1 (≥ 4,5)" % _ratio(_brightest(left, Rect2(o + tr.position + Vector2(0, 12), Vector2(240, 24))), bg),
		_ratio(_brightest(left, Rect2(o + tr.position + Vector2(0, 12), Vector2(240, 24))), bg) >= 4.5)
	_check("nombre sobre el panel: %.1f:1 (≥ 4,5)" % _ratio(_brightest(left, Rect2(o + tr.position, Vector2(60, 12))), bg),
		_ratio(_brightest(left, Rect2(o + tr.position, Vector2(60, 12))), bg) >= 4.5)
	var c := o + _box.continue_origin()
	_check("el ▼ sobre el panel: %.1f:1 (≥ 3)" % _ratio(_brightest(left, Rect2(c, Vector2(7, 12))), bg),
		_ratio(_brightest(left, Rect2(c, Vector2(7, 12))), bg) >= 3.0)
	_box.show_line("Rasgo", RASGO, DialogueBox.Side.RIGHT, load("res://assets/sprites/portraits/rasgo_neutral.png"),
		DesignTokens.EMBER_400)
	var right := await _shot()
	right.save_png(ProjectSettings.globalize_path(OUT % "derecha-rasgo"))
	o = _box.position
	tr = _box.text_rect()
	_check("nombre de Rasgo en brasa: %.1f:1 (≥ 4,5)" % _ratio(_brightest(right, Rect2(o + tr.position, Vector2(60, 12))), bg),
		_ratio(_brightest(right, Rect2(o + tr.position, Vector2(60, 12))), bg) >= 4.5)
	DesignTokens.reduced_motion = false


func _shot() -> Image:
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


func _brightest(img: Image, r: Rect2) -> float:
	var best := 0.0
	for y in range(int(r.position.y), int(r.end.y)):
		for x in range(int(r.position.x), int(r.end.x)):
			best = maxf(best, _lum(img.get_pixel(x, y)))
	return best


func _ratio(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


func _lum(c: Color) -> float:
	var ch := func(v: float) -> float:
		return v / 12.92 if v <= 0.04045 else pow((v + 0.055) / 1.055, 2.4)
	return 0.2126 * ch.call(c.r) + 0.7152 * ch.call(c.g) + 0.0722 * ch.call(c.b)
