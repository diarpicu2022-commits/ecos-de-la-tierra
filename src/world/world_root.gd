class_name WorldRoot
extends Node2D

## El mundo explorable: una zona pintada, el cuerpo del personaje y la cámara.
## Contrato «Umbral», fase 5, paso 3 (esqueleto).
##
## Cambio de zona: cuando el centro de la caja de colisión sale del mapa por
## una salida, se carga la zona de destino y el cuerpo aparece en la casilla
## `to_cell`, un tile dentro, mirando igual. El cuerpo lee el teclado en cada
## cuadro, así que **con la tecla pulsada se sigue andando**: el control no se
## pierde al cruzar.
##
## En este paso el cambio es un corte directo. El fundido de 120 + 120 ms, el
## rótulo de lugar, `GameState` y los límites de la cámara son del paso 4.

signal zone_changed(zone_id: String)

## Zona y casilla con las que arranca la escena.
@export var start_zone := "prueba_a"
@export var start_cell := Vector2i(5, 9)

var zone_id := ""
var zone_size := Vector2i.ZERO
var body := PlayerBody.new()
var camera := WorldCamera.new()

var _layer: TileMapLayer = null
var _exits: Array = []
var _zone_exits: Array = []


func _ready() -> void:
	_exits = ZoneRules.load_exits()
	add_child(body)
	camera.target = body
	add_child(camera)
	camera.make_current()
	# Después del cuerpo (0) y antes de la cámara (100): la salida se decide con
	# la posición de este cuadro, y la cámara ya sigue al cuerpo en su sitio nuevo.
	process_physics_priority = 50
	enter_zone(start_zone, start_cell)


## Carga `id` y pone al cuerpo de pie en la casilla `cell`, sin tocar hacia
## dónde mira.
func enter_zone(id: String, cell: Vector2i) -> void:
	var lines := ZoneRules.load_zone(id)
	if _layer != null:
		_layer.queue_free()
	_layer = TileMapLayer.new()
	_layer.tile_set = WorldTiles.build_tileset()
	add_child(_layer)
	move_child(_layer, 0)
	WorldTiles.paint(_layer, WorldTiles.parse(lines), func(_c: Vector2i) -> bool: return false)
	zone_id = id
	zone_size = Vector2i(lines[0].length(), lines.size())
	_zone_exits = ZoneRules.exits_from(id, _exits)
	body.global_position = Vector2(feet_of(cell))
	camera.snap_to_target()
	zone_changed.emit(id)


## Pies del cuerpo de pie en `cell`: centro de la base de la casilla.
static func feet_of(cell: Vector2i) -> Vector2i:
	var t := DesignTokens.TILE_SIZE
	return Vector2i(cell.x * t + t / 2, (cell.y + 1) * t)


func _physics_process(_delta: float) -> void:
	var exit := _exit_crossed()
	if not exit.is_empty():
		enter_zone(exit["to"], ZoneRules.cell_of(exit, "to_cell"))


## La salida por la que el cuerpo acaba de dejar el mapa, o `{}`.
func _exit_crossed() -> Dictionary:
	var t := DesignTokens.TILE_SIZE
	var center := Vector2i(body.global_position) - Vector2i(0, DesignTokens.PLAYER_HITBOX.y / 2)
	var map := Rect2i(Vector2i.ZERO, zone_size * t)
	if map.has_point(center):
		return {}
	# Casilla del borde por la que salió: la más cercana dentro del mapa.
	var cell := Vector2i(clampi(center.x / t if center.x >= 0 else -1, 0, zone_size.x - 1),
		clampi(center.y / t if center.y >= 0 else -1, 0, zone_size.y - 1))
	for e in _zone_exits:
		if ZoneRules.cell_of(e, "cell") == cell:
			return e
	push_error("%s: el cuerpo salió del mapa por %s, que no es una salida" % [zone_id, cell])
	return {}
