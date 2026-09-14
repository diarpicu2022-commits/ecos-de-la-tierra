class_name TurnOrderStrip
extends Control

## Cola de turnos de la ronda en curso, en franja horizontal sobre el campo.
##
## Contesta a «quién actúa ahora **y quién sigue**», que es lo que decide si
## conviene curar ya o aguantar un turno más.
##
## Va en horizontal y no en columna porque el campo pasó a composición diagonal:
## las esquinas son ahora el sitio de las fichas de cada bando, y una columna
## lateral se comía el espacio donde el grupo se escalona.
##
## El orden lo recalcula `TurnManager` en cada ronda con la velocidad efectiva
## del momento, así que la lista **no** se prolonga a rondas futuras: un estado
## de lentitud puede cambiarla entera. Se muestra solo lo ya decidido, y se
## cierra con un tope para que quede claro dónde acaba lo seguro.

const HEIGHT := 13.0
const CHIP_WIDTH := 54.0
const TEAM_BAR := 2.0
const LABEL := "TURNOS"
## Cuántos turnos caben sin que la franja pise el ancho de la pantalla.
const MAX_CHIPS := 6

var _font: Font = null
var _current: Combatant = null
var _pending: Array[Combatant] = []


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(BattleScreen.SCREEN.x, HEIGHT)
	size = custom_minimum_size


## Turnos que quedan por jugarse, sin contar a quien actúa ahora.
func set_pending(order: Array) -> void:
	_pending.clear()
	for combatant in order:
		if combatant != null and (combatant as Combatant).is_alive():
			_pending.append(combatant as Combatant)
	queue_redraw()


func set_current(combatant: Combatant) -> void:
	_current = combatant
	queue_redraw()


func clear() -> void:
	_current = null
	_pending.clear()
	queue_redraw()


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(size.x, HEIGHT)),
			DesignTokens.PANEL_FILL_DEEP)

	var queue: Array[Combatant] = []
	if _current != null and _current.is_alive():
		queue.append(_current)
	queue.append_array(_pending)
	if queue.is_empty():
		return

	_text(LABEL, Vector2(DesignTokens.SPACE_4, 9.0),
			DesignTokens.TEXT_SECONDARY)

	var x: float = DesignTokens.SPACE_4 + _width(LABEL) + DesignTokens.SPACE_8
	var shown: int = mini(queue.size(), MAX_CHIPS)
	for i in range(shown):
		_draw_chip(queue[i], x, i == 0)
		x += CHIP_WIDTH

	if queue.size() > MAX_CHIPS:
		_text("+%d" % (queue.size() - MAX_CHIPS), Vector2(x + 2.0, 9.0),
				DesignTokens.TEXT_SECONDARY)


func _draw_chip(combatant: Combatant, left: float, is_current: bool) -> void:
	var chip := Rect2(Vector2(left, 1.0), Vector2(CHIP_WIDTH - 2.0, HEIGHT - 2.0))
	if is_current:
		draw_rect(chip, DesignTokens.PANEL_FILL)
		draw_rect(chip, DesignTokens.BORDER_FOCUS, false, DesignTokens.BORDER_WIDTH)

	# Barra de bando. El enemigo se marca en brasa, que en todo el juego
	# significa «causa activa»: no hace falta un color nuevo para decir «este
	# va contra ti».
	var team_color: Color = DesignTokens.EMBER_400 \
			if combatant.team == Enums.Team.ENEMY else DesignTokens.ASH_200
	draw_rect(Rect2(chip.position, Vector2(TEAM_BAR, chip.size.y)), team_color)

	var tone: Color = DesignTokens.TEXT_CRITICAL if is_current \
			else DesignTokens.TEXT_SECONDARY
	_text(_short_name(combatant, CHIP_WIDTH - TEAM_BAR - 6.0),
			Vector2(left + TEAM_BAR + 3.0, 9.0), tone)


## Primera palabra del nombre. «Llama de la Deforestación» no cabe en un chip, y
## «Llama» basta para reconocerlo cuando su sprite está en pantalla.
func _short_name(combatant: Combatant, available: float) -> String:
	var parts: PackedStringArray = combatant.display_name.split(" ", false)
	var label: String = parts[0] if parts.size() > 0 else combatant.display_name
	while label.length() > 1 and _width(label) > available:
		label = label.substr(0, label.length() - 1)
	return label


func _text(text: String, position: Vector2, color: Color) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, color)


func _width(text: String) -> float:
	return _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY).x
