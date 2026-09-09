class_name PoisonEffect
extends StatusEffect

## Veneno: daño fijo al inicio de cada turno del portador.
## Lo aplican la Marea Negra del Devorador de Petróleo y los venenos de Suri.

func _init(turns: int = 3, damage_per_turn: float = 6.0) -> void:
	status_type = Enums.StatusType.POISON
	display_name = "Veneno"
	duration = turns
	potency = damage_per_turn


func on_turn_start() -> String:
	var damage: int = int(potency)
	target.take_damage(damage, Enums.EcoType.OIL, true)
	return "%s pierde %d PV por el veneno." % [target.display_name, damage]
