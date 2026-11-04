extends Node2D

## Prueba de la caja de diálogo (`components/DialogBox`), en el motor y a 640 × 360:
##
##   godot --path . res://tools/verify_dialogue_box.tscn
##
## - Geometría: 616 × 76 en (12, 276); el retrato de 40 × 44 en su marco, a un lado
##   o al otro; la chapa asoma por encima sin salirse; nada se pisa.
## - Texto: partido por palabras en ≤ DIALOGUE_CHARS caracteres; las líneas no
##   cambian mientras se escribe; ninguna se sale de la columna de texto.
## - Ritmo: cuadros hasta completar = los esperados por DUR_TYPE_CHAR y
##   DUR_TYPE_PAUSE; `confirm` completa y después avanza; con movimiento
##   reducido, completo en el primer cuadro.
## - Contraste medido sobre el render: texto, nombre y nombre de Rasgo ≥ 4,5:1; el
##   ▼ ≥ 3:1.
## Capturas en docs/ux/capturas/<fecha>-dialogo-*.png.
## Sale con código 1 si algo falla.

const OUT := "res://docs/ux/capturas/%s-dialogo-%s.png"
const YARA := "La tierra no enferma sola, Ilan. Alguien la exprimió durante generaciones."
const RASGO := "La Compañía da pan a mil familias. ¿Y tú qué les das?"

var _pass := 0
var _fail := 0
var _box := DialogueBox.new()


func _ready() -> void:
	RenderingServer.set_default_clear_color(DesignTokens.TV_GRASS_3)
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
	_check("la caja: %s, %s" % [_box.position, _box.size],
		_box.position == Vector2(12, 276) and _box.size == Vector2(616, 76)
		and Rect2(Vector2.ZERO, Vector2(640, 360)).encloses(Rect2(_box.position, _box.size)))
	_check("el retrato mide 40 × 44", _box.portrait_rect().size == Vector2(40, 44))
	# Sin retrato no hay marco: el sistema lo pide solo «si lo hay», y el texto
	# ocupa la caja.
	_check("sin retrato, el texto ocupa la caja",
		_box.text_rect().size.x == _box.size.x - TvFrame.SLICE * 2.0)
	var face: Texture2D = load("res://assets/sprites/portraits/tierra_viva/yara.png")
	for s in [DialogueBox.Side.LEFT, DialogueBox.Side.RIGHT]:
		_box.show_line("Yara", YARA, s, face)
		var tr := _box.text_rect()
		var frame := _box.portrait_frame()
		var box := Rect2(Vector2.ZERO, _box.size)
		var label: String = ["izquierdo", "derecho"][s]
		_check("  lado %s: retrato y texto dentro y sin pisarse" % label,
			box.encloses(frame) and box.encloses(tr) and not tr.intersects(frame))
		var tag := _box.tag_rect()
		_check("  lado %s: la chapa asoma por arriba y no se sale de la pantalla" % label,
			tag.position.y < 0.0 and tag.end.y > 0.0 and _box.position.y + tag.position.y >= 0.0)
		var arrow := Rect2(_box.continue_origin() - Vector2(0, 9), Vector2(7, 9))
		_check("  lado %s: el ▼ queda dentro y sin tocar el retrato" % label,
			box.encloses(arrow) and not arrow.intersects(frame))
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
		var room := _box.text_rect().size.x
		_check("«%s…»: %d líneas, la más ancha %d px (≤ %d)" % [text.substr(0, 20), lines.size(), widest, room],
			ok and widest <= room)
	_check("la frase de Yara cabe en 2 líneas", DialogueBox.wrap_text(YARA).size() <= DesignTokens.DIALOGUE_LINES)


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
			(await _shot()).save_png(ProjectSettings.globalize_path(OUT % [_day(), "escribiendo"]))
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


## Contraste sobre el render: el tono más alejado del fondo contra ese fondo.
func _contrast() -> void:
	print("\nContraste medido sobre el render")
	DesignTokens.reduced_motion = true
	_box.show_line("Yara", YARA, DialogueBox.Side.LEFT, load("res://assets/sprites/portraits/yara_neutral.png"))
	var left := await _shot()
	left.save_png(ProjectSettings.globalize_path(OUT % [_day(), "izquierda"]))
	var paper := _lum(DesignTokens.TV_PAPER)
	var o := _box.position
	var tr := _box.text_rect()
	var ratio := _ratio(_darkest(left, Rect2(o + Vector2(tr.position.x, 24), Vector2(tr.size.x - 12, 26))), paper)
	_check("texto sobre el papel: %.1f:1 (≥ 4,5)" % ratio, ratio >= 4.5)
	ratio = _ratio(_darkest(left, Rect2(o + _box.continue_origin() - Vector2(0, 9), Vector2(7, 9))), paper)
	_check("el ▼ sobre el papel: %.1f:1 (≥ 3)" % ratio, ratio >= 3.0)
	var tag := Rect2(o + _box.tag_rect().position + Vector2(_box.TAG_PAD, 4), Vector2(20, 9))
	ratio = _ratio(_brightest(left, tag), _lum(_fill("tag")))
	_check("nombre sobre su chapa: %.1f:1 (≥ 4,5)" % ratio, ratio >= 4.5)
	_box.show_line("Rasgo", RASGO, DialogueBox.Side.RIGHT, load("res://assets/sprites/portraits/rasgo_neutral.png"),
		DesignTokens.TV_FIRE_4)
	var right := await _shot()
	right.save_png(ProjectSettings.globalize_path(OUT % [_day(), "derecha-rasgo"]))
	tag = Rect2(o + _box.tag_rect().position + Vector2(_box.TAG_PAD, 4), Vector2(20, 9))
	ratio = _ratio(_brightest(right, tag), _lum(_fill("plate")))
	_check("nombre de Rasgo en fuego: %.1f:1 (≥ 4,5)" % ratio, ratio >= 4.5)
	DesignTokens.reduced_motion = false


func _day() -> String:
	return Time.get_date_string_from_system()


## El relleno de un marco: el píxel del centro de su imagen.
func _fill(frame: String) -> Color:
	var img: Image = (load(TvFrame.DIR + frame + ".png") as Texture2D).get_image()
	return img.get_pixel(img.get_width() / 2, img.get_height() / 2)


func _darkest(img: Image, r: Rect2) -> float:
	var best := 1.0
	for y in range(int(r.position.y), int(r.end.y)):
		for x in range(int(r.position.x), int(r.end.x)):
			best = minf(best, _lum(img.get_pixel(x, y)))
	return best


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
