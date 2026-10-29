extends Node

## Prueba del paso mundo ↔ combate (contrato «Persiana», paso 4):
##
##   godot --path . res://tools/verify_flow.tscn
##
## - La persiana, cuadro a cuadro: dura DUR_BATTLE_BLINDS, empieza por la fila
##   del monstruo, cubre la pantalla entera en píxeles enteros, y con
##   movimiento reducido cubre en el primer cuadro y espera lo mismo.
## - La ventaja ordena la primera ronda y solo la primera.
## - El paso completo: contacto → combate con el grupo de GameState → vuelta.
##   Huida con gracia y el monstruo rendido; victoria con la zona purificada y
##   sin monstruo; derrota a la casilla de llegada con el grupo a 1 PV. Los PV
##   del grupo salen del combate tal como quedaron.
## Sale con código 1 si algo falla.

var _pass := 0
var _fail := 0


func _ready() -> void:
	await _blinds()
	_opening()
	await _flow()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool, detail := "") -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s%s" % ["OK   " if ok else "FALLA", label, "  (%s)" % detail if detail != "" else ""])


func _blinds() -> void:
	print("Persiana")
	var b := BattleBlinds.new()
	add_child(b)
	await get_tree().physics_frame
	var expected := roundi(DesignTokens.DUR_BATTLE_BLINDS * 60)
	var full := int(b.size.x)
	for from in [BattleBlinds.Side.LEFT, BattleBlinds.Side.RIGHT, BattleBlinds.Side.BOTH]:
		DesignTokens.reduced_motion = false
		b.close(200, from)
		var origin := 200 / DesignTokens.BLIND_STRIP
		var frames := 0
		var origin_first := true
		var monotonic := true
		var prev := b.widths.duplicate()
		while b.running and frames < 100:
			await get_tree().physics_frame
			frames += 1
			for i in b.widths.size():
				if b.widths[i] < prev[i]:
					monotonic = false
				if b.widths[i] > b.widths[origin]:
					origin_first = false
			prev = b.widths.duplicate()
		var covered := Array(b.widths).all(func(w): return w == full)
		_check("cerrar desde %s: %d cuadros (%d esperados), cubre las %d franjas" % [
			["izquierda", "derecha", "los dos lados"][from], frames, expected, b.widths.size()],
			frames == expected and covered)
		_check("  la fila del monstruo va siempre por delante y nada retrocede",
			origin_first and monotonic)
		b.open()
		frames = 0
		while b.running and frames < 100:
			await get_tree().physics_frame
			frames += 1
		_check("  abrir: %d cuadros y la pantalla queda descubierta" % frames,
			frames == expected and Array(b.widths).all(func(w): return w == 0))
	DesignTokens.reduced_motion = true
	b.close(100, BattleBlinds.Side.BOTH)
	var instant := Array(b.widths).all(func(w): return w == full)
	var frames := 0
	while b.running and frames < 100:
		await get_tree().physics_frame
		frames += 1
	_check("movimiento reducido: cubierta en el primer cuadro y %d cuadros de espera" % frames,
		instant and frames == expected)
	DesignTokens.reduced_motion = false
	b.queue_free()


## La ventaja adelanta al equipo entero en la primera ronda, y solo en ella.
func _opening() -> void:
	print("\nVentaja en el orden de turnos")
	for team in [Enums.Team.PLAYER, Enums.Team.ENEMY]:
		var tm := TurnManager.new()
		var fast := Monster.new()
		var slow := Character.new()
		fast.team = Enums.Team.ENEMY
		slow.team = Enums.Team.PLAYER
		fast.hp = 10
		slow.hp = 10
		fast.base_speed = 99
		slow.base_speed = 1
		var all: Array[Combatant] = [fast, slow]
		tm.start_round(all)
		tm.prioritize(team)
		var first := tm.next_combatant()
		_check("abre el equipo %s aunque sea más lento" % ["del jugador", "del monstruo"][team],
			first.team == team)
		fast.free()
		slow.free()


func _flow() -> void:
	print("\nPaso mundo ↔ combate")
	var state := get_node("/root/GameState")
	state.flags.clear()
	state.party.clear()
	var flow := GameFlow.new()
	flow.start_zone = "ashen_forest"
	flow.start_cell = Vector2i(1, 12)
	add_child(flow)
	await get_tree().physics_frame
	flow.world.body.input_enabled = false
	# Huida.
	await _encounter(flow, MapMonster.Advantage.PLAYER)
	_check("en combate: el mundo oculto y parado, «Ceniza y Brasa» delante",
		flow.screen != null and not flow.world.visible
		and flow.world.process_mode == Node.PROCESS_MODE_DISABLED)
	_check("el grupo es el de GameState (%d)" % state.party.size(), state.party.size() == 2)
	_check("con ventaja de Ilan, el combate se abre con su equipo",
		flow.screen._manager.opening_team == Enums.Team.PLAYER)
	state.party[0].hp = 7
	flow.result = Enums.BattleResult.FLED
	await _leave(flow)
	var mon := flow.world.monster
	_check("huida: vuelve el mundo y el monstruo sigue ahí, rendido",
		flow.world.visible and mon != null and mon.state == MapMonster.State.GIVE_UP)
	_check("  con %d cuadros de gracia (%d esperados)" % [mon.grace_frames, roundi(DesignTokens.DUR_FLEE_GRACE * 60)],
		mon.grace_frames == roundi(DesignTokens.DUR_FLEE_GRACE * 60))
	_check("  el grupo sale con los PV del combate (7)", state.party[0].hp == 7)
	# Derrota.
	await _encounter(flow, MapMonster.Advantage.MONSTER)
	_check("con ventaja del monstruo, el combate se abre con el suyo",
		flow.screen._manager.opening_team == Enums.Team.ENEMY)
	for c in state.party:
		c.hp = 0
	flow.result = Enums.BattleResult.DEFEAT
	await _leave(flow)
	var at := MapMonster.cell_of(Vector2i(flow.world.body.global_position))
	_check("derrota: vuelta a la casilla de llegada %s" % flow.world.arrival_cell, at == flow.world.arrival_cell)
	_check("  con el grupo a 1 PV", state.party.all(func(c): return c.hp == 1))
	# Victoria.
	await _encounter(flow, MapMonster.Advantage.NONE)
	_check("sin ventaja, manda la velocidad", flow.screen._manager.opening_team == -1)
	flow.result = Enums.BattleResult.VICTORY
	await _leave(flow)
	_check("victoria: la zona queda purificada y sin monstruo",
		state.is_zone_purified("ashen_forest") and flow.world.monster == null)
	state.flags.clear()
	flow.queue_free()


func _encounter(flow: GameFlow, adv: MapMonster.Advantage) -> void:
	flow.world.monster.active = false
	flow.world.monster.contact.emit(adv)
	for _i in 120:
		await get_tree().physics_frame
		if flow.screen != null and not flow.blinds.running:
			return


func _leave(flow: GameFlow) -> void:
	flow.leave_battle()
	for _i in 120:
		await get_tree().physics_frame
		if flow.screen == null and not flow.blinds.running:
			return
