class_name TitleScreen
extends Control

## Pantalla de título, dirección A de `docs/ux/tierra-viva/titulo-y-creditos.md`
## (referencia `docs/ux/tierra-viva/referencias/titulo_nueva.png`).
##
## - El fondo es Valdehoja real en el estado de la partida, con la cámara
##   quieta sobre la plaza: lo que el jugador devuelve se ve aquí.
## - Un solo punto de entrada, el nombre en Brote: «Ecos de la» a ×3 y
##   «Tierra» a ×5. «Tierra» va en blanco en partida nueva y en eco en cuanto
##   hay algo purificado: el verde dice exactamente eso.
## - El nombre lleva el contorno de 1 px en tinta de la referencia. La
##   referencia además oscurece la mitad izquierda multiplicando el color, lo
##   que crea colores que no son tokens; con trama se veía como un damero, así
##   que no se oscurece y el contraste del nombre se mide en `verify_title`.
## - Menú en la placa de pizarra: Nueva partida, Privacidad y Salir. No hay
##   «Continuar» porque aún no hay guardado, ni «Opciones» porque no existen.
## - Abajo a la derecha, el estado de la partida.
##
## «Privacidad» enseña el aviso de `data/legal/privacidad.txt`, que resume
## `docs/legal/privacidad.md`: si uno cambia, cambia el otro.

signal started
signal quit_requested

const ENTRIES := ["Nueva partida", "Privacidad", "Salir"]
const NAME_AT := Vector2(28, 52)
const MENU := Rect2(24, 252, 140, 58)
const ROW := 14.0
const PRIVACY := "res://data/legal/privacidad.txt"
const NOTE := Rect2(150, 230, 460, 116)

var focused := 0
var showing_privacy := false
var active := false
var _font: Font = null
var _privacy := PackedStringArray()


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(640, 360)
	var text := FileAccess.get_file_as_string(PRIVACY)
	_privacy = text.strip_edges().split("\n")


func open() -> void:
	active = true
	visible = true
	modulate.a = 1.0
	focused = 0
	showing_privacy = false
	queue_redraw()


## Cuántas zonas están purificadas según `GameState`.
func purified_count() -> int:
	var state := get_node_or_null("/root/GameState")
	if state == null:
		return 0
	var n := 0
	for z in GameFlow.ZONE_ENCOUNTER.keys():
		if state.is_zone_purified(z):
			n += 1
	return n


func status_text() -> String:
	match purified_count():
		0:
			return "Partida nueva"
		1:
			return "Una región devuelta"
		var n:
			return "%d regiones devueltas" % n


func _unhandled_input(event: InputEvent) -> void:
	if not active or not event.is_pressed() or event.is_echo():
		return
	if showing_privacy:
		if event.is_action("confirm") or event.is_action("cancel"):
			showing_privacy = false
			GameAudio.play("ui_cancel")
			queue_redraw()
			get_viewport().set_input_as_handled()
		return
	if event.is_action("move_down"):
		move(1)
	elif event.is_action("move_up"):
		move(-1)
	elif event.is_action("confirm"):
		choose()
	else:
		return
	get_viewport().set_input_as_handled()


func move(direction: int) -> void:
	focused = wrapi(focused + direction, 0, ENTRIES.size())
	GameAudio.play("ui_move")
	queue_redraw()


func choose() -> void:
	GameAudio.play("ui_confirm")
	match ENTRIES[focused]:
		"Nueva partida":
			close()
			started.emit()
		"Privacidad":
			showing_privacy = true
			queue_redraw()
		"Salir":
			quit_requested.emit()


## Se va con un fundido de opacidad, o de golpe con movimiento reducido.
func close() -> void:
	active = false
	if DesignTokens.reduced_motion:
		visible = false
		return
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, DesignTokens.DUR_ZONE_FADE * 2.0)
	tween.tween_callback(func(): visible = false)


func _draw() -> void:
	var tierra := DesignTokens.TV_ECO_3 if purified_count() > 0 else DesignTokens.TV_UI_6
	_big("Ecos de la", NAME_AT, 3, DesignTokens.TV_UI_6)
	_big("Tierra", NAME_AT + Vector2(0, 66), 5, tierra)
	TvFrame.draw(self, TvFrame.PLATE, MENU)
	for i in ENTRIES.size():
		var y := MENU.position.y + 16.0 + ROW * i
		var on := i == focused
		if on:
			TvFrame.slate_text(self, _font, Vector2(MENU.position.x + 8, y), "▶", DesignTokens.TV_TEXT_HIGHLIGHT)
		TvFrame.slate_text(self, _font, Vector2(MENU.position.x + 20, y), ENTRIES[i],
			DesignTokens.TV_TEXT_HIGHLIGHT if on else DesignTokens.TV_TEXT_ON_SLATE)
	var status := status_text()
	var w := TvFrame.width(_font, status)
	TvFrame.slate_text(self, _font, Vector2(640 - 12 - w, 350), status, DesignTokens.TV_UI_4)
	if showing_privacy:
		TvFrame.draw(self, TvFrame.TEXTBOX, NOTE)
		TvFrame.paper_text(self, _font, NOTE.position + Vector2(12, 20), "Privacidad")
		for i in _privacy.size():
			TvFrame.paper_text(self, _font, NOTE.position + Vector2(12, 38 + 13 * i), _privacy[i])
		var hint := "Enter para volver"
		TvFrame.paper_text(self, _font, NOTE.end - Vector2(TvFrame.width(_font, hint) + 12, 8), hint)


## Texto a escala entera con contorno de 1 px en tinta, como `outlined` de
## `tools/tierra_viva/title_credits.py`.
func _big(text: String, at: Vector2, scale_: int, color: Color) -> void:
	var size_ := DesignTokens.FONT_SIZE_BODY * scale_
	for dx in [-1, 0, 1]:
		for dy in [-1, 0, 1]:
			if dx != 0 or dy != 0:
				draw_string(_font, at + Vector2(dx, dy), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_,
					DesignTokens.TV_INK_0)
	draw_string(_font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_, color)

