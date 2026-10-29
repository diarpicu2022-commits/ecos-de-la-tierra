extends Node

## Prueba de IA-5, el componente clave (contrato «Orden de líder», paso 2).
## Sin ventana y con semilla fija:
##
##   godot --headless --path . res://tools/verify_party_ai.tscn
##
## - La red aprende un estilo sintético: > 80 % de acierto sobre situaciones
##   nuevas tras PARTY_LEARN_DECISIONS decisiones.
## - Cada orden sesga lo que debe.
## - Con un líder bueno la sintonía sube; con uno malo baja; desde 0,
##   SYNC_RECOVER decisiones buenas la devuelven al tramo medio.
## - Con la sintonía alta el compañero duda menos que con la baja.
## - En combate (Cuenca, 40 combates por líder): solo se le pide decisión al
##   líder; cada compañero deja su línea en el registro; con un líder bueno la
##   sintonía sube y se gana en menos rondas que con uno malo.
## - El menú de Ilan lleva la fila de orden, cabe sin recorte y cambia la
##   orden al confirmar.
## Sale con código 1 si algo falla.

const C := PartyMind.Choice

var _pass := 0
var _fail := 0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = 20261028
	_learning()
	_orders()
	_sync()
	_doubt()
	await _battles()
	await _menu()
	print("\n%d de %d OK" % [_pass, _pass + _fail])
	get_tree().quit(1 if _fail else 0)


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
	else:
		_fail += 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


## Una situación al azar con las 12 entradas.
func _situation() -> PackedFloat32Array:
	var x := PackedFloat32Array()
	for i in DesignTokens.PARTY_INPUTS:
		x.append(_rng.randf())
	for i in [5, 6, 7, 8]:
		x[i] = float(_rng.randf() < 0.5)
	return x


## El estilo sintético de un líder: ataja la causa si puede; si no, cura a
## quien baja del 45 %; si no, ataca.
func _style(x: PackedFloat32Array) -> int:
	if x[5] > 0.5 and x[6] > 0.5:
		return C.COUNTER
	if x[3] < PartyMind.HURT and x[7] > 0.5:
		return C.HEAL
	return C.ATTACK


func _learning() -> void:
	print("La red aprende del líder")
	var mind := PartyMind.new(7)
	var before := _accuracy(mind)
	for n in DesignTokens.PARTY_LEARN_DECISIONS:
		var x := _situation()
		mind.train(x, _style(x))
	var after := _accuracy(mind)
	_check("acierto sobre 500 situaciones nuevas: %d %% antes, %d %% tras %d decisiones (> 80 %%)" % [
		roundi(before * 100), roundi(after * 100), DesignTokens.PARTY_LEARN_DECISIONS], after > 0.8)


func _accuracy(mind: PartyMind) -> float:
	var ok := 0
	var all := [true, true, true, true]
	for n in 500:
		var x := _situation()
		ok += int(mind.preferred(x, PartyMind.Order.FOLLOW, all) == _style(x))
	return ok / 500.0


func _orders() -> void:
	print("\nLa orden sesga")
	var mind := PartyMind.new(3)
	var all := [true, true, true, true]
	var cause := 0
	var cover := 0
	for n in 300:
		var x := _situation()
		cause += int(mind.preferred(x, PartyMind.Order.CAUSE, all) == C.COUNTER)
		var c := mind.preferred(x, PartyMind.Order.COVER, all)
		cover += int(c == C.HEAL or c == C.ITEM)
	_check("«Atajad la causa» lleva a la contramedida (%d de 300)" % cause, cause > 270)
	_check("«Cubríos» lleva a curar u objeto (%d de 300)" % cover, cover > 270)
	var no_counter := [true, false, true, true]
	var x := _situation()
	_check("nunca elige lo que no puede hacer",
		mind.preferred(x, PartyMind.Order.CAUSE, no_counter) != C.COUNTER)


func _sync() -> void:
	print("\nSintonía")
	var s := DesignTokens.SYNC_START
	for n in 6:
		s = PartyMind.update_sync(s, PartyMind.judge(C.COUNTER, true, true, 1.0, false))
	_check("un líder bueno la sube: %.2f → %.2f" % [DesignTokens.SYNC_START, s], s > DesignTokens.SYNC_START)
	s = DesignTokens.SYNC_START
	for n in 6:
		s = PartyMind.update_sync(s, PartyMind.judge(C.ATTACK, true, true, 1.0, false))
	_check("uno malo la baja: %.2f → %.2f" % [DesignTokens.SYNC_START, s], s < DesignTokens.SYNC_START)
	s = 0.0
	for n in DesignTokens.SYNC_RECOVER:
		s = PartyMind.update_sync(s, 1)
	_check("desde 0, %d decisiones buenas la devuelven al tramo medio (%.2f ≥ 0,5)" % [
		DesignTokens.SYNC_RECOVER, s], s >= 0.5)
	_check("repetir un tipo contra la Sombra es malo",
		PartyMind.judge(C.COUNTER, true, true, 1.0, true) == -1)
	_check("curar sin que haga falta es malo; curar a quien baja del 45 % es bueno",
		PartyMind.judge(C.HEAL, true, true, 0.9, false) == -1 and PartyMind.judge(C.HEAL, true, true, 0.3, false) == 1)


