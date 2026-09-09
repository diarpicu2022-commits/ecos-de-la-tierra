class_name Skill
extends Resource

## Clase base de todo lo que un combatiente puede ejecutar en su turno.
## Se hereda en dos direcciones: AttackSkill (daño directo, con o sin estado
## alterado) y EcoSkill (Habilidades Ecológicas, las únicas que purifican).

@export var display_name: String = "Habilidad"
@export_multiline var description: String = ""
@export var energy_cost: int = 0
@export var power: int = 10
@export var accuracy: float = 1.0
@export var targets_all: bool = false   ## true = alcanza a todo el bando rival.


## ¿Tiene el usuario energía suficiente para lanzarla?
func can_use(user: Combatant) -> bool:
	return user.has_energy(energy_cost)


## Ejecuta la habilidad y devuelve las líneas del registro de batalla.
## El BattleManager ya descontó la energía antes de llamar aquí.
func execute(user: Combatant, target: Combatant) -> Array[String]:
	push_warning("Skill.execute() debe sobrescribirse en la subclase.")
	return []


## Cálculo de daño compartido: potencia escalada por el ataque del usuario.
## La defensa del objetivo se resta después, dentro de Combatant.take_damage().
func calculate_damage(user: Combatant) -> int:
	var raw: float = float(power) + float(user.get_attack()) * 0.6
	var variance: float = randf_range(0.9, 1.1)   # pequeña variación por golpe
	return maxi(1, int(raw * variance))


## Tirada de acierto: precisión de la habilidad por la del usuario (la ceguera
## entra por aquí).
func rolls_hit(user: Combatant) -> bool:
	return randf() <= accuracy * user.get_accuracy()
