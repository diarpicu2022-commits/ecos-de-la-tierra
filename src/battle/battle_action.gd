class_name BattleAction
extends RefCounted

## Una acción concreta elegida en un turno: qué hace el combatiente, con qué y
## sobre quién. Es lo que devuelve la IA de los monstruos y lo que envía la
## interfaz cuando el jugador elige una opción del menú de batalla.

var actor: Combatant = null
var type: Enums.ActionType = Enums.ActionType.ATTACK
var skill: Skill = null
var item: Item = null
var target: Combatant = null


func _init(action_actor: Combatant = null, action_type: Enums.ActionType = Enums.ActionType.ATTACK, action_target: Combatant = null) -> void:
	actor = action_actor
	type = action_type
	target = action_target


static func attack(actor: Combatant, target: Combatant) -> BattleAction:
	return BattleAction.new(actor, Enums.ActionType.ATTACK, target)


static func use_skill(actor: Combatant, skill: Skill, target: Combatant) -> BattleAction:
	var action := BattleAction.new(actor, Enums.ActionType.SKILL, target)
	action.skill = skill
	return action


static func use_item(actor: Combatant, item: Item, target: Combatant) -> BattleAction:
	var action := BattleAction.new(actor, Enums.ActionType.ITEM, target)
	action.item = item
	return action


static func flee(actor: Combatant) -> BattleAction:
	return BattleAction.new(actor, Enums.ActionType.FLEE, null)
