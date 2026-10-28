class_name WorldAmbient
extends Node

## El movimiento ambiental de una zona. Enmienda 8, autorizada el 2026-10-28:
## **solo se mueve lo purificado**, porque en este mundo estar vivo se lee como
## moverse. Lo enfermo queda quieto, y con movimiento reducido no se mueve
## nada.
##
## - El agua viva alterna sus dos cuadros (filas 4 y 8 del atlas) cada
##   `DUR_AMBIENT_WATER`.
## - La hierba, las flores, los matojos y los cultivos purificados alternan
##   sus dos cuadros cada `DUR_AMBIENT_SWAY`, cada pieza con su fase: un prado
##   no se mece a la vez.
## - La fauna silvestre aletea cada `DUR_FAUNA_FLAP` y sube y baja `FAUNA_BOB`.
## - Los animales domésticos que están en lo purificado andan a saltos cortos
##   a `WALK_SPEED` (1 px por cuadro y eje) dentro de `ANIMAL_RANGE` de su
##   sitio, con pausas de `ANIMAL_PAUSE_MIN` a `ANIMAL_PAUSE_MAX`. No salen de
##   lo purificado ni entran en lo sólido.
##
## Todo se cuenta en cuadros de física, con `advance()`, para que la prueba lo
## mida cuadro a cuadro. El azar es determinista por pieza: la misma zona se
## mueve siempre igual.

var tick := 0

var _layer: TileMapLayer = null
var _water: Array[Vector2i] = []
var _swayers: Array[Sprite2D] = []
var _fauna: Array[Sprite2D] = []
var _animals: Array[Sprite2D] = []
var _walkable: Callable


func _physics_process(_delta: float) -> void:
	advance()


## Recoge lo que se mueve en la zona recién montada. `walkable` dice si un
## animal puede estar en una casilla (pisable, sin sólido y purificada).
func setup(layer: TileMapLayer, entities: Node, walkable: Callable) -> void:
	_layer = layer
	_walkable = walkable
	tick = 0
	_water.clear()
	_swayers.clear()
	_fauna.clear()
	_animals.clear()
	for cell in layer.get_used_cells():
		if layer.get_cell_atlas_coords(cell).y == WorldTiles.OVERLAY_ROW[WorldTiles.Terrain.WATER] + 1:
			_water.append(cell)
	for node in entities.get_children():
		if not node is Sprite2D or not node.has_meta("frames"):
			continue
		match String(node.get_meta("kind")):
			"fauna":
				_fauna.append(node)
			"animal":
				_animals.append(node)
				node.set_meta("home", node.position)
				node.set_meta("target", node.position)
				node.set_meta("wait", _pause(node))
			_:
				_swayers.append(node)


func advance() -> void:
	if DesignTokens.reduced_motion:
		return
	tick += 1
	var water_frames := _frames(DesignTokens.DUR_AMBIENT_WATER)
	if tick % water_frames == 0:
		var row := WorldTiles.WATER_ALT_ROW if (tick / water_frames) % 2 == 1 \
			else WorldTiles.OVERLAY_ROW[WorldTiles.Terrain.WATER] + 1
		for cell in _water:
			_layer.set_cell(cell, 0, Vector2i(_layer.get_cell_atlas_coords(cell).x, row))
	var sway := _frames(DesignTokens.DUR_AMBIENT_SWAY)
	for sprite in _swayers:
		_show(sprite, ((tick + int(sprite.get_meta("phase"))) / sway) % 2)
	var flap := _frames(DesignTokens.DUR_FAUNA_FLAP)
	for sprite in _fauna:
		var f := ((tick + int(sprite.get_meta("phase"))) / flap) % 2
		_show(sprite, f)
		sprite.position.y = float(sprite.get_meta("base_y")) - f * DesignTokens.FAUNA_BOB
	for sprite in _animals:
		_walk(sprite)


## Un cuadro de un animal: espera, o da un paso de 1 px por eje hacia su
## destino. Al llegar, elige otro salto y otra pausa.
func _walk(sprite: Sprite2D) -> void:
	var wait := int(sprite.get_meta("wait"))
	if wait > 0:
		sprite.set_meta("wait", wait - 1)
		_show(sprite, 0)
		return
	var target: Vector2 = sprite.get_meta("target")
	if sprite.position == target:
		sprite.set_meta("target", _next_target(sprite))
		sprite.set_meta("wait", _pause(sprite))
		return
	var step := Vector2(signf(target.x - sprite.position.x), signf(target.y - sprite.position.y))
	var next := sprite.position + step
	if not _walkable.call(_cell_of(next)):
		sprite.set_meta("target", sprite.position)
		return
	sprite.position = next
	if step.x != 0:
		sprite.flip_h = step.x < 0
	_show(sprite, (tick / 8) % 2)


func _next_target(sprite: Sprite2D) -> Vector2:
	var rng: RandomNumberGenerator = sprite.get_meta("rng")
	var home: Vector2 = sprite.get_meta("home")
	for _try in 8:
		var hop := Vector2(rng.randi_range(-DesignTokens.ANIMAL_HOP_MAX, DesignTokens.ANIMAL_HOP_MAX),
			rng.randi_range(-DesignTokens.ANIMAL_HOP_MAX / 2, DesignTokens.ANIMAL_HOP_MAX / 2))
		var to := sprite.position + hop
		if to.distance_to(home) <= DesignTokens.ANIMAL_RANGE and _walkable.call(_cell_of(to)):
			return to
	return sprite.position


func _pause(sprite: Sprite2D) -> int:
	if not sprite.has_meta("rng"):
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(sprite.name)
		sprite.set_meta("rng", rng)
	var rng: RandomNumberGenerator = sprite.get_meta("rng")
	return roundi(rng.randf_range(DesignTokens.ANIMAL_PAUSE_MIN, DesignTokens.ANIMAL_PAUSE_MAX)
		* Engine.physics_ticks_per_second)


func _show(sprite: Sprite2D, frame: int) -> void:
	var frames: Array = sprite.get_meta("frames")
	sprite.texture = frames[frame % frames.size()]


## Casilla de los pies de un sprite: su posición es el borde inferior.
static func _cell_of(feet: Vector2) -> Vector2i:
	var t := DesignTokens.TILE_SIZE
	return Vector2i(floori(feet.x / t), floori((feet.y - 1) / t))


static func _frames(seconds: float) -> int:
	return maxi(1, roundi(seconds * Engine.physics_ticks_per_second))
