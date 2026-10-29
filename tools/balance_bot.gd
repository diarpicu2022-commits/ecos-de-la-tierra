extends Node

## IA-4 · Bot de equilibrado (guía §3.3). Solo desarrollo, sin ventana:
##
##   godot --headless --path . res://tools/balance_bot.tscn
##
## Juega COMBATS combates por región con tres políticas y semilla fija:
##
## - **aleatoria:** cualquier acción posible, al azar;
## - **voraz:** el grupo repite una sola habilidad, la contramedida del fuego;
##   quien no la tiene, o no puede usarla, ataca;
## - **experta:** cura a tiempo, ataja la causa con la contramedida de la
##   región y, contra la Sombra, combina las que aún no ha usado.
##
## Escribe `docs/balance/2026-10-28-<región>.csv` (una fila por combate) y
## comprueba los dos criterios de la guía:
## 1. la experta gana siempre;
## 2. la voraz pierde contra la Sombra (gana ≤ GREEDY_BOSS_MAX).
## Además entrena la tabla Q de la Sombra encadenando sus combates (la
## tabla de uno pasa al siguiente) y la guarda en
## `data/balance/sombra_q.json`, para cargarla con `load_q_table()`.
## Sale con código 1 si un criterio falla.

const COMBATS := 300
const SEED := 20261028
const MAX_ROUNDS := 30
## La voraz puede ganar alguna por suerte, pero no más que esto.
const GREEDY_BOSS_MAX := 0.10
const DATE := "2026-10-28"
const POLICIES := ["aleatoria", "voraz", "experta"]
const SLUG := ["bosque", "cuenca", "costa", "llanura", "cumbre", "cripta"]

var _manager: BattleManager = null
var _policy := ""
var _rng := RandomNumberGenerator.new()
var _used := {}
var _fails := 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/balance"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://data/balance"))
	var trained := {}
	for index in Encounters.count():
		var rows := PackedStringArray(["politica,combate,resultado,rondas,habilidades"])
		var wins := {}
		print("\n%s (%s)" % [Encounters.get_encounter(index)["region"], SLUG[index]])
		for policy in POLICIES:
			_policy = policy
			_rng.seed = SEED + index * 10 + POLICIES.find(policy)
			seed(_rng.seed)
			wins[policy] = 0
			var rounds_total := 0
			for n in COMBATS:
				var outcome := _play(index, trained if index == 5 else {})
				if outcome["result"] == Enums.BattleResult.VICTORY:
					wins[policy] += 1
				rounds_total += outcome["rounds"]
				if index == 5:
					trained = outcome["q"]
				rows.append("%s,%d,%s,%d,%s" % [policy, n, ["en curso", "victoria", "derrota", "huida"][outcome["result"]],
					outcome["rounds"], " ".join(outcome["skills"])])
			print("  %-9s gana %3d de %d · %.1f rondas de media" % [policy, wins[policy], COMBATS,
				float(rounds_total) / COMBATS])
		var file := FileAccess.open("res://docs/balance/%s-%s.csv" % [DATE, SLUG[index]], FileAccess.WRITE)
		file.store_string("\n".join(rows) + "\n")
		file.close()
		_check("la experta gana siempre (%d de %d)" % [wins["experta"], COMBATS], wins["experta"] == COMBATS)
		if index == 5:
			_check("la voraz pierde contra la Sombra (gana %d de %d, tope %d %%)" % [
				wins["voraz"], COMBATS, roundi(GREEDY_BOSS_MAX * 100)],
				float(wins["voraz"]) / COMBATS <= GREEDY_BOSS_MAX)
	var q := {}
	for k in trained:
		q[str(k)] = trained[k]
	var out := FileAccess.open("res://data/balance/sombra_q.json", FileAccess.WRITE)
	out.store_string(JSON.stringify({"_doc": "Tabla Q de la Sombra entrenada por tools/balance_bot.gd (IA-4). Clave: Enums.EcoType.", "seed": SEED, "q": q}, "\t") + "\n")
	out.close()
	print("\nTabla Q de la Sombra entrenada: %s" % JSON.stringify(q))
	print("\n%s" % ("Todo en verde." if _fails == 0 else "%d criterios fallan." % _fails))
	get_tree().quit(1 if _fails else 0)


