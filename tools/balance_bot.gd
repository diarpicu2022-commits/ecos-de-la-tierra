extends Node

## IA-4 · Bot de equilibrado (guía §3.3). Solo desarrollo, sin ventana:
##
##   godot --headless --path . res://tools/balance_bot.tscn             (medir)
##   godot --headless --path . res://tools/balance_bot.tscn -- --sweep  (barrido)
##
## Juega en el modo de IA-5, «Orden de líder»: el bot solo decide por Ilan y la
## orden de grupo; los compañeros deciden con su `PartyMind`. Políticas, con
## semilla fija:
##
## - **aleatoria:** acción de Ilan y orden al azar;
## - **voraz** (fuerza bruta): Ilan solo ataca y manda «Seguidme». En el modo
##   líder, repetir su contramedida no es jugar mal: el grupo aprende «atajar»
##   y cada uno usa su propio tipo. El mal líder equivalente es el que no ataja
##   nunca (cambio de criterio, 2026-10-28, se le lleva a Diego);
## - **experta:** cura a quien baja del 45 %, usa su contramedida si sirve, y
##   manda «Cubríos», «Atajad» o «Seguidme» según haga falta.
##
## Criterios («ajuste y criterio real», Diego 2026-10-28):
## 1. la experta gana siempre;
## 2. la fuerza bruta gana como mucho BRUTE_MAX;
## 3. la aleatoria gana menos que la experta.
## La Costa queda fuera del 2 como deuda escrita: su Gólem no presiona (ver
## anexo), y se mide igual.
##
## Antes de medir, entrena los **pesos iniciales** de las mentes (IA-5) con
## las decisiones de la experta jugando a los cinco, y los guarda en
## `data/balance/party_init.json`. Escribe un CSV por región en
## `docs/balance/` y la tabla Q de la Sombra en `data/balance/sombra_q.json`.
##
## Con `--sweep` no escribe nada: prueba multiplicadores del ataque del
## monstruo por región e imprime el menor que cumple los criterios.
## Sale con código 1 si un criterio falla.

const COMBATS := 200
const SEED := 20261028
const MAX_ROUNDS := 30
const BRUTE_MAX := 0.30
## Regiones fuera del criterio 2, con su motivo en el anexo.
const BRUTE_EXEMPT := [2]
const RANDOM_MAX := 0.30
const DATE := "2026-10-28"
const POLICIES := ["aleatoria", "voraz", "experta"]
const SLUG := ["bosque", "cuenca", "costa", "llanura", "cumbre", "cripta"]
const SWEEP := [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
const INIT_SAMPLES_PER_REGION := 60
const INIT_EPOCHS := 6

var _manager: BattleManager = null
var _policy := ""
var _rng := RandomNumberGenerator.new()
var _used := {}
var _fails := 0
var _samples: Array = []


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/balance"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://data/balance"))
	_train_initial_minds()
	if "--sweep" in OS.get_cmdline_user_args():
		_sweep()
		get_tree().quit()
		return
	_measure()
	print("\n%s" % ("Todo en verde." if _fails == 0 else "%d criterios fallan." % _fails))
	get_tree().quit(1 if _fails else 0)


func _check(label: String, ok: bool) -> void:
	_fails += 0 if ok else 1
	print("  %s %s" % ["OK   " if ok else "FALLA", label])


# --- Pesos iniciales de IA-5 ------------------------------------------------

## La experta juega a los cinco (sin compañeros automáticos) y cada decisión
## suya es un ejemplo «situación → acción». Una mente aprende de todos.
func _train_initial_minds() -> void:
	_samples.clear()
	_policy = "maestra"
	_rng.seed = SEED
	for index in Encounters.count():
		for n in INIT_SAMPLES_PER_REGION:
			_play(index, {}, 1.0, false)
	var mind := PartyMind.new(SEED)
	var order := range(_samples.size())
	for epoch in INIT_EPOCHS:
		order.shuffle()
		for i in order:
			mind.train(_samples[i][0], _samples[i][1])
	var hits := 0
	var all := [true, true, true, true]
	for s in _samples:
		hits += int(mind.preferred(s[0], PartyMind.Order.FOLLOW, all) == s[1])
	var out := FileAccess.open(PartyMind.INIT_PATH, FileAccess.WRITE)
	out.store_string(JSON.stringify({"_doc": "Pesos iniciales de PartyMind (IA-5), aprendidos por tools/balance_bot.gd (IA-4) de la política experta.",
		"seed": SEED, "samples": _samples.size(), "accuracy": float(hits) / _samples.size(),
		"weights": mind.to_dict()}) + "\n")
	out.close()
	print("Pesos iniciales: %d ejemplos de la experta, %d %% de acierto sobre ellos" % [
		_samples.size(), roundi(100.0 * hits / _samples.size())])


