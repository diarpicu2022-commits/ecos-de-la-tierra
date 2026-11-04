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
	# Viene de la prueba de derrota, con el grupo a 1 PV.
	for c in state.party:
		c.hp = c.max_hp
	await _encounter(flow, MapMonster.Advantage.NONE)
	_check("sin ventaja, manda la velocidad", flow.screen._manager.opening_team == -1)
	await _pace(flow)
	_turn_by_turn(flow)
	flow.result = Enums.BattleResult.VICTORY
	await _leave(flow)
	for _i in 200:
		if flow.world.wave_radius < 0.0 and state.is_zone_purified("ashen_forest"):
			break
		await get_tree().physics_frame
	_check("victoria: la zona queda purificada y sin monstruo",
		state.is_zone_purified("ashen_forest") and flow.world.monster == null)
	state.flags.clear()
	flow.queue_free()


## El ritmo del combate (Juan José Rueda, 2026-11-03): cada línea se queda según
## lo que hay que leer, `confirm` la adelanta salvo justo al salir, y el
## desenlace no se puede cerrar hasta pasado RESULT_HOLD.
func _pace(flow: GameFlow) -> void:
	var screen: BattleScreen = flow.screen
	var long_line := "Golpe directo. No ataja la causa: el monstruo se rehará."
	_check("una línea corta se queda al menos %.1f s" % BattleScreen.LOG_READ_MIN,
		screen._read_seconds("Ilan ataca.", false) == BattleScreen.LOG_READ_MIN)
	_check("una línea larga se queda más: %.1f s" % screen._read_seconds(long_line, false),
		screen._read_seconds(long_line, false) > BattleScreen.LOG_READ_MIN)
	_check("un momento clave se queda más todavía",
		screen._read_seconds(long_line, true) > screen._read_seconds(long_line, false))

	var press := InputEventAction.new()
	press.action = "confirm"
	press.pressed = true
	var saved_phase: int = screen._phase
	var saved_queue: Array[Dictionary] = screen._queue.duplicate()
	screen._phase = BattleScreen.Phase.PLAYING
	screen._queue.clear()
	screen._queue.append({"type": "log", "text": "Primera."})
	screen._queue.append({"type": "log", "text": "Segunda."})
	screen._advance_queue()
	screen._unhandled_input(press)
	_check("Enter recién salida la línea no se la come", screen._message == "Primera.", screen._message)
	screen._shown_at_msec -= roundi(BattleScreen.LOG_MIN_SHOW * 1000.0) + 1
	screen._unhandled_input(press)
	_check("después, Enter pasa a la siguiente", screen._message == "Segunda.", screen._message)
	_check("sin Enter, el temporizador sigue en marcha", not screen._step_timer.is_stopped())
	screen._step_timer.stop()
	screen._queue.assign(saved_queue)
	screen._phase = saved_phase

	flow.awaiting_confirm = false
	flow._on_finished(Enums.BattleResult.ONGOING)
	_check("el desenlace no se puede cerrar al salir", not flow.awaiting_confirm)
	var frames := roundi((GameFlow.RESULT_HOLD + 0.2) * Engine.physics_ticks_per_second)
	for _i in frames:
		await get_tree().physics_frame
	_check("pasado %.1f s, Enter ya lo cierra" % GameFlow.RESULT_HOLD, flow.awaiting_confirm)
	flow.awaiting_confirm = false
	_check("en el mundo, la indicación es seguir", screen.continue_hint == "Enter para continuar",
		screen.continue_hint)


## Por turnos (Juan José Rueda, 2026-11-03): en rondas reales, la vida de cada
## bando baja con la acción que la quita, nunca las dos con la misma línea.
func _turn_by_turn(flow: GameFlow) -> void:
	var was_reduced := DesignTokens.reduced_motion
	DesignTokens.reduced_motion = true
	var screen: BattleScreen = flow.screen
	var view: MonsterView = screen._monster_views[0]
	var monster_drops := 0
	var party_drops := 0
	var together := 0
	for round_i in 8:
		while screen._phase != BattleScreen.Phase.CHOOSING and not screen._queue.is_empty():
			screen._advance_queue()
		screen._step_timer.stop()
		if screen._phase != BattleScreen.Phase.CHOOSING:
			break
		# `_submit` ya enseña la primera línea: también hay que medirla.
		var first := true
		while first or (screen._phase == BattleScreen.Phase.PLAYING and not screen._queue.is_empty()):
			var monster_was: float = view._shown_hp
			var party_was := _party_hp(screen)
			if first:
				screen._submit(BattleAction.attack(screen._actor, view.monster))
				first = false
			else:
				screen._advance_queue()
			var monster_fell: bool = view._shown_hp < monster_was
			var party_fell := _party_hp(screen) < party_was
			monster_drops += int(monster_fell)
			party_drops += int(party_fell)
			together += int(monster_fell and party_fell)
		screen._step_timer.stop()
		if monster_drops > 0 and party_drops > 0:
			break
	_check("en rondas reales baja la vida de los dos bandos (monstruo %d, grupo %d)" % [
		monster_drops, party_drops], monster_drops > 0 and party_drops > 0)
	_check("ninguna línea baja las dos vidas a la vez (%d)" % together, together == 0)
	screen._step_timer.stop()
	DesignTokens.reduced_motion = was_reduced


func _party_hp(screen: BattleScreen) -> float:
	var total := 0.0
	for hud in screen._huds:
		total += hud._shown_hp
	return total


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
		if flow.screen == null and not flow.blinds.running and flow.world.wave_radius < 0.0:
			return
