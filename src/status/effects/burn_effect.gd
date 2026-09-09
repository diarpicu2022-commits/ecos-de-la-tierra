class_name BurnEffect
extends StatusEffect

## Quemadura: daño progresivo de tipo fuego al inicio de cada turno.
## La aplica la Onda de Calor de la Llama de la Deforestación.
## Se separa del veneno porque los antídotos de Suri no deben apagar un incendio.

func _init(turns: int = 3, damage_per_turn: float = 7.0) -> void:
	status_type = Enums.StatusType.BURN
	display_name = "Quemadura"
	duration = turns
	potency = damage_per_turn


func on_turn_start() -> String:
	var damage: int = int(potency)
	target.take_damage(damage, Enums.EcoType.FIRE, true)
	return "%s pierde %d PV por la quemadura." % [target.display_name, damage]