# --- Medir y barrer ---------------------------------------------------------

func _measure() -> void:
	var trained := {}
	for index in Encounters.count():
		var rows := PackedStringArray(["politica,combate,resultado,rondas,sintonia,habilidades"])
		var wins := {}
		print("\n%s (%s)" % [Encounters.get_encounter(index)["region"], SLUG[index]])
		for policy in POLICIES:
			var res := _series(index, policy, 1.0, trained if index == 5 else {})
			wins[policy] = res["wins"]
			if index == 5:
				trained = res["q"]
			rows.append_array(res["rows"])
			print("  %-9s gana %3d de %d · %.1f rondas · sintonía final %.2f" % [policy, res["wins"], COMBATS,
				res["rounds"], res["sync"]])
		var file := FileAccess.open("res://docs/balance/%s-%s.csv" % [DATE, SLUG[index]], FileAccess.WRITE)
		file.store_string("\n".join(rows) + "\n")
		file.close()
		_check("la experta gana siempre (%d de %d)" % [wins["experta"], COMBATS], wins["experta"] == COMBATS)
		if index in BRUTE_EXEMPT:
			print("  DEUDA la fuerza bruta gana %d de %d (región fuera del criterio, ver anexo)" % [wins["voraz"], COMBATS])
		else:
			_check("la fuerza bruta gana como mucho el %d %% (%d de %d)" % [roundi(BRUTE_MAX * 100), wins["voraz"], COMBATS],
				float(wins["voraz"]) / COMBATS <= BRUTE_MAX)
		if index in BRUTE_EXEMPT:
			print("  DEUDA la aleatoria gana %d frente a %d de la experta" % [wins["aleatoria"], wins["experta"]])
		else:
			_check("la aleatoria gana menos que la experta (%d frente a %d)" % [wins["aleatoria"], wins["experta"]],
				wins["aleatoria"] < wins["experta"])
	var q := {}
	for k in trained:
		q[str(k)] = trained[k]
	var out := FileAccess.open("res://data/balance/sombra_q.json", FileAccess.WRITE)
	out.store_string(JSON.stringify({"_doc": "Tabla Q de la Sombra entrenada por tools/balance_bot.gd (IA-4). Clave: Enums.EcoType.", "seed": SEED, "q": q}, "\t") + "\n")
	out.close()


func _sweep() -> void:
	# `-- --sweep --only=1,2`: solo esas regiones (índices de Encounters).
	var only := []
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = Array(arg.substr(7).split(",")).map(func(v): return int(v))
	for index in Encounters.count():
		if not only.is_empty() and index not in only:
			continue
		var found := -1.0
		var line := PackedStringArray()
		for mult in SWEEP:
			var r := _series(index, "aleatoria", mult, {})
			var g := _series(index, "voraz", mult, {})
			var e := _series(index, "experta", mult, {})
			line.append("x%.2f: %d/%d/%d" % [mult, r["wins"], g["wins"], e["wins"]])
			if float(r["wins"]) / COMBATS <= RANDOM_MAX and e["wins"] == COMBATS and found < 0:
				found = mult
		print("%s: %s → %s" % [SLUG[index], " · ".join(line),
			"x%.2f" % found if found > 0 else "ninguno cumple"])


func _series(index: int, policy: String, mult: float, q: Dictionary) -> Dictionary:
	_policy = policy
	_rng.seed = SEED + index * 10 + POLICIES.find(policy)
	seed(_rng.seed)
	var wins := 0
	var rounds := 0
	var sync := 0.0
	var rows := PackedStringArray()
	for n in COMBATS:
		var out := _play(index, q, mult, true)
		if index == 5 and policy != "aleatoria":
			q = out["q"]
		wins += int(out["result"] == Enums.BattleResult.VICTORY)
		rounds += out["rounds"]
		sync += out["sync"]
		rows.append("%s,%d,%s,%d,%.2f,%s" % [policy, n, ["en curso", "victoria", "derrota", "huida"][out["result"]],
			out["rounds"], out["sync"], " ".join(out["skills"])])
	return {"wins": wins, "rounds": float(rounds) / COMBATS, "sync": sync / COMBATS, "rows": rows, "q": q}


