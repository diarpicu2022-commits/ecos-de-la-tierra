class_name BattleManager
extends Node

## Controla el flujo del combate por turnos: abre rondas, pide la acción de cada
## combatiente (a la interfaz si es del jugador, a la IA si es un monstruo),
## resuelve el resultado y decide cuándo termina la batalla.
##
## No dibuja nada. Todo lo que ocurre sale por señales, de modo que la interfaz
## de batalla pueda construirse y cambiarse sin tocar las reglas.

signal battle_started(players: Array, enemies: Array)
signal round_started(round_number: int)
signal turn_started(combatant: Combatant)
signal turn_ended(combatant: Combatant)
signal player_input_required(character: Character)
signal action_resolved(log_lines: Array)
signal combatant_defeated(combatant: Combatant)
signal enemy_joined(enemy: Combatant)
signal battle_ended(result: Enums.BattleResult)

## Energía que recupera cada personaje al empezar una ronda.
const ENERGY_REGEN_PER_ROUND: int = 3

var player_party: Array[Combatant] = []
var enemy_party: Array[Combatant] = []
var inventory: Inventory = null
var result: Enums.BattleResult = Enums.BattleResult.ONGOING

var _turn_manager: TurnManager = null
var _basic_attack: AttackSkill = null
var _current: Combatant = null
var _awaiting_player_input: bool = false


func _init() -> void:
	_basic_attack = SkillLibrary.basic_attack()


# --- Ciclo del combate ------------------------------------------------------

func start_battle(players: Array[Combatant], enemies: Array[Combatant], shared_inventory: Inventory = null) -> void:
	player_party = players
	enemy_party = enemies
	inventory = shared_inventory if shared_inventory != null else Inventory.new()
	result = Enums.BattleResult.ONGOING
	_turn_manager = TurnManager.new()

	for combatant in player_party:
		combatant.team = Enums.Team.PLAYER
	for enemy in enemy_party:
		enemy.team = Enums.Team.ENEMY
		_connect_enemy(enemy)

	battle_started.emit(player_party, enemy_party)
	_start_round()
	advance()


## Hace avanzar el combate hasta que haga falta una decisión del jugador o hasta
## que la batalla termine. La interfaz solo vuelve a llamarla al reanudar.
func advance() -> void:
	while result == Enums.BattleResult.ONGOING:
		if not _turn_manager.has_next():
			_start_round()
			continue

		_current = _turn_manager.next_combatant()
		if _current == null:
			continue

		turn_started.emit(_current)
		_emit_log(_current.tick_statuses_on_turn_start())
		if _check_battle_end():
			return
		if not _current.is_alive() or not _current.can_act():
			_finish_turn(_current)
			continue

		if _current.team == Enums.Team.PLAYER:
			# Se cede el control a la interfaz: el bucle se reanuda cuando esta
			# llame a submit_action().
			_awaiting_player_input = true
			player_input_required.emit(_current as Character)
			return

		var enemy: Monster = _current as Monster
		if enemy != null:
			_resolve_action(enemy.decide_action(_build_context()))
		if _check_battle_end():
			return
		_finish_turn(_current)


## La interfaz envía aquí la acción elegida por el jugador.
func submit_action(action: BattleAction) -> bool:
	if not _awaiting_player_input or action == null or action.actor != _current:
		return false
	_awaiting_player_input = false
	_resolve_action(action)
	if _check_battle_end():
		return true
	_finish_turn(_current)
	advance()
	return true


func get_current_combatant() -> Combatant:
	return _current


func is_awaiting_player_input() -> bool:
	return _awaiting_player_input


## Turnos que quedan por jugarse en la ronda, sin contar a quien actúa ahora.
## Lo consulta la interfaz para responder «¿y después de mí, quién?». Es solo
## lectura: no cambia nada del flujo.
func get_pending_turns() -> Array[Combatant]:
	return _turn_manager.get_pending() if _turn_manager != null else []


func _start_round() -> void:
	var participants: Array[Combatant] = []
	participants.append_array(player_party)
	participants.append_array(enemy_party)
	_turn_manager.start_round(participants)

	for combatant in player_party:
		if combatant.is_alive():
			combatant.restore_energy(ENERGY_REGEN_PER_ROUND)

	round_started.emit(_turn_manager.round_number)


func _finish_turn(combatant: Combatant) -> void:
	_emit_log(combatant.tick_statuses_on_turn_end())
	turn_ended.emit(combatant)


# --- Resolución de acciones -------------------------------------------------

func _resolve_action(action: BattleAction) -> void:
	if action == null:
		return

	var log_lines: Array[String] = []
	match action.type:
		Enums.ActionType.ATTACK:
			log_lines = _apply_skill(action.actor, _basic_attack, action.target)
		Enums.ActionType.SKILL:
			log_lines = _use_skill(action)
		Enums.ActionType.ITEM:
			log_lines = _use_item(action)
		Enums.ActionType.FLEE:
			log_lines = _try_flee(action.actor)

	_emit_log(log_lines)
	_collect_defeated()


