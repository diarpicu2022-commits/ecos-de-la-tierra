class_name StunEffect
extends StatusEffect

## Aturdimiento: el portador pierde su turno mientras dure.
## Lo aplica la Sofocación por Humo de la Llama de la Deforestación.

func _init(turns: int = 1) -> void:
	status_type = Enums.StatusType.STUN
	display_name = "Aturdimiento"
	duration = turns
	potency = 1.0


func blocks_action() -> bool:
	return true


func on_turn_start() -> String:
	return "%s está aturdido y no puede actuar." % target.display_name
