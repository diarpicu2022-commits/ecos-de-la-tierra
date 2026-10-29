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
## Ilan ha tocado al monstruo de la zona (contrato «Persiana» §2). El cuerpo
## ya está parado; la persiana y el combate van en el paso 4.
signal encounter(advantage: MapMonster.Advantage)

enum Fade { NONE, OUT, IN }

## Zona y casilla con las que arranca la escena.
@export var start_zone := "prueba_a"
@export var start_cell := Vector2i(5, 9)

var zone_id := ""
var zone_size := Vector2i.ZERO
var body := PlayerBody.new()
var camera := WorldCamera.new()
## Capa de lo que se mueve o se alza sobre el suelo, ordenada por altura: lo
## que está más al sur se dibuja encima. Tiene al cuerpo y, desde la parte 3,
## el decorado, el hito, las personas y los animales de la zona
## (`WorldDecor`). Los monstruos entran aquí en la parte 4.
var entities := Node2D.new()
## Cuerpos sólidos del decorado de la zona: casas, árboles, pozo, rocas.
var solids := Node2D.new()
## Lo que se mueve solo en lo purificado: agua, plantas, fauna y animales
## (enmienda 8).
var ambient := WorldAmbient.new()
var label := PlaceLabel.new()
## El monstruo de historia de la zona mientras está enferma (IA-1), o null.
var monster: MapMonster = null
## Casilla por la que se entró en la zona: adonde se vuelve tras una derrota.
var arrival_cell := Vector2i.ZERO

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
	add_child(ambient)
	add_child(solids)
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
	# Estado por casilla: en Valdehoja, cada parte sigue a su región.
	var purified_at := WorldDecor.purified_lookup(id, state)
	WorldTiles.paint(_layer, WorldTiles.parse(lines), purified_at)
	# Fuera del árbol antes de liberarlos: así el decorado de la zona anterior
	# no choca de nombre con el nuevo ni cuenta para la física de este cuadro.
	for child in entities.get_children() + solids.get_children():
		if child != body:
			child.get_parent().remove_child(child)
			child.queue_free()
	var blocked := {}
	WorldDecor.build(id, purified_at, entities, solids, blocked)
	_spawn_monster(id, lines, blocked)
	var size := Vector2i(lines[0].length(), lines.size())
	ambient.setup(_layer, entities, func(c: Vector2i) -> bool:
		return Rect2i(Vector2i.ZERO, size).has_point(c) and not blocked.has(c) \
			and ZoneRules.walkable(lines[c.y][c.x]) and purified_at.call(c))
	if id != zone_id:
		arrival_cell = cell
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


## La ola de purificación desde `origin_cell` (enmienda 3, contrato
## «Persiana» §5). El suelo purificado se pinta en una capa encima del enfermo
## y `purify_wave.gdshader` lo descubre píxel a píxel en tramado de Bayer 4x4,
## en DUR_ZONE_PURIFY. El frente recorre la pantalla visible; lo que queda
## fuera no se ve y se resuelve al final. Al terminar, la zona queda purificada
## en `GameState` y se vuelve a montar entera (decorado y fauna incluidos).
## Con movimiento reducido, de golpe. Devuelve cuando ha terminado.
signal wave_finished

## Radio del frente de la ola, en píxeles, mientras dura. Lo lee la prueba.
var wave_radius := -1.0
var wave_layer: TileMapLayer = null


func purify_wave(origin_cell: Vector2i) -> void:
	var state := get_node_or_null("/root/GameState")
	var lines := ZoneRules.load_zone(zone_id)
	var t := DesignTokens.TILE_SIZE
	var origin := Vector2(origin_cell * t) + Vector2(t / 2, t / 2)
	var frames := roundi(DesignTokens.duration(DesignTokens.DUR_ZONE_PURIFY)
		* Engine.physics_ticks_per_second)
	if frames > 0:
		body.input_enabled = false
		wave_layer = TileMapLayer.new()
		wave_layer.tile_set = _layer.tile_set
		WorldTiles.paint(wave_layer, WorldTiles.parse(lines), func(_c): return true)
		var mat := ShaderMaterial.new()
		mat.shader = load("res://src/world/purify_wave.gdshader")
		var flat: Array[int] = []
		for row in DesignTokens.BAYER_4X4:
			flat.append_array(row)
		mat.set_shader_parameter("bayer", flat)
		mat.set_shader_parameter("steps", float(DesignTokens.PURIFY_DITHER_STEPS))
		mat.set_shader_parameter("origin", origin)
		# Ocho pasos de un tile: la banda del tramado mide medio tile.
		var band := float(t) / 2.0
		mat.set_shader_parameter("band", band)
		wave_layer.material = mat
		add_child(wave_layer)
		move_child(wave_layer, _layer.get_index() + 1)
		# El frente llega a la esquina visible más lejana, más la banda.
		var view := Rect2(camera.get_screen_center_position() - get_viewport_rect().size / 2,
			get_viewport_rect().size)
		var reach := 0.0
		for corner in [view.position, view.end, Vector2(view.position.x, view.end.y),
				Vector2(view.end.x, view.position.y)]:
			reach = maxf(reach, origin.distance_to(corner))
		reach += band
		for f in range(1, frames + 1):
			wave_radius = reach * float(f) / frames
			mat.set_shader_parameter("radius", wave_radius)
			await get_tree().physics_frame
		wave_layer.queue_free()
		wave_layer = null
	wave_radius = -1.0
	if state != null:
		state.set_zone_purified(zone_id)
	var here := MapMonster.cell_of(Vector2i(body.global_position))
	enter_zone(zone_id, here)
	body.input_enabled = true
	wave_finished.emit()


## El monstruo de la capa de decorado, si sigue enfermo, pasa a ser un
## `MapMonster` que patrulla: se quitan su sprite fijo, su cuerpo y su casilla
## de lo bloqueado, y entra él con su propio cuerpo entre los sólidos.
func _spawn_monster(id: String, lines: PackedStringArray, blocked: Dictionary) -> void:
	monster = null
	for child in entities.get_children():
		var nm := String(child.name)
		if not nm.begins_with("monster_") or child is MapMonster:
			continue
		var parts := nm.split("_")
		var post := Vector2i(int(parts[-2]), int(parts[-1]))
		var body_node := solids.get_node_or_null("solid_" + nm)
		for n in [child, body_node]:
			if n != null:
				n.get_parent().remove_child(n)
				n.queue_free()
		blocked.erase(post)
		monster = MapMonster.new()
		monster.setup(id, post, lines, blocked, solids)
		monster.target = body
		monster.contact.connect(_on_contact)
		entities.add_child(monster)
		return


func _on_contact(advantage: MapMonster.Advantage) -> void:
	body.input_enabled = false
	encounter.emit(advantage)


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
