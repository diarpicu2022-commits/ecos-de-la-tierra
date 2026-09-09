class_name WitherEffect
extends StatusEffect

## Marchitez: reduce la defensa del portador.
## La aplica el Espectro del Monocultivo a todo el equipo.

func _init(turns: int = 3, defense_loss: float = 0.4) -> void:
	status_type = Enums.StatusType.WITHER
	display_name = "Marchitez"
	duration = turns
	potency = defense_loss


func modify_defense(value: int) -> int:
	return int(maxf(0.0, value * (1.0 - potency)))
