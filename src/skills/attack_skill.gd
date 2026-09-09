class_name AttackSkill
extends Skill

## Ataque físico o elemental estándar. Hace daño y, opcionalmente, aplica un
## estado alterado. No purifica a ningún monstruo: por diseño, la fuerza bruta
## nunca cierra un combate.

## Estados alterados que aplica al impactar (vacío si no aplica ninguno).
## Es un array porque hay ataques que combinan dos, como la Sofocación por
## Humo, que ciega y además puede aturdir.
@export var inflicted_statuses: Array[StatusEffect] = []
@export_range(0.0, 1.0) var status_chance: float = 0.0
## Tipo del ataque. Sirve para las resistencias, no para purificar.
@export var eco_type: Enums.EcoType = Enums.EcoType.NONE


func execute(user: Combatant, target: Combatant) -> Array[String]:
	var log_lines: Array[String] = []
	if not rolls_hit(user):
		log_lines.append("%s usa %s… pero falla." % [user.display_name, display_name])
		return log_lines

	var damage: int = target.take_damage(calculate_damage(user), eco_type)
	log_lines.append("%s usa %s. %s pierde %d PV." % [
		user.display_name, display_name, target.display_name, damage
	])

	if not inflicted_statuses.is_empty() and randf() <= status_chance and target.is_alive():
		for template in inflicted_statuses:
			# Se duplica el recurso para que cada víctima tenga su propia
			# instancia con su propia duración.
			var effect: StatusEffect = template.duplicate() as StatusEffect
			log_lines.append(target.apply_status(effect))

	return log_lines
