class_name StatusEffect
extends Resource

## Clase base de los estados alterados (veneno, aturdimiento, ceguera, marchitez,
## lentitud). Cada efecto vive un número de turnos y puede hacer tres cosas:
##   1. actuar al inicio del turno de quien lo sufre (on_turn_start),
##   2. modificar sus estadísticas mientras dura (modify_*),
##   3. impedirle actuar (blocks_action).
## Las subclases sobrescriben solo lo que necesitan.

@export var status_type: Enums.StatusType = Enums.StatusType.POISON
@export var display_name: String = "Estado"
@export var duration: int = 3          ## Turnos restantes.
@export var potency: float = 1.0       ## Intensidad; su significado lo define cada subclase.

## Combatiente que sufre el efecto. Lo asigna Combatant.apply_status().
## Se deja sin tipo a propósito: Combatant ya depende de StatusEffect, así que
## tiparlo aquí crearía una referencia cíclica entre ambas clases.
var target = null


## Se llama al aplicar el efecto. Devuelve el texto para el registro de batalla.
func on_applied(new_target) -> String:
	target = new_target
	return "%s sufre %s." % [new_target.display_name, display_name]


## Se llama al inicio del turno del portador, antes de que actúe.
## Devuelve el texto para el registro de batalla ("" si no hay nada que contar).
func on_turn_start() -> String:
	return ""


## Se llama al final del turno del portador. Consume un turno de duración.
func on_turn_end() -> void:
	duration -= 1


## Se llama al expirar o al curarse el efecto.
func on_removed() -> String:
	return "%s se recupera de %s." % [target.display_name, display_name]


func is_expired() -> bool:
	return duration <= 0


## ¿Impide actuar este turno? Solo el aturdimiento devuelve true.
func blocks_action() -> bool:
	return false


## Modificadores de estadísticas. Reciben el valor acumulado y devuelven el nuevo.
func modify_attack(value: int) -> int:
	return value


func modify_defense(value: int) -> int:
	return value


func modify_speed(value: int) -> int:
	return value


func modify_accuracy(value: float) -> float:
	return value
