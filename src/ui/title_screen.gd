class_name TitleScreen
extends Control

## Pantalla de título con la portada del sistema de diseño (componente
## `Cover`, `docs/ux/sistema-de-diseno/project/components/Cover/preview.html`),
## elegida por Diego el 2026-11-04.
##
## - A la derecha, la portada: Valdehoja que pasa de enferma a sana por un
##   frente tramado de 4 × 4. Es la idea de `Cover` («el mapa que vuelve a ser
##   verde, el mecanismo del juego») hecha con el arte real.
## - A la izquierda, un solo punto de entrada: el nombre en Brote, «Ecos de la»
##   a ×3 y «Tierra» a ×5 con sombra de tinta, y la frase del sistema debajo.
##   «Tierra» pasa a eco en cuanto hay algo purificado: el verde dice eso.
## - Debajo, el menú: Nueva partida, Créditos, Privacidad y Salir. No hay
##   «Continuar» porque aún no hay guardado, ni «Opciones» porque no existen.
## - Abajo a la izquierda, el estado de la partida.
##
## «Créditos» y «Privacidad» enseñan `data/legal/creditos.txt` y
## `data/legal/privacidad.txt`; este resume `docs/legal/privacidad.md`.

signal started
signal quit_requested

const ENTRIES := ["Nueva partida", "Créditos", "Privacidad", "Salir"]
const NAME_AT := Vector2(32, 92)
const TAGLINE_AT := Vector2(34, 186)
const MENU_AT := Vector2(34, 232)
const ROW := 16.0
const PRIVACY := "res://data/legal/privacidad.txt"
const CREDITS := "res://data/legal/creditos.txt"
const NOTE := Rect2(150, 216, 460, 130)
const TAGLINE := ["Tierra Viva: el mundo enferma con color", "y sana con color."]

## Portada: la columna donde empieza y su imagen.
const COVER_X := 320
const COVER: Texture2D = preload("res://assets/ui/portada.png")

var focused := 0
var showing := ""
var active := false
var _font: Font = null
var _texts := {}


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(640, 360)
	_texts["Privacidad"] = FileAccess.get_file_as_string(PRIVACY).strip_edges().split("\n")
	_texts["Créditos"] = FileAccess.get_file_as_string(CREDITS).strip_edges().split("\n")


## Compatibilidad con la prueba: el aviso de privacidad abierto.
var showing_privacy: bool:
	get:
		return showing == "Privacidad"


var _privacy: PackedStringArray:
	get:
		return _texts.get("Privacidad", PackedStringArray())


func lines_of(entry: String) -> PackedStringArray:
	return _texts.get(entry, PackedStringArray())


func open() -> void:
	active = true
	visible = true
	modulate.a = 1.0
	focused = 0
	showing = ""
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
	if showing != "":
		if event.is_action("confirm") or event.is_action("cancel"):
			showing = ""
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
		"Créditos", "Privacidad":
			showing = ENTRIES[focused]
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
	draw_rect(Rect2(Vector2.ZERO, size), DesignTokens.TV_UI_0)
	_draw_cover()
	var tierra := DesignTokens.TV_ECO_3 if purified_count() > 0 else DesignTokens.TV_UI_6
	_big("Ecos de la", NAME_AT, 3, DesignTokens.TV_UI_6)
	_big("Tierra", NAME_AT + Vector2(0, 62), 5, tierra)
	for i in TAGLINE.size():
		TvFrame.slate_text(self, _font, TAGLINE_AT + Vector2(0, 13 * i), TAGLINE[i], DesignTokens.TV_UI_4)
	for i in ENTRIES.size():
		var y := MENU_AT.y + ROW * i
		var on := i == focused
		if on:
			TvFrame.slate_text(self, _font, Vector2(MENU_AT.x, y), "▶", DesignTokens.TV_TEXT_HIGHLIGHT)
		TvFrame.slate_text(self, _font, Vector2(MENU_AT.x + 12, y), ENTRIES[i],
			DesignTokens.TV_TEXT_HIGHLIGHT if on else DesignTokens.TV_TEXT_ON_SLATE)
	TvFrame.slate_text(self, _font, Vector2(MENU_AT.x, 346), status_text(), DesignTokens.TV_UI_4)
	if showing != "":
		_draw_note(showing, lines_of(showing))


## La portada, a la derecha: Valdehoja que sana de izquierda a derecha
## (`tools/gen_title_cover.py`). Con las bandas planas de `Cover` a 640 × 360
## las losetas de 32 px parecían relleno, así que la idea del componente se
## hace con el arte del juego. Una línea de tinta la separa de la columna.
func _draw_cover() -> void:
	draw_texture(COVER, Vector2(COVER_X, 0))
	draw_rect(Rect2(COVER_X - 2, 0, 2, 360), DesignTokens.TV_INK_0)


func _draw_note(title: String, lines: PackedStringArray) -> void:
	TvFrame.draw(self, TvFrame.TEXTBOX, NOTE)
	TvFrame.paper_text(self, _font, NOTE.position + Vector2(12, 20), title)
	for i in lines.size():
		TvFrame.paper_text(self, _font, NOTE.position + Vector2(12, 38 + 13 * i), lines[i])
	var hint := "Enter para volver"
	TvFrame.paper_text(self, _font, NOTE.end - Vector2(TvFrame.width(_font, hint) + 12, 8), hint)


## Texto a escala entera con la sombra de tinta de la portada (6 px con 66 px
## de letra: un píxel por cada 11 de alto).
func _big(text: String, at: Vector2, scale_: int, color: Color) -> void:
	var size_ := DesignTokens.FONT_SIZE_BODY * scale_
	var shadow := Vector2(scale_, scale_)
	draw_string(_font, at + shadow, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_, DesignTokens.TV_INK_0)
	draw_string(_font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size_, color)
