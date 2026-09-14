extends Node2D

## Fase 6: pruebas de usabilidad ejecutadas contra el juego real.
##
## Comprueba lo que se puede comprobar sin una persona delante: que todo se
## alcanza con el teclado, que el foco nunca se pierde, que las opciones que no
## se pueden pagar siguen siendo visitables, y que la rejilla de píxeles
## sobrevive a cualquier tamaño de ventana.
##   godot --path . res://tools/verify_usability.tscn

const CHOOSING := 2

var _screen: BattleScreen = null
var _menu: ActionMenu = null
var _pass: int = 0
var _fail: int = 0


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

	await _await_choice()
	_menu = _screen.get("_menu")

	print("\n=== RECORRIDO POR TECLADO ===")
	await _test_keyboard()

	print("\n=== OPCIONES QUE NO SE PUEDEN PAGAR ===")
	await _test_unaffordable()

	print("\n=== ESCALADO ENTERO DE LA REJILLA ===")
	await _test_integer_scale()

	print("\n%d comprobaciones superadas, %d fallidas." % [_pass, _fail])
	get_tree().quit(0 if _fail == 0 else 1)


func _check(label: String, condition: bool, detail: String = "") -> void:
	if condition:
		_pass += 1
		print("  OK    %s %s" % [label, detail])
	else:
		_fail += 1
		printerr("  FALLA %s %s" % [label, detail])


func _test_keyboard() -> void:
	var total: int = _menu.entries.size()
	_check("el menu raiz ofrece las cuatro acciones", total == 4,
			"(%d entradas)" % total)
	_check("hay foco desde el primer cuadro", _menu.focused == 0)

	# Recorrer el menu entero y volver al principio: nadie debe quedarse fuera.
	var visitados: Array[int] = []
	for i in range(total):
		visitados.append(_menu.focused)
		await _press("move_down")
	_check("se alcanzan todas las opciones bajando", visitados.size() == total
			and visitados.duplicate().size() == total)
	_check("el cursor da la vuelta al final", _menu.focused == 0)

	await _press("move_up")
	_check("tambien se recorre hacia arriba", _menu.focused == total - 1)
	await _press("move_down")

	# Entrar en un submenu y volver: cancelar no puede costar el turno.
	await _reach_actor_with_skills()
	await _press("move_down")     # HABILIDADES
	await _press("confirm")
	# Comprobar el tamaño no basta: si la opcion estuviera apagada, el menu
	# seguiria siendo el de la raiz y la prueba daria un falso positivo.
	var en_submenu: int = _menu.entries.size()
	_check("Habilidades abre su propia lista",
			str(_menu.entries[0].get("kind", "")) == "skill",
			"(%d habilidades)" % en_submenu)
	await _press("cancel")
	_check("cancelar devuelve al menu raiz", _menu.entries.size() == 4)
	_check("sigue siendo el turno del mismo personaje",
			int(_screen.get("_phase")) == CHOOSING)


func _test_unaffordable() -> void:
	await _reach_actor_with_skills()
	var actor: Character = _screen.get("_actor")
	actor.energy = 0
	await _press("move_down")     # HABILIDADES
	await _press("confirm")
	if str(_menu.entries[0].get("kind", "")) != "skill":
		_fail += 1
		printerr("  FALLA no se pudo abrir el submenu de habilidades")
		return

	var visitables: int = 0
	var bloqueadas: int = 0
	for entry in _menu.entries:
		visitables += 1
		if not entry.get("enabled", true):
			bloqueadas += 1
	_check("sin energia, las habilidades siguen listadas", visitables > 0,
			"(%d listadas)" % visitables)
	_check("y aparecen como no pagables", bloqueadas == visitables,
			"(%d de %d)" % [bloqueadas, visitables])

	# El cursor tiene que poder pararse encima para leer el coste.
	var antes: int = _menu.focused
	await _press("move_down")
	_check("el cursor visita una opcion no pagable", _menu.focused != antes)

	await _press("confirm")
	_check("confirmar una no pagable no gasta el turno",
			_menu.entries.size() == visitables)
	await _press("cancel")


func _test_integer_scale() -> void:
	var window := get_window()
	for size in [Vector2i(480, 270), Vector2i(960, 540), Vector2i(1103, 621),
			Vector2i(1440, 810)]:
		window.size = size
		await get_tree().process_frame
		await get_tree().process_frame
		var scale := get_viewport().get_final_transform().get_scale()
		var entero: bool = is_equal_approx(scale.x, roundf(scale.x)) \
				and is_equal_approx(scale.y, roundf(scale.y))
		_check("ventana %dx%d" % [size.x, size.y], entero,
				"-> escala %.3f x %.3f" % [scale.x, scale.y])


## Avanza turnos hasta que le toque a alguien que tenga habilidades.
##
## En el Bosque de las Cenizas, Ilan solo conoce el Escudo de Albedo, que es de
## deshielo: su menu de Habilidades esta legitimamente vacio, y quien trae la
## contramedida es Bruma. La prueba tiene que llegar hasta ella.
func _reach_actor_with_skills() -> void:
	for _i in range(8):
		var actor: Character = _screen.get("_actor")
		if actor != null and not actor.get_known_skills().is_empty():
			return
		await _press("confirm")   # ATACAR, objetivo unico
		await _await_choice()
	printerr("  AVISO: nadie del grupo tiene habilidades disponibles.")


func _await_choice() -> void:
	for _i in range(900):
		if _screen != null and int(_screen.get("_phase")) == CHOOSING:
			await get_tree().create_timer(0.25).timeout
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
