extends Node2D

## Prueba de IA-1 y del contacto (contrato «Persiana», paso 3). Sin ventana:
##
##   godot --headless --path . res://tools/verify_encounters.tscn
##
## En cada una de las seis regiones:
## - el territorio y la ruta están dentro de la zona de daño, en suelo libre;
## - con Ilan rondando, el monstruo nunca pisa fuera de su territorio;
## - Ilan corriendo en línea recta no es alcanzado;
## - cada transición de estado se fuerza y se comprueba;
## - la ventaja sale bien en los tres casos, y un contacto real la emite.
## Sale con código 1 si algo falla.

const ZONES := ["ashen_forest", "tar_basin", "broken_coast", "withered_plain", "waning_peak", "greed_crypt"]

var _world := WorldRoot.new()
var _pass := 0
var _fail := 0


func _ready() -> void:
	get_node("/root/GameState").flags.clear()
	_world.start_zone = ZONES[0]
	_world.start_cell = Vector2i(1, 12)
	add_child(_world)
	await get_tree().physics_frame
	_world.body.input_enabled = false
	_advantage_table()
	for zone in ZONES:
		await _zone(zone)
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool, detail := "") -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s%s" % ["OK   " if ok else "FALLA", label, "  (%s)" % detail if detail != "" else ""])


## Contrato §2, los tres casos, sin mundo.
func _advantage_table() -> void:
	print("Ventaja")
	var m := Vector2i(100, 100)
	_check("Ilan toca la espalda del monstruo: empieza Ilan",
		MapMonster.advantage(m, Vector2i.LEFT, m + Vector2i(14, 0), Vector2i.LEFT) == MapMonster.Advantage.PLAYER)
	_check("el monstruo toca la espalda de Ilan: empieza el monstruo",
		MapMonster.advantage(m, Vector2i.RIGHT, m + Vector2i(14, 0), Vector2i.RIGHT) == MapMonster.Advantage.MONSTER)
	_check("de frente: sin ventaja",
		MapMonster.advantage(m, Vector2i.RIGHT, m + Vector2i(14, 0), Vector2i.LEFT) == MapMonster.Advantage.NONE)
	_check("de lado: sin ventaja",
		MapMonster.advantage(m, Vector2i.UP, m + Vector2i(14, 0), Vector2i.UP) == MapMonster.Advantage.NONE)


