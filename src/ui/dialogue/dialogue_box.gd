class_name DialogueBox
extends Control

## La caja de diálogo (contrato «Columna», docs/ux/anexos/
## 2026-10-28-dialogos.md). Panel del repertorio de 312 × 52 px, pegado abajo
## y al lado de quien habla, con el retrato en el lado exterior.
##
## - El texto se **parte en líneas antes de escribirse** (palabras enteras,
##   DIALOGUE_CHARS por línea, DIALOGUE_LINES como mucho): ninguna palabra
##   salta de línea mientras aparece.
## - Máquina de escribir opcional: un carácter cada DUR_TYPE_CHAR y una pausa
##   de DUR_TYPE_PAUSE tras la puntuación. Se cuenta en cuadros de física para
##   que la prueba la mida.
## - `confirm`: si la línea se escribe, la completa; si está completa, avanza
##   (`advanced`). Nunca avanza sola.
## - Con movimiento reducido o la máquina apagada, el texto sale completo.

signal advanced

enum Side { LEFT, RIGHT }

const CONTINUE := "▼"

## Opción del jugador (parte 10). Encendida por defecto.
static var typewriter_enabled := true

var side: int = Side.LEFT
var speaker := ""
var name_color: Color = DesignTokens.TEXT_SECONDARY
var portrait: Texture2D = null
## Líneas ya partidas y caracteres visibles de su total.
var lines: PackedStringArray = []
var visible_chars := 0
var total_chars := 0

var _font: Font = null
var _wait := 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(DesignTokens.DIALOGUE_SIZE)
	visible = false


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	set_physics_process(false)


## Parte `text` en líneas de como mucho DIALOGUE_CHARS caracteres, por palabras.
## Si sobran líneas, las devuelve igual: `verify_dialogue.py` impide que
## lleguen al juego, y la caja no aprieta el cuerpo para que quepan.
static func wrap_text(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	var current := ""
	for word in text.split(" ", false):
		var candidate := word if current.is_empty() else current + " " + word
		if candidate.length() <= DesignTokens.DIALOGUE_CHARS:
			current = candidate
		else:
			if not current.is_empty():
				out.append(current)
			current = word
	if not current.is_empty():
		out.append(current)
	return out


## Muestra una línea de diálogo. `side` decide dónde va la caja; el retrato
## queda siempre en el lado exterior.
func show_line(who: String, text: String, from: int, face: Texture2D = null,
		who_color: Color = DesignTokens.TEXT_SECONDARY) -> void:
	speaker = who
	side = from
	portrait = face
	name_color = who_color
	lines = wrap_text(text)
	total_chars = 0
	for l in lines:
		total_chars += l.length()
	var screen := get_viewport_rect().size
	var x := DesignTokens.DIALOGUE_MARGIN if side == Side.LEFT \
		else int(screen.x) - DesignTokens.DIALOGUE_MARGIN - DesignTokens.DIALOGUE_SIZE.x
	position = Vector2(x, int(screen.y) - DesignTokens.DIALOGUE_MARGIN - DesignTokens.DIALOGUE_SIZE.y)
	visible = true
	if DesignTokens.reduced_motion or not typewriter_enabled:
		visible_chars = total_chars
	else:
		visible_chars = 0
		_wait = 0
	set_physics_process(visible_chars < total_chars)
	queue_redraw()


func close() -> void:
	visible = false
	set_physics_process(false)


func is_complete() -> bool:
	return visible_chars >= total_chars


## `confirm`: completa o avanza.
func confirm() -> void:
	if not is_complete():
		visible_chars = total_chars
		set_physics_process(false)
		queue_redraw()
	else:
		advanced.emit()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("confirm"):
		get_viewport().set_input_as_handled()
		confirm()


func _physics_process(_delta: float) -> void:
	if _wait > 0:
		_wait -= 1
		return
	visible_chars += 1
	var ch := _char_at(visible_chars - 1)
	_wait = roundi(DesignTokens.DUR_TYPE_CHAR * Engine.physics_ticks_per_second) - 1
	if DesignTokens.TYPE_PAUSE_AFTER.contains(ch):
		_wait += roundi(DesignTokens.DUR_TYPE_PAUSE * Engine.physics_ticks_per_second)
	if is_complete():
		set_physics_process(false)
	queue_redraw()


func _char_at(index: int) -> String:
	for l in lines:
		if index < l.length():
			return l[index]
		index -= l.length()
	return ""


## Rectángulo del retrato y origen del texto, dentro de la caja.
func portrait_rect() -> Rect2:
	var p := DesignTokens.DIALOGUE_PADDING
	var x := p if side == Side.LEFT else DesignTokens.DIALOGUE_SIZE.x - p - DesignTokens.PORTRAIT_SIZE
	var y := (DesignTokens.DIALOGUE_SIZE.y - DesignTokens.PORTRAIT_SIZE) / 2
	return Rect2(x, y, DesignTokens.PORTRAIT_SIZE, DesignTokens.PORTRAIT_SIZE)


func text_rect() -> Rect2:
	var p := DesignTokens.DIALOGUE_PADDING
	var width := DesignTokens.DIALOGUE_SIZE.x - 2 * p - DesignTokens.PORTRAIT_SIZE - DesignTokens.PORTRAIT_GAP
	var x := p + DesignTokens.PORTRAIT_SIZE + DesignTokens.PORTRAIT_GAP if side == Side.LEFT else p
	return Rect2(x, p, width, DesignTokens.DIALOGUE_SIZE.y - 2 * p)


func _draw() -> void:
	var box := Rect2(Vector2.ZERO, Vector2(DesignTokens.DIALOGUE_SIZE))
	draw_rect(box, DesignTokens.PANEL_FILL)
	draw_rect(box, DesignTokens.BORDER_IDLE, false, DesignTokens.BORDER_WIDTH)
	var pr := portrait_rect()
	if portrait != null:
		draw_texture_rect(portrait, pr, false)
	else:
		draw_rect(pr, DesignTokens.PANEL_FILL_DEEP)
	var tr := text_rect()
	var line_h := DesignTokens.LINE_HEIGHT
	var size_px := DesignTokens.FONT_SIZE_BODY
	var ascent := _font.get_ascent(size_px)
	draw_string(_font, tr.position + Vector2(0, ascent), speaker, HORIZONTAL_ALIGNMENT_LEFT, -1,
		size_px, name_color)
	var left := visible_chars
	for i in lines.size():
		var shown := lines[i].substr(0, clampi(left, 0, lines[i].length()))
		left -= lines[i].length()
		draw_string(_font, tr.position + Vector2(0, line_h * (i + 1) + ascent), shown,
			HORIZONTAL_ALIGNMENT_LEFT, -1, size_px, DesignTokens.TEXT_PRIMARY)
	if is_complete():
		draw_string(_font, continue_origin() + Vector2(0, ascent), CONTINUE,
			HORIZONTAL_ALIGNMENT_LEFT, -1, size_px, DesignTokens.EMBER_300)


## Dónde va el ▼: en el hueco de 8 px justo a la derecha de la columna de
## texto, a la altura de la última línea. Dentro de la columna taparía la
## última letra de una línea de 40 caracteres.
func continue_origin() -> Vector2:
	var tr := text_rect()
	return Vector2(tr.end.x + 1, tr.position.y + DesignTokens.LINE_HEIGHT * DesignTokens.DIALOGUE_LINES)
