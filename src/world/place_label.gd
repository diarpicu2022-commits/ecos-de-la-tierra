class_name PlaceLabel
extends Node2D

## Rótulo de lugar. Contrato «Umbral» y «Vereda»: el nombre de la zona al
## entrar, arriba a la izquierda con margen `SPACE_8`, panel `PANEL_FILL` con
## borde `BORDER_IDLE` de 1 px y texto 1x en `TEXT_PRIMARY` (repertorio de la
## guía §3.1: «panel `ASH_800` + borde `ASH_600`, todo texto que se lee»).
##
## Entra en `DUR_PLACE_LABEL` con la curva de salida de la batalla, se queda
## `PLACE_LABEL_HOLD` y se va solo en `DUR_PLACE_LABEL`. Solo se anima la
## opacidad (`modulate`). Con movimiento reducido entra y se va de golpe, pero
## la espera se mantiene: es tiempo para leer, no una animación (decisión
## confirmada por Diego el 2026-09-30).
##
## Se cuenta en cuadros de física, no con un `Tween`: así la prueba puede
## medir cada fase cuadro a cuadro y el resultado no depende del reloj.

enum Phase { HIDDEN, IN, HOLD, OUT }

var phase := Phase.HIDDEN
var text := ""

var _font: Font = null
var _frame := 0
var _in_frames := 0
var _hold_frames := 0


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	position = Vector2(DesignTokens.SPACE_8, DesignTokens.SPACE_8)
	modulate.a = 0.0


## Enseña `name` desde el principio, aunque hubiera otro rótulo a medias.
func show_name(name: String) -> void:
	text = name
	var ticks := Engine.physics_ticks_per_second
	_in_frames = roundi(DesignTokens.duration(DesignTokens.DUR_PLACE_LABEL) * ticks)
	_hold_frames = roundi(DesignTokens.PLACE_LABEL_HOLD * ticks)
	_frame = 0
	phase = Phase.IN if _in_frames > 0 else Phase.HOLD
	modulate.a = 0.0 if _in_frames > 0 else 1.0
	queue_redraw()


func _physics_process(_delta: float) -> void:
	match phase:
		Phase.IN:
			_frame += 1
			modulate.a = _eased(float(_frame) / _in_frames)
			if _frame >= _in_frames:
				_next(Phase.HOLD)
		Phase.HOLD:
			_frame += 1
			if _frame >= _hold_frames:
				if _in_frames > 0:
					_next(Phase.OUT)
				else:
					_next(Phase.HIDDEN)
					modulate.a = 0.0
		Phase.OUT:
			_frame += 1
			modulate.a = 1.0 - _eased(float(_frame) / _in_frames)
			if _frame >= _in_frames:
				_next(Phase.HIDDEN)
				modulate.a = 0.0


func _next(p: Phase) -> void:
	phase = p
	_frame = 0


func _eased(t: float) -> float:
	return Tween.interpolate_value(0.0, 1.0, clampf(t, 0.0, 1.0), 1.0,
		DesignTokens.EASE_OUT_TRANS, DesignTokens.EASE_OUT_EASE)


## Caja del panel en coordenadas de pantalla. La usan la prueba y `_draw`.
func panel_rect() -> Rect2i:
	var pad := DesignTokens.SPACE_4
	var width := int(_font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
		DesignTokens.FONT_SIZE_BODY).x) if _font != null else 0
	return Rect2i(Vector2i(position), Vector2i(width + pad * 2, DesignTokens.LINE_HEIGHT + pad * 2))


func _draw() -> void:
	if text.is_empty():
		return
	var box := Rect2(Vector2.ZERO, Vector2(panel_rect().size))
	draw_rect(box, DesignTokens.PANEL_FILL)
	draw_rect(box.grow(-0.5), DesignTokens.BORDER_IDLE, false, DesignTokens.BORDER_WIDTH)
	# Línea base de la fuente: 9 px dentro de su celda de 11.
	draw_string(_font, Vector2(DesignTokens.SPACE_4, DesignTokens.SPACE_4 + 9), text,
		HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY, DesignTokens.TEXT_PRIMARY)
