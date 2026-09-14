class_name PartyMemberHud
extends Control

## Fila de un personaje dentro de la ventana del grupo.
##
## El grupo se escalona en diagonal por el campo, de modo que cada miembro ocupa
## una altura distinta. La ventana los lista **en ese mismo orden vertical**:
## quien está más abajo en el campo está más abajo en la lista. Es el
## *third-best mapping* de la crítica de Final Fantasy VI recogida en la fase 3,
## aplicado a una composición diagonal en vez de a una fila recta.
##
## Antes era una columna de 96 px bajo cada sprite. Con el campo en diagonal esa
## correspondencia dejó de existir, y una lista vertical la recupera.

const ROW := Vector2(168, 16)
const PAD := DesignTokens.SPACE_4

## Umbrales de la barra de PV, los mismos que usa la ficha del monstruo.
const HP_WOUNDED := 0.55
const HP_CRITICAL := 0.25

var character: Character = null

var _font: Font = null
## PV mostrados en valor absoluto, no en proporción: así la cifra y la barra
## cuentan lo mismo mientras la barra se mueve.
var _shown_hp: float = 0.0
var _is_turn: bool = false
var _hp_tween: Tween = null

# Pausa durante la resolución síncrona del combate. Ver la explicación en
# MonsterView: la pantalla vuelca los cambios al ritmo del registro.
var _paused: bool = false
var _pending_hp: float = -1.0


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	custom_minimum_size = ROW
	size = ROW


func bind(target: Character) -> void:
	_disconnect_current()
	character = target
	if character == null:
		queue_redraw()
		return
	_shown_hp = float(character.hp)
	_pending_hp = -1.0
	character.hp_changed.connect(_on_hp_changed)
	character.energy_changed.connect(_on_any_change)
	character.status_applied.connect(_on_status_change)
	character.status_removed.connect(_on_status_change)
	character.defeated.connect(_on_any_change)
	queue_redraw()


## Marca de quién es el turno. Es la respuesta a «¿a quién le toca?», que la
## fase 2 pide resolver en menos de un segundo.
func set_active_turn(active: bool) -> void:
	if _is_turn == active:
		return
	_is_turn = active
	queue_redraw()


func _disconnect_current() -> void:
	if character == null:
		return
	for signal_name in ["hp_changed", "energy_changed", "status_applied",
			"status_removed", "defeated"]:
		for connection in character.get_signal_connection_list(signal_name):
			if connection["callable"].get_object() == self:
				character.disconnect(signal_name, connection["callable"])


func set_paused(value: bool) -> void:
	_paused = value


## Muestra lo que quedó pendiente mientras la vista estaba en pausa.
func flush() -> void:
	if _pending_hp < 0.0:
		queue_redraw()
		return
	var target: float = _pending_hp
	_pending_hp = -1.0
	_tween_hp(target)


func _on_hp_changed(current: int, _maximum: int) -> void:
	if _paused:
		_pending_hp = float(current)
		return
	_tween_hp(float(current))


func _tween_hp(target: float) -> void:
	if _hp_tween != null and _hp_tween.is_valid():
		_hp_tween.kill()
	if DesignTokens.reduced_motion:
		_shown_hp = target
		queue_redraw()
		return
	_hp_tween = create_tween()
	_hp_tween.set_trans(DesignTokens.EASE_OUT_TRANS)
	_hp_tween.set_ease(DesignTokens.EASE_OUT_EASE)
	_hp_tween.tween_method(_set_shown_hp, _shown_hp, target, DesignTokens.DUR_BAR)


func _set_shown_hp(value: float) -> void:
	_shown_hp = value
	queue_redraw()


func _ratio() -> float:
	if character == null or character.max_hp <= 0:
		return 0.0
	return clampf(_shown_hp / float(character.max_hp), 0.0, 1.0)


func _on_status_change(_effect: StatusEffect) -> void:
	queue_redraw()


func _on_any_change(_a = null, _b = null) -> void:
	queue_redraw()


# --- Dibujo ------------------------------------------------------------------

func _draw() -> void:
	if character == null:
		return

	var down: bool = not character.is_alive()

	if _is_turn:
		# A quien le toca se le ilumina la fila entera, no solo el nombre: es lo
		# primero que hay que poder localizar sin buscar.
		draw_rect(Rect2(Vector2.ZERO, ROW), DesignTokens.PANEL_FILL)
		draw_rect(Rect2(Vector2.ZERO, Vector2(2, ROW.y)),
				DesignTokens.BORDER_FOCUS)

	var name_tone: Color = DesignTokens.TEXT_PRIMARY
	if down:
		name_tone = DesignTokens.TEXT_SECONDARY
	elif _is_turn:
		name_tone = DesignTokens.TEXT_CRITICAL
	_text(character.display_name, Vector2(PAD + 2.0, 10), name_tone)

	# Estado alterado o «fuera de combate», justo tras el nombre: es lo que
	# cambia lo que el jugador puede hacer con este personaje.
	var flag: String = _status_flag(down)
	if not flag.is_empty():
		_text(flag, Vector2(PAD + 44.0, 10), DesignTokens.TEXT_WARNING)

	# Energía: la cifra que decide si una Habilidad Ecológica se puede pagar.
	var energy := "%d" % character.energy
	_text(energy, Vector2(ROW.x - PAD - 54.0 - _width(energy), 10),
			DesignTokens.ASH_200)

	var hp_label := "%d/%d" % [roundi(_shown_hp), character.max_hp]
	_text(hp_label, Vector2(ROW.x - PAD - _width(hp_label), 10), _hp_tone(down))

	_bar(Vector2(PAD + 2.0, 12), ROW.x - PAD * 2.0 - 4.0, 3, _ratio(),
			_hp_fill(down))


## Marca corta del estado. A 168 px no cabe «Aturdimiento», y lo que importa es
## que haya algo raro con este personaje: el detalle lo da el registro.
func _status_flag(down: bool) -> String:
	if down:
		return "✖ fuera"
	var statuses: Array[StatusEffect] = character.get_statuses()
	if statuses.is_empty():
		return ""
	for effect in statuses:
		if effect.blocks_action():
			return effect.display_name.substr(0, 4) + "."
	return statuses[0].display_name.substr(0, 4) + "."


func _hp_fill(down: bool) -> Color:
	if down:
		return DesignTokens.ASH_600
	var ratio: float = _ratio()
	if ratio <= HP_CRITICAL:
		return DesignTokens.EMBER_500
	if ratio <= HP_WOUNDED:
		return DesignTokens.EMBER_400
	return DesignTokens.ASH_050


func _hp_tone(down: bool) -> Color:
	if down:
		return DesignTokens.TEXT_SECONDARY
	return DesignTokens.TEXT_CRITICAL if _ratio() <= HP_CRITICAL \
			else DesignTokens.TEXT_PRIMARY


func _bar(origin: Vector2, width: float, height: float, ratio: float,
		fill: Color) -> void:
	draw_rect(Rect2(origin, Vector2(width, height)), DesignTokens.BAR_TRACK)
	if ratio > 0.0:
		# Al menos 1 px mientras quede algo: una barra a cero diría que no hay
		# nada, y eso es otra información.
		draw_rect(Rect2(origin, Vector2(maxf(1.0, roundf(width * ratio)), height)),
				fill)


func _text(text: String, position: Vector2, color: Color) -> void:
	draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY, color)


func _width(text: String) -> float:
	return _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
			DesignTokens.FONT_SIZE_BODY).x
