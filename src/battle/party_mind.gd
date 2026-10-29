class_name PartyMind
extends RefCounted

## IA-5 · La mente de un compañero (contrato «Orden de líder»,
## docs/ux/anexos/2026-10-28-encuentros.md). Un perceptrón pequeño en GDScript
## puro, sin librerías: 12 entradas, 16 neuronas ocultas (tanh) y 4 salidas
## (softmax) —atacar, contramedida, curar, objeto—.
##
## Aprende de Ilan: tras cada decisión del líder, un paso de descenso por
## gradiente con el par «situación → lo que hizo». La orden de grupo sesga la
## salida, y la sintonía decide cuánto acierta el compañero al seguirla.
##
## La sintonía y su juicio son estáticos: son del grupo, no de un compañero.

enum Choice { ATTACK, COUNTER, HEAL, ITEM }
enum Order { FOLLOW, CAUSE, COVER }

## Umbral de «alguien está tocado», el mismo de la política experta (IA-4).
const HURT := 0.45

var w1: Array = []   ## [PARTY_HIDDEN][PARTY_INPUTS]
var b1: Array = []
var w2: Array = []   ## [PARTY_OUTPUTS][PARTY_HIDDEN]
var b2: Array = []


func _init(seed_value: int = 1) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var scale := 1.0 / sqrt(DesignTokens.PARTY_INPUTS)
	for h in DesignTokens.PARTY_HIDDEN:
		var row := []
		for i in DesignTokens.PARTY_INPUTS:
			row.append(rng.randf_range(-scale, scale))
		w1.append(row)
		b1.append(0.0)
	scale = 1.0 / sqrt(DesignTokens.PARTY_HIDDEN)
	for o in DesignTokens.PARTY_OUTPUTS:
		var row := []
		for h in DesignTokens.PARTY_HIDDEN:
			row.append(rng.randf_range(-scale, scale))
		w2.append(row)
		b2.append(0.0)


func _hidden(x: PackedFloat32Array) -> Array:
	var out := []
	for h in DesignTokens.PARTY_HIDDEN:
		var s: float = b1[h]
		for i in DesignTokens.PARTY_INPUTS:
			s += w1[h][i] * x[i]
		out.append(tanh(s))
	return out


func logits(x: PackedFloat32Array) -> Array:
	var hid := _hidden(x)
	var out := []
	for o in DesignTokens.PARTY_OUTPUTS:
		var s: float = b2[o]
		for h in DesignTokens.PARTY_HIDDEN:
			s += w2[o][h] * hid[h]
		out.append(s)
	return out


static func softmax(z: Array) -> Array:
	var top: float = z.max()
	var e := []
	var total := 0.0
	for v in z:
		e.append(exp(v - top))
		total += e[-1]
	return e.map(func(v): return v / total)


## Un paso de descenso por gradiente con entropía cruzada hacia `target`.
func train(x: PackedFloat32Array, target: int) -> void:
	var lr := DesignTokens.PARTY_LEARNING_RATE
	var hid := _hidden(x)
	var p := softmax(logits(x))
	var d2 := []
	for o in DesignTokens.PARTY_OUTPUTS:
		d2.append(p[o] - (1.0 if o == target else 0.0))
	var d1 := []
	for h in DesignTokens.PARTY_HIDDEN:
		var s := 0.0
		for o in DesignTokens.PARTY_OUTPUTS:
			s += w2[o][h] * d2[o]
		d1.append(s * (1.0 - hid[h] * hid[h]))
	for o in DesignTokens.PARTY_OUTPUTS:
		for h in DesignTokens.PARTY_HIDDEN:
			w2[o][h] -= lr * d2[o] * hid[h]
		b2[o] -= lr * d2[o]
	for h in DesignTokens.PARTY_HIDDEN:
		for i in DesignTokens.PARTY_INPUTS:
			w1[h][i] -= lr * d1[h] * x[i]
		b1[h] -= lr * d1[h]


## Lo que la red elegiría con la orden `order`, entre lo posible (`allowed`,
## uno por salida).
func preferred(x: PackedFloat32Array, order: Order, allowed: Array) -> int:
	var z := logits(x)
	match order:
		Order.CAUSE:
			z[Choice.COUNTER] += DesignTokens.ORDER_BIAS
		Order.COVER:
			z[Choice.HEAL] += DesignTokens.ORDER_BIAS
			z[Choice.ITEM] += DesignTokens.ORDER_BIAS
	var best := -1
	for o in DesignTokens.PARTY_OUTPUTS:
		if allowed[o] and (best < 0 or z[o] > z[best]):
			best = o
	return maxi(best, Choice.ATTACK)


