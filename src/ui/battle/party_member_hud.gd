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

## 176 × 24, las filas a 27 px (`PartyRow`).
const ROW := Vector2(176, 24)
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


## Saca lo pendiente hasta ahora (ver `MonsterView.take_pending`).
func take_pending() -> float:
	var pending := _pending_hp
	_pending_hp = -1.0
	return pending


## Muestra lo sacado con `take_pending`.
func show_pending(target: float) -> void:
	if target < 0.0:
		queue_redraw()
		return
	_tween_hp(target)


## Muestra lo que quedó pendiente mientras la vista estaba en pausa.
func flush() -> void:
	show_pending(take_pending())


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

## `PartyRow` del sistema de diseño: marco `f-row` (pizarra) o `f-active`
## con borde de oro para quien tiene el turno; nombre, chapa de estado y PV
## arriba; barra de PV de 5 px y, debajo, la de energía de 4 px.
func _draw() -> void:
	if character == null:
		return
	var down: bool = not character.is_alive()
	TvFrame.draw(self, TvFrame.PLATE_ACTIVE if _is_turn else TvFrame.ROW, Rect2(Vector2.ZERO, ROW))
	var name_tone: Color = DesignTokens.TV_TEXT_HIGHLIGHT if _is_turn \
			else DesignTokens.TV_TEXT_ON_SLATE
	if down:
		name_tone = DesignTokens.TV_UI_3
	TvFrame.slate_text(self, _font, Vector2(PAD + 2.0, 11), character.display_name, name_tone)
	var flag: String = _status_flag(down)
	if not flag.is_empty():
		var x := PAD + 6.0 + TvFrame.width(_font, character.display_name)
		TvFrame.badge(self, _font, Vector2(x, 3), flag, DesignTokens.TV_STATUS_CORRUPT,
				DesignTokens.TV_PAPER_4)
	var hp_label := "%d/%d" % [roundi(_shown_hp), character.max_hp]
	TvFrame.slate_text(self, _font, Vector2(ROW.x - PAD - 2.0 - TvFrame.width(_font, hp_label), 11),
			hp_label, DesignTokens.TV_TEXT_MUTED_SLATE)
	var w := ROW.x - PAD * 2.0 - 4.0
	TvFrame.bar(self, Vector2(PAD + 2.0, 13), w, 5, _ratio(),
			DesignTokens.TV_UI_3 if down else TvFrame.hp_fill(_ratio()))
	var energy_ratio := 0.0 if character.max_energy <= 0 \
			else clampf(float(character.energy) / character.max_energy, 0.0, 1.0)
	TvFrame.bar(self, Vector2(PAD + 2.0, 18), w, 4, energy_ratio, DesignTokens.TV_ENERGY)


## Marca corta del estado. A 168 px no cabe «Aturdimiento», y lo que importa es
## que haya algo raro con este personaje: el detalle lo da el registro.
func _status_flag(down: bool) -> String:
	if down:
		return "FUERA"
	var statuses: Array[StatusEffect] = character.get_statuses()
	if statuses.is_empty():
		return ""
	for effect in statuses:
		if effect.blocks_action():
			return effect.display_name.substr(0, 4).to_upper() + "."
	return statuses[0].display_name.substr(0, 4).to_upper() + "."


func _hp_fill(down: bool) -> Color:
	if down:
		return DesignTokens.TV_UI_2
	var ratio: float = _ratio()
	if ratio <= HP_CRITICAL:
		return DesignTokens.TV_HP_LOW
	if ratio <= HP_WOUNDED:
		return DesignTokens.TV_HP_MID
	return DesignTokens.TV_HP_HIGH


func _hp_tone(down: bool) -> Color:
	if down:
		return DesignTokens.TEXT_SECONDARY
	return DesignTokens.TEXT_CRITICAL if _ratio() <= HP_CRITICAL \
			else DesignTokens.TEXT_PRIMARY


func _bar(origin: Vector2, width: float, height: float, ratio: float,
		fill: Color) -> void:
	draw_rect(Rect2(origin, Vector2(width, height)), DesignTokens.TV_INK_1)
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
