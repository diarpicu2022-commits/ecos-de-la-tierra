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

## Hoja del sprite (`tools/gen_world_sprites.py`): 2 poses por 4 orientaciones
## de 16x24, con los pies en la última fila.
const SPRITE_PATH := "res://assets/sprites/world/ilan.png"
const SPRITE_SIZE := Vector2i(16, 24)
## Fila de la hoja por orientación.
const ROW_DOWN := 0
const ROW_UP := 1
const ROW_LEFT := 2
const ROW_RIGHT := 3
## La pose cambia cada medio tile recorrido. Va por distancia y no por
## tiempo: se para justo cuando el cuerpo se para y no añade ninguna duración
## (aclaración de «caminar no se anima», anexo de la parte 2, paso 5).
const STRIDE := 8

## Pose y fila que enseña el sprite. Las leen las pruebas.
var pose := 0
var sprite_row := ROW_DOWN

var _sprite := Sprite2D.new()
var _travelled := 0


func _init() -> void:
	var shape := RectangleShape2D.new()
	shape.size = Vector2(DesignTokens.PLAYER_HITBOX)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	collider.position = Vector2(0, -DesignTokens.PLAYER_HITBOX.y / 2)
	add_child(collider)
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	_sprite.texture = load(SPRITE_PATH)
	_sprite.centered = false
	_sprite.region_enabled = true
	_sprite.offset = Vector2(-SPRITE_SIZE.x / 2, -SPRITE_SIZE.y)
	add_child(_sprite)
	_update_sprite()


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
	_update_sprite()


## Fila según hacia dónde mira (en diagonal manda el eje horizontal) y pose
## según la distancia recorrida. Sin avance, de pie: también empujando una
## pared, que así se distingue de andar.
func _update_sprite() -> void:
	if facing.x != 0:
		sprite_row = ROW_RIGHT if facing.x > 0 else ROW_LEFT
	else:
		sprite_row = ROW_DOWN if facing.y > 0 else ROW_UP
	if last_step == Vector2i.ZERO:
		_travelled = 0
		pose = 0
	else:
		_travelled += maxi(absi(last_step.x), absi(last_step.y))
		pose = (_travelled / STRIDE) % 2
	_sprite.region_rect = Rect2(Vector2(pose * SPRITE_SIZE.x, sprite_row * SPRITE_SIZE.y),
		Vector2(SPRITE_SIZE))


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