## Decide con la sintonía: sigue su red con probabilidad 0,5 + 0,5 × sync; si
## no, duda y elige al azar entre lo posible. Devuelve {choice, doubted}.
func choose(x: PackedFloat32Array, order: Order, sync: float, allowed: Array,
		rng: RandomNumberGenerator) -> Dictionary:
	if rng.randf() < 0.5 + 0.5 * sync:
		return {"choice": preferred(x, order, allowed), "doubted": false}
	var options := []
	for o in DesignTokens.PARTY_OUTPUTS:
		if allowed[o]:
			options.append(o)
	return {"choice": options[rng.randi_range(0, options.size() - 1)], "doubted": true}


## Las 12 entradas, todas entre 0 y 1.
static func features(actor: Combatant, party: Array, monster: Combatant, round_number: int,
		can_counter: bool, can_heal: bool, has_item: bool, last_choice: int) -> PackedFloat32Array:
	var alive := party.filter(func(c): return c.is_alive())
	var avg := 0.0
	var low := 1.0
	for c in alive:
		avg += c.get_hp_ratio()
		low = minf(low, c.get_hp_ratio())
	avg = avg / maxf(alive.size(), 1)
	var cause := 1.0 if monster is Monster and not (monster as Monster).is_purified else 0.0
	return PackedFloat32Array([
		actor.get_hp_ratio(),
		float(actor.energy) / maxf(actor.max_energy, 1),
		avg,
		low,
		monster.get_hp_ratio() if monster != null else 0.0,
		cause,
		1.0 if can_counter else 0.0,
		1.0 if can_heal else 0.0,
		1.0 if has_item else 0.0,
		clampf(round_number / 10.0, 0.0, 1.0),
		1.0 if last_choice == Choice.COUNTER else 0.0,
		1.0 if last_choice == Choice.HEAL or last_choice == Choice.ITEM else 0.0,
	])


## Juicio de la decisión del líder (contrato §5): +1 buena, -1 mala, 0 neutra.
## `repeated`: contra la Sombra, el tipo ya estaba usado.
static func judge(choice: int, cause_active: bool, could_counter: bool, lowest_hp: float,
		repeated: bool) -> int:
	if choice == Choice.COUNTER:
		return -1 if repeated else (1 if cause_active else 0)
	if choice == Choice.HEAL or choice == Choice.ITEM:
		return 1 if lowest_hp < HURT else -1
	if cause_active and could_counter:
		return -1
	return 0


## Juicio de la orden de grupo (enmienda 1 del contrato «Orden de líder»,
## Diego 2026-10-28): mandar también es decidir. +1, -1 o 0.
## - Atajad: buena con la causa activa y alguien del grupo que puede atajarla.
## - Cubríos: buena si alguien baja del 45 %; mala si nadie está tocado.
## - Seguidme: mala si el grupo podía atajar la causa y el líder no lo hace.
static func judge_order(order: int, cause_active: bool, party_can_counter: bool,
		lowest_hp: float, leader_choice: int) -> int:
	match order:
		Order.CAUSE:
			return 1 if cause_active and party_can_counter else 0
		Order.COVER:
			return 1 if lowest_hp < HURT else -1
	if cause_active and party_can_counter and leader_choice != Choice.COUNTER:
		return -1
	return 0


## Sintonía tras un juicio. Sube hacia 1 más deprisa de lo que baja hacia 0.
static func update_sync(sync: float, verdict: int) -> float:
	if verdict > 0:
		return sync + DesignTokens.SYNC_UP * (1.0 - sync)
	if verdict < 0:
		return sync - DesignTokens.SYNC_DOWN * sync
	return sync


## Pesos iniciales aprendidos por IA-4 de la política experta
## (`tools/balance_bot.gd`). Sin el archivo, pesos al azar con semilla.
const INIT_PATH := "res://data/balance/party_init.json"


## Una mente nueva: parte de los pesos de IA-4 si existen.
static func initial(seed_value: int) -> PartyMind:
	var mind := PartyMind.new(seed_value)
	if FileAccess.file_exists(INIT_PATH):
		var data = JSON.parse_string(FileAccess.get_file_as_string(INIT_PATH))
		if data is Dictionary and data.has("weights"):
			mind.load_dict((data["weights"] as Dictionary).duplicate(true))
	return mind


func to_dict() -> Dictionary:
	return {"w1": w1, "b1": b1, "w2": w2, "b2": b2}


func load_dict(d: Dictionary) -> void:
	w1 = d["w1"]
	b1 = d["b1"]
	w2 = d["w2"]
	b2 = d["b2"]
