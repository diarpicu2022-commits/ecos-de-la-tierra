class_name SlowEffect
extends StatusEffect

## Lentitud: reduce la velocidad y por tanto el orden de turnos.
## La aplican la Trampa Viscosa (Devorador de Petróleo) y el Frío Calcinante
## (Coloso del Deshielo).

func _init(turns: int = 3, speed_loss: float = 0.35) -> void:
	status_type = Enums.StatusType.SLOW
	display_name = "Lentitud"
	duration = turns
	potency = speed_loss


func modify_speed(value: int) -> int:
	return int(maxf(1.0, value * (1.0 - potency)))
