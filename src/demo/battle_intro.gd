extends Control

## Punto de entrada del juego: monta la pantalla de batalla y lanza el combate
## del Bosque de las Cenizas, que es el que enseña la regla central.
##
## Es la primera pantalla jugable con gráficos. Sustituye a la prueba por
## consola de `battle_demo.gd`, que sigue disponible en
## `tools/console_demo.tscn` para verificar las reglas sin interfaz.

var _screen: BattleScreen = null
var _combatants: Array[Node] = []
var _finished: bool = false


func _ready() -> void:
	randomize()
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_start()


func _start() -> void:
	_finished = false

	_screen = BattleScreen.new()
	add_child(_screen)
	_screen.battle_finished.connect(_on_battle_finished)

	# Bosque de las Cenizas: Bruma y Coral contra la Llama de la Deforestación.
	# Las dos llegan con el Conocimiento Ambiental del fuego, así que la Línea
	# Cortafuegos está disponible desde el primer turno: el jugador puede
	# descubrir por su cuenta que atacar sin más no cierra el combate.
	var bruma: Character = PartyLibrary.bruma()
	var coral: Character = PartyLibrary.coral()
	var players: Array[Combatant] = []
	for character in [bruma, coral]:
		character.gain_knowledge(Enums.EcoType.FIRE)
		character.gain_knowledge(Enums.EcoType.OIL)
		add_child(character)
		_combatants.append(character)
		players.append(character)

	var monster := DeforestationFlame.new()
	add_child(monster)
	_combatants.append(monster)
	var enemies: Array[Combatant] = [monster]

	var inventory := Inventory.new()
	inventory.add(ItemLibrary.healing_herb(), 3)
	inventory.add(ItemLibrary.purified_water(), 2)

	_screen.start_battle(players, enemies, inventory)


func _on_battle_finished(_result: Enums.BattleResult) -> void:
	_finished = true


## Terminado el combate, `confirm` vuelve a empezar. Sin esto habría que cerrar
## y relanzar el juego para probar otra vez.
func _unhandled_input(event: InputEvent) -> void:
	if not _finished or not event.is_action_pressed("confirm"):
		return
	get_viewport().set_input_as_handled()
	for node in _combatants:
		node.queue_free()
	_combatants.clear()
	_screen.queue_free()
	_screen = null
	await get_tree().process_frame
	_start()
