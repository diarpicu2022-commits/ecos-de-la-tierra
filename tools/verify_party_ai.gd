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
## - En combate (contra la Sombra, 40 combates por líder; en una región la
##   compañera con la contramedida purifica antes de que Ilan decida, y la
##   causa no dura lo bastante para juzgar): solo se le pide decisión al
##   líder; cada compañero deja su línea en el registro; con un líder bueno la
##   sintonía sube y se gana en menos rondas que con uno malo.
## - El menú de Ilan son los cuatro mandos, sin fila de orden. Tab cambia la orden
##   sin gastar el turno, solo para el líder y solo en la raíz, y el aviso de papel
##   la dice sin salirse de `MESSAGE_RECT`.
## - Lo deshabilitado recibe foco, dice el porqué y no se puede elegir.
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
			for c in Encounters.build_party(5):
				holder.add_child(c)
				players.append(c)
			var monster := Encounters.build_monster(5)
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
				var fresh: bool = counter != null and not (target is AdaptiveBoss
					and (target as AdaptiveBoss).used_eco_types.has(counter.weakness_type))
				if style == "bueno":
					# Manda atajar y combina: usa su contramedida solo si es un tipo nuevo.
					m.order = PartyMind.Order.CAUSE
					if fresh:
						m.submit_action(BattleAction.use_skill(c, counter, target))
					else:
						m.submit_action(BattleAction.attack(c, target))
				else:
					m.order = PartyMind.Order.FOLLOW
					m.submit_action(BattleAction.attack(c, target)))
			m.action_resolved.connect(func(l: Array):
				for t in l:
					if " sigue " in str(t) or " duda:" in str(t):
						count["lines"] += 1)
			m.start_battle(players, enemies, Encounters.build_inventory(5))
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


