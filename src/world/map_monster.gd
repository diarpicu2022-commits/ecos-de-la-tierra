class_name MapMonster
extends Node2D

## El monstruo de historia en el mapa (IA-1, contrato «Persiana»,
## docs/ux/anexos/2026-10-28-encuentros.md). Cuatro estados: patrulla →
## alerta → persecución → se rinde, y vuelta a patrullar.
##
## - **Territorio:** las casillas pisables y libres a ≤ MONSTER_SIGHT_TILES de
##   su puesto (por pasos ortogonales). La rejilla A* tiene sólido todo lo
##   demás, así que no puede salir de su zona de daño por construcción.
## - **Ve a Ilan** si está a ≤ MONSTER_SIGHT_TILES (Manhattan), en el
##   semiplano al que mira y sin nada sólido en la línea entre los dos.
## - **Anda a WALK_SPEED**, 1 px por cuadro y eje a eje: quien corre escapa.
## - **Se lee sin color:** cada estado tiene su postura, y la alerta estira la
##   señal (brasa con filo oscuro, enmienda 1) hacia Ilan un tile por paso.
##
## El tiempo se cuenta en cuadros de física para que la prueba lo mida.

signal contact(advantage: Advantage)

enum State { PATROL, ALERT, CHASE, GIVE_UP }
## Quién empieza el combate (contrato §2).
enum Advantage { NONE, PLAYER, MONSTER }

const DECOR := "res://assets/sprites/world/decor/"

var state := State.PATROL
var cell := Vector2i.ZERO          ## Casilla de los pies.
var facing := Vector2i.LEFT
var target: PlayerBody = null
## Mientras es false no se mueve ni toca: el combate o una prueba lo paran.
var active := true
## Cuadros sin contacto posible tras huir (contrato §5).
var grace_frames := 0
var alert_steps := 0
var territory := {}
var route: Array[Vector2i] = []

var _zone := ""
var _post := Vector2i.ZERO
var _lines := PackedStringArray()
var _blocked := {}
var _grid := AStarGrid2D.new()
var _path: Array[Vector2i] = []
var _timer := 0
var _unseen := 0
var _route_index := 0
var _sprite := Sprite2D.new()
var _bands: Array[Sprite2D] = []
var _textures := {}
var _body := StaticBody2D.new()


## `blocked`: casillas que ocupa lo sólido del decorado. `solids`: donde va su
## cuerpo, con los demás sólidos de la zona.
func setup(zone_id: String, post: Vector2i, lines: PackedStringArray, blocked: Dictionary,
		solids: Node) -> void:
	_zone = zone_id
	_post = post
	cell = post
	_lines = lines
	_blocked = blocked
	name = "monster_%d_%d" % [post.x, post.y]
	for pose in ["rest", "alert", "chase"]:
		var file := "monster_%s_sick.png" % zone_id if pose == "rest" \
			else "monster_%s_%s_sick.png" % [zone_id, pose]
		_textures[pose] = load(DECOR + file)
	_sprite.centered = false
	add_child(_sprite)
	_build_territory()
	_build_grid()
	_build_route()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(DesignTokens.PLAYER_HITBOX)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	collider.position = Vector2(0, -DesignTokens.PLAYER_HITBOX.y / 2)
	_body.name = "solid_" + name
	_body.add_child(collider)
	solids.add_child(_body)
	position = Vector2(WorldRoot.feet_of(cell))
	_sync()


func _physics_process(_delta: float) -> void:
	if target != null:
		tick(Vector2i(target.global_position), target.facing)


