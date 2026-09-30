class_name WorldCamera
extends Camera2D

## Cámara del mundo. Contrato «Vereda», cláusula «Cámara», y enmienda 5.
##
## Zona muerta de 28x48 px con el personaje 12 px por debajo del centro de la
## pantalla, y anticipación de hasta 30 px en la dirección del avance.
##
## `Camera2D` no tiene ajuste a píxel propio (anexo de exploración, B.1), y su
## suavizado y su arrastre trabajan en fracciones. Por eso los dos quedan
## apagados y toda la cuenta se hace aquí, en enteros: la cámara se mueve solo
## cuando el personaje empuja el borde de la zona o cuando la anticipación
## avanza un píxel, y nunca queda entre dos píxeles.

## A quién sigue. Su posición tiene que ser entera: lo garantiza el movimiento,
## que avanza píxeles enteros por cuadro (cláusula «Movimiento del personaje»).
var target: Node2D = null

## Desplazamiento actual de la anticipación, por eje. Nunca pasa de
## `CAMERA_LOOKAHEAD`.
var lookahead := Vector2i.ZERO

## Centro de la pantalla en coordenadas del mundo.
var center := Vector2i.ZERO

var _last_target := Vector2i.ZERO
## Presupuesto acumulado de la anticipación, en píxeles por tick: cuando llega
## a `Engine.physics_ticks_per_second`, se avanza un píxel. Así un ritmo de
## 30 px/s son exactamente dos cuadros por píxel, sin fracciones.
var _open_budget := Vector2i.ZERO
var _return_budget := Vector2i.ZERO


func _ready() -> void:
	position_smoothing_enabled = false
	drag_horizontal_enabled = false
	drag_vertical_enabled = false
	anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
	top_level = true
	# Después de quien mueve al personaje, para seguirlo en el mismo cuadro.
	process_physics_priority = 100
	if target != null:
		snap_to_target()


func _physics_process(_delta: float) -> void:
	if target != null:
		advance()


## Coloca la cámara en reposo sobre el objetivo, sin anticipación. Al entrar en
## una zona o al cargar partida.
func snap_to_target() -> void:
	var p := _target_position()
	center = p - bias()
	_last_target = p
	lookahead = Vector2i.ZERO
	_open_budget = Vector2i.ZERO
	_return_budget = Vector2i.ZERO
	global_position = Vector2(center)


## Un cuadro de cámara. Lo llama `_physics_process`; las pruebas lo llaman a
## mano para recorrer cientos de cuadros sin esperar al reloj.
func advance() -> void:
	var p := _target_position()
	var moved := p - _last_target
	_last_target = p
	_update_lookahead(moved)

	var zone := deadzone()
	for axis in 2:
		if p[axis] < zone.position[axis]:
			center[axis] -= zone.position[axis] - p[axis]
		elif p[axis] > zone.end[axis]:
			center[axis] += p[axis] - zone.end[axis]
	global_position = Vector2(center)


## Donde el personaje puede moverse sin que la cámara lo siga, en coordenadas
## del mundo. Los dos bordes cuentan como dentro: de `position` a `end` hay
## exactamente 28 x 48 px de recorrido libre.
func deadzone() -> Rect2i:
	var half := Vector2i(DesignTokens.CAMERA_DEADZONE_WIDTH, DesignTokens.CAMERA_DEADZONE_HEIGHT) / 2
	# La anticipación empuja la zona hacia atrás: el personaje se queda detrás
	# del centro y la pantalla enseña más terreno por delante.
	var middle := center + bias() - lookahead
	return Rect2i(middle - half, half * 2)


## El sesgo inferior: en reposo, el personaje queda 12 px por debajo del centro
## y se ve más terreno al norte.
static func bias() -> Vector2i:
	return Vector2i(0, DesignTokens.CAMERA_BIAS_DOWN)


func _update_lookahead(moved: Vector2i) -> void:
	if DesignTokens.reduced_motion:
		lookahead = Vector2i.ZERO
		_open_budget = Vector2i.ZERO
		_return_budget = Vector2i.ZERO
		return
	var ticks := Engine.physics_ticks_per_second
	for axis in 2:
		var direction := signi(moved[axis])
		if direction != 0:
			_return_budget[axis] = 0
			_open_budget[axis] += int(DesignTokens.CAMERA_LOOKAHEAD_OPEN_SPEED)
			while _open_budget[axis] >= ticks:
				_open_budget[axis] -= ticks
				lookahead[axis] = clampi(lookahead[axis] + direction,
					-DesignTokens.CAMERA_LOOKAHEAD, DesignTokens.CAMERA_LOOKAHEAD)
		else:
			_open_budget[axis] = 0
			if lookahead[axis] == 0:
				_return_budget[axis] = 0
				continue
			_return_budget[axis] += int(DesignTokens.CAMERA_LOOKAHEAD_RETURN_SPEED)
			while _return_budget[axis] >= ticks and lookahead[axis] != 0:
				_return_budget[axis] -= ticks
				lookahead[axis] -= signi(lookahead[axis])


func _target_position() -> Vector2i:
	return Vector2i(target.global_position.round())
