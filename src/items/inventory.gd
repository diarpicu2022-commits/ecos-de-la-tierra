class_name Inventory
extends RefCounted

## Bolsa compartida por todo el grupo. Guarda cuántas unidades hay de cada
## objeto en un diccionario Item -> cantidad, para no repetir recursos.

signal contents_changed()

var _slots: Dictionary = {}


func add(item: Item, amount: int = 1) -> void:
	if amount <= 0:
		return
	_slots[item] = get_amount(item) + amount
	contents_changed.emit()


## Descuenta unidades. Devuelve false si no había suficientes.
func remove(item: Item, amount: int = 1) -> bool:
	var current: int = get_amount(item)
	if current < amount:
		return false
	if current == amount:
		_slots.erase(item)
	else:
		_slots[item] = current - amount
	contents_changed.emit()
	return true


func get_amount(item: Item) -> int:
	return _slots.get(item, 0)


func has(item: Item) -> bool:
	return get_amount(item) > 0


## Objetos que pueden elegirse desde el menú Bolsa durante un combate.
func get_battle_items() -> Array[Item]:
	var available: Array[Item] = []
	for item in _slots.keys():
		if item.usable_in_battle and not item.crafting_material:
			available.append(item)
	return available


## Todos los objetos guardados, para el menú fuera de combate.
func get_all() -> Array[Item]:
	var all_items: Array[Item] = []
	for item in _slots.keys():
		all_items.append(item)
	return all_items


## Usa un objeto y lo descuenta si es consumible.
func use(item: Item, user: Combatant, target: Combatant) -> Array[String]:
	if not has(item):
		return ["No queda ninguna unidad de %s." % item.display_name]
	var log_lines: Array[String] = item.use(user, target)
	if item.consumable:
		remove(item, 1)
	return log_lines
