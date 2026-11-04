extends Node2D

## Fase 6: pruebas de usabilidad ejecutadas contra el juego real.
##
## Comprueba lo que se puede comprobar sin una persona delante: que todo se
## alcanza con el teclado, que el foco nunca se pierde, que las opciones que no
## se pueden pagar siguen siendo visitables, y que la rejilla de píxeles
## sobrevive a cualquier tamaño de ventana.
##   godot --path . res://tools/verify_usability.tscn

const CHOOSING := 2
const CHOICE_TIMEOUT_MS := 30000

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

	print("\n=== LOS SUBMENUS CABEN ===")
	_test_submenu_fit()

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

	# Recorrer la rejilla entera en un circulo y volver al principio: nadie debe
	# quedarse fuera.
	var visitados: Array[int] = []
	for action in ["move_right", "move_down", "move_left", "move_up"]:
		visitados.append(_menu.focused)
		await _press(action)
	var distintos := {}
	for i in visitados:
		distintos[i] = true
	_check("se alcanzan todas las opciones", distintos.size() == total,
			"(%s)" % str(visitados))
	_check("el cursor vuelve al principio", _menu.focused == 0)

	# Los cuatro sentidos desde los cuatro mandos, con la vuelta incluida:
	# 0 LUCHAR, 1 ECO, 2 BOLSA, 3 HUIR.
	var esperado := {
		"move_right": [1, 0, 3, 2],
		"move_left": [1, 0, 3, 2],
		"move_down": [2, 3, 0, 1],
		"move_up": [2, 3, 0, 1],
	}
	for action in esperado:
		var obtenido: Array[int] = []
		for i in range(total):
			await _go_to(i)
			await _press(action)
			obtenido.append(_menu.focused)
		_check("rejilla 2x2: %s" % action, obtenido == (esperado[action] as Array),
				"(%s)" % str(obtenido))
	await _go_to(0)
	await _press("move_up")
	_check("tambien se recorre hacia arriba, dando la vuelta", _menu.focused == 2)
	await _press("move_down")

	# Escape vuelve al mando anterior y no gasta el turno.
	await _press("move_right")
	await _press("cancel")
	_check("Escape vuelve al mando anterior", _menu.focused == 0)
	_check("Escape en la raiz no gasta el turno", int(_screen.get("_phase")) == CHOOSING)

	# Entrar en un submenu y volver: cancelar no puede costar el turno.
	await _reach_actor_with_skills()
	await _press("move_right")    # ECO
	await _press("confirm")
	# Comprobar el tamaño no basta: si la opcion estuviera apagada, el menu
	# seguiria siendo el de la raiz y la prueba daria un falso positivo.
	var en_submenu: int = _menu.entries.size()
	_check("ECO abre su propia lista",
			str(_menu.entries[0].get("kind", "")) == "skill",
			"(%d habilidades)" % en_submenu)
	_check("el submenu es lista, no rejilla", not _menu.is_grid())
	await _press("move_down")
	_check("la lista se recorre con arriba y abajo", _menu.focused == 1 % en_submenu)
	await _press("cancel")
	_check("cancelar devuelve al menu raiz", _menu.entries.size() == 4 and _menu.is_grid())
	_check("con el foco en el mando del que se vino", _menu.focused == 1)
	_check("sigue siendo el turno del mismo personaje",
			int(_screen.get("_phase")) == CHOOSING)
	await _go_to(0)


## Lleva el foco a un mando directamente, sin pasar por el teclado.
func _go_to(index: int) -> void:
	_menu.focused = index
	await get_tree().process_frame


## El mayor numero de filas posible, con los datos reales de los seis combates,
## contra el alto util de la placa y sin recortar ninguna etiqueta.
func _test_submenu_fit() -> void:
	var capacity: int = _menu.list_capacity()
	var filas := {"habilidades": 0, "objetos": 0, "aliados": 0, "enemigos": 3}
	var mas_ancha := {"sobra": INF, "texto": ""}
	var medir := func(entry: Dictionary) -> void:
		var sobra: float = _menu.label_room(entry) - _menu._width(str(entry["label"]))
		if sobra < float(mas_ancha["sobra"]):
			mas_ancha["sobra"] = sobra
			mas_ancha["texto"] = str(entry["label"])
	for i in range(Encounters.count()):
		var grupo := Encounters.build_party(i)
		filas["aliados"] = maxi(filas["aliados"], grupo.size())
		for character in grupo:
			var known := character.get_known_skills()
			filas["habilidades"] = maxi(filas["habilidades"], known.size())
			for skill in known:
				medir.call({"label": skill.display_name, "cost": skill.energy_cost})
			medir.call({"label": character.display_name, "cost": -1})
			character.free()
		var monster := Encounters.build_monster(i)
		medir.call({"label": monster.display_name, "cost": -1})
		monster.free()
	# Todos los objetos de batalla que existen, con una cantidad de dos cifras.
	for item in [ItemLibrary.healing_herb(), ItemLibrary.purified_water(),
			ItemLibrary.suri_antidote(), ItemLibrary.field_ration()]:
		if item.usable_in_battle and not item.crafting_material:
			filas["objetos"] += 1
			medir.call({"label": "%s x%d" % [item.display_name, 99], "cost": -1})
	var peor: int = filas.values().max()
	_check("el submenu mas largo cabe en la placa", peor <= capacity,
			"(%s; caben %d)" % [str(filas), capacity])
	_check("ninguna etiqueta real se recorta", float(mas_ancha["sobra"]) >= 0.0,
			"(la mas justa: «%s», sobran %.0f px)" % [mas_ancha["texto"], mas_ancha["sobra"]])


func _test_unaffordable() -> void:
	await _reach_actor_with_skills()
	var actor: Character = _screen.get("_actor")
	actor.energy = 0
	await _press("move_right")    # ECO
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
	_check("sin nada que pagar, ECO se queda con su mando", _menu.focused == 1)


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
		await _press("confirm")   # LUCHAR, objetivo unico
		await _await_choice()
	printerr("  AVISO: nadie del grupo tiene habilidades disponibles.")


## Espera por tiempo real, no por cuadros: sin ventana los cuadros pasan muy
## rápido y los mensajes del combate duran segundos, así que 900 cuadros podían
## acabarse antes de que abriera el menú.
func _await_choice() -> void:
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < CHOICE_TIMEOUT_MS:
		if _screen != null and int(_screen.get("_phase")) == CHOOSING:
			print("  (menu abierto tras %d ms)" % (Time.get_ticks_msec() - start))
			await get_tree().create_timer(0.25).timeout
			return
		await get_tree().process_frame
	_check("el menu abre antes de %d ms" % CHOICE_TIMEOUT_MS, false)


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
