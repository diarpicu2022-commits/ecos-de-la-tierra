class_name ActionMenu
extends Control

## Menú de acción del turno. Es donde se toma la decisión, así que es el
## componente con más peso de la banda C del layout.
##
## Es **genérico a propósito**: recibe una lista de entradas y no sabe si son
## las cuatro opciones de la raíz, las Habilidades Ecológicas de un personaje o
## los objetos de la Bolsa. Los tres menús se comportan igual, y el jugador solo
## tiene que aprender a manejar uno.
##
## Cada entrada es un diccionario:
##   label       texto visible
##   description explicación que aparece a la derecha, en el área de mensaje
##   enabled     si se puede elegir ahora mismo
##   cost        energía que cuesta, o -1 si no cuesta
##   payload     lo que el llamante necesite recuperar al elegir
##
## Las entradas que no se pueden pagar **no se ocultan ni se apagan en gris
## mudo**: se muestran con el coste en rojo. Es la corrección al fallo del port
## de Final Fantasy VI que se registró en la fase 3: el gris solo frustra,
## mientras que ver el coste enseña cuánta energía falta.

signal option_focused(entry: Dictionary)
signal option_chosen(entry: Dictionary)
signal cancelled()

const ROW_HEIGHT := 12
const CURSOR := "▶"
const CURSOR_WIDTH := 8.0

var entries: Array[Dictionary] = []
var focused: int = 0

var _font: Font = null
var _active: bool = false
var _cursor_y: float = 0.0
var _cursor_tween: Tween = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	focus_mode = Control.FOCUS_ALL
	set_process_input(false)


## Carga las entradas y enfoca la primera que se pueda elegir.
func set_entries(new_entries: Array) -> void:
	entries.clear()
	for entry in new_entries:
		entries.append(entry as Dictionary)
	focused = _first_selectable()
	_cursor_y = _row_top(focused)
	queue_redraw()
	_announce_focus()


## Abre el menú y le cede el teclado. La entrada dura 160 ms y arranca en 0.94:
## empezar en cero se leería como un fallo de dibujo, no como una apertura.
func open() -> void:
	_active = true
	set_process_input(true)
	visible = true
	grab_focus()

	pivot_offset = Vector2(0, size.y * 0.5)
	if DesignTokens.reduced_motion:
		scale = Vector2.ONE
		modulate.a = 1.0
	else:
		scale = Vector2(DesignTokens.MENU_IN_SCALE, DesignTokens.MENU_IN_SCALE)
		modulate.a = 0.0
		var tween := create_tween()
		tween.set_trans(DesignTokens.EASE_OUT_TRANS)
		tween.set_ease(DesignTokens.EASE_OUT_EASE)
		tween.tween_property(self, "scale", Vector2.ONE, DesignTokens.DUR_MENU_IN)
		tween.parallel().tween_property(self, "modulate:a", 1.0,
				DesignTokens.DUR_MENU_IN)
	queue_redraw()


func close() -> void:
	_active = false
	set_process_input(false)
	visible = false


func is_active() -> bool:
	return _active


# --- Teclado -----------------------------------------------------------------

func _input(event: InputEvent) -> void:
	if not _active or not event.is_pressed():
		return

	if event.is_action("move_down"):
		_move(1)
	elif event.is_action("move_up"):
		_move(-1)
	elif event.is_action("confirm"):
		_confirm()
	elif event.is_action("cancel"):
		cancelled.emit()
	else:
		return
	get_viewport().set_input_as_handled()


## Salta a la siguiente entrada, dando la vuelta al llegar al final. Las
## entradas deshabilitadas **sí** reciben el cursor: el jugador tiene que poder
## leer por qué no puede usarlas.
func _move(direction: int) -> void:
	if entries.is_empty():
		return
	focused = wrapi(focused + direction, 0, entries.size())
	_tween_cursor()
	_announce_focus()


