class_name PartyLibrary
extends RefCounted

## Construye a los personajes jugables con sus estadísticas y sus habilidades de
## partida. El Conocimiento Ambiental se deja vacío a propósito: se recolecta
## durante el juego y es lo que habilita cada Habilidad Ecológica.

## Ilan — protagonista. Su nombre lo puede cambiar el jugador.
static func ilan(player_name: String = "Ilan") -> Character:
	var character := Character.new()
	character.display_name = player_name
	character.specialty = "Vínculo con los espíritus elementales"
	character.max_hp = 120
	character.max_energy = 30
	character.base_attack = 14
	character.base_defense = 9
	character.base_speed = 12
	character.skills = [SkillLibrary.albedo_shield()]
	return character


## Bruma — antigua guardabosques. Reforestación y control de fuego.
static func bruma() -> Character:
	var character := Character.new()
	character.display_name = "Bruma"
	character.specialty = "Reforestación y control de fuego"
	character.max_hp = 110
	character.max_energy = 34
	character.base_attack = 13
	character.base_defense = 10
	character.base_speed = 11
	character.skills = [SkillLibrary.firebreak_line(), SkillLibrary.reforestation()]
	return character


## Coral — hija de pescadores. Purificación de agua.
static func coral() -> Character:
	var character := Character.new()
	character.display_name = "Coral"
	character.specialty = "Purificación de agua"
	character.max_hp = 100
	character.max_energy = 38
	character.base_attack = 11
	character.base_defense = 8
	character.base_speed = 14
	character.skills = [SkillLibrary.absorbent_barrier(), SkillLibrary.biological_filter()]
	return character


## Nix — ingeniero autodidacta. Reciclaje y fabricación de objetos.
static func nix() -> Character:
	var character := Character.new()
	character.display_name = "Nix"
	character.specialty = "Reciclaje y fabricación"
	character.max_hp = 115
	character.max_energy = 30
	character.base_attack = 12
	character.base_defense = 12
	character.base_speed = 9
	character.skills = [SkillLibrary.source_separation()]
	return character


## Suri — agricultora experta en suelos. Regeneración de tierras.
static func suri() -> Character:
	var character := Character.new()
	character.display_name = "Suri"
	character.specialty = "Regeneración de suelos, venenos y antídotos"
	character.max_hp = 105
	character.max_energy = 36
	character.base_attack = 12
	character.base_defense = 9
	character.base_speed = 10
	character.skills = [SkillLibrary.crop_rotation()]
	return character


## Grupo completo del tramo final, ya con todo el Conocimiento Ambiental.
static func full_party() -> Array[Character]:
	var party: Array[Character] = [ilan(), bruma(), coral(), nix(), suri()]
	for character in party:
		for eco_type in [
			Enums.EcoType.FIRE, Enums.EcoType.OIL, Enums.EcoType.PLASTIC,
			Enums.EcoType.MONOCULTURE, Enums.EcoType.THAW,
		]:
			character.gain_knowledge(eco_type)
	return party