func _check(label: String, ok: bool) -> void:
	_fails += 0 if ok else 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


## Un combate entero. Devuelve resultado, rondas, habilidades y la tabla Q.
func _play(index: int, q: Dictionary) -> Dictionary:
	var holder := Node.new()
	add_child(holder)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(index):
		holder.add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(index)
	holder.add_child(monster)
	if monster is AdaptiveBoss and not q.is_empty():
		(monster as AdaptiveBoss).load_q_table(q)
	var enemies: Array[Combatant] = [monster]
	_used = {}
	_manager = BattleManager.new()
	holder.add_child(_manager)
	_manager.player_input_required.connect(_decide)
	_manager.start_battle(players, enemies, Encounters.build_inventory(index))
	var skills := PackedStringArray()
	for k in _used:
		skills.append("%s:%d" % [k, _used[k]])
	var out := {"result": _manager.result, "rounds": _manager._turn_manager.round_number,
		"skills": skills, "q": (monster as AdaptiveBoss).q_table.duplicate() if monster is AdaptiveBoss else {}}
	holder.free()
	return out


func _decide(character: Character) -> void:
	if _manager._turn_manager.round_number > MAX_ROUNDS:
		_submit(BattleAction.flee(character))
		return
	var target := _enemy()
	match _policy:
		"aleatoria":
			_submit(_random_action(character, target))
		"voraz":
			for skill in character.get_usable_skills():
				if skill is EcoSkill and (skill as EcoSkill).weakness_type == Enums.EcoType.FIRE:
					_submit(BattleAction.use_skill(character, skill, target))
					return
			_submit(BattleAction.attack(character, target))
		"experta":
			_submit(_expert_action(character, target))


func _submit(action: BattleAction) -> void:
	if action.type == Enums.ActionType.SKILL:
		_used[action.skill.display_name] = _used.get(action.skill.display_name, 0) + 1
	_manager.submit_action(action)


func _random_action(character: Character, target: Combatant) -> BattleAction:
	var options: Array[BattleAction] = [BattleAction.attack(character, target)]
	for skill in character.get_usable_skills():
		var healing := skill is EcoSkill and (skill as EcoSkill).ally_healing > 0
		options.append(BattleAction.use_skill(character, skill, _ally() if healing else target))
	for item in _manager.inventory.get_battle_items():
		options.append(BattleAction.use_item(character, item, _ally()))
	return options[_rng.randi_range(0, options.size() - 1)]


## La experta: cura bajo el 45 %, ataja la causa y, contra la Sombra,
## combina las contramedidas que aún no ha aplicado.
func _expert_action(character: Character, target: Combatant) -> BattleAction:
	var ally := _ally()
	if ally != null and ally.get_hp_ratio() < 0.45:
		for skill in character.get_usable_skills():
			if skill is EcoSkill and (skill as EcoSkill).ally_healing > 0:
				return BattleAction.use_skill(character, skill, ally)
		for item in _manager.inventory.get_battle_items():
			if item is HealingItem and (item as HealingItem).heal_amount > 0:
				return BattleAction.use_item(character, item, ally)
	var monster := target as Monster
	if monster != null and not monster.is_purified:
		var offensive: Array[EcoSkill] = []
		for skill in character.get_usable_skills():
			if skill is EcoSkill and (skill as EcoSkill).ally_healing == 0:
				offensive.append(skill)
		if monster is AdaptiveBoss:
			for skill in offensive:
				if not (monster as AdaptiveBoss).used_eco_types.has(skill.weakness_type):
					return BattleAction.use_skill(character, skill, target)
		else:
			for skill in offensive:
				if skill.weakness_type == monster.required_counter_type:
					return BattleAction.use_skill(character, skill, target)
	return BattleAction.attack(character, target)


func _enemy() -> Combatant:
	for e in _manager.enemy_party:
		if e.is_alive():
			return e
	return null


func _ally() -> Combatant:
	var weakest: Combatant = null
	for m in _manager.player_party:
		if m.is_alive() and (weakest == null or m.get_hp_ratio() < weakest.get_hp_ratio()):
			weakest = m
	return weakest