## Un cuadro de IA-1 con Ilan en `ilan_feet` mirando a `ilan_facing`. Lo
## llama `_physics_process`; las pruebas lo llaman a mano.
func tick(ilan_feet: Vector2i, ilan_facing: Vector2i) -> void:
	if not active:
		return
	if grace_frames > 0:
		grace_frames -= 1
	var ilan := cell_of(ilan_feet)
	var seen := sees(ilan)
	match state:
		State.PATROL:
			if seen:
				_enter(State.ALERT, ilan)
			else:
				_patrol()
		State.ALERT:
			_face(ilan)
			if not seen:
				_enter(State.GIVE_UP, ilan)
			else:
				_timer += 1
				if _timer >= _frames(DesignTokens.DUR_MONSTER_ALERT_STEP):
					_timer = 0
					alert_steps += 1
					if alert_steps >= DesignTokens.MONSTER_ALERT_STEPS:
						_enter(State.CHASE, ilan)
		State.CHASE:
			_unseen = 0 if seen else _unseen + 1
			if _unseen >= _frames(DesignTokens.DUR_MONSTER_GIVE_UP):
				_enter(State.GIVE_UP, ilan)
			else:
				_walk_to(_closest_in_territory(ilan))
		State.GIVE_UP:
			if seen:
				_enter(State.ALERT, ilan)
			elif _walk_to(route[0]):
				_route_index = 0
				_enter(State.PATROL, ilan)
	_sync()
	if grace_frames == 0 and touching(ilan_feet):
		active = false
		contact.emit(advantage(Vector2i(position), facing, ilan_feet, ilan_facing))


## Fuerza un estado. La prueba lo usa para recorrer cada transición.
func force(s: State, ilan: Vector2i = cell) -> void:
	_enter(s, ilan)
	_sync()


func _enter(s: State, ilan: Vector2i) -> void:
	state = s
	_timer = 0
	_unseen = 0
	_path.clear()
	alert_steps = 0
	if s == State.ALERT:
		_face(ilan)


func _patrol() -> void:
	if _timer > 0:
		_timer -= 1
		return
	if _walk_to(route[_route_index]):
		_route_index = (_route_index + 1) % route.size()
		_timer = _frames(DesignTokens.MONSTER_PATROL_PAUSE)


## Avanza 1 px hacia `goal` por el camino A*. Devuelve true al llegar.
func _walk_to(goal: Vector2i) -> bool:
	if cell == goal and Vector2i(position) == WorldRoot.feet_of(goal):
		return true
	if _path.is_empty() or _path[-1] != goal:
		_path = _grid.get_id_path(cell, goal)
		if not _path.is_empty():
			_path.remove_at(0)
	if _path.is_empty():
		return cell == goal
	var next: Vector2i = _path[0]
	var to := WorldRoot.feet_of(next)
	var at := Vector2i(position)
	var step := (to - at).sign()
	# Eje a eje, como Ilan: nunca en diagonal.
	if step.x != 0:
		step.y = 0
	facing = step if step != Vector2i.ZERO else facing
	position = Vector2(at + step)
	if Vector2i(position) == to:
		cell = next
		_path.remove_at(0)
	return false


func _face(ilan: Vector2i) -> void:
	var d := ilan - cell
	if d == Vector2i.ZERO:
		return
	facing = Vector2i(signi(d.x), 0) if absi(d.x) >= absi(d.y) else Vector2i(0, signi(d.y))


## ¿Ve la casilla `c`? Distancia, semiplano y línea libre.
func sees(c: Vector2i) -> bool:
	var d := c - cell
	if absi(d.x) + absi(d.y) > DesignTokens.MONSTER_SIGHT_TILES or d == Vector2i.ZERO:
		return d == Vector2i.ZERO
	if d.x * facing.x + d.y * facing.y <= 0:
		return false
	for p in _line(cell, c):
		if not _free(p):
			return false
	return true


## Las cajas se tocan (o están a 1 px): eso es contacto.
func touching(ilan_feet: Vector2i) -> bool:
	var hb := DesignTokens.PLAYER_HITBOX
	var mine := Rect2i(Vector2i(position) - Vector2i(hb.x / 2, hb.y), hb).grow(1)
	var his := Rect2i(ilan_feet - Vector2i(hb.x / 2, hb.y), hb)
	return mine.intersects(his)


