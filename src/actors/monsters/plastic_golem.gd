class_name PlasticGolem
extends Monster

## Costa Quebrada — residuos sólidos y microplásticos.
## Se vence con la Separación en la Fuente: clasificar antes de que se mezcle.
##
## Su "Muro Indestructible" no es una habilidad de turno sino una resistencia
## pasiva altísima: golpearlo más fuerte nunca funciona, solo separar el residuo.

func _init() -> void:
	display_name = "Gólem de Plástico"
	lore = "Una montaña de envases compactados por el mar durante décadas."
	max_hp = 240
	max_energy = 30
	base_attack = 17
	base_defense = 16
	base_speed = 6
	required_counter_type = Enums.EcoType.PLASTIC
	wrong_type_resistance = 0.8
	regeneration_ratio = 0.3
	experience_reward = 90
	skills = [SkillLibrary.microparticles(), SkillLibrary.debris_slam()]
