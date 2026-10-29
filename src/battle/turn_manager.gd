class_name TurnManager
extends RefCounted

## Lleva el orden de turnos de una ronda. Se separa del BattleManager para que
## este se ocupe solo del flujo del combate y las reglas, y el orden pueda
## probarse de forma aislada.
##
## El orden se recalcula cada ronda con la velocidad efectiva del momento, así
## que los estados de lentitud cambian de verdad quién actúa antes.

var round_number: int = 0

var _queue: Array[Combatant] = []


## Abre una ronda nueva con los combatientes que sigan en pie.
func start_round(participants: Array[Combatant]) -> void:
	round_number += 1
	_queue.clear()
	for combatant in participants:
		if combatant.is_alive():
			_queue.append(combatant)
	_sort_by_speed(_queue)


func has_next() -> bool:
	return not _queue.is_empty()


## Devuelve el siguiente combatiente vivo, o null si la ronda terminó.
func next_combatant() -> Combatant:
	while not _queue.is_empty():
		var combatant: Combatant = _queue.pop_front()
		if combatant.is_alive():
			return combatant
	return null


## Saca a alguien de la ronda (por ejemplo, al caer derrotado).
func remove(combatant: Combatant) -> void:
	_queue.erase(combatant)


## Mete a un recién llegado en la ronda en curso, en su lugar por velocidad.
## Lo usan los clones del Espectro del Monocultivo.
func insert(combatant: Combatant) -> void:
	_queue.append(combatant)
	_sort_by_speed(_queue)


## Turnos que quedan por jugarse en la ronda actual.
func get_pending() -> Array[Combatant]:
	return _queue.duplicate()


## Adelanta a todo el equipo `team` en la ronda en curso, sin romper su orden
## por velocidad. Es la ventaja del contacto (contrato «Persiana» §2): quien
## toca por la espalda abre la primera ronda.
func prioritize(team: Enums.Team) -> void:
	var first: Array[Combatant] = []
	var rest: Array[Combatant] = []
	for combatant in _queue:
		(first if combatant.team == team else rest).append(combatant)
	_queue = first + rest


## Más rápido primero; a igualdad de velocidad, el desempate es al azar para que
## los turnos no queden fijados por el orden de creación.
func _sort_by_speed(queue: Array[Combatant]) -> void:
	queue.shuffle()
	queue.sort_custom(func(a: Combatant, b: Combatant) -> bool:
		return a.get_speed() > b.get_speed()
	)
