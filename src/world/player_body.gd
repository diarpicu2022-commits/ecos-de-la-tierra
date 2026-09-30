class_name PlayerBody
extends CharacterBody2D

## El cuerpo del personaje en el mundo. Contrato «Umbral», fase 5, paso 2
## (docs/ux/anexos/2026-09-30-movimiento-y-zonas.md).
##
## El origen del nodo son los pies, en la base del tile. La caja de colisión
## (`PLAYER_HITBOX`, 12x8) va justo encima, centrada: con los bordes en píxel
## entero, un paso de un tile deja 2 px de margen a cada lado.
##
## Cómo se mueve, cada cuadro de física:
## - Se lee la entrada en ese mismo cuadro: se mueve al pulsar y se para al
##   soltar, sin aceleración (contrato «Vereda»).
## - Andando, 1 sub-paso de 1 px; corriendo, 2. En cada sub-paso cada eje se
##   prueba por separado con `test_move()`, que pregunta sin mover. Nunca
##   `move_and_slide()`: resuelve en fracciones y la posición dejaría de ser
##   entera (anexo, fase 3).
## - Pared plana: en diagonal se sigue por el eje libre; en recto, se para.
## - Esquina: en recto, si el paso está cerrado pero hay hueco a `CORNER_SLIP`
##   px o menos hacia un lado, el cuerpo se desliza 1 px lateral por cuadro
##   hacia ese hueco, también corriendo. Si hay hueco igual de cerca a los dos
##   lados, no se elige ninguno: se para.

## Con `false`, el cuerpo ignora el teclado (escenas, diálogo, fundido).
var input_enabled := true

## Hacia dónde mira: la última dirección pulsada. Al cruzar una salida se
## aparece mirando igual (contrato «Umbral»).
var facing := Vector2i.DOWN

## Dirección que se aplicó en el último cuadro, por eje. La leen las pruebas.
var last_step := Vector2i.ZERO

## Fracción del píxel que se sonda con `test_move()`. Godot cuenta como choque
## que el movimiento acabe **tocando** la pared, con cualquier margen: medido el
## 2026-09-30, sondando 1 px el cuerpo se paraba a 1 px del muro, un paso de
## 16 px solo se cruzaba hasta 5 px descentrado y cada esquina pedía 1 px más.
## Sondando 0,99 px, tocando ya choca y con 1 px de hueco no; el cuerpo avanza
## después el píxel entero, así que la posición sigue siendo entera.
const PROBE := 0.99


func _init() -> void:
	var shape := RectangleShape2D.new()
	shape.size = Vector2(DesignTokens.PLAYER_HITBOX)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	collider.position = Vector2(0, -DesignTokens.PLAYER_HITBOX.y / 2)
	add_child(collider)
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING


func _physics_process(_delta: float) -> void:
	var direction := read_direction() if input_enabled else Vector2i.ZERO
	var run := input_enabled and Input.is_action_pressed("run")
	step(direction, run)


## Dirección pulsada, por eje: -1, 0 o 1. Izquierda y derecha a la vez se
## anulan, igual que arriba y abajo.
static func read_direction() -> Vector2i:
	return Vector2i(
		int(Input.is_action_pressed("move_right")) - int(Input.is_action_pressed("move_left")),
		int(Input.is_action_pressed("move_down")) - int(Input.is_action_pressed("move_up")))


## Un cuadro de movimiento. Lo llama `_physics_process`; las pruebas lo llaman
## a mano para poner el cuerpo en cada caso sin simular el teclado.
func step(direction: Vector2i, run: bool) -> void:
	var start := Vector2i(global_position)
	if direction != Vector2i.ZERO:
		facing = direction
	var substeps := int((DesignTokens.RUN_SPEED if run else DesignTokens.WALK_SPEED)
		/ Engine.physics_ticks_per_second)
	var slipped := false
	for _i in substeps:
		var moved := false
		for axis in 2:
			if direction[axis] == 0:
				continue
			var delta := Vector2i.ZERO
			delta[axis] = direction[axis]
			if _free(delta):
				_shift(delta)
				moved = true
		# Esquina: solo en recto, y un píxel lateral por cuadro como máximo.
		if not moved and not slipped and (direction.x == 0) != (direction.y == 0):
			var side := _corner_side(direction)
			if side != Vector2i.ZERO and _free(side):
				_shift(side)
				slipped = true
	last_step = Vector2i(global_position) - start


## Hacia qué lado librar la esquina, o `ZERO` si no se libra.
func _corner_side(direction: Vector2i) -> Vector2i:
	var across := Vector2i(direction.y, direction.x).abs()
	for offset in range(1, DesignTokens.CORNER_SLIP + 1):
		var a := _clear_after(across * offset, direction)
		var b := _clear_after(-across * offset, direction)
		if a and b:
			return Vector2i.ZERO
		if a:
			return across
		if b:
			return -across
	return Vector2i.ZERO


## ¿Desde la posición desplazada `shift`, se puede avanzar 1 px en `direction`?
## Exige también que el recorrido lateral hasta ahí esté libre.
func _clear_after(shift: Vector2i, direction: Vector2i) -> bool:
	var from := global_transform
	if _blocked(from, shift):
		return false
	from.origin += Vector2(shift)
	return not _blocked(from, direction)


func _free(delta: Vector2i) -> bool:
	return not _blocked(global_transform, delta)


## ¿Choca el recorrido `delta`, píxel a píxel, desde `from`? Se sonda cada
## píxel a `PROBE` para no contar como choque llegar a tocar.
func _blocked(from: Transform2D, delta: Vector2i) -> bool:
	var unit := Vector2(delta.sign())
	for _i in maxi(absi(delta.x), absi(delta.y)):
		if test_move(from, unit * PROBE):
			return true
		from.origin += unit
	return false


func _shift(delta: Vector2i) -> void:
	global_position += Vector2(delta)
