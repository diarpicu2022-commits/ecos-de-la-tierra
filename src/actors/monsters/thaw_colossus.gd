class_name ThawColossus
extends Monster

## Cumbre Menguante — deshielo glaciar por calentamiento global.
## Se vence con el Escudo de Albedo: devolver la radiación en vez de absorberla.

func _init() -> void:
	display_name = "Coloso del Deshielo"
	lore = "El último bloque de un glaciar que ya no vuelve a formarse en invierno."
	max_hp = 300
	max_energy = 40
	base_attack = 20
	base_defense = 14
	base_speed = 9
	required_counter_type = Enums.EcoType.THAW
	wrong_type_resistance = 0.7
	regeneration_ratio = 0.45
	experience_reward = 120
	skills = [SkillLibrary.avalanche(), SkillLibrary.searing_cold()]
