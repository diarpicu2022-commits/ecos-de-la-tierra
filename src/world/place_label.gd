class_name PlaceLabel
extends Node2D

## Cartel de lugar (`components/LocationSign` del sistema de diseño «Tierra
## Viva», guía del equipo §3.1, fila 15): tabla de madera con clavos (marco
## `TvFrame.SIGN`) arriba a la izquierda, en (12, 12), con el nombre de la
## zona en `paper-5` y, debajo, su estado o su apodo en `paper-4`, los dos con
## sombra `wood-2`. Sustituye al panel de ceniza del contrato «Umbral».
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

## Relleno horizontal del texto dentro del marco (`.sign { padding: 0 6px }`)
## y altura de cada línea.
const SIGN_PAD := 6
const SIGN_LINE := 12

var phase := Phase.HIDDEN
var text := ""
## Segunda línea: el estado de la zona o su apodo. Vacía, el cartel lleva una.
var subtitle := ""

var _font: Font = null
var _frame := 0
var _in_frames := 0
var _hold_frames := 0


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	position = Vector2(DesignTokens.SPACE_12, DesignTokens.SPACE_12)
	modulate.a = 0.0


## Enseña `name` (y `sub` debajo) desde el principio, aunque hubiera otro
## cartel a medias.
func show_name(name: String, sub: String = "") -> void:
	text = name
	subtitle = sub
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


## Caja del cartel en coordenadas de pantalla. La usan la prueba y `_draw`.
func panel_rect() -> Rect2i:
	var inset := TvFrame.SLICE
	var width := 0
	if _font != null:
		width = int(maxf(TvFrame.width(_font, text), TvFrame.width(_font, subtitle)))
	var lines := 1 if subtitle.is_empty() else 2
	return Rect2i(Vector2i(position), Vector2i(width + (inset + SIGN_PAD) * 2,
		inset * 2 + DesignTokens.FONT_SIZE_BODY + SIGN_LINE * (lines - 1)))


func _draw() -> void:
	if text.is_empty():
		return
	var box := Rect2(Vector2.ZERO, Vector2(panel_rect().size))
	TvFrame.draw(self, TvFrame.SIGN, box)
	# Línea base de la fuente: 9 px dentro de su celda de 11. Centrado, como
	# en el sistema.
	var y := float(TvFrame.SLICE + 9)
	for line in [[text, DesignTokens.TV_PAPER_4], [subtitle, DesignTokens.TV_PAPER_3]]:
		if String(line[0]).is_empty():
			continue
		var x := roundf((box.size.x - TvFrame.width(_font, line[0])) * 0.5)
		TvFrame.text(self, _font, Vector2(x, y), line[0], line[1], DesignTokens.TV_WOOD_1)
		y += SIGN_LINE