## Un combate entero, con el ataque del monstruo por `mult`.
func _play(index: int, q: Dictionary, mult: float, leader_mode: bool) -> Dictionary:
	var holder := Node.new()
	add_child(holder)
	var players: Array[Combatant] = []
	for c in Encounters.build_party(index):
		holder.add_child(c)
		players.append(c)
	var monster := Encounters.build_monster(index)
	monster.base_attack = roundi(monster.base_attack * mult)
	holder.add_child(monster)
	if monster is AdaptiveBoss and not q.is_empty():
		(monster as AdaptiveBoss).load_q_table(q)
	var enemies: Array[Combatant] = [monster]
	_used = {}
	_manager = BattleManager.new()
	_manager.companions_auto = leader_mode
	holder.add_child(_manager)
	_manager.player_input_required.connect(_decide)
	_manager.start_battle(players, enemies, Encounters.build_inventory(index))
	var skills := PackedStringArray()
	for k in _used:
		skills.append("%s:%d" % [k, _used[k]])
	var out := {"result": _manager.result, "rounds": _manager._turn_manager.round_number,
		"sync": _manager.sync, "skills": skills,
		"q": (monster as AdaptiveBoss).q_table.duplicate() if monster is AdaptiveBoss else {}}
	holder.free()
	return out


# --- Políticas --------------------------------------------------------------

func _decide(character: Character) -> void:
	if _manager._turn_manager.round_number > MAX_ROUNDS:
		_submit(BattleAction.flee(character))
		return
	var target := _manager._monster()
	match _policy:
		"aleatoria":
			_manager.order = _rng.randi_range(0, 2)
			_submit(_random_action(character, target))
		"voraz":
			_manager.order = PartyMind.Order.FOLLOW
			_submit(BattleAction.attack(character, target))
		"experta", "maestra":
			var action := _expert_action(character, target)
			if _policy == "maestra":
				_samples.append([_manager._situation(character), BattleManager.choice_of(action)])
			_submit(action)


func _submit(action: BattleAction) -> void:
	if action.type == Enums.ActionType.SKILL:
		_used[action.skill.display_name] = _used.get(action.skill.display_name, 0) + 1
	_manager.submit_action(action)


func _random_action(character: Character, target: Combatant) -> BattleAction:
	var options: Array[BattleAction] = [BattleAction.attack(character, target)]
	for skill in character.get_usable_skills():
		var healing := skill is EcoSkill and (skill as EcoSkill).ally_healing > 0
		options.append(BattleAction.use_skill(character, skill, _manager._weakest() if healing else target))
	for item in _manager.inventory.get_battle_items():
		options.append(BattleAction.use_item(character, item, _manager._weakest()))
	return options[_rng.randi_range(0, options.size() - 1)]


## La experta: cura bajo el 45 %, usa su contramedida si sirve (contra la
## Sombra, un tipo nuevo) y elige la orden que pide el momento.
func _expert_action(character: Character, target: Combatant) -> BattleAction:
	var weakest := _manager._weakest()
	var hurt := weakest != null and weakest.get_hp_ratio() < PartyMind.HURT
	var monster := target as Monster
	var cause := monster != null and not monster.is_purified
	var party_can := false
	for c in _manager.player_party:
		if c != character and c.is_alive() and _fresh(_manager._counter_skill(c), monster):
			party_can = true
	if hurt:
		_manager.order = PartyMind.Order.COVER
	elif cause and party_can:
		_manager.order = PartyMind.Order.CAUSE
	else:
		_manager.order = PartyMind.Order.FOLLOW
	if hurt:
		var heal := _manager._heal_skill(character)
		if heal != null:
			return BattleAction.use_skill(character, heal, weakest)
		var item := _manager._heal_item()
		if item != null:
			return BattleAction.use_item(character, item, weakest)
	var counter := _manager._counter_skill(character)
	if cause and _fresh(counter, monster):
		return BattleAction.use_skill(character, counter, target)
	return BattleAction.attack(character, target)


## La contramedida sirve: existe y, contra la Sombra, es de un tipo sin usar.
func _fresh(skill: EcoSkill, monster: Monster) -> bool:
	return skill != null and not (monster is AdaptiveBoss
		and (monster as AdaptiveBoss).used_eco_types.has(skill.weakness_type))
