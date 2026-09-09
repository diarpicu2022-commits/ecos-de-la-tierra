class_name Monster
extends Combatant

## Clase base de los monstruos ambientales. Añade a Combatant las dos piezas que
## definen el combate del juego:
##
## 1. El sistema de debilidad ambiental. Mientras el monstruo no esté purificado
##    resiste el daño que no ataca la causa real y se regenera al quedarse sin
##    PV. Solo la EcoSkill cuyo `weakness_type` coincide con
##    `required_counter_type` lo purifica y permite derrotarlo.
## 2. La IA por pesos: en cada turno reparte probabilidad entre sus opciones
##    según los PV del grupo rival, los estados ya aplicados y el número de
##    turno, en vez de repetir siempre el mismo ataque.

signal purified()
signal regenerated(current_hp: int)

## Tipo de daño ambiental que encarna y, por tanto, la contramedida que lo vence.
@export var required_counter_type: Enums.EcoType = Enums.EcoType.FIRE
@export_multiline var lore: String = ""
## Reducción del daño recibido de tipos que no son su contramedida (0 a 1).
@export_range(0.0, 0.95) var wrong_type_resistance: float = 0.6
## Proporción de PV que recupera al regenerarse si aún no está purificado.
@export_range(0.05, 1.0) var regeneration_ratio: float = 0.3
## Recompensas al ser derrotado.
@export var experience_reward: int = 40
@export var knowledge_reward: int = 1

var is_purified: bool = false
var skills: Array[Skill] = []


func _ready() -> void:
	super._ready()
	team = Enums.Team.ENEMY


# --- Sistema de debilidad ambiental -----------------------------------------

## Resistencia frente a un tipo concreto. AdaptiveBoss la sobrescribe para que
## dependa de su tabla Q.
func get_resistance_for(eco_type: Enums.EcoType) -> float:
	if is_purified:
		return 0.0
	return 0.0 if eco_type == required_counter_type else wrong_type_resistance


func take_damage(amount: int, eco_type: Enums.EcoType = Enums.EcoType.NONE, ignore_defense: bool = false) -> int:
	var incoming: int = maxi(1, int(float(amount) * (1.0 - get_resistance_for(eco_type))))
	return super.take_damage(incoming, eco_type, ignore_defense)


## Quedarse sin PV solo derrota al monstruo si ya fue purificado. Si no, se
## regenera: es la traducción mecánica de "el daño ambiental vuelve mientras no
## se ataje su causa".
func _on_hp_depleted() -> void:
	if is_purified:
		super._on_hp_depleted()
		return
	hp = maxi(1, int(float(max_hp) * regeneration_ratio))
	hp_changed.emit(hp, max_hp)
	regenerated.emit(hp)


## Reacción a una Habilidad Ecológica. El BattleManager la invoca a través de
## EcoSkill.execute(); aquí se valida la contramedida sin lógica por monstruo.
func receive_eco_skill(skill: EcoSkill) -> Array[String]:
	var log_lines: Array[String] = []
	if is_purified:
		return log_lines
	if skill.weakness_type == required_counter_type:
		is_purified = true
		purified.emit()
		log_lines.append("¡%s deja de regenerarse! %s ataja la causa del daño." % [
			display_name, skill.display_name
		])
	else:
		log_lines.append("%s resiste: %s no corrige el daño que lo origina." % [
			display_name, skill.display_name
		])
	return log_lines


# --- IA por pesos -----------------------------------------------------------

## Decide la acción del turno. Se puede sobrescribir en las subclases, pero lo
## habitual es ajustar solo los pesos en _weight_for_skill().
func decide_action(context: BattleContext) -> BattleAction:
	var target: Combatant = _choose_target(context)
	if target == null:
		return BattleAction.flee(self)

	var candidates: Array[Dictionary] = []
	candidates.append({"skill": null, "weight": _weight_for_basic_attack(context)})
	for skill in skills:
		if skill.can_use(self):
			candidates.append({"skill": skill, "weight": _weight_for_skill(skill, context, target)})

	var chosen: Skill = _pick_weighted(candidates)
	if chosen == null:
		return BattleAction.attack(self, target)
	return BattleAction.use_skill(self, chosen, target)


## A quién ataca. Por defecto remata al más debilitado tres de cada cuatro
## veces, y el resto elige al azar para no volverse predecible.
func _choose_target(context: BattleContext) -> Combatant:
	if randf() < 0.75:
		return context.get_weakest(Enums.Team.PLAYER)
	return context.get_random(Enums.Team.PLAYER)


## Peso del ataque básico: sube cuando el grupo rival está muy tocado, porque
## rematar pesa más que seguir aplicando estados.
func _weight_for_basic_attack(context: BattleContext) -> float:
	var party_health: float = context.get_average_hp_ratio(Enums.Team.PLAYER)
	return 1.0 + (1.0 - party_health) * 2.0


## Peso de una habilidad concreta. Reglas por defecto:
##  - Si aplica un estado que el objetivo ya sufre, casi nunca se repite.
##  - En los primeros turnos se prefiere aplicar estados; más tarde, daño.
func _weight_for_skill(skill: Skill, context: BattleContext, target: Combatant) -> float:
	var weight: float = 1.5
	if skill is AttackSkill:
		var attack_skill: AttackSkill = skill as AttackSkill
		if not attack_skill.inflicted_statuses.is_empty():
			if _target_has_all_statuses(attack_skill, target):
				return 0.15
			weight += 1.0 if context.turn_number <= 3 else -0.5
	if context.get_average_hp_ratio(Enums.Team.PLAYER) < 0.3:
		weight += float(skill.power) * 0.02
	return maxf(0.05, weight)


## ¿El objetivo ya sufre todos los estados que aplicaría esta habilidad?
func _target_has_all_statuses(skill: AttackSkill, target: Combatant) -> bool:
	for template in skill.inflicted_statuses:
		if not target.has_status(template.status_type):
			return false
	return true


## Ruleta ponderada sobre las opciones. Devuelve null para el ataque básico.
func _pick_weighted(candidates: Array[Dictionary]) -> Skill:
	var total: float = 0.0
	for candidate in candidates:
		total += float(candidate["weight"])
	if total <= 0.0:
		return null

	var roll: float = randf() * total
	for candidate in candidates:
		roll -= float(candidate["weight"])
		if roll <= 0.0:
			return candidate["skill"] as Skill
	return null
