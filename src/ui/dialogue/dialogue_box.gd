class_name DialogueBox
extends Control

## La caja de diálogo del sistema de diseño (`components/DialogBox`): papel con
## marco de madera en (12, 276), de 616 × 76, con el retrato en su marco, la chapa
## con el nombre asomando por arriba, la hojita `eco` en la esquina y `▼` cuando
## la línea está entera. Sustituye al panel de ceniza del contrato «Columna»
## (propuesta pendiente de Diego; conserva su motor).
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
## Medidas dentro de la caja. El marco de nueve partes ocupa `TvFrame.SLICE`.
const PORTRAIT_FRAME := Vector2(56, 60)
const PORTRAIT_GAP := 10.0
const FIRST_BASELINE := 33.0
const LINE_GAP := 15.0
## La chapa del nombre asoma por encima de la caja.
const TAG_HEIGHT := 18.0
const TAG_RISE := 11.0
const TAG_PAD := 10.0
const TAG_BASELINE := 12.0
const LEAF := Rect2(3, 3, 3, 3)

## Opción del jugador (parte 10). Encendida por defecto.
static var typewriter_enabled := true

var side: int = Side.LEFT
var speaker := ""
var name_color: Color = DesignTokens.TV_TEXT_ON_SLATE
var portrait: Texture2D = null
## Líneas ya partidas y caracteres visibles de su total.
var lines: PackedStringArray = []
var visible_chars := 0
var total_chars := 0

var _font: Font = null
var _wait := 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	position = Vector2(DesignTokens.DIALOGUE_POSITION)
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


## Muestra una línea de diálogo. `from` decide de qué lado va el retrato: los de
## casa a la izquierda, los de fuera a la derecha.
func show_line(who: String, text: String, from: int, face: Texture2D = null,
		who_color: Color = DesignTokens.TV_TEXT_ON_SLATE) -> void:
	speaker = who
	side = from
	portrait = face
	name_color = who_color
	lines = wrap_text(text)
	total_chars = 0
	for l in lines:
		total_chars += l.length()
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


## El marco del retrato, dentro de la caja.
func portrait_frame() -> Rect2:
	var inset := float(TvFrame.SLICE)
	var x := inset if side == Side.LEFT else size.x - inset - PORTRAIT_FRAME.x
	return Rect2(Vector2(x, inset), PORTRAIT_FRAME)


## El retrato de 40 × 44, dentro de su marco.
func portrait_rect() -> Rect2:
	return portrait_frame().grow(-TvFrame.SLICE)


## La columna de texto.
func text_rect() -> Rect2:
	var inset := float(TvFrame.SLICE)
	var width := size.x - inset * 2.0 - PORTRAIT_FRAME.x - PORTRAIT_GAP
	var x := inset + PORTRAIT_FRAME.x + PORTRAIT_GAP if side == Side.LEFT else inset
	return Rect2(x, inset, width, size.y - inset * 2.0)


## La chapa con el nombre, sobre el arranque de la columna de texto.
func tag_rect() -> Rect2:
	var width := TvFrame.width(_font, speaker) + TAG_PAD * 2.0
	return Rect2(text_rect().position.x, -TAG_RISE, width, TAG_HEIGHT)


func continue_origin() -> Vector2:
	var tr := text_rect()
	return Vector2(tr.end.x - TvFrame.width(_font, CONTINUE), size.y - TvFrame.SLICE - 1.0)


func _draw() -> void:
	TvFrame.draw(self, TvFrame.TEXTBOX, Rect2(Vector2.ZERO, size))
	draw_rect(LEAF, DesignTokens.TV_ECO_4)
	TvFrame.draw(self, TvFrame.PORTRAIT, portrait_frame())
	if portrait != null:
		draw_texture_rect_region(portrait, portrait_rect(), _portrait_region())
	_draw_tag()
	var tr := text_rect()
	var left := visible_chars
	for i in lines.size():
		var shown := lines[i].substr(0, clampi(left, 0, lines[i].length()))
		left -= lines[i].length()
		TvFrame.paper_text(self, _font, Vector2(tr.position.x, FIRST_BASELINE + LINE_GAP * i), shown)
	if is_complete():
		draw_string(_font, continue_origin(), CONTINUE, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, DesignTokens.TV_RUST_2)


## Chapa `eco` con el nombre en blanco. Quien sirve a la Compañía (Rasgo) la lleva
## en pizarra con su nombre en fuego: sobre `eco` no se leería, y `eco` significa
## lo purificado.
func _draw_tag() -> void:
	var tag := tag_rect()
	var plain := name_color == DesignTokens.TV_TEXT_ON_SLATE
	TvFrame.draw(self, TvFrame.TAG if plain else TvFrame.PLATE, tag)
	TvFrame.text(self, _font, tag.position + Vector2(TAG_PAD, TAG_BASELINE), speaker, name_color,
		DesignTokens.TV_ECO_1 if plain else DesignTokens.TV_UI_0)


## Qué parte del retrato cabe en 40 × 44: los retratos de 48 × 48 se recortan por
## el centro y por abajo, sin escalar.
func _portrait_region() -> Rect2:
	var tex_size := portrait.get_size()
	var wanted := portrait_rect().size
	return Rect2(Vector2(roundf((tex_size.x - wanted.x) * 0.5), 0.0), wanted)