## Contrato §2: la espalda es el semiplano opuesto a donde se mira.
static func advantage(monster_feet: Vector2i, monster_facing: Vector2i, ilan_feet: Vector2i,
		ilan_facing: Vector2i) -> Advantage:
	var to_ilan := ilan_feet - monster_feet
	var ilan_behind_monster := to_ilan.x * monster_facing.x + to_ilan.y * monster_facing.y < 0
	var monster_behind_ilan := -to_ilan.x * ilan_facing.x - to_ilan.y * ilan_facing.y < 0
	if ilan_behind_monster and not monster_behind_ilan:
		return Advantage.PLAYER
	if monster_behind_ilan and not ilan_behind_monster:
		return Advantage.MONSTER
	return Advantage.NONE


static func cell_of(feet: Vector2i) -> Vector2i:
	var t := DesignTokens.TILE_SIZE
	return Vector2i(feet.x / t, (feet.y - 1) / t)


func _closest_in_territory(c: Vector2i) -> Vector2i:
	if territory.has(c):
		return c
	var best := cell
	var best_d := 1 << 30
	for t: Vector2i in territory:
		var d := absi(t.x - c.x) + absi(t.y - c.y)
		if d < best_d:
			best_d = d
			best = t
	return best


func _free(c: Vector2i) -> bool:
	return c.y >= 0 and c.y < _lines.size() and c.x >= 0 and c.x < _lines[0].length() \
		and ZoneRules.walkable(_lines[c.y][c.x]) and not _blocked.has(c)


func _build_territory() -> void:
	territory = {_post: true}
	var queue: Array[Vector2i] = [_post]
	while not queue.is_empty():
		var c: Vector2i = queue.pop_front()
		for step in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			var n: Vector2i = c + step
			if territory.has(n) or not _free(n):
				continue
			if absi(n.x - _post.x) + absi(n.y - _post.y) > DesignTokens.MONSTER_SIGHT_TILES:
				continue
			territory[n] = true
			queue.append(n)


func _build_grid() -> void:
	_grid.region = Rect2i(0, 0, _lines[0].length(), _lines.size())
	_grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	_grid.update()
	_grid.fill_solid_region(_grid.region, true)
	for c: Vector2i in territory:
		_grid.set_point_solid(c, false)


## Ruta corta: del puesto a 2 tiles en la primera dirección libre, ida y vuelta.
func _build_route() -> void:
	route = [_post]
	for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
		if territory.has(_post + d) and territory.has(_post + d * 2):
			route.append(_post + d * 2)
			facing = d
			return


## Casillas entre `a` y `b`, sin contar los extremos (Bresenham).
static func _line(a: Vector2i, b: Vector2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var d := (b - a).abs()
	var s := (b - a).sign()
	var err := d.x - d.y
	var p := a
	while p != b:
		var e2 := err * 2
		if e2 > -d.y:
			err -= d.y
			p.x += s.x
		if e2 < d.x:
			err += d.x
			p.y += s.y
		if p != b:
			out.append(p)
	return out


func _frames(seconds: float) -> int:
	return roundi(seconds * Engine.physics_ticks_per_second)


## Postura, volteo, señal de alerta y cuerpo, según el estado.
func _sync() -> void:
	var pose := "rest"
	if state == State.ALERT:
		pose = "alert"
	elif state == State.CHASE:
		pose = "chase"
	var tex: Texture2D = _textures[pose]
	_sprite.texture = tex
	_sprite.offset = Vector2(-tex.get_width() / 2, -tex.get_height())
	if facing.x != 0:
		_sprite.flip_h = facing.x < 0
	_body.position = position
	var steps := alert_steps if state == State.ALERT else 0
	while _bands.size() > steps:
		_bands.pop_back().queue_free()
	var vertical := facing.x == 0
	var own := "_" + _zone if _zone == "greed_crypt" else ""
	var band_tex: Texture2D = load(DECOR + "alert_shadow%s%s_sick.png" % ["_v" if vertical else "", own])
	var t := DesignTokens.TILE_SIZE
	for k in steps:
		if k >= _bands.size():
			var b := Sprite2D.new()
			b.centered = false
			add_child(b)
			move_child(b, 0)
			_bands.append(b)
		_bands[k].texture = band_tex
		var c := cell + facing * (k + 1)
		_bands[k].position = Vector2(c * t) - position
		_bands[k].visible = _free(c)
