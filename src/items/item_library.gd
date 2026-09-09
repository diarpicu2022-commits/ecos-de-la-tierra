class_name ItemLibrary
extends RefCounted

## Catálogo de objetos de la Bolsa, con el mismo criterio que SkillLibrary:
## una función por objeto, todas devolviendo una instancia ya configurada.

## Curación básica que se encuentra desde Valdehoja.
static func healing_herb() -> HealingItem:
	var item := HealingItem.new()
	item.display_name = "Hierba de Valdehoja"
	item.description = "Hoja común del huerto de la abuela. Restaura algo de vida."
	item.heal_amount = 40
	return item


## Agua filtrada: cura y corta el veneno de los derrames.
static func purified_water() -> HealingItem:
	var item := HealingItem.new()
	item.display_name = "Agua Purificada"
	item.description = "Agua pasada por el filtro de Coral. Corta el veneno."
	item.heal_amount = 25
	item.cures_status = true
	item.cured_status_type = Enums.StatusType.POISON
	return item


## Antídoto de Suri, preparado con plantas de suelo recuperado.
static func suri_antidote() -> HealingItem:
	var item := HealingItem.new()
	item.display_name = "Antídoto de Suri"
	item.description = "Preparado con plantas de suelo regenerado. Elimina el veneno."
	item.heal_amount = 0
	item.cures_status = true
	item.cured_status_type = Enums.StatusType.POISON
	return item


## Ración que devuelve energía para las Habilidades Ecológicas.
static func field_ration() -> HealingItem:
	var item := HealingItem.new()
	item.display_name = "Ración de Campo"
	item.description = "Comida de viaje. Devuelve energía para las habilidades."
	item.heal_amount = 10
	item.energy_amount = 12
	return item


## Chatarra de la costa: material de fabricación de Nix, no se usa en combate.
static func scrap_plastic() -> Item:
	var item := Item.new()
	item.display_name = "Plástico Recuperado"
	item.description = "Residuo clasificado en la Costa Quebrada. Nix lo aprovecha."
	item.usable_in_battle = false
	item.crafting_material = true
	return item
