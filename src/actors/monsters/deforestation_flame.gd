class_name DeforestationFlame
extends Monster

## Bosque de las Cenizas — incendios forestales y tala de árboles.
## Se vence con la Línea Cortafuegos: aislar el oxígeno, no golpear el fuego.

func _init() -> void:
	display_name = "Llama de la Deforestación"
	lore = "Nació del humo de un bosque talado y quemado para abrir terreno."
	max_hp = 180
	max_energy = 30
	base_attack = 16
	base_defense = 8
	base_speed = 12
	required_counter_type = Enums.EcoType.FIRE
	wrong_type_resistance = 0.6
	regeneration_ratio = 0.35
	experience_reward = 60
	skills = [SkillLibrary.heat_wave(), SkillLibrary.smoke_suffocation()]
