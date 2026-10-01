class_name WorldRoot
extends Node2D

## El mundo explorable: una zona pintada, el cuerpo del personaje, la cámara,
## el fundido y el rótulo de lugar. Contrato «Umbral», fase 5, pasos 3 y 4.
##
## Cambio de zona: cuando el centro de la caja de colisión sale del mapa por
## una salida, empieza el fundido. Son dos medios fundidos lineales de
## `DUR_ZONE_FADE` en `ASH_950`, el color más profundo de la paleta (no hay
## token «negro»). Durante el de salida el cuerpo se detiene. Con la pantalla
## ya cubierta se carga la zona de destino, el cuerpo aparece en `to_cell`
## mirando igual y **vuelve a leer el teclado**: si la tecla sigue pulsada,
## sigue andando mientras la zona nueva aparece. Con movimiento reducido no hay
## fundido: corte directo, en el mismo cuadro.
##
## El fundido se cuenta en cuadros de física (120 ms = 7 cuadros a 60 Hz) para
## que la prueba lo mida cuadro a cuadro.

signal zone_changed(zone_id: String)

enum Fade { NONE, OUT, IN }

## Zona y casilla con las que arranca la escena.
@export var start_zone := "prueba_a"
@export var start_cell := Vector2i(5, 9)

var zone_id := ""
var zone_size := Vector2i.ZERO
var body := PlayerBody.new()
var camera := WorldCamera.new()
## Capa de lo que se mueve o se alza sobre el suelo, ordenada por altura: lo
## que está más al sur se dibuja encima. Hoy solo tiene al cuerpo; las
## personas, los monstruos y los objetos del catálogo entran aquí en las
## partes 3 y 4.
var entities := Node2D.new()
var label := PlaceLabel.new()

## Estado del fundido y opacidad de la cortina, 0 a 1. Las leen las pruebas.
var fade := Fade.NONE
var curtain := ColorRect.new()

var _layer: TileMapLayer = null
var _exits: Array = []
var _zone_exits: Array = []
var _names: Dictionary = {}
var _pending: Dictionary = {}
var _fade_frame := 0
var _fade_frames := 0


func _ready() -> void:
	DesignTokens.load_settings()
	# Fuera de la zona solo se ve cuando el mapa es menor que la pantalla, en
	# las bandas que deja al centrarse. Ese es el papel de `ASH_950` en la
	# paleta («fondo más profundo y bandas del viewport»); sin esto, Godot pinta
	# su gris por defecto, que no es un token.
	RenderingServer.set_default_clear_color(DesignTokens.ASH_950)
	_exits = ZoneRules.load_exits()
	_names = ZoneRules.load_names()
	# El rótulo va por debajo de la cortina: aparece con la zona, no encima del
	# negro.
	var label_layer := CanvasLayer.new()
	label_layer.layer = 5
	label_layer.add_child(label)
	add_child(label_layer)
	var fade_layer := CanvasLayer.new()
	fade_layer.layer = 10
	curtain.color = DesignTokens.ASH_950
	curtain.size = get_viewport_rect().size
	curtain.mouse_filter = Control.MOUSE_FILTER_IGNORE
	curtain.modulate.a = 0.0
	fade_layer.add_child(curtain)
	add_child(fade_layer)
	entities.y_sort_enabled = true
	add_child(entities)
	entities.add_child(body)
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
	var state := get_node_or_null("/root/GameState")
	var purified: bool = state != null and state.is_zone_purified(id)
	WorldTiles.paint(_layer, WorldTiles.parse(lines), func(_c: Vector2i) -> bool: return purified)
	zone_id = id
	zone_size = Vector2i(lines[0].length(), lines.size())
	_zone_exits = ZoneRules.exits_from(id, _exits)
	body.global_position = Vector2(feet_of(cell))
	camera.limits = Rect2i(Vector2i.ZERO, zone_size * DesignTokens.TILE_SIZE)
	camera.snap_to_target()
	label.show_name(_names.get(id, id))
	if state != null:
		state.facing = body.facing
		state.set_zone(id)
	zone_changed.emit(id)


## Pies del cuerpo de pie en `cell`: centro de la base de la casilla.
static func feet_of(cell: Vector2i) -> Vector2i:
	var t := DesignTokens.TILE_SIZE
	return Vector2i(cell.x * t + t / 2, (cell.y + 1) * t)


func _physics_process(_delta: float) -> void:
	match fade:
		Fade.NONE:
			var exit := _exit_crossed()
			if exit.is_empty():
				return
			_fade_frames = roundi(DesignTokens.duration(DesignTokens.DUR_ZONE_FADE)
				* Engine.physics_ticks_per_second)
			if _fade_frames == 0:
				enter_zone(exit["to"], ZoneRules.cell_of(exit, "to_cell"))
				return
			_pending = exit
			body.input_enabled = false
			_start(Fade.OUT)
		Fade.OUT:
			_fade_frame += 1
			curtain.modulate.a = float(_fade_frame) / _fade_frames
			if _fade_frame >= _fade_frames:
				enter_zone(_pending["to"], ZoneRules.cell_of(_pending, "to_cell"))
				body.input_enabled = true
				_start(Fade.IN)
		Fade.IN:
			_fade_frame += 1
			curtain.modulate.a = 1.0 - float(_fade_frame) / _fade_frames
			if _fade_frame >= _fade_frames:
				curtain.modulate.a = 0.0
				_start(Fade.NONE)


func _start(f: Fade) -> void:
	fade = f
	_fade_frame = 0


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
