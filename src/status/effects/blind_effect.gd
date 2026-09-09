class_name BlindEffect
extends StatusEffect

## Ceguera: reduce la precisión del portador.
## La aplican las Micropartículas del Gólem de Plástico.

func _init(turns: int = 3, accuracy_loss: float = 0.35) -> void:
	status_type = Enums.StatusType.BLIND
	display_name = "Ceguera"
	duration = turns
	potency = accuracy_loss


func modify_accuracy(value: float) -> float:
	return maxf(0.15, value - potency)