func _doubt() -> void:
	print("\nPrecisión según la sintonía")
	var mind := PartyMind.new(5)
	var all := [true, true, true, true]
	var doubts := {}
	for sync in [0.0, 1.0]:
		var d := 0
		for n in 1000:
			d += int(mind.choose(_situation(), PartyMind.Order.FOLLOW, sync, all, _rng)["doubted"])
		doubts[sync] = d
	_check("duda %d de 1000 con sintonía 0 y %d con sintonía 1" % [doubts[0.0], doubts[1.0]],
		doubts[0.0] > 400 and doubts[1.0] == 0)


## Combates reales con los compañeros en automático.
func _battles() -> void:
	print("
En combate")
	var stats := {}
	for style in ["bueno", "malo"]:
		var rounds := 0
		var wins := 0
		var sync_end := 0.0
		# Contadores en un diccionario: las lambdas capturan los enteros por valor.
		var count := {"asked": 0, "lines": 0}
		for n in 40:
			var holder := Node.new()
			add_child(holder)
			var players: Array[Combatant] = []
			for c in Encounters.build_party(1):
				holder.add_child(c)
				players.append(c)
			var monster := Encounters.build_monster(1)
			holder.add_child(monster)
			var enemies: Array[Combatant] = [monster]
			var m := BattleManager.new()
			holder.add_child(m)
			m.companions_auto = true
			m.player_input_required.connect(func(c: Character):
				if c != m.leader:
					count["asked"] += 1
				if m._turn_manager.round_number > 30:
					m.submit_action(BattleAction.flee(c))
					return
				var target := m._monster()
				var counter := m._counter_skill(c)
				if style == "bueno" and counter != null:
					m.order = PartyMind.Order.CAUSE
					m.submit_action(BattleAction.use_skill(c, counter, target))
				else:
					m.order = PartyMind.Order.FOLLOW
					m.submit_action(BattleAction.attack(c, target)))
			m.action_resolved.connect(func(l: Array):
				for t in l:
					if " sigue " in str(t) or " duda:" in str(t):
						count["lines"] += 1)
			m.start_battle(players, enemies, Encounters.build_inventory(1))
			rounds += m._turn_manager.round_number
			wins += int(m.result == Enums.BattleResult.VICTORY)
			sync_end += m.sync
			holder.free()
		stats[style] = {"rounds": rounds / 40.0, "wins": wins, "sync": sync_end / 40.0}
		_check("líder %s: solo se le pide decisión a él (%d peticiones a otros)" % [style, count["asked"]],
			count["asked"] == 0)
		_check("  cada compañero deja su motivo en el registro (%d líneas)" % count["lines"], count["lines"] > 40)
	_check("con un líder bueno la sintonía sube (%.2f) y con uno malo baja (%.2f)" % [
		stats["bueno"]["sync"], stats["malo"]["sync"]],
		stats["bueno"]["sync"] > DesignTokens.SYNC_START and stats["malo"]["sync"] < DesignTokens.SYNC_START)
	_check("con un líder bueno se gana en menos rondas (%.1f frente a %.1f; victorias %d y %d de 40)" % [
		stats["bueno"]["rounds"], stats["malo"]["rounds"], stats["bueno"]["wins"], stats["malo"]["wins"]],
		stats["bueno"]["rounds"] < stats["malo"]["rounds"])
	await get_tree().process_frame


## La fila de orden en el menú de Ilan.
func _menu() -> void:
	print("
Menú del líder")
	var holder := Node.new()
	add_child(holder)
	var screen := BattleScreen.new()
	screen.companions_auto = true
	holder.add_child(screen)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(1):
		holder.add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(1)
	holder.add_child(monster)
	var enemies: Array[Combatant] = [monster]
	screen.start_battle(players, enemies, Encounters.build_inventory(1), Enums.Team.PLAYER)
	for i in 300:
		if screen._phase == BattleScreen.Phase.CHOOSING and screen._actor == screen._manager.leader:
			break
		screen._advance_queue()
		await get_tree().process_frame
	var labels: Array = screen._menu.entries.map(func(e): return str(e["label"]))
	_check("el menú de Ilan lleva la fila de orden (%s)" % ", ".join(labels),
		labels.size() == 5 and labels[-1].begins_with("ORDEN"))
	var room: float = screen._menu.size.x - ActionMenu.CURSOR_WIDTH
	var widest := 0.0
	for o in BattleScreen.ORDERS:
		widest = maxf(widest, screen._menu._width("ORDEN: " + o["label"]))
	_check("las tres órdenes caben sin recorte (%d de %d px)" % [widest, room], widest <= room)
	var before: int = screen._manager.order
	screen._on_option_chosen(screen._menu.entries[-1])
	_check("confirmar la fila cambia la orden sin gastar el turno (%d → %d)" % [before, screen._manager.order],
		screen._manager.order == (before + 1) % 3 and screen._phase == BattleScreen.Phase.CHOOSING)
	holder.queue_free()
	await get_tree().process_frame
