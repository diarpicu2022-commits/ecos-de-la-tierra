class_name AdaptiveBoss
extends Monster

## Sombra de la Avaricia — jefe final, en la Cripta de la Avaricia.
##
## Es el módulo de aprendizaje por refuerzo del proyecto. Mantiene una tabla Q
## (Dictionary: Enums.EcoType -> peso de resistencia) que se actualiza tras cada
## Habilidad Ecológica que recibe: la que el jugador repite le hace cada vez
## menos, y las que no usa vuelven poco a poco a ser efectivas.
##
## Además no se purifica con una sola contramedida: exige haber aplicado varias
## distintas. Es el mensaje del juego dentro de la propia mecánica —ninguna
## solución ambiental aislada revierte el daño acumulado—.
##
## La tabla se puede preentrenar con partidas simuladas durante el desarrollo y
## cargar con load_q_table(); si no, arranca en cero y aprende en la partida.

signal resistance_updated(eco_type: Enums.EcoType, resistance: float)
signal combo_progressed(used_types: int, required_types: int)

## Cuánto sube la resistencia con cada repetición (tasa de aprendizaje).
@export_range(0.0, 1.0) var learning_rate: float = 0.22
## Techo de resistencia: nunca es inmune del todo, para no bloquear al jugador.
@export_range(0.0, 0.95) var max_learned_resistance: float = 0.75
## Cuánto se relaja la resistencia de los tipos que el jugador deja de usar.
@export_range(0.0, 1.0) var decay_rate: float = 0.08
## Contramedidas distintas necesarias para purificarlo.
@export var required_combo_size: int = 5

## Tabla Q: tipo de daño ambiental -> peso de resistencia aprendido (0 a 1).
var q_table: Dictionary = {}

## Tipos de Habilidad Ecológica ya aplicados en este combate.
## Se tipa Array[int] porque GDScript no admite arrays tipados de enum; los
## valores siguen siendo Enums.EcoType.
var used_eco_types: Array[int] = []


func _init() -> void:
	display_name = "Sombra de la Avaricia"
	lore = "No es un monstruo de una región: es lo que las produjo a todas."
	max_hp = 420
	max_energy = 60
	base_attack = 22
	base_defense = 16
	base_speed = 13
	# No tiene una única contramedida: cualquier EcoSkill suma al combo.
	required_counter_type = Enums.EcoType.NONE
	wrong_type_resistance = 0.35
	regeneration_ratio = 0.25
	experience_reward = 300
	skills = [SkillLibrary.greed_grasp()]


# --- Tabla Q ----------------------------------------------------------------

## Resistencia efectiva: la base del monstruo más lo aprendido de ese tipo.
func get_resistance_for(eco_type: Enums.EcoType) -> float:
	if is_purified:
		return 0.0
	var learned: float = float(q_table.get(eco_type, 0.0))
	if eco_type == Enums.EcoType.NONE:
		return clampf(wrong_type_resistance + learned, 0.0, max_learned_resistance)
	return clampf(learned, 0.0, max_learned_resistance)


## Refuerza el tipo recibido y relaja los demás. Es la actualización de la
## tabla Q tras la acción del jugador.
func _update_q_table(used_type: Enums.EcoType) -> void:
	var current: float = float(q_table.get(used_type, 0.0))
	# Aproximación al techo: cuanto más resistente ya es, menos sube.
	var updated: float = current + learning_rate * (max_learned_resistance - current)
	q_table[used_type] = clampf(updated, 0.0, max_learned_resistance)
	resistance_updated.emit(used_type, q_table[used_type])

	for key in q_table.keys():
		if key == used_type:
			continue
		q_table[key] = maxf(0.0, float(q_table[key]) - decay_rate)


## Carga una tabla preentrenada (por ejemplo, desde partidas simuladas).
func load_q_table(trained_table: Dictionary) -> void:
	q_table = trained_table.duplicate()


func get_learned_resistance(eco_type: Enums.EcoType) -> float:
	return float(q_table.get(eco_type, 0.0))


# --- Purificación por combinación -------------------------------------------

func receive_eco_skill(skill: EcoSkill) -> Array[String]:
	var log_lines: Array[String] = []
	if is_purified:
		return log_lines

	_update_q_table(skill.weakness_type)

	if used_eco_types.has(skill.weakness_type):
		log_lines.append("La Sombra ya conocía %s: se endurece contra ella." % skill.display_name)
	else:
		used_eco_types.append(skill.weakness_type)
		combo_progressed.emit(used_eco_types.size(), required_combo_size)
		log_lines.append("La Sombra retrocede ante algo que no había visto: %s." % skill.display_name)

	if used_eco_types.size() >= required_combo_size:
		is_purified = true
		purified.emit()
		log_lines.append("Las contramedidas se combinan y la Sombra de la Avaricia deja de rehacerse.")
	return log_lines


## El jefe apunta a quien mejor puede rematar, sin la aleatoriedad del resto.
func _choose_target(context: BattleContext) -> Combatant:
	return context.get_weakest(Enums.Team.PLAYER)