func _zone(zone: String) -> void:
	print("\n%s" % zone)
	_world.enter_zone(zone, Vector2i(1, 1))
	await get_tree().physics_frame
	var mon := _world.monster
	_check("hay monstruo en el mapa", mon != null)
	if mon == null:
		return
	mon.target = null    # La prueba mueve el tiempo a mano.
	var lines := ZoneRules.load_zone(zone)
	var bad := []
	for c: Vector2i in mon.territory:
		if not ZoneRules.walkable(lines[c.y][c.x]):
			bad.append(c)
	_check("territorio de %d casillas, todas pisables y a ≤ %d del puesto" % [
		mon.territory.size(), DesignTokens.MONSTER_SIGHT_TILES],
		bad.is_empty() and mon.territory.size() > 1, str(bad.slice(0, 3)))
	_check("ruta de patrulla dentro del territorio (%d puntos)" % mon.route.size(),
		mon.route.size() == 2 and mon.route.all(func(c): return mon.territory.has(c)))

	# Ilan rondando: 900 cuadros en casillas del territorio y fuera de él.
	var post: Vector2i = mon.cell
	var left := false
	var spots := [post + Vector2i(3, 0), post + Vector2i(-3, 1), post + Vector2i(0, 4), post + Vector2i(9, 9)]
	for i in 900:
		var spot: Vector2i = spots[(i / 120) % spots.size()]
		mon.active = true
		mon.grace_frames = 2
		mon.tick(WorldRoot.feet_of(spot), Vector2i.DOWN)
		if not mon.territory.has(mon.cell):
			left = true
	_check("900 cuadros con Ilan rondando: nunca pisa fuera de su territorio", not left)

	# Transiciones forzadas.
	var dir := _clear_line(post, lines, mon)
	_check("hay línea libre de %d tiles para la prueba" % DesignTokens.MONSTER_SIGHT_TILES,
		dir != Vector2i.ZERO)
	if dir == Vector2i.ZERO:
		return
	var ilan: Vector2i = post + dir * (DesignTokens.MONSTER_SIGHT_TILES - 1)
	_reset(mon, post, dir)
	mon.tick(WorldRoot.feet_of(ilan), -dir)
	_check("patrulla → alerta al verlo de frente", mon.state == MapMonster.State.ALERT)
	_reset(mon, post, -dir)
	mon.tick(WorldRoot.feet_of(ilan), -dir)
	_check("no lo ve si está a su espalda", mon.state == MapMonster.State.PATROL)
	_reset(mon, post, dir)
	mon.force(MapMonster.State.ALERT, ilan)
	var frames := 0
	while mon.state == MapMonster.State.ALERT and frames < 200:
		mon.tick(WorldRoot.feet_of(ilan), -dir)
		frames += 1
	var expected := roundi(DesignTokens.DUR_MONSTER_ALERT_STEP * 60) * DesignTokens.MONSTER_ALERT_STEPS
	_check("alerta → persecución en %d cuadros (%d esperados)" % [frames, expected],
		mon.state == MapMonster.State.CHASE and frames == expected)
	_reset(mon, post, dir)
	mon.force(MapMonster.State.CHASE, ilan)
	var hidden: Vector2i = post - dir * 20    # Fuera de su vista y de su territorio.
	frames = 0
	while mon.state == MapMonster.State.CHASE and frames < 400:
		mon.tick(WorldRoot.feet_of(hidden), Vector2i.DOWN)
		frames += 1
	var give_up := roundi(DesignTokens.DUR_MONSTER_GIVE_UP * 60)
	_check("persecución → se rinde tras %d cuadros sin verlo (%d esperados)" % [frames, give_up],
		mon.state == MapMonster.State.GIVE_UP and frames == give_up)
	frames = 0
	while mon.state == MapMonster.State.GIVE_UP and frames < 900:
		mon.tick(WorldRoot.feet_of(hidden), Vector2i.DOWN)
		frames += 1
	_check("se rinde → patrulla al volver a su ruta",
		mon.state == MapMonster.State.PATROL and mon.cell == mon.route[0])

	# Corriendo en línea recta, nunca lo alcanza: la distancia no baja.
	_reset(mon, post, dir)
	_world.body.global_position = Vector2(WorldRoot.feet_of(post + dir * 3))
	_world.body.facing = dir
	mon.force(MapMonster.State.CHASE, post + dir * 3)
	# Solo mientras Ilan avanza de verdad: si choca con algo, ya no corre.
	var gap := _gap(mon)
	var shrank := false
	var ran := 0
	for i in 120:
		var before := Vector2i(_world.body.global_position)
		_world.body.step(dir, true)
		if Vector2i(_world.body.global_position) == before:
			break
		ran += 2
		mon.tick(Vector2i(_world.body.global_position), dir)
		var g := _gap(mon)
		if g < gap:
			shrank = true
		gap = g
	_check("Ilan corriendo %d px en línea recta: la distancia nunca baja y no hay contacto" % ran,
		ran >= 32 and not shrank and mon.active, "distancia final %d px" % gap)

	# Contacto real por la espalda del monstruo: ventaja de Ilan.
	_reset(mon, post, dir)
	var got := [-1]
	var cb := func(a): got[0] = a
	mon.contact.connect(cb)
	# Pegado: el monstruo es sólido, así que más cerca que esto no se llega.
	var behind: Vector2i = WorldRoot.feet_of(post) - dir * DesignTokens.PLAYER_HITBOX.x
	mon.tick(behind, dir)
	_check("contacto real por la espalda del monstruo: empieza Ilan",
		got[0] == MapMonster.Advantage.PLAYER and not mon.active, "ventaja %d" % got[0])
	mon.contact.disconnect(cb)
	_reset(mon, post, dir)
	mon.grace_frames = 5
	mon.tick(behind, dir)
	_check("con gracia no hay contacto", mon.active)


func _reset(mon: MapMonster, post: Vector2i, facing: Vector2i) -> void:
	mon.cell = post
	mon.position = Vector2(WorldRoot.feet_of(post))
	mon.active = true
	mon.grace_frames = 0
	mon.force(MapMonster.State.PATROL)
	mon.facing = facing


func _gap(mon: MapMonster) -> int:
	var d := Vector2i(_world.body.global_position) - Vector2i(mon.position)
	return absi(d.x) + absi(d.y)


## Una dirección con MONSTER_SIGHT_TILES casillas libres seguidas desde el
## puesto (pisables y sin decorado sólido), para poner a Ilan a la vista.
func _clear_line(post: Vector2i, lines: PackedStringArray, mon: MapMonster) -> Vector2i:
	for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.UP]:
		var ok := true
		for k in range(1, DesignTokens.MONSTER_SIGHT_TILES + 1):
			var c: Vector2i = post + d * k
			if not mon._free(c):
				ok = false
				break
		if ok:
			return d
	return Vector2i.ZERO
