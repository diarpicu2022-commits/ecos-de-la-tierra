extends Node

## Juega el combate real de `scenes/main.tscn` inyectando pulsaciones y captura
## el momento de la purificación, que es la prueba del paso 5: la regla central
## del juego, vista en pantalla.
##
## En vez de pulsar a ciegas cada X segundos, espera a que la pantalla entre en
## fase de elección. Así la captura no depende de acertar con el ritmo.
##   godot --path . res://tools/play_capture.tscn

const CHOOSING := 2   # BattleScreen.Phase.CHOOSING

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

	# Turno 1 (Coral, la más rápida): atacar. Sus Habilidades son de petróleo,
	# así que no pueden purificar a un monstruo de fuego.
	await _await_choice()
	# El menú tarda 160 ms en entrar. Sin esta espera se capturaría un cuadro a
	# medio fundir, y la auditoría de contraste mediría un color transitorio.
	await get_tree().create_timer(0.3).timeout
	await _shoot("menu raiz")
	await _press("confirm")          # ATACAR, objetivo unico: se resuelve solo

	# Turno 2 (Bruma): Habilidades -> Linea Cortafuegos. Aquí se ataja la causa.
	await _await_choice()
	await _press("move_down")        # HABILIDADES
	await _shoot("habilidades enfocado")
	await _press("confirm")
	await _shoot("lista de habilidades")
	await _press("confirm")          # Linea Cortafuegos

	# La purificación dura 300 ms: se captura cuadro a cuadro.
	for i in range(10):
		await get_tree().create_timer(0.14).timeout
		await _shoot("purificacion %d" % i)

	for i in range(6):
		await get_tree().create_timer(0.5).timeout
		await _shoot("despues %d" % i)

	print("Listo.")
	get_tree().quit()


## Espera a que la pantalla pida una decisión al jugador.
func _await_choice() -> void:
	for _i in range(600):
		if _screen != null and int(_screen.get("_phase")) == CHOOSING:
			return
		await get_tree().process_frame
	push_warning("No llego la fase de eleccion.")


func _shoot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("user://shot_%02d.png" % _shot)
	print("  %02d  %s" % [_shot, label])
	_shot += 1


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