## La orden en Tab, en el menú de Ilan.
func _menu() -> void:
	print("
Menú del líder")
	var holder := Node.new()
	add_child(holder)
	var screen := await _leader_screen(holder, true)
	var labels: Array = screen._menu.entries.map(func(e): return str(e["label"]))
	_check("el menú de Ilan son cuatro mandos, sin fila de orden (%s)" % ", ".join(labels),
		labels == ["LUCHAR", "ECO", "BOLSA", "HUIR"] and screen._menu.is_grid())
	var on_tab := false
	if InputMap.has_action("order"):
		for e in InputMap.action_get_events("order"):
			on_tab = on_tab or (e is InputEventKey and (e as InputEventKey).physical_keycode == KEY_TAB)
	_check("la acción «order» está en Tab", on_tab)
	_check("el aviso de la raíz dice la orden actual y la tecla",
		screen._message.contains("Orden: " + str(BattleScreen.ORDERS[screen._manager.order]["label"]))
		and screen._message.contains("Tab"))
	await _message_fit(screen)

	var before: int = screen._manager.order
	var actor: Character = screen._actor
	var round_before: int = screen._manager._turn_manager.round_number
	var queue_before: int = screen._queue.size()
	screen._menu.focused = 2
	await _press_tab()
	var o: Dictionary = BattleScreen.ORDERS[screen._manager.order]
	_check("Tab cambia la orden (%d → %d)" % [before, screen._manager.order],
		screen._manager.order == (before + 1) % 3)
	_check("Tab no gasta el turno", screen._phase == BattleScreen.Phase.CHOOSING
		and screen._actor == actor and screen._queue.size() == queue_before
		and screen._manager._turn_manager.round_number == round_before and screen._menu.is_active())
	_check("el aviso enseña la descripción de la nueva orden: «%s»" % screen._message,
		screen._message.begins_with(str(o["description"])))
	_check("Tab no mueve el foco", screen._menu.focused == 2)
	_check("al moverse, el aviso sigue diciendo la orden nueva",
		str(screen._menu.entries[0]["description"]).contains("Orden: " + str(o["label"])))
	await _press_tab()
	await _press_tab()
	_check("tres pulsaciones dan la vuelta a las tres órdenes", screen._manager.order == before)

	# Fuera de la raíz, Tab no hace nada: el aviso está explicando otra cosa.
	screen._menu.focused = 2
	screen._on_option_chosen(screen._menu.entries[2])
	var shown: String = screen._message
	await _press_tab()
	_check("en un submenú, Tab no cambia la orden",
		screen._manager.order == before and screen._message == shown)
	screen._on_menu_cancelled()
	_check("al volver, el foco sigue en el mando del que se vino", screen._menu.focused == 2)

	# Tampoco para quien no es el líder ni mientras se reproduce el registro.
	for c in screen._manager.player_party:
		if c != screen._manager.leader:
			screen._actor = c
			break
	await _press_tab()
	_check("Tab no actúa si el turno no es del líder", screen._manager.order == before)
	screen._actor = screen._manager.leader
	screen._phase = BattleScreen.Phase.PLAYING
	await _press_tab()
	_check("Tab no actúa fuera de la fase de elección", screen._manager.order == before)
	screen._phase = BattleScreen.Phase.CHOOSING

	# Lo deshabilitado: recibe foco, dice el porqué y no se puede elegir.
	screen._manager.inventory = Inventory.new()
	screen._root_focus = 0
	screen._open_root_menu()
	var bag: Dictionary = screen._menu.entries[2]
	await _press("move_down")
	_check("BOLSA vacía recibe el foco y dice el porqué: «%s»" % screen._message,
		screen._menu.focused == 2 and not bool(bag["enabled"]) and screen._message.contains("vacía"))
	await _press("confirm")
	_check("confirmarla no abre nada ni gasta el turno",
		screen._menu.is_grid() and screen._menu.focused == 2 and screen._phase == BattleScreen.Phase.CHOOSING)
	var voice: AudioStreamPlayer = GameAudio._voices[wrapi(GameAudio._next_voice - 1, 0, GameAudio.VOICES)]
	_check("y suena ui_denied", voice.stream == GameAudio._streams["ui_denied"])
	holder.queue_free()
	await get_tree().process_frame

	var solo := Node.new()
	add_child(solo)
	var manual := await _leader_screen(solo, false)
	var order_manual: int = manual._manager.order
	await _press_tab()
	_check("sin compañeros en automático, Tab no actúa y el aviso no la nombra",
		manual._manager.order == order_manual and not manual._message.contains("Orden"))
	solo.queue_free()
	await get_tree().process_frame


## Todas las combinaciones de aviso de la raíz contra `MESSAGE_RECT`: se reparten
## con el mismo `_wrap` y la interlínea del dibujo.
func _message_fit(screen: BattleScreen) -> void:
	var rect := BattleScreen.MESSAGE_RECT
	var pad: float = DesignTokens.SPACE_8 + 2.0
	var room := rect.size.x - pad * 2.0
	# Primera línea de base 18 px bajo el borde; `_draw_message` corta a 6 del fondo.
	var capacity: int = floori((rect.size.y - 18.0 - 6.0) / BattleScreen.MESSAGE_LINE) + 1
	var worst := 0
	var widest := 0.0
	var longest := ""
	var messages: Array[String] = []
	var saved: int = screen._manager.order
	var actor: Character = screen._actor
	var skills: Array[Skill] = actor.skills
	var inventory: Inventory = screen._manager.inventory
	for order in BattleScreen.ORDERS.size():
		screen._manager.order = order
		messages.append("%s %s" % [BattleScreen.ORDERS[order]["description"], BattleScreen.ORDER_KEY_HINT])
		# Con lo que hay y con lo deshabilitado: es el texto más largo.
		for empty in [false, true]:
			actor.skills = ([] as Array[Skill]) if empty else skills
			screen._manager.inventory = Inventory.new() if empty else inventory
			for entry in screen._root_entries():
				messages.append(str(entry["description"]))
	actor.skills = skills
	screen._manager.inventory = inventory
	screen._manager.order = saved
	for text in messages:
		var lines: PackedStringArray = screen._wrap(text, room)
		if lines.size() > worst:
			worst = lines.size()
			longest = text
		for line in lines:
			widest = maxf(widest, screen._width(line))
	_check("los %d avisos posibles caben en el papel: %d líneas de %d, %d de %d px («%s»)" % [
		messages.size(), worst, capacity, roundi(widest), roundi(room), longest.replace("\n", " / ")],
		worst <= capacity and widest <= room)


## Monta un combate y espera a la primera elección del líder.
func _leader_screen(holder: Node, auto: bool) -> BattleScreen:
	var screen := BattleScreen.new()
	screen.companions_auto = auto
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
	return screen


## Una pulsación real de la tecla, no de la acción: es la que Godot podría quedarse
## para mover el foco de los controles.
func _press_tab() -> void:
	for pressed in [true, false]:
		var key := InputEventKey.new()
		key.physical_keycode = KEY_TAB
		key.pressed = pressed
		Input.parse_input_event(key)
		await get_tree().process_frame


func _press(action: String) -> void:
	for pressed in [true, false]:
		var event := InputEventAction.new()
		event.action = action
		event.pressed = pressed
		Input.parse_input_event(event)
		await get_tree().process_frame
