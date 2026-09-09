class_name Item
extends Resource

## Objeto de la Bolsa. Los consumibles se gastan al usarse; los materiales que
## recoge Nix por la costa sirven de ingrediente para fabricar y no se "usan"
## directamente en combate.

@export var display_name: String = "Objeto"
@export_multiline var description: String = ""
@export var consumable: bool = true
@export var usable_in_battle: bool = true
## Material de fabricación: no se consume desde el menú de batalla.
@export var crafting_material: bool = false


## Aplica el efecto del objeto. Devuelve las líneas del registro de batalla.
func use(user: Combatant, target: Combatant) -> Array[String]:
	push_warning("Item.use() debe sobrescribirse en la subclase.")
	return []
