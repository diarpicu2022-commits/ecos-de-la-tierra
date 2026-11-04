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
## A doble tamaño una cifra de tres dígitos mide unos 36 px.
const FAN := 28.0
## Doble tamaño (README del sistema §Movimiento; guía del equipo §3.1, fila 13).
const SIZE := DesignTokens.FONT_SIZE_TITLE
## Alto de la celda a doble tamaño, para que la cifra no se salga por arriba.
const CELL_HEIGHT := 22.0
## Por encima de los monstruos, que llevan `z_index` propio y las tapaban, y por
## debajo de la pantalla de resultado (`ResultOverlay.FRONT_Z`).
const FRONT_Z := 50

## Al apagarse, la cifra baja un escalón de la rampa en lugar de fundirse con
## transparencia: mezclar alfa generaría colores que no son tokens, y la
## auditoría de paleta los marcaría como incumplimiento del contrato.
const DIM := {
	DesignTokens.TV_GOLD_4: DesignTokens.TV_GOLD_3,
	DesignTokens.TV_RUST_4: DesignTokens.TV_RUST_3,
	DesignTokens.TV_UI_6: DesignTokens.TV_UI_4,
	DesignTokens.TV_UI_4: DesignTokens.TV_UI_3,
}

var _font: Font = null
var _entries: Array[Dictionary] = []


func _ready() -> void:
	_font = load(DesignTokens.FONT_PATH)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = FRONT_Z
	set_process(false)


## Escribe una cifra sobre `anchor`, que es el centro superior del sprite.
func spawn(anchor: Vector2, text: String, color: Color) -> void:
	# Las cifras que salen a la vez sobre el mismo objetivo se abren en abanico:
	# dos golpes en área no pueden quedar uno encima del otro. La primera va en el
	# centro; las de objetivos distintos no se empujan entre sí.
	var same := 0
	for entry in _entries:
		if entry["anchor"] == anchor:
			same += 1
	var offset: float = (((same + 1) % 3) - 1) * FAN
	_entries.append({
		"anchor": anchor,
		"origin": anchor + Vector2(offset, 0.0),
		"text": text,
		"color": color,
		"elapsed": 0.0,
	})
	set_process(true)
	queue_redraw()


func clear() -> void:
	_entries.clear()
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
		set_process(false)
	queue_redraw()


func _draw() -> void:
	for entry in _entries:
		var t: float = float(entry["elapsed"]) / DesignTokens.DUR_DAMAGE_NUMBER
		var color: Color = entry["color"]
		# Último tramo: un escalón más apagado, y se va.
		if t > 0.62:
			color = DIM.get(color, DesignTokens.TV_UI_3)

		var text: String = entry["text"]
		var position := baseline_of(entry["origin"], text, t)

		# Sombra de 1 px: la cifra tiene que leerse sobre el sprite, que puede
		# ser tan claro como ella.
		draw_string(_font, position + Vector2.ONE, text,
				HORIZONTAL_ALIGNMENT_LEFT, -1, SIZE, DesignTokens.TV_INK_0)
		draw_string(_font, position, text, HORIZONTAL_ALIGNMENT_LEFT, -1, SIZE, color)


## Dónde se escribe `text` en el instante `t` (de 0 a 1): centrado sobre `origin`,
## subiendo y sin salirse de la pantalla, porque a doble tamaño un monstruo
## pegado al borde la cortaba.
func baseline_of(origin: Vector2, text: String, t: float) -> Vector2:
	var width: float = _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, SIZE).x
	# La subida se redondea a píxel entero: un desplazamiento fraccionario
	# rompería la rejilla de la que vive el pixel art.
	var rise: float = 0.0 if DesignTokens.reduced_motion else roundf(RISE * t)
	return Vector2(
		clampf(roundf(origin.x - width * 0.5), 0.0, maxf(0.0, size.x - width)),
		maxf(CELL_HEIGHT, origin.y - rise))
