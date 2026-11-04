class_name DamageNumbers
extends Control

## Cifras que suben sobre el objetivo al recibir un golpe o una curación.
##
## Cierra la fila «¿qué acaba de pasar?» de la tabla de la fase 2. El registro
## ya narraba el resultado, pero con varios enemigos en el campo había que leer
## el nombre en la frase para saber a quién le había tocado. La cifra sobre el
## sprite lo resuelve sin leer.
##
## **La cifra también enseña la regla del juego.** Un golpe que el monstruo
## resiste por no atacar la causa real sale apagado y con `~` delante; uno que
## sí hace mella sale en brasa viva. El jugador ve la diferencia entre «le hice
## 3» y «le hice 24» sin que nadie se lo explique.

## La cifra sube 12 px en 260 ms. Es el `DUR_DAMAGE_NUMBER` del contrato.
const RISE := 12.0
## Reparto de las cifras simultáneas, para que no se apilen en el mismo píxel.
const FAN := 14.0

## Al apagarse, la cifra baja un escalón de la rampa en lugar de fundirse con
## transparencia: mezclar alfa generaría colores que no son tokens, y la
## auditoría de paleta los marcaría como incumplimiento del contrato.
const DIM := {
	DesignTokens.EMBER_300: DesignTokens.EMBER_400,
	DesignTokens.EMBER_400: DesignTokens.ASH_400,
	DesignTokens.ASH_050: DesignTokens.ASH_400,
	DesignTokens.ASH_400: DesignTokens.ASH_600,
}

var _font: Font = null
var _entries: Array[Dictionary] = []
var _fan_index: int = 0


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)


## Escribe una cifra sobre `anchor`, que es el centro superior del sprite.
func spawn(anchor: Vector2, text: String, color: Color) -> void:
	# Las cifras que salen a la vez se abren en abanico: dos golpes en área
	# sobre el mismo objetivo no pueden quedar uno encima del otro.
	var offset: float = (_fan_index % 3 - 1) * FAN
	_fan_index += 1
	_entries.append({
		"origin": anchor + Vector2(offset, 0.0),
		"text": text,
		"color": color,
		"elapsed": 0.0,
	})
	set_process(true)
	queue_redraw()


func clear() -> void:
	_entries.clear()
	_fan_index = 0
	set_process(false)
	queue_redraw()


func _process(delta: float) -> void:
	var alive: Array[Dictionary] = []
	for entry in _entries:
		entry["elapsed"] = float(entry["elapsed"]) + delta
		if float(entry["elapsed"]) < DesignTokens.DUR_DAMAGE_NUMBER:
			alive.append(entry)
	_entries = alive
	if _entries.is_empty():
		_fan_index = 0
		set_process(false)
	queue_redraw()


func _draw() -> void:
	for entry in _entries:
		var t: float = float(entry["elapsed"]) / DesignTokens.DUR_DAMAGE_NUMBER
		var color: Color = entry["color"]
		# Último tramo: un escalón más apagado, y se va.
		if t > 0.62:
			color = DIM.get(color, DesignTokens.ASH_400)

		var origin: Vector2 = entry["origin"]
		var text: String = entry["text"]
		var width: float = _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT,
				-1, DesignTokens.FONT_SIZE_BODY).x
		# La subida se redondea a píxel entero: un desplazamiento fraccionario
		# rompería la rejilla de la que vive el pixel art.
		var rise: float = 0.0 if DesignTokens.reduced_motion else roundf(RISE * t)
		var position := Vector2(roundf(origin.x - width * 0.5), origin.y - rise)

		# Sombra de 1 px: la cifra tiene que leerse sobre el sprite, que puede
		# ser tan claro como ella.
		draw_string(_font, position + Vector2.ONE, text,
				HORIZONTAL_ALIGNMENT_LEFT, -1, DesignTokens.FONT_SIZE_BODY,
				DesignTokens.ASH_950)
		draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1,
				DesignTokens.FONT_SIZE_BODY, color)