func _confirm() -> void:
	if focused < 0 or focused >= entries.size():
		return
	var entry: Dictionary = entries[focused]
	if not entry.get("enabled", true):
		return
	option_chosen.emit(entry)


func _announce_focus() -> void:
	if focused >= 0 and focused < entries.size():
		option_focused.emit(entries[focused])


func _tween_cursor() -> void:
	if _cursor_tween != null and _cursor_tween.is_valid():
		_cursor_tween.kill()
	if DesignTokens.reduced_motion:
		_cursor_y = _row_top(focused)
		queue_redraw()
		return
	_cursor_tween = create_tween()
	_cursor_tween.set_trans(DesignTokens.EASE_OUT_TRANS)
	_cursor_tween.set_ease(DesignTokens.EASE_OUT_EASE)
	_cursor_tween.tween_method(_set_cursor_y, _cursor_y, _row_top(focused),
			DesignTokens.DUR_CURSOR)


func _set_cursor_y(value: float) -> void:
	_cursor_y = value
	queue_redraw()


func _first_selectable() -> int:
	for i in range(entries.size()):
		if entries[i].get("enabled", true):
			return i
	return 0


func _row_top(index: int) -> float:
	return float(index * ROW_HEIGHT)


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	if entries.is_empty():
		return

	# El cursor se dibuja como una banda, no solo como una flecha: a 11 px de
	# texto una flecha sola no basta para saber dónde estás de un vistazo.
	var band := Rect2(Vector2(0, roundf(_cursor_y)),
			Vector2(size.x, ROW_HEIGHT))
	draw_rect(band, DesignTokens.PANEL_FILL_DEEP)
	draw_rect(Rect2(band.position, Vector2(2, band.size.y)),
			DesignTokens.BORDER_FOCUS)

	for i in range(entries.size()):
		_draw_row(i, entries[i])


func _draw_row(index: int, entry: Dictionary) -> void:
	var top: float = _row_top(index)
	var baseline: float = top + 9.0
	var is_focused: bool = index == focused
	var enabled: bool = entry.get("enabled", true)

	if is_focused:
		draw_string(_font, Vector2(0, baseline), CURSOR,
				HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
				DesignTokens.TEXT_CRITICAL)

	# El coste va a la derecha, y en rojo cuando no alcanza. Así el jugador ve
	# cuánta energía le falta en vez de encontrarse una opción muerta.
	var cost: int = int(entry.get("cost", -1))
	var cost_label: String = "%d" % cost if cost >= 0 else ""
	var reserved: float = 0.0 if cost_label.is_empty() \
			else _width(cost_label) + DesignTokens.SPACE_4

	var tone: Color = DesignTokens.TEXT_PRIMARY if is_focused \
			else DesignTokens.TEXT_SECONDARY
	# La etiqueta se recorta a lo que queda entre el cursor y el coste. Sin
	# esto, un objetivo llamado «Espectro del Monocultivo» se salía del menú y
	# se metía encima del mensaje de al lado.
	draw_string(_font, Vector2(CURSOR_WIDTH, baseline),
			_fit(str(entry.get("label", "")), size.x - CURSOR_WIDTH - reserved),
			HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY, tone)

	if not cost_label.is_empty():
		var color: Color = DesignTokens.TEXT_SECONDARY if enabled \
				else DesignTokens.TEXT_WARNING
		draw_string(_font, Vector2(size.x - _width(cost_label), baseline),
				cost_label, HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY, color)


func _width(text: String) -> float:
	return _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY).x


## Recorta una etiqueta que no quepa y la cierra con un punto. Desbordar sería
## peor que perder tres letras: el texto se montaría sobre lo que tenga al lado.
func _fit(text: String, available: float) -> String:
	if _width(text) <= available:
		return text
	var trimmed: String = text
	while trimmed.length() > 1 and _width(trimmed + ".") > available:
		trimmed = trimmed.substr(0, trimmed.length() - 1)
	return trimmed.strip_edges() + "."
