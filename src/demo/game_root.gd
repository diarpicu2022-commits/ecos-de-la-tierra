extends Control

## Raíz del juego: alterna entre la elección de región y el combate.
##
## Sustituye al arranque de un solo combate. Los seis encuentros de la propuesta
## se pueden jugar en cualquier orden, que es lo que permite revisar el juego
## sin tener que ganar cinco veces para llegar a la Cripta.

var _select: RegionSelect = null
var _screen: BattleScreen = null
var _combatants: Array[Node] = []
var _index: int = 0
var _finished: bool = false


func _ready() -> void:
	randomize()
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_open_select()


func _open_select() -> void:
	_clear_battle()
	_select = RegionSelect.new()
	add_child(_select)
	_select.region_chosen.connect(_start_battle)


func _start_battle(index: int) -> void:
	_index = index
	_finished = false
	if _select != null:
		_select.queue_free()
		_select = null

	_screen = BattleScreen.new()
	add_child(_screen)
	_screen.battle_finished.connect(_on_battle_finished)

	var players: Array[Combatant] = []
	for character in Encounters.build_party(index):
		add_child(character)
		_combatants.append(character)
		players.append(character)

	var monster: Monster = Encounters.build_monster(index)
	add_child(monster)
	_combatants.append(monster)
	var enemies: Array[Combatant] = [monster]

	_screen.start_battle(players, enemies, Encounters.build_inventory(index))


func _on_battle_finished(_result: Enums.BattleResult) -> void:
	_finished = true


## Terminado el combate, `confirm` vuelve a la elección de región. Sin esto
## habría que cerrar y relanzar el juego para probar otro.
func _unhandled_input(event: InputEvent) -> void:
	if not _finished or not event.is_action_pressed("confirm"):
		return
	get_viewport().set_input_as_handled()
	_finished = false
	await get_tree().process_frame
	_open_select()


func _clear_battle() -> void:
	for node in _combatants:
		if is_instance_valid(node):
			node.queue_free()
	_combatants.clear()
	if _screen != null:
		_screen.queue_free()
		_screen = null
