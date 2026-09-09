class_name EcoSkill
extends Skill

## Habilidad Ecológica: la contramedida real a un tipo de daño ambiental.
## Se aprende recolectando Conocimiento Ambiental, no subiendo de nivel.
##
## Aquí vive el sistema de debilidad ambiental: si `weakness_type` coincide con
## el tipo de daño que encarna el monstruo, el monstruo queda purificado y ya
## puede ser derrotado de forma definitiva. Si no coincide, hace daño reducido y
## el monstruo se sigue regenerando.

@export var weakness_type: Enums.EcoType = Enums.EcoType.FIRE
## Curación que reparte al bando propio (Reforestación, Filtro Biológico…).
@export var ally_healing: int = 0
## Estado alterado que retira del objetivo aliado (antídotos de Suri).
@export var cures_status: bool = false
@export var cured_status_type: Enums.StatusType = Enums.StatusType.POISON


func execute(user: Combatant, target: Combatant) -> Array[String]:
	var log_lines: Array[String] = []
	log_lines.append("%s aplica %s." % [user.display_name, display_name])

	# Uso sobre un aliado: curar o retirar un estado alterado.
	if target.team == user.team:
		if ally_healing > 0:
			var healed: int = target.heal(ally_healing)
			log_lines.append("%s recupera %d PV." % [target.display_name, healed])
		if cures_status and target.has_status(cured_status_type):
			log_lines.append(target.remove_status(cured_status_type))
		return log_lines

	# Uso sobre un monstruo: se comprueba la debilidad ambiental por duck typing
	# para no crear una dependencia cíclica entre EcoSkill y Monster.
	var monster = target   # sin tipo: la llamada se resuelve en ejecución
	if monster.has_method("receive_eco_skill"):
		log_lines.append_array(monster.receive_eco_skill(self))

	var damage: int = target.take_damage(calculate_damage(user), weakness_type)
	log_lines.append("%s pierde %d PV." % [target.display_name, damage])
	return log_lines
