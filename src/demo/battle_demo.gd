extends Node

## Prueba de concepto del sistema de combate, sin interfaz gráfica todavía.
## Ejecuta varios combates automáticos y escribe el registro por consola:
##
##   1. Bosque de las Cenizas: demuestra que la fuerza bruta no cierra el
##      combate (el monstruo se regenera) y que la Línea Cortafuegos sí.
##   2. Llanura Marchita: demuestra los clones del Espectro del Monocultivo,
##      que se suman a la ronda en curso.
##   3. Cripta de la Avaricia: demuestra la tabla Q del jefe final, comparando a
##      un jugador que repite siempre la misma habilidad con otro que las
##      combina.
##
## Sirve para verificar la arquitectura antes de montar la interfaz de batalla.

## Turnos que el grupo malgasta atacando antes de aplicar la contramedida.
const BRUTE_FORCE_TURNS: int = 3
## Tope de rondas para que un combate sin salida no se quede colgado.
const MAX_ROUNDS: int = 14

var _manager: BattleManager = null
var _brute_force_left: int = 0
var _rotate_eco_skills: bool = false
var _eco_skill_index: int = 0
var _round: int = 0


func _ready() -> void:
	randomize()
	_check_regeneration_rule()
	_run_forest_battle()
	_run_specter_battle()
	_run_boss_battle(false)
	_run_boss_battle(true)


# --- Regla 1: la fuerza bruta no cierra el combate --------------------------

## Comprobación directa, sin combate de por medio: se tira al monstruo a 0 PV
## dos veces, antes y después de aplicar la contramedida, y se mira qué pasa.
func _check_regeneration_rule() -> void:
	_print_header("REGLA 1 — el monstruo se regenera hasta que se ataja la causa")

	var monster := DeforestationFlame.new()
	add_child(monster)
	print("   PV iniciales: %d de %d" % [monster.hp, monster.max_hp])

	monster.take_damage(monster.max_hp * 4, Enums.EcoType.NONE, true)
	print("   Tras un golpe que lo dejaría a 0 sin purificar: %d PV, purificado = %s" % [
		monster.hp, monster.is_purified
	])

	var counter := SkillLibrary.firebreak_line()
	for line in monster.receive_eco_skill(counter):
		print("   %s" % line)

	monster.take_damage(monster.max_hp * 4, Enums.EcoType.NONE, true)
	print("   Tras el mismo golpe ya purificado: %d PV, sigue en pie = %s" % [
		monster.hp, monster.is_alive()
	])
	monster.queue_free()


# --- Combate 1: Bosque de las Cenizas ---------------------------------------

func _run_forest_battle() -> void:
	_print_header("BOSQUE DE LAS CENIZAS — Llama de la Deforestación")

	var bruma: Character = PartyLibrary.bruma()
	var coral: Character = PartyLibrary.coral()
	for character in [bruma, coral]:
		character.gain_knowledge(Enums.EcoType.FIRE)
		character.gain_knowledge(Enums.EcoType.OIL)

	var monster := DeforestationFlame.new()
	_brute_force_left = BRUTE_FORCE_TURNS
	_rotate_eco_skills = false
	_start([bruma, coral], [monster])


# --- Combate 2: Llanura Marchita --------------------------------------------

## Comprueba la Multiplicación: el Espectro genera clones que entran en la ronda
## en curso y que también hay que purificar uno a uno.
func _run_specter_battle() -> void:
	_print_header("LLANURA MARCHITA — Espectro del Monocultivo y sus clones")

	# En este punto de la historia Ilan ya viaja con Nix y con Suri: tres contra
	# el Espectro y sus dos clones.
	var ilan: Character = PartyLibrary.ilan()
	var nix: Character = PartyLibrary.nix()
	var suri: Character = PartyLibrary.suri()
	for character in [ilan, nix, suri]:
		character.gain_knowledge(Enums.EcoType.MONOCULTURE)
		character.gain_knowledge(Enums.EcoType.PLASTIC)

	var monster := MonocultureSpecter.new()
	_brute_force_left = 0
	_rotate_eco_skills = false
	_start([ilan, nix, suri], [monster])


# --- Combate 3: Cripta de la Avaricia ---------------------------------------

func _run_boss_battle(rotate: bool) -> void:
	var title: String = "combinando las cinco contramedidas" if rotate else "repitiendo siempre la misma"
	_print_header("CRIPTA DE LA AVARICIA — %s" % title)

	var party: Array[Character] = PartyLibrary.full_party()
	var boss := AdaptiveBoss.new()
	boss.combo_progressed.connect(func(used: int, required: int) -> void:
		print("   · Contramedidas distintas aplicadas: %d de %d" % [used, required])
	)

	_brute_force_left = 0
	_rotate_eco_skills = rotate
	_eco_skill_index = 0

	var combatants: Array[Combatant] = []
	for character in party:
		combatants.append(character)
	_start(combatants, [boss])

	print("   Tabla Q final del jefe:")
	for eco_type in boss.q_table.keys():
		print("     %-12s resistencia aprendida %.2f" % [
			Enums.eco_type_name(eco_type), boss.q_table[eco_type]
		])


# --- Infraestructura del combate --------------------------------------------

