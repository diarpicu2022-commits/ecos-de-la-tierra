class_name OilDevourer
extends Monster

## Cuenca de Alquitrán — derrames de crudo y contaminación del agua.
## Se vence con la Barrera Absorbente: contener y filtrar el vertido.

func _init() -> void:
	display_name = "Devorador de Petróleo"
	lore = "Se formó en la desembocadura donde el crudo lleva años acumulándose."
	max_hp = 210
	max_energy = 30
	base_attack = 15
	base_defense = 11
	base_speed = 8
	required_counter_type = Enums.EcoType.OIL
	wrong_type_resistance = 0.65
	regeneration_ratio = 0.4
	experience_reward = 75
	skills = [SkillLibrary.black_tide(), SkillLibrary.viscous_trap()]
