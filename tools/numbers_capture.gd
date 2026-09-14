extends Node

## Captura las cifras de daño, que duran 260 ms. Enseña los dos casos que
## importan: un golpe que el monstruo resiste por no atacar la causa, y el
## mismo golpe una vez purificado.
##   godot --path . res://tools/numbers_capture.tscn

const CHOOSING := 2

var _screen: BattleScreen = null
var _shot: int = 0


func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	# El juego arranca en el selector de región: se entra en la primera, el
	# Bosque de las Cenizas, y se espera a que la pantalla de combate exista.
	await get_tree().create_timer(0.45).timeout
	await _press("confirm")
	for _i in range(300):
		_screen = main.get("_screen")
		if _screen != null:
			break
		await get_tree().process_frame
	if _screen == null:
		printerr("No se pudo abrir el combate desde el selector.")
		get_tree().quit(1)
		return

	# Turno 1: ataque físico contra un monstruo de fuego. No ataja la causa,
	# así que el monstruo lo resiste.
	await _await_choice()
	await _press("confirm")
	await _burst("resistido")

	# Turno 2: Línea Cortafuegos. Ataja la causa.
	await _await_choice()
	await _press("move_down")
	await _press("confirm")
	await _press("confirm")
	await _burst("purificacion")

	# Turno 3: el mismo ataque físico, ya purificado. Ahora sí hace mella.
	await _await_choice()
	await _press("confirm")
	await _burst("completo")

	print("Listo.")
	get_tree().quit()


## Ráfaga de capturas seguidas, para atrapar una animación de 260 ms.
func _burst(label: String) -> void:
	for i in range(8):
		await get_tree().create_timer(0.05).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(
				"user://num_%s_%d.png" % [label, i])
	print("  %s capturado" % label)


func _await_choice() -> void:
	for _i in range(900):
		if _screen != null and int(_screen.get("_phase")) == CHOOSING:
			await get_tree().create_timer(0.28).timeout
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