func _start(players: Array, enemies: Array) -> void:
	_round = 0
	_manager = BattleManager.new()
	add_child(_manager)

	var player_party: Array[Combatant] = []
	for player in players:
		add_child(player)
		player_party.append(player)
	var enemy_party: Array[Combatant] = []
	for enemy in enemies:
		add_child(enemy)
		enemy_party.append(enemy)

	var inventory := Inventory.new()
	inventory.add(ItemLibrary.healing_herb(), 3)
	inventory.add(ItemLibrary.purified_water(), 2)

	for enemy in enemy_party:
		if enemy is Monster:
			(enemy as Monster).regenerated.connect(_on_monster_regenerated.bind(enemy))

	_manager.round_started.connect(_on_round_started)
	_manager.action_resolved.connect(_on_action_resolved)
	_manager.combatant_defeated.connect(_on_combatant_defeated)
	_manager.enemy_joined.connect(_on_enemy_joined)
	_manager.player_input_required.connect(_on_player_input_required)
	_manager.battle_ended.connect(_on_battle_ended)

	_manager.start_battle(player_party, enemy_party, inventory)

	# El combate es síncrono en esta prueba: al volver ya terminó.
	_manager.queue_free()
	_manager = null


func _on_round_started(round_number: int) -> void:
	_round = round_number
	print("\n-- Ronda %d --" % round_number)


func _on_action_resolved(log_lines: Array) -> void:
	for line in log_lines:
		print("   %s" % line)


func _on_combatant_defeated(combatant: Combatant) -> void:
	print("   ** %s queda fuera de combate. **" % combatant.display_name)


func _on_monster_regenerated(current_hp: int, monster: Combatant) -> void:
	print("   ** %s se rehace: vuelve a %d PV. El daño no se atajó. **" % [
		monster.display_name, current_hp
	])


func _on_enemy_joined(enemy: Combatant) -> void:
	print("   ** Se suma al combate: %s **" % enemy.display_name)


func _on_battle_ended(result: Enums.BattleResult) -> void:
	match result:
		Enums.BattleResult.VICTORY: print("\n   >> Victoria del grupo.")
		Enums.BattleResult.DEFEAT: print("\n   >> El grupo queda fuera de combate.")
		Enums.BattleResult.FLED: print("\n   >> El grupo se retira.")
		_: print("\n   >> Combate interrumpido.")


func _print_header(title: String) -> void:
	print("\n==============================================================")
	print(" %s" % title)
	print("==============================================================")


# --- Política del jugador simulado ------------------------------------------
# Sustituye a la interfaz: decide qué hace el grupo en cada turno.

func _on_player_input_required(character: Character) -> void:
	var target: Combatant = _first_living_enemy()
	if target == null:
		return

	# Cortafuegos de la prueba: si el combate se alarga, el grupo se retira.
	if _round > MAX_ROUNDS:
		_manager.submit_action(BattleAction.flee(character))
		return

	# Primeros turnos a base de golpes, para ver cómo el monstruo se regenera.
	if _brute_force_left > 0:
		_brute_force_left -= 1
		_manager.submit_action(BattleAction.attack(character, target))
		return

	# Antes de atacar, atiende al grupo si alguien está muy tocado. Así la
	# prueba recorre también el Filtro Biológico y la Bolsa.
	var support: BattleAction = _choose_support_action(character)
	if support != null:
		_manager.submit_action(support)
		return

	var skill: Skill = _choose_eco_skill(character, target)
	if skill != null:
		_manager.submit_action(BattleAction.use_skill(character, skill, target))
	else:
		_manager.submit_action(BattleAction.attack(character, target))


## Curar o usar un objeto cuando alguien del grupo baja del 45 % de sus PV.
## Devuelve null si no hace falta o si no hay con qué.
func _choose_support_action(character: Character) -> BattleAction:
	var ally: Combatant = _weakest_ally()
	if ally == null or ally.get_hp_ratio() > 0.45:
		return null

	for skill in character.get_usable_skills():
		if skill is EcoSkill and (skill as EcoSkill).ally_healing > 0:
			return BattleAction.use_skill(character, skill, ally)

	for item in _manager.inventory.get_battle_items():
		if item is HealingItem and (item as HealingItem).heal_amount > 0:
			return BattleAction.use_item(character, item, ally)
	return null


func _weakest_ally() -> Combatant:
	var weakest: Combatant = null
	for member in _manager.player_party:
		if not member.is_alive():
			continue
		if weakest == null or member.get_hp_ratio() < weakest.get_hp_ratio():
			weakest = member
	return weakest


## Elige la Habilidad Ecológica adecuada según el monstruo que haya delante.
func _choose_eco_skill(character: Character, target: Combatant) -> Skill:
	if not (target is Monster):
		return null
	var monster: Monster = target as Monster
	if monster.is_purified:
		return null

	var offensive: Array[EcoSkill] = []
	for skill in character.get_usable_skills():
		if skill is EcoSkill and (skill as EcoSkill).ally_healing == 0:
			offensive.append(skill as EcoSkill)
	if offensive.is_empty():
		return null

	if monster is AdaptiveBoss:
		var boss: AdaptiveBoss = monster as AdaptiveBoss
		if _rotate_eco_skills:
			# Jugador que combina: prioriza una contramedida que no haya usado.
			for skill in offensive:
				if not boss.used_eco_types.has(skill.weakness_type):
					return skill
			return offensive[0]
		# Jugador que abusa de una sola habilidad: solo la del fuego.
		for skill in offensive:
			if skill.weakness_type == Enums.EcoType.FIRE:
				return skill
		return null

	for skill in offensive:
		if skill.weakness_type == monster.required_counter_type:
			return skill
	return null


func _first_living_enemy() -> Combatant:
	for enemy in _manager.enemy_party:
		if enemy.is_alive():
			return enemy
	return null
