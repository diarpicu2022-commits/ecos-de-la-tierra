extends Node2D

## Verifica el único caso con varios enemigos en el campo: el Espectro del
## Monocultivo y sus clones.
##
## No se espera a que la IA decida multiplicarse, que puede tardar muchas
## rondas: se fuerza la Multiplicación directamente, que es exactamente lo que
## el combate acabaría haciendo. Lo que se comprueba es el **reparto en
## pantalla**, no la IA, que ya está verificada en la prueba por consola.
##   godot --path . res://tools/clones_capture.tscn

const CHOOSING := 2

var _screen: BattleScreen = null
var _specter: MonocultureSpecter = null


func _ready() -> void:
	_screen = BattleScreen.new()
	add_child(_screen)

	var players: Array[Combatant] = []
	for character in Encounters.build_party(3):
		add_child(character)
		players.append(character)

	_specter = Encounters.build_monster(3) as MonocultureSpecter
	add_child(_specter)
	var enemies: Array[Combatant] = [_specter]
	_screen.start_battle(players, enemies, Encounters.build_inventory(3))

	await _await_choice()
	await _shoot("01_uno")

	# Dos clones: el tope que permite el Espectro.
	for i in range(2):
		for line in _specter.summon_clone():
			print("  %s" % line)

	# La aparición se encola como cualquier otro evento, así que hay que dejar
	# que la reproducción avance para que las vistas lleguen a existir. Se
	# resuelve un turno del grupo, que es lo que ocurriría en el juego.
	await _press("confirm")          # ATACAR
	await _press("confirm")          # primer objetivo
	await _await_choice()
	await _shoot("02_tres")

	# Recorrer objetivos: la ficha completa debe seguir al cursor.
	await _press("confirm")          # ATACAR -> menu de objetivos
	await get_tree().create_timer(0.35).timeout
	await _shoot("03_objetivo_1")
	await _press("move_down")
	await get_tree().create_timer(0.35).timeout
	await _shoot("04_objetivo_2")
	await _press("move_down")
	await get_tree().create_timer(0.35).timeout
	await _shoot("05_objetivo_3")

	print("Listo.")
	get_tree().quit()


func _shoot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("user://clon_%s.png" % label)
	print("  capturado %s" % label)


func _await_choice() -> void:
	for _i in range(900):
		if int(_screen.get("_phase")) == CHOOSING:
			await get_tree().create_timer(0.3).timeout
			return
		await get_tree().process_frame


func _press(action: String) -> void:
	var down := InputEventAction.new()
	down.action = action
	down.pressed = true
	Input.parse_input_event(down)
	await get_tree().process_frame
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)
	await get_tree().process_frame
