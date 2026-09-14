class_name Character
extends Combatant

## Personaje jugable: Ilan y los cuatro compañeros (Bruma, Coral, Nix y Suri).
##
## Su progresión tiene dos vías separadas a propósito. La experiencia sube
## estadísticas; el Conocimiento Ambiental —que se consigue resolviendo puzzles,
## hablando con la gente de cada región o encontrando objetos— es lo único que
## desbloquea Habilidades Ecológicas. Subir de nivel nunca basta para vencer a
## un jefe.

signal leveled_up(new_level: int)
signal skill_learned(skill: Skill)
signal knowledge_gained(eco_type: Enums.EcoType)

const EXPERIENCE_PER_LEVEL: int = 100

@export var specialty: String = ""          ## Especialidad de combate, para la ficha.
@export var portrait: Texture2D = null
@export var level: int = 1

var experience: int = 0
var skills: Array[Skill] = []
## Tipos de daño ambiental cuyo Conocimiento Ambiental ya se recolectó.
## Array[int] porque GDScript no admite arrays tipados de enum; los valores
## siguen siendo Enums.EcoType.
var eco_knowledge: Array[int] = []


func _ready() -> void:
	super._ready()
	team = Enums.Team.PLAYER


# --- Habilidades ------------------------------------------------------------

func learn_skill(skill: Skill) -> bool:
	if skills.has(skill):
		return false
	skills.append(skill)
	skill_learned.emit(skill)
	return true


## Habilidades utilizables ahora mismo: el personaje debe tener energía y, si es
## una Habilidad Ecológica, el Conocimiento Ambiental de ese tipo.
func get_usable_skills() -> Array[Skill]:
	var usable: Array[Skill] = []
	for skill in skills:
		if not skill.can_use(self):
			continue
		if skill is EcoSkill and not has_knowledge((skill as EcoSkill).weakness_type):
			continue
		usable.append(skill)
	return usable


## Habilidades que el personaje **sabe** usar, tenga o no energía ahora mismo.
##
## Es distinto de `get_usable_skills()`, que además exige poder pagarlas. La
## interfaz usa esta: muestra todas las conocidas y marca en rojo el coste de
## las que no alcanzan. Ocultar una opción impide aprender que existe, que es
## el fallo del menú de batalla de Final Fantasy VI recogido en el anexo de UX.
func get_known_skills() -> Array[Skill]:
	var known: Array[Skill] = []
	for skill in skills:
		if skill is EcoSkill and not has_knowledge((skill as EcoSkill).weakness_type):
			continue
		known.append(skill)
	return known


func get_eco_skills() -> Array[Skill]:
	var eco_skills: Array[Skill] = []
	for skill in skills:
		if skill is EcoSkill:
			eco_skills.append(skill)
	return eco_skills


# --- Conocimiento Ambiental -------------------------------------------------

func has_knowledge(eco_type: Enums.EcoType) -> bool:
	return eco_knowledge.has(eco_type)


func gain_knowledge(eco_type: Enums.EcoType) -> bool:
	if has_knowledge(eco_type):
		return false
	eco_knowledge.append(eco_type)
	knowledge_gained.emit(eco_type)
	return true


# --- Experiencia y niveles --------------------------------------------------

func add_experience(amount: int) -> void:
	experience += amount
	while experience >= EXPERIENCE_PER_LEVEL:
		experience -= EXPERIENCE_PER_LEVEL
		_level_up()


func _level_up() -> void:
	level += 1
	max_hp += 12
	max_energy += 4
	base_attack += 3
	base_defense += 2
	base_speed += 1
	hp = max_hp
	energy = max_energy
	hp_changed.emit(hp, max_hp)
	energy_changed.emit(energy, max_energy)
	leveled_up.emit(level)
