class_name HealingItem
extends Item

## Consumible de curación: restaura PV, energía o ambos, y opcionalmente retira
## un estado alterado (los antídotos de Suri).

@export var heal_amount: int = 30
@export var energy_amount: int = 0
@export var cures_status: bool = false
@export var cured_status_type: Enums.StatusType = Enums.StatusType.POISON


func use(user: Combatant, target: Combatant) -> Array[String]:
	var log_lines: Array[String] = []
	log_lines.append("%s usa %s en %s." % [user.display_name, display_name, target.display_name])

	if heal_amount > 0:
		var healed: int = target.heal(heal_amount)
		log_lines.append("%s recupera %d PV." % [target.display_name, healed])
	if energy_amount > 0:
		target.restore_energy(energy_amount)
		log_lines.append("%s recupera %d de energía." % [target.display_name, energy_amount])
	if cures_status and target.has_status(cured_status_type):
		log_lines.append(target.remove_status(cured_status_type))

	return log_lines
