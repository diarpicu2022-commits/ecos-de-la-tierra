class_name ActionMenu
extends Control

## Menú de acción del turno. Es donde se toma la decisión, así que es el
## componente con más peso de la banda C del layout.
##
## Es **genérico a propósito**: recibe una lista de entradas y no sabe si son las
## Habilidades Ecológicas de un personaje, los objetos de la Bolsa o los objetivos.
## Tiene dos formas:
##
##   rejilla  el `CommandMenu` del sistema de diseño, la raíz del turno: 2 × 2,
##            izquierda y derecha cambian de columna, arriba y abajo de fila, y
##            dan la vuelta. Escape vuelve al mando anterior.
##   lista    los submenús. Con `plate`, sobre el marco `TvFrame.PLATE` y con
##            texto de pizarra (guía §4.0). Sin él, como el selector de región,
##            que todavía no se ha rediseñado.
##
## Cada entrada es un diccionario:
##   label       texto visible
##   description explicación que aparece a la derecha, en el área de mensaje
##   enabled     si se puede elegir ahora mismo
##   cost        energía que cuesta, o -1 si no cuesta
##   payload     lo que el llamante necesite recuperar al elegir
##   frame       en la rejilla, el marco fijo del mando (`TvFrame.CMD_*`)
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
const GRID_COLUMNS := 2
## Sangría de la lista dentro de la placa.
const PLATE_PAD := float(DesignTokens.SPACE_4)

var entries: Array[Dictionary] = []
var focused: int = 0
## La lista se dibuja sobre `TvFrame.PLATE`, con texto de pizarra.
var plate := true

var _grid := false
## Mando del que se vino, para que Escape vuelva a él. -1 si no hay.
var _previous := -1

var _font: Font = null
var _active: bool = false
var _cursor_y: float = 0.0
var _cursor_tween: Tween = null


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	focus_mode = Control.FOCUS_ALL
	set_process_input(false)


## Carga las entradas y enfoca la primera que se pueda elegir, o `focus` si se
## pide una. Con `grid`, en la rejilla del `CommandMenu`.
func set_entries(new_entries: Array, grid: bool = false, focus: int = -1) -> void:
	replace_entries(new_entries)
	_grid = grid
	_previous = -1
	focused = focus if focus >= 0 and focus < entries.size() else _first_selectable()
	_cursor_y = _row_top(focused)
	queue_redraw()
	_announce_focus()


## Cambia el contenido sin mover el foco ni anunciarlo.
func replace_entries(new_entries: Array) -> void:
	entries.clear()
	for entry in new_entries:
		entries.append(entry as Dictionary)
	queue_redraw()


func is_grid() -> bool:
	return _grid


## Rectángulo del mando `index` en la rejilla, relativo al menú.
func cell_rect(index: int) -> Rect2:
	var step := TvFrame.CMD_SIZE + TvFrame.CMD_GAP
	return Rect2(Vector2(index % GRID_COLUMNS, index / GRID_COLUMNS) * step, TvFrame.CMD_SIZE)


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
		if _grid:
			_move_grid(0, 1)
		else:
			_move(1)
	elif event.is_action("move_up"):
		if _grid:
			_move_grid(0, -1)
		else:
			_move(-1)
	elif _grid and event.is_action("move_left"):
		_move_grid(-1, 0)
	elif _grid and event.is_action("move_right"):
		_move_grid(1, 0)
	elif event.is_action("confirm"):
		_confirm()
	elif event.is_action("cancel"):
		GameAudio.play("ui_cancel")
		_back_to_previous()
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
	GameAudio.play("ui_move")
	_tween_cursor()
	_announce_focus()


## El anillo salta de mando en mando, sin recorrido, como en `preview.html`. Las
## entradas deshabilitadas reciben foco, igual que en la lista.
func _move_grid(dx: int, dy: int) -> void:
	if entries.is_empty():
		return
	var rows: int = ceili(float(entries.size()) / GRID_COLUMNS)
	var column: int = wrapi(focused % GRID_COLUMNS + dx, 0, GRID_COLUMNS)
	var row: int = wrapi(focused / GRID_COLUMNS + dy, 0, rows)
	_previous = focused
	focused = mini(row * GRID_COLUMNS + column, entries.size() - 1)
	GameAudio.play("ui_move")
	queue_redraw()
	_announce_focus()