func _use_skill(action: BattleAction) -> Array[String]:
	var skill: Skill = action.skill
	if skill == null:
		return []
	if not skill.can_use(action.actor):
		return ["%s no puede usar %s ahora mismo." % [action.actor.display_name, skill.display_name]]
	action.actor.spend_energy(skill.energy_cost)
	return _apply_skill(action.actor, skill, action.target)


## Aplica una habilidad a un objetivo o a todo el bando, según targets_all.
func _apply_skill(user: Combatant, skill: Skill, target: Combatant) -> Array[String]:
	var log_lines: Array[String] = []
	for actual_target in _resolve_targets(user, skill, target):
		log_lines.append_array(skill.execute(user, actual_target))
	return log_lines


func _resolve_targets(user: Combatant, skill: Skill, target: Combatant) -> Array[Combatant]:
	if not skill.targets_all:
		if target != null and target.is_alive():
			return [target]
		return []
	# Una habilidad en área alcanza al bando contrario, salvo que sea de apoyo
	# (cura), en cuyo caso alcanza al propio.
	var is_support: bool = skill is EcoSkill and (skill as EcoSkill).ally_healing > 0
	var affected_team: Enums.Team = user.team if is_support else _opposing_team(user.team)
	return _build_context().get_living(affected_team)


func _use_item(action: BattleAction) -> Array[String]:
	if action.item == null:
		return []
	return inventory.use(action.item, action.actor, action.target)


func _try_flee(actor: Combatant) -> Array[String]:
	# Huir depende de la velocidad de quien huye frente al enemigo más rápido.
	var fastest_enemy: int = 0
	for enemy in _build_context().get_living(Enums.Team.ENEMY):
		fastest_enemy = maxi(fastest_enemy, enemy.get_speed())
	var chance: float = clampf(0.35 + float(actor.get_speed() - fastest_enemy) * 0.05, 0.1, 0.9)

	if randf() <= chance:
		result = Enums.BattleResult.FLED
		battle_ended.emit(result)
		return ["El grupo consigue retirarse del combate."]
	return ["%s intenta huir, pero no encuentra salida." % actor.display_name]


# --- Estado del combate -----------------------------------------------------

func _build_context() -> BattleContext:
	return BattleContext.new(player_party, enemy_party, _turn_manager.round_number)


func _opposing_team(team: Enums.Team) -> Enums.Team:
	return Enums.Team.ENEMY if team == Enums.Team.PLAYER else Enums.Team.PLAYER


## Saca de la ronda a quien haya caído y lo anuncia una sola vez.
func _collect_defeated() -> void:
	var everyone: Array[Combatant] = []
	everyone.append_array(player_party)
	everyone.append_array(enemy_party)
	for combatant in everyone:
		if not combatant.is_alive() and _turn_manager.get_pending().has(combatant):
			_turn_manager.remove(combatant)
			combatant_defeated.emit(combatant)


func _check_battle_end() -> bool:
	if result != Enums.BattleResult.ONGOING:
		return true

	var context: BattleContext = _build_context()
	if context.get_living(Enums.Team.ENEMY).is_empty():
		result = Enums.BattleResult.VICTORY
		_award_rewards()
		battle_ended.emit(result)
		return true
	if context.get_living(Enums.Team.PLAYER).is_empty():
		result = Enums.BattleResult.DEFEAT
		battle_ended.emit(result)
		return true
	return false


## Reparte experiencia al ganar. El Conocimiento Ambiental no se reparte aquí:
## se consigue explorando y resolviendo puzzles, no ganando combates.
func _award_rewards() -> void:
	var total_experience: int = 0
	for enemy in enemy_party:
		if enemy is Monster:
			total_experience += (enemy as Monster).experience_reward

	var survivors: Array[Combatant] = _build_context().get_living(Enums.Team.PLAYER)
	if survivors.is_empty() or total_experience <= 0:
		return
	var share: int = int(float(total_experience) / float(survivors.size()))
	for survivor in survivors:
		if survivor is Character:
			(survivor as Character).add_experience(share)


# --- Enemigos que aparecen a mitad del combate ------------------------------

func _connect_enemy(enemy: Combatant) -> void:
	if enemy.has_signal("clone_requested") and not enemy.is_connected("clone_requested", _on_clone_requested):
		enemy.connect("clone_requested", _on_clone_requested)


func _on_clone_requested(clone: Combatant) -> void:
	clone.team = Enums.Team.ENEMY
	add_child(clone)
	enemy_party.append(clone)
	_connect_enemy(clone)
	_turn_manager.insert(clone)
	enemy_joined.emit(clone)


func _emit_log(log_lines: Array) -> void:
	if log_lines.is_empty():
		return
	action_resolved.emit(log_lines)
