class_name BattleContext
extends RefCounted

## Fotografía del estado del combate en un momento dado. Se le pasa a la IA de
## los monstruos para que decida sin necesidad de conocer al BattleManager.

var player_party: Array[Combatant] = []
var enemy_party: Array[Combatant] = []
var turn_number: int = 1


func _init(players: Array[Combatant] = [], enemies: Array[Combatant] = [], turn: int = 1) -> void:
	player_party = players
	enemy_party = enemies
	turn_number = turn


## Miembros vivos de un bando.
func get_living(team: Enums.Team) -> Array[Combatant]:
	var source: Array[Combatant] = player_party if team == Enums.Team.PLAYER else enemy_party
	var living: Array[Combatant] = []
	for combatant in source:
		if combatant.is_alive():
			living.append(combatant)
	return living


## Objetivo con menos PV proporcionales de un bando (null si no queda ninguno).
func get_weakest(team: Enums.Team) -> Combatant:
	var candidates: Array[Combatant] = get_living(team)
	if candidates.is_empty():
		return null
	var weakest: Combatant = candidates[0]
	for combatant in candidates:
		if combatant.get_hp_ratio() < weakest.get_hp_ratio():
			weakest = combatant
	return weakest


## Objetivo al azar de un bando (null si no queda ninguno).
func get_random(team: Enums.Team) -> Combatant:
	var candidates: Array[Combatant] = get_living(team)
	if candidates.is_empty():
		return null
	return candidates[randi() % candidates.size()]


## PV medios del bando, en proporción de 0 a 1. La IA lo usa para decidir si
## conviene rematar o seguir desgastando.
func get_average_hp_ratio(team: Enums.Team) -> float:
	var candidates: Array[Combatant] = get_living(team)
	if candidates.is_empty():
		return 0.0
	var total: float = 0.0
	for combatant in candidates:
		total += combatant.get_hp_ratio()
	return total / float(candidates.size())