## Escape en la rejilla: vuelve al mando anterior, una sola vez.
func _back_to_previous() -> void:
	if not _grid or _previous < 0:
		return
	focused = _previous
	_previous = -1
	queue_redraw()
	_announce_focus()


func _confirm() -> void:
	if focused < 0 or focused >= entries.size():
		return
	var entry: Dictionary = entries[focused]
	if not entry.get("enabled", true):
		GameAudio.play("ui_denied")
		return
	GameAudio.play("ui_confirm")
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
	return (TvFrame.PLATE_EDGE_TOP if plate else 0.0) + float(index * ROW_HEIGHT)


## Cuántas filas caben en el alto útil de la placa.
func list_capacity() -> int:
	return floori((size.y - TvFrame.PLATE_EDGE_TOP - TvFrame.PLATE_EDGE_BOTTOM) / ROW_HEIGHT)


## Ancho que le queda a la etiqueta entre el cursor y el coste.
func label_room(entry: Dictionary) -> float:
	var pad := PLATE_PAD
	var cost: int = int(entry.get("cost", -1))
	var reserved: float = 0.0 if cost < 0 else _width("%d" % cost) + DesignTokens.SPACE_4
	return size.x - pad * 2.0 - CURSOR_WIDTH - reserved


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	if entries.is_empty():
		return

	if _grid:
		for i in range(entries.size()):
			TvFrame.command(self, _font, str(entries[i].get("frame", TvFrame.CMD_FIGHT)),
					cell_rect(i), str(entries[i].get("label", "")), i == focused)
		return

	# El cursor se dibuja como una banda, no solo como una flecha: a 11 px de
	# texto una flecha sola no basta para saber dónde estás de un vistazo.
	TvFrame.draw(self, TvFrame.PLATE, Rect2(Vector2.ZERO, size))
	# `TV_UI_0` y no `TV_UI_2`: el coste en aviso no llega a 4,5:1 sobre la
	# segunda, y la banda es justo donde se lee.
	draw_rect(Rect2(TvFrame.PLATE_EDGE_SIDE, roundf(_cursor_y),
			size.x - TvFrame.PLATE_EDGE_SIDE * 2.0, ROW_HEIGHT), DesignTokens.TV_UI_0)

	for i in range(entries.size()):
		_draw_row(i, entries[i])


func _draw_row(index: int, entry: Dictionary) -> void:
	var top: float = _row_top(index)
	var baseline: float = top + 9.0
	var is_focused: bool = index == focused
	var enabled: bool = entry.get("enabled", true)
	var pad := PLATE_PAD

	if is_focused:
		_row_text(pad, baseline, CURSOR, DesignTokens.TV_TEXT_HIGHLIGHT)

	# La etiqueta se recorta a lo que queda entre el cursor y el coste. Sin
	# esto, un objetivo llamado «Espectro del Monocultivo» se salía del menú y
	# se metía encima del mensaje de al lado.
	var tone: Color = DesignTokens.TV_TEXT_HIGHLIGHT if is_focused else DesignTokens.TV_TEXT_ON_SLATE
	_row_text(pad + CURSOR_WIDTH, baseline,
			_fit(str(entry.get("label", "")), label_room(entry)), tone)

	# El coste va a la derecha, y en su tono de aviso cuando no alcanza. Así el
	# jugador ve cuánta energía le falta en vez de encontrarse una opción muerta.
	var cost: int = int(entry.get("cost", -1))
	if cost >= 0:
		var cost_label: String = "%d" % cost
		var color: Color = DesignTokens.TV_RUST_4
		if enabled:
			color = DesignTokens.TV_TEXT_MUTED_SLATE
		_row_text(size.x - pad - _width(cost_label), baseline, cost_label, color)


func _row_text(x: float, baseline: float, value: String, color: Color) -> void:
	TvFrame.slate_text(self, _font, Vector2(x, baseline), value, color)


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
