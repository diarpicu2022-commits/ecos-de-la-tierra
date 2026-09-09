class_name MonocultureSpecter
extends Monster

## Llanura Marchita — agroquímicos y monocultivo intensivo.
## Se vence con la Rotación de Cultivos: variar la especie y devolver nutrientes.
##
## Su Multiplicación genera clones, la traducción mecánica de repetir siempre el
## mismo cultivo: son enemigos débiles pero constantes que obligan a gastar
## turnos. El BattleManager escucha `clone_requested` y los añade al combate.

signal clone_requested(clone: Monster)

## Copias simultáneas que puede llegar a tener sobre el campo.
@export var max_clones: int = 2

## Un clon no puede a su vez multiplicarse: si no, el combate no termina nunca.
var is_clone: bool = false

var _clones_spawned: int = 0


func _init() -> void:
	display_name = "Espectro del Monocultivo"
	lore = "Lo que queda de una llanura sembrada mil veces con la misma semilla."
	max_hp = 200
	max_energy = 40
	base_attack = 14
	base_defense = 10
	base_speed = 11
	required_counter_type = Enums.EcoType.MONOCULTURE
	wrong_type_resistance = 0.6
	regeneration_ratio = 0.35
	experience_reward = 100
	skills = [SkillLibrary.withering(), SkillLibrary.multiplication()]


## Lo consulta SummonSkill antes de dejar usar la Multiplicación.
func can_summon() -> bool:
	return not is_clone and _clones_spawned < max_clones


## Crea la copia y avisa al BattleManager. Devuelve el registro de batalla.
func summon_clone() -> Array[String]:
	var clone := MonocultureSpecter.new()
	clone.is_clone = true
	clone.display_name = "Eco del Monocultivo"
	clone.max_hp = int(float(max_hp) * 0.35)
	clone.base_attack = int(float(base_attack) * 0.6)
	clone.base_defense = int(float(base_defense) * 0.5)
	clone.base_speed = base_speed
	clone.experience_reward = 0
	clone.knowledge_reward = 0
	# El clon comparte la debilidad del original, pero solo sabe marchitar.
	clone.skills = [SkillLibrary.withering()]

	_clones_spawned += 1
	clone_requested.emit(clone)
	return ["%s se multiplica: aparece un %s." % [display_name, clone.display_name]]
